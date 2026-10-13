#!/usr/bin/env python3
"""Lay out the copper of the system candidate (D-033, PCB-002).

Hand-designed part, fixed and locked before any track search:
  * stackup: In1.Cu solid GND plane; In2.Cu PVDD plane over the power region only
    (rectifier/bulk, buck, TPA strip), signals elsewhere; F.Cu/B.Cu GND fill;
  * TPA3255 fanout: PVDD/GND pin runs strapped and dropped to the planes with
    two vias per run; every other SMD GND pad gets its own via to In1.
The remaining nets (signals, PWM/SPK/T1 with power widths) are laid by Freerouting
inside those constraints; GND is not offered to it (planes carry it). The result is
checked with DRC + schematic parity; Class-D loops are reviewed in docs/pcb-layout.md.
"""

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "kicad/system-candidate/system-candidate.kicad_pcb"
JAR = ROOT / "build/tools/freerouting-1.9.0.jar"
WORK = ROOT / "build/route"

# Track width in um for the searched nets (DSN classes). Planes carry PVDD/GND current.
POWER = {"SPK_P": 1500, "SPK_N": 1500, "T1_A": 1500, "T1_B": 1500, "T1_CT": 1500,
         "PVDD": 600, "BUCK_SW": 600, "AUX_RAW": 600, "NRAW": 400, "P15V": 400, "N15V": 400}
POWER_PATTERN = re.compile(r"^/PWM_(AC|BD)$")  # PBTL bridge outputs, necked by 0.4 mm TPA pads
# In2.Cu PVDD region (KiCad mm): transformer end, TPA strip under the block, C14 at the left end.
PVDD_REGION = [(124.0, 20.5), (173.5, 20.5), (173.5, 100.5), (123.5, 100.5), (123.5, 68.5),
               (44.0, 68.5), (44.0, 42.5), (62.5, 42.5), (62.5, 52.0), (124.0, 52.0)]


def zone(pcb, pcbnew, net, layer, points, priority, name, solid=False):
    z = pcbnew.ZONE(pcb)
    z.SetLayer(layer)
    z.SetNet(pcb.FindNet(net))
    z.SetZoneName(name)
    z.SetAssignedPriority(priority)
    z.SetLocalClearance(pcbnew.FromMM(0.3))
    z.SetMinThickness(pcbnew.FromMM(0.25))
    # shortcut: outer GND fills connect THT pads solid (no spokes) so dense pads never
    # starve; preheat/iron power for hand soldering, revisit if assembly complains.
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    poly = pcbnew.SHAPE_POLY_SET()
    poly.NewOutline()
    for x, y in points:
        poly.Append(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    z.SetOutline(poly)
    poly.thisown = False
    pcb.Add(z)
    return z


def planes(pcb, pcbnew):
    pcb.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    pcb.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_MIXED)
    bb = pcb.GetBoardEdgesBoundingBox()
    x0, y0, x1, y1 = (pcbnew.ToMM(v) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom()))
    board = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    zone(pcb, pcbnew, "/GND", pcbnew.In1_Cu, board, 0, "GND_PLANE", solid=True)
    zone(pcb, pcbnew, "/PVDD", pcbnew.In2_Cu, PVDD_REGION, 1, "PVDD_PLANE", solid=True)
    zone(pcb, pcbnew, "/GND", pcbnew.F_Cu, board, 0, "GND_FILL_TOP")
    zone(pcb, pcbnew, "/GND", pcbnew.B_Cu, board, 0, "GND_FILL_BOTTOM")


def add_track(pcb, pcbnew, a, b, width, layer, net):
    t = pcbnew.PCB_TRACK(pcb)
    t.SetStart(a)
    t.SetEnd(b)
    t.SetWidth(pcbnew.FromMM(width))
    t.SetLayer(layer)
    t.SetNet(net)
    t.SetLocked(True)
    pcb.Add(t)
    return t


def add_via(pcb, pcbnew, pos, net, d=0.6, drill=0.3):
    v = pcbnew.PCB_VIA(pcb)
    v.SetPosition(pos)
    v.SetWidth(pcbnew.FromMM(d))
    v.SetDrill(pcbnew.FromMM(drill))
    v.SetNet(net)
    v.SetLocked(True)
    pcb.Add(v)
    return v


FANOUT = []  # (stub track, via) pairs added by hand, pruned against DRC


def prune(pcb, pcbnew, rounds=6):
    """Remove hand-placed stub+via pairs that DRC flags (clearance, shorts, holes, rule
    areas). A pad that loses its via is then joined by the fills or reported unconnected."""
    import json
    bad_types = {"clearance", "shorting_items", "solder_mask_bridge", "hole_clearance",
                 "items_not_allowed", "hole_to_hole", "copper_edge_clearance", "tracks_crossing",
                 "via_dangling", "track_dangling"}
    removed = 0
    for _ in range(rounds):
        pcbnew.ZONE_FILLER(pcb).Fill(pcb.Zones())
        tmp, report = WORK / "prune.kicad_pcb", WORK / "prune-drc.json"
        pcbnew.SaveBoard(str(tmp), pcb)
        subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "--severity-all", "-o",
                        str(report), str(tmp)], capture_output=True, check=False)
        flagged = {i.get("uuid") for v in json.loads(report.read_text())["violations"]
                   if v["type"] in bad_types for i in v["items"]}
        doomed = [pair for pair in FANOUT if {x.m_Uuid.AsString() for x in pair} & flagged]
        if not doomed:
            break
        for pair in doomed:
            FANOUT.remove(pair)
            for item in pair:
                pcb.Remove(item)
            removed += 1
    return removed


def fanout_tpa(pcb, pcbnew, ref="U1"):
    """PVDD/GND pin runs of U1: pad-width strap along the run, then two staggered vias
    straight out of the row (TI layout: power pins to planes with short, wide paths)."""
    fp = pcb.FindFootprintByReference(ref)
    cy = fp.GetPosition().y
    rows = {}
    for p in fp.Pads():
        if p.GetNetname() in ("/PVDD", "/GND") and p.GetSize(pcbnew.F_Cu).x != p.GetSize(pcbnew.F_Cu).y:
            rows.setdefault(p.GetPosition().y > cy, []).append(p)
    vias = 0
    for down, row in rows.items():
        row.sort(key=lambda p: p.GetPosition().x)
        runs = [[row[0]]]
        for p in row[1:]:
            last = runs[-1][-1]
            if pcbnew.ToMM(p.GetPosition().x - last.GetPosition().x) < 0.7 and p.GetNetCode() == last.GetNetCode():
                runs[-1].append(p)
            else:
                runs.append([p])
        sign = 1 if down else -1
        for run in runs:
            if len(run) > 1:
                add_track(pcb, pcbnew, run[0].GetPosition(), run[-1].GetPosition(), 0.3, pcbnew.F_Cu, run[0].GetNet())
            half = max(run[0].GetSize(pcbnew.F_Cu).x, run[0].GetSize(pcbnew.F_Cu).y) / 2
            ends = [run[0], run[-1]] if len(run) > 1 else [run[0]]
            for k, lead in enumerate(ends):
                pos = lead.GetPosition()
                # 1st via just past the pad, 2nd one row further so 0.6 mm vias clear each other
                reach = half + pcbnew.FromMM(0.2 + 0.3 + 0.95 * k)
                via = pcbnew.VECTOR2I(pos.x, pos.y + sign * int(reach))
                FANOUT.append((add_track(pcb, pcbnew, pos, via, 0.3, pcbnew.F_Cu, lead.GetNet()),
                               add_via(pcb, pcbnew, via, lead.GetNet())))
                vias += 1
    return vias


def gnd_pad_vias(pcb, pcbnew, skip=("U1",)):
    """One via per SMD GND pad, beside the pad in the first direction that keeps 0.2 mm
    from every other-net pad and via already placed."""
    gnd = pcb.FindNet("/GND")
    clear = pcbnew.FromMM(0.2 + 0.3)  # clearance + via radius
    obstacles = [(p.GetBoundingBox(), p.GetNetCode()) for fp in pcb.GetFootprints() for p in fp.Pads()]
    placed, missed = 0, []
    for fp in pcb.GetFootprints():
        if fp.GetReference() in skip:
            continue
        for pad in fp.Pads():
            if pad.GetNetname() != "/GND" or pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                continue
            layer = pcbnew.B_Cu if fp.IsFlipped() else pcbnew.F_Cu
            bb = pad.GetBoundingBox()
            c = bb.GetCenter()
            options = [pcbnew.VECTOR2I(c.x + s * (bb.GetWidth() // 2 + clear + pcbnew.FromMM(0.05)), c.y)
                       for s in (1, -1)] + [
                pcbnew.VECTOR2I(c.x, c.y + s * (bb.GetHeight() // 2 + clear + pcbnew.FromMM(0.05)))
                for s in (1, -1)]
            for pos in options:
                hit = False
                for box, code in obstacles:
                    if code == gnd.GetNetCode():
                        continue
                    grown = pcbnew.BOX2I(box.GetOrigin(), box.GetSize())
                    grown.Inflate(clear)
                    if grown.Contains(pos):
                        hit = True
                        break
                if not hit:
                    FANOUT.append((add_track(pcb, pcbnew, c, pos, 0.4, layer, gnd),
                                   add_via(pcb, pcbnew, pos, gnd)))
                    box = pcbnew.BOX2I(pcbnew.VECTOR2I(pos.x - clear, pos.y - clear),
                                       pcbnew.VECTOR2L(2 * clear, 2 * clear))
                    obstacles.append((box, -1))  # later vias keep distance from this one
                    placed += 1
                    break
            else:
                missed.append(f"{fp.GetReference()}.{pad.GetNumber()}")
    return placed, missed


def dsn_classes(dsn, nets):
    """Width classes for the searched power nets; GND removed (carried by the planes)."""
    widths = {}
    for net in nets:
        plain = net.lstrip("/")
        if plain in POWER:
            widths[net] = POWER[plain]
        elif POWER_PATTERN.match(net):
            widths[net] = 400
    start = dsn.index("(class kicad_default")
    end = dsn.index("(circuit", start)
    members = dsn[start:end]
    for net in [*widths, "/GND"]:
        members = re.sub(r"(?<=\s)" + re.escape(net) + r"(?=\s)", "", members)
    dsn = dsn[:start] + members + dsn[end:]
    via = re.search(r'\(use_via "([^"]+)"\)', dsn).group(1)
    classes = "".join(
        f"    (class power_{w} {' '.join(n for n, x in widths.items() if x == w)}\n"
        f'      (circuit (use_via "{via}"))\n      (rule (width {w}) (clearance 250)))\n'
        for w in sorted(set(widths.values())))
    depth, i = 0, start
    while True:
        depth += {"(": 1, ")": -1}.get(dsn[i], 0)
        i += 1
        if depth == 0:
            break
    dsn = dsn[:i + 1] + classes + dsn[i + 1:]
    # Drop the GND net and every plane from the search: In1/F/B fills join it.
    dsn = re.sub(r"\(net /GND\s*\(pins[^)]*\)\)\s*", "", dsn)
    dsn = re.sub(r"\(plane [^\s]+ \(polygon[^)]*\)\)\s*", "", dsn)
    return dsn, widths


def main():
    import pcbnew

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--passes", type=int, default=20)
    ap.add_argument("--resume", action="store_true",
                    help="keep the existing copper and route only the open connections")
    args = ap.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    pcb = pcbnew.LoadBoard(str(BOARD))
    if args.resume:
        pass  # existing tracks/vias go to the DSN as fixed wiring
    elif any(True for _ in pcb.GetTracks()):
        raise SystemExit("Board already has copper; regenerate the candidate or use --resume")
    else:
        planes(pcb, pcbnew)
        tpa = fanout_tpa(pcb, pcbnew)
        placed, missed = gnd_pad_vias(pcb, pcbnew)
        removed = prune(pcb, pcbnew)
        print(f"fanout: {tpa} TPA vias, {placed} GND pad vias, {removed} pruned by DRC, "
              f"no room for {missed}")
    dsn, ses = WORK / "system.dsn", WORK / "system.ses"
    if not pcbnew.ExportSpecctraDSN(pcb, str(dsn)):
        raise SystemExit("DSN export failed")
    text, widths = dsn_classes(dsn.read_text(), [n.GetNetname() for n in pcb.GetNetsByName().values()])
    dsn.write_text(text)
    ses.unlink(missing_ok=True)
    log = WORK / "freerouting.log"
    with log.open("w") as out:
        # Freerouting 1.9 needs an AWT display even in batch mode; single-thread optimizer.
        subprocess.run(["xvfb-run", "-a", "java", "-jar", str(JAR), "-de", str(dsn), "-do", str(ses),
                        "-mp", str(args.passes), "-mt", "1"],
                       stdout=out, stderr=subprocess.STDOUT, timeout=5400, check=False)
    if not ses.exists():
        raise SystemExit(f"Freerouting produced no session; see {log}")
    if not pcbnew.ImportSpecctraSES(pcb, str(ses)):
        raise SystemExit("SES import failed")
    pcbnew.ZONE_FILLER(pcb).Fill(pcb.Zones())
    pcbnew.SaveBoard(str(BOARD), pcb)
    tracks = sum(1 for t in pcb.GetTracks() if t.GetClass() == "PCB_TRACK")
    vias = sum(1 for t in pcb.GetTracks() if t.GetClass() == "PCB_VIA")
    print(f"layout: {tracks} tracks, {vias} vias, {len(widths)} power-width nets")


if __name__ == "__main__":
    main()
