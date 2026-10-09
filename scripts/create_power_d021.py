#!/usr/bin/env python3
"""Capture D-021 power block separately; never overwrite existing designs.

Scope: T1 secondary input, CT return fuse, two-diode full-wave rectifier, added bulk,
bleeder, TVS, AUX 12 V buck (TI LM5164 SNVSAU4D Fig 7-1 values) and PVDD window
supervisor (TI TPS3700 SBVS187G). Footprints and most passive MPNs remain TBD.
"""

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from create_analog_capture import build
from create_core_draft import parse, q, render
from simulate_opa1656 import ROOT

DESIGN = ROOT / "kicad/power-d021"
SOURCE = "D-021: unregulated PVDD from T1 CT two-diode rectifier; study only; no hardware sign-off"

# PVDD window divider PVDD-R320-UV-R321-OV-R322-GND (E96, 0.1 %).
R_TOP, R_MID, R_BOT = 931e3, 6.04e3, 7.32e3
R_TOL = 0.001
# TPS3700 SBVS187G p.6 sec.6.5: VIT+ 396/400/404 mV, VIT- 387/394.5/400 mV,
# INA+ +/-25 nA, INB- +/-15 nA.
VIT_POS = (0.396, 0.400, 0.404)
VIT_NEG = (0.387, 0.3945, 0.400)
# LM5164 SNVSAU4D p.5: VREF 1.181/1.2/1.218 V; Fig 7-1 RFB1 453k, RFB2 49.9k (1 %).
VREF = (1.181, 1.2, 1.218)
R_FB1, R_FB2, R_FB_TOL = 453e3, 49.9e3, 0.01


def _extremes(f):
    return min(f(*c) for c in _corners()), max(f(*c) for c in _corners())


def _corners():
    for t in (1 - R_TOL, 1 + R_TOL):
        for m in (1 - R_TOL, 1 + R_TOL):
            for b in (1 - R_TOL, 1 + R_TOL):
                yield R_TOP * t, R_MID * m, R_BOT * b


def ovp_window():
    """Worst-case PVDD trip points from datasheet threshold limits and resistor tolerance."""
    def ov(vit, i_in):
        return lambda t, m, b: (vit + i_in * b * (t + m) / (t + m + b)) * (t + m + b) / b

    def uv(vit, i_in):
        return lambda t, m, b: (vit + i_in * (m + b) * t / (t + m + b)) * (t + m + b) / (m + b)

    ov_lo = min(_extremes(ov(VIT_POS[0], i))[0] for i in (-15e-9, 15e-9))
    ov_hi = max(_extremes(ov(VIT_POS[2], i))[1] for i in (-15e-9, 15e-9))
    uv_lo = min(_extremes(uv(VIT_NEG[0], i))[0] for i in (-25e-9, 25e-9))
    uv_hi = max(_extremes(uv(VIT_NEG[2], i))[1] for i in (-25e-9, 25e-9))
    total = R_TOP + R_MID + R_BOT
    return {
        "ov_trip_v": [round(ov_lo, 2), round(VIT_POS[1] * total / R_BOT, 2), round(ov_hi, 2)],
        "uv_trip_falling_v": [round(uv_lo, 2), round(VIT_NEG[1] * total / (R_MID + R_BOT), 2), round(uv_hi, 2)],
    }


def aux_output():
    lo = VREF[0] * (1 + R_FB1 * (1 - R_FB_TOL) / (R_FB2 * (1 + R_FB_TOL)))
    hi = VREF[2] * (1 + R_FB1 * (1 + R_FB_TOL) / (R_FB2 * (1 - R_FB_TOL)))
    return [round(lo, 3), round(VREF[1] * (1 + R_FB1 / R_FB2), 3), round(hi, 3)]


def tps3700_symbol():
    # No KiCad stock symbol; pins from TI SBVS187G p.4 (DDC SOT-6).
    pins = [
        ("1", "OUTA", "open_collector", 10.16, 2.54, 180),
        ("2", "GND", "power_in", 0, -7.62, 90),
        ("3", "INA+", "input", -10.16, 2.54, 0),
        ("4", "INB-", "input", -10.16, -2.54, 0),
        ("5", "VDD", "power_in", 0, 7.62, 270),
        ("6", "OUTB", "open_collector", 10.16, -2.54, 180),
    ]
    font = "(effects (font (size 1.27 1.27)))"
    body = " ".join(
        f'(pin {kind} line (at {x} {y} {a}) (length 2.54) (name "{name}" {font}) (number "{n}" {font}))'
        for n, name, kind, x, y, a in pins
    )
    return parse(
        '(symbol "PS28_POWER:TPS3700DDC" (pin_names (offset 1.016)) (in_bom yes) (on_board yes) '
        f'(property "Reference" "U" (at 0 10.16 0) {font}) '
        f'(property "Value" "TPS3700DDC" (at 0 -10.16 0) {font}) '
        f'(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes))) '
        f'(property "Datasheet" "https://www.ti.com/lit/ds/symlink/tps3700.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes))) '
        '(symbol "TPS3700DDC_0_1" (rectangle (start -7.62 5.08) (end 7.62 -5.08) '
        '(stroke (width 0.254) (type default)) (fill (type background)))) '
        f'(symbol "TPS3700DDC_1_1" {body}))'
    )


def parts():
    # (ref, lib_id, value, MPN or requirement, footprint, pin->net)
    specs = [
        ("J301", "Connector_Generic:Conn_01x03", "T1_SECONDARY",
         "TBD: mate original T1 harness (3-way, red-black-red, ~3.96 mm pitch, 20 AWG UL1015); >=8 A/pin", "",
         {"1": "T1_A", "2": "T1_CT", "3": "T1_B"}),
        ("F301", "Device:Fuse", "T8A slow",
         "TBD: time-lag, I2t >= 60 A2s inrush margin, >=63 VDC", "",
         {"1": "T1_CT", "2": "GND"}),
        ("D301", "Device:D", "RECT >=400V",
         "TBD: VRRM>=400 V, IF(AV)>=6 A, IFSM>=200 A", "",
         {"1": "PVDD", "2": "T1_A"}),
        ("D302", "Device:D", "RECT >=400V",
         "TBD: VRRM>=400 V, IF(AV)>=6 A, IFSM>=200 A", "",
         {"1": "PVDD", "2": "T1_B"}),
        ("C301", "Device:C_Polarized", "4700u 63V",
         "TBD: >=63 V, 105 C, ripple >=3.5 A at 120 Hz each", "",
         {"1": "PVDD", "2": "GND"}),
        ("C302", "Device:C_Polarized", "4700u 63V",
         "TBD: >=63 V, 105 C, ripple >=3.5 A at 120 Hz each", "",
         {"1": "PVDD", "2": "GND"}),
        ("R301", "Device:R", "4.7k 2W",
         "TBD: >=1 W continuous at 50 V (0.53 W), >=100 V", "",
         {"1": "PVDD", "2": "GND"}),
        ("D303", "Device:D_TVS", "TVS VWM>=51V",
         "TBD: VWM>=51 V (above 49.8 V worst idle), Vc below 69 V abs max at rated pulse", "",
         {"1": "PVDD", "2": "GND"}),
        ("J302", "Connector_Generic:Conn_01x02", "PVDD_TO_CORE",
         "Logical interface to core J1; same PCB, not a new connector", "",
         {"1": "PVDD", "2": "GND"}),
        # AUX 12 V: TI LM5164 SNVSAU4D Fig 7-1 / Table 7-1 (VIN 15-100 V, 12 V 1 A, 300 kHz).
        ("U302", "Regulator_Switching:LM5164DDA", "LM5164DDA",
         "LM5164DDAR (TI SNVSAU4D Table 7-1); HSOP-8 EP footprint not audited", "",
         {"1": "GND", "2": "PVDD", "3": "PVDD", "4": "BUCK_RON", "5": "BUCK_FB",
          "6": "RAILS_OK", "7": "BUCK_BST", "8": "BUCK_SW", "9": "GND"}),
        ("C310", "Device:C", "2.2u 100V X7R", "CGA6N3X7R2A225K230AB (TI Table 7-1)", "",
         {"1": "PVDD", "2": "GND"}),
        ("C311", "Device:C", "2.2u 100V X7R", "CGA6N3X7R2A225K230AB (TI Table 7-1)", "",
         {"1": "PVDD", "2": "GND"}),
        ("C312", "Device:C", "2.2n 50V X7R", "GCM155R71H222KA37D (TI Table 7-1); 1.5-2.5 nF abs range",
         "", {"1": "BUCK_BST", "2": "BUCK_SW"}),
        ("L301", "Device:L", "68u", "MSS1246T-683MLB (TI Table 7-1); Isat above 1.5 A limit", "",
         {"1": "BUCK_SW", "2": "AUX_RAW"}),
        ("R310", "Device:R", "100k 1%", "RG1608P-1053-B-T5 (TI Table 7-1); FSW 300 kHz", "",
         {"1": "BUCK_RON", "2": "GND"}),
        ("R311", "Device:R", "453k 1%",
         "TBD: TI Table 7-1 lists RT0603BRD07448KL (448k) against value 453k; resolve before BOM", "",
         {"1": "AUX_RAW", "2": "BUCK_FB"}),
        ("R312", "Device:R", "49.9k 1%", "RG1608P-4992-B-T5 (TI Table 7-1)", "",
         {"1": "BUCK_FB", "2": "GND"}),
        ("R313", "Device:R", "453k 1%", "RT0603BRD07453KL (TI Table 7-1); RA type-3 ripple", "",
         {"1": "BUCK_SW", "2": "BUCK_RAMP"}),
        ("C313", "Device:C", "3.3n", "CGA3E2X7R2A332K080AA (TI Table 7-1); CA", "",
         {"1": "BUCK_RAMP", "2": "AUX_RAW"}),
        ("C314", "Device:C", "56p", "C0603C560J5GACTU (TI Table 7-1); CB", "",
         {"1": "BUCK_RAMP", "2": "BUCK_FB"}),
        ("C315", "Device:C", "22u 25V X7R", "TMK325B7226KMHT (TI Table 7-1)", "",
         {"1": "AUX_RAW", "2": "GND"}),
        ("C316", "Device:C", "22u 25V X7R", "TMK325B7226KMHT (TI Table 7-1)", "",
         {"1": "AUX_RAW", "2": "GND"}),
        # PVDD window: OUTB low above OV, OUTA low below UV; wired-AND with buck PGOOD.
        ("U303", "PS28_POWER:TPS3700DDC", "TPS3700DDC",
         "TPS3700DDCR (TI SBVS187G p.23 package option addendum); SOT-23-6 footprint not audited", "",
         {"1": "RAILS_OK", "2": "GND", "3": "PVDD_UV_SENSE", "4": "PVDD_OV_SENSE",
          "5": "AUX_RAW", "6": "RAILS_OK"}),
        ("R320", "Device:R", "931k 0.1%", "TBD: 0.1 %, <=25 ppm/K, >=100 V working (sees ~50 V)", "",
         {"1": "PVDD", "2": "PVDD_UV_SENSE"}),
        ("R321", "Device:R", "6.04k 0.1%", "TBD: 0.1 %, <=25 ppm/K", "",
         {"1": "PVDD_UV_SENSE", "2": "PVDD_OV_SENSE"}),
        ("R322", "Device:R", "7.32k 0.1%", "TBD: 0.1 %, <=25 ppm/K", "",
         {"1": "PVDD_OV_SENSE", "2": "GND"}),
        ("C320", "Device:C", "100n", "TBD: X7R >=25 V (SBVS187G p.4 VDD bypass)", "",
         {"1": "AUX_RAW", "2": "GND"}),
        ("R323", "Device:R", "100k", "TBD: pull-up; SEQ_LOGIC_VCC <=14 V (LM5164 PGOOD abs max)", "",
         {"1": "SEQ_LOGIC_VCC", "2": "RAILS_OK"}),
        ("J303", "Connector_Generic:Conn_01x04", "AUX_TO_CORE",
         "Logical interface: AUX_RAW to core J2, RAILS_OK into D-020 rails_valid; same PCB", "",
         {"1": "AUX_RAW", "2": "RAILS_OK", "3": "SEQ_LOGIC_VCC", "4": "GND"}),
    ]
    return [
        {"ref": r, "lib_id": lib, "value": v, "mpn": m, "footprint": fp, "nets": n,
         "units": [(1, 38.1 + (i % 6) * 63.5, 45.72 + (i // 6) * 40.64)]}
        for i, (r, lib, v, m, fp, n) in enumerate(specs)
    ]


def generate(out):
    if out.exists():
        raise FileExistsError("Refusing to overwrite existing power capture")
    out.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix=".power-d021-", dir=out.parent))
    try:
        sch, manifest = build(
            parts(),
            project="power-d021",
            namespace="power-d021",
            source=SOURCE,
            title="PS28 D-021 POWER - STUDY ONLY",
            warning="NEVER BRIDGE T1_A-T1_B (~97 V). FOOTPRINTS AND MOST PASSIVE MPNs TBD. RAILS_OK IS NOT A DIRECT RESET DRIVE.",
            power_flags=("PVDD", "GND", "AUX_RAW"),
            extra_symbols={"PS28_POWER:TPS3700DDC": tps3700_symbol()},
        )
        manifest["interface_contract"] = {
            "J301": "1=red A, 2=black CT, 3=red B; order photo-confirmed 2026-10-09; ~3.96 mm pitch measured; header series/rating TBD",
            "J302": "PVDD 40-50 V unregulated to core J1; core C14/C15 3000 uF add to C301/C302",
            "J303": "AUX_RAW 12 V to core J2; RAILS_OK open-drain wired-AND (buck PGOOD, PVDD UV, PVDD OV), low = fault, feeds D-020 rails_valid",
            "not_captured": ["inrush limiting (NTC or bypass relay)", "sequencer logic supply SEQ_LOGIC_VCC"],
            "new_physical_board": False,
        }
        manifest["calculated"] = {
            "pvdd_window": ovp_window(),
            "aux_raw_v": aux_output(),
            "sources": "TI SBVS187G p.6 sec.6.5; TI SNVSAU4D p.5 VREF and Fig 7-1",
        }
        (staged / "power-d021.kicad_sch").write_text(sch)
        (staged / "power-d021.kicad_pro").write_text("{}\n")
        library = tps3700_symbol()
        library[1] = q("TPS3700DDC")
        (staged / "libraries").mkdir()
        (staged / "libraries/PS28_POWER.kicad_sym").write_text(
            '(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '
            + render(library) + ")\n"
        )
        (staged / "sym-lib-table").write_text(
            '(sym_lib_table (version 7) (lib (name "PS28_POWER") (type "KiCad") '
            '(uri "${KIPRJMOD}/libraries/PS28_POWER.kicad_sym") (options "") '
            '(descr "Local symbol; TI TPS3700 SBVS187G p.4 DDC pinout")))\n'
        )
        (staged / "power-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        staged.rename(out)
    except BaseException:
        shutil.rmtree(staged, ignore_errors=True)
        raise


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=DESIGN)
    generate(p.parse_args().output)
