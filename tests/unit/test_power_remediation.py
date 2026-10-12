import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'scripts'))
from analyze_power_remediation import square_integral, divider_interval, analyze_wave


class PowerRemediationTests(unittest.TestCase):
    def test_linear_square_integral_and_clipping(self):
        self.assertAlmostEqual(square_integral([0, 1], [0, 3], 0, 1), 3)
        self.assertAlmostEqual(square_integral([0, 1], [0, 3], .5, 1), 2.625)

    def test_invalid_waveforms_are_rejected(self):
        for t, v in [([0, 0, 1], [1, 1, 1]), ([0, 1], [1]), ([0, 1], [1, float('nan')])]:
            with self.assertRaises(ValueError): square_integral(t, v, 0, 1)
        with self.assertRaises(ValueError): square_integral([0, 1], [1, 1], 0, 2)

    def test_ct_is_sum_not_maximum_or_one_half(self):
        result = analyze_wave([0, .1, .9, 1], [3]*4, [4]*4, 2)
        self.assertAlmostEqual(result['ct_rms_a'], 7)
        self.assertAlmostEqual(result['bank_ripple_rms_a'], 5)
        self.assertAlmostEqual(result['ct_inrush_i2t_100ms_a2s'], 4.9)

    def test_lm5069_ovlo_cannot_fit_required_window(self):
        self.assertFalse(divider_interval(49.84, 53.5, 2.4, 2.6)['feasible_even_with_ideal_resistors'])
        self.assertTrue(divider_interval(40, 60, 2.4, 2.6)['feasible_even_with_ideal_resistors'])
