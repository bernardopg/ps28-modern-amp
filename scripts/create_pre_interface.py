#!/usr/bin/env python3
"""D-032 interface to the reused PS28 preamp + limiter boards (ELEC-004).

The original preamp/limiter boards keep RCA L/R/LFE, LR4 50-150 Hz, LEVEL, PHASE,
subsonic filter, limiter and auto-on in the original panel holes (service manual
p.22-23). The new main board replaces the original P101 side (manual p.24):
7-way JST XH header, +/-15 V rails copied from the discrete Q117/Q119 followers,
audio IN coupled to the existing OPA1656 differential driver, and LIMIT driven by
the TPA3255 CLIP_OTW so the original limiter engages on clipping/over-temperature.
"""

from create_power_d021 import local_symbol

# P101 order on manual p.24 (top to bottom) = pin 1..7. Consistent with the owner
# readings of 2026-10-10: pin 4 GND 0.5 ohm, pin 5 bulk +V, pin 7 high-Z (IN, R101 47k).
P101 = {"1": "LIMIT", "2": "STB", "3": "N15V", "4": "GND", "5": "P15V", "6": "PTC", "7": "PRE_IN"}

R0603, R1206, R2512 = ("Resistor_SMD:R_0603_1608Metric", "Resistor_SMD:R_1206_3216Metric",
                       "Resistor_SMD:R_2512_6332Metric")
C0603, C1206 = "Capacitor_SMD:C_0603_1608Metric", "Capacitor_SMD:C_1206_3216Metric"
SOT223, SOT23 = "Package_TO_SOT_SMD:SOT-223-3_TabPin2", "Package_TO_SOT_SMD:SOT-23"


def symbols():
    bjt = [("1", "B", "input", -7.62, 0, 0), ("2", "C", "passive", 2.54, 7.62, 270),
           ("3", "E", "passive", 2.54, -7.62, 90)]
    return {
        "PS28_PRE:BCP56": local_symbol("PS28_PRE:BCP56", bjt, "onsemi BCP56/D: SOT-223 1=B 2=C 3=E tab=C",
                                       half_width=5.08),
        "PS28_PRE:BCP53": local_symbol("PS28_PRE:BCP53", bjt, "onsemi BCP53/D: SOT-223 1=B 2=C 3=E tab=C",
                                       half_width=5.08),
        "PS28_PRE:BSS138": local_symbol("PS28_PRE:BSS138", [
            ("1", "G", "input", -7.62, 0, 0), ("2", "S", "passive", 2.54, -7.62, 90),
            ("3", "D", "passive", 2.54, 7.62, 270)], "onsemi BSS138/D: SOT-23 1=G 2=S 3=D", half_width=5.08),
    }


def parts():
    specs = [
        # ref, lib_id, value, MPN/requirement, footprint, nets
        ("J7", "Connector_Generic:Conn_01x07", "B7B-XH-A(LF)(SN)",
         "JST B7B-XH-A(LF)(SN), 2.5 mm: mates OEM 7-way preamp harness (P101, manual p.14/p.24)",
         "Connector_JST:JST_XH_B7B-XH-A_1x07_P2.50mm_Vertical", P101),
        ("TP102", "Connector:TestPoint", "STB", "PCB test pad, no part; preamp auto-on not used (D-032)",
         "TestPoint:TestPoint_Pad_D2.0mm", {"1": "STB"}),
        ("TP103", "Connector:TestPoint", "PTC", "PCB test pad, no part; OEM protection LED line not driven",
         "TestPoint:TestPoint_Pad_D2.0mm", {"1": "PTC"}),
        # +15 V: OEM Q117 follower (manual p.24): collector resistor shares dissipation.
        ("R601", "Device:R", "470 1W", "2512 thick film 1 W; MPN at BOM", R2512, {"1": "PVDD", "2": "P15_COL"}),
        ("R602", "Device:R", "10k", "1206 0.25 W; 34 V max across", R1206, {"1": "PVDD", "2": "P15_BASE"}),
        ("D601", "Device:D_Zener", "BZT52C16", "Diodes BZT52C16 (DS18004): 15.3-17.1 V @5 mA",
         "Diode_SMD:D_SOD-123", {"1": "P15_BASE", "2": "GND"}),
        ("Q601", "PS28_PRE:BCP56", "BCP56", "onsemi BCP56T1G: 80 V, 1 A, SOT-223", SOT223,
         {"1": "P15_BASE", "2": "P15_COL", "3": "P15V"}),
        ("C601", "Device:C", "10u 25V", "X7R 1206 >=25 V; MPN at BOM", C1206, {"1": "P15V", "2": "GND"}),
        ("C602", "Device:C", "100n", "X7R 0603 50 V", C0603, {"1": "P15_BASE", "2": "GND"}),
        # -15 V: T1 negative half-cycles (OEM KBL405 negative legs) into a small reservoir.
        ("D602", "Device:D", "S1M", "S1M 1000 V 1 A SMA (Vishay/onsemi); light load", "Diode_SMD:D_SMA",
         {"1": "T1_A", "2": "NRAW"}),
        ("D603", "Device:D", "S1M", "S1M 1000 V 1 A SMA (Vishay/onsemi); light load", "Diode_SMD:D_SMA",
         {"1": "T1_B", "2": "NRAW"}),
        ("C603", "Device:C_Polarized", "120u 63V", "Nichicon UHE1J121MPD 120 uF/63 V 8x20 (CAT.8100M)",
         "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm", {"1": "GND", "2": "NRAW"}),
        ("R603", "Device:R", "470 1W", "2512 thick film 1 W; MPN at BOM", R2512, {"1": "NRAW", "2": "N15_COL"}),
        ("R604", "Device:R", "10k", "1206 0.25 W", R1206, {"1": "NRAW", "2": "N15_BASE"}),
        ("D604", "Device:D_Zener", "BZT52C16", "Diodes BZT52C16 (DS18004)", "Diode_SMD:D_SOD-123",
         {"1": "GND", "2": "N15_BASE"}),
        ("Q602", "PS28_PRE:BCP53", "BCP53", "onsemi BCP53T1G: -80 V, -1 A, SOT-223", SOT223,
         {"1": "N15_BASE", "2": "N15_COL", "3": "N15V"}),
        ("C604", "Device:C", "10u 25V", "X7R 1206 >=25 V; MPN at BOM", C1206, {"1": "GND", "2": "N15V"}),
        ("C605", "Device:C", "100n", "X7R 0603 50 V", C0603, {"1": "GND", "2": "N15_BASE"}),
        # LIMIT: limiter window ~+/-7.1 V (R301-R303 10k/18k/10k, manual p.23); clip pulls it to +15 V.
        ("Q603", "PS28_PRE:BSS138", "BSS138", "onsemi BSS138: gate on CLIP_OTW, no DC load on the TPA pin",
         SOT23, {"1": "CLIP_OTW", "2": "GND", "3": "LIMIT"}),
        ("R605", "Device:R", "10k", "0603 1 %", R0603, {"1": "P15V", "2": "LIMIT"}),
        # Audio: IN coupled to the driver; DC bias through R101+R102 to VMID.
        ("C109", "Device:C", "2.2u 63V film", "Film 2.2 uF >=63 V, P5 mm (WIMA MKS2 class); MPN at BOM",
         "Capacitor_THT:C_Rect_L7.2mm_W5.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2", {"1": "PRE_IN", "2": "MONO_BIASED"}),
        ("R110", "Device:R", "8.87k", "0603 1 % thin film; U2A gain 1+8.87k/10k = 1.887", R0603,
         {"1": "BUFFERED", "2": "U2_FB"}),
        ("R111", "Device:R", "10k", "0603 1 % thin film", R0603, {"1": "U2_FB", "2": "VMID"}),
    ]
    out = []
    for i, (ref, lib, value, mpn, fp, nets) in enumerate(specs):
        out.append({"ref": ref, "lib_id": lib, "value": value, "mpn": mpn, "footprint": fp, "nets": nets,
                    "units": [(1, 38.1 + (i % 6) * 50.8, 45.72 + (i // 6) * 50.8)]})
    return out


def analog_changes(parts):
    """Drop the on-board LR4 (the OEM preamp does the crossover) and turn U2A into the gain stage."""
    lr4 = {"R103", "R104", "R105", "R106", "C101", "C102", "C103", "C104", "C105", "C106"}
    out = [p for p in parts if p["ref"] not in lr4]
    for p in out:
        if p["ref"] == "R101":
            p.update(value="1k", mpn="CRCW08051K00FKEA")
        elif p["ref"] == "R102":
            p.update(value="100k", mpn="CRCW0805100KFKEA")
        elif p["ref"] == "U2":
            p["nets"].update({"2": "U2_FB", "5": "VMID", "6": "U2B_PARK", "7": "U2B_PARK"})
        elif p["ref"] == "U3":
            p["nets"]["3"] = "BUFFERED"
    return out


def gain():
    """IN (V) to TPA differential input for the OEM sensitivity (manual p.24: R104/R103)."""
    divided = 100e3 / (1e3 + 100e3)
    return divided * (1 + 8.87e3 / 10e3) * 2  # U3 drives DIFF_P and inverted DIFF_N


if __name__ == "__main__":
    oem_in = 25.7 / (1 + 56e3 / 1.5e3)          # 150 W/4.4 ohm -> 25.7 Vrms; OEM gain 1+R104/R103
    tpa_in = 25.7 / 10 ** (21.5 / 20)           # SLASEA8A: 21.5 dB
    series = 10 ** (-1.33 / 20)                 # D-024a 3.3 k series, typical
    print(f"OEM IN at full power {oem_in:.3f} Vrms; need {tpa_in / series:.3f} Vrms diff at driver; "
          f"chain gives {oem_in * gain():.3f} Vrms")
