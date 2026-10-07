#!/usr/bin/env python3
"""Download allowlisted manufacturer PDFs; do not execute retrieved content."""

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "tpa3255": "https://www.ti.com/lit/ds/symlink/tpa3255.pdf",
    "slou441": "https://www.ti.com/lit/pdf/slou441",
    "slar129a": "https://www.ti.com/lit/df/slar129a/slar129a.pdf",
    "slar130a": "https://www.ti.com/lit/df/slar130a/slar130a.pdf",
}


def valid_pdf(data):
    return data.startswith(b"%PDF-") and len(data) > 100


def main():
    manifest = ROOT / "reference/manifest.json"
    previous = json.loads(manifest.read_text()) if manifest.exists() else []
    refreshed_files = {f"reference/ti/{name}.pdf" for name in SOURCES}
    records = [
        record for record in previous if record.get("file") not in refreshed_files
    ]
    directory = ROOT / "reference/ti"
    directory.mkdir(parents=True, exist_ok=True)
    # Fetch all first: a network failure does not leave a partially refreshed set.
    fetched = []
    for name, url in SOURCES.items():
        request = urllib.request.Request(
            url, headers={"User-Agent": "PS28-engineering-reference/1.0"}
        )
        with urllib.request.urlopen(request, timeout=45) as response:
            final = response.geturl()
            parsed = urllib.parse.urlparse(final)
            if parsed.scheme != "https" or parsed.hostname not in {
                "www.ti.com",
                "ti.com",
            }:
                raise ValueError(f"Unexpected redirect: {final}")
            data = response.read(20 * 1024 * 1024 + 1)
        if len(data) > 20 * 1024 * 1024 or not valid_pdf(data):
            raise ValueError(f"Invalid/oversized PDF: {name}")
        fetched.append((name, url, final, data))
    for name, url, final, data in fetched:
        path = directory / f"{name}.pdf"
        temp = path.with_suffix(".pdf.tmp")
        temp.write_bytes(data)
        temp.replace(path)
        records.append(
            {
                "file": str(path.relative_to(ROOT)),
                "url": url,
                "resolved_url": final,
                "accessed": datetime.now(timezone.utc).isoformat(),
                "sha256": hashlib.sha256(data).hexdigest(),
                "license": "Third-party copyright; local engineering reference only",
                "review_status": "Downloaded; revision and circuit review required",
            }
        )
    (ROOT / "reference/manifest.json").write_text(json.dumps(records, indent=2) + "\n")
    print(
        "Manufacturer PDFs downloaded. Review revisions and manifest diff before relying on them."
    )


if __name__ == "__main__":
    main()
