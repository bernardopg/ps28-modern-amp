import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InfrastructureTests(unittest.TestCase):
    def test_repository_validates(self):
        self.assertEqual(load('validate').validate(), [])

    def test_empty_eda_is_rejected(self):
        checker = load('eda_check')
        self.assertFalse(checker.has_design('(kicad_sch (lib_symbols))', 'erc'))
        self.assertFalse(checker.has_design('(kicad_pcb (layers))', 'drc'))

    def test_design_detection(self):
        checker = load('eda_check')
        self.assertTrue(checker.has_design('(symbol\n(lib_id "Device:R"))', 'erc'))
        self.assertTrue(checker.has_design('(footprint "Resistor_SMD:R_0603")', 'drc'))

    def test_ideal_response(self):
        response = load('simulate').lr4_magnitude
        self.assertEqual(response(80), 0.5)
        self.assertGreater(response(10), 0.999)
        self.assertLess(response(800), 0.000101)

    def test_download_content_guard(self):
        guard = load('fetch_reference').valid_pdf
        self.assertFalse(guard(b'<html>access denied</html>'))
        self.assertFalse(guard(b'%PDF-short'))
        self.assertTrue(guard(b'%PDF-1.7\n' + b'x' * 200))

    def test_missing_metadata_fails(self):
        with self.assertRaises(ValueError):
            load('validate').metadata('# no frontmatter')

    def test_blank_repo_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertTrue(load('validate').validate(Path(directory)))


if __name__ == '__main__':
    unittest.main()
