from pathlib import Path
import json
import math
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from simulate_analog import deck, metrics, section_response, tolerance_study


class AnalogStudyTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / 'simulation/analog/lr4-study.json').read_text())
        self.values = self.config['stage_ohm'] + self.config['stage_feedback_capacitors_f'] + [self.config['stage_ground_capacitor_f']]

    def test_two_unity_stages_have_butterworth_q_and_explicit_rc(self):
        m = metrics(self.values)
        self.assertAlmostEqual(m['q'], 1 / math.sqrt(2))
        self.assertAlmostEqual(m['natural_frequency_hz'], 80.38538537117)
        self.assertEqual(section_response(0, self.values), 1)
        self.assertAlmostEqual(abs(section_response(m['natural_frequency_hz'], self.values) ** 2), .5)

    def test_committed_netlist_is_current_and_feedback_caps_are_parallel(self):
        expected = deck(self.config, 'build/analog/rc-ideal.dat')
        self.assertEqual((ROOT / 'simulation/analog/lr4-rc.cir').read_text(), expected)
        self.assertIn('CF11 x1 filtered1 1e-07', expected)
        self.assertIn('CF12 x1 filtered1 1e-07', expected)
        self.assertIn('CG1 y1 mid 1e-07', expected)
        self.assertNotIn('.shell', expected)

    def test_tolerances_are_reproducible_and_not_hardware_approval(self):
        a = tolerance_study(self.config)
        self.assertEqual(a, tolerance_study(self.config))
        self.assertEqual(a['corner_combinations'], 16384)
        self.assertEqual(a['monte_carlo_samples'], 2048)
        self.assertGreater(a['section_q_corner_range'][1], a['section_q_corner_range'][0])
        self.assertLess(a['corner_gain_db_80hz_range'][0], -6)
        self.assertGreater(a['corner_gain_db_80hz_range'][1], -6)
        self.assertFalse(self.config['hardware_validated'])
        self.assertFalse(self.config['NE5532_at_10_8_to_13_2V_qualified'])

    def test_attenuation_preserves_ideal_differential_gain_not_headroom_guarantee(self):
        top, bottom = self.config['attenuator_ohm']
        self.assertEqual(2 * bottom / (top + bottom), 1)
        peak = self.config['input_rms_v'] * math.sqrt(2)
        assumed_swing = self.config['aux_supply_min_v'] / 2 - self.config['assumed_rail_margin_v_NOT_guaranteed_at_12V']
        self.assertGreater(peak, assumed_swing)
        self.assertLess(peak * bottom / (top + bottom), assumed_swing)
        self.assertFalse(self.config['VMID_source_impedance_startup_qualified'])


if __name__ == '__main__':
    unittest.main()
