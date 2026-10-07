#!/usr/bin/env python3
"""Prepare the selected core revision in a NEW directory; never overwrite GUI buffers.
Datasheet-based footprints, no automatic release or removal of ERC violations.
"""
from pathlib import Path
import argparse
import copy
import csv
import hashlib
import json
import math
import shutil
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from create_core_draft import parse, render, q, uid, stock_symbol, library_pins

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'kicad/core-selected'
SOURCES = {
 'hcf': ('7443631000.pdf', 'we-hcf-7443631000.pdf', 'https://www.we-online.com/components/products/datasheet/7443631000.pdf', 'WE 006.000 2025-07-08 p.1: 10uH/16A/22A typ/8.76mOhm max; stability land NOT electrical'),
 'film': ('wima-mkp2.pdf', 'wima-mkp2.pdf', 'https://www.wima.de/wp-content/uploads/media/e_WIMA_MKP_2.pdf', 'WIMA MKP2 03.26 p.38-39: 470nF 100V, W8.5 H14 L7.2 PCM5; J S SD suffix'),
 'aux': ('860020575014.pdf', 'we-860020575014.pdf', 'https://www.we-online.com/components/products/datasheet/860020575014.pdf', 'WE WCAP-ATG5 rev1.0 2014-11-11 p.1: 470uF 35V D10 H16+1.5 P5 drill0.9; ripple520mA/120Hz'),
 'bulk': ('nichicon-uhe-series.pdf', 'nichicon-uhe.pdf', 'https://www.nichicon.co.jp/english/series_items/catalog_pdf/e-uhe.pdf', 'Nichicon UHE CAT.8100M p.1/p.6: UHE1J152MHD 1500uF 63V D18 H40+2 P7.5; Zmax36mOhm/100kHz/20C; ripple2470mA/100kHz/105C (x0.8 at120Hz); 10000h/105C'),
 'terminal': ('691137710002.pdf', 'we-691137710002.pdf', 'https://www.we-online.com/components/products/datasheet/691137710002.pdf', 'WE WR-TBL1377 rev001.003 2021-07-30 p.1-2: pitch5.00 NOT5.08; 2pins, D1.3 drill, 16A UL/24A VDE'),
 'resistor': ('dcrcwe3.pdf', 'vishay-dcrcwe3.pdf', 'https://www.vishay.com/docs/20035/dcrcwe3.pdf', 'Vishay D/CRCW e3 doc20035: 0603 0.1W, 1206 0.25W and ordering system'),
}
TI_BOM = 'TI SLOU441 July2016 Table8 p.14-16; nominal package geometry; sourcing/lifecycle not verified'


def child(node, tag):
    return next((x for x in node if isinstance(x, list) and x[0] == tag), None)


def prop(node, name, value):
    found = next((x for x in node if isinstance(x, list) and x[:2] == ['property', q(name)]), None)
    if found:
        found[2] = q(value)
    else:
        template = copy.deepcopy(next(x for x in node if isinstance(x, list) and x[0] == 'property'))
        template[1:3] = [q(name), q(value)]
        template.append(['hide', 'yes']) if node[0] == 'footprint' else child(template, 'effects').append(['hide', 'yes'])
        node.append(template)


def clone_fp(library, name, custom_name, description):
    fp = parse((Path('/usr/share/kicad/footprints') / (library+'.pretty') / (name+'.kicad_mod')).read_text())
    fp[1] = q(custom_name)
    prop(fp, 'Value', custom_name)
    child(fp, 'descr')[1] = q(description)
    return fp


def custom_footprints(directory):
    pretty = directory / 'libraries/PS28.pretty'
    pretty.mkdir(parents=True)
    fp = clone_fp('Inductor_SMD', 'L_Wuerth_HCF-2013', 'WE_HCF2013_7443631000', SOURCES['hcf'][3])
    for pad in [x for x in fp if isinstance(x, list) and x[0] == 'pad']:
        number = json.loads(pad[1])
        child(pad, 'at')[2] = '-8.5' if not number else '8.5'
    # Generic stock model is not a verified 14.5mm-high model of this MPN.
    fp = [x for x in fp if not (isinstance(x, list) and x[0] == 'model')]
    (pretty/'WE_HCF2013_7443631000.kicad_mod').write_text(render(fp)+'\n')
    fp = clone_fp('Capacitor_THT', 'CP_Radial_D10.0mm_P5.00mm', 'WE_860020575014', SOURCES['aux'][3])
    for item in fp:
        if not isinstance(item, list):
            continue
        if item[0] == 'pad':
            child(item, 'drill')[1] = '0.9'
        if item[0] == 'fp_circle' and child(item, 'layer')[1] in {q('F.Courtyard'), q('F.CrtYd')}:
            center = child(item, 'center')
            child(item, 'end')[1:3] = [str(float(center[1])+5.75), center[2]]
    fp = [x for x in fp if not (isinstance(x, list) and x[0] == 'model')]
    (pretty/'WE_860020575014.kicad_mod').write_text(render(fp)+'\n')
    # Body front is +Y. Datasheet pin offset 3.5 from front, body 10 x 7.5.
    terminal = f'''(footprint "WE_WR_TBL_691137710002" (version 20241229) (generator "pcbnew")
      (layer "F.Cu") (descr {q(SOURCES['terminal'][3])}) (attr through_hole)
      (property "Reference" "REF**" (at 2.5 -5.5 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
      (property "Value" "691137710002" (at 2.5 5 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
      (fp_rect (start -2.5 -4) (end 7.5 3.5) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))
      (fp_rect (start -2.65 -4.15) (end 7.65 3.65) (stroke (width 0.12) (type default)) (fill none) (layer "F.SilkS"))
      (fp_rect (start -3.1 -4.6) (end 8.1 4.1) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
      (fp_line (start -2.5 2.5) (end 7.5 2.5) (stroke (width 0.1) (type default)) (layer "F.Fab"))
      (pad "1" thru_hole rect (at 0 0) (size 2.6 2.6) (drill 1.3) (layers "*.Cu" "*.Mask"))
      (pad "2" thru_hole circle (at 5 0) (size 2.6 2.6) (drill 1.3) (layers "*.Cu" "*.Mask")))'''
    (pretty/'WE_WR_TBL_691137710002.kicad_mod').write_text(terminal+'\n')
    (directory/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "PS28") (type "KiCad") '
        '(uri "${KIPRJMOD}/libraries/PS28.pretty") (options "") (descr "Manufacturer-sourced core footprints")))\n')


def selection(parts):
    by_ref = {p['ref']: p for p in parts}

    def set_part(refs, value, mpn, manufacturer, footprint, source, geometry=None):
        for ref in refs.split():
            p = by_ref[ref]
            p.update(value=value, mpn=mpn, manufacturer=manufacturer, footprint=footprint,
                     source=source, selection='Selected for engineering validation; NO procurement/release approval')
            if geometry:
                p['geometry'] = geometry
    set_part('U1', 'TPA3255DDV', 'TPA3255DDVR', 'Texas Instruments', by_ref['U1']['footprint'], 'TI SLASEA8A DDV0044D / package addendum')
    set_part('L1 L2', '10uH 16A 22A_Isat_typ', '7443631000', 'Wurth Elektronik', 'PS28:WE_HCF2013_7443631000', SOURCES['hcf'][3], {'body_max_mm':[21.8,21.5,14.5], 'pad3':'unnumbered mechanical stability; no net'})
    set_part('C1', '470uF 35V', '860020575014', 'Wurth Elektronik', 'PS28:WE_860020575014', SOURCES['aux'][3], {'diameter_max_mm':10.5,'height_max_mm':17.5,'pitch_mm':5,'drill_mm':0.9})
    set_part('C14 C15', '1500uF 63V', 'UHE1J152MHD', 'Nichicon', 'Capacitor_THT:CP_Radial_D18.0mm_P7.50mm', SOURCES['bulk'][3], {'diameter_max_mm':18.5,'height_max_mm':42,'pitch_mm':7.5,'ripple_A_100kHz_105C':2.470,'ripple_A_120Hz_105C':1.976,'impedance_max_ohm_100kHz_20C':0.036,'endurance_hours_105C':10000})
    set_part('C22 C23 C26 C27', '470nF 100V PP 5%', 'MKP2D034701M00JSSD', 'WIMA', 'Capacitor_THT:C_Rect_L7.2mm_W8.5mm_P5.00mm_FKP2_FKP2_MKS2_MKP2', SOURCES['film'][3], {'body_nominal_mm':[7.2,8.5,14],'pitch_mm':5,'lead_mm':0.5})
    set_part('J1 J5', '691137710002 2P 5.00mm', '691137710002', 'Wurth Elektronik', 'PS28:WE_WR_TBL_691137710002', SOURCES['terminal'][3], {'body_mm':[10,7.5,11.5],'pitch_mm':5,'drill_mm':1.3,'rated_current_UL_A':16})
    set_part('J6', 'GND bond M3 - NOT original plate hole', 'ISO4762 M3x8 + ISO7089 M3 + nut/ring lug', 'Standard hardware assembly', 'MountingHole:MountingHole_3.2mm_M3_Pad', 'Assembly specification; PCB bond point only, no original plate dimension asserted')
    set_part('C2 C4 C5', '100nF 50V X7R', 'C0603C104K5RACTU', 'KEMET', 'Capacitor_SMD:C_0603_1608Metric', TI_BOM)
    set_part('C3 C20 C21', '10uF 16V X5R', 'EMK212BJ106KG-T', 'Taiyo Yuden', 'Capacitor_SMD:C_0805_2012Metric', TI_BOM+'; effective capacitance/DC-bias check still required at VDD')
    set_part('C6 C7 C9', '1uF 16V X7R', 'GRM188R71C105KA12D', 'Murata', 'Capacitor_SMD:C_0603_1608Metric', TI_BOM)
    set_part('C8', '47nF 25V X7R', 'GRM155R71E473KA88D', 'Murata', 'Capacitor_SMD:C_0402_1005Metric', TI_BOM)
    set_part('C10 C11 C12 C13', '1uF 100V X7R', 'GRM31CR72A105KA01L', 'Murata', 'Capacitor_SMD:C_1206_3216Metric', TI_BOM)
    set_part('C16 C17 C18 C19', '33nF 25V X7R', 'GRM188R71E333KA01D', 'Murata', 'Capacitor_SMD:C_0603_1608Metric', TI_BOM)
    set_part('C24 C28', '1nF 100V C0G', '12061A102JAT2A', 'KYOCERA AVX', 'Capacitor_SMD:C_1206_3216Metric', TI_BOM)
    set_part('C25 C29', '10nF 100V X7R', '06031C103KAT2A', 'KYOCERA AVX', 'Capacitor_SMD:C_0603_1608Metric', TI_BOM)
    set_part('J2', 'Auxiliary 12V', 'PBC02SAAN', 'Sullins', by_ref['J2']['footprint'], TI_BOM)
    set_part('J3', 'Differential audio', 'PBC03SAAN', 'Sullins', by_ref['J3']['footprint'], TI_BOM)
    set_part('J4', 'Control 2x4: 3V3 RESET FAULT CLIP GND GND NC NC', 'PEC04DAAN', 'Sullins', 'Connector_PinHeader_2.54mm:PinHeader_2x04_P2.54mm_Vertical', TI_BOM)
    by_ref['J4']['lib_id'] = 'Connector_Generic:Conn_02x04_Odd_Even'
    by_ref['J4']['nets'].update({'6':'GND','7':None,'8':None})
    for refs, value, code, package in [('R1 R2 R5 R6','3.3R 0.25W 1%','3R30','1206'), ('R3','22k 1%','22K0','0603'), ('R4','30k 1%','30K0','0603'), ('R7 R8 R9','10k 1%','10K0','0603')]:
        set_part(refs,value,'CRCW'+package+code+'FKEA','Vishay',f'Resistor_SMD:R_{package}_{"3216" if package=="1206" else "1608"}Metric',SOURCES['resistor'][3])
    by_ref['J6']['in_bom'] = False  # PCB copper bond feature; fasteners are an assembly BOM.
    poses = {'L1':[111,46.5,0], 'L2':[111,77.5,180], 'C1':[52,82,0], 'C14':[50,35,0], 'C15':[74,35,0],
             'C22':[128,54,0], 'C23':[138,54,0], 'C26':[128,70,0], 'C27':[138,70,0],
             'C24':[150,57.5,0], 'C25':[150,53,0], 'R5':[155,48,0],
             'C28':[150,76.5,0], 'C29':[150,72,0], 'R6':[155,81,0],
             'J1':[35,30,0], 'J2':[35,48,0], 'J5':[151,64,0], 'J6':[70,86,0],
             'R7':[46,87,0], 'R8':[46,91,0], 'R9':[46,95,0]}
    # Single uncoupled L can reverse winding polarity: input pad remains nearer IC.
    by_ref['L2']['nets'] = {'1':'SPK_N','2':'PWM_BD'}
    for p in parts:
        pose = poses.get(p['ref'], (p['pcb_position'] or [0,0])+[0])
        p['pcb_position'], p['rotation'] = pose[:2], pose[2]
    return by_ref


def wire_pin(out, ref, number, x, y, px, py, angle, net):
    wx, wy = round(x+px,4), round(y-py,4)
    if net is None:
        out.append(['no_connect',['at',str(wx),str(wy)],['uuid',q(uid(ref+':nc:'+number))]])
        return
    rad = math.radians(angle+180)
    lx,ly=round(wx+2.54*math.cos(rad),4),round(wy-2.54*math.sin(rad),4)
    out.append(['wire',['pts',['xy',str(wx),str(wy)],['xy',str(lx),str(ly)]],['stroke',['width','0'],['type','default']],['uuid',q(uid(ref+':wire:'+number))]])
    out.append(['label',q(net),['at',str(lx),str(ly),'0'],['effects',['font',['size','0.9','0.9']],['justify','right' if lx<wx else 'left','bottom']],['uuid',q(uid(ref+':label:'+number))]])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install',action='store_true')
    args=parser.parse_args()
    if args.install and DEST.exists():
        raise SystemExit('Selected revision exists: edit in KiCad, do not overwrite it.')
    directory=ROOT/'build/core-selected'
    if directory.exists():
        raise SystemExit('Preview already exists; preserve it or select a new revision, no overwrite.')
    directory.mkdir(parents=True)
    for name in ['ps28-modern.kicad_pro','sym-lib-table']:
        shutil.copy2(ROOT/'kicad'/name,directory/name)
    (directory/'libraries').mkdir()
    shutil.copy2(ROOT/'kicad/libraries/PS28.kicad_sym',directory/'libraries/PS28.kicad_sym')
    custom_footprints(directory)
    manifest=json.loads((ROOT/'kicad/core-manifest.json').read_text())
    manifest.update(revision='B-selected', mechanical_approved=False, manufacturing_approved=False, design_directory='kicad/core-selected', unassigned_footprints=[])
    selected=selection(manifest['parts'])
    sch=parse((ROOT/'kicad/ps28-modern.kicad_sch').read_text())
    cache=child(sch,'lib_symbols')
    extra=stock_symbol('Connector_Generic','Conn_02x04_Odd_Even')
    cache.append(extra)
    # An uncoupled inductor's winding direction is interchangeable; update BOTH
    # schematic labels and placement metadata when reversing L2 to shorten loops.
    for item in sch:
        if isinstance(item,list) and item[0]=='label' and child(item,'uuid'):
            for number in ['1','2']:
                if child(item,'uuid')[1] == q(uid('L2:label:'+number)):
                    item[1] = q(selected['L2']['nets'][number])
    # Replace J4 pin geometry; keep all other captured wires/nets/UUIDs.
    old_ids={uid('J4:'+kind+':'+str(n)) for kind in ['wire','label','nc'] for n in range(1,6)}
    sch=[item for item in sch if not (isinstance(item,list) and child(item,'uuid') and json.loads(child(item,'uuid')[1]) in old_ids)]
    flag_template=None
    for symbol in [x for x in sch if isinstance(x,list) and x[0]=='symbol' and child(x,'lib_id')]:
        ref=json.loads(next(x for x in symbol if isinstance(x,list) and x[:2]==['property',q('Reference')])[2])
        if ref.startswith('#'):
            flag_template=copy.deepcopy(symbol)
            continue
        p=selected[ref]
        for name,key in [('Value','value'),('Footprint','footprint'),('SelectionStatus','selection'),('MPN','mpn'),('Manufacturer','manufacturer'),('Source','source')]:
            prop(symbol,name,p[key])
        if ref == 'J6':
            child(symbol,'in_bom')[1] = 'no'
        if ref=='J4':
            child(symbol,'lib_id')[1]=q(p['lib_id'])
            symbol[:]=[v for v in symbol if not (isinstance(v,list) and v[0]=='pin')]
            x,y=map(float,child(symbol,'at')[1:3])
            for number,px,py,angle in library_pins(extra):
                symbol.append(['pin',q(number),['uuid',q(uid(ref+':pin:'+number))]])
                wire_pin(sch,ref,number,x,y,px,py,angle,p['nets'][number])
    # Bootstrap sources are internal charge circuits, not unpowered external supplies.
    for i,net in enumerate(['BST_A','BST_B','BST_C','BST_D']):
        ref='#FLG_BS'+str(i+1)
        flag=copy.deepcopy(flag_template)
        x,y=round(round((40+i*45)/1.27)*1.27,4),233.68
        old_x,old_y=map(float,child(flag,'at')[1:3])
        child(flag,'uuid')[1]=q(uid('symbol:'+ref)); child(flag,'at')[1:3]=[str(x),str(y)]
        prop(flag,'Reference',ref);prop(flag,'Source','SLASEA8A bootstrap driven from internal GVDD gate driver, 33nF to switching node')
        for field in [v for v in flag if isinstance(v,list) and v[0]=='property']:
            at=child(field,'at');at[1:3]=[str(round(float(at[1])+x-old_x,4)),str(round(float(at[2])+y-old_y,4))]
        child(flag,'pin')[2][1]=q(uid(ref+':pin:1'))
        instances=child(flag,'instances');project=instances[1];path=project[2];child(path,'reference')[1]=q(ref)
        sch.append(flag)
        # PWR_FLAG pin is at its anchor; attach a short downward stub.
        wire_pin(sch,ref,'1',x,y,0,0,90,net)
    child(child(sch,'title_block'),'rev')[1]=q('B-selected-NOT-RELEASED')
    for v in sch:
        if isinstance(v,list) and v[0]=='text':
            v[1]=q('SELECTED CORE - PBTL - POWER/FRONT-END NOT INCLUDED - CASE FIT UNMEASURED')
    (directory/'ps28-modern.kicad_sch').write_text(render(sch)+'\n')
    (directory/'core-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    # Export actual updated connectivity, then place from it, never from guessed pad positions.
    netlist=directory/'core.xml'
    subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','--output',str(netlist),str(directory/'ps28-modern.kicad_sch')],check=True,timeout=60)
    import pcbnew
    board=pcbnew.BOARD();board.SetCopperLayerCount(4)
    title=board.GetTitleBlock();title.SetTitle('PS28 CORE B - SELECTED - CASE FIT UNMEASURED');title.SetRevision('B-selected');board.SetTitleBlock(title)
    graph=ET.parse(netlist).getroot();nets={};mapping={}
    for net in graph.findall('./nets/net'):
        name=net.attrib['name'];item=pcbnew.NETINFO_ITEM(board,name,int(net.attrib['code']));board.Add(item);nets[name]=item
        for pin in net.findall('node'):
            mapping[(pin.attrib['ref'],pin.attrib['pin'])]=name
    for component in graph.findall('./components/comp'):
        ref=component.attrib['ref']
        if ref not in selected:continue
        p=selected[ref];lib,name=p['footprint'].split(':',1)
        path=directory/'libraries/PS28.pretty' if lib=='PS28' else Path('/usr/share/kicad/footprints')/(lib+'.pretty')
        fp=pcbnew.FootprintLoad(str(path),name)
        if fp is None:raise ValueError(f'Missing footprint {ref}: {lib}:{name}')
        fp.SetFPID(pcbnew.LIB_ID(lib,name));fp.SetReference(ref);fp.SetValue(p['value']);fp.Value().SetVisible(False)
        for field in component.findall('./fields/field'):
            key=field.attrib.get('name','')
            if key in ['Source','MPN','Manufacturer','SelectionStatus']:
                fp.SetField(key,field.text or '');fp.GetField(key).SetVisible(False)
        x,y=p['pcb_position'];fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y)));fp.SetOrientationDegrees(p['rotation'])
        if ref == 'C20':
            fp.Reference().SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(51),pcbnew.FromMM(46)))
        path_id=pcbnew.KIID_PATH();path_id.push_back(pcbnew.KIID(manifest['schematic_uuid']));path_id.push_back(pcbnew.KIID(component.findtext('tstamps').strip('/').split('/')[-1]));fp.SetPath(path_id)
        for pad in fp.Pads():
            number=pad.GetNumber()
            if not number:continue  # HCF stability tab, explicitly no electrical connection.
            pad.SetNet(nets[mapping[(ref,number)]])
        board.Add(fp)
    def point(x,y):return pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))
    def line(a,b,layer=pcbnew.Dwgs_User):
        item=pcbnew.PCB_SHAPE();item.SetShape(pcbnew.SHAPE_T_SEGMENT);item.SetStart(point(*a));item.SetEnd(point(*b));item.SetWidth(pcbnew.FromMM(0.05));item.SetLayer(layer);board.Add(item)
    for a,b in [((20,20),(165,20)),((165,20),(165,115)),((165,115),(20,115)),((20,115),(20,20))]:line(a,b,pcbnew.Edge_Cuts)
    # Only the top contact area, not a fake outline of the original heatsink.
    for a,b in [((73.1,56.7),(76.9,56.7)),((76.9,56.7),(76.9,63.3)),((76.9,63.3),(73.1,63.3)),((73.1,63.3),(73.1,56.7))]:line(a,b)
    for text,x,y in [('TOP CONTACT: Cu adapter to ORIGINAL METAL SINK - dimensions pending',94,106),('145x95 provisional - verify original plate/holes/depth before freeze',94,110),('NOT ROUTED / NOT FOR FABRICATION',94,113)]:
        note=pcbnew.PCB_TEXT(board);note.SetText(text);note.SetPosition(point(x,y));note.SetTextSize(point(0.8,0.8));note.SetTextThickness(pcbnew.FromMM(0.12));note.SetLayer(pcbnew.Dwgs_User);board.Add(note)
    pcbnew.SaveBoard(str(directory/'ps28-modern.kicad_pcb'),board)
    with (directory/'selected-bom.csv').open('w',newline='') as f:
        columns=['ref','value','mpn','manufacturer','footprint','source','selection','in_bom'];writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(manifest['parts'])
    (directory/'README.md').write_text('# Core B — seleção e placement\n\n47 componentes/footprints; consultar ../../docs/selected-core.md.\n'
        'Sem fit medido, sem roteamento e sem fabricação autorizada.\nMPNs são seleção de engenharia, sem estoque/compra/lifecycle aprovados.\n')
    if args.install:
        shutil.copytree(directory,DEST,ignore=shutil.ignore_patterns('core.xml'))
        refdir=ROOT/'reference/parts';refdir.mkdir(exist_ok=True)
        entries=json.loads((ROOT/'reference/manifest.json').read_text())
        for key,(raw,name,url,review) in SOURCES.items():
            data=(ROOT/'build/parts'/raw).read_bytes()
            if not data.startswith(b'%PDF-'):raise ValueError('Invalid manufacturer PDF: '+raw)
            destination=refdir/name;destination.write_bytes(data)
            file=str(destination.relative_to(ROOT))
            entries=[e for e in entries if e.get('file')!=file]
            entries.append({'file':file,'url':url,'accessed':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(data).hexdigest(),'license':'Third-party copyright; local engineering reference only','review_status':review})
        (ROOT/'reference/manifest.json').write_text(json.dumps(entries,indent=2)+'\n')
    print('47 selected components/footprints; no routing, measured fit or release approval. New revision:',DEST if args.install else directory)


if __name__=='__main__':main()
