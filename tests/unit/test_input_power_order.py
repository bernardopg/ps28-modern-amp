import copy
import hashlib
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import simulate_input_power_order as order

C = json.loads(order.CONFIG.read_text())


class InputOrderTests(unittest.TestCase):
    def test_linear_ramp_against_independent_closed_form(self):
        for rs in (0, 1000):
            cap, rin, fall, v0, delta = 10e-6, 20000, 0.03, 2.0, -2.75
            tau, gain = cap * (rin + rs), rin / (rin + rs)
            expected = v0 * math.exp(-fall / tau) + gain * delta * tau / fall * (
                1 - math.exp(-fall / tau)
            )
            self.assertAlmostEqual(
                order.advance(v0, delta, 0, 0, fall, cap, rin, rs), expected, places=12
            )

    def test_segment_split_and_receiver_bias_feedthrough(self):
        cap, rin, rs, dt = 10e-6, 20000, 1000, 0.02
        full = order.advance(3, -2, 4, -4, dt, cap, rin, rs)
        half = order.advance(3, -1, 4, -2, dt / 2, cap, rin, rs)
        half = order.advance(half, -1, 2, -2, dt / 2, cap, rin, rs)
        self.assertAlmostEqual(full, half, places=12)
        # As a bias ramp approaches a step, only the series R feedthrough jumps.
        tiny = order.advance(4, 0, 4, -4, 1e-12, cap, rin, rs)
        self.assertAlmostEqual(tiny, 4 * rin / (rin + rs), places=8)

    def test_coupling_and_series_resistor_are_not_voltage_protection(self):
        native = order.loss_case(C, 10e-6, 20000, 0, 3.875, 0.1, 0.03)
        self.assertAlmostEqual(native["minimum_input_v"], -0.530759713925, places=9)
        series = order.loss_case(C, 10e-6, 20000, 1000, 0, 0, 0.02)
        self.assertLess(series["minimum_input_v"], -2)
        self.assertTrue(native["violates_input_voltage_rating"])
        self.assertTrue(series["violates_input_voltage_rating"])

    def test_cold_connection_requires_signal_mute_and_observed_precharge(self):
        cold, quiet = order.startup(C, False), order.startup(C, True)
        self.assertLess(cold["minimum_input_v"], -2)
        self.assertTrue(cold["violates_input_voltage_rating"])
        self.assertFalse(quiet["violates_input_voltage_rating"])
        self.assertGreater(quiet["hypothetical_ready_s"], 0.14)
        self.assertLess(quiet["hypothetical_ready_s"], 0.15)

    def test_complete_sweep_preserves_unsafe_cases_and_no_hardware_claim(self):
        result = order.study(C)
        self.assertEqual(result["case_count"], 288)
        self.assertEqual(result["violating_hypothesis_cases"], 196)
        self.assertLess(result["upstream_switch_clamped_plate_counterexample_v"], -0.3)
        self.assertFalse(
            result["unrealized_isolation_contract"]["hardware_implemented_or_qualified"]
        )

    def test_isolation_budget_includes_leakage_injection_feedthrough_and_preclose(self):
        bound = order.isolation_bound(C)
        self.assertAlmostEqual(bound["total_excursion_bound_v"], 0.24)
        self.assertAlmostEqual(bound["minimum_margin_to_absolute_v"], 0.06)
        self.assertTrue(bound["passes_if_all_unmeasured_requirements_hold"])
        for key, value in [
            ("maximum_detection_and_open_delay_s", 0.001),
            ("minimum_added_pin_capacitance_f", 1e-9),
            ("maximum_off_capacitance_f", 100e-12),
            ("maximum_off_leakage_a", 10e-6),
            ("maximum_preclose_plate_error_v", 0.2),
        ]:
            c = copy.deepcopy(C)
            c["isolation_contract_requirements_not_measured"][key] = value
            self.assertFalse(
                order.isolation_bound(c)["passes_if_all_unmeasured_requirements_hold"],
                key,
            )

    def test_invalid_values_and_rating_relaxation_rejected(self):
        for key, value in [
            ("input_absolute_limits_v", [-0.5, 8]),
            ("coupling_nominal_f", 20e-6),
            ("driver_final_v", 2),
            ("signal_peak_v", float("nan")),
            ("hypothesis_receiver_first_delays_s", [-1]),
            ("startup_qualified_dc_window_v", [2, float("nan")]),
        ]:
            c = copy.deepcopy(C)
            c[key] = value
            with self.assertRaises(ValueError, msg=key):
                order.validate(c)
        c = copy.deepcopy(C)
        c["isolation_contract_requirements_not_measured"][
            "minimum_margin_to_absolute_v"
        ] = 0
        with self.assertRaises(ValueError):
            order.isolation_bound(c)
        with self.assertRaises(ValueError):
            order.advance(0, 1, 0, 0, 0, 10e-6, 20000)

    def test_native_interface_mapping_is_review_only_and_rejects_mutation(self):
        core = json.loads((ROOT / "kicad/core-selected/core-manifest.json").read_text())
        analog = json.loads(
            (ROOT / "kicad/analog-protected/vmid-manifest.json").read_text()
        )
        audit = order.audit_interfaces(core, analog)
        self.assertFalse(audit["schematics_connected_or_modified"])
        for p in core["parts"]:
            if p["ref"] == "C20":
                p["nets"]["2"] = "GND"
        with self.assertRaises(ValueError):
            order.audit_interfaces(core, analog)

    def test_stale_report_removed_before_preflight_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            build = Path(tmp)
            (build / "result.json").write_text("stale success")
            missing = build / "missing-config.json"
            with (
                patch.object(order, "BUILD", build),
                patch.object(order, "CONFIG", missing),
                self.assertRaises(FileNotFoundError),
            ):
                order.main()
            self.assertFalse((build / "result.json").exists())

    def test_published_evidence_binds_sources_topology_and_code(self):
        report = json.loads(
            (ROOT / "tests/reports/input-power-order-study.json").read_text()
        )
        self.assertFalse(report["hardware_validated"])
        self.assertFalse(report["existing_interface_protected"])
        self.assertFalse(report["vendor_macro_executed"])
        for name, expected in report["hashes"].items():
            self.assertEqual(
                hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected, name
            )
        self.assertEqual(
            report["sources"],
            [{**s, "local_pdf_hash_rechecked": True} for s in C["sources"]],
        )
        self.assertEqual(len(report["independent_passive_spice"]), 4)
        for case in report["independent_passive_spice"]:
            self.assertGreater(case["points_checked"], 1000)
            self.assertLess(case["maximum_analytical_error_v"], 0.002)
        coupled = report["coupled_d018_rail_receiver_hypotheses"]
        self.assertEqual(len(coupled), 2)
        self.assertTrue(
            coupled[0]["violates_tpa_input_rating_in_powered_analog_window"]
        )
        self.assertFalse(
            coupled[1]["violates_tpa_input_rating_in_powered_analog_window"]
        )
        for case in coupled:
            self.assertTrue(case["vmid_input_voltage_envelope_passes"])
            self.assertGreaterEqual(case["analog_supply_at_minimum_v"], 4.5)
            self.assertLess(case["maximum_independent_integration_error_v"], 0.002)


if __name__ == "__main__":
    unittest.main()
