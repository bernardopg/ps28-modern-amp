import csv
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from pcb_model import parse


class CapacitorDeratingTests(unittest.TestCase):
    def test_critical_capacitance_budgets_include_bias_temperature_tolerance_and_age(self):
        fixture = json.loads((ROOT / 'tests/fixtures/capacitor-characteristics.json').read_text())
        rows = {r['Reference']: r for r in csv.DictReader(
            (ROOT / 'bom/system-candidate-capacitor-derating.csv').read_text().splitlines())}
        for ref, part, tolerance, required, dc in [
            ('C401', 'GRM21BR61H106KE43', .9, 1, 13.2),
            ('C403', 'GRM188R61E106MA73', .8, 2.2, 3.5),
        ]:
            points = [p for p in fixture['points'] if p['partnumber'] == part]
            self.assertEqual({p['temperature_C'] for p in points}, {-20, 25, 70})
            self.assertTrue(all(p['dc_V'] >= dc and p['ac_Vrms'] <= .01 for p in points))
            budget = min(p['typical_uF'] for p in points) * tolerance * .8 * .9
            self.assertAlmostEqual(budget, float(rows[ref]['EstimatedBudget_uF']), places=4)
            self.assertGreaterEqual(budget, required)
        # Both previous selections were insufficient for the legacy chip.
        self.assertLess(.32011 * .9, 1)
        self.assertLess(1.9371 * .9, 2.2)

    def test_power_capacitor_coverage_voltages_and_purchase_codes(self):
        choices = {r['Reference']: r for r in csv.DictReader(
            (ROOT / 'bom/system-candidate-selection.csv').read_text().splitlines())}
        rows = list(csv.DictReader((ROOT / 'bom/system-candidate-capacitor-derating.csv').read_text().splitlines()))
        self.assertEqual(len(rows), 48)
        self.assertEqual(len({r['Reference'] for r in rows}), 48)
        required = {'C1', 'C3', 'C14', 'C15', 'C301', 'C302', 'C310', 'C311',
                    'C315', 'C316', 'C401', 'C403', 'C601', 'C603', 'C604'}
        self.assertTrue(required.issubset({r['Reference'] for r in rows}))
        for row in rows:
            self.assertEqual(row['MPN'], choices[row['Reference']]['MPN'])
            self.assertLess(float(row['WorkingVoltage_V']), float(row['RatedVoltage_V']))
            self.assertEqual(float(row['VoltageUtilization_pct']),
                             round(100 * float(row['WorkingVoltage_V']) / float(row['RatedVoltage_V']), 2))
        by_ref = {r['Reference']: r for r in rows}
        self.assertGreater(sum(float(by_ref[r]['EstimatedBudget_uF']) for r in ('C310', 'C311')), .9)
        self.assertGreater(sum(float(by_ref[r]['EstimatedBudget_uF']) for r in ('C315', 'C316')), 3)
        self.assertAlmostEqual(sum(float(by_ref[r]['EstimatedBudget_uF'])
                                   for r in ('C14', 'C15', 'C301', 'C302')), 6886.4)

    def test_ldo_capacitors_remain_local_and_legacy_esr_path_is_preserved(self):
        tree = parse((ROOT / 'kicad/system-candidate/system-candidate.kicad_pcb').read_text())
        parts = {}
        segments = []
        for node in tree:
            if not isinstance(node, list):
                continue
            if node[0] == 'footprint':
                fields = {x[1].strip('"'): x[2].strip('"') for x in node
                          if isinstance(x, list) and x[0] == 'property'}
                at = next(x for x in node if isinstance(x, list) and x[0] == 'at')
                parts[fields['Reference']] = (node[1].strip('"'), tuple(map(float, at[1:3])))
            elif node[0] == 'segment':
                segments.append({x[0]: x[1:] for x in node[1:] if isinstance(x, list)})
        self.assertIn('0805', parts['C401'][0])
        for ref in ('C401', 'C403'):
            self.assertLess(math.dist(parts[ref][1], parts['U401'][1]), 10)
        # This unavoidable neck provides the legacy chip's >=5mOhm ESR floor,
        # even for 70um outer copper at -20C. Shortening it requires a new review.
        path = [(126.1, 68.375), (126.898, 67.5765),
                (129.552, 67.5765), (130.35, 68.375)]
        resistance = 0
        for start, end in zip(path, path[1:]):
            match = [s for s in segments if set((tuple(map(float, s['start'])),
                                               tuple(map(float, s['end'])))) == {start, end}]
            self.assertEqual(len(match), 1)
            self.assertEqual(match[0]['layer'], ['"B.Cu"'])
            resistance += math.dist(start, end) / float(match[0]['width'][0])
        resistance *= (.01724 / 1000) * (1 + .00393 * (-20 - 20)) / .070
        self.assertGreaterEqual(resistance, .005)


if __name__ == '__main__':
    unittest.main()
