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
GAP = 0.5  # courtyard-to-courtyard spacing (0.6+ no longer fits the fixed power anchors)
EDGE = 0.75
HOLE_KEEP = 4.0  # M3 head / L-bracket clearance radius

# (x, y, rotation) footprint centers in mm, KiCad frame. Top side.
FIXED = {
    # D-031/D-032/D-033 placement review (PCB-001), by functional zone. KiCad frame: x 20..174
    # along the backplate, y 20 (free edge) .. 101 (backplate edge); profile U keepout
    # x 58..123, y 68..101; thermal block x 64..117, y 52..68 (low SMD only).
    # TPA3255 just beyond the profile outer leg, long axis along the leg (block contact).
    "U1": (90.5, 60.5, 90),
    # Output LC straight above the TPA output pin row (y 56.7): PWM loops ~10 mm long.
    "L1": (78.0, 40.75, 0), "L2": (103.0, 40.75, 180),
    "C22": (61.5, 28.0, 0), "C23": (61.5, 38.5, 0), "C26": (119.5, 28.0, 0), "C27": (119.5, 38.5, 0),
    # Woofer header at the OEM relay end, next to the L-bracket.
    "J5": (40.0, 94.0, 0),
    # OEM P101 harness to the preamp: centre of the free edge (oem-harness-sealing.md).
    "J7": (97.0, 24.0, 0),
    # PVDD/GVDD bulk on the left end of U1, relay and ground strap beside it.
    "C14": (56.0, 49.0, 0), "C15": (51.0, 62.0, 0), "C1": (27.5, 71.5, 0),
    "K501": (38.0, 60.0, 0), "J6": (121.0, 60.0, 0),
    # Left (relay end): analog rail, film coupling cap.
    "C201": (30.0, 28.0, 0), "C202": (42.0, 28.0, 0), "C603": (30.0, 41.0, 0), "C109": (42.0, 41.0, 0),
    "D201": (48.0, 81.0, 0), "R201": (30.0, 82.0, 0), "C203": (52.0, 90.0, 0),
    # Right (transformer end): bulk stack, rectifier column, buck inductor, CT fuse, T1 header.
    "C301": (140.5, 36.5, 0), "C302": (140.5, 68.5, 0),
    "D301": (165.0, 30.0, 90), "D302": (165.0, 61.0, 90), "L301": (166.0, 77.0, 0),
    "F301": (137.0, 93.0, 0), "J301": (158.0, 95.5, 0),
    # PCB-004 fan header and mode jumper by the T1 end (fan would sit near the profile).
    "J8": (170.0, 22.5, 90), "JP701": (148.0, 24.0, 90),
}
# D-031 thermal block: aluminium bar on the U1 PowerPAD, screwed into the two tapped M3
# TO-3P holes of the profile leg (x 70.7 / 110.3), relieved 3 mm above the board except
# on the pad. Only low SMD parts (R/C/D/U, < 2.5 mm) may sit under it on top.
BLOCK = (64.0, 53.5, 117.0, 68.0)  # block body y 54..67 + 0.5 mm
LOW_UNDER_BLOCK = ("R", "C", "D", "U")
# Packing targets per group: (top x, top y), preferred side.
# Routing room (D-034): logic groups kept away from U1 so its fanout and the PWM/INPUT
# pins have channels; only the core group (U1 decoupling/bootstrap) packs next to it.
TARGETS = {None: ((90.5, 55.0), "top"), "power": ((150.0, 55.0), "top"),
           "seq": ((140.0, 85.0), "bottom"), "iso": ((45.0, 75.0), "bottom"),
           "analog": ((40.0, 50.0), "bottom"), "pre": ((60.0, 30.0), "bottom"),
           "dbg": ((140.0, 60.0), "top")}
U1_RING = (80.0, 52.0, 101.0, 69.0)  # U1 courtyard + ~3 mm: core group only, both sides  # probes/LEDs on the component side when room
# LM5164 buck loop stays under its inductor L301 (switch node/input caps short).
BUCK = ((160.0, 77.0), "bottom")


def place(pcb, pcbnew, mech, parts):
    groups = {p["ref"]: p.get("group") for p in parts}
    # Buck parts: U302, anything on a BUCK_ net, and its 1210 input/output caps.
    buck = {p["ref"] for p in parts if p["ref"] == "U302" or any(
        str(n).startswith("BUCK_") for n in p["nets"].values()) or (
        p.get("group") == "power" and "C_1210" in p.get("footprint", ""))}
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
        for hx, hy in mech.get("block_holes", []):  # M3 clamp head (bottom) / block (top)
            occ[side] |= (cx - hx) ** 2 + (cy - hy) ** 2 < 3.0 ** 2
    kx0, ky0, kx1, ky1 = mech["profile_keepout"]
    occ["top"] |= (cx >= kx0) & (cx <= kx1) & (cy >= ky0) & (cy <= ky1)
    bx0, by0, bx1, by1 = BLOCK
    block = (cx >= bx0) & (cx <= bx1) & (cy >= by0) & (cy <= by1)
    rx0, ry0, rx1, ry1 = U1_RING
    ring = (cx >= rx0) & (cx <= rx1) & (cy >= ry0) & (cy <= ry1)

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

    def fits(side, w, h, target, tall=False, tht=False, core=True):
        grid = occ[side] | block if tall and side == "top" else occ[side]
        if not core:
            grid = grid | ring
        if tht:  # through-hole leads also need the other side free
            grid = grid | occ["bottom" if side == "top" else "top"]
        sat = np.pad(grid.astype(np.int32).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
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
        smd = all(p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD for p in fp.Pads())
        tall = ref not in ("U1", "J6") and not (smd and ref.startswith(LOW_UNDER_BLOCK))
        for side in sides:
            options = []
            for rot in rotations:
                put(fp, 0, 0, rot, side)
                l, t, r, b = box(fp)
                pos = fits(side, r - l, b - t, target, tall, not smd, groups.get(ref) is None)
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
            pack(fps[ref], (x, y), ["top"], [rot, (rot + 90) % 360])
    rest = [fp for ref, fp in fps.items() if ref not in FIXED]

    def area(fp):
        put(fp, 0, 0, 0, "top")
        l, t, r, b = box(fp)
        return (r - l) * (b - t)
    for fp in sorted(rest, key=lambda fp: -area(fp)):
        smd = all(p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD for p in fp.Pads())
        target, prefer = BUCK if fp.GetReference() in buck else TARGETS[groups.get(fp.GetReference())]
        sides = [prefer, "bottom" if prefer == "top" else "top"] if smd else ["top"]
        pack(fp, target, sides, [0, 90])
    return {"anchors": len(FIXED), "top": sum(s == "top" for s in placed.values()),
            "bottom": sum(s == "bottom" for s in placed.values())}
