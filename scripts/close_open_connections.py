#!/usr/bin/env python3
"""Close the connections left open by Freerouting (PCB-002): grid A* over F.Cu/In2/B.Cu.

Obstacles = every copper item of another net, inflated by clearance + half track width,
rasterised with PIL from KiCad's own polygons. In1 (solid GND plane) is never routed;
fills (GND F/B, PVDD In2) are passable because the refill clears around new copper,
but In2 inside the PVDD plane costs more so the plane stays whole. Every connection is
DRC-checked after insertion and rolled back if it adds a violation.
Usage: python3 scripts/close_open_connections.py [drc.json]
"""

import heapq
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "kicad/system-candidate/system-candidate.kicad_pcb"
WORK = ROOT / "build/route"
G = 0.1          # grid mm
CLEAR = 0.2      # copper clearance mm
EDGE = 0.5       # copper to board edge
VIA_D, VIA_DRILL = 0.6, 0.3
WIDTH = {"/PWM_AC": 0.25, "/PWM_BD": 0.25}  # pin escape; PWM pours carry the current
DEFAULT_W = 0.2
GRAVEYARD = []  # removed BOARD_ITEMs stay referenced: SWIG must not free them twice


def drc(pcb, pcbnew, name):
    pcbnew.ZONE_FILLER(pcb).Fill(pcb.Zones())
    tmp, out = WORK / f"{name}.kicad_pcb", WORK / f"{name}.json"
    pcbnew.SaveBoard(str(tmp), pcb)
    subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "--schematic-parity", "--severity-all",
                    "-o", str(out), str(tmp)], capture_output=True, check=False)
    return json.loads(out.read_text())


def router(pcb, pcbnew):
    bb = pcb.GetBoardEdgesBoundingBox()
    x0, y0 = pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop())
    nx, ny = int(pcbnew.ToMM(bb.GetWidth()) / G) + 1, int(pcbnew.ToMM(bb.GetHeight()) / G) + 1
    layers = [pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]

    def to_px(v):
        return ((pcbnew.ToMM(v.x) - x0) / G, (pcbnew.ToMM(v.y) - y0) / G)

    copper = []
    for fp in pcb.GetFootprints():
        for pad in fp.Pads():
            for layer in layers:
                if pad.IsOnLayer(layer):
                    copper.append((pad, layer))
    for t in pcb.GetTracks():
        for layer in layers:
            if t.IsOnLayer(layer):
                copper.append((t, layer))
    holes = [p for fp in pcb.GetFootprints() for p in fp.Pads() if p.GetDrillSize().x > 0] + \
            [t for t in pcb.GetTracks() if t.GetClass() == "PCB_VIA"]
    pvdd = next((z for z in pcb.Zones() if z.GetZoneName() == "PVDD_PLANE"), None)
    edge = np.zeros((ny, nx), bool)
    m = int(np.ceil(EDGE / G)) + 1
    edge[:m, :] = edge[-m:, :] = True
    edge[:, :m] = edge[:, -m:] = True

    def blocked(net, width):
        """Per-layer boolean masks of cells a track of `width` on `net` may not enter."""
        masks = []
        by_layer = {l: Image.new("1", (nx, ny), 0) for l in layers}
        for item, layer in copper:
            if item.GetNetCode() == net:
                continue
            poly = pcbnew.SHAPE_POLY_SET()
            item.TransformShapeToPolygon(poly, layer, pcbnew.FromMM(CLEAR + width / 2), pcbnew.FromMM(0.02),
                                         pcbnew.ERROR_OUTSIDE)
            draw = ImageDraw.Draw(by_layer[layer])
            for i in range(poly.OutlineCount()):
                o = poly.Outline(i)
                draw.polygon([to_px(o.CPoint(k)) for k in range(o.PointCount())], fill=1)
        for layer in layers:
            masks.append(np.array(by_layer[layer], bool) | edge)
        return masks

    def via_blocked(net):
        img = Image.new("1", (nx, ny), 0)
        draw = ImageDraw.Draw(img)
        r = VIA_D / 2 + CLEAR
        for item, layer in copper:
            if item.GetNetCode() == net:
                continue
            poly = pcbnew.SHAPE_POLY_SET()
            item.TransformShapeToPolygon(poly, layer, pcbnew.FromMM(r), pcbnew.FromMM(0.02), pcbnew.ERROR_OUTSIDE)
            for i in range(poly.OutlineCount()):
                o = poly.Outline(i)
                draw.polygon([to_px(o.CPoint(k)) for k in range(o.PointCount())], fill=1)
        for h in holes:  # hole-to-hole 0.25 mm
            c = to_px(h.GetPosition())
            rr = (pcbnew.ToMM(h.GetDrillSize().x if h.GetClass() == "PAD" else h.GetDrill()) / 2
                  + VIA_DRILL / 2 + 0.25) / G
            draw.ellipse([c[0] - rr, c[1] - rr, c[0] + rr, c[1] + rr], fill=1)
        mask = np.array(img, bool) | edge
        m2 = int(np.ceil((EDGE + VIA_D / 2) / G))
        mask[:m2, :] = mask[-m2:, :] = True
        mask[:, :m2] = mask[:, -m2:] = True
        return mask

    pvdd_mask = np.zeros((ny, nx), bool)
    if pvdd:
        img = Image.new("1", (nx, ny), 0)
        o = pvdd.Outline().Outline(0)
        ImageDraw.Draw(img).polygon([to_px(o.CPoint(k)) for k in range(o.PointCount())], fill=1)
        pvdd_mask = np.array(img, bool)

    def own(item):
        """Cells covered by the item's own copper, per routed layer (start/goal sets)."""
        cells = set()
        for li, layer in enumerate(layers):
            if not item.IsOnLayer(layer):
                continue
            img = Image.new("1", (nx, ny), 0)
            poly = pcbnew.SHAPE_POLY_SET()
            item.TransformShapeToPolygon(poly, layer, 0, pcbnew.FromMM(0.02), pcbnew.ERROR_INSIDE)
            for i in range(poly.OutlineCount()):
                o = poly.Outline(i)
                ImageDraw.Draw(img).polygon([to_px(o.CPoint(k)) for k in range(o.PointCount())], fill=1)
            ys, xs = np.nonzero(np.array(img, bool))
            cells |= {(li, int(x), int(y)) for x, y in zip(xs, ys)}
        return cells

    def route(net, ia, ib, width, masks=None):
        masks = masks or blocked(net, width)
        vmask = via_blocked(net)
        starts, goals = own(ia), own(ib)
        if not starts or not goals:
            return None
        for li, x, y in starts | goals:
            masks[li][y, x] = False
        bx = sum(g[1] for g in goals) / len(goals)
        by = sum(g[2] for g in goals) / len(goals)
        dirs = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
                (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
        layer_cost = [1.0, 1.6, 1.2]
        open_ = [(0.0, 0.0, s_, None) for s_ in starts]
        best, prev = {s_: 0.0 for s_ in starts}, {}
        h = lambda x, y: np.hypot(x - bx, y - by)
        while open_:
            f, g, (li, x, y), d = heapq.heappop(open_)
            if (li, x, y) in goals:
                path, node = [], (li, x, y)
                while node in prev:
                    path.append(node)
                    node = prev[node]
                path.append(node)
                return path[::-1]
            if g > best.get((li, x, y), 1e18):
                continue
            moves = []
            for dx, dy, c in dirs:
                X, Y = x + dx, y + dy
                if 0 <= X < nx and 0 <= Y < ny and not masks[li][Y, X]:
                    extra = 0.4 if d is not None and d != (dx, dy) else 0.0  # fewer bends
                    if layers[li] == pcbnew.In2_Cu and pvdd_mask[Y, X]:
                        extra += 3.0  # keep the PVDD plane whole
                    moves.append(((li, X, Y), c * layer_cost[li] + extra, (dx, dy)))
            if not vmask[y, x]:
                for lj in range(len(layers)):
                    if lj != li and not masks[lj][y, x]:
                        moves.append(((lj, x, y), 25.0, None))
            for node, c, nd in moves:
                ng = g + c
                if ng < best.get(node, 1e18):
                    best[node], prev[node] = ng, (li, x, y)
                    heapq.heappush(open_, (ng + h(node[1], node[2]), ng, node, nd))
        return None

    def commit(path, net_item, width):
        added = []

        def pt(x, y):
            return pcbnew.VECTOR2I(pcbnew.FromMM(x0 + x * G), pcbnew.FromMM(y0 + y * G))
        i = 0
        while i < len(path) - 1:
            li, x, y = path[i]
            if path[i + 1][0] != li:  # via
                v = pcbnew.PCB_VIA(pcb)
                v.SetPosition(pt(x, y))
                v.SetWidth(pcbnew.FromMM(VIA_D))
                v.SetDrill(pcbnew.FromMM(VIA_DRILL))
                v.SetNet(net_item)
                pcb.Add(v)
                added.append(v)
                i += 1
                continue
            j = i + 1
            d = (path[j][1] - x, path[j][2] - y)
            while j + 1 < len(path) and path[j + 1][0] == li and \
                    (path[j + 1][1] - path[j][1], path[j + 1][2] - path[j][2]) == d:
                j += 1
            t = pcbnew.PCB_TRACK(pcb)
            t.SetStart(pt(x, y))
            t.SetEnd(pt(path[j][1], path[j][2]))
            t.SetWidth(pcbnew.FromMM(width))
            t.SetLayer(layers[li])
            t.SetNet(net_item)
            pcb.Add(t)
            added.append(t)
            i = j
        return added

    return route, commit, layers


def endpoint(pcb, pcbnew, item):
    """(position, layers) of an unconnected-item end from the DRC JSON."""
    pos = pcbnew.VECTOR2I(pcbnew.FromMM(item["pos"]["x"]), pcbnew.FromMM(item["pos"]["y"]))
    target = item["uuid"]
    for fp in pcb.GetFootprints():
        for pad in fp.Pads():
            if pad.m_Uuid.AsString() == target:
                return pad.GetPosition(), [l for l in (pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.B_Cu) if pad.IsOnLayer(l)], pad
    for t in pcb.GetTracks():
        if t.m_Uuid.AsString() == target:
            if t.GetClass() == "PCB_VIA":
                return t.GetPosition(), [pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.B_Cu], t
            near = min((t.GetStart(), t.GetEnd()), key=lambda p: (p - pos).EuclideanNorm())
            return near, [t.GetLayer()], t
    raise KeyError(target)


def errors(report):
    """Error violations by (type, items); dangling stubs are cleanup, not a regression."""
    return {(v["type"], tuple(sorted(i.get("uuid", "") for i in v["items"])))
            for v in report["violations"]
            if v["severity"] == "error" and v["type"] not in ("track_dangling", "via_dangling")}


def main():
    import pcbnew

    WORK.mkdir(parents=True, exist_ok=True)
    pcb = pcbnew.LoadBoard(str(BOARD))
    report = drc(pcb, pcbnew, "close-0")
    route, commit, _ = router(pcb, pcbnew)
    closed, failed = [], []
    for n, u in enumerate(report["unconnected_items"]):
        (pa, la, ia), (pb, lb, ib) = (endpoint(pcb, pcbnew, i) for i in u["items"])
        net = ia.GetNetCode()
        name = ia.GetNetname()
        width = WIDTH.get(name, DEFAULT_W)
        path = route(net, ia, ib, width)
        if not path:
            failed.append((name, "no path"))
            continue
        added = commit(path, ia.GetNet(), width)
        check = drc(pcb, pcbnew, f"close-{n + 1}")
        new_errors = errors(check) - errors(report)
        if new_errors or len(check["unconnected_items"]) >= len(report["unconnected_items"]):
            for item in added:
                pcb.Remove(item)
                GRAVEYARD.append(item)
            failed.append((name, sorted({t for t, _ in new_errors})[:4] or "no gain"))
            continue
        report = check
        closed.append(name)
        route, commit, _ = router(pcb, pcbnew)  # new copper becomes an obstacle
    pcbnew.ZONE_FILLER(pcb).Fill(pcb.Zones())
    pcbnew.SaveBoard(str(BOARD), pcb)
    print("closed", closed)
    print("failed", failed)


if __name__ == "__main__":
    main()
