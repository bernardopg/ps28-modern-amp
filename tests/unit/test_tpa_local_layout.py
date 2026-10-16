"""Native-CAD regressions, not electrical/thermal qualification."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from check_tpa_local_layout import inspect_board, LOCAL


@unittest.skipUnless(importlib.util.find_spec("pcbnew"), "Native KiCad required")
class TPALocalLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pcbnew
        cls.pcbnew = pcbnew
        cls.board = pcbnew.LoadBoard(str(ROOT / "kicad/system-candidate/system-candidate.kicad_pcb"))
        cls.metrics = inspect_board()

    def test_capacitors_remain_local_and_connected_to_expected_pin_nets(self):
        for ref, row in self.metrics["local_components"].items():
            self.assertEqual(row["side"], "B.Cu", ref)
            self.assertLess(row["pad_to_pin_mm"], 5, ref)
        # CAD regression budgets for this design, not datasheet limits.
        for net, row in self.metrics["bootstrap_copper"].items():
            self.assertGreater(row["track_length_mm"], 0, net)
            self.assertLess(row["track_length_mm"], 12, net)
            self.assertLessEqual(row["vias"], 2, net)
            self.assertNotIn("In1.Cu", row["layers"], net)
        self.assertEqual(self.metrics["in1_signal_tracks"], 0)

    def test_bottom_side_courtyards_and_fields_match_actual_face(self):
        p = self.pcbnew
        for ref in LOCAL:
            fp = self.board.FindFootprintByReference(ref)
            self.assertTrue(fp.IsFlipped(), ref)
            self.assertTrue(fp.GetCourtyard(p.B_CrtYd).OutlineCount(), ref)
            self.assertFalse(fp.GetCourtyard(p.F_CrtYd).OutlineCount(), ref)
            for field in fp.GetFields():
                if field.GetLayer() in (p.B_Fab, p.B_SilkS):
                    self.assertTrue(field.IsMirrored(), ref)


if __name__ == "__main__":
    unittest.main()
