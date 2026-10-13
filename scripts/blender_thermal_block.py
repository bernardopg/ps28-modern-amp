"""D-031 TPA3255 thermal block: STL (machining/print reference), VRML (KiCad 3D on H5) and PNG.

Run: blender --background --factory-startup --python scripts/blender_thermal_block.py
Frame = PCB frame in mm: x along the board, y towards the profile leg (leg face y = 68),
z up from the PCB top surface. Dimensions are documented in mechanical/thermal-block.md.
"""

import math
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[1]
U = 2.54
H5 = (79.0, 60.5)  # VRML origin = clamp hole H5 footprint origin

# Body, pedestal on the PowerPAD, clamp holes from below, side slots to the leg.
X0, X1, Y0, Y1, Z0, Z1 = 64.0, 117.0, 54.0, 67.0, 3.0, 13.0
PED = (86.5, 94.5, 57.9, 63.1, 1.25)            # x0, x1, y0, y1, z bottom (DDV max 1.2)
CLAMP = [(79.0, 60.5), (102.0, 60.5)]            # M3 tapped from below, depth 8
SIDE = [(70.7, 6.35), (110.3, 6.35)]             # x, z of the TO-3P M3 holes in the leg


def box(name, x0, y0, z0, x1, y1, z1):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.object
    o.name, o.scale = name, (x1 - x0, y1 - y0, z1 - z0)
    bpy.ops.object.transform_apply(scale=True)
    return o


def cyl(r, depth, loc, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=32)
    return bpy.context.object


def boolean(target, tool, op):
    m = target.modifiers.new("b", "BOOLEAN")
    m.operation, m.object = op, tool
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(tool)


bpy.ops.wm.read_factory_settings(use_empty=True)
block = box("block", X0, Y0, Z0, X1, Y1, Z1)
boolean(block, box("ped", PED[0], PED[2], PED[4], PED[1], PED[3], Z0 + 0.01), "UNION")
for x, y in CLAMP:  # 2.5 mm tap drill for M3, 8 mm deep from the underside
    boolean(block, cyl(1.25, 8.0, (x, y, Z0 + 4.0)), "DIFFERENCE")
for x, z in SIDE:   # 3.4 mm wide slot, +/-1.5 mm in z, through y; 6.5 mm counterbore 3 mm deep
    for dz in (-1.5, 0, 1.5):
        boolean(block, cyl(1.7, 20, (x, (Y0 + Y1) / 2, z + dz), (math.pi / 2, 0, 0)), "DIFFERENCE")
    boolean(block, box("slot", x - 1.7, Y0 - 1, z - 1.5, x + 1.7, Y1 + 1, z + 1.5), "DIFFERENCE")
    boolean(block, cyl(3.25, 6.0, (x, Y0, z), (math.pi / 2, 0, 0)), "DIFFERENCE")

(ROOT / "mechanical").mkdir(exist_ok=True)
bpy.ops.object.select_all(action="DESELECT")
block.select_set(True)
bpy.ops.wm.stl_export(filepath=str(ROOT / "mechanical/thermal-block.stl"), export_selected_objects=True)

bm = bmesh.new()
bm.from_mesh(block.data)
bmesh.ops.triangulate(bm, faces=bm.faces)
# KiCad VRML: y up = -PCB y, origin at H5, units of 2.54 mm.
pts = " ".join(f"{(v.co.x - H5[0]) / U:.4f} {-(v.co.y - H5[1]) / U:.4f} {v.co.z / U:.4f}," for v in bm.verts)
idx = " ".join(" ".join(str(v.index) for v in f.verts) + " -1," for f in bm.faces)
faces = len(bm.faces)
bm.free()
(ROOT / "kicad/models/ps28-bodies/thermal_block.wrl").write_text(
    "#VRML V2.0 utf8\nShape { appearance Appearance { material Material { diffuseColor 0.78 0.8 0.82 } } "
    f"geometry IndexedFaceSet {{ coord Coordinate {{ point [ {pts} ] }} coordIndex [ {idx} ] }} }}\n")

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x, scene.render.resolution_y = 1400, 800
scene.display.shading.light = "STUDIO"
scene.display.shading.show_cavity = True
bpy.ops.object.camera_add()
cam = bpy.context.object
scene.camera = cam
cam.data.type, cam.data.ortho_scale = "ORTHO", 70
scene.world = bpy.data.worlds.new("w")
scene.display.shading.background_type = "VIEWPORT"
for name, loc, rot in (("thermal-block.png", (130, 10, 60), (55, 0, 45)),
                       ("thermal-block-bottom.png", (130, 10, -55), (125, 0, 45))):
    cam.location, cam.rotation_euler = loc, tuple(math.radians(a) for a in rot)
    scene.render.filepath = str(ROOT / "docs/images" / name)
    bpy.ops.render.render(write_still=True)
print("thermal block:", faces, "triangles")
