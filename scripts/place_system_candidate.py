#!/usr/bin/env python3
"""Place every footprint of the system candidate inside the measured OEM outline.

Study placement for 3D review and PCB-001 iteration, NOT a routed or approved layout.
Frame (integrate_candidate.oem_mechanics): x = 20 is the upper board edge (OEM relay
end), x = 174 the lower edge (transformer end); y = 101 is the backplate edge.
Big/critical parts get fixed positions; the rest are packed on a 0.25 mm grid:
core and power parts near their block on top, logic/analog SMD on the bottom.
"""

import numpy as np

GRID = 0.25
GAP = 0.5  # courtyard-to-courtyard spacing
EDGE = 0.75
HOLE_KEEP = 4.0  # M3 head / L-bracket clearance radius

# (x, y, rotation) footprint centers in mm, KiCad frame. Top side.
FIXED = {
    # TPA3255 just beyond the profile outer leg (y = 68); long axis along the leg so a
    # thermal block can bridge the top PowerPAD and the leg face (TO-3P M3 holes).
    "U1": (90.5, 60.5, 90),
    # Output LC and speaker at the upper (relay) end, as in the OEM.
    "L1": (39.0, 32.0, 0), "L2": (39.0, 66.0, 180),
    "C22": (54.0, 25.0, 0), "C23": (54.0, 35.0, 0), "C26": (54.0, 52.0, 0), "C27": (54.0, 62.0, 0),
    "J5": (40.0, 94.0, 0), "J1": (50.0, 82.0, 0),
    # PVDD bulk around U1.
    "C301": (72.0, 33.0, 0), "C302": (110.0, 33.0, 0),
    "C14": (71.0, 56.0, 0), "C15": (110.0, 56.0, 0),
    "C1": (91.0, 27.0, 0), "K501": (91.0, 42.0, 0),
    # Transformer (lower) end: harness, CT fuse, rectifier, AUX buck, analog rail.
    "J301": (155.0, 96.0, 0), "F301": (130.0, 85.0, 90),
    "D301": (148.0, 82.0, 0), "D302": (148.0, 72.0, 0),
    "L301": (160.0, 60.0, 0), "R301": (140.0, 60.0, 0),
    "C201": (135.0, 30.0, 0), "C202": (135.0, 44.0, 0), "R201": (160.0, 33.0, 90),
    "C203": (148.0, 30.0, 0), "J4": (150.0, 45.0, 0),
}
# Packing targets per group: (top x, top y), preferred side.
TARGETS = {None: ((90.5, 55.0), "top"), "power": ((150.0, 55.0), "top"),
           "seq": ((60.0, 45.0), "bottom"), "iso": ((90.0, 62.0), "bottom"),
           "analog": ((130.0, 40.0), "bottom")}


def place(pcb, pcbnew, mech, parts):
    groups = {p["ref"]: p.get("group") for p in parts}
    x0, y0, x1, y1 = mech["outline"]
    nx, ny = int(round((x1 - x0) / GRID)), int(round((y1 - y0) / GRID))
    occ = {"top": np.zeros((ny, nx), bool), "bottom": np.zeros((ny, nx), bool)}
    yy, xx = np.mgrid[0:ny, 0:nx]
    cx, cy = x0 + (xx + 0.5) * GRID, y0 + (yy + 0.5) * GRID
    margin = (cx < x0 + EDGE) | (cx > x1 - EDGE) | (cy < y0 + EDGE) | (cy > y1 - EDGE)
    for side in occ:
        occ[side] |= margin
        for hx, hy in mech["holes"]:
            occ[side] |= (cx - hx) ** 2 + (cy - hy) ** 2 < HOLE_KEEP ** 2
    kx0, ky0, kx1, ky1 = mech["profile_keepout"]
    occ["top"] |= (cx >= kx0) & (cx <= kx1) & (cy >= ky0) & (cy <= ky1)

    def mm(v):
        return pcbnew.ToMM(v)

    def box(fp):
        layer = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
        court = fp.GetCourtyard(layer)
        bb = court.BBox() if court.OutlineCount() else fp.GetBoundingBox(False, False)
        return mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())

    def cells(b):
        l, t, r, btm = b
        return (slice(max(0, int((t - GAP - y0) / GRID)), min(ny, int(np.ceil((btm + GAP - y0) / GRID)))),
                slice(max(0, int((l - GAP - x0) / GRID)), min(nx, int(np.ceil((r + GAP - x0) / GRID)))))

    def mark(fp, side):
        occ[side][cells(box(fp))] = True
        if side == "top":  # THT pins also occupy the bottom side
            for pad in fp.Pads():
                if pad.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                    pb = pad.GetBoundingBox()
                    occ["bottom"][cells((mm(pb.GetLeft()), mm(pb.GetTop()),
                                         mm(pb.GetRight()), mm(pb.GetBottom())))] = True

    def put(fp, x, y, rot, side):
        if fp.IsFlipped() != (side == "bottom"):
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
        fp.SetOrientationDegrees(rot)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))

    def fits(side, w, h, target):
        sat = np.pad(occ[side].astype(np.int32).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
        kh, kw = int(np.ceil((h + 2 * GAP) / GRID)), int(np.ceil((w + 2 * GAP) / GRID))
        if kh > ny or kw > nx:
            return None
        win = sat[kh:, kw:] - sat[:-kh, kw:] - sat[kh:, :-kw] + sat[:-kh, :-kw]
        free = np.argwhere(win == 0)
        if not len(free):
            return None
        centers = np.column_stack((x0 + (free[:, 1] + kw / 2) * GRID, y0 + (free[:, 0] + kh / 2) * GRID))
        best = np.argmin(((centers - target) ** 2).sum(1))
        return float(centers[best][0]), float(centers[best][1])

    fps = {fp.GetReference(): fp for fp in pcb.GetFootprints() if not fp.IsBoardOnly()}
    placed = {}

    def pack(fp, target, sides, rotations):
        ref = fp.GetReference()
        for side in sides:
            options = []
            for rot in rotations:
                put(fp, 0, 0, rot, side)
                l, t, r, b = box(fp)
                pos = fits(side, r - l, b - t, target)
                if pos:
                    options.append((pos, rot))
            if options:
                pos, rot = min(options, key=lambda o: (o[0][0] - target[0]) ** 2 + (o[0][1] - target[1]) ** 2)
                put(fp, 0, 0, rot, side)
                l, t, r, b = box(fp)
                # Center the courtyard (not the footprint origin) on the chosen cell.
                put(fp, pos[0] - (l + r) / 2, pos[1] - (t + b) / 2, rot, side)
                mark(fp, side)
                placed[ref] = side
                return
        raise ValueError("No room for " + ref)

    # Anchors keep their intended rotation and take the nearest free spot to the target.
    for ref, (x, y, rot) in FIXED.items():
        if ref in fps:  # D-029 Rev A omits the deferred T1 rectifier anchors
            pack(fps[ref], (x, y), ["top"], [rot])
    rest = [fp for ref, fp in fps.items() if ref not in FIXED]

    def area(fp):
        put(fp, 0, 0, 0, "top")
        l, t, r, b = box(fp)
        return (r - l) * (b - t)
    for fp in sorted(rest, key=lambda fp: -area(fp)):
        smd = all(p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD for p in fp.Pads())
        target, prefer = TARGETS[groups.get(fp.GetReference())]
        sides = [prefer, "bottom" if prefer == "top" else "top"] if smd else ["top"]
        pack(fp, target, sides, [0, 90])
    return {"anchors": len(FIXED), "top": sum(s == "top" for s in placed.values()),
            "bottom": sum(s == "bottom" for s in placed.values())}
