#!/usr/bin/env python3
"""Fail closed for empty EDA. Rule checks are not release approval."""

from pathlib import Path
import argparse
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def has_design(text, kind):
    pattern = r"\(symbol\s+\(lib_id\s" if kind == "erc" else r'\(footprint\s+"'
    return bool(re.search(pattern, text))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=["erc", "drc"])
    parser.add_argument("--design", type=Path, default=Path("kicad/system-candidate/system-candidate"),
                        help="Caminho base sem extensão; padrão é a placa única atual, nunca fallback histórico.")
    args = parser.parse_args()
    out = ROOT / "build"
    report = out / f"{args.kind}.json"
    report.unlink(missing_ok=True)  # Never reuse a report after an empty/invalid input.
    ext = "sch" if args.kind == "erc" else "pcb"
    design = args.design if args.design.is_absolute() else ROOT / args.design
    path = design.with_suffix(f".kicad_{ext}")
    if not path.exists() or not has_design(path.read_text(), args.kind):
        print("BLOCKED: empty EDA container; no circuit to validate.", file=sys.stderr)
        return 2
    out.mkdir(exist_ok=True)
    command = [
        "kicad-cli",
        "sch" if args.kind == "erc" else "pcb",
        args.kind,
        "--exit-code-violations",
        "--severity-all",
        "--format",
        "json",
        "--output",
        str(out / f"{args.kind}.json"),
    ]
    if args.kind == "drc":
        command.extend(["--schematic-parity", "--refill-zones"])
    command.append(str(path))
    result = subprocess.run(command, cwd=ROOT, timeout=180)
    print("Rule-check result only; human gates still required.")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
