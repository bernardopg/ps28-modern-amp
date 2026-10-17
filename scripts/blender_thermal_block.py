"""D-031 fit study, mm. No manufacturing release.

blender --background --factory-startup --python scripts/blender_thermal_block.py
Geometry source: mechanical/thermal-fit.json. PCB copper is never modified.
"""
import json
import math
from pathlib import Path
import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
C = json.loads((ROOT / "mechanical/thermal-fit.json").read_text())
U = 2.54
H5 = C["clamp_holes_xy_mm"][0]
OUT = ROOT / "build/thermal-fit"
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)


def material(name, color):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    return m


AL = material("aluminium", (.65,.69,.73))
STEEL = material("fasteners", (.22,.25,.29))
PROFILE = material("OEM profile nominal", (.16,.35,.51))
PCB = material("PCB envelope", (.08,.28,.14))
CASE = material("package", (.045,.045,.05))
PAD = material("top PowerPAD", (.72,.63,.30))
TIM = material("thin TIM nominal", (.94,.58,.15))
ENV = material("component HEIGHT ENVELOPES not exact bodies", (.24,.51,.51))


def box(name, x0,y0,z0,x1,y1,z1, mat=AL):
    bpy.ops.mesh.primitive_cube_add(size=1,location=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
    o=bpy.context.object;o.name=name;o.scale=(x1-x0,y1-y0,z1-z0)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if mat:o.data.materials.append(mat)
    return o


def cyl(name, radius, depth, center, along_y=False, mat=STEEL):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=depth,location=center,
                                      rotation=(math.pi/2,0,0) if along_y else (0,0,0))
    o=bpy.context.object;o.name=name
    if mat:o.data.materials.append(mat)
    return o


def boolean(target, tool, op="DIFFERENCE"):
    m=target.modifiers.new("machining reference", "BOOLEAN");m.operation=op;m.object=tool
    bpy.context.view_layer.objects.active=target
    bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(tool,do_unlink=True)


b=C["body_mm"];p=C["pedestal"];s=C["side_holes"]
block=box("THERMAL BLOCK - ENGINEERING STUDY", b['x'][0],b['y'][0],b['z'][0],b['x'][1],b['y'][1],b['z'][1])
px,py=p['center_xy_mm'];pw,pd=p['size_xy_mm']
boolean(block,box("pedestal",px-pw/2,py-pd/2,p['bottom_z_nominal_mm'],px+pw/2,py+pd/2,b['z'][0]+.01),"UNION")
for x,y in C['clamp_holes_xy_mm']:
    boolean(block,cyl("M3 TAP DRILL, threads not modelled",C['clamp_tap_drill_mm']/2,C['clamp_tap_depth_mm']+.2,
                      (x,y,b['z'][0]+(C['clamp_tap_depth_mm']-.2)/2),mat=None))

def cut_slots(target, ycenter, depth):
    r=s['slot_width_mm']/2;half=(s['slot_total_height_mm']-s['slot_width_mm'])/2
    for x in s['x_mm']:
        for dz in [-half,half]:
            boolean(target,cyl("OEM hole allowance",r,depth,(x,ycenter,s['z_mm']+dz),True,None))
        boolean(target,box("slot centre",x-r,ycenter-depth/2,s['z_mm']-half,x+r,ycenter+depth/2,s['z_mm']+half,None))
cut_slots(block,(b['y'][0]+b['y'][1])/2,20)

# Export main piece BEFORE assembly proxies/section operations.
bpy.ops.object.select_all(action='DESELECT');block.select_set(True)
bpy.ops.wm.stl_export(filepath=str(ROOT/'mechanical/thermal-block.stl'),export_selected_objects=True)
bm=bmesh.new();bm.from_mesh(block.data);bmesh.ops.triangulate(bm,faces=bm.faces)
# IMPORTANT: apply object world transform. Local mesh coordinates alone misplace
# the H5-anchored model even when the STL looks correct.
points=[block.matrix_world @ v.co for v in bm.verts]
vertices=' '.join(f'{(v.x-H5[0])/U:.6f} {-(v.y-H5[1])/U:.6f} {v.z/U:.6f},' for v in points)
faces=' '.join(' '.join(str(v.index) for v in f.verts)+' -1,' for f in bm.faces);bm.free()
def ray_hits(x,y,z,direction):
    inv=block.matrix_world.inverted()
    hit,loc,_,_=block.ray_cast(inv@Vector((x,y,z)),inv.to_3x3()@Vector(direction),distance=100)
    return bool(hit), list(block.matrix_world@loc) if hit else None
mesh_check={'bounds_world_mm':[[min(v[k] for v in points),max(v[k] for v in points)] for k in range(3)],
            'side_hole_rays':[ray_hits(x,40,s['z_mm'],(0,1,0))[0] for x in s['x_mm']],
            'old_wrong_height_rays':[ray_hits(x,40,6.35,(0,1,0))[0] for x in s['x_mm']],
            'contact_ray':ray_hits(px,py,-5,(0,0,1)),
            'clamp_first_hit_z_mm':[ray_hits(x,y,-5,(0,0,1))[1][2] for x,y in C['clamp_holes_xy_mm']],
            'manufacturing_approved':False}
assert not any(mesh_check['side_hole_rays']) and all(mesh_check['old_wrong_height_rays'])
assert abs(mesh_check['contact_ray'][1][2]-p['bottom_z_nominal_mm'])<.001
assert all(abs(z-(b['z'][0]+C['clamp_tap_depth_mm']))<.001 for z in mesh_check['clamp_first_hit_z_mm'])
(OUT/'mesh-check.json').write_text(json.dumps(mesh_check,indent=2)+'\n')
model=ROOT/'kicad/models/ps28-bodies/thermal_block.wrl';model.parent.mkdir(parents=True,exist_ok=True)
model.write_text('#VRML V2.0 utf8\n# ENGINEERING STUDY - NOT FOR MANUFACTURING\n'
                 'Shape { appearance Appearance { material Material { diffuseColor .74 .76 .78 specularColor .45 .45 .45 shininess .3 } } '
                 # Exported triangles wind clockwise seen from outside; ccw FALSE keeps KiCad normals outward.
                 f'geometry IndexedFaceSet {{ ccw FALSE creaseAngle .5 coord Coordinate {{ point [ {vertices} ] }} coordIndex [ {faces} ] }} }}\n')
block['status']='NOT RELEASED; calibrate stops/TIM on actual assembly'
block['side_hole_height_mm']=s['z_mm']

scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1400;scene.render.resolution_y=1000
scene.render.resolution_percentage=100;scene.display.shading.light='STUDIO'
scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True
scene.display.shading.background_type='WORLD';scene.world=bpy.data.worlds.new('studio')
scene.world.color=(.78,.80,.83)
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.clip_end=10000

def render(name, loc, target, scale):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=scale;scene.render.filepath=str(ROOT/'docs/images'/name)
    bpy.ops.render.render(write_still=True)
render('thermal-block.png',(140,0,65),(90.5,60.5,15),70)
render('thermal-block-bottom.png',(140,0,-60),(90.5,60.5,12),70)

board=box('PCB nominal 1.6 mm',20,20,-1.6,174,101,0,PCB)
for x,y in C['clamp_holes_xy_mm']:
    boolean(board,cyl('PCB clearance 3.2',1.6,4,(x,y,-.8),mat=None))
    stop=cyl('CALIBRATED METAL STOP nominal 3.3',3,3.3,(x,y,1.65),mat=STEEL)
    boolean(stop,cyl('stop bore',1.6,5,(x,y,1.65),mat=None))
    cyl('M3x10 candidate head, max OD5.5',2.75,3,(x,y,-3.1))
    cyl('M3x10 candidate shaft',1.5,10,(x,y,3.4))
# Package envelope matches the existing nominal body proxy, not an as-built height.
box('U1 case envelope',px-7,py-3.05,.1,px+7,py+3.05,1.1,CASE)
box('EXPOSED PAD minimum area',px-6.72/2,py-3.85/2,1.1,px+6.72/2,py+3.85/2,1.15,PAD)
box('TOP TIM nominal 0.05',px-3,py-1.5,1.15,px+3,py+1.5,1.2,TIM)
for i in range(22):
    x=px-6.6675+i*.635
    for sign in [-1,1]:
        y=py+sign*3.55
        box('lead envelope',x-.125,y-.6,0,x+.125,y+.6,.25,STEEL)
report=json.loads((ROOT/'tests/reports/thermal-fit-review.json').read_text())
for part in report['fit']['under_body_parts']:
    x0,y0,x1,y1=part['courtyard_xy_mm']
    box(part['reference']+' HEIGHT ENVELOPE',x0,y0,0,x1,y1,part['height_envelope_mm'],ENV)
for ref in ('L1','L2'):
    part=next(p for p in report['fit']['external_side_hardware_clearances'] if p['reference']==ref)
    x0,y0,x1,y1=part['courtyard_xy_mm']
    box(ref+' CATALOG HEIGHT ENVELOPE',x0,y0,0,x1,y1,part['height_envelope_mm'],ENV)
# Nominal original U profile, NOT an owner scan.
box('OEM base',58,68,0,123,101,6,PROFILE)
leg=box('OEM outer leg',58,68,6,123,74,30,PROFILE)
box('OEM backplate leg',58,95,6,123,101,30,PROFILE)
for x in s['x_mm']:
    boolean(leg,cyl('OEM threaded M3 simplified',1.5,8,(x,71,s['z_mm']),True,None))
shim=box('SELECTED SOLID SHIM nominal 0.9',64,67.05,3.3,117,67.95,30,AL);cut_slots(shim,67.5,3)
box('SIDE TIM 1',64,67,3.3,117,67.05,30,TIM)
box('SIDE TIM 2',64,67.95,3.3,117,68,30,TIM)
for x in s['x_mm']:
    plate=box('LOAD SPREADER 12x12x1 OFFSET HOLE',x-6,53,s['z_mm']-s['spreader_hole_from_bottom_mm'],x+6,54,s['z_mm']+(12-s['spreader_hole_from_bottom_mm']),STEEL)
    boolean(plate,cyl('spreader bore',1.7,3,(x,53.5,s['z_mm']),True,None))
    cyl('M3x20 candidate head',2.75,3,(x,51.5,s['z_mm']),True)
    cyl('M3x20 candidate shaft',1.5,20,(x,63,s['z_mm']),True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'thermal-fit-study.blend'))
render('thermal-fit-assembly.png',(157,-25,100),(90,68,12),105)
# Section is visualization only. Exported STL/WRL remain the uncut part.
for obj in list(scene.objects):
    if obj.type=='MESH':
        boolean(obj,box('visual section cutter',px,-30,-20,250,200,100,None))
        if len(obj.data.vertices):
            boolean(obj,box('thin central section only',-200,-30,-20,px-.15,200,100,None))
render('thermal-fit-section.png',(200,64,18),(px,66,14),58)
render('thermal-fit-contact.png',(160,59.5,3),(px,60.5,1.3),10)
print('Corrected block exported; fit assembly/section are STUDY views, not manufacturing drawings.')
