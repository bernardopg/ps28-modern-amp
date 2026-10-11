#!/usr/bin/env python3
"""Write simple VRML body models for footprints KiCad 10.0.7 ships without a 3D model.

Envelopes only, from the cited datasheet outline drawings: visual review, NOT
manufacturer CAD. VRML unit = 2.54 mm (KiCad convention); origin = footprint origin.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "kicad/models/ps28-bodies"
U = 2.54

COLORS = {"black": (0.1, 0.1, 0.1), "metal": (0.75, 0.75, 0.78), "green": (0.1, 0.5, 0.2),
          "white": (0.92, 0.92, 0.88), "zinc": (0.6, 0.62, 0.65)}


def box(x, y, z, w, d, h, color):
    """Axis-aligned box: center x,y (mm, KiCad +y down), bottom z, size w x d x h."""
    r, g, b = COLORS[color]
    return (f"Transform {{ translation {x / U:.4f} {-y / U:.4f} {(z + h / 2) / U:.4f} children Shape {{ "
            f"appearance Appearance {{ material Material {{ diffuseColor {r} {g} {b} }} }} "
            f"geometry Box {{ size {w / U:.4f} {d / U:.4f} {h / U:.4f} }} }} }}")


def htssop44_top_ep():
    # TI SLASEA8A DDV0044D p.44: body 13.9-14.1 x 6.2, 1.2 mm max; pads at x = +/-3.7125,
    # y = +/-6.6675 (KiCad footprint), pitch 0.635; top PowerPAD 4.14 x 7.01 (footprint name).
    parts = [box(0, 0, 0.1, 6.1, 14.0, 1.0, "black"), box(0, 0, 1.1, 4.14, 7.01, 0.05, "metal")]
    for i in range(22):
        y = -6.6675 + i * 0.635
        for sx in (-1, 1):
            parts.append(box(sx * 3.55, y, 0, 1.2, 0.25, 0.25, "metal"))
    return parts


def jst_vh_b3p():
    # JST eVH header B3P-VH (top entry): A = 7.92, B = 11.82, depth 8.5, height 10.9.
    return [box(3.96, 0, 0, 11.82, 8.5, 10.9, "white")] + [
        box(3.96 * i, 0, 3, 1.1, 1.1, 7.9, "metal") for i in range(3)]


def wr_tbl_2p():
    # Wurth 691137710002 drawing p.1: L 10, depth 7.5, height 11.5, pitch 5.
    parts = [box(2.5, -0.25, 0, 10.0, 7.5, 11.5, "green")]
    for i in range(2):
        parts.append(box(5 * i, -0.25, 11.5, 3.0, 3.0, 0.3, "zinc"))  # screw head
    return parts


def m3_screw():
    # M3 pan-head screw head (ISO 7045 nominal dk 5.6, k 2.4) on the OEM L-bracket hole.
    return [box(0, 0, 0, 5.6, 5.6, 2.4, "zinc")]


MODELS = {"HTSSOP-44_TopEP_DDV.wrl": htssop44_top_ep, "JST_VH_B3P-VH.wrl": jst_vh_b3p,
          "WE_WR-TBL_691137710002.wrl": wr_tbl_2p, "M3_pan_head.wrl": m3_screw}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in MODELS.items():
        (OUT / name).write_text("#VRML V2.0 utf8\n" + "\n".join(fn()) + "\n")
    print(f"{len(MODELS)} envelope models in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
