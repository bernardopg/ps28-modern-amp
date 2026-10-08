#!/usr/bin/env python3
"""Capture D-018 power/bias block separately; never overwrite original analog capture."""

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from create_analog_capture import build, opamp_symbol
from create_analog_capture import parts as analog_parts
from create_core_draft import q, render
from simulate_opa1656 import ROOT

DESIGN = ROOT / "kicad/vmid-protected"
SOURCE = "D-018: isolated ANALOG_12V/passive VMID; declared envelope only; no hardware sign-off"


def parts():
    specs = [
        (
            "D201",
            "Device:D",
            "1N4007",
            "1N4007-E3/54",
            "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal",
            {"1": "ISO_FEED", "2": "AUX_RAW"},
        ),
        (
            "R201",
            "Device:R",
            "15",
            "TBD: >=0.1J input-charge pulse qualification",
            "",
            {"1": "ISO_FEED", "2": "ANALOG_12V"},
        ),
        ("R202", "Device:R", "1k", "TBD", "", {"1": "AUX_RAW", "2": "GND"}),
        ("R203", "Device:R", "2.2k", "TBD", "", {"1": "ANALOG_12V", "2": "GND"}),
        (
            "R204",
            "Device:R",
            "75",
            "CRCW120675R0FKEA",
            "Resistor_SMD:R_1206_3216Metric",
            {"1": "ANALOG_12V", "2": "DIV_TOP"},
        ),
        (
            "R205",
            "Device:R",
            "75",
            "CRCW120675R0FKEA",
            "Resistor_SMD:R_1206_3216Metric",
            {"1": "DIV_TOP", "2": "VMID"},
        ),
        (
            "R206",
            "Device:R",
            "75",
            "CRCW120675R0FKEA",
            "Resistor_SMD:R_1206_3216Metric",
            {"1": "VMID", "2": "DIV_BOTTOM"},
        ),
        (
            "R207",
            "Device:R",
            "75",
            "CRCW120675R0FKEA",
            "Resistor_SMD:R_1206_3216Metric",
            {"1": "DIV_BOTTOM", "2": "GND"},
        ),
        (
            "C201",
            "Device:C_Polarized",
            "470u",
            "860020575014",
            "PS28:WE_860020575014",
            {"1": "ANALOG_12V", "2": "GND"},
        ),
        (
            "C202",
            "Device:C_Polarized",
            "470u",
            "860020575014",
            "PS28:WE_860020575014",
            {"1": "ANALOG_12V", "2": "GND"},
        ),
        (
            "C203",
            "Device:C",
            "1u",
            "TBD: total VMID storage <=2uF, ESR<=2ohm",
            "",
            {"1": "VMID", "2": "GND"},
        ),
        (
            "J201",
            "Connector_Generic:Conn_01x02",
            "RAW_AUX_INPUT",
            "TBD",
            "",
            {"1": "AUX_RAW", "2": "GND"},
        ),
        (
            "J202",
            "Connector_Generic:Conn_01x03",
            "PROTECTED_ANALOG_OUTPUT",
            "TBD",
            "",
            {"1": "ANALOG_12V", "2": "VMID", "3": "GND"},
        ),
    ]
    result = []
    for i, (ref, lib, value, mpn, foot, nets) in enumerate(specs):
        result.append(
            {
                "ref": ref,
                "lib_id": lib,
                "value": value,
                "mpn": mpn,
                "footprint": foot,
                "nets": nets,
                "units": [(1, 50.8 + (i % 4) * 88.9, 40.64 + (i // 4) * 55.88)],
            }
        )
    return result


def integrated_parts():
    base = analog_parts()
    for p in base:
        p["nets"] = {
            pin: {"AUX_12V": "ANALOG_12V", "VMID_EXTERNAL": "VMID"}.get(net, net)
            for pin, net in p["nets"].items()
        }
        if p["ref"] == "J103":
            p["nets"]["1"] = "AUX_RAW"
            p["value"] = "RAW_AUX_IN / VMID_MONITOR"
    power = [p for p in parts() if not p["ref"].startswith("J")]
    for i, p in enumerate(power):
        p["units"] = [(1, 457.2 + (i % 2) * 63.5, 40.64 + (i // 2) * 38.1)]
    return base + power


def generate(out, integrated=False):
    if out.exists():
        raise FileExistsError("Refusing to overwrite existing protection capture")
    out.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix=".vmid-protected-", dir=out.parent))
    try:
        project = "analog-protected" if integrated else "vmid-protected"
        sch, manifest = build(
            integrated_parts() if integrated else parts(),
            project=project,
            namespace=project,
            source=SOURCE,
            title="PS28 D-018 POWER/VMID BLOCK - PROTOTYPE ENVELOPE ONLY",
            warning="LOGICAL BLOCK FOR SAME OEM PCB - POWER-OFF EXTERNAL SIGNAL INPUTS/SUPERVISOR/PULSE/ESR QUALIFICATION PENDING",
            power_flags=("AUX_RAW", "ANALOG_12V", "GND"),
            paper="A2" if integrated else "A3",
        )
        manifest["interface_contract"] = {
            "J201": "Regulated raw AUX10.8-13.2V, not PVDD or transformer",
            "J202": "All front-end opamp V+ MUST use ANALOG_12V, not raw AUX; VMID load <=1mA, total effective C<=2uF",
            "new_physical_board": False,
        }
        (staged / (project + ".kicad_sch")).write_text(sch)
        if integrated:
            manifest["interface_contract"] = {
                "J103": "1=AUX_RAW;2=VMID monitoring only;3=GND; never drive VMID externally",
                "all_opamp_vplus": "ANALOG_12V only; no raw AUX connection",
                "new_physical_board": False,
            }
        (staged / "vmid-manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n"
        )
        (staged / (project + ".kicad_pro")).write_text("{}\n")
        libs = staged / "libraries"
        libs.mkdir()
        (libs / "PS28_ANALOG.kicad_sym").write_text(
            '(kicad_symbol_lib (version 20241209) (generator "ps28")\n'
            + render([opamp_symbol()[0], q("OPA1656ID"), *opamp_symbol()[2:]])
            + "\n)\n"
        )
        (staged / "sym-lib-table").write_text(
            '(sym_lib_table (version 7) (lib (name "PS28_ANALOG") (type "KiCad") (uri "${KIPRJMOD}/libraries/PS28_ANALOG.kicad_sym") (options "") (descr "Audited local symbol reuse")))\n'
        )
        # Existing audited cap land, not a new global registration.
        if out.parent.resolve() == (ROOT / "kicad").resolve():
            (staged / "fp-lib-table").write_text(
                '(fp_lib_table (version 7) (lib (name "PS28") (type "KiCad") (uri "${KIPRJMOD}/../core-selected/libraries/PS28.pretty") (options "") (descr "Existing audited core footprints")))\n'
            )
        staged.rename(out)
    except BaseException:
        shutil.rmtree(staged, ignore_errors=True)
        raise


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--integrated", action="store_true")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    generate(
        args.output or (ROOT / "kicad/analog-protected" if args.integrated else DESIGN),
        args.integrated,
    )
