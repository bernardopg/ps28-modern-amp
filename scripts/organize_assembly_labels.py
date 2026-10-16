#!/usr/bin/env python3
"""Organize Fab reference labels without moving footprints or changing copper.

Values stay in footprint properties/BOM, but are hidden on Fab layers. Existing
silkscreen values (test-point and LED names) are left untouched. Run explicitly
AFTER generation/placement/routing; the default writes a separate output file.
"""

import argparse
import json
import math
from pathlib import Path

# Keep removed SWIG wrappers alive: destruction can invalidate native wrappers.
REMOVED_GRAPHICS = []


def organize(board, pcbnew):
    """Plan in memory; fail without saving if any reference cannot fit nearby."""
    fab = (pcbnew.F_Fab, pcbnew.B_Fab)
    occupied = {layer: [] for layer in fab}
    boundary = board.GetBoardEdgesBoundingBox()
    boundary.Inflate(-pcbnew.FromMM(0.5))
    hidden, duplicates, moved = [], [], []
    for drawing in board.GetDrawings():
        if drawing.GetClass() == "PCB_TEXT" and drawing.GetLayer() in fab:
            occupied[drawing.GetLayer()].append(drawing.GetBoundingBox())
    footprints = sorted(board.GetFootprints(), key=lambda f: f.GetReference())
    for fp in footprints:
        for graphic in list(fp.GraphicalItems()):
            if graphic.GetClass() != "PCB_TEXT" or graphic.GetLayer() not in fab:
                continue
            if graphic.GetText() == "${REFERENCE}":
                fp.Remove(graphic)
                # Remove transfers ownership; KiCad 10's SWIG destructor is unsafe
                # here. Keep the native object alive for this short batch process.
                graphic.thisown = False
                REMOVED_GRAPHICS.append(graphic)
                duplicates.append(fp.GetReference())
            elif graphic.IsVisible():
                occupied[graphic.GetLayer()].append(graphic.GetBoundingBox())
        value = fp.Value()
        if value.GetLayer() in fab and value.IsVisible():
            value.SetVisible(False)
            hidden.append(fp.GetReference())
    # Largest labels first, deterministic ordering for repeatable placement.
    footprints.sort(key=lambda f: (-len(f.GetReference()), f.GetReference()))
    offsets = [(x / 2, y / 2) for x in range(-16, 17) for y in range(-16, 17)
               if x * x + y * y <= 16 * 16]
    offsets.sort(key=lambda xy: (math.hypot(*xy), abs(xy[1]), xy))
    for fp in footprints:
        text = fp.Reference()
        # Non-Fab fields are not restyled (especially real silkscreen labels).
        if text.GetLayer() not in fab:
            continue
        old = pcbnew.ToMM(text.GetPosition())
        text.SetVisible(True)
        text.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8)))
        text.SetTextThickness(pcbnew.FromMM(0.12))
        text.SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
        text.SetMirrored(fp.IsFlipped())
        anchor = pcbnew.ToMM(fp.GetPosition())
        for dx, dy in offsets:
            text.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(anchor[0] + dx),
                                           pcbnew.FromMM(anchor[1] + dy)))
            box = text.GetBoundingBox()
            box.Inflate(pcbnew.FromMM(0.15))
            if boundary.Contains(box) and not any(box.Intersects(b) for b in occupied[text.GetLayer()]):
                occupied[text.GetLayer()].append(box)
                moved.append({"reference": fp.GetReference(), "layer": board.GetLayerName(text.GetLayer()),
                              "before_mm": old, "after_mm": pcbnew.ToMM(text.GetPosition()),
                              "offset_from_anchor_mm": round(math.hypot(dx, dy), 3)})
                break
        else:
            raise RuntimeError(f"No label position within 8 mm of {fp.GetReference()}; no file saved")
    return {"hidden_fab_values": hidden, "removed_duplicate_references": duplicates, "references": moved,
            "note": "Values retained in BOM/properties; silk and copper unchanged. Fab text bounding boxes separated by 0.3 mm."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error("Use a separate output path, review and validate before promotion")
    import pcbnew
    board = pcbnew.LoadBoard(str(args.input))
    result = organize(board, pcbnew)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pcbnew.SaveBoard(str(args.output), board)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Organized {len(result['references'])} references; hidden {len(result['hidden_fab_values'])} Fab values")


if __name__ == "__main__":
    main()
