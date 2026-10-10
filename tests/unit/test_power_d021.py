import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from create_power_d021 import aux_output, generate, ovp_window, parts
from simulate_power_d021 import MAINS, PVDD_MAX, RATIO

R = json.loads((ROOT / "tests/reports/power-d021-study.json").read_text())


class PowerD021Tests(unittest.TestCase):
    def test_two_diode_ct_topology_never_bridges_ends(self):
        nets = {p["ref"]: p["nets"] for p in parts()}
        self.assertEqual(nets["D301"], {"1": "PVDD", "2": "T1_A"})
        self.assertEqual(nets["D302"], {"1": "PVDD", "2": "T1_B"})
        self.assertEqual(nets["F301"], {"1": "T1_CT", "2": "GND"})
        for p in parts():
            if p["ref"] == "J301":  # the harness itself carries both winding ends
                continue
            self.assertFalse({"T1_A", "T1_B"} <= set(p["nets"].values()), p["ref"])
        self.assertNotIn("GND", nets["J301"].values())

    def test_report_covers_sweep_and_stays_below_tpa_limit(self):
        self.assertEqual(len(R["cases"]), 54)
        self.assertLessEqual(R["worst_pvdd_max_v"], PVDD_MAX)
        self.assertGreaterEqual(R["diode_piv_required_v"], 2 * max(MAINS) * RATIO * 2**0.5 - 0.1)
        self.assertFalse(R["hardware_validated"])
        self.assertFalse(R["manufacturing_approved"])

    def test_three_mf_bank_ripple_justifies_larger_bulk(self):
        def worst(c_uf):
            return max(c["ripple_vpp"] for c in R["cases"] if c["bulk_uf"] == c_uf and c["load_a"] == 3.9)
        self.assertGreater(worst(3000), 3 * worst(10000))

    def test_pvdd_window_trips_between_worst_idle_and_tpa_limit(self):
        w = ovp_window()
        self.assertGreater(w["ov_trip_v"][0], R["worst_pvdd_max_v"])  # no nuisance trip at 133 V idle
        self.assertLess(w["ov_trip_v"][2], PVDD_MAX)
        self.assertGreater(w["uv_trip_falling_v"][0], 18.0)  # SLASEA8A p.6 PVDD min
        self.assertLess(w["uv_trip_falling_v"][2], 32.0)  # below 10 mF / 108 V / 3.9 A valley

    def test_aux_within_tpa_vdd_gvdd_range(self):
        lo, _, hi = aux_output()
        self.assertGreaterEqual(lo, 10.8)  # SLASEA8A sec.7.3
        self.assertLessEqual(hi, 13.2)

    def test_supervisor_and_buck_wiring(self):
        nets = {p["ref"]: p["nets"] for p in parts()}
        self.assertEqual(nets["U303"], {"1": "RAILS_OK", "2": "GND", "3": "PVDD_UV_SENSE",
                                        "4": "PVDD_OV_SENSE", "5": "AUX_RAW", "6": "RAILS_OK"})
        self.assertEqual(nets["U302"]["6"], "RAILS_OK")
        self.assertEqual((nets["U302"]["2"], nets["U302"]["8"]), ("PVDD", "BUCK_SW"))
        self.assertEqual(nets["L301"], {"1": "BUCK_SW", "2": "AUX_RAW"})
        self.assertNotIn("RESET", {n for p in parts() for n in p["nets"].values()})

    @unittest.skipUnless(Path("/usr/share/kicad/symbols").is_dir(), "needs KiCad stock symbol libraries")
    def test_generator_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "p"
            generate(out)
            self.assertTrue((out / "power-d021.kicad_sch").exists())
            self.assertTrue((out / "power-manifest.json").exists())
            with self.assertRaises(FileExistsError):
                generate(out)


if __name__ == "__main__":
    unittest.main()
