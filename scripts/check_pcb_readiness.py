#!/usr/bin/env python3
"""Auditoria conservadora da candidata; nunca libera fabricação nem modifica EDA."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "kicad/system-candidate/system-candidate"


def audit_parts(parts):
    """Checagens específicas de contradições D-025; não qualifica alternativas."""
    findings = []
    by_ref = {p["ref"]: p for p in parts}

    def block(code, ref, message):
        findings.append({"code": code, "ref": ref, "message": message})

    for ref in ("D301", "D302", "C301", "C302", "F301", "J301"):
        if ref not in by_ref:
            block("missing_part", ref, "Componente de potência ausente.")
    for p in parts:
        ref, mpn = p["ref"], p.get("mpn", "")
        footprint = p.get("footprint", "")
        if not footprint:
            block("missing_footprint", ref, "Footprint ausente.")
        if not mpn or "TBD" in mpn or "not audited" in mpn:
            block("unqualified_mpn", ref, "MPN/qualificação pendente; não é linha de BOM liberada.")
        if "MUR3040WTG" in mpn:
            block("rectifier_surge_requirement_failed", ref,
                  "MUR3040WT/D Rev.7 p.2: MUR3040WTG IFSM=150 A por junção, abaixo do requisito 200 A; trocar footprint não resolve.")
        if "MUR3040WTG" in mpn and "D_P600" in footprint:
            block("rectifier_package_mismatch", ref,
                  "MPN MUR3040WTG atribuído a diodo axial P600; auditar símbolo, pads, encapsulamento e térmica antes de rotear.")
        if "D30xL30" in mpn and "D25.0mm" in footprint:
            block("bulk_body_mismatch", ref,
                  "Corpo declarado Ø30 mm associado a footprint Ø25 mm; refazer courtyard/fit após auditoria do fabricante.")
        if "VHR-4N" in mpn and "1x03" in footprint:
            block("connector_positions_mismatch", ref,
                  "Housing VHR-4N informado com header de 3 posições; terminal de crimp não define o header da PCB.")
        if ref == "F301" and "T6.3A" in p.get("value", "") and "measured inrush" in mpn:
            block("fuse_rating_unqualified", ref,
                  "6,3 A apresentado como valor, mas I²t/inrush e MPN exato continuam pendentes.")
    return findings


def audit_drc(report):
    """Não confundir ausência de curto com conectividade/paridade completa."""
    result = []
    for key in ("violations", "unconnected_items", "schematic_parity"):
        entries = report.get(key)
        if not isinstance(entries, list):
            raise ValueError(f"Relatório DRC incompleto: {key}")
        if entries:
            result.append({"code": key, "count": len(entries),
                           "types": dict(Counter(e.get("type", "unknown") for e in entries))})
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=ROOT / "build/readiness/pcb-readiness.json")
    args = ap.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    drc_path = args.output.with_name("native-drc.json")
    # Remove relatório anterior para não aceitar evidência velha se KiCad falhar.
    drc_path.unlink(missing_ok=True)
    command = ["kicad-cli", "pcb", "drc", "--format", "json", "--severity-all",
               "--schematic-parity", "--refill-zones", "--output", str(drc_path),
               str(DESIGN.with_suffix(".kicad_pcb"))]
    report = {"manufacturing_approved": False, "scope": "Auditoria parcial; não sign-off G1/G2/G3",
              "drc_command": command, "blockers": []}
    sources = [DESIGN.with_suffix(ext) for ext in (".kicad_pcb", ".kicad_sch", ".kicad_pro")]
    manifest_path = DESIGN.parent / "system-manifest.json"
    sources.extend([manifest_path, Path(__file__)])
    try:
        manifest = json.loads(manifest_path.read_text())
        report["blockers"].extend(audit_parts(manifest["parts"]))
        subprocess.run(command, check=True, capture_output=True, text=True)
        report["blockers"].extend(audit_drc(json.loads(drc_path.read_text())))
        sources.append(drc_path)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        report["blockers"].append({"code": "audit_failed", "message": str(exc)})
    report["blockers"].append({"code": "human_review_required", "message":
        "Auditar OVP/transientes, inrush, D-022 completo, placement crítico, térmica e BOM; G0–G5 continuam pendentes."})
    report["source_sha256"] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sources if p.exists() and p.is_relative_to(ROOT)}
    report["status"] = "BLOCKED"
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(f"BLOCKED: {len(report['blockers'])} achados/grupos; {args.output}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
