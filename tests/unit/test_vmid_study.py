import hashlib
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from simulate_vmid import (
    circuit,
    differential_metrics,
    loop_metrics,
    power_down_counterexample,
    reference_bounds,
    reference_startup_settling,
)


class VMIDStudyTests(unittest.TestCase):
    def setUp(self):
        self.c = json.loads((ROOT / "simulation/analog/vmid-study.json").read_text())

    def test_versioned_evidence_cannot_hide_unsafe_power_down_or_stale_source(self):
        result = json.loads((ROOT / "tests/reports/vmid-buffer-study.json").read_text())
        for key, path in [
            ("config_sha256", "simulation/analog/vmid-study.json"),
            ("script_sha256", "scripts/simulate_vmid.py"),
            ("shared_runner_sha256", "scripts/simulate_opa1656.py"),
            ("analog_config_sha256", "simulation/analog/lr4-study.json"),
        ]:
            self.assertEqual(
                result[key], hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            )
        self.assertEqual(len(result["return_ratio_cases"]), 32)
        self.assertTrue(
            any(
                x["input_abs_max_violated"]
                for x in result["hard_power_down_passive_counterexamples"]
            )
        )
        self.assertFalse(result["manufacturing_approved"])
        self.assertFalse(
            result["startup_power_down_input_clamps_or_backfeed_qualified"]
        )

    def test_divider_leakage_and_bidirectional_load_budget_is_only_assumed(self):
        lo, hi = reference_bounds(self.c, 13.2)
        self.assertAlmostEqual(lo, 6.51050235, places=8)
        self.assertAlmostEqual(hi, 6.666, places=8)
        self.assertLess(
            max(6.6 - lo, hi - 6.6) + 0.05, self.c["proposed_dc_error_limit_v"]
        )
        self.assertFalse(self.c["exact_mpn_footprint_and_esr_selected"])

    def test_passive_power_down_matches_numerical_ode_and_rejects_safety(self):
        tau = 2350 * self.c["reference_capacitance_f"]
        fall = 0.002
        dt = fall / 10000
        v = 6
        # Midpoint integration is independent of the closed-form ramp expression.
        for i in range(10000):
            t = i * dt
            dv = (0.5 * 12 * (1 - t / fall) - v) / tau
            middle = v + 0.5 * dt * dv
            v += dt * (0.5 * 12 * (1 - (t + 0.5 * dt) / fall) - middle) / tau
        result = power_down_counterexample(self.c, 12, fall)
        self.assertAlmostEqual(v, result["reference_at_aux_zero_v"], places=8)
        self.assertTrue(result["input_abs_max_violated"])
        self.assertGreater(result["reference_at_aux_zero_v"], 5)
        self.assertFalse(self.c["supervisor_or_input_clamps_implemented"])

    def test_reference_settling_is_not_instantaneous(self):
        t = reference_startup_settling(self.c, 12, 25)
        self.assertGreater(t, 0.33)
        self.assertLess(t, 0.34)

    def test_return_ratio_phase_margin_known_transfer_and_missing_sweep(self):
        # Single pole with known analytical unity crossing and PM.
        rows = []
        for i in range(721):
            f = 10 ** (i / 80)
            gain = 1e5 / (1 + complex(0, f / 100))
            rows.append([f, gain.real, f, gain.imag])
        m = loop_metrics(rows)
        expected_cross = 100 * math.sqrt(1e10 - 1)
        expected_margin = 180 - math.degrees(math.atan(expected_cross / 100))
        self.assertAlmostEqual(m["crossover_hz"] / expected_cross, 1, places=5)
        self.assertAlmostEqual(m["phase_margin_deg"], expected_margin, places=4)
        with self.assertRaises(ValueError):
            loop_metrics(rows[:-1])

    def test_time_weighted_rms_rejects_duplicate_time(self):
        rows = []
        for i in range(1001):
            t = 0.25 + 0.1 * i / 1000
            v = math.sqrt(2) * math.sin(40 * math.pi * t)
            rows.append([t, 6, t, 6 + v / 2, t, 6 - v / 2, t, 6])
        rms, dc, _ = differential_metrics(rows)
        self.assertAlmostEqual(rms, 1, places=5)
        self.assertAlmostEqual(dc, 0, places=5)
        rows[5][0] = rows[4][0]
        with self.assertRaises(ValueError):
            differential_metrics(rows)

    def test_coupled_chain_replaces_ideal_vmid_without_changing_model(self):
        text = circuit(
            self.c, 12, 27, 25, 47e-6, 0.05, "build/analog/vmid/test.dat", "chain"
        )
        self.assertNotIn("VMID mid 0", text)
        self.assertIn("XVMID reference feedback supply 0 driver OPA1656", text)
        self.assertIn("VFEEDBACK feedback driver 0", text)
        self.assertIn("R11 buffered x1 14000", text)
        self.assertEqual(text.count('.include "build/analog/parts/OPA1656.LIB"'), 1)


if __name__ == "__main__":
    unittest.main()
