import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from check_pcb_readiness import audit_drc, audit_parts


class PCBReadinessTests(unittest.TestCase):
    def test_drc_requires_connectivity_and_parity_even_without_shorts(self):
        report = {"violations": [], "unconnected_items": [{"type": "unconnected_items"}],
                  "schematic_parity": [{"type": "footprint"}]}
        self.assertEqual({x["code"] for x in audit_drc(report)},
                         {"unconnected_items", "schematic_parity"})

    def test_missing_drc_section_fails_closed(self):
        for key in ("violations", "unconnected_items", "schematic_parity"):
            report = {"violations": [], "unconnected_items": [], "schematic_parity": []}
            del report[key]
            with self.assertRaises(ValueError):
                audit_drc(report)
        self.assertEqual(audit_drc({"violations": [], "unconnected_items": [],
                                    "schematic_parity": []}), [])

    def test_package_and_body_conflicts(self):
        parts = [{"ref": "D301", "mpn": "MUR3040WTG", "footprint": "Diode_THT:D_P600"},
                 {"ref": "C301", "mpn": "Rubycon D30xL30", "footprint": "CP_D25.0mm"},
                 {"ref": "J301", "mpn": "VHR-4N", "footprint": "JST_1x03"},
                 {"ref": "F301", "mpn": "I2t above measured inrush", "value": "T6.3A slow",
                  "footprint": "Fuseholder"}]
        original = copy.deepcopy(parts)
        codes = {x["code"] for x in audit_parts(parts)}
        self.assertTrue({"rectifier_surge_requirement_failed", "rectifier_package_mismatch", "bulk_body_mismatch",
                         "connector_positions_mismatch", "fuse_rating_unqualified",
                         "missing_part"} <= codes)
        self.assertEqual(parts, original)

    def test_missing_qualification_is_not_silently_passed(self):
        codes = {x["code"] for x in audit_parts([{"ref": "U1", "mpn": "TBD"}])}
        self.assertTrue({"missing_footprint", "unqualified_mpn"} <= codes)
