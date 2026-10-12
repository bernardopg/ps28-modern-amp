import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import integrate_candidate as base
from create_rev_a_bench import DEFERRED, JOINS, bench_parts

BENCH = ROOT / "kicad/rev-a-bench"


class RevABenchTests(unittest.TestCase):
    def test_only_the_t1_rectifier_block_is_deferred(self):
        full = {p["ref"] for p in base.system_parts()}
        self.assertLessEqual(DEFERRED, full)
        self.assertEqual({p["ref"] for p in bench_parts(base.system_parts())}, full - DEFERRED)
        # The supervisor, buck and bleeder still see PVDD on the bench board.
        self.assertTrue({"U302", "R301", "D303"} <= full - DEFERRED)

    def test_generated_candidate_feeds_pvdd_from_j1_and_stays_unapproved(self):
        m = json.loads((BENCH / "system-manifest.json").read_text())
        refs = {p["ref"]: p for p in m["parts"]}
        self.assertEqual(len(refs), 198)
        self.assertFalse(DEFERRED & set(refs))
        self.assertEqual(refs["J1"]["nets"], {"1": "PVDD", "2": "GND"})
        self.assertEqual(refs["U1"]["nets"]["36"], "PVDD")
        self.assertEqual(m["staged_validation"]["bench_joins_checked"], len(JOINS))
        self.assertEqual(m["unassigned_footprints"], [])
        self.assertFalse(m["routed"] or m["hardware_validated"] or m["manufacturing_approved"])
        self.assertNotIn("T1_A", (BENCH / "system-candidate.kicad_pcb").read_text())

    def test_review_report_matches_sources(self):
        r = json.loads((ROOT / "tests/reports/rev-a-bench-review.json").read_text())
        self.assertEqual(r["drc"]["geometry_errors"], 0)
        self.assertEqual(r["drc"]["schematic_parity"], 0)
        self.assertFalse(r["manufacturing_approved"])
        for name, expected in r["source_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected, name)


if __name__ == "__main__":
    unittest.main()
