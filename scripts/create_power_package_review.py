#!/usr/bin/env python3
"""Captura D-021 de revisão, sem sobrescrever a candidata roteada.

Retira seleções contraditórias; não escolhe componentes sem fonte primária.
Onsemi MUR3020WT/D Rev.7 p.2: MUR3040WT IFSM=150 A, não 200 A.
"""
import argparse
import hashlib
import json
from pathlib import Path

from create_analog_capture import build
from create_power_d021 import parts, tps3700_symbol, write_local_library
from simulate_opa1656 import ROOT


def reviewed_parts():
    result = parts()
    for p in result:
        ref = p["ref"]
        if ref in ("D301", "D302"):
            p.update(value="RECT TBD >=400V >=200A surge", footprint="", mpn=
                     "TBD: VRRM>=400 V, IFSM>=200 A; MUR3040WTG rejected: IFSM=150 A per leg (onsemi MUR3020WT/D Rev.7 p.2). Symbol is a functional two-terminal placeholder, NOT the dual MUR package.")
        elif ref in ("C301", "C302"):
            p.update(value="4700u >=63V TBD", footprint="", mpn=
                     "TBD: >=105 C, ripple>=3.5 A rms at 120 Hz; previous Rubycon candidate declared 85 C/3.49 A/D30, not qualified. No D25 footprint substitution.")
        elif ref == "F301":
            p.update(value="T TBD", mpn=
                     "TBD: exact time-lag fuse, DC breaking rating and I2t coordination; CT branch RMS and measured inrush required. 6.3 A not selected.")
        elif ref == "J301":
            p.update(footprint="", mpn=
                     "TBD: exact three-position header mating OEM harness; pin order 1=T1_A, 2=T1_CT, 3=T1_B preserved. VHR-4N not selected; SVH terminal alone does not identify PCB header.")
        elif ref == "D303":
            p["mpn"] = ("Littelfuse SMCJ51A candidate only: Vc=82.4 V exceeds TPA3255 PVDD abs max 69 V; "
                        "NOT qualified OVP. RAILS_OK/RESET do not disconnect PVDD; transient/OVP design TBD.")
    return result


def generate(out):
    if out.exists():
        raise FileExistsError(f"Refusing to overwrite {out}")
    sch, manifest = build(
        reviewed_parts(), project="power-package-review", namespace="power-package-review",
        source="D-021 package review; onsemi MUR3020WT/D Rev.7 p.1-2; NOT FOR FABRICATION",
        title="PS28 POWER PACKAGE REVIEW - BLOCKED",
        warning="UNQUALIFIED RECTIFIERS/BULK/CONNECTOR/FUSE. RESET DOES NOT DISCONNECT PVDD. NO FABRICATION.",
        power_flags=("PVDD", "GND", "AUX_RAW"),
        extra_symbols={"PS28_POWER:TPS3700DDC": tps3700_symbol()},
    )
    out.mkdir(parents=True)
    (out / "power-package-review.kicad_sch").write_text(sch)
    (out / "power-package-review.kicad_pro").write_text("{}\n")
    write_local_library(out, "PS28_POWER", [tps3700_symbol()], "TPS3700 DDC pinout from TI")
    manifest.update(manufacturing_approved=False, hardware_validated=False,
                    status="BLOCKED: incomplete package selection; no PCB placement generated",
                    rejected_mpn={"MUR3040WTG": {"ifsm_a_per_leg": 150, "required_a": 200,
                                  "source": "onsemi MUR3020WT/D Rev.7 p.2"}})
    sources = [Path(__file__), ROOT / "scripts/create_power_d021.py",
               ROOT / "reference/parts/onsemi-mur3020wtg.pdf"]
    manifest["source_sha256"] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sources}
    (out / "review-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build/power-package-review/capture")
    generate(parser.parse_args().output)
