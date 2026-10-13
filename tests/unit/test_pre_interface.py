import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from create_pre_interface import P101, analog_changes, gain, parts


class PreInterfaceTests(unittest.TestCase):
    def test_full_power_gain_matches_oem_sensitivity(self):
        oem_in = 25.7 / (1 + 56e3 / 1.5e3)  # manual p.24: OEM amp gain 1+R104/R103
        need = 25.7 / 10 ** (21.5 / 20) / 10 ** (-1.33 / 20)  # TPA 21.5 dB, D-024a series
        self.assertAlmostEqual(oem_in * gain(), need, delta=0.05 * need)

    def test_rails_and_harness(self):
        refs = {p["ref"]: p for p in parts()}
        self.assertEqual(refs["J7"]["nets"], P101)
        self.assertEqual(refs["Q601"]["nets"]["3"], "P15V")
        self.assertEqual(refs["Q602"]["nets"]["3"], "N15V")
        # Negative raw rail: diode cathodes on the T1 ends, never bridging T1_A-T1_B.
        self.assertEqual({refs["D602"]["nets"]["1"], refs["D603"]["nets"]["1"]}, {"T1_A", "T1_B"})
        self.assertEqual(refs["C603"]["nets"], {"1": "GND", "2": "NRAW"})  # + on GND

    def test_lr4_removed_and_u2_is_gain_stage(self):
        demo = [{"ref": r, "nets": {}, "value": "", "mpn": ""} for r in ("R103", "C101", "R101", "R102")]
        demo.append({"ref": "U2", "nets": {}, "value": "", "mpn": ""})
        demo.append({"ref": "U3", "nets": {}, "value": "", "mpn": ""})
        out = {p["ref"]: p for p in analog_changes(demo)}
        self.assertNotIn("R103", out)
        self.assertEqual(out["U2"]["nets"]["2"], "U2_FB")
        self.assertEqual(out["U3"]["nets"]["3"], "BUFFERED")


if __name__ == "__main__":
    unittest.main()
