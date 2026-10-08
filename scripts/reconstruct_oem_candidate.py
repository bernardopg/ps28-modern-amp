#!/usr/bin/env python3
"""Create an OEM-referenced STUDY in a new directory; never overwrite routed/manual work.
Digitization is inferred from service-manual artwork, not physical measurement.
No inferred mechanical feature is converted into a drill hole.
"""
import argparse
import copy
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from create_core_draft import parse, render, q
from complete_core_selection import prop

ROOT = Path(__file__).resolve().parents[1]


def reconstruction():
    # PDF page19 rendered by poppler with -scale-to1600. Copper/component views
    # match connector positions without mirroring. P101 first6 usable stem centres;
    # last pin joins a plane, so don't use that irregular blob to measure the pitch.
    p101 = [606.5, 623.5, 639.5, 655.5, 672.0, 688.5]
    p103 = [1107.5, 1133.5, 1159.5]
    scales = [(p101[-1]-p101[0])/(5*2.5), (p103[-1]-p103[0])/(2*3.96)]
    scale = sum(scales)/2
    disagreement = abs(scales[0]-scales[1])/scale
    if disagreement > 0.01:
        raise ValueError('Independent connector scales disagree by more than 1%')
    origin = [254,59]
    def mm(point):return [round((v-o)/scale,3) for v,o in zip(point,origin)]
    features = [
        ('LEFT_UPPER',[274,119],'rectangular copper opening; drill/slot/support identity unconfirmed'),
        ('LEFT_LOWER',[274,390],'rectangular opening + nearby small aperture; identity unconfirmed'),
        ('RIGHT_UPPER',[1227,119],'octagonal land with small aperture; mounting/ground-contact role unconfirmed'),
        ('RIGHT_LOWER',[1227,390],'octagonal land; drill is not unambiguously shown'),
        ('THERMAL_LEFT',[592,157],'large octagonal land near power-stage region; NOT assumed a screw hole'),
        ('THERMAL_RIGHT',[822,157],'large octagonal land near power-stage region; NOT assumed a screw hole'),
    ]
    return {
        'status':'SCALED STUDY ONLY; NOT a drill template or manufacturing approval',
        'source':'reference/infinity/ps28-service-manual.pdf',
        'source_sha256':hashlib.sha256((ROOT/'reference/infinity/ps28-service-manual.pdf').read_bytes()).hexdigest(),
        'printed_pages':[15,16,17,18], 'raster_pdf_page':19,
        'raster_render':'pdftoppm -f19 -l19 -scale-to1600 -png',
        'raster_dimensions_px':[1600,1131],
        'digitization_uncertainty_px':1.0,
        'calibrations':[
            {'ref':'P101','manual_printed_page':15,'pitch_mm':2.5,'five_pitch_span_mm':12.5,'x_centers_px':p101,'pixels_per_mm':scales[0]},
            {'ref':'P103','manual_printed_page':15,'pitch_mm':3.96,'outer_pin_span_mm':7.92,'x_centers_px':p103,'pixels_per_mm':scales[1]},
        ],
        'horizontal_scale_disagreement_fraction':disagreement,
        'pixels_per_mm_study':scale,
        'vertical_scale':'ASSUMED isotropic; no independent vertical calibration/measurement',
        'origin_px':origin,
        'copper_panel_bounds_px':[254,59,1257,578],
        'outer_graphic_frame_bounds_px':[254,59,1343,578],
        'copper_region_mm_study':mm([1257,578]),
        'outer_graphic_frame_mm_study':mm([1343,578]),
        'right_blank_strip_is_actual_PCB':'UNRESOLVED: could be drawing/frame/side-view, not adopted as fabrication edge',
        'mechanical_features':[{'id':name,'center_px':xy,'center_mm_study':mm(xy),'classification':kind,
                                'drill_shape_mm':None,'reserve_radius_mm':4.5} for name,xy,kind in features],
        'OEM_Q107_Q108_centers_mm_study':[mm([576,271]),mm([840,271])],
        'new_U1_center_mm_study':[69,32],
        'preserve_original_mounting_points':True,'allow_new_plate_holes':False,
        'mounting_pattern_complete':False,'mechanical_approved':False,'manufacturing_approved':False,
    }


def candidate(out):
    """Publish only a complete candidate; failures must not leave a usable-looking PCB."""
    out = Path(out).resolve()
    if out.exists():raise ValueError(f'Refusing to overwrite existing directory: {out}')
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.oem-stage-', dir=out.parent) as temporary:
        staged = Path(temporary) / out.name
        data = _candidate(staged)
        staged.rename(out)
    return data


def _candidate(out):
    source=ROOT/'kicad/core-selected'
    # No deletion/reroute, even if user later points this initializer at an edited file.
    pcb_text=(source/'ps28-modern.kicad_pcb').read_text()
    tree=parse(pcb_text)
    if any(isinstance(x,list) and x[0] in ['segment','arc','via','zone'] for x in tree):
        raise ValueError('Source has routing/zones: this placement initializer must not regenerate it')
    data=reconstruction()
    out.mkdir(parents=True)
    for name in ['ps28-modern.kicad_pro','ps28-modern.kicad_sch','ps28-modern.kicad_pcb',
                 'fp-lib-table','sym-lib-table','core-manifest.json']:
        shutil.copy2(source/name,out/name)
    shutil.copytree(source/'libraries',out/'libraries')
    # No new mounting hole: use a copper solder-bond feature instead of draft J6/M3.
    fp='''(footprint "Ground_Bond_SMD_6mm" (version 20241229) (generator pcbnew)
(layer "F.Cu") (descr "Soldered GND braid landing; NOT an OEM mounting point; no drill")
(attr smd exclude_from_pos_files exclude_from_bom)
(fp_text reference "REF**" (at 0 -4) (layer "F.SilkS") (effects (font (size 0.8 0.8))))
(fp_text value "Ground_Bond_SMD_6mm" (at 0 4) (layer "F.Fab") (effects (font (size 1 1))))
(fp_rect (start -3.5 -3.5) (end 3.5 3.5) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
(pad "1" smd rect (at 0 0) (size 6 6) (layers "F.Cu" "F.Mask")))'''
    (out/'libraries/PS28.pretty/Ground_Bond_SMD_6mm.kicad_mod').write_text(fp+'\n')
    manifest=json.loads((out/'core-manifest.json').read_text())
    positions={'C14':[16.25,25,0],'C15':[16.25,53,0],
        'L1':[114,18.5,0],'L2':[114,49.5,180],
        'C22':[136,14,0],'C23':[139,28,0],'C26':[136,49,0],'C27':[139,63,0],
        'C24':[132,13,0],'C25':[132,20,0],'R5':[131,28,0],
        'C28':[132,48,0],'C29':[132,55,0],'R6':[130,63,0],
        'J1':[20,70,0],'J2':[70,70,0],'J3':[52,69,0],'J4':[36,51,0],
        'J5':[143,74,0],'J6':[92,67,0],
        'C1':[77.5,64,0],'C20':[45,27,0],'C21':[45,31,0],
        'R1':[61,20,0],'R7':[49,54,0],'R8':[49,58,0],'R9':[49,62,0]}
    for p in manifest['parts']:
        # Source B has board origin(20,20). Move U1/local55,40 to local69,32;
        # shift quiet/local bypass group rigidly, then place tall/interfaces explicitly.
        old=p['pcb_position'];new=positions.get(p['ref'],[old[0]-20+14,old[1]-20-8,p.get('rotation',0)])
        p['pcb_position']=[new[0]+20,new[1]+20];p['rotation']=new[2]
        if p['ref']=='J6':
            p.update(footprint='PS28:Ground_Bond_SMD_6mm',value='GND braid solder bond - NO mounting hole',
                mpn='PCB solder land + grounded braid assembly; NOT purchase PN',manufacturer='PCB assembly feature',
                source='D-014: reuse OEM mounts, no new mounting point; dedicated GND bond',in_bom=False)
    manifest['mechanical_reconstruction']=data
    manifest['mechanical_approved']=False;manifest['manufacturing_approved']=False
    manifest['provisional_outline_mm']=[153,79.1]
    manifest['outline_basis']='Conservative copper-panel crop study; actual OEM edge/right strip unresolved, not OEM fit approval'
    (out/'core-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    schema=parse((out/'ps28-modern.kicad_sch').read_text())
    for node in schema:
        if not isinstance(node,list) or node[0]!='symbol':continue
        ref=next((x[2] for x in node if isinstance(x,list) and x[:2]==['property',q('Reference')]),None)
        if ref==q('J6'):
            for key,val in [('Value','GND braid solder bond - NO mounting hole'),('Footprint','PS28:Ground_Bond_SMD_6mm'),
                            ('MPN','PCB solder land + grounded braid assembly; NOT purchase PN'),('Manufacturer','PCB assembly feature'),
                            ('Source','D-014: reuse OEM mounts, no new mounting point; dedicated GND bond')]:prop(node,key,val)
    (out/'ps28-modern.kicad_sch').write_text(render(schema)+'\n')
    import pcbnew
    board=pcbnew.LoadBoard(str((out/'ps28-modern.kicad_pcb').resolve()))
    if board is None:raise ValueError('Native KiCad failed to load source')
    parts={p['ref']:p for p in manifest['parts']}
    for f in list(board.GetFootprints()):
        p=parts[f.GetReference()]
        if p['ref']=='J6':
            path=f.GetPath();net=next(iter(f.Pads())).GetNet();board.Remove(f)
            f=pcbnew.FootprintLoad(str((out/'libraries/PS28.pretty').resolve()),'Ground_Bond_SMD_6mm')
            f.SetFPID(pcbnew.LIB_ID('PS28','Ground_Bond_SMD_6mm'));f.SetReference('J6');f.SetValue(p['value']);f.SetPath(path)
            f.Value().SetVisible(False);next(iter(f.Pads())).SetNet(net)
            for key in ['MPN','Manufacturer','Source']:f.SetField(key,p[key.lower()]);f.GetField(key).SetVisible(False)
            f.SetField('SelectionStatus',p['selection']);f.GetField('SelectionStatus').SetVisible(False)
            board.Add(f)
        f.SetPosition(pcbnew.VECTOR2I(*(pcbnew.FromMM(v) for v in p['pcb_position'])))
        f.SetOrientationDegrees(p['rotation'])
    # Remove old study edge and drawings; no electrically meaningful copper is removed.
    for obj in list(board.GetDrawings()):board.Remove(obj)
    def point(x,y):return pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))
    def segment(a,b,layer):
        s=pcbnew.PCB_SHAPE(board);s.SetShape(pcbnew.SHAPE_T_SEGMENT);s.SetStart(point(*a));s.SetEnd(point(*b));s.SetLayer(layer);s.SetWidth(pcbnew.FromMM(.05));board.Add(s)
    def note(txt,x,y,size=1):
        t=pcbnew.PCB_TEXT(board);t.SetText(txt);t.SetPosition(point(x,y));t.SetLayer(pcbnew.Dwgs_User);t.SetTextSize(point(size,size));t.SetTextThickness(pcbnew.FromMM(.15));board.Add(t)
    edges=[(20,20),(173,20),(173,99.1),(20,99.1)]
    for a,b in zip(edges,edges[1:]+edges[:1]):segment(a,b,pcbnew.Edge_Cuts)
    # Reservations, NOT holes: do not convert uncertain pads into drilling information.
    for feature in data['mechanical_features']:
        x,y=feature['center_mm_study'];x+=20;y+=20;r=feature['reserve_radius_mm']
        c=pcbnew.PCB_SHAPE(board);c.SetShape(pcbnew.SHAPE_T_CIRCLE);c.SetStart(point(x,y));c.SetEnd(point(x+r,y));c.SetWidth(pcbnew.FromMM(.15));c.SetLayer(pcbnew.Dwgs_User);board.Add(c)
        note(feature['id']+' / NO DRILL',x,y+6,.75)
        for layer in [pcbnew.F_Cu,pcbnew.In1_Cu,pcbnew.In2_Cu,pcbnew.B_Cu]:
            z=pcbnew.ZONE(board);z.SetLayer(layer);z.SetIsRuleArea(True)
            z.SetDoNotAllowFootprints(True);z.SetDoNotAllowPads(True)
            z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowZoneFills(True)
            poly=pcbnew.SHAPE_POLY_SET();poly.NewOutline()
            for dx,dy in [(-r,-r),(r,-r),(r,r),(-r,r)]:poly.Append(point(x+dx,y+dy))
            z.SetOutline(poly);poly.thisown=False  # ZONE takes ownership of the polygon.
            board.Add(z)
    segment((173,20),(173,99.1),pcbnew.Dwgs_User)
    note('RIGHT FRAME STRIP: EDGE UNRESOLVED',179.5,104,.8)
    note('OEM STUDY - 2 X CALIBRATION - NOT FABRICATION / MOUNT FIT UNVERIFIED',103,14,1)
    note('NO INFERRED MOUNT HOLES; J6 = SOLDERED GND BOND',103,109,1)
    pcbnew.SaveBoard(str((out/'ps28-modern.kicad_pcb').resolve()),board)
    with (out/'selected-bom.csv').open('w',newline='') as f:
        cols=['ref','value','mpn','manufacturer','footprint','source','selection','in_bom']
        w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(manifest['parts'])
    (out/'README.md').write_text('# OEM-referenced core STUDY\n\nReconstructed scale/placement, NOT manufacturing approval.\n'
        'Original B preserved. See ../../mechanical/original-board-reference.md and oem-reconstruction.json.\n'
        'No inferred holes; ambiguous features reserved. Actual edge/right strip and vertical scale unresolved.\n')
    (out/'oem-reconstruction.json').write_text(json.dumps(data,indent=2)+'\n')
    return data


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=ROOT/'build/oem-candidate')
    args=ap.parse_args();data=candidate(args.output.resolve())
    print(json.dumps({'output':str(args.output),'scale_disagreement':data['horizontal_scale_disagreement_fraction'],
                      'mounting_pattern_complete':False,'manufacturing_approved':False},indent=2))

if __name__=='__main__':main()
