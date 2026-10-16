#!/usr/bin/env python3
"""Read a fabrication draft with Gerbonara, independently from KiCad's parser."""
import hashlib
import json
import sys
import warnings
from pathlib import Path

from gerbonara import LayerStack
from gerbonara.utils import MM


def main():
    package = Path(sys.argv[1]).resolve()
    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter("always")
        stack = LayerStack.open(package / "gerber")
        bounds = stack.outline.bounding_box(unit=MM)
        width, height = [bounds[1][i] - bounds[0][i] for i in range(2)]
        assert len(stack.copper_layers) == 4, "Four copper layers required"
        # Gerber extents include the 0.05 mm outline stroke.
        assert abs(width - 154) < .1 and abs(height - 81) < .1, bounds
        assert stack.drill_pth and stack.drill_npth, "Separate PTH/NPTH drill files required"
        for side in ("top", "bottom"):
            (package / f"gerber-{side}.svg").write_text(str(stack.to_pretty_svg(side=side)))
    report = {"parser": "Gerbonara 1.6.3", "copper_layers": len(stack.copper_layers),
              "bounds_mm_including_outline_stroke": bounds,
              "pth_objects": len(stack.drill_pth.objects),
              "npth_objects": len(stack.drill_npth.objects),
              "warnings": sorted({str(w.message) for w in seen}),
              "scope": "File parsing, outline and layer inventory; not electrical/DFM sign-off",
              "manufacturing_approved": False,
              "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted((package / "gerber").iterdir()) if p.is_file()}}
    output = package / "independent-gerber-review.json"
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"4 copper layers; {report['pth_objects']} PTH / {report['npth_objects']} NPTH objects; {len(report['warnings'])} warnings")
    print(output)


if __name__ == "__main__":
    main()
