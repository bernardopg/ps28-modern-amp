"""Render the actual KiCad GLB; no invented component geometry or PCB edits.

make render-studio exports the board and runs this in a separate Blender process.
It can also be executed through Blender MCP with __file__ set to this path.
"""
import contextlib
import hashlib
import io
import json
import shutil
from pathlib import Path

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/studio"
MEDIA = ROOT / "docs/images/pcb-studio"
GLB = OUT / "board.glb"
OUT.mkdir(parents=True, exist_ok=True)
MEDIA.mkdir(parents=True, exist_ok=True)


def setup():
    scene = bpy.data.scenes.new("PS28 studio")
    bpy.context.window.scene = scene
    with contextlib.redirect_stdout(io.StringIO()):
        bpy.ops.import_scene.gltf(filepath=str(GLB))
    meshes = [o for o in scene.objects if o.type == "MESH"]
    points = [o.matrix_world @ Vector(p) for o in meshes for p in o.bound_box]
    bounds = [(min(p[i] for p in points), max(p[i] for p in points)) for i in range(3)]
    assert abs(bounds[0][1] - bounds[0][0] - .154) < .0001, bounds
    assert abs(bounds[1][1] - bounds[1][0] - .081) < .0001, bounds
    assert any("thermal_block" in o.data.name for o in meshes), "Thermal block missing"
    assert any("HTSSOP" in o.data.name for o in meshes), "TPA package missing"
    center = Vector([sum(b) / 2 for b in bounds])
    # Imported CAD material colors stay intact; surface response replaces flat plastic.
    for mat in {m for o in meshes for m in o.data.materials if m}:
        mat.use_nodes = True
        shader = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        rgb = shader.inputs["Base Color"].default_value[:3]
        neutral = max(rgb) - min(rgb) < .085
        shader.inputs["Metallic"].default_value = .8 if neutral and max(rgb) > .25 else 0
        shader.inputs["Roughness"].default_value = .28 if neutral and max(rgb) > .25 else .4
    for obj in meshes:
        if "soldermask" in obj.data.name:
            for mat in obj.data.materials:
                node = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
                node.inputs["Base Color"].default_value = (.012, .105, .037, 1)
                node.inputs["Roughness"].default_value = .3
                node.inputs["Coat Weight"].default_value = .25
        if "silkscreen" in obj.data.name:
            for mat in obj.data.materials:
                node = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
                node.inputs["Metallic"].default_value = 0
                node.inputs["Roughness"].default_value = .65
        if "thermal_block" in obj.data.name:
            for mat in obj.data.materials:
                node = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
                node.inputs["Metallic"].default_value = .92
                node.inputs["Roughness"].default_value = .25
    scene.unit_settings.system = "METRIC"
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 12
    scene.render.resolution_x = 1800
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world = bpy.data.worlds.new("PS28 neutral studio")
    scene.world.use_nodes = True
    background = next(n for n in scene.world.node_tree.nodes if n.type == "BACKGROUND")
    background.inputs["Color"].default_value = (.22, .25, .3, 1)
    background.inputs["Strength"].default_value = .35
    scene.view_settings.view_transform = "AgX"
    for name, offset, power, size in [
        ("Key softbox", (-.08, -.08, .18), 1.5, .16),
        ("Fill softbox", (.12, .06, .12), 1, .13),
        ("Edge strip", (-.05, .14, .08), 1.25, .1),
        ("Underside fill", (.03, -.06, -.15), .875, .12),
    ]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy, data.shape, data.size = power, "DISK", size
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = center + Vector(offset)
        obj.rotation_euler = (center - obj.location).to_track_quat("-Z", "Y").to_euler()
    data = bpy.data.cameras.new("Product camera")
    camera = bpy.data.objects.new("Product camera", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    data.lens, data.clip_start, data.clip_end = 58, .001, 10
    scene.render.film_transparent = True
    scene["source_glb_sha256"] = hashlib.sha256(GLB.read_bytes()).hexdigest()
    scene["geometry_status"] = "KiCad geometry, catalog/proxy models; not physical fit approval"
    return scene, center, len(meshes)


def frame(scene, center, offset):
    scene.camera.location = center + Vector(offset)
    scene.camera.rotation_euler = (center - scene.camera.location).to_track_quat("-Z", "Y").to_euler()
    points = [o.matrix_world @ Vector(p) for o in scene.objects if o.type == "MESH" for p in o.bound_box]
    for _ in range(6):
        bpy.context.view_layer.update()
        projected = [world_to_camera_view(scene, scene.camera, p) for p in points]
        span = max(abs(v - .5) * 2 for p in projected for v in (p.x, p.y))
        if span <= .9 and min(p.z for p in projected) > 0:
            return
        scene.camera.location = center + (scene.camera.location - center) * max(1.1, span / .88)
    raise ValueError("Board does not fit the camera with a 5 percent border")


def render():
    scene, center, count = setup()
    staging = OUT / "renders"
    staging.mkdir(exist_ok=True)
    views = {"isometric": (.17, -.21, .21), "top": (0, 0, .34),
             "bottom": (.13, -.13, -.29)}
    for name, offset in views.items():
        frame(scene, center, offset)
        scene.render.filepath = str(staging / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    frame(scene, center, views["isometric"])
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "ps28-studio.blend"))
    for name in views:
        shutil.copy2(staging / f"{name}.png", MEDIA / f"{name}.png")
    sources = [GLB, Path(__file__), ROOT / "kicad/system-candidate/system-candidate.kicad_pcb"]
    manifest = {"blender": bpy.app.version_string, "engine": scene.render.engine,
                "mesh_count": count, "samples": scene.cycles.samples,
                "manufacturing_approved": False,
                "limitations": ["Catalog and proxy models inherited from KiCad; no as-built validation",
                                "GLB exporter warning is recorded in build/studio/export.log"],
                "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                "image_sha256": {f"{n}.png": hashlib.sha256((MEDIA / f"{n}.png").read_bytes()).hexdigest() for n in views}}
    (MEDIA / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    render()
