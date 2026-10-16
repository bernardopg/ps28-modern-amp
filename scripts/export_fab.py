#!/usr/bin/env python3
"""FAB-001: fabrication/assembly package of the single board into build/fab/<commit>/.

Gerber + drill, CPL (top/bottom), BOM CSV from the schematic, schematic PDF, 1:1
template PDF (outline, holes, profile keepout, courtyards) for the physical fit check,
ERC/DRC reports and SHA-256 manifest. Generates files only: no upload, no order.
"""

import csv
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRJ = ROOT / "kicad/system-candidate"
PCB, SCH = PRJ / "system-candidate.kicad_pcb", PRJ / "system-candidate.kicad_sch"


def run(*args):
    r = subprocess.run(["kicad-cli", *args], capture_output=True, text=True)
    allowed = (0, 5) if args[:2] in (("sch", "erc"), ("pcb", "drc")) else (0,)
    if r.returncode not in allowed:
        raise SystemExit(f"kicad-cli {' '.join(args[:3])} failed: {r.stderr[-400:]}")


def write_checksums(out):
    """Write last, including summary.json; never reuse an earlier package."""
    files = sorted(p for p in out.rglob("*") if p.is_file() and p.name != "SHA256SUMS")
    (out / "SHA256SUMS").write_text("".join(
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(out)}\n" for p in files))


def main():
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT, check=True).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                               text=True, cwd=ROOT, check=True).stdout.strip())
    sources = [PCB, SCH, PRJ / "system-candidate.kicad_pro", Path(__file__),
               Path(__file__).with_name("export_mechanical_drawing.py"),
               Path(__file__).with_name("audit_final_design.py"),
               ROOT / "bom/system-candidate-accessories.csv"]
    source_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in sources}
    drafts = ROOT / "build/fab/drafts"
    drafts.mkdir(parents=True, exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix=commit[:12] + ("-dirty-" if dirty else "-"), dir=drafts))
    (out / "README.txt").write_text(
        "RASCUNHO NÃO LIBERADO — não enviar à fábrica.\n"
        "Peças selecionadas; BOM/CPL ainda exigem cotação, conversão e revisão JLCPCB.\n"
        "Somente summary.json + SHA256SUMS indicam exportação concluída, não aprovação.\n")
    (out / "gerber").mkdir()
    layers = "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts"
    run("pcb", "export", "gerbers", "--layers", layers, "--subtract-soldermask", "-o", str(out / "gerber"), str(PCB))
    run("pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th", "--generate-map",
        "--map-format", "gerberx2", "-o", str(out / "gerber") + "/", str(PCB))
    for side in ("front", "back"):
        run("pcb", "export", "pos", "--side", side, "--format", "csv", "--units", "mm",
            "--exclude-dnp", "-o", str(out / f"cpl-{side}.csv"), str(PCB))
    run("sch", "export", "bom", "--fields", "Reference,Value,Footprint,Manufacturer,MPN,Datasheet,SelectionNotes,${QUANTITY},${DNP}",
        "--group-by", "Value,Footprint,Manufacturer,MPN", "--exclude-dnp", "-o", str(out / "bom.csv"), str(SCH))
    run("sch", "export", "netlist", "--format", "kicadxml", "-o", str(out / "netlist.xml"), str(SCH))
    from audit_final_design import inventory
    purchase = [r for r in inventory((out / "netlist.xml").read_text()) if r["Purchase"]]
    if any(r["Pending"] for r in purchase):
        raise SystemExit("Incomplete purchasing metadata; draft incomplete.")
    fields = ["Reference", "Quantity", "Value", "Footprint", "Manufacturer", "MPN", "Datasheet", "SelectionNotes"]
    with (out / "purchase-bom.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: 1 if key == "Quantity" else r[key] for key in fields} for r in purchase)
    shutil.copy2(ROOT / "bom/system-candidate-accessories.csv", out / "accessories.csv")
    purchased_refs = {r["Reference"] for r in purchase}
    placed = []
    for side in ("front", "back"):
        with (out / f"cpl-{side}.csv").open() as stream:
            reader = csv.DictReader(stream)
            headers = reader.fieldnames
            positions = [r for r in reader if r["Ref"] in purchased_refs]
        placed.extend(r["Ref"] for r in positions)
        with (out / f"purchase-cpl-{side}.csv").open("w") as stream:
            writer = csv.DictWriter(stream, fieldnames=headers, lineterminator="\n")
            writer.writeheader()
            writer.writerows(positions)
    if len(placed) != len(set(placed)) or set(placed) != purchased_refs:
        raise SystemExit("Purchasing BOM/CPL references differ; draft incomplete.")
    run("sch", "export", "pdf", "-o", str(out / "schematic.pdf"), str(SCH))
    # 1:1 template: print at 100 %, check against the original board/brackets (FAB-001).
    run("pcb", "export", "pdf", "--layers", "Edge.Cuts,Dwgs.User,F.CrtYd,F.Fab", "--mode-single",
        "--scale", "1", "-o", str(out / "template-1to1.pdf"), str(PCB))
    for side, layers in (("front", "F.Fab,F.CrtYd,F.SilkS,Edge.Cuts"),
                         ("back", "B.Fab,B.CrtYd,B.SilkS,Edge.Cuts")):
        run("pcb", "export", "pdf", "--layers", layers, "--mode-single",
            "--scale", "1", "--sketch-pads-on-fab-layers", "--crossout-DNP-footprints-on-fab-layers",
            *(["--mirror"] if side == "back" else []),
            "-o", str(out / f"assembly-{side}.pdf"), str(PCB))
    run("pcb", "export", "pdf", "--layers", "F.Cu,In1.Cu,In2.Cu,B.Cu",
        "--common-layers", "Edge.Cuts", "--mode-multipage", "--scale", "1",
        "-o", str(out / "copper-layers.pdf"), str(PCB))
    run("pcb", "export", "dxf", "--layers", "Edge.Cuts,Dwgs.User", "--mode-single", "--output-units", "mm",
        "-o", str(out / "mechanical.dxf"), str(PCB))
    from export_mechanical_drawing import export, stamp_draft
    export(PCB, out / "mechanical-dimensioned-1to1.pdf")
    for name in ("template-1to1.pdf", "assembly-front.pdf", "assembly-back.pdf", "copper-layers.pdf"):
        stamp_draft(out / name, source_hashes[str(PCB.relative_to(ROOT))])
    run("sch", "erc", "--format", "json", "--severity-all", "-o", str(out / "erc.json"), str(SCH))
    run("pcb", "drc", "--format", "json", "--schematic-parity", "--refill-zones", "--severity-all",
        "-o", str(out / "drc.json"), str(PCB))
    erc = json.loads((out / "erc.json").read_text())
    drc = json.loads((out / "drc.json").read_text())
    summary = {
        "commit": commit,
        "working_tree_dirty": dirty,
        "source_sha256": source_hashes,
        "manufacturing_approved": False,
        "release_status": "DRAFT_NOT_FOR_MANUFACTURING",
        "erc_violations": sum(len(s["violations"]) for s in erc["sheets"]),
        "drc_errors": sum(v["severity"] == "error" for v in drc["violations"]),
        "drc_warnings": sum(v["severity"] == "warning" for v in drc["violations"]),
        "unconnected": len(drc["unconnected_items"]),
        "parity": len(drc.get("schematic_parity", [])),
        "purchase_positions": len(purchase),
        "purchasing_metadata_pending": 0,
        "purchase_cpl_positions": len(placed),
        "ordered": False,
    }
    if any(hashlib.sha256(p.read_bytes()).hexdigest() != source_hashes[str(p.relative_to(ROOT))]
           for p in sources):
        raise SystemExit("Sources changed during export; draft incomplete, discard it.")
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    write_checksums(out)
    print(json.dumps(summary), out)


if __name__ == "__main__":
    main()
