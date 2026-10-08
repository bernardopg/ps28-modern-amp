import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import render_kicad_gallery as gallery


class RenderGalleryTests(unittest.TestCase):
    def test_assets_match_native_render_manifest_and_board(self):
        directory = ROOT / "docs/images/kicad-3d"
        manifest = json.loads((directory / "manifest.json").read_text())
        self.assertIn("kicad-cli pcb render", manifest["method"])
        self.assertFalse(manifest["hardware_validated"])
        self.assertFalse(manifest["manufacturing_approved"])
        self.assertEqual(len(manifest["asset_sha256"]), 8)
        self.assertEqual(
            manifest["generator_sha256"],
            hashlib.sha256(
                (ROOT / "scripts/render_kicad_gallery.py").read_bytes()
            ).hexdigest(),
        )
        context = manifest["electrical_context"]
        self.assertEqual(context, gallery.electrical_context())
        self.assertEqual(context["scope"], "POWER_CORE_ONLY")
        self.assertFalse(context["analog_protection_integrated_in_rendered_pcbs"])
        self.assertEqual(context["protected_analog_capture_components"], 32)
        self.assertEqual(len(context["protected_analog_unassigned_footprints"]), 13)
        for name, digest in manifest["asset_sha256"].items():
            content = (directory / name).read_bytes()
            self.assertEqual(hashlib.sha256(content).hexdigest(), digest)
            self.assertTrue(
                content.startswith(b"\x89PNG\r\n\x1a\n")
                if name.endswith(".png")
                else content.startswith(b"GIF89a")
            )
        for entry in manifest["designs"].values():
            content = (ROOT / entry["pcb"]).read_bytes()
            self.assertEqual(hashlib.sha256(content).hexdigest(), entry["pcb_sha256"])
            self.assertEqual(entry["footprints"], 47)
            self.assertEqual(entry["frames"], 16)
            self.assertEqual(len(entry["native_commands"]), 19)
            self.assertIn("U1", entry["without_available_model"])
            self.assertIn("L1", entry["without_available_model"])
            self.assertEqual(len(entry["model_audit"]), 47)
            for command in entry["native_commands"]:
                self.assertEqual(command[:3], ["kicad-cli", "pcb", "render"])

    def test_failed_or_incomplete_generation_preserves_existing_gallery(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "gallery"
            output.mkdir()
            (output / "manifest.json").write_text("old manifest")
            (output / "selected-top.png").write_bytes(b"old asset")
            with (
                self.assertRaises(RuntimeError),
                gallery.staged_assets(output) as staging,
            ):
                (staging / "selected-top.png").write_bytes(b"incomplete new asset")
                raise RuntimeError("native render failed")
            self.assertEqual((output / "selected-top.png").read_bytes(), b"old asset")
            with (
                self.assertRaises(ValueError),
                gallery.staged_assets(output) as staging,
            ):
                (staging / "manifest.json").write_text(json.dumps({"asset_sha256": {}}))
            self.assertEqual((output / "manifest.json").read_text(), "old manifest")

    def test_invalid_asset_hash_preserves_previous_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "gallery"
            output.mkdir()
            (output / "selected-top.png").write_bytes(b"previous")
            with (
                self.assertRaises(ValueError),
                gallery.staged_assets(output) as staging,
            ):
                assets = {}
                for key in gallery.DESIGNS:
                    for view, extension in [
                        ("isometric", "png"),
                        ("top", "png"),
                        ("bottom", "png"),
                        ("orbit", "gif"),
                    ]:
                        name = f"{key}-{view}.{extension}"
                        (staging / name).write_bytes(b"new")
                        assets[name] = "0" * 64
                (staging / "manifest.json").write_text(
                    json.dumps({"asset_sha256": assets})
                )
            self.assertEqual((output / "selected-top.png").read_bytes(), b"previous")

    def test_successful_generation_preserves_manual_readme(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "gallery"
            output.mkdir()
            (output / "README.md").write_text("manual notes")
            with gallery.staged_assets(output) as staging:
                assets = {}
                for key in gallery.DESIGNS:
                    for view, extension in [
                        ("isometric", "png"),
                        ("top", "png"),
                        ("bottom", "png"),
                        ("orbit", "gif"),
                    ]:
                        name = f"{key}-{view}.{extension}"
                        content = name.encode()
                        (staging / name).write_bytes(content)
                        assets[name] = hashlib.sha256(content).hexdigest()
                (staging / "manifest.json").write_text(
                    json.dumps({"asset_sha256": assets})
                )
            self.assertEqual((output / "README.md").read_text(), "manual notes")
            self.assertEqual(
                len(json.loads((output / "manifest.json").read_text())["asset_sha256"]),
                8,
            )


if __name__ == "__main__":
    unittest.main()
