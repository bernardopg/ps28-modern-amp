#!/usr/bin/env python3
"""Initial unrouted PCB placement from actual KiCad-exported XML connectivity.
Default output: build/core-draft/ps28-modern.kicad_pcb. --apply only over empty PCB.
Requires the installed KiCad pcbnew bindings. Never regenerates an edited/routed PCB.
"""

from pathlib import Path
import argparse
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    import pcbnew

    directory = ROOT / "build/core-draft"
    directory.mkdir(exist_ok=True)
    xml = directory / "core.xml"
    xml.unlink(missing_ok=True)
    result = subprocess.run(
        [
            "kicad-cli",
            "sch",
            "export",
            "netlist",
            "--format",
            "kicadxml",
            "--output",
            str(xml),
            str(ROOT / "kicad/ps28-modern.kicad_sch"),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    (directory / "xml-export.log").write_text(result.stdout + result.stderr)
    if result.returncode or not xml.exists():
        raise RuntimeError("Cannot export schematic connectivity")
    graph = ET.parse(xml).getroot()
    target = ROOT / "kicad/ps28-modern.kicad_pcb"
    board = pcbnew.LoadBoard(str(target))
    if args.apply and (list(board.GetFootprints()) or list(board.GetTracks())):
        raise SystemExit(
            "Refusing to replace nonempty PCB. Continue in KiCad, not generator."
        )
    if args.apply and (list(board.GetDrawings()) or list(board.Zones())):
        raise SystemExit("Refusing to replace existing geometry/zones")
    board = pcbnew.BOARD()  # Preview regeneration never changes existing PCB buffers.
    board.SetCopperLayerCount(4)
    title = board.GetTitleBlock()
    title.SetTitle("PS28 TPA3255 CORE - UNROUTED DRAFT")
    title.SetRevision("A-core-draft")
    title.SetComment(0, "NOT FOR FABRICATION - POWER SUPPLY / FRONT-END NOT INCLUDED")
    board.SetTitleBlock(title)
    manifest = json.loads((ROOT / "kicad/core-manifest.json").read_text())
    metadata = {p["ref"]: p for p in manifest["parts"]}
    nets = {}
    mapping = {}
    for net in graph.findall("./nets/net"):
        name = net.attrib["name"]
        item = pcbnew.NETINFO_ITEM(board, name, int(net.attrib["code"]))
        board.Add(item)
        nets[name] = item
        for node in net.findall("node"):
            mapping[(node.attrib["ref"], node.attrib["pin"])] = name
    placed, missing = [], []
    for component in graph.findall("./components/comp"):
        ref = component.attrib["ref"]
        if ref not in metadata:
            continue
        part = metadata[ref]
        lib_id = component.findtext("footprint", default="")
        if not lib_id:
            missing.append(ref)
            continue
        if lib_id != part["footprint"] or not part["pcb_position"]:
            raise ValueError(f"Footprint/position metadata mismatch: {ref}")
        library, name = lib_id.split(":", 1)
        fp = pcbnew.FootprintLoad(
            str(Path("/usr/share/kicad/footprints") / (library + ".pretty")), name
        )
        if fp is None:
            raise ValueError(f"Library footprint unavailable: {ref} {lib_id}")
        fp.SetFPID(pcbnew.LIB_ID(library, name))
        fp.SetReference(ref)
        fp.SetValue(component.findtext("value"))
        for field in component.findall("./fields/field"):
            key = field.attrib.get("name", "")
            if key in {"SelectionStatus", "Source"}:
                fp.SetField(key, field.text or "")
                fp.GetField(key).SetVisible(False)
        fp.Value().SetVisible(False)
        x, y = part["pcb_position"]
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        fp.SetOrientationDegrees(0)
        path = pcbnew.KIID_PATH()
        path.push_back(pcbnew.KIID(manifest["schematic_uuid"]))
        path.push_back(
            pcbnew.KIID(component.findtext("tstamps").strip("/").split("/")[-1])
        )
        fp.SetPath(path)
        for pad in fp.Pads():
            number = pad.GetNumber()
            net_name = mapping.get((ref, number))
            if net_name:
                pad.SetNet(nets[net_name])
            elif number:
                raise ValueError(f"Footprint pad missing schematic net: {ref}.{number}")
        board.Add(fp)
        placed.append(ref)

    def point(x, y):
        return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))

    def rectangle(x1, y1, x2, y2, layer, width=0.05):
        for a, b in [
            ((x1, y1), (x2, y1)),
            ((x2, y1), (x2, y2)),
            ((x2, y2), (x1, y2)),
            ((x1, y2), (x1, y1)),
        ]:
            line = pcbnew.PCB_SHAPE()
            line.SetShape(pcbnew.SHAPE_T_SEGMENT)
            line.SetStart(point(*a))
            line.SetEnd(point(*b))
            line.SetWidth(pcbnew.FromMM(width))
            line.SetLayer(layer)
            board.Add(line)

    def note(text, x, y, size=1):
        item = pcbnew.PCB_TEXT(board)
        item.SetText(text)
        item.SetPosition(point(x, y))
        item.SetTextSize(point(size, size))
        item.SetTextThickness(pcbnew.FromMM(0.15))
        item.SetLayer(pcbnew.Dwgs_User)
        board.Add(item)

    rectangle(20, 20, 165, 115, pcbnew.Edge_Cuts)
    rectangle(95, 32, 124, 54, pcbnew.Dwgs_User)
    rectangle(95, 68, 124, 90, pcbnew.Dwgs_User)
    rectangle(60, 44, 92, 80, pcbnew.Dwgs_User)
    note("L1 reservation only - MPN/pads TBD", 110, 42, 0.8)
    note("L2 reservation only - MPN/pads TBD", 110, 78, 0.8)
    note("TOP HEATSINK: envelope/bond/fixing TBD", 76, 40, 0.8)
    note("PVDD bulk + connector reservation", 45, 27, 0.8)
    note("UNROUTED CORE ONLY - NOT FOR FABRICATION", 94, 108, 1.3)
    note(
        "145 x 95 mm provisional outline; NOT a measured mechanical envelope",
        97,
        112,
        0.8,
    )
    output = directory / "ps28-modern.kicad_pcb"
    pcbnew.SaveBoard(str(output), board)
    report = {
        "placed": placed,
        "missing_footprints": missing,
        "routed": False,
        "mechanical_approved": False,
        "manufacturing_approved": False,
    }
    (directory / "placement.json").write_text(json.dumps(report, indent=2) + "\n")
    if args.apply:
        shutil.copy2(output, target)
    print(
        f"{len(placed)} footprints placed from schematic; {len(missing)} intentionally unassigned; no tracks."
    )


if __name__ == "__main__":
    main()
