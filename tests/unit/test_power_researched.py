import sys
from pathlib import Path
import unittest
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'scripts'))
from create_power_researched import researched_parts, bulk_footprint, generate
from create_power_package_review import reviewed_parts
from create_core_draft import parse


class ResearchedPowerTests(unittest.TestCase):
    def test_new_candidates_preserve_topology_and_do_not_invent_diode_land_pattern(self):
        old={p['ref']:p for p in reviewed_parts()}
        new={p['ref']:p for p in researched_parts()}
        self.assertEqual(set(old),set(new))
        for ref in old: self.assertEqual(old[ref]['nets'],new[ref]['nets'])
        for ref in ('D301','D302'):
            self.assertIn('RHRP1560',new[ref]['mpn'])
            self.assertEqual(new[ref]['footprint'],'')
        for ref in ('C301','C302'):
            self.assertIn('LGU2A472MELC',new[ref]['mpn'])
            self.assertIn('TBD',new[ref]['mpn'])

    def test_bulk_pitch_drill_and_courtyard(self):
        tree=parse(bulk_footprint())
        pads=[p for p in tree if isinstance(p,list) and p[0]=='pad']
        self.assertEqual(len(pads),2)
        at=lambda p:next(x for x in p if isinstance(x,list) and x[0]=='at')
        drill=lambda p:next(x for x in p if isinstance(x,list) and x[0]=='drill')
        self.assertEqual(float(at(pads[1])[1])-float(at(pads[0])[1]),10)
        for p in pads: self.assertEqual(float(drill(p)[1]),2)
        self.assertIn('(end 23.75 0)',bulk_footprint())

    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as p:
            with self.assertRaises(FileExistsError): generate(Path(p))
