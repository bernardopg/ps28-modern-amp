import hashlib
import json
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from check_analog_capture import verify
from create_analog_capture import parts
from create_core_draft import parse, walk
from simulate_opa1656 import audit_model


class AnalogCaptureTests(unittest.TestCase):
    def setUp(self):
        self.design = ROOT / "kicad/analog-front-end"
        self.xml = (ROOT / "tests/fixtures/analog-capture.xml").read_text()
        self.manifest = json.loads((self.design / "analog-manifest.json").read_text())
        self.spice = (ROOT / "simulation/analog/lr4-rc.cir").read_text()

    def test_native_fixture_matches_capture_and_independent_spice(self):
        report = verify(self.xml, self.manifest, self.spice)
        self.assertEqual(report["components"], 21)
        self.assertEqual(report["native_pins_checked"], 58)
        self.assertEqual(report["passives_matched_to_spice"], 14)
        self.assertEqual(len(report["unassigned_footprints"]), 9)
        evidence = json.loads(
            (ROOT / "tests/reports/analog-capture-review.json").read_text()
        )
        self.assertEqual(
            hashlib.sha256(
                (self.design / "analog-front-end.kicad_sch").read_bytes()
            ).hexdigest(),
            evidence["schematic_sha256"],
        )
        self.assertEqual(
            hashlib.sha256(self.xml.encode()).hexdigest(), evidence["native_xml_sha256"]
        )
        self.assertFalse(report["manufacturing_approved"])

    def test_wrong_opamp_pin_or_filter_wiring_is_rejected(self):
        tree = ET.fromstring(self.xml)
        node = next(
            n
            for n in tree.findall("nets/net/node")
            if n.attrib.get("ref") == "U2" and n.attrib.get("pin") == "3"
        )
        node.attrib["pin"] = "2"
        with self.assertRaises(ValueError):
            verify(ET.tostring(tree, encoding="unicode"), self.manifest, self.spice)
        with self.assertRaises(ValueError):
            verify(
                self.xml,
                self.manifest,
                self.spice.replace("CF11 x1 filtered1", "CF11 x1 mid"),
            )

    def test_generator_inventory_and_local_pinout_are_explicit(self):
        self.assertEqual(parts(), self.manifest["parts"])
        self.assertEqual(
            [p["mpn"] for p in self.manifest["parts"] if p["ref"].startswith("U")],
            ["OPA1656ID", "OPA1656ID"],
        )
        library = parse((self.design / "libraries/PS28_ANALOG.kicad_sym").read_text())
        numbers = sorted(
            int(
                next(
                    x[1].strip('"')
                    for x in n
                    if isinstance(x, list) and x[0] == "number"
                )
            )
            for n in walk(library)
            if n[0] == "pin"
        )
        self.assertEqual(numbers, list(range(1, 9)))

    def test_vendor_file_audit_rejects_changed_hash_and_executable_directives(self):
        with self.assertRaisesRegex(ValueError, "hash changed"):
            audit_model(b"unknown model")
        safe = b".SUBCKT OPA1656 IN+ IN- VCC VEE OUT\nR1 OUT VEE 1k\n.ENDS OPA1656\n"
        with patch("simulate_opa1656.MODEL_SHA", hashlib.sha256(safe).hexdigest()):
            self.assertEqual(audit_model(safe), [".ENDS", ".SUBCKT"])
        unsafe = safe + b".control\nshell echo forbidden\n.endc\n"
        with (
            patch("simulate_opa1656.MODEL_SHA", hashlib.sha256(unsafe).hexdigest()),
            self.assertRaisesRegex(ValueError, "directive"),
        ):
            audit_model(unsafe)


if __name__ == "__main__":
    unittest.main()
