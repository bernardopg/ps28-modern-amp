import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from create_iso_d019 import RELAY_RELEASE_MAX_S, generate, parts, windows

R = json.loads((ROOT / "tests/reports/d019-interface-study.json").read_text())


class D019InterfaceTests(unittest.TestCase):
    def test_relay_form_c_isolates_and_discharges_by_default(self):
        nets = {p["ref"]: p["nets"] for p in parts()}
        k = nets["K501"]
        # Omron K106-E1-11 p.6: COM 3/6, NC 2/7, NO 4/5, coil 1(+)/8(-).
        self.assertEqual((k["3"], k["2"], k["4"]), ("INA_ISO", "INA_DIS", "INPUT_A_AC"))
        self.assertEqual((k["6"], k["7"], k["5"]), ("INB_ISO", "INB_DIS", "INPUT_B_AC"))
        self.assertEqual((k["1"], k["8"]), ("AUX_RAW", "RELAY_DRV"))
        self.assertEqual(nets["R503"], {"1": "INA_DIS", "2": "GND"})
        # The pin never has a direct path to GND below the ~1 Mohm window divider.
        for p in parts():
            if p["ref"].startswith("R") and "INPUT_A_AC" in p["nets"].values():
                self.assertEqual(p["ref"], "R505")
        self.assertEqual(nets["R502"]["2"], "GND")  # relay off without logic

    def test_mute_defaults_on_and_shunts_divided_to_vmid(self):
        u = {p["ref"]: p["nets"] for p in parts()}["U503"]
        self.assertEqual((u["1"], u["2"], u["5"], u["6"]), ("DIVIDED", "VMID", "MUTE_EN", "GND"))
        r511 = {p["ref"]: p["nets"] for p in parts()}["R511"]
        self.assertEqual(r511, {"1": "ANALOG_12V", "2": "MUTE_EN"})

    def test_windows_keep_pin_inside_limits_with_contract_audio(self):
        w = windows()
        self.assertGreaterEqual(w["pin_dc"]["uv_trip_falling_v"][0] - R["inputs"]["audio_pk_v"]
                                - R["dc_estimate_ripple_at_20hz_v"], -0.3)
        self.assertLessEqual(w["pin_dc"]["ov_trip_v"][2] + R["inputs"]["audio_pk_v"]
                             + R["dc_estimate_ripple_at_20hz_v"], 7.0)
        self.assertGreaterEqual(w["aux_raw"]["uv_trip_falling_v"][0], 10.8)  # SLASEA8A sec.7.3
        self.assertLess(w["aux_raw"]["uv_trip_falling_v"][2], 11.69)  # AUX min
        self.assertGreater(w["aux_raw"]["ov_trip_v"][0], 12.50)
        self.assertLessEqual(w["aux_raw"]["ov_trip_v"][2], 13.2)

    def test_simulation_report_all_cases_inside_limits(self):
        self.assertTrue(R["all_ok"])
        self.assertGreaterEqual(R["worst_pin_min_v"], -0.3)
        self.assertLessEqual(R["worst_pin_max_v"], 7.0)
        self.assertLessEqual(R["worst_plate_abs_v"], 16.0)
        self.assertEqual(R["inputs"]["relay_operate_release_max_s"][1], RELAY_RELEASE_MAX_S)
        self.assertIn(0.01, R["inputs"]["t_open_s"])  # pessimistic beyond datasheet
        self.assertFalse(R["hardware_validated"])

    def test_generator_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "i"
            generate(out)
            self.assertTrue((out / "iso-manifest.json").exists())
            with self.assertRaises(FileExistsError):
                generate(out)


if __name__ == "__main__":
    unittest.main()
