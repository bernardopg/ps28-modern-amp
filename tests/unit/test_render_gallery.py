from pathlib import Path
import hashlib
import json
import unittest

ROOT = Path(__file__).resolve().parents[2]


class RenderGalleryTests(unittest.TestCase):
    def test_assets_match_native_render_manifest_and_board(self):
        directory = ROOT / 'docs/images/kicad-3d'
        manifest = json.loads((directory / 'manifest.json').read_text())
        self.assertIn('kicad-cli pcb render', manifest['method'])
        self.assertFalse(manifest['hardware_validated'])
        self.assertFalse(manifest['manufacturing_approved'])
        self.assertEqual(len(manifest['asset_sha256']), 8)
        for name, digest in manifest['asset_sha256'].items():
            content = (directory / name).read_bytes()
            self.assertEqual(hashlib.sha256(content).hexdigest(), digest)
            self.assertTrue(content.startswith(b'\x89PNG\r\n\x1a\n') if name.endswith('.png')
                            else content.startswith(b'GIF89a'))
        for entry in manifest['designs'].values():
            content = (ROOT / entry['pcb']).read_bytes()
            self.assertEqual(hashlib.sha256(content).hexdigest(), entry['pcb_sha256'])
            self.assertEqual(entry['footprints'], 47)
            self.assertEqual(entry['frames'], 16)
            self.assertEqual(len(entry['native_commands']), 19)
            self.assertIn('U1', entry['without_available_model'])
            self.assertIn('L1', entry['without_available_model'])
            self.assertEqual(len(entry['model_audit']), 47)
            for command in entry['native_commands']:
                self.assertEqual(command[:3], ['kicad-cli', 'pcb', 'render'])


if __name__ == '__main__':
    unittest.main()
