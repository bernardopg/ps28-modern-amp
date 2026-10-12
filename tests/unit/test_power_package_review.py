import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from create_power_package_review import reviewed_parts, generate
from create_power_d021 import parts
import tempfile


class PowerPackageReviewTests(unittest.TestCase):
    def test_removes_false_selections_without_changing_topology(self):
        original = {p['ref']: p for p in parts()}
        reviewed = {p['ref']: p for p in reviewed_parts()}
        self.assertEqual(set(original), set(reviewed))
        for ref in original:
            self.assertEqual(original[ref]['nets'], reviewed[ref]['nets'])
        for ref in ('D301', 'D302', 'C301', 'C302', 'J301'):
            self.assertEqual(reviewed[ref]['footprint'], '')
            self.assertIn('TBD', reviewed[ref]['mpn'])
        self.assertIn('150 A', reviewed['D301']['mpn'])
        self.assertNotIn('6.3', reviewed['F301']['value'])
        self.assertIn('do not disconnect PVDD', reviewed['D303']['mpn'])
        self.assertEqual(parts(), list(original.values()))

    def test_existing_directory_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileExistsError):
                generate(Path(directory))
