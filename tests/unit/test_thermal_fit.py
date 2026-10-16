import copy
import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from check_thermal_fit import budget, inspect, mesh_geometry, mesh_ray_hits, resistance_mm


class ThermalBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=json.loads((ROOT/'mechanical/thermal-fit.json').read_text())

    def test_units_and_invalid_contact(self):
        self.assertAlmostEqual(resistance_mm(.05,3,18),.9259259259)
        for args in [(0,3,18),(.05,0,18),(.05,3,0)]:
            with self.assertRaises(ValueError):resistance_mm(*args)

    def test_budget_uses_junction_to_case_not_conditional_rja(self):
        r=budget(self.config)
        self.assertEqual(r['rjc_top_K_W'],.36)
        self.assertAlmostEqual(r['r_pedestal_K_W'],.6986027944)
        self.assertAlmostEqual(r['r_junction_to_profile_range_K_W'][1],3.9749922377)
        self.assertFalse(r['legacy_path_measured'])
        self.assertFalse(r['thermal_performance_validated'])

    def test_no_continuous_power_rating_is_invented(self):
        r=budget(self.config)
        bad=next(c for c in r['cases'] if c['ambient_C']==40 and c['loss_W']==20 and c['legacy_path_K_W']==3)
        self.assertFalse(bad['worst_within_recommended_range'])
        limit=next(c for c in r['required_limits'] if c['ambient_C']==40 and c['loss_W']==10)
        self.assertAlmostEqual(limit['legacy_path_max_K_W_for_design_target'],3.0250077623)
        self.assertFalse(self.config['manufacturing_approved'])

    def test_world_model_is_at_H5_not_local_origin(self):
        c=self.config;vertices,_=mesh_geometry(ROOT/'kicad/models/ps28-bodies/thermal_block.wrl',c['clamp_holes_xy_mm'][0])
        expected=[c['body_mm']['x'],c['body_mm']['y'],[c['pedestal']['bottom_z_nominal_mm'],c['body_mm']['z'][1]]]
        for k,(lo,hi) in enumerate(expected):
            self.assertAlmostEqual(min(v[k] for v in vertices),lo,places=3)
            self.assertAlmostEqual(max(v[k] for v in vertices),hi,places=3)

    def test_actual_mesh_has_holes_at_owner_height(self):
        c=self.config;vertices,triangles=mesh_geometry(ROOT/'kicad/models/ps28-bodies/thermal_block.wrl',c['clamp_holes_xy_mm'][0])
        for x in c['side_holes']['x_mm']:
            self.assertFalse(mesh_ray_hits(vertices,triangles,(x,40,23.65),(0,1,0)))
            self.assertTrue(mesh_ray_hits(vertices,triangles,(x,40,6.35),(0,1,0)))
            # Test the full M3 shaft boundary at all combined alignment corners,
            # not just a centre ray through a potentially undersized slot.
            dx,dz=c['side_holes']['combined_alignment_budget_xz_mm']
            for sx in (-dx,dx):
                for sz in (-dz,dz):
                    for k in range(16):
                        angle=k*math.tau/16
                        origin=(x+sx+1.5*math.cos(angle),40,23.65+sz+1.5*math.sin(angle))
                        self.assertFalse(mesh_ray_hits(vertices,triangles,origin,(0,1,0)))
        px,py=c['pedestal']['center_xy_mm']
        hits=mesh_ray_hits(vertices,triangles,(px,py,-5),(0,0,1))
        self.assertAlmostEqual(-5+hits[0],1.2,places=3)
        for x,y in c['clamp_holes_xy_mm']:
            hits=mesh_ray_hits(vertices,triangles,(x,y,-5),(0,0,1))
            self.assertAlmostEqual(-5+hits[0],c['body_mm']['z'][0]+c['clamp_tap_depth_mm'],places=3)

    @unittest.skipUnless(importlib.util.find_spec('pcbnew'),'Native KiCad required')
    def test_nominal_fit_preserves_mounts_and_has_height_margins(self):
        r=inspect(self.config)
        self.assertTrue(r['nominal_fit_pass'])
        self.assertFalse(r['physical_fit_validated'])
        self.assertGreater(min(r['pedestal_min_pad_margin_after_xy_budget_mm']),0)
        self.assertGreater(r['slot_combined_error_margin_mm'],0)
        self.assertGreaterEqual(min(p['worst_body_clearance_mm'] for p in r['under_body_parts']),.2)
        self.assertAlmostEqual(r['required_stop_selection_mm'][1],3.5)
        coils=[p for p in r['external_side_hardware_clearances'] if p['reference'] in ('L1','L2')]
        self.assertEqual({p['reference'] for p in coils},{'L1','L2'})
        self.assertGreaterEqual(min(p['worst_vertical_clearance_mm'] for p in coils),4.5-1e-9)

    @unittest.skipUnless(importlib.util.find_spec('pcbnew'),'Native KiCad required')
    def test_reverting_old_hole_height_or_large_pedestal_fails(self):
        for field in ['hole','pedestal','datum','oldslot']:
            c=copy.deepcopy(self.config)
            if field=='hole':c['side_holes']['z_mm']=6.35
            elif field=='pedestal':c['pedestal']['size_xy_mm']=[8,5.2]
            elif field=='datum':c['side_holes']['combined_alignment_budget_xz_mm'][1]=1.2
            else:c['side_holes']['slot_total_height_mm']=7.4
            with self.assertRaises(AssertionError):inspect(c)


if __name__=='__main__':unittest.main()
