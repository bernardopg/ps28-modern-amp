"""S-expression helpers and the measured OEM frame of the product board.

Extracted from the retired generators (create_core_draft, create_analog_capture,
integrate_candidate) so checks keep working without the historical revisions.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse(text):
    tokens = iter(re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text))

    def body():
        result = []
        for token in tokens:
            if token == "(":
                result.append(body())
            elif token == ")":
                return result
            else:
                result.append(token)
        raise ValueError("unbalanced S-expression")

    if next(tokens) != "(":
        raise ValueError("expected S-expression")
    return body()


def render(node):
    return "(" + " ".join(render(x) if isinstance(x, list) else x for x in node) + ")"


def walk(node):
    yield node
    for child in node:
        if isinstance(child, list):
            yield from walk(child)


def child(node, tag):
    return next((x for x in node if isinstance(x, list) and x[0] == tag), None)


def oem_mechanics():
    """Measured OEM main-PCB frame (MECH-001, owner tape measurements, ~1 mm error).

    KiCad frame: origin (20, 20); x along the backplate from the UPPER board edge
    (OEM relay/woofer end) to the lower edge (transformer end); y from the free edge
    to the backplate edge. Orientation confirmed by the owner (2026-10-10).
    """
    m = json.loads((ROOT / "mechanical/oem-heatsink-measurements.json").read_text())
    pcb, u = m["main_pcb"], m["u_profile"]
    x0, y0 = 20.0, 20.0
    w, h = pcb["length_mm"], pcb["depth_mm"]
    back = y0 + h  # backplate edge
    edge = pcb["mounting_holes"]["from_edge_mm"]
    holes = [(x, back - d) for x in (x0 + edge, x0 + w - edge)
             for d in pcb["mounting_holes"]["from_backplate_mm"]]
    top_gap = pcb["profile_gaps_mm"]["top"]
    keepout = (x0 + top_gap, back - u["outer_width"], x0 + top_gap + u["length"], back)
    to3p = [(x0 + top_gap + d, back - u["outer_width"]) for d in
            (u["to3p_holes"]["from_profile_ends_mm"], u["length"] - u["to3p_holes"]["from_profile_ends_mm"])]
    # D-031: two plated M3 holes at the pinless ends of U1 (90.5, 60.5) clamp the thermal
    # block onto the PowerPAD from below, as on the TI EVM; block is GND (SLASEA8A pin table).
    block_holes = [(79.0, 60.5), (102.0, 60.5)]
    return {"outline": (x0, y0, x0 + w, back), "holes": holes, "profile_keepout": keepout,
            "to3p_holes_at_leg_face": to3p, "hole_thread": pcb["mounting_holes"]["thread"],
            "block_holes": block_holes}
