import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from create_power_d021 import generate, parts
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

    def test_generator_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "p"
            generate(out)
            self.assertTrue((out / "power-d021.kicad_sch").exists())
            with self.assertRaises(FileExistsError):
                generate(out)


if __name__ == "__main__":
    unittest.main()
