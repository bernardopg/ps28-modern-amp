import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from export_fab import run, write_checksums


class FabExportTests(unittest.TestCase):
    @patch("export_fab.subprocess.run")
    def test_only_rule_checks_may_return_violation_code(self, mocked):
        mocked.return_value = subprocess.CompletedProcess([], 5, "", "failed")
        run("sch", "erc", "test.kicad_sch")
        run("pcb", "drc", "test.kicad_pcb")
        for args in [("pcb", "export", "gerbers"), ("sch", "export", "bom")]:
            with self.assertRaises(SystemExit):
                run(*args)

    @patch("export_fab.subprocess.run")
    def test_other_failures_are_never_accepted(self, mocked):
        mocked.return_value = subprocess.CompletedProcess([], 1, "", "failed")
        with self.assertRaises(SystemExit):
            run("pcb", "drc", "test.kicad_pcb")

    def test_manifest_includes_completed_summary_and_not_itself(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "summary.json").write_text('{"manufacturing_approved": false}\n')
            (out / "gerber").mkdir()
            (out / "gerber/test.gbr").write_text("draft\n")
            (out / "SHA256SUMS").write_text("stale manifest")
            write_checksums(out)
            lines = (out / "SHA256SUMS").read_text().splitlines()
            self.assertEqual(len(lines), 2)
            for line in lines:
                digest, name = line.split("  ", 1)
                self.assertNotEqual(name, "SHA256SUMS")
                self.assertEqual(digest, hashlib.sha256((out / name).read_bytes()).hexdigest())
            self.assertTrue(any(line.endswith("  summary.json") for line in lines))


if __name__ == "__main__":
    unittest.main()
