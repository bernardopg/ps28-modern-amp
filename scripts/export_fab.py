#!/usr/bin/env python3
"""FAB-001: fabrication/assembly package of the single board into build/fab/<commit>/.

Gerber + drill, CPL (top/bottom), BOM CSV from the schematic, schematic PDF, 1:1
template PDF (outline, holes, profile keepout, courtyards) for the physical fit check,
ERC/DRC reports and SHA-256 manifest. Generates files only: no upload, no order.
"""

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRJ = ROOT / "kicad/system-candidate"
PCB, SCH = PRJ / "system-candidate.kicad_pcb", PRJ / "system-candidate.kicad_sch"


def run(*args):
    r = subprocess.run(["kicad-cli", *args], capture_output=True, text=True)
    if r.returncode not in (0, 5):  # 5 = DRC/ERC found violations; judged from the report
        raise SystemExit(f"kicad-cli {' '.join(args[:3])} failed: {r.stderr[-400:]}")


def main():
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    out = ROOT / "build/fab" / commit
    (out / "gerber").mkdir(parents=True, exist_ok=True)
    layers = "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts"
    run("pcb", "export", "gerbers", "--layers", layers, "--subtract-soldermask", "-o", str(out / "gerber"), str(PCB))
    run("pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th", "--generate-map",
        "--map-format", "gerberx2", "-o", str(out / "gerber") + "/", str(PCB))
    for side in ("front", "back"):
        run("pcb", "export", "pos", "--side", side, "--format", "csv", "--units", "mm",
            "--exclude-dnp", "-o", str(out / f"cpl-{side}.csv"), str(PCB))
    run("sch", "export", "bom", "--fields", "Reference,Value,Footprint,MPN,${QUANTITY},${DNP}",
        "--group-by", "Value,Footprint,MPN", "--exclude-dnp", "-o", str(out / "bom.csv"), str(SCH))
    run("sch", "export", "pdf", "-o", str(out / "schematic.pdf"), str(SCH))
    # 1:1 template: print at 100 %, check against the original board/brackets (FAB-001).
    run("pcb", "export", "pdf", "--layers", "Edge.Cuts,Dwgs.User,F.CrtYd,F.Fab", "--mode-single",
        "--include-border-title", "-o", str(out / "template-1to1.pdf"), str(PCB))
    run("sch", "erc", "--format", "json", "--severity-all", "-o", str(out / "erc.json"), str(SCH))
    run("pcb", "drc", "--format", "json", "--schematic-parity", "--refill-zones", "--severity-all",
        "-o", str(out / "drc.json"), str(PCB))
    erc = json.loads((out / "erc.json").read_text())
    drc = json.loads((out / "drc.json").read_text())
    summary = {
        "commit": commit,
        "erc_violations": sum(len(s["violations"]) for s in erc["sheets"]),
        "drc_errors": sum(v["severity"] == "error" for v in drc["violations"]),
        "drc_warnings": sum(v["severity"] == "warning" for v in drc["violations"]),
        "unconnected": len(drc["unconnected_items"]),
        "parity": len(drc.get("schematic_parity", [])),
        "ordered": False,
    }
    files = sorted(p for p in out.rglob("*") if p.is_file() and p.name != "SHA256SUMS")
    (out / "SHA256SUMS").write_text("".join(
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(out)}\n" for p in files))
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary), out)


if __name__ == "__main__":
    main()
