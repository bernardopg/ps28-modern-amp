#!/usr/bin/env python3
"""Autoroute the system candidate with Freerouting (study only, NOT a reviewed layout).

Stackup 4 layers: In1.Cu = solid GND plane (KiCad zone); F.Cu, In2.Cu, B.Cu signal,
GND also routed as a net so every pad has a path (Freerouting plane handling skips SMD pads).
Power nets get wider tracks via a DSN class. Freerouting jar must be supplied
(build/tools/, not versioned). Class-D loops, current density and EMI still need
manual layout review (PCB-002); an autorouted board is not fabrication-ready.
"""

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "kicad/system-candidate/system-candidate.kicad_pcb"
JAR = ROOT / "build/tools/freerouting-1.9.0.jar"
WORK = ROOT / "build/route"

# Track width in um per net, study values: PVDD/OUT/SPK/T1 carry several amperes.
# shortcut: 0.5-1.0 mm is what the autorouter can complete out of 0.635 mm TPA pins;
# replace with PVDD/OUT copper pours in the manual review (PCB-002).
POWER = {"PVDD": 500, "SPK_P": 1000, "SPK_N": 1000, "T1_A": 1000, "T1_B": 1000, "T1_CT": 1000,
         "BUCK_SW": 600, "AUX_RAW": 600}
POWER_PATTERN = re.compile(r"^/PWM_(AC|BD)$")  # PBTL bridge outputs


def prepare(pcb, pcbnew):
    pcb.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    bb = pcb.GetBoardEdgesBoundingBox()
    zone = pcbnew.ZONE(pcb)
    zone.SetLayer(pcbnew.In1_Cu)
    zone.SetNet(pcb.FindNet("/GND"))
    zone.SetZoneName("GND_PLANE")
    zone.SetLocalClearance(pcbnew.FromMM(0.3))
    zone.SetMinThickness(pcbnew.FromMM(0.25))
    zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    poly = pcbnew.SHAPE_POLY_SET()
    poly.NewOutline()
    for x, y in [(bb.GetLeft(), bb.GetTop()), (bb.GetRight(), bb.GetTop()),
                 (bb.GetRight(), bb.GetBottom()), (bb.GetLeft(), bb.GetBottom())]:
        poly.Append(pcbnew.VECTOR2I(x, y))
    zone.SetOutline(poly)
    poly.thisown = False
    pcb.Add(zone)


def bridge_adjacent_pads(pcb, pcbnew, pitch_mm=0.7, width_mm=0.3):
    """Join neighbouring same-net pads of one footprint (fine-pitch power pins) on their layer.

    Freerouting cannot neck a 1.5-2 mm power track into a 0.635 mm pitch; KiCad shorts
    such pins with a pad-width strap, as the TI layout guide does for PVDD/OUT pins.
    """
    added = 0
    for fp in pcb.GetFootprints():
        pads = [p for p in fp.Pads() if p.GetNetname() and p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
        for i, a in enumerate(pads):
            for b in pads[i + 1:]:
                if a.GetNetCode() != b.GetNetCode() or a.GetLayer() != b.GetLayer():
                    continue
                if pcbnew.ToMM((a.GetPosition() - b.GetPosition()).EuclideanNorm()) > pitch_mm:
                    continue
                t = pcbnew.PCB_TRACK(pcb)
                t.SetStart(a.GetPosition())
                t.SetEnd(b.GetPosition())
                t.SetWidth(pcbnew.FromMM(width_mm))
                t.SetLayer(a.GetLayer())
                t.SetNet(a.GetNet())
                pcb.Add(t)
                added += 1
    return added


def power_class(dsn, nets):
    """Move power nets out of kicad_default into width classes (DSN units: um)."""
    widths = {}
    for net in nets:
        plain = net.lstrip("/")
        if plain in POWER:
            widths[net] = POWER[plain]
        elif POWER_PATTERN.match(net):
            widths[net] = 500  # PWM_AC/BD leave 0.4 mm TPA pads
    start = dsn.index("(class kicad_default")
    end = dsn.index("(circuit", start)
    members = dsn[start:end]
    for net in widths:
        members = re.sub(r"(?<=\s)" + re.escape(net) + r"(?=\s)", "", members)
    dsn = dsn[:start] + members + dsn[end:]
    via = re.search(r'\(use_via "([^"]+)"\)', dsn).group(1)
    classes = "".join(
        f"    (class power_{w} {' '.join(n for n, x in widths.items() if x == w)}\n"
        f'      (circuit (use_via "{via}"))\n      (rule (width {w}) (clearance 300)))\n'
        for w in sorted(set(widths.values())))
    depth, i = 0, start  # find the closing paren of the kicad_default class
    while True:
        depth += {"(": 1, ")": -1}.get(dsn[i], 0)
        i += 1
        if depth == 0:
            break
    insert_at = i + 1
    return dsn[:insert_at] + classes + dsn[insert_at:], widths


def main():
    import pcbnew

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--passes", type=int, default=30)
    ap.add_argument("--resume", action="store_true", help="continue from existing tracks")
    args = ap.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    pcb = pcbnew.LoadBoard(str(BOARD))
    if any(t for t in pcb.GetTracks()) and not args.resume:
        raise SystemExit("Board already has tracks; regenerate the candidate or use --resume")
    if not args.resume:
        prepare(pcb, pcbnew)
        bridge_adjacent_pads(pcb, pcbnew)
    dsn, ses = WORK / "system.dsn", WORK / "system.ses"
    if not pcbnew.ExportSpecctraDSN(pcb, str(dsn)):
        raise SystemExit("DSN export failed")
    text, widths = power_class(dsn.read_text(), [n.GetNetname() for n in pcb.GetNetsByName().values()])
    # Freerouting 1.9 leaves SMD pads of a plane net unconnected: route GND as a normal
    # net on the signal layers; the KiCad In1 zone still floods and joins its vias.
    text = re.sub(r"\(plane /GND \(polygon[^)]*\)\)\s*", "", text)
    dsn.write_text(text)
    ses.unlink(missing_ok=True)
    log = WORK / "freerouting.log"
    with log.open("w") as out:
        # Freerouting 1.9 needs an AWT display even in batch mode: run it under Xvfb.
        subprocess.run(["xvfb-run", "-a", "java", "-jar", str(JAR), "-de", str(dsn), "-do", str(ses),
                        "-mp", str(args.passes), "-mt", "1"],  # multi-thread optimizer breaks clearance
                       stdout=out, stderr=subprocess.STDOUT, timeout=3600, check=False)
    if not ses.exists():
        raise SystemExit(f"Freerouting produced no session; see {log}")
    if not pcbnew.ImportSpecctraSES(pcb, str(ses)):
        raise SystemExit("SES import failed")
    pcbnew.ZONE_FILLER(pcb).Fill(pcb.Zones())
    pcbnew.SaveBoard(str(BOARD), pcb)
    tracks = sum(1 for t in pcb.GetTracks() if t.GetClass() == "PCB_TRACK")
    vias = sum(1 for t in pcb.GetTracks() if t.GetClass() == "PCB_VIA")
    print(f"routed: {tracks} tracks, {vias} vias, {len(widths)} power nets; NOT a reviewed layout")


if __name__ == "__main__":
    main()
