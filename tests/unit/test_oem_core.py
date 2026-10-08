from pathlib import Path
import json
import math
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_core import check, child, text
from create_core_draft import parse
import reconstruct_oem_candidate as oem
from simulate import output_lc_magnitude


class OEMCoreTests(unittest.TestCase):
    def test_explicit_candidate_connectivity(self):
        failures, report = check(directory=ROOT / 'kicad/core-oem-refined')
        self.assertEqual(failures, [])
        self.assertEqual(report['placed_footprints'], 47)
        self.assertEqual(report['placed_pads_checked'], 142)
        self.assertFalse(report['manufacturing_approved'])

    def test_reservations_all_copper_layers_and_no_new_drill(self):
        directory = ROOT / 'kicad/core-oem-refined'
        manifest = json.loads((directory / 'core-manifest.json').read_text())
        self.assertFalse(manifest['mechanical_approved'])
        self.assertFalse(manifest['manufacturing_approved'])
        self.assertEqual(manifest['provisional_outline_mm'], [153, 79.1])
        data = manifest['mechanical_reconstruction']
        self.assertLess(data['horizontal_scale_disagreement_fraction'], .01)
        self.assertFalse(data['mounting_pattern_complete'])
        self.assertTrue(all(x['drill_shape_mm'] is None for x in data['mechanical_features']))
        board = parse((directory / 'ps28-modern.kicad_pcb').read_text())
        zones = [x for x in board if isinstance(x, list) and x[0] == 'zone']
        self.assertEqual(len(zones), 24)
        for layer in ['F.Cu', 'In1.Cu', 'In2.Cu', 'B.Cu']:
            self.assertEqual(sum(text(child(z, 'layer')[1]) == layer for z in zones), 6)
        for zone in zones:
            keepout = child(zone, 'keepout')
            for kind in ['tracks', 'vias', 'pads', 'copperpour', 'footprints']:
                self.assertEqual(child(keepout, kind)[1], 'not_allowed')
        j6 = next(x for x in board if isinstance(x, list) and x[0] == 'footprint'
                  and any(isinstance(p, list) and p[:3] == ['property', '"Reference"', '"J6"'] for p in x))
        pads = [x for x in j6 if isinstance(x, list) and x[0] == 'pad']
        self.assertEqual(len(pads), 1)
        self.assertIsNone(child(pads[0], 'drill'))
        self.assertEqual(pads[0][2], 'smd')

    def test_initializer_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'Refusing to overwrite'):
                oem.candidate(Path(directory))

    def test_failed_generation_is_not_published(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'candidate'
            def fail(staged):
                staged.mkdir()
                (staged / 'ps28-modern.kicad_pcb').write_text('partial')
                raise RuntimeError('deliberate test failure')
            with patch.object(oem, '_candidate', side_effect=fail):
                with self.assertRaisesRegex(RuntimeError, 'deliberate'):
                    oem.candidate(output)
            self.assertFalse(output.exists())
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_lc_units_and_differential_equivalence(self):
        fn = 1 / (2 * math.pi * math.sqrt(10e-6 * 940e-9))
        self.assertGreater(fn, 51000)
        self.assertLess(fn, 53000)
        self.assertAlmostEqual(output_lc_magnitude(0), 4 / (4 + .01752))
        self.assertAlmostEqual(output_lc_magnitude(fn, winding_dcr=0),
                               2 * math.sqrt(940e-9 / 10e-6))
        self.assertGreater(output_lc_magnitude(80), .99)
        self.assertLess(output_lc_magnitude(1e6), .003)


if __name__ == '__main__':
    unittest.main()
