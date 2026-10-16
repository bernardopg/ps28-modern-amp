"""Regression for TP127 overlapping the INA_UV divider in the integrated sheet."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from create_debug_io import parts
from create_core_draft import parse
from create_analog_capture import child


class DebugSchematicTests(unittest.TestCase):
    def test_tp127_generator_stays_outside_r506_stub(self):
        tp = next(p for p in parts() if p["ref"] == "TP127")
        self.assertEqual(tp["nets"], {"1": "INPUT_A_AC"})
        self.assertEqual(tp["units"], [(1, 101.6, 109.22)])
        # Integration adds 1270 to X; R506 and its stub sit at X=1346.2.
        self.assertGreater(abs(tp["units"][0][1] + 1270 - 1346.2), 20)

    def test_reviewed_sheet_has_separate_labels_and_divider_wire(self):
        root = parse((ROOT / "kicad/system-candidate/system-candidate.kicad_sch").read_text())
        labels = {(n[1].strip('"'), tuple(map(float, child(n, "at")[1:3])))
                  for n in root if isinstance(n, list) and n[0] == "label"}
        self.assertIn(("INPUT_A_AC", (1371.6, 109.22)), labels)
        self.assertIn(("INA_UV", (1346.2, 119.38)), labels)
        self.assertNotIn(("INPUT_A_AC", (1346.2, 125.73)), labels)
        wires = {frozenset(tuple(map(float, xy[1:])) for xy in child(n, "pts")[1:])
                 for n in root if isinstance(n, list) and n[0] == "wire"}
        self.assertIn(frozenset(((1346.2, 123.19), (1346.2, 119.38))), wires)
        self.assertNotIn(frozenset(((1346.2, 119.38), (1346.2, 125.73))), wires)


if __name__ == "__main__":
    unittest.main()
