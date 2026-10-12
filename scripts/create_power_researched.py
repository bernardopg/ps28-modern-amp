#!/usr/bin/env python3
"""Candidatos por fonte primária, em captura isolada; sem qualificação fab/fit/térmica."""
import argparse
import hashlib
import json
from pathlib import Path
from create_analog_capture import build
from create_power_package_review import reviewed_parts
from create_power_d021 import tps3700_symbol, write_local_library
from simulate_opa1656 import ROOT


def researched_parts():
    selected = reviewed_parts()
    for p in selected:
        if p['ref'] in ('D301', 'D302'):
            p.update(value='RHRP1560 candidate', mpn=
                     'RHRP1560; onsemi RHRP1560/D Oct-2017 Rev.3 p.1-2: 600 V, 15 A at Tc=140 C, IFSM=200 A halfwave 60 Hz. TO-220AC; cathode flange LIVE PVDD. TBD physical pad mapping/land pattern and thermal. Functional symbol only.')
        if p['ref'] in ('C301', 'C302'):
            p.update(value='4700u 100V candidate', mpn=
                     'LGU2A472MELC; Nichicon LGU CAT.8100M p.1/3: 4700 uF 100 V 105 C, 4.14 A rms at 120 Hz, D35 L50, 3000 h; TBD fit/ESR/ripple sharing/stock',
                     footprint='PS28_POWER:LGU_D35_L50_P10_Study')
    return selected


def bulk_footprint():
    # CAT.8100M p.1: 10 mm pitch, two 2±0.1 mm holes. Conservative body envelope
    # uses D+1.5 =36.5 mm, plus 0.5 mm radial courtyard. Height up to L+2=52 mm.
    return '''(footprint "LGU_D35_L50_P10_Study" (version 20241229) (generator "ps28")
(layer "F.Cu") (attr through_hole)
(descr "Nichicon LGU CAT.8100M p.1: D35 L50; envelope D36.5 H52; STUDY ONLY fit/ripple TBD")
(fp_text reference "REF**" (at 5 -19.5) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
(fp_text value "LGU2A472MELC" (at 5 19.5) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
(fp_circle (center 5 0) (end 22.5 0) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))
(fp_circle (center 5 0) (end 23.25 0) (stroke (width 0.12) (type default)) (fill none) (layer "F.SilkS"))
(fp_circle (center 5 0) (end 23.75 0) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
(fp_text user "+" (at -3 0) (layer "F.SilkS") (effects (font (size 1.5 1.5) (thickness 0.2))))
(fp_text user "-" (at 13 0) (layer "F.SilkS") (effects (font (size 1.5 1.5) (thickness 0.2))))
(pad "1" thru_hole rect (at 0 0) (size 4 4) (drill 2) (layers "*.Cu" "*.Mask"))
(pad "2" thru_hole circle (at 10 0) (size 4 4) (drill 2) (layers "*.Cu" "*.Mask")))
'''


def generate(out):
    if out.exists():
        raise FileExistsError(f'Refusing to overwrite {out}')
    sch, manifest = build(researched_parts(), project='power-researched', namespace='power-researched',
                          source='onsemi RHRP1560/D Rev.3; Nichicon LGU CAT.8100M; electrical candidates only',
                          title='PS28 POWER CANDIDATES - NOT FOR FABRICATION',
                          warning='NO OVP DISCONNECT. RECTIFIER LAND PATTERN AND FUSE TBD. BULK HEIGHT UP TO 52mm: FIT NOT VERIFIED.',
                          power_flags=('PVDD','GND','AUX_RAW'),
                          extra_symbols={'PS28_POWER:TPS3700DDC':tps3700_symbol()})
    out.mkdir(parents=True)
    (out/'power-researched.kicad_sch').write_text(sch)
    (out/'power-researched.kicad_pro').write_text('{}\n')
    write_local_library(out, 'PS28_POWER', [tps3700_symbol()], 'TPS3700 DDC from TI')
    library = out/'libraries/PS28_POWER.pretty'
    library.mkdir(parents=True, exist_ok=True)
    (library/'LGU_D35_L50_P10_Study.kicad_mod').write_text(bulk_footprint())
    (out/'fp-lib-table').write_text('(fp_lib_table (lib (name "PS28_POWER") (type "KiCad") (uri "${KIPRJMOD}/libraries/PS28_POWER.pretty") (options "") (descr "Study, not for fabrication")))\n')
    manifest.update(status='Electrical candidates only; NO PCB/OVP disconnect/approved fit', manufacturing_approved=False,
                    hardware_validated=False, bulk_height_envelope_mm=52,
                    source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in (Path(__file__), ROOT/'scripts/create_power_package_review.py',
                                             ROOT/'reference/parts/onsemi-rhrp1560.pdf', ROOT/'reference/parts/nichicon-lgu.pdf')})
    (out/'researched-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'build/power-researched')
    generate(parser.parse_args().output)
