"""make erc/drc must validate the product, never a historical PCB silently."""
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import eda_check


class CandidateDispatchTests(unittest.TestCase):
    def test_default_native_checks_target_system_candidate(self):
        for kind, ext, text in [("erc", "sch", '(symbol (lib_id "Device:R"))'),
                                ("drc", "pcb", '(footprint "test")')]:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                directory = root / "kicad/system-candidate"
                directory.mkdir(parents=True)
                design = directory / f"system-candidate.kicad_{ext}"
                design.write_text(text)
                with patch.object(eda_check, "ROOT", root), patch.object(sys, "argv", ["eda_check.py", kind]), \
                     patch.object(eda_check.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run:
                    self.assertEqual(eda_check.main(), 0)
                    command = run.call_args.args[0]
                    self.assertEqual(command[-1], str(design))
                    if kind == "drc":
                        self.assertIn("--schematic-parity", command)
                        self.assertIn("--refill-zones", command)

    def test_missing_candidate_never_falls_back_to_selected_core(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            historical = root / "kicad/core-selected"
            historical.mkdir(parents=True)
            (historical / "ps28-modern.kicad_pro").write_text("{}")
            (historical / "ps28-modern.kicad_pcb").write_text('(footprint "test")')
            with patch.object(eda_check, "ROOT", root), patch.object(sys, "argv", ["eda_check.py", "drc"]), \
                 patch.object(eda_check.subprocess, "run") as run:
                self.assertEqual(eda_check.main(), 2)
                run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
