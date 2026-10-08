#!/usr/bin/env python3
"""Native protection capture: all pins plus independent canonical terminal topology."""

import json
import subprocess
import xml.etree.ElementTree as ET

from simulate_opa1656 import ROOT

DESIGN = ROOT / "kicad/vmid-protected"
BUILD = ROOT / "build/analog/vmid-protection"
ALIASES = {
    "AUX_RAW": "raw",
    "ISO_FEED": "iso",
    "ANALOG_12V": "ana",
    "VMID": "mid",
    "GND": "ret",
    "DIV_TOP": "divtop",
    "DIV_BOTTOM": "divbottom",
}


def verify(xml, manifest, spice):
    tree = ET.fromstring(xml)
    comps = {
        n.attrib["ref"]: n
        for n in tree.findall("components/comp")
        if not n.attrib["ref"].startswith("#")
    }
    expected = {p["ref"]: p for p in manifest["parts"]}
    if set(comps) != set(expected):
        raise ValueError("Native component set mismatch")
    pins = {}
    for net in tree.findall("nets/net"):
        for node in net.findall("node"):
            if not node.attrib["ref"].startswith("#"):
                key = (node.attrib["ref"], node.attrib["pin"])
                if key in pins:
                    raise ValueError("Duplicate native pin")
                pins[key] = net.attrib["name"].rsplit("/", 1)[-1]
    for ref, p in expected.items():
        fields = {x.attrib["name"]: x.text for x in comps[ref].findall("fields/field")}
        if fields.get("MPN") != p["mpn"]:
            raise ValueError("Native MPN property mismatch: " + ref)
        if (
            comps[ref].findtext("value") != p["value"]
            or (comps[ref].findtext("footprint") or "") != p["footprint"]
        ):
            raise ValueError("Native property mismatch: " + ref)
        for pin, net in p["nets"].items():
            if pins.get((ref, pin)) != net:
                raise ValueError("Native pin mismatch: " + ref + "." + pin)
    if len(pins) != sum(len(p["nets"]) for p in expected.values()):
        raise ValueError("Unexpected pin count")
    rows = {s.split()[0]: s.split() for s in spice.splitlines() if s and s[0] in "RC"}
    scale = {"k": 1e3, "u": 1e-6}
    for ref, row in rows.items():
        if [ALIASES[pins[(ref, str(p))]] for p in [1, 2]] != row[1:3]:
            raise ValueError("SPICE terminal mismatch: " + ref)
        text = expected[ref]["value"]
        val = float(text[:-1]) * scale[text[-1]] if text[-1] in scale else float(text)
        if abs(val - float(row[3])) > 1e-12 * val:
            raise ValueError("SPICE value mismatch: " + ref)
    # KiCad Device:D pin1=K/pin2=A; BISO current flows raw(A)->iso(K).
    if ALIASES[pins[("D201", "2")]] != "raw" or ALIASES[pins[("D201", "1")]] != "iso":
        raise ValueError("Blocking diode polarity mismatch")
    if "BISO raw iso I=" not in spice:
        raise ValueError("Independent diode orientation absent")
    if "J202" in comps and (
        pins[("J202", "1")] != "ANALOG_12V" or pins[("J202", "2")] != "VMID"
    ):
        raise ValueError("Wrong output domain")
    return {
        "components": len(comps),
        "native_pins_checked": len(pins),
        "independent_passives_checked": len(rows),
        "diode_polarity_checked": True,
        "hardware_validated": False,
        "manufacturing_approved": False,
    }


def filtered(xml, refs):
    tree = ET.fromstring(xml)
    for comp in list(tree.find("components")):
        if comp.attrib["ref"] not in refs and not comp.attrib["ref"].startswith("#"):
            tree.find("components").remove(comp)
    for net in tree.findall("nets/net"):
        for node in list(net):
            if node.attrib["ref"] not in refs and not node.attrib["ref"].startswith(
                "#"
            ):
                net.remove(node)
    return ET.tostring(tree, encoding="unicode")


def main(integrated=False):
    from check_analog_capture import ALIASES as analog_aliases
    from check_analog_capture import verify as verify_analog

    design = ROOT / "kicad/analog-protected" if integrated else DESIGN
    project = "analog-protected" if integrated else "vmid-protected"
    prefix = "integrated-" if integrated else ""
    BUILD.mkdir(parents=True, exist_ok=True)
    xml = BUILD / (prefix + "capture.xml")
    erc = BUILD / (prefix + "erc.json")
    report = BUILD / (prefix + "capture-check.json")
    for f in [xml, erc, report]:
        f.unlink(missing_ok=True)
    sch = design / (project + ".kicad_sch")
    commands = [
        (
            "netlist",
            [
                "kicad-cli",
                "sch",
                "export",
                "netlist",
                "--format",
                "kicadxml",
                "-o",
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
                "-o",
                str(erc),
                str(sch),
            ],
        ),
    ]
    for name, cmd in commands:
        r = subprocess.run(
            cmd, cwd=ROOT, text=True, capture_output=True, timeout=60, check=False
        )
        (BUILD / (prefix + name + ".log")).write_text(r.stdout + r.stderr)
        if r.returncode:
            raise RuntimeError("Native " + name + " failed; success report invalidated")
    findings = [
        v for s in json.loads(erc.read_text())["sheets"] for v in s["violations"]
    ]
    if findings:
        raise ValueError("Native ERC violations remain")
    text = xml.read_text()
    manifest = json.loads((design / "vmid-manifest.json").read_text())
    power = [
        p
        for p in manifest["parts"]
        if p["ref"]
        in {
            "D201",
            *[f"R{i}" for i in range(201, 208)],
            "C201",
            "C202",
            "C203",
            "J201",
            "J202",
        }
    ]
    result = verify(
        filtered(text, {p["ref"] for p in power}),
        {"parts": power},
        (ROOT / "simulation/analog/vmid-protected.cir").read_text(),
    )
    if integrated:
        ap = [p for p in manifest["parts"] if p not in power]
        aliases = {
            **analog_aliases,
            "VMID": "mid",
            "ANALOG_12V": "supply",
            "AUX_RAW": "raw",
        }
        analog = verify_analog(
            filtered(text, {p["ref"] for p in ap}),
            {
                "parts": ap,
                "unassigned_footprints": [p["ref"] for p in ap if not p["footprint"]],
            },
            (ROOT / "simulation/analog/lr4-rc.cir").read_text(),
            aliases,
        )
        result["analog_validation"] = analog
        result["total_components"] = len(manifest["parts"])
        result["total_native_pins_checked"] = result["native_pins_checked"] + sum(
            len(p["nets"]) for p in ap
        )
    result["native_erc_violations"] = 0
    report.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--integrated", action="store_true")
    main(parser.parse_args().integrated)
