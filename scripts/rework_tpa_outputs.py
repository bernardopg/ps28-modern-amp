#!/usr/bin/env python3
"""PCB-002: hand layout of the TPA3255 PBTL output copper (D-035).

Pins (top row, y 56.66): OUT_A 39/40 and OUT_C 32 = PWM_AC; OUT_B 35 and OUT_D 27/28 =
PWM_BD, interleaved with the locked PVDD/GND fanout vias. Layout:
  * 0.25 mm escapes straight out of each PWM pin between the fanout vias;
  * PWM_AC: 1.0 mm F.Cu bus north of the via rows joining 39/40 and 32, then to L1.1;
  * PWM_BD: escapes drop to B.Cu, 0.6 mm bus joining 35 and 27/28, then to L2.2;
  * unlocked small-signal copper in that strip is ripped up and re-laid afterwards by
    close_open_connections.py.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from close_open_connections import BOARD, drc, router  # noqa: E402

STRIP = (81.0, 49.5, 100.5, 56.3)  # x0, y0, x1, y1 mm: north of the U1 output row
AC_BUS_Y, BD_VIA_Y, ESC_W = 52.4, 53.5, 0.25
C8_UNDER_BODY = (91.5, 60.4, 90)  # C_START cap moved off the output strip, B.Cu under U1
GRAVEYARD = []  # removed BOARD_ITEMs stay referenced: SWIG must not free them twice


def main():
    import pcbnew

    mm, MM = pcbnew.ToMM, pcbnew.FromMM
    pcb = pcbnew.LoadBoard(str(BOARD))
    x0, y0, x1, y1 = STRIP
    # Read pin coordinates before ripping copper (SWIG pad proxies go stale after Remove()).
    pins = {p.GetNumber(): (mm(p.GetPosition().x), mm(p.GetPosition().y))
            for p in pcb.FindFootprintByReference("U1").Pads()}

    def inside(p):
        return x0 <= mm(p.x) <= x1 and y0 <= mm(p.y) <= y1

    columns = [x for x, y in pins.values()]

    def fanout(t):
        """Locked U1 power fanout: stub + via straight above a pin."""
        pts = [t.GetPosition()] if t.GetClass() == "PCB_VIA" else [t.GetStart(), t.GetEnd()]
        return t.IsLocked() and all(min(abs(mm(p.x) - c) for c in columns) < 0.05 for p in pts)

    c8 = pcb.FindFootprintByReference("C8")
    old_c8 = c8.GetBoundingBox()
    old_c8.Inflate(MM(1.5))
    new_c8 = pcbnew.BOX2I(pcbnew.VECTOR2I(MM(C8_UNDER_BODY[0] - 1.6), MM(C8_UNDER_BODY[1] - 1.6)),
                          pcbnew.VECTOR2L(MM(3.2), MM(3.2)))
    ripped = 0
    for t in list(pcb.GetTracks()):
        net = t.GetNetname()
        if fanout(t) and net in ("/GND", "/PVDD"):
            continue
        pts = [t.GetPosition()] if t.GetClass() == "PCB_VIA" else [t.GetStart(), t.GetEnd()]
        if (net in ("/PWM_AC", "/PWM_BD") or any(inside(p) or old_c8.Contains(p) for p in pts)
                or t.HitTest(new_c8, False, 0)):
            pcb.Remove(t)
            GRAVEYARD.append(t)
            ripped += 1

    def track(a, b, w, layer, net):
        t = pcbnew.PCB_TRACK(pcb)
        t.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
        t.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
        t.SetWidth(MM(w))
        t.SetLayer(layer)
        t.SetNet(net)
        t.SetLocked(True)
        pcb.Add(t)
        return t

    def via(x, y, net):
        v = pcbnew.PCB_VIA(pcb)
        v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        v.SetWidth(MM(0.6))
        v.SetDrill(MM(0.3))
        v.SetNet(net)
        v.SetLocked(True)
        pcb.Add(v)
        return v

    if not c8.IsFlipped():
        c8.Flip(c8.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    c8.SetOrientationDegrees(C8_UNDER_BODY[2])
    c8.SetPosition(pcbnew.VECTOR2I(MM(C8_UNDER_BODY[0]), MM(C8_UNDER_BODY[1])))

    def x(n):
        return pins[n][0]

    row = pins["32"][1]
    ac, bd = pcb.FindNet("/PWM_AC"), pcb.FindNet("/PWM_BD")
    for n in ("39", "32"):
        track((x(n), row), (x(n), AC_BUS_Y), ESC_W, pcbnew.F_Cu, ac)
    ac_bus = track((x("39"), AC_BUS_Y), (x("32"), AC_BUS_Y), 1.0, pcbnew.F_Cu, ac)
    for n in ("35", "28"):
        track((x(n), row), (x(n), BD_VIA_Y), ESC_W, pcbnew.F_Cu, bd)
        via(x(n), BD_VIA_Y, bd)
    bd_bus = track((x("35"), BD_VIA_Y), (x("28"), BD_VIA_Y), 0.6, pcbnew.B_Cu, bd)
    print(f"ripped {ripped}; escapes/buses placed")

    report = drc(pcb, pcbnew, "rework-0")
    bad = [v for v in report["violations"] if v["severity"] == "error"]
    if bad:
        raise SystemExit(f"hand geometry violates DRC: {[(v['type'], v['description'][:60]) for v in bad[:5]]}")

    route, commit, _ = router(pcb, pcbnew)
    for bus, ref, number in ((ac_bus, "L1", "1"), (bd_bus, "L2", "2")):
        target = next(p for p in pcb.FindFootprintByReference(ref).Pads() if p.GetNumber() == number)
        for width in (1.5, 1.0, 0.8, 0.6, 0.4):
            path = route(bus.GetNetCode(), bus, target, width)
            if path:
                commit(path, bus.GetNet(), width)
                print(f"{bus.GetNetname()} -> {ref}.{number}: {width} mm")
                route, commit, _ = router(pcb, pcbnew)
                break
        else:
            print(f"{bus.GetNetname()} -> {ref}.{number}: NO PATH")
    pcbnew.ZONE_FILLER(pcb).Fill(pcb.Zones())
    pcbnew.SaveBoard(str(BOARD), pcb)


if __name__ == "__main__":
    main()
