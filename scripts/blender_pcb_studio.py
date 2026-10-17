"""Product renders of the real KiCad GLB plus the nominal OEM thermal parts.

make render-studio exports the board and runs this in a separate Blender process.
Board/component geometry comes only from the GLB. The OEM U profile, side shim,
load spreaders and M3 screws are added from mechanical/thermal-fit.json and the
same nominal profile used by scripts/blender_thermal_block.py (not an owner scan).
Materials follow datasheets where known (Nichicon UHE: white print on black sleeve).
Set PS28_STUDIO_PREVIEW=1 for a fast low-sample check, PS28_STUDIO_VIEWS=top,... for a subset.
"""
import contextlib
import hashlib
import io
import json
import math
import os
import shutil
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/studio"
MEDIA = ROOT / "docs/images/pcb-studio"
GLB = OUT / "board.glb"
FIT = json.loads((ROOT / "mechanical/thermal-fit.json").read_text())
PREVIEW = os.environ.get("PS28_STUDIO_PREVIEW") == "1"
OUT.mkdir(parents=True, exist_ok=True)
MEDIA.mkdir(parents=True, exist_ok=True)

MATS = {}


def mat(name, color, metal=0.0, rough=0.5, coat=0.0, aniso=0.0, bump=0.0):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    p = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metal
    p.inputs["Roughness"].default_value = rough
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Coat Roughness"].default_value = .06
    p.inputs["Anisotropic"].default_value = aniso
    if bump:
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 9000
        noise.inputs["Detail"].default_value = 4
        b = nodes.new("ShaderNodeBump")
        b.inputs["Strength"].default_value = bump
        b.inputs["Distance"].default_value = .00002
        links.new(noise.outputs["Fac"], b.inputs["Height"])
        links.new(b.outputs["Normal"], p.inputs["Normal"])
    MATS[name] = m
    return m


def library():
    return {
        "mask": mat("Solder mask green", (.008, .12, .045), rough=.3, coat=.55),
        "silk": mat("Silkscreen", (.93, .93, .9), rough=.7),
        "enig": mat("ENIG gold", (1.0, .77, .42), metal=1, rough=.18),
        "fr4": mat("FR4 edge", (.5, .45, .28), rough=.65),
        "blasted": mat("Al 6061 bead blasted", (.83, .84, .85), metal=1, rough=.42, bump=.25),
        "extrusion": mat("Al extrusion mill finish", (.78, .79, .8), metal=1, rough=.3, aniso=.6, bump=.12),
        "shim": mat("Al shim", (.7, .71, .72), metal=1, rough=.35),
        "steel": mat("Black oxide steel", (.05, .05, .055), metal=1, rough=.38),
        "zinc": mat("Zinc plated steel", (.72, .73, .74), metal=1, rough=.28),
        "sleeve": mat("Capacitor sleeve black PET", (.008, .008, .009), rough=.28, coat=.35),
        "print": mat("Capacitor print", (.42, .42, .41), rough=.5),
        "can": mat("Capacitor aluminium top", (.8, .81, .82), metal=1, rough=.25, aniso=.8),
        "rubber": mat("Capacitor rubber seal", (.03, .03, .03), rough=.7),
        "tin": mat("Tinned leads", (.8, .8, .78), metal=1, rough=.28),
        "gold": mat("Gold plating", (.95, .7, .32), metal=1, rough=.22),
        "epoxy": mat("Mold compound", (.018, .018, .019), rough=.55),
        "copper": mat("Enamelled copper", (.85, .42, .25), metal=1, rough=.25),
        "ferrite": mat("Ferrite", (.06, .062, .065), rough=.62),
    }


def classify(lib, obj):
    name = obj.data.name
    for key, role in (("soldermask", "mask"), ("silkscreen", "silk"), ("_pad", "enig"),
                      ("_PCB", "fr4"), ("thermal_block", "blasted")):
        if key in name:
            obj.data.materials.clear()
            obj.data.materials.append(lib[role])
            return
    is_cap, is_coil = name.startswith("CP_"), "HCF" in name
    for i, m in enumerate(obj.data.materials):
        if not m or not m.use_nodes:
            continue
        p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        r, g, b = p.inputs["Base Color"].default_value[:3]
        top, chroma = max(r, g, b), max(r, g, b) - min(r, g, b)
        if r > .35 and .1 < g < .25 and b < .2 and r > 2 * g:
            new = lib["copper"]
        elif is_coil and (top > .8 or top < .3):  # vendor "Marking" placeholder text goes body colour
            new = lib["ferrite"]
        elif is_cap and b > .3 and b > r * 2:
            new = lib["sleeve"]
        elif is_cap and chroma > .08 and top > .3:
            new = lib["print"]
        elif is_cap and chroma < .08 and top > .5:
            new = lib["can"]
        elif is_cap and top < .05:
            new = lib["rubber"]
        elif r > .6 and .4 < g < .6 and b < .3:
            new = lib["gold"]
        elif chroma < .078 and top >= .5:
            new = lib["tin"]
        elif top < .04:
            new = lib["epoxy"]
        else:
            new = mat(f"Plastic {r:.2f} {g:.2f} {b:.2f}", (r, g, b), rough=.45)
        obj.data.materials[i] = new


def trim_leads(meshes, bottom_z):
    """Cut catalog THT leads 2 mm below the board, as after assembly trimming."""
    cut = bottom_z - .002
    for obj in meshes:
        if min((obj.matrix_world @ Vector(p)).z for p in obj.bound_box) >= cut:
            continue
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        inv = obj.matrix_world.inverted()
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                                     plane_co=inv @ Vector((0, 0, cut)),
                                     plane_no=(inv.to_3x3() @ Vector((0, 0, -1))).normalized(),
                                     clear_outer=True)
        edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
        if edges:
            bmesh.ops.holes_fill(bm, edges=edges, sides=0)
        bm.to_mesh(obj.data)
        bm.free()


def kicad_frame(block):
    """Map KiCad mm (x right, y down, z up from component face) to Blender metres."""
    box = [block.matrix_world @ Vector(p) for p in block.bound_box]
    lo = Vector([min(p[i] for p in box) for i in range(3)])
    hi = Vector([max(p[i] for p in box) for i in range(3)])
    body = FIT["body_mm"]
    assert abs((hi.x - lo.x) * 1000 - (body["x"][1] - body["x"][0])) < .2, (lo, hi)
    x0, y0, z0 = body["x"][0], body["y"][0], body["z"][0]
    return lambda x, y, z: Vector((lo.x + (x - x0) / 1000, hi.y - (y - y0) / 1000, lo.z + (z - z0) / 1000))


def solid(name, verts, faces, material, bevel=.0004):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    if bevel:
        mod = obj.modifiers.new("edge break", "BEVEL")
        mod.width, mod.segments, mod.limit_method = bevel, 3, "ANGLE"
        mod.harden_normals = True
    obj.modifiers.new("weighted", "WEIGHTED_NORMAL").keep_sharp = True
    return obj


def box(name, k, a, b, material, bevel=.0004):
    (x0, y0, z0), (x1, y1, z1) = a, b
    v = [k(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return solid(name, v, f, material, bevel)


def prism_x(name, k, section, x0, x1, material):
    """Extrude a closed (y, z) KiCad section along X."""
    n = len(section)
    v = [k(x, y, z) for x in (x0, x1) for y, z in section]
    f = [tuple(range(n))[::-1], tuple(range(n, 2 * n))]
    f += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    obj = solid(name, v, f, material, .0006)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def socket_screw(name, k, x, y_face, z, lib):
    """M3 socket cap head (5.5 x 3 mm) with hex recess, axis along KiCad -Y."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=.00275, radius2=.00275, depth=.003)
    hexagon = bmesh.new()
    bmesh.ops.create_cone(hexagon, cap_ends=True, segments=6, radius1=.00144, radius2=.00144, depth=.0024)
    mesh, tool = bpy.data.meshes.new(name), bpy.data.meshes.new(name + " hex")
    bm.to_mesh(mesh)
    hexagon.to_mesh(tool)
    bm.free()
    hexagon.free()
    head = bpy.data.objects.new(name, mesh)
    cutter = bpy.data.objects.new(name + " hex", tool)
    for o in (head, cutter):
        bpy.context.scene.collection.objects.link(o)
        o.rotation_euler = (math.pi / 2, 0, 0)
    head.location = k(x, y_face - 1.5, z)
    cutter.location = k(x, y_face - 2.6, z)
    mod = head.modifiers.new("hex", "BOOLEAN")
    mod.object, mod.operation = cutter, "DIFFERENCE"
    bev = head.modifiers.new("chamfer", "BEVEL")
    bev.width, bev.segments, bev.limit_method = .0003, 2, "ANGLE"
    cutter.hide_render = cutter.hide_viewport = True
    head.data.materials.append(lib["steel"])
    for p in head.data.polygons:
        p.use_smooth = True
    return head


def oem_thermal_parts(k, lib):
    side = FIT["side_holes"]
    profile = [(68, 0), (101, 0), (101, 30), (95, 30), (95, 6), (74, 6), (74, 30), (68, 30)]
    prism_x("OEM U profile nominal 65x33x30", k, profile, 58, 123, lib["extrusion"])
    box("Side shim 0.9 nominal", k, (64, 67.05, 3.3), (117, 67.95, 30), lib["shim"], .0001)
    stops = FIT["stops"]
    for x, y in FIT["clamp_holes_xy_mm"]:
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=40, radius1=stops["outer_diameter_max_mm"] / 2000,
                              radius2=stops["outer_diameter_max_mm"] / 2000, depth=stops["nominal_mm"] / 1000)
        mesh = bpy.data.meshes.new(f"Stop {x}")
        bm.to_mesh(mesh)
        bm.free()
        stop = bpy.data.objects.new(f"Metal stop {x}", mesh)
        bpy.context.scene.collection.objects.link(stop)
        stop.location = k(x, y, stops["nominal_mm"] / 2)
        stop.data.materials.append(lib["zinc"])
        for p in mesh.polygons:
            p.use_smooth = len(p.vertices) == 4
    spread, below = side["external_load_spreader_mm"], side["spreader_hole_from_bottom_mm"]
    for x in side["x_mm"]:
        z0 = side["z_mm"] - below
        box(f"Load spreader {x}", k, (x - spread[0] / 2, 53, z0), (x + spread[0] / 2, 54, z0 + spread[1]),
            lib["zinc"], .00025)
        socket_screw(f"M3x20 side screw {x}", k, x, 53, side["z_mm"], lib)


def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "PS28 studio"
    with contextlib.redirect_stdout(io.StringIO()):
        bpy.ops.import_scene.gltf(filepath=str(GLB))
    meshes = [o for o in scene.objects if o.type == "MESH"]
    points = [o.matrix_world @ Vector(p) for o in meshes for p in o.bound_box]
    bounds = [(min(p[i] for p in points), max(p[i] for p in points)) for i in range(3)]
    assert abs(bounds[0][1] - bounds[0][0] - .154) < .0001, bounds
    assert abs(bounds[1][1] - bounds[1][0] - .081) < .0001, bounds
    block = next(o for o in meshes if "thermal_block" in o.data.name)
    assert any("HTSSOP" in o.data.name for o in meshes), "TPA package missing"
    lib = library()
    for obj in meshes:
        classify(lib, obj)
    # Imported WRL block carries smoothed normals that read as liquid chrome.
    with bpy.context.temp_override(object=block, active_object=block, selected_objects=[block]):
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
    for p in block.data.polygons:
        p.use_smooth = False
    k = kicad_frame(block)
    trim_leads([o for o in meshes if o is not block and "system-candidate" not in o.data.name],
               k(0, 0, -1.6).z)
    oem_thermal_parts(k, lib)
    count = len([o for o in scene.objects if o.type == "MESH" and not o.hide_render])
    scene["source_glb_sha256"] = hashlib.sha256(GLB.read_bytes()).hexdigest()
    scene["geometry_status"] = "KiCad GLB + nominal OEM profile/hardware; not physical fit approval"
    return scene, k, count


def studio(scene, k):
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24 if PREVIEW else 384
    scene.cycles.adaptive_threshold = .006
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 8
    scene.render.threads_mode = "FIXED"
    scene.render.threads = os.cpu_count() or 8
    scene.render.resolution_x, scene.render.resolution_y = 2400, 1500
    scene.render.resolution_percentage = 40 if PREVIEW else 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.view_transform = "AgX"
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass
    scene.world = bpy.data.worlds.new("Graphite studio")
    scene.world.use_nodes = True
    bg = next(n for n in scene.world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (.012, .013, .015, 1)
    bg.inputs["Strength"].default_value = 1
    # Cyclorama: floor curving into a back wall, graphite with soft sheen.
    floor_z = min((o.matrix_world @ Vector(p)).z for o in scene.objects if o.type == "MESH" for p in o.bound_box)
    centre = k(97, 60, 0)
    # Section (y, z): floor from behind the camera, quarter arc, wall behind the board.
    section = [(1.5, 0)] + [(-.6 - .35 * math.sin(a), .35 - .35 * math.cos(a))
                            for a in (i / 16 * math.pi / 2 for i in range(17))] + [(-.95, 1.5)]
    verts, faces = [], []
    for y, z in section:
        verts += [(centre.x - 1.5, centre.y + y, floor_z + z), (centre.x + 1.5, centre.y + y, floor_z + z)]
    for i in range(len(section) - 1):
        faces.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    cyc = solid("Cyclorama", verts, faces, mat("Graphite sweep", (.02, .021, .024), rough=.55), 0)
    for p in cyc.data.polygons:
        p.use_smooth = True
    cyc.modifiers.clear()
    lights = [
        ("Key softbox", (-.1, .14, .36), 2.2, (.34, .22)),
        ("Fill softbox", (.3, .26, .14), .3, (.3, .3)),
        ("Rim strip left", (-.26, -.18, .1), 1.0, (.04, .4)),
        ("Rim strip right", (.28, -.22, .12), .85, (.04, .4)),
        ("Underside softbox", (.1, .2, -.3), 1.4, (.3, .3)),
    ]
    for name, off, power, size in lights:
        data = bpy.data.lights.new(name, "AREA")
        data.shape, data.energy = "RECTANGLE", power
        data.size, data.size_y = size
        # Narrow softbox beams stop spill onto the back wall (hotspot behind the board).
        data.spread = math.radians(38 if "softbox" in name else 75)
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = centre + Vector(off)
        obj.rotation_euler = (centre - obj.location).to_track_quat("-Z", "Y").to_euler()
    cam_data = bpy.data.cameras.new("Product camera")
    cam = bpy.data.objects.new("Product camera", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam_data.lens, cam_data.clip_start, cam_data.clip_end = 85, .005, 20
    cam_data.sensor_width = 36
    # Rim strips only sculpt product edges; light linking keeps them off the sweep (no hotspot).
    sweep_only = bpy.data.collections.new("Sweep excluded from rims")
    sweep_only.objects.link(cyc)
    sweep_only.collection_objects[0].light_linking.link_state = "EXCLUDE"
    for name in ("Rim strip left", "Rim strip right"):
        scene.objects[name].light_linking.receiver_collection = sweep_only
    under = scene.objects["Underside softbox"]
    return cyc, under, centre


def frame(scene, target, offset, margin=.86, fit=None):
    cam = scene.camera
    cam.location = target + Vector(offset)
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    objs = fit or [o for o in scene.objects if o.type == "MESH" and o.name != "Cyclorama" and not o.hide_render]
    points = [o.matrix_world @ Vector(p) for o in objs for p in o.bound_box]
    aspect = scene.render.resolution_x / scene.render.resolution_y
    for _ in range(40):
        bpy.context.view_layer.update()
        proj = [world_to_camera_view(scene, cam, p) for p in points]
        span = max(max(abs(p.x - .5) * 2 for p in proj), max(abs(p.y - .5) * 2 for p in proj))
        if abs(span - margin) < .01 and min(p.z for p in proj) > 0:
            return
        cam.location = target + (cam.location - target) * (span / margin) ** .8
    raise ValueError(f"Camera framing did not converge: span {span:.3f}")


def render():
    scene, k, count = setup()
    cyc, under, centre = studio(scene, k)
    staging = OUT / "renders"
    staging.mkdir(exist_ok=True)
    detail = [o for o in scene.objects if o.type == "MESH" and any(
        s in o.name + o.data.name for s in ("thermal_block", "OEM U", "Load spreader", "M3x20", "Side shim"))]
    views = {
        "isometric": (k(97, 55, 6), (.2, .3, .22), .84, None, True),
        "top": (k(97, 60.5, 0), (0, .0001, .6), .9, None, True),
        "detail": (k(90, 62, 14), (-.1, .16, .085), .72, detail, True),
        "bottom": (k(97, 60.5, 0), (.12, .22, -.3), .86, None, False),
    }
    only = os.environ.get("PS28_STUDIO_VIEWS", "").split(",")  # e.g. "top" re-renders one view
    for name, (target, offset, margin, fit, floor) in views.items():
        if only != [""] and name not in only:
            continue
        cyc.hide_render, under.hide_render = not floor, floor
        scene.view_settings.exposure = -.8 if name == "top" else 0  # key light sits right above
        frame(scene, target, offset, margin, fit)
        scene.render.filepath = str(staging / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    cyc.hide_render, under.hide_render = False, True
    scene.view_settings.exposure = 0
    frame(scene, views["isometric"][0], views["isometric"][1], views["isometric"][2])
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "ps28-studio.blend"))
    if PREVIEW:
        return
    for name in views:
        if only != [""] and name not in only:
            continue
        shutil.copy2(staging / f"{name}.png", MEDIA / f"{name}.png")
    sources = [GLB, Path(__file__), ROOT / "kicad/system-candidate/system-candidate.kicad_pcb",
               ROOT / "mechanical/thermal-fit.json"]
    manifest = {"blender": bpy.app.version_string, "engine": scene.render.engine,
                "mesh_count": count, "samples": scene.cycles.samples,
                "manufacturing_approved": False,
                "limitations": ["Board and components from the KiCad GLB (catalog/proxy models)",
                                "OEM U profile, shim, spreaders and M3 heads are nominal geometry "
                                "from mechanical/thermal-fit.json, not an owner scan",
                                "Green mask and ENIG pads per D-039 fab spec; not a sign-off"],
                "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                "image_sha256": {f"{n}.png": hashlib.sha256((MEDIA / f"{n}.png").read_bytes()).hexdigest() for n in views}}
    (MEDIA / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    render()
