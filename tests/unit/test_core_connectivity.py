from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from check_core import check, design_dir


class CoreConnectivityTests(unittest.TestCase):
    def test_actual_capture_and_pad_nets_match(self):
        failures, report = check()
        self.assertEqual(failures, [])
        self.assertEqual(report["components"], 47)
        self.assertEqual(report["placed_footprints"], 47)
        self.assertEqual(report["placed_pads_checked"], 142)
        self.assertFalse(report["manufacturing_approved"])

    def copy_design(self, destination):
        (destination / "kicad").mkdir()
        for name in [
            "ps28-modern.kicad_sch",
            "ps28-modern.kicad_pcb",
            "core-manifest.json",
        ]:
            shutil.copy2(design_dir() / name, destination / "kicad" / name)

    def test_grounding_speaker_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_design(root)
            schematic = root / "kicad/ps28-modern.kicad_sch"
            schematic.write_text(
                schematic.read_text().replace('(label "SPK_N"', '(label "GND"')
            )
            failures, _ = check(root)
            self.assertTrue(
                any("Speaker must be floating" in error for error in failures)
            )

    def test_wrong_thermal_footprint_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_design(root)
            board = root / "kicad/ps28-modern.kicad_pcb"
            board.write_text(
                board.read_text().replace("TopEP4.14x7.01mm", "EP5.2x14mm")
            )
            failures, _ = check(root)
            self.assertTrue(any("PowerPAD" in error for error in failures))


if __name__ == "__main__":
    unittest.main()
