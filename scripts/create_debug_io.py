#!/usr/bin/env python3
"""PCB-004: probe test points, status LEDs and an optional fan output.

Nothing here touches a TPA pin, VMID or the audio path with a DC load: status lines
only drive MOSFET gates (BSS138, leakage < 1 uA) and the inverters pull up to SEQ_3V3.
LED R values: (12 V - 2 V) / 2.2 k = 4.5 mA, 45 mW in 0805. PVDD LED sits across the
bulk (48 V / 47 k = 1 mA): it also shows that the capacitors are still charged.
Fan: 12 V <= 200 mA (LM5164 1 A rail, existing load < 0.3 A), AO3400A low side.
"""

from create_power_d021 import local_symbol

# Probe points: net -> silk label. SPK+/- are deliberately absent (active, never ground).
PROBES = {"GND": "GND", "PVDD": "PVDD", "AUX_RAW": "12V", "P15V": "+15V", "N15V": "-15V",
          "ANALOG_12V": "A12V", "VMID": "VMID", "SEQ_3V3": "3V3", "GVDD_AB": "GVDD",
          "RESET": "RST", "FAULT": "FLT", "CLIP_OTW": "OTW", "RAILS_OK": "ROK", "DC_OK": "DCOK",
          "PRE_IN": "IN", "DIFF_P": "D+", "DIFF_N": "D-", "INPUT_A_AC": "INA", "INPUT_B_AC": "INB",
          "T1_CT": "CT"}
TP = "TestPoint:TestPoint_Pad_D2.0mm"
R0805, R1206, LED = ("Resistor_SMD:R_0805_2012Metric", "Resistor_SMD:R_1206_3216Metric",
                     "LED_SMD:LED_0805_2012Metric")
SOT23 = "Package_TO_SOT_SMD:SOT-23"


def symbols():
    fet = [("1", "G", "input", -7.62, 0, 0), ("2", "S", "passive", 2.54, -7.62, 90),
           ("3", "D", "passive", 2.54, 7.62, 270)]
    return {"PS28_PRE:AO3400A": local_symbol("PS28_PRE:AO3400A", fet,
                                             "AOS AO3400A: SOT-23 1=G 2=S 3=D, 30 V 5.7 A", half_width=5.08)}


def parts():
    specs = []
    for i, (net, label) in enumerate(PROBES.items()):
        specs.append((f"TP{110 + i}", "Connector:TestPoint", label, "PCB test pad, no part", TP, {"1": net}))
    specs.append(("TP130", "Connector:TestPoint", "GND", "PCB test pad, no part", TP, {"1": "GND"}))

    def led(n, label, anode, cathode, r, rfp=R0805):
        specs.append((f"D{n}", "Device:LED", label, "Green 0805 LED (e.g. Lite-On LTST-C171GKT)", LED,
                      {"1": cathode, "2": f"LED{n}_A"}))
        specs.append((f"R{n}", "Device:R", r, f"{rfp.split('_')[1]} 1 %", rfp, {"1": anode, "2": f"LED{n}_A"}))

    def fet(ref, gate, drain, mpn="BSS138", lib="PS28_PRE:BSS138"):
        specs.append((ref, lib, mpn, f"onsemi {mpn}" if mpn == "BSS138" else "AOS AO3400A", SOT23,
                       {"1": gate, "2": "GND", "3": drain}))

    led(701, "PVDD", "PVDD", "GND", "47k", R1206)              # bulk charged / PVDD present
    led(702, "RAILS_OK", "AUX_RAW", "LED_ROK_K", "2.2k")
    fet("Q701", "RAILS_OK", "LED_ROK_K")
    led(703, "RUN", "AUX_RAW", "LED_RUN_K", "2.2k")
    fet("Q702", "RESET", "LED_RUN_K")                          # RESET high = TPA running
    led(704, "AUDIO", "AUX_RAW", "RELAY_DRV", "2.2k")          # lit while Q501 holds K501 closed
    for n, line, inv, q in ((705, "FAULT", "FAULT_N", ("Q703", "Q704")),
                            (706, "CLIP_OTW", "CLIP_N", ("Q705", "Q706"))):
        # Active-low open-drain line -> inverter (pull-up to 3V3) -> LED driver.
        fet(q[0], line, inv)
        specs.append((f"R{n + 10}", "Device:R", "10k", "0805 1 %", R0805, {"1": "SEQ_3V3", "2": inv}))
        led(n, line, "AUX_RAW", f"LED{n}_K", "2.2k")
        fet(q[1], inv, f"LED{n}_K")
    # Fan: J8 + low-side AO3400A; JP701 1-2 always on, 2-3 on CLIP_OTW (clip or thermal warning).
    specs += [
        ("J8", "Connector_Generic:Conn_01x02", "FAN 12V", "JST B2B-XH-A(LF)(SN); fan <= 200 mA",
         "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", {"1": "AUX_RAW", "2": "FAN_N"}),
        ("D707", "Device:D", "S1M", "S1M flyback across the fan", "Diode_SMD:D_SMA",
         {"1": "AUX_RAW", "2": "FAN_N"}),
        ("JP701", "Connector_Generic:Conn_01x03", "FAN MODE", "2.54 mm header + jumper: 1-2 ON, 2-3 OTW",
         "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
         {"1": "SEQ_3V3", "2": "FAN_G", "3": "CLIP_N"}),
        ("R720", "Device:R", "100k", "0805 1 %; fan off without jumper", R0805, {"1": "FAN_G", "2": "GND"}),
    ]
    fet("Q707", "FAN_G", "FAN_N", "AO3400A", "PS28_PRE:AO3400A")
    out = []
    for i, (ref, lib, value, mpn, fp, nets) in enumerate(specs):
        out.append({"ref": ref, "lib_id": lib, "value": value, "mpn": mpn, "footprint": fp, "nets": nets,
                    "units": [(1, 38.1 + (i % 8) * 38.1, 45.72 + (i // 8) * 38.1)]})
    return out
