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
            report["native_media"], {"pngs": 9, "gifs": 3, "frames_per_gif": 16}
        )
        # The 2026-10-08 record stays historical (no hardware change in THAT
        # refresh). A later hardware review must supply independently labelled,
        # current media evidence rather than overwrite its historical hashes.
        current = json.loads((ROOT / report["current_media_evidence"]).read_text())
        self.assertFalse(current["hardware_validated"])
        self.assertFalse(current["manufacturing_approved"])
        self.assertTrue(current["pcb_geometry_or_schematic_changed"])
        self.assertTrue(set(report["source_sha256"]).issubset(current["current_source_sha256"]))
        for filename, expected in current["current_source_sha256"].items():
            self.assertEqual(
                hashlib.sha256((ROOT / filename).read_bytes()).hexdigest(),
                expected,
                filename,
            )
        # Manufacturer PDFs are local-only copyrighted references, not Git assets.
        # Bind their recorded bytes to the versioned fetch manifest offline;
        # also verify the actual bytes whenever that local cache is present.
        references = {r["file"]: r for r in json.loads(
            (ROOT / "reference/manifest.json").read_text())}
        external = current["external_reference_sha256"]
        self.assertEqual(set(external), {
            "reference/ti/tpa3255.pdf",
            "reference/parts/littelfuse-smcj51a.pdf",
            "reference/parts/we-hcf-7443631000.pdf",
        })
        for filename, expected in external.items():
            self.assertEqual(expected, references[filename]["sha256"], filename)
            cached = ROOT / filename
            if cached.exists():
                self.assertEqual(hashlib.sha256(cached.read_bytes()).hexdigest(),
                                 expected, filename)
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
