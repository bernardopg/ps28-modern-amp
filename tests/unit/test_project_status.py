import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from validate import metadata


class ProjectStatusTests(unittest.TestCase):
    def test_documentation_media_evidence_and_task_mirrors_are_current(self):
        report = json.loads(
            (ROOT / "tests/reports/documentation-media-refresh.json").read_text()
        )
        tasks = {}
        for p in (ROOT / ".tasks/items").glob("*.md"):
            meta = {k.strip(): v.strip() for k, v in metadata(p.read_text()).items()}
            tasks[meta["id"]] = meta["status"]
        mirrors = json.loads((ROOT / ".tasks/github-mirror.json").read_text())
        self.assertEqual(set(mirrors), set(tasks))
        self.assertEqual(len(set(mirrors.values())), len(mirrors))
        self.assertEqual(report["task_status_snapshot"], tasks)
        self.assertLessEqual(sum(v == "In Progress" for v in tasks.values()), 2)
        self.assertFalse(report["hardware_validated"])
        self.assertFalse(report["manufacturing_approved"])
        self.assertFalse(report["pcb_geometry_or_schematic_changed"])
        self.assertEqual(
            report["native_media"], {"pngs": 6, "gifs": 2, "frames_per_gif": 16}
        )
        for filename, expected in report["source_sha256"].items():
            self.assertEqual(
                hashlib.sha256((ROOT / filename).read_bytes()).hexdigest(),
                expected,
                filename,
            )
        for case in report["native_core_checks"].values():
            self.assertEqual(case["components"], 47)
            self.assertEqual(case["pads_checked"], 142)
            self.assertEqual(case["erc_unexcluded_violations"], 4)
            self.assertEqual(case["drc_geometry_violations"], 0)
            self.assertEqual(case["drc_parity_violations"], 0)
            self.assertEqual(case["unrouted_connections"], 109)
        self.assertEqual(
            report["analog_capture"],
            {
                "components": 32,
                "pins_checked": 80,
                "erc_violations": 0,
                "missing_footprints": 13,
                "pcb_integrated": False,
            },
        )


if __name__ == "__main__":
    unittest.main()
