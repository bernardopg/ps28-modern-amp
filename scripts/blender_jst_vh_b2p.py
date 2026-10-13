"""JST B2P-VH header body for KiCad, modelled in Blender and written as VRML 2.0.

Run: blender --background --factory-startup --python scripts/blender_jst_vh_b2p.py
KiCad 10 reads only VRML/STEP/IGES and Blender 5 exports neither, so the mesh built
here is written as VRML IndexedFaceSet directly. Dimensions: JST VH catalogue p.65-66
(B2P-VH: A 3.96, B 7.86, depth 8.5 incl. lock, height 10.9 as in make_body_models.py)
and the KiCad footprint Fab outline (body x -1.95..5.91, y -2.0..4.8, lock y -3.7).
Visual envelope, not manufacturer CAD. Origin = pin 1, KiCad +y down, VRML unit 2.54 mm.
"""

from pathlib import Path

import bmesh
import bpy

OUT = Path(__file__).resolve().parents[1] / "kicad/models/ps28-bodies/JST_VH_B2P-VH.wrl"
U = 2.54
WHITE, METAL = (0.92, 0.92, 0.88), (0.75, 0.75, 0.78)


def cube(name, x0, y0, z0, x1, y1, z1):
    """Box between two corners in KiCad mm (y down)."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, -(y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.object
    o.name = name
    o.scale = (x1 - x0, y1 - y0, z1 - z0)
    bpy.ops.object.transform_apply(scale=True)
    return o


def cut(target, tool):
    mod = target.modifiers.new("cut", "BOOLEAN")
    mod.operation, mod.object = "DIFFERENCE", tool
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(tool)


bpy.ops.wm.read_factory_settings(use_empty=True)
H = 10.9
body = cube("body", -1.95, -2.0, 0.0, 5.91, 4.8, H)
cut(body, cube("cavity", -1.15, -1.2, 3.0, 5.11, 4.0, H + 1))      # 0.8 mm shroud walls
cut(body, cube("polarizer", 0.4, 3.9, 6.0, 3.56, 4.9, H + 1))      # key slot on the back wall
lock = cube("lock", -0.75, -3.7, 6.5, 4.71, -2.0, 9.0)             # housing latch ramp
pins = [cube(f"pin{i}", 3.96 * i - 0.55, -0.55, -3.4, 3.96 * i + 0.55, 0.55, H - 1.0) for i in range(2)]


def vrml(obj, color):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    pts = " ".join(f"{v.co.x / U:.4f} {v.co.y / U:.4f} {v.co.z / U:.4f}," for v in bm.verts)
    idx = " ".join(" ".join(str(v.index) for v in f.verts) + " -1," for f in bm.faces)
    bm.free()
    r, g, b = color
    return (f"Shape {{ appearance Appearance {{ material Material {{ diffuseColor {r} {g} {b} }} }} "
            f"geometry IndexedFaceSet {{ coord Coordinate {{ point [ {pts} ] }} coordIndex [ {idx} ] }} }}")


shapes = [vrml(body, WHITE), vrml(lock, WHITE)] + [vrml(p, METAL) for p in pins]
OUT.write_text("#VRML V2.0 utf8\n" + "\n".join(shapes) + "\n")
print("wrote", OUT, sum(len(o.data.polygons) for o in [body, lock, *pins]), "faces")
