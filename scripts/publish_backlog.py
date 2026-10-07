#!/usr/bin/env python3
"""Create an initial GitHub issue/milestone mirror; dry-run unless --apply.
Existing issues are never overwritten or reopened. Local tasks remain canonical.
"""

from pathlib import Path
import argparse
import json
import subprocess

from validate import metadata

ROOT = Path(__file__).resolve().parents[1]
REPO = "bernardopg/ps28-modern-amp"
MILESTONES = {
    "M0": "Foundation and reproducible setup",
    "M1": "Requirements and feasibility - G0",
    "M2": "Validated schematic - G1",
    "M3": "Layout and manufacturing approval - G2/G3",
    "M4": "Bench prototype and acoustic integration - G4/G5",
}


def api(endpoint, data=None):
    command = ["gh", "api", f"repos/{REPO}/{endpoint}"]
    if data is not None:
        command += ["--method", "POST", "--input", "-"]
    result = subprocess.run(
        command,
        input=json.dumps(data) if data is not None else None,
        capture_output=True,
        text=True,
        check=True,
        timeout=45,
    )
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="Create missing milestones/issues remotely"
    )
    args = parser.parse_args()
    tasks = []
    for path in sorted((ROOT / ".tasks/items").glob("*.md")):
        body = path.read_text()
        data = {k.strip(): v.strip() for k, v in metadata(body).items()}
        tasks.append((path, data, body))
    if not args.apply:
        print(
            f"DRY RUN: {len(tasks)} task mirrors, 5 milestones in {REPO}; no network mutation."
        )
        return
    milestones = {
        item["title"].split(":", 1)[0]: item["number"]
        for item in api("milestones?state=all&per_page=100")
    }
    for ident, title in MILESTONES.items():
        if ident not in milestones:
            milestones[ident] = api(
                "milestones",
                {
                    "title": f"{ident}: {title}",
                    "description": "No dates promised; human evidence gates required.",
                },
            )["number"]
    # The initial project has <100 tasks. Fail rather than silently miss pagination.
    issues = api("issues?state=all&per_page=100")
    if len(issues) >= 100:
        raise RuntimeError("Pagination required before publishing a larger backlog")
    existing = {item["title"].split("]", 1)[0].lstrip("["): item for item in issues}
    links = {}
    for path, data, body in tasks:
        ident = data["id"]
        if ident in existing:
            issue = existing[ident]
        else:
            local = path.relative_to(ROOT)
            issue = api(
                "issues",
                {
                    "title": f"[{ident}] {data['title']}",
                    "body": f"Initial mirror of `{local}`; local task is canonical.\n"
                    f"Sprint: {data['sprint']}; status at publication: {data['status']}.\n"
                    "No purchase/manufacturing/energization authorization.\n\n" + body,
                    "milestone": milestones[data["milestone"]],
                },
            )
            if data["status"] == "Done":
                subprocess.run(
                    [
                        "gh",
                        "issue",
                        "close",
                        str(issue["number"]),
                        "--repo",
                        REPO,
                        "--comment",
                        "Infrastructure task completed; evidence in tests/reports/setup.md. Not hardware sign-off.",
                    ],
                    check=True,
                    timeout=45,
                )
        links[ident] = issue["html_url"]
        print(f"{ident}: {issue['html_url']}")
    (ROOT / ".tasks/github-mirror.json").write_text(json.dumps(links, indent=2) + "\n")


if __name__ == "__main__":
    main()
