#!/usr/bin/env python3
"""Capture the discrete (no-MCU) D-020 sequencing subset; never overwrite.

Implements rails qualification hold (two TPS3808 stages, >=360 ms), human start edge,
CLIP_OTW start permission, FAULT arming/latching with human re-arm, a start timeout
and (D-024) connect-before-RESET delay, DC dwell and audio latch. The relay, mute
and DC windows themselves live in kicad/iso-d019. Sources in docs/seq-d020.md.
"""

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from create_analog_capture import build
from create_power_d021 import VIT_NEG, VIT_POS, local_symbol, tps3700_symbol, write_local_library
from simulate_opa1656 import ROOT

DESIGN = ROOT / "kicad/seq-d020"
SOURCE = "D-020 discrete sequencing subset; study only; D-019 bridge still open"

SOT5 = "Package_TO_SOT_SMD:SOT-23-5"
SOT6 = "Package_TO_SOT_SMD:SOT-23-6"
DCT = "Package_SO:SSOP-8_2.95x2.8mm_P0.65mm"
R0603 = "Resistor_SMD:R_0603_1608Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"


# Analog rail windows (contract reset-supervisor: verify AUX_RAW AND ANALOG_12V/VMID).
# (net, kind, R_top, R_bottom); 0.1 % parts; TPS3700 VIT SBVS187G p.6.
WINDOWS = {
    "ANALOG_UV": ("ANALOG_12V", "uv", 1e6, 46.4e3),
    "ANALOG_OV": ("ANALOG_12V", "ov", 1e6, 30.1e3),
    "VMID_UV": ("VMID", "uv", 909e3, 101e3),
    "VMID_OV": ("VMID", "ov", 1e6, 64.9e3),
}


def window_thresholds(tol=0.001):
    """Worst-case trip voltages: rising OV (VIT+), falling UV (VIT-), divider tolerance."""
    out = {}
    for name, (_, kind, top, bot) in WINDOWS.items():
        vit = VIT_POS if kind == "ov" else VIT_NEG
        ratios = [(1 + top * a / (bot * b)) for a in (1 - tol, 1 + tol) for b in (1 - tol, 1 + tol)]
        out[name] = [round(vit[0] * min(ratios), 3), round(vit[1] * (1 + top / bot), 3),
                     round(vit[2] * max(ratios), 3)]
    return out


def lp2985_symbol():
    # KiCad LP2985-3.3 uses inheritance (unsupported); pins from TI SLVS522S Table 4-1.
    return local_symbol("PS28_SEQ:LP2985-33DBV", [
        ("1", "VIN", "power_in", -10.16, 2.54, 0),
        ("2", "GND", "power_in", 0, -7.62, 90),
        ("3", "ON/OFF", "input", -10.16, -2.54, 0),
        ("4", "BYPASS", "passive", 10.16, -2.54, 180),
        ("5", "VOUT", "power_out", 10.16, 2.54, 180),
    ], "https://www.ti.com/lit/ds/symlink/lp2985.pdf")


def supervisor(ref, mr, ct_net, reset, role):
    return (ref, "Power_Supervisor:TPS3808DBV", "TPS3808G33",
            f"TPS3808G33DBVR (TI SBVS050N); {role}", SOT6,
            {"1": reset, "2": "GND", "3": mr, "4": ct_net, "5": "SEQ_3V3", "6": "SEQ_3V3"})  # ct_net None = open


def flip_flop(ref, clk, d, q, qn, clr, role):
    return (ref, "74xGxx:74LVC2G74", "74LVC2G74", f"SN74LVC2G74DCTR (TI SCES203Q); {role}",
            DCT, {"1": clk, "2": d, "3": qn, "4": "GND", "5": q, "6": clr,
                  "7": "SEQ_3V3", "8": "SEQ_3V3"})


def gate(ref, name, mpn, nets):
    full = {"3": "GND", "5": "SEQ_3V3", **nets}
    return (ref, f"74xGxx:{name}", name, mpn, SOT5, full)


def bypass(ref, note="VCC bypass"):
    return (ref, "Device:C", "100n", f"TBD: X7R >=10 V; {note}", C0603,
            {"1": "SEQ_3V3", "2": "GND"})


def parts():
    specs = [
        # Logic supply: AUX_RAW (11.7-12.5 V) -> 3.3 V. TPA RESET abs max 4.2 V (SLASEA8A p.6).
        ("U401", "PS28_SEQ:LP2985-33DBV", "LP2985-33",
         "LP2985-33DBVR (TI SLVS522S p.33 orderable); VIN 16 V max", SOT5,
         {"1": "AUX_RAW", "2": "GND", "3": "AUX_RAW", "4": "SEQ_BYP", "5": "SEQ_3V3"}),
        ("C401", "Device:C", "1u 25V", "TBD: X7R >=25 V; CIN >=1 uF (SLVS522S Table 4-1)", C0603,
         {"1": "AUX_RAW", "2": "GND"}),
        ("C402", "Device:C", "10n", "TBD: X7R; CBYPASS 10 nF (SLVS522S)", C0603,
         {"1": "SEQ_BYP", "2": "GND"}),
        ("C403", "Device:C", "2.2u 10V", "TBD: X7R, >=1 uF effective, ESR <=1 ohm new die", C0603,
         {"1": "SEQ_3V3", "2": "GND"}),
        # Rails hold: RAILS_OK (power-good, PVDD window and trips, wired-AND) -> 2 x 180..420 ms.
        supervisor("U402", "RAILS_OK", "SEQ_CT1", "SEQ_HOLD1", "hold stage 1, CT to VDD"),
        ("R401", "Device:R", "100k", "TBD: 1 %; CT to VDD 40-200k => 180/300/420 ms", R0603,
         {"1": "SEQ_3V3", "2": "SEQ_CT1"}),
        ("R402", "Device:R", "100k", "TBD: RESET pull-up 10k-1M (SBVS050N Table 5-1)", R0603,
         {"1": "SEQ_3V3", "2": "SEQ_HOLD1"}),
        supervisor("U403", "SEQ_HOLD1", "SEQ_CT2", "RAILS_QUAL", "hold stage 2, CT to VDD"),
        ("R403", "Device:R", "100k", "TBD: 1 %; CT to VDD", R0603, {"1": "SEQ_3V3", "2": "SEQ_CT2"}),
        ("R404", "Device:R", "100k", "TBD: RESET pull-up", R0603, {"1": "SEQ_3V3", "2": "RAILS_QUAL"}),
        # Start timeout: MR high only while running AND not armed; CT 180 nF => 0.62-1.44 s.
        supervisor("U404", "START_WIN", "SEQ_CT3", "START_TIMEOUT", "start timeout, CT 180 nF"),
        ("C404", "Device:C", "180n", "TBD: C0G/X7R low leakage; CT 180 nF => 0.62-1.44 s", C0603,
         {"1": "SEQ_CT3", "2": "GND"}),
        ("R405", "Device:R", "100k", "TBD: RESET pull-up", R0603, {"1": "SEQ_3V3", "2": "START_TIMEOUT"}),
        # Human start: momentary switch to GND, RC debounce, inverting Schmitt => rising on press.
        ("J401", "Connector_Generic:Conn_01x02", "START_BUTTON",
         "TBD: panel momentary switch harness; location/mechanics not decided",
         "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
         {"1": "START_BTN", "2": "GND"}),
        ("R406", "Device:R", "100k", "TBD: button pull-up", R0603, {"1": "SEQ_3V3", "2": "START_BTN"}),
        ("R407", "Device:R", "10k", "TBD: debounce series; press tau 10 ms", R0603,
         {"1": "START_BTN", "2": "START_DEB"}),
        ("C405", "Device:C", "1u", "TBD: X7R; release tau ~110 ms", C0603, {"1": "START_DEB", "2": "GND"}),
        gate("U405", "74LVC1G14", "SN74LVC1G14DBVR (TI SCES218AA)",
             {"1": None, "2": "START_DEB", "4": "START_EDGE"}),
        # RUN flip-flop: start edge latches CLIP_OTW (contract: otw_high) while RAILS_QUAL high.
        flip_flop("U406", "START_EDGE", "CLIP_OTW", "RUN", None, "RAILS_QUAL", "RUN latch"),
        # D-024: RESET released 12-28 ms (CT open) after RUN closes the relay (3 ms max).
        supervisor("U414", "RUN", None, "RESET_GO", "connect-before-reset delay, CT open"),
        ("R428", "Device:R", "100k", "TBD: RESET pull-up", R0603, {"1": "SEQ_3V3", "2": "RESET_GO"}),
        ("R408", "Device:R", "1k", "TBD: series to TPA RESET; with R9 4.7k gives >=2.6 V (VIH 1.9 V)", R0603,
         {"1": "RESET_GO", "2": "RESET"}),
        # ARMED flip-flop: FAULT rising edge after RESET release (contract START_AVDD).
        flip_flop("U407", "FAULT", "RUN", "ARMED", "NOT_ARMED", "RUN", "FAULT arming"),
        gate("U408", "74LVC1G32", "SN74LVC1G32DBVR (TI SCES219W)",
             {"1": "NOT_ARMED", "2": "FAULT", "4": "FAULT_TRIP_N"}),
        gate("U409", "74LVC1G07", "SN74LVC1G07DBVR (TI SCES296AG); open-drain trip into RAILS_OK",
             {"1": None, "2": "FAULT_TRIP_N", "4": "RAILS_OK"}),
        gate("U410", "74LVC1G08", "SN74LVC1G08DBVR (TI SCES217AA)",
             {"1": "RUN", "2": "NOT_AUDIO", "4": "START_WIN"}),
        gate("U411", "74LVC1G06", "SN74LVC1G06DBVR (TI SCES295AB); open-drain timeout trip",
             {"2": "START_TIMEOUT", "4": "RAILS_OK"}),
        bypass("C406", "U402"), bypass("C407", "U403"), bypass("C408", "U404"),
        bypass("C409", "U405"), bypass("C410", "U406"), bypass("C411", "U407"),
        bypass("C412", "U408"), bypass("C413", "U409"), bypass("C414", "U410"),
        bypass("C415", "U411"),
        # D-024 precharge observation: both pins in the 2-5 V window, after arming, for
        # 12-28 ms continuous (CT open), latches AUDIO_EN (unmute). DC loss after that trips.
        ("R429", "Device:R", "100k", "TBD: DC_OK pull-up (open-drain from iso-d019 U501/U502)", R0603,
         {"1": "SEQ_3V3", "2": "DC_OK"}),
        gate("U415", "74LVC1G08", "SN74LVC1G08DBVR (TI SCES217AA)",
             {"1": "ARMED", "2": "DC_OK", "4": "DC_GATE"}),
        supervisor("U416", "DC_GATE", None, "DWELL_OK", "DC dwell, CT open"),
        ("R430", "Device:R", "100k", "TBD: RESET pull-up", R0603, {"1": "SEQ_3V3", "2": "DWELL_OK"}),
        flip_flop("U417", "DWELL_OK", "SEQ_3V3", "AUDIO_EN", "NOT_AUDIO", "RUN", "AUDIO latch"),
        gate("U418", "74LVC1G32", "SN74LVC1G32DBVR (TI SCES219W)",
             {"1": "NOT_AUDIO", "2": "DC_OK", "4": "DC_TRIP_N"}),
        gate("U419", "74LVC1G07", "SN74LVC1G07DBVR (TI SCES296AG); open-drain DC trip into RAILS_OK",
             {"1": None, "2": "DC_TRIP_N", "4": "RAILS_OK"}),
        bypass("C418", "U414"), bypass("C419", "U415"), bypass("C420", "U416"),
        bypass("C421", "U417"), bypass("C422", "U418"), bypass("C423", "U419"),
        # Analog rails into RAILS_OK: OUTA low below UV, OUTB low above OV (SBVS187G p.4).
        ("U412", "PS28_POWER:TPS3700DDC", "TPS3700DDC", "TPS3700DDCR (TI SBVS187G); ANALOG_12V window", SOT6,
         {"1": "RAILS_OK", "2": "GND", "3": "ANALOG_UV", "4": "ANALOG_OV", "5": "AUX_RAW", "6": "RAILS_OK"}),
        ("U413", "PS28_POWER:TPS3700DDC", "TPS3700DDC", "TPS3700DDCR (TI SBVS187G); VMID window", SOT6,
         {"1": "RAILS_OK", "2": "GND", "3": "VMID_UV", "4": "VMID_OV", "5": "AUX_RAW", "6": "RAILS_OK"}),
        *[
            (ref, "Device:R", value, "TBD: 0.1 %, <=25 ppm/K", R0603, nets)
            for ref, value, nets in [
                ("R420", "1M", {"1": "ANALOG_12V", "2": "ANALOG_UV"}),
                ("R421", "46.4k", {"1": "ANALOG_UV", "2": "GND"}),
                ("R422", "1M", {"1": "ANALOG_12V", "2": "ANALOG_OV"}),
                ("R423", "30.1k", {"1": "ANALOG_OV", "2": "GND"}),
                ("R424", "909k", {"1": "VMID", "2": "VMID_UV"}),
                ("R425", "101k", {"1": "VMID_UV", "2": "GND"}),
                ("R426", "1M", {"1": "VMID", "2": "VMID_OV"}),
                ("R427", "64.9k", {"1": "VMID_OV", "2": "GND"}),
            ]
        ],
        ("C416", "Device:C", "100n", "TBD: X7R >=25 V; U412 VDD", C0603, {"1": "AUX_RAW", "2": "GND"}),
        ("C417", "Device:C", "100n", "TBD: X7R >=25 V; U413 VDD", C0603, {"1": "AUX_RAW", "2": "GND"}),
        ("J402", "Connector_Generic:Conn_01x10", "SEQ_TO_SYSTEM",
         "Logical interface to power-d021/iso-d019/core; same PCB, not a connector", "",
         {"1": "AUX_RAW", "2": "RAILS_OK", "3": "SEQ_3V3", "4": "RESET", "5": "FAULT",
          "6": "CLIP_OTW", "7": "GND", "8": "RUN", "9": "AUDIO_EN", "10": "DC_OK"}),
    ]
    return [
        {"ref": r, "lib_id": lib, "value": v, "mpn": m, "footprint": fp, "nets": n,
         "units": [(1, 38.1 + (i % 6) * 63.5, 45.72 + (i // 6) * 40.64)]}
        for i, (r, lib, v, m, fp, n) in enumerate(specs)
    ]


def generate(out):
    if out.exists():
        raise FileExistsError("Refusing to overwrite existing sequencing capture")
    out.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix=".seq-d020-", dir=out.parent))
    try:
        sch, manifest = build(
            parts(),
            project="seq-d020",
            namespace="seq-d020",
            source=SOURCE,
            title="PS28 D-020 DISCRETE SEQUENCER SUBSET - STUDY ONLY",
            warning="RELAY/MUTE/DC WINDOWS IN iso-d019. FOOTPRINTS NOT AUDITED. DO NOT ENERGIZE.",
            power_flags=("GND", "AUX_RAW"),
            extra_symbols={"PS28_SEQ:LP2985-33DBV": lp2985_symbol(),
                           "PS28_POWER:TPS3700DDC": tps3700_symbol()},
        )
        manifest["interface_contract"] = {
            "J402": "logical: RAILS_OK wired-AND input/trip output, RESET drive via R408, FAULT/CLIP_OTW TPA open-drain inputs",
            "J401": "physical start button harness; panel location TBD",
            "implemented_contract_subset": [
                "rails hold >=360 ms (BOOT_HOLD_US)", "new human edge, held button ignored",
                "otw_high at request", "FAULT armed by rising edge after RESET release",
                "FAULT low after arming latches off, human re-arm after new hold",
                "start timeout 0.62-1.44 s (START_TIMEOUT_US 1.44 s max)",
                "ANALOG_12V and VMID windows (reference_valid / vmid_valid) into RAILS_OK",
            ],
            "d019_logic_d024": [
                "RESET released 12-28 ms after RUN (relay operate 3 ms max)",
                "DC_OK (both pins 2-5 V) after arming, continuous 12-28 ms, latches AUDIO_EN",
                "DC_OK loss after AUDIO_EN trips RAILS_OK; start timeout covers arming + dwell",
            ],
            "by_design_not_observed": [
                "open/close_confirmed: relay datasheet timing, no auxiliary contact",
                "preclose_match: isolated plate and unpowered pin both near 0 V",
            ],
            "new_physical_board": False,
        }
        (staged / "seq-d020.kicad_sch").write_text(sch)
        (staged / "seq-d020.kicad_pro").write_text("{}\n")
        write_local_library(staged, "PS28_SEQ", [lp2985_symbol()],
                            "Local symbol; TI LP2985 SLVS522S Table 4-1 DBV pinout")
        (staged / "libraries/PS28_POWER.kicad_sym").write_text(
            (ROOT / "kicad/power-d021/libraries/PS28_POWER.kicad_sym").read_text()
        )
        (staged / "sym-lib-table").write_text(
            (staged / "sym-lib-table").read_text().rstrip()[:-1]
            + '(lib (name "PS28_POWER") (type "KiCad") (uri "${KIPRJMOD}/libraries/PS28_POWER.kicad_sym") '
            '(options "") (descr "Local symbol; TI TPS3700 SBVS187G p.4")))\n'
        )
        manifest["calculated"] = {"analog_windows_v": window_thresholds(),
                                  "source": "TI SBVS187G p.6 sec.6.5 VIT limits; 0.1 % dividers"}
        (staged / "seq-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        staged.rename(out)
    except BaseException:
        shutil.rmtree(staged, ignore_errors=True)
        raise


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=DESIGN)
    generate(p.parse_args().output)
