import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from validate import metadata


class ProjectStatusTests(unittest.TestCase):
    def tasks(self):
        out = {}
        for p in (ROOT / ".tasks/items").glob("*.md"):
            meta = {k.strip(): v.strip() for k, v in metadata(p.read_text()).items()}
            out[meta["id"]] = meta["status"]
        return out

    def test_every_task_has_one_distinct_github_mirror(self):
        tasks = self.tasks()
        mirrors = json.loads((ROOT / ".tasks/github-mirror.json").read_text())
        self.assertEqual(set(mirrors), set(tasks))
        self.assertEqual(len(set(mirrors.values())), len(mirrors))
        self.assertLessEqual(sum(v == "In Progress" for v in tasks.values()), 2)

    def test_backlog_counts_match_task_files(self):
        tasks = self.tasks()
        text = (ROOT / ".tasks/project-backlog.md").read_text()
        done = sum(v == "Done" for v in tasks.values())
        self.assertIn(f"{len(tasks)} tasks, {done} Done", text)
        for ident, status in tasks.items():
            if status != "Done":
                self.assertIn(f"items/{ident}.md", text)

    def test_repository_holds_only_the_product_board(self):
        tracked = subprocess.check_output(["git", "ls-files", "kicad"], cwd=ROOT, text=True).split()
        boards = sorted(p for p in tracked if p.endswith(".kicad_pcb"))
        self.assertEqual(boards, ["kicad/system-candidate/system-candidate.kicad_pcb"])
        self.assertFalse((ROOT / "docs/archive").exists())


if __name__ == "__main__":
    unittest.main()
