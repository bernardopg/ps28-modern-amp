#!/usr/bin/env python3
"""Check native KiCad analog netlist against independently specified simulated topology."""

import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "kicad/analog-front-end"
ALIASES = {
    "MONO_BIASED": "input",
    "DIVIDED": "divided",
    "BUFFERED": "buffered",
    "X1": "x1",
    "Y1": "y1",
    "FILTERED1": "filtered1",
    "X2": "x2",
    "Y2": "y2",
    "DIFF_POS": "positive",
    "DIFF_NEG": "negative",
    "MINUS": "minus",
    "VMID_EXTERNAL": "mid",
    "AUX_12V": "supply",
    "GND": "0",
}
SPICE_REFS = {
    "R101": "RATT",
    "R102": "RBIAS",
    "R103": "R11",
    "R104": "R12",
    "R105": "R21",
    "R106": "R22",
    "R107": "RINV",
    "R108": "RF",
    "C101": "CF11",
    "C102": "CF12",
    "C103": "CG1",
    "C104": "CF21",
    "C105": "CF22",
    "C106": "CG2",
}
OPA_EXPECTED = {
    "U2": {
        "1": "buffered",
        "2": "buffered",
        "3": "divided",
        "4": "0",
        "5": "y1",
        "6": "filtered1",
        "7": "filtered1",
        "8": "supply",
    },
    "U3": {
        "1": "positive",
        "2": "positive",
        "3": "y2",
        "4": "0",
        "5": "mid",
        "6": "minus",
        "7": "negative",
        "8": "supply",
    },
}


def verify(xml, manifest, spice):
    tree = ET.fromstring(xml)
    components = {
        n.attrib["ref"]: n
        for n in tree.findall("components/comp")
        if not n.attrib["ref"].startswith("#")
    }
    expected = {p["ref"]: p for p in manifest["parts"]}
    if set(components) != set(expected):
        raise ValueError("Native component set mismatch")
    pins = {}
    for net in tree.findall("nets/net"):
        name = net.attrib["name"].rsplit("/", 1)[-1]
        for node in net.findall("node"):
            if not node.attrib["ref"].startswith("#"):
                key = (node.attrib["ref"], node.attrib["pin"])
                if key in pins:
                    raise ValueError("Duplicate pin in exported nets")
                pins[key] = name
    for ref, p in expected.items():
        if components[ref].findtext("value") != p["value"]:
            raise ValueError("Native value mismatch: " + ref)
        if (components[ref].findtext("footprint") or "") != p["footprint"]:
            raise ValueError("Native footprint mismatch: " + ref)
        for pin, net in p["nets"].items():
            if pins.get((ref, pin)) != net:
                raise ValueError("Native connectivity mismatch: " + ref + "." + pin)
    if len(pins) != sum(len(p["nets"]) for p in expected.values()):
        raise ValueError("Unexpected native pin count")
    lines = {
        s.split()[0].upper(): s.split()
        for s in spice.splitlines()
        if s.strip() and s[0].upper() in "RC" and not s.startswith("*")
    }
    for ref, sref in SPICE_REFS.items():
        a, b = lines[sref][1:3]
        if ALIASES[pins[(ref, "1")]] != a or ALIASES[pins[(ref, "2")]] != b:
            raise ValueError("KiCad vs SPICE passive wiring mismatch: " + ref)
        value = expected[ref]["value"]
        numeric = (
            float(value[:-1]) * 1000
            if value.endswith("k")
            else float(value[:-1]) * 1e-9
        )
        if abs(numeric - float(lines[sref][3])) > abs(numeric) * 1e-12:
            raise ValueError("KiCad vs SPICE R/C value mismatch: " + ref)
    for ref, table in OPA_EXPECTED.items():
        for pin, net in table.items():
            if ALIASES[pins[(ref, pin)]] != net:
                raise ValueError("TI SOIC8 pin mapping differs: " + ref + "." + pin)
        mpn = next(
            (
                x.text
                for x in components[ref].findall("fields/field")
                if x.attrib.get("name") == "MPN"
            ),
            None,
        )
        if mpn != "OPA1656ID":
            raise ValueError("Incorrect candidate opamp MPN")
    return {
        "components": len(components),
        "native_pins_checked": len(pins),
        "passives_matched_to_spice": len(SPICE_REFS),
        "opamp_packages": 2,
        "opamp_units": 4,
        "opamp_power_pins_checked": 4,
        "unassigned_footprints": manifest["unassigned_footprints"],
        "hardware_validated": False,
        "manufacturing_approved": False,
    }


def main():
    build = ROOT / "build/analog"
    build.mkdir(parents=True, exist_ok=True)
    xml = build / "analog-capture.xml"
    erc = build / "capture-erc.json"
    report = build / "capture-check.json"
    for path in [xml, erc, report]:
        path.unlink(missing_ok=True)
    sch = DESIGN / "analog-front-end.kicad_sch"
    for name, command in [
        (
            "netlist",
            [
                "kicad-cli",
                "sch",
                "export",
                "netlist",
                "--format",
                "kicadxml",
                "--output",
                str(xml),
                str(sch),
            ],
        ),
        (
            "erc",
            [
                "kicad-cli",
                "sch",
                "erc",
                "--format",
                "json",
                "--exit-code-violations",
                "--output",
                str(erc),
                str(sch),
            ],
        ),
    ]:
        r = subprocess.run(
            command, cwd=ROOT, capture_output=True, text=True, timeout=60, check=False
        )
        (build / ("capture-" + name + ".log")).write_text(r.stdout + r.stderr)
        if r.returncode:
            raise RuntimeError(
                "Native analog " + name + " failed; no success report published"
            )
    result = verify(
        xml.read_text(),
        json.loads((DESIGN / "analog-manifest.json").read_text()),
        (ROOT / "simulation/analog/lr4-rc.cir").read_text(),
    )
    violations = [
        v
        for sheet in json.loads(erc.read_text())["sheets"]
        for v in sheet["violations"]
    ]
    if violations:
        raise ValueError("Native analog ERC findings remain")
    result["native_erc_violations"] = 0
    result["status"] = "CAPTURE CONSISTENCY PASS; NO PCB/VMID/FULL FRONT-END"
    report.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
