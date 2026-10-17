import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import render_kicad_gallery as gallery


class RenderGalleryTests(unittest.TestCase):
    def test_assets_match_manifest_and_current_board(self):
        directory = ROOT / "docs/images/kicad-3d"
        manifest = json.loads((directory / "manifest.json").read_text())
        self.assertIn("kicad-cli pcb render", manifest["method"])
        self.assertFalse(manifest["hardware_validated"])
        self.assertFalse(manifest["manufacturing_approved"])
        self.assertEqual(manifest["generator_sha256"],
                         hashlib.sha256((ROOT / "scripts/render_kicad_gallery.py").read_bytes()).hexdigest())
        self.assertEqual(manifest["pcb_sha256"], hashlib.sha256(gallery.BOARD.read_bytes()).hexdigest())
        self.assertEqual(set(manifest["asset_sha256"]),
                         {"system-isometric.png", "system-top.png", "system-bottom.png", "system-orbit.gif"})
        self.assertEqual(len(manifest["native_commands"]), 3 + manifest["frames"])
        for name, digest in manifest["asset_sha256"].items():
            content = (directory / name).read_bytes()
            self.assertEqual(hashlib.sha256(content).hexdigest(), digest)
            self.assertTrue(content.startswith(b"\x89PNG" if name.endswith(".png") else b"GIF89a"))

    def test_only_test_pads_and_block_holes_lack_models(self):
        missing = gallery.missing_models(gallery.BOARD)
        self.assertEqual(missing, ["H6", "J6"] + sorted(f"TP{n}" for n in [102, 103, *range(110, 131)]))

    def test_block_model_faces_outward_in_kicad(self):
        text = (ROOT / "kicad/models/ps28-bodies/thermal_block.wrl").read_text()
        self.assertIn("ccw FALSE", text)


if __name__ == "__main__":
    unittest.main()
