#!/usr/bin/env python3
"""Inventory the current schematic and PCB; never infer hardware approval."""
import csv
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "kicad/system-candidate/system-candidate"


def inventory(xml):
    rows = []
    for comp in ET.fromstring(xml).findall("components/comp"):
        fields = {f.get("name"): f.text or "" for f in comp.findall("fields/field")}
        properties = {p.get("name"): p.get("value", "") for p in comp.findall("property")}
        ref = comp.get("ref")
        fp = comp.findtext("footprint", "")
        dnp = "dnp" in properties
        purchase = not dnp and ref != "J6" and not fp.startswith(("TestPoint:", "MountingHole:"))
        mpn = fields.get("MPN", "")
        pending = []
        if purchase:
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9().+/_-]+", mpn) or "TBD" in mpn.upper():
                pending.append("MPN ausente ou sem normalizacao")
            if not fields.get("Manufacturer"):
                pending.append("fabricante ausente")
            if not fp:
                pending.append("footprint ausente")
        rows.append({"Reference": ref, "Value": comp.findtext("value", ""), "Footprint": fp,
                     "Manufacturer": fields.get("Manufacturer", ""), "MPN": mpn,
                     "DNP": dnp, "Purchase": purchase,
                     "LCSC": fields.get("LCSC", ""), "Pending": "; ".join(pending)})
    return rows


def main():
    import pcbnew
    out = ROOT / "build/finalization"
    out.mkdir(parents=True, exist_ok=True)
    xml = out / "netlist.xml"
    xml.unlink(missing_ok=True)
    subprocess.run(["kicad-cli", "sch", "export", "netlist", "--format", "kicadxml",
                    "-o", str(xml), str(DESIGN.with_suffix(".kicad_sch"))], check=True,
                   capture_output=True, text=True)
    rows = inventory(xml.read_text())
    board = pcbnew.LoadBoard(str(DESIGN.with_suffix(".kicad_pcb")))
    footprints = {fp.GetReference() for fp in board.GetFootprints()}
    refs = {r["Reference"] for r in rows}
    missing = sorted(refs - footprints)
    pending = [r for r in rows if r["Pending"]]
    with (ROOT / "bom/system-candidate-inventory.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    report = {"schematic_components": len(rows), "board_footprints": len(footprints),
              "missing_on_pcb": missing, "board_only": sorted(footprints - refs),
              "dnp": [r["Reference"] for r in rows if r["DNP"]],
              "purchase_positions": sum(r["Purchase"] for r in rows),
              "purchasing_metadata_pending": len(pending),
              "pending_references": [r["Reference"] for r in pending],
              "scope": "Inventory/parity and purchasing metadata, not full circuit or part qualification",
              "manufacturing_approved": False,
              "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [DESIGN.with_suffix(".kicad_sch"), DESIGN.with_suffix(".kicad_pcb"), Path(__file__)]}}
    (out / "inventory.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))
    if missing:
        raise SystemExit("Schematic components missing on PCB")


if __name__ == "__main__":
    main()
