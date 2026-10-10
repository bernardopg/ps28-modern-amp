#!/usr/bin/env python3
"""Capture the D-019 TPA input interface (D-024); never overwrite existing designs.

Per branch: Form C relay contact after C20/C21 (COM = isolated plate, NC = discharge,
NO = TPA pin), pin-side capacitor, DC window (TPS3700) observing both pins, plus
analog mute (TMUX6219 shunting DIVIDED to VMID), AUX window and relay/mute drivers.
Primary sources and limits in docs/iso-d019.md. Study only; no hardware sign-off.
"""

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from create_analog_capture import build
from create_power_d021 import local_symbol, tps3700_symbol, window3, write_local_library
from simulate_opa1656 import ROOT

DESIGN = ROOT / "kicad/iso-d019"
SOURCE = "D-024: D-019 relay isolation, mute and DC observation; study only"

SOT23 = "Package_TO_SOT_SMD:SOT-23"
SOT6 = "Package_TO_SOT_SMD:SOT-23-6"
SOD123 = "Diode_SMD:D_SOD-123"
R0603 = "Resistor_SMD:R_0603_1608Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"

# Pin DC window per branch: INPUT_x-R_top-UV-R_mid-OV-R_bot-GND (0.1 %), also the
# pin-side return (~0.98 Mohm) when the contact is open.
PIN_DIVIDER = (787e3, 115e3, 78.7e3)
# AUX_RAW window: TPA VDD/GVDD 10.8-13.2 V (SLASEA8A sec.7.3) vs AUX 11.69-12.50 V.
AUX_DIVIDER = (357e3, 1.5e3, 11.5e3)
# Omron G6K Cat. No. K106-E1-11 p.3: operate and release 3 ms max each.
RELAY_OPERATE_MAX_S = 3e-3
RELAY_RELEASE_MAX_S = 3e-3


# Tap filter time constants (Thevenin of the divider at each tap times its capacitor).
TAP_TAU_S = {
    "uv": (PIN_DIVIDER[0] * (PIN_DIVIDER[1] + PIN_DIVIDER[2]) / sum(PIN_DIVIDER)) * 330e-9,
    "ov": (PIN_DIVIDER[2] * (PIN_DIVIDER[0] + PIN_DIVIDER[1]) / sum(PIN_DIVIDER)) * 680e-9,
}


def windows():
    return {"pin_dc": window3(*PIN_DIVIDER, digits=3), "aux_raw": window3(*AUX_DIVIDER, digits=3)}


def dgk_footprint():
    # TI DGK0008A land pattern, SCDS420E p.50: 8x 1.4 x 0.45 mm, pitch 0.65, centers 4.4 mm.
    pads = "\n".join(
        f'(pad "{n}" smd roundrect(at {x} {y})(size 1.4 0.45)(layers "F.Cu" "F.Paste" "F.Mask")(roundrect_rratio 0.11))'
        for n, x, y in [(1, -2.2, -0.975), (2, -2.2, -0.325), (3, -2.2, 0.325), (4, -2.2, 0.975),
                        (5, 2.2, 0.975), (6, 2.2, 0.325), (7, 2.2, -0.325), (8, 2.2, -0.975)]
    )
    return f"""(footprint "TI_DGK0008A" (version 20241229) (generator "ps28")
(layer "F.Cu") (attr smd)
(descr "TI DGK0008A VSSOP-8 example board layout, SCDS420E p.50; nominal body 3x3 mm")
(property "Reference" "REF**" (at 0 -2.6 0) (layer "F.SilkS") (effects(font(size 1 1)(thickness 0.15))))
(property "Value" "TI_DGK0008A" (at 0 2.6 0) (layer "F.Fab") (effects(font(size 1 1)(thickness 0.15))))
(fp_rect(start -1.5 -1.5)(end 1.5 1.5)(stroke(width 0.1)(type default))(fill none)(layer "F.Fab"))
(fp_rect(start -3.15 -1.75)(end 3.15 1.75)(stroke(width 0.05)(type default))(fill none)(layer "F.CrtYd"))
(fp_circle(center -1.0 -1.0)(end -0.85 -1.0)(stroke(width 0.1)(type default))(fill none)(layer "F.Fab"))
{pads}
(model "${{KICAD10_3DMODEL_DIR}}/Package_SO.3dshapes/MSOP-8_3x3mm_P0.65mm.step" (offset(xyz 0 0 0))(scale(xyz 1 1 1))(rotate(xyz 0 0 0))))\n"""


def tmux6219_symbol():
    # TI SCDS420E p.3 Table 4-1, DGK (VSSOP-8).
    return local_symbol("PS28_ISO:TMUX6219DGK", [
        ("1", "D", "passive", -10.16, 2.54, 0),
        ("2", "S1", "passive", -10.16, 0, 0),
        ("3", "GND", "power_in", 0, -7.62, 90),
        ("4", "VDD", "power_in", 0, 7.62, 270),
        ("5", "EN", "input", 10.16, 2.54, 180),
        ("6", "SEL", "input", 10.16, 0, 180),
        ("7", "VSS", "power_in", 2.54, -7.62, 90),
        ("8", "S2", "passive", -10.16, -2.54, 0),
    ], "https://www.ti.com/lit/ds/symlink/tmux6219.pdf")


def mmbt3904_symbol():
    # Diodes DS30036 Rev.27 p.1 SOT23 pinout: 1 B, 2 E, 3 C (top view).
    return local_symbol("PS28_ISO:MMBT3904", [
        ("1", "B", "input", -10.16, 0, 0),
        ("2", "E", "passive", 0, -7.62, 90),
        ("3", "C", "passive", 0, 7.62, 270),
    ], "https://www.diodes.com/assets/Datasheets/ds30036.pdf", half_width=5.08)


def window_part(ref, net, uv, ov, out, role):
    return (ref, "PS28_POWER:TPS3700DDC", "TPS3700DDC", f"TPS3700DDCR (TI SBVS187G); {role}", SOT6,
            {"1": out, "2": "GND", "3": uv, "4": ov, "5": "AUX_RAW", "6": out})


def divider(refs, top_net, uv, ov, values, note):
    a, b, c = refs
    return [
        (a, "Device:R", values[0], f"TBD: 0.1 %, <=25 ppm/K; {note}", R0603, {"1": top_net, "2": uv}),
        (b, "Device:R", values[1], f"TBD: 0.1 %, <=25 ppm/K; {note}", R0603, {"1": uv, "2": ov}),
        (c, "Device:R", values[2], f"TBD: 0.1 %, <=25 ppm/K; {note}", R0603, {"1": ov, "2": "GND"}),
    ]


def parts():
    specs = [
        # Isolation relay, both branches; unpowered = isolated and discharging (Form C, BBM).
        ("K501", "Relay:G6K-2", "G6K-2F DC12",
         "G6K-2F DC12 (Omron K106-E1-11 p.2-3: 1315 ohm, 3 ms operate/release max, Au alloy)",
         "Relay_SMD:Relay_DPDT_Omron_G6K-2F",
         {"1": "AUX_RAW", "8": "RELAY_DRV", "3": "INA_ISO", "2": "INA_DIS", "4": "INA_NO",
          "6": "INB_ISO", "7": "INB_DIS", "5": "INB_NO"}),
        # Single-fault mitigation: series R + Schottky clamp at the TPA pin bounds a driver
        # failing low to about -VF (BAT54 DS11005 p.2: <=240 mV at 0.1 mA, <=320 mV at 1 mA).
        ("R517", "Device:R", "3.3k", "TBD: 1 %, thin film; RIN 10/20/40k => -2.48/-1.33/-0.69 dB", R0603,
         {"1": "INA_NO", "2": "INPUT_A_AC"}),
        ("R518", "Device:R", "3.3k", "TBD: 1 %, thin film; RIN 10/20/40k => -2.48/-1.33/-0.69 dB", R0603,
         {"1": "INB_NO", "2": "INPUT_B_AC"}),
        ("D503", "PS28_ISO:BAT54", "BAT54", "BAT54-7-F (Diodes DS11005 Rev.34)", SOT23,
         {"1": "GND", "2": None, "3": "INPUT_A_AC"}),
        ("D504", "PS28_ISO:BAT54", "BAT54", "BAT54-7-F (Diodes DS11005 Rev.34)", SOT23,
         {"1": "GND", "2": None, "3": "INPUT_B_AC"}),
        ("Q501", "PS28_ISO:MMBT3904", "MMBT3904",
         "MMBT3904-7-F (Diodes DS30036): VCEsat <=0.2 V at 10 mA/1 mA, VCEO 40 V", SOT23,
         {"1": "RELAY_BASE", "2": "GND", "3": "RELAY_DRV"}),
        ("R501", "Device:R", "2.2k", "TBD: 1 %; IB >=1.0 mA from 3.3 V (VBEsat 0.85 V max)", R0603,
         {"1": "RUN", "2": "RELAY_BASE"}),
        ("R502", "Device:R", "100k", "TBD: base pull-down, relay off without logic", R0603,
         {"1": "RELAY_BASE", "2": "GND"}),
        ("D501", "Device:D", "1N4148W", "1N4148W-7-F (Diodes DS30086)", SOD123,
         {"1": "RELAY_FLY", "2": "RELAY_DRV"}),
        ("D502", "Device:D_Zener", "BZT52C15", "BZT52C15-7-F (Diodes DS18004): 13.8-15.6 V; faster release", SOD123,
         {"1": "RELAY_FLY", "2": "AUX_RAW"}),
        # Isolated side: NC discharge only when the plate is disconnected from the pin.
        ("R503", "Device:R", "1k", "TBD: 1 %, >=0.1 W; tau 10 ms with 10 uF", R0603, {"1": "INA_DIS", "2": "GND"}),
        ("R504", "Device:R", "1k", "TBD: 1 %, >=0.1 W; tau 10 ms with 10 uF", R0603, {"1": "INB_DIS", "2": "GND"}),
        # Pin side: defined capacitance (contract >=4 nF).
        ("C503", "Device:C", "4.7n C0G", "TBD: C0G/NP0 >=50 V", C0603, {"1": "INPUT_A_AC", "2": "GND"}),
        ("C504", "Device:C", "4.7n C0G", "TBD: C0G/NP0 >=50 V", C0603, {"1": "INPUT_B_AC", "2": "GND"}),
        # DC observation of both TPA pins: OUTA low < ~2 V, OUTB low > ~5 V; low = not valid.
        window_part("U501", "INPUT_A_AC", "INA_UV", "INA_OV", "DC_OK", "INPUT_A DC window"),
        window_part("U502", "INPUT_B_AC", "INB_UV", "INB_OV", "DC_OK", "INPUT_B DC window"),
        *divider(("R505", "R506", "R507"), "INPUT_A_AC", "INA_UV", "INA_OV", ("787k", "115k", "78.7k"),
                 "pin DC window and return"),
        *divider(("R508", "R509", "R510"), "INPUT_B_AC", "INB_UV", "INB_OV", ("787k", "115k", "78.7k"),
                 "pin DC window and return"),
        # Tap filters: tau ~50 ms (Thevenin ~155k / ~72k) so 20 Hz audio (<=1.556 V pk at the pin)
        # leaves <=0.24 V on the DC estimate; requires a subsonic HPF in the front-end (ELEC-002).
        ("C509", "Device:C", "330n", "TBD: X7R >=16 V; UV tap filter", C0603, {"1": "INA_UV", "2": "GND"}),
        ("C510", "Device:C", "680n", "TBD: X7R >=16 V; OV tap filter", C0603, {"1": "INA_OV", "2": "GND"}),
        ("C511", "Device:C", "330n", "TBD: X7R >=16 V; UV tap filter", C0603, {"1": "INB_UV", "2": "GND"}),
        ("C512", "Device:C", "680n", "TBD: X7R >=16 V; OV tap filter", C0603, {"1": "INB_OV", "2": "GND"}),
        # AUX_RAW window: independent of LM5164 PGOOD (undefined if the buck is dead).
        window_part("U504", "AUX_RAW", "AUX_UV", "AUX_OV", "RAILS_OK", "AUX_RAW window"),
        *divider(("R514", "R515", "R516"), "AUX_RAW", "AUX_UV", "AUX_OV", ("357k", "1.5k", "11.5k"),
                 "AUX window"),
        # Analog mute: EN high (default, internal 4 M pull-up + R511) shunts DIVIDED to VMID.
        ("U503", "PS28_ISO:TMUX6219DGK", "TMUX6219",
         "TMUX6219DGKR (TI SCDS420E p.39); RON <=7.5 ohm at 12 V single supply (p.10)",
         "PS28_ANALOG:TI_DGK0008A",  # TI SCDS420E p.50 land pattern
         {"1": "DIVIDED", "2": "VMID", "3": "GND", "4": "ANALOG_12V", "5": "MUTE_EN", "6": "GND",
          "7": "GND", "8": "GND"}),
        ("R511", "Device:R", "100k", "TBD: EN pull-up to ANALOG_12V (default muted)", R0603,
         {"1": "ANALOG_12V", "2": "MUTE_EN"}),
        ("Q502", "PS28_ISO:MMBT3904", "MMBT3904", "MMBT3904-7-F (Diodes DS30036); unmute pull-down", SOT23,
         {"1": "MUTE_BASE", "2": "GND", "3": "MUTE_EN"}),
        ("R512", "Device:R", "10k", "TBD: 1 %", R0603, {"1": "AUDIO_EN", "2": "MUTE_BASE"}),
        ("R513", "Device:R", "100k", "TBD: base pull-down, muted without logic", R0603,
         {"1": "MUTE_BASE", "2": "GND"}),
        ("C505", "Device:C", "100n", "TBD: X7R >=25 V; U503 VDD (SCDS420E Table 4-1)", C0603,
         {"1": "ANALOG_12V", "2": "GND"}),
        ("C506", "Device:C", "100n", "TBD: X7R >=25 V; U501 VDD", C0603, {"1": "AUX_RAW", "2": "GND"}),
        ("C507", "Device:C", "100n", "TBD: X7R >=25 V; U502 VDD", C0603, {"1": "AUX_RAW", "2": "GND"}),
        ("C508", "Device:C", "100n", "TBD: X7R >=25 V; U504 VDD", C0603, {"1": "AUX_RAW", "2": "GND"}),
        ("J501", "Connector_Generic:Conn_01x13", "ISO_TO_SYSTEM",
         "Logical interface to core/analog/seq; same PCB, not a connector", "",
         {"1": "AUX_RAW", "2": "ANALOG_12V", "3": "VMID", "4": "DIVIDED", "5": "RUN", "6": "AUDIO_EN",
          "7": "DC_OK", "8": "RAILS_OK", "9": "INA_ISO", "10": "INB_ISO", "11": "INPUT_A_AC",
          "12": "INPUT_B_AC", "13": "GND"}),
    ]
    return [
        {"ref": r, "lib_id": lib, "value": v, "mpn": m, "footprint": fp, "nets": n,
         "units": [(1, 38.1 + (i % 6) * 63.5, 45.72 + (i // 6) * 40.64)]}
        for i, (r, lib, v, m, fp, n) in enumerate(specs)
    ]


def bat54_symbol():
    # Diodes DS11005 Rev.34 p.1 SOT23 (standard) top view: 1 anode, 3 cathode, 2 NC.
    return local_symbol("PS28_ISO:BAT54", [
        ("1", "A", "passive", -10.16, 0, 0),
        ("2", "NC", "no_connect", 0, -7.62, 90),
        ("3", "K", "passive", 10.16, 0, 180),
    ], "https://www.diodes.com/assets/Datasheets/ds11005.pdf", half_width=5.08)


def local_symbols():
    return [tmux6219_symbol(), mmbt3904_symbol(), bat54_symbol()]


def generate(out):
    if out.exists():
        raise FileExistsError("Refusing to overwrite existing D-019 capture")
    out.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix=".iso-d019-", dir=out.parent))
    try:
        sch, manifest = build(
            parts(),
            project="iso-d019",
            namespace="iso-d019",
            source=SOURCE,
            title="PS28 D-019 INPUT ISOLATION / MUTE / DC OBSERVATION - STUDY ONLY",
            warning="RELAY UNPOWERED = ISOLATED + DISCHARGING. SINGLE-FAULT (PREAMP RAIL/DRIVER SHORT) NOT COVERED. DO NOT ENERGIZE.",
            power_flags=("GND", "AUX_RAW", "ANALOG_12V"),
            extra_symbols={"PS28_POWER:TPS3700DDC": tps3700_symbol(),
                           **{s[1].strip('"'): s for s in local_symbols()}},
        )
        manifest["calculated"] = {
            "windows_v": windows(),
            "relay_operate_release_max_s": [RELAY_OPERATE_MAX_S, RELAY_RELEASE_MAX_S],
            "sources": "TI SBVS187G p.6; Omron K106-E1-11 p.3; TI SLASEA8A sec.7.3",
        }
        manifest["interface_contract"] = {
            "C20/C21": "plate side becomes INA_ISO/INB_ISO (relay COM); TPA pins stay INPUT_A_AC/INPUT_B_AC (relay NO)",
            "RUN": "relay drive (seq-d020 U406 Q)", "AUDIO_EN": "unmute (seq-d020 audio latch)",
            "DC_OK": "open-drain from U501/U502 into seq-d020 dwell; pull-up in seq",
            "RAILS_OK": "U504 AUX window joins the wired-AND",
            "new_physical_board": False,
        }
        (staged / "iso-d019.kicad_sch").write_text(sch)
        (staged / "iso-d019.kicad_pro").write_text("{}\n")
        write_local_library(staged, "PS28_ISO", local_symbols(),
                            "Local symbols; TI SCDS420E Table 4-1, Diodes DS30036 pinout")
        (staged / "libraries/PS28_POWER.kicad_sym").write_text(
            (ROOT / "kicad/power-d021/libraries/PS28_POWER.kicad_sym").read_text()
        )
        (staged / "sym-lib-table").write_text(
            (staged / "sym-lib-table").read_text().rstrip()[:-1]
            + '(lib (name "PS28_POWER") (type "KiCad") (uri "${KIPRJMOD}/libraries/PS28_POWER.kicad_sym") '
            '(options "") (descr "Local symbol; TI TPS3700 SBVS187G p.4")))\n'
        )
        (staged / "libraries/PS28_ANALOG.pretty").mkdir()
        (staged / "libraries/PS28_ANALOG.pretty/TI_DGK0008A.kicad_mod").write_text(dgk_footprint())
        (staged / "fp-lib-table").write_text(
            '(fp_lib_table (version 7) (lib (name "PS28_ANALOG") (type "KiCad") '
            '(uri "${KIPRJMOD}/libraries/PS28_ANALOG.pretty") (options "") (descr "TI DGK0008A SCDS420E p.50")))\n'
        )
        (staged / "iso-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        staged.rename(out)
    except BaseException:
        shutil.rmtree(staged, ignore_errors=True)
        raise


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=DESIGN)
    generate(p.parse_args().output)
