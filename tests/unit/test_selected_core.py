from pathlib import Path
import json
import math
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import eda_check
from check_core import check, child, design_dir, text
from create_core_draft import parse


class SelectedCoreTests(unittest.TestCase):
    def test_manufacturer_lands_not_approximate_substitutes(self):
        directory = design_dir()
        manifest = json.loads((directory / 'core-manifest.json').read_text())
        self.assertFalse(manifest['mechanical_approved'])
        self.assertFalse(manifest['manufacturing_approved'])
        self.assertEqual(manifest['unassigned_footprints'], [])
        parts = {p['ref']: p for p in manifest['parts']}
        for ref in ['C1','C14','C15','C22','C23','C26','C27','L1','L2','J1','J5','J6']:
            self.assertTrue(parts[ref]['mpn'])
            self.assertTrue(parts[ref]['source'])
        for ref in ['C14','C15']:
            self.assertEqual(parts[ref]['mpn'],'UHE1J152MHD')
            self.assertEqual(parts[ref]['geometry']['height_max_mm'],42)
            self.assertEqual(parts[ref]['geometry']['ripple_A_100kHz_105C'],2.470)
            self.assertEqual(parts[ref]['geometry']['ripple_A_120Hz_105C'],1.976)
        tree = parse((directory / 'ps28-modern.kicad_pcb').read_text())
        footprints = {}
        for node in tree:
            if isinstance(node,list) and node[0]=='footprint':
                ref=next(text(x[2]) for x in node if isinstance(x,list) and x[:2]==['property','"Reference"'])
                footprints[ref]=node
        for ref in ['J1','J5']:
            pads=[x for x in footprints[ref] if isinstance(x,list) and x[0]=='pad']
            xy=[list(map(float,child(x,'at')[1:3])) for x in pads]
            self.assertAlmostEqual(math.dist(*xy),5.00)  # This MPN is NOT 5.08mm.
            self.assertTrue(all(float(child(x,'drill')[1])==1.3 for x in pads))
        for pad in [x for x in footprints['C1'] if isinstance(x,list) and x[0]=='pad']:
            self.assertEqual(float(child(pad,'drill')[1]),0.9)
        for ref in ['L1','L2']:
            dummy=[x for x in footprints[ref] if isinstance(x,list) and x[:2]==['pad','""']]
            self.assertEqual(len(dummy),1)
            self.assertIsNone(child(dummy[0],'net'))  # Tab is mechanical, not grounded winding.

    def test_original_case_fit_is_not_inferred_from_external_dimensions(self):
        data = json.loads((ROOT / 'mechanical/ps28-original-integration.json').read_text())
        for key in ['plate_inner_usable_width_mm', 'plate_inner_usable_height_mm',
                    'plate_hole_centers_mm', 'existing_heatsink_contact_and_hole_geometry_mm',
                    'component_side_available_depth_mm']:
            self.assertIsNone(data[key])
        self.assertFalse(data['mechanical_approved'])
        self.assertFalse(data['manufacturing_approved'])
        self.assertTrue(data['J6_is_not_an_original_case_hole'])
        self.assertTrue(data['preserve_original_mounting_points'])
        self.assertFalse(data['allow_new_plate_holes'])
        self.assertFalse(data['allow_relocation_of_original_mounts'])
        oem={part['part_number']:part for part in data['documented_OEM_parts_mm']}
        self.assertEqual(oem['302-AL-00406-1BDE']['dimensions_as_listed'],[300,200,2.5])
        self.assertEqual(oem['323-AL-00106-0BBE']['dimensions_as_listed'],[117.5,71.5,25])
        self.assertFalse(data['original_pcb_artwork']['declared_scale_or_dimensioned_hole_centers'])

    def test_undefined_layer_is_not_a_valid_draft(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'kicad').mkdir()
            for name in ['core-manifest.json','ps28-modern.kicad_sch','ps28-modern.kicad_pcb']:
                shutil.copy2(design_dir()/name,root/'kicad'/name)
            board=root/'kicad/ps28-modern.kicad_pcb'
            board.write_text(board.read_text().replace('(layer "F.Fab")','(layer "Rescue")',1))
            failures,_=check(root)
            self.assertTrue(any('Undefined PCB layer' in error for error in failures))

    def test_failed_or_empty_drc_does_not_reuse_old_report(self):
        for content in ['(kicad_pcb)', '(kicad_pcb (footprint "sample"))']:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                root=Path(directory);(root/'kicad').mkdir();(root/'build').mkdir()
                (root/'kicad/ps28-modern.kicad_pcb').write_text(content)
                report=root/'build/drc.json';report.write_text('{"violations":[]}')
                with patch.object(eda_check,'ROOT',root), patch.object(sys,'argv',['eda_check.py','drc']), patch.object(eda_check.subprocess,'run',return_value=SimpleNamespace(returncode=3)):
                    self.assertNotEqual(eda_check.main(),0)
                self.assertFalse(report.exists())


if __name__ == '__main__':
    unittest.main()
