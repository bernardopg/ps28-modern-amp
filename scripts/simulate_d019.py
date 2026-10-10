#!/usr/bin/env python3
"""D-024 study: TPA INPUT_x protection by Form C relay after C20/C21, ngspice transient.

One branch: driver (VMID + audio) -> C20 -> relay COM; NO -> TPA pin (4.7 nF, ~0.98 M
window divider, RIN to a bias source); NC -> 1 k discharge. TPA is NOT modelled beyond
RIN to an ideal bias (same hypothesis class as input-power-order-study); RIN swept,
bias collapses instantly at the fault (worst). Not hardware validation.
"""

import itertools
import json
import math
import subprocess
from pathlib import Path

from create_iso_d019 import RELAY_OPERATE_MAX_S, RELAY_RELEASE_MAX_S, TAP_TAU_S, windows

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build/d019"
REPORT = ROOT / "tests/reports/d019-interface-study.json"

PIN_MIN, PIN_MAX = -0.3, 7.0  # SLASEA8A sec.7.1 p.5, INPUT_X to GND
PLATE_MAX = 16.0  # D-019 proposed isolated-plate excursion
C_COUPLE = (8e-6, 10e-6, 12e-6)  # 10 uF X5R with -20 % DC-bias/tolerance, +20 %
R_IN = (10e3, 20e3, 40e3)  # 20 k typical (SLASEA8A sec.7.5), not guaranteed
WIN = windows()["pin_dc"]
BIAS = (WIN["uv_trip_falling_v"][0], 3.875, WIN["ov_trip_v"][2])  # DC window corners
VMID = (4.36, 6.25)  # ANALOG_12V UV min / AUX max, divided by 2
ANALOG_MAX = 12.5  # driver stuck at ANALOG_12V (AUX max)
AUDIO_PK = 1.41421 * 1.1  # contract 1.414 V pk per branch + 10 % LR4 mute-step overshoot
F_AUDIO = 20.0  # lowest band after the required subsonic HPF
# ANALOG_12V storage decay after AUX loss: (95 mA) / (2 x 470 uF -20 %) / 2 for VMID.
VMID_SLOPE = 0.095 / (2 * 470e-6 * 0.8) / 2
T_OPEN = (RELAY_RELEASE_MAX_S, 10e-3)  # datasheet max; pessimistic logic/coil delay
C_PIN, R_DIV, R_DIS, R_SER = 4.7e-9, 980.7e3, 1e3, 3.3e3
T_FAULT = 1e-3


def netlist(c, rin, bias, vm, data, kind, t_open=None, phase=0.0, t_audio=None, slope=0.0):
    sw = (".model SWR SW(VT=0.5 VH=0.1 RON=0.1 ROFF=1e12)\n"
          # BAT54 fitted to DS11005 p.2 MAXIMUM VF (0.24 V/0.1 mA, 0.32 V/1 mA, 0.4 V/10 mA, 0.5 V/30 mA).
          f".model DCLAMP D(IS=1e-7 N=1.344 RS=2 BV=30 CJO=10p)\nRSER no pin {R_SER}\nDCL 0 pin DCLAMP")
    if kind == "startup":
        # Relay command at 0, NO closes at operate max; RESET 12 ms later; bias step via RIN.
        t_no = RELAY_OPERATE_MAX_S
        t_res = 12e-3
        audio = f"{AUDIO_PK}*sin(2*pi*{F_AUDIO}*(time-{t_audio}))*(time>{t_audio})" if t_audio else "0"
        return f"""* D-019 startup
B1 drv 0 V={vm}+{audio}
C1 drv plate {c} IC={vm}
VCNO cno 0 PWL(0 0 {t_no} 0 {t_no + 1e-6} 1)
VCNC cnc 0 PWL(0 1 {t_no - 1e-4} 1 {t_no - 1e-4 + 1e-6} 0)
SNO plate no cno 0 SWR
SNC plate dis cnc 0 SWR
RDIS dis 0 {R_DIS}
CPIN pin 0 {C_PIN} IC=0
RDIV pin 0 {R_DIV}
RIN pin b {rin}
VB b 0 PWL(0 0 {t_res} 0 {t_res + 1e-6} {bias})
{sw}
.tran 50u 1.2 0 50u UIC
.control
run
wrdata {data} v(pin) v(plate)
quit
.endc
.end
"""
    if kind == "single":
        # Single fault with relay CLOSED throughout: driver output jumps to `slope` volts
        # (0 = shorted low, ANALOG_12V max = stuck high); TPA bias held (worst for low).
        return f"""* D-019 single fault
B1 drv 0 V=({vm}+{AUDIO_PK}*sin(2*pi*{F_AUDIO}*time+{phase}))*(time<{T_FAULT})+{slope}*(time>={T_FAULT})
C1 drv plate {c} IC={vm - bias}
VCNO cno 0 1
VCNC cnc 0 0
SNO plate no cno 0 SWR
SNC plate dis cnc 0 SWR
RDIS dis 0 {R_DIS}
CPIN pin 0 {C_PIN} IC={bias}
RDIV pin 0 {R_DIV}
RIN pin b {rin}
VB b 0 {bias}
{sw}
.tran 20u 0.3 0 20u UIC
.control
run
wrdata {data} v(pin) v(plate) i(VB)
quit
.endc
.end
"""
    # Running fault: steady state at t=0, bias -> 0 at T_FAULT, relay opens t_open later.
    t_o = T_FAULT + t_open
    vm_expr = f"max({vm}-{slope}*max(time-{T_FAULT},0),0)"
    return f"""* D-019 fault
B1 drv 0 V={vm_expr}+{AUDIO_PK}*sin(2*pi*{F_AUDIO}*time+{phase})
C1 drv plate {c} IC={vm - bias}
VCNO cno 0 PWL(0 1 {t_o} 1 {t_o + 1e-6} 0)
VCNC cnc 0 PWL(0 0 {t_o + 1e-4} 0 {t_o + 1e-4 + 1e-6} 1)
SNO plate no cno 0 SWR
SNC plate dis cnc 0 SWR
RDIS dis 0 {R_DIS}
CPIN pin 0 {C_PIN} IC={bias}
RDIV pin 0 {R_DIV}
RIN pin b {rin}
VB b 0 PWL(0 {bias} {T_FAULT} {bias} {T_FAULT + 1e-6} 0)
{sw}
.tran 20u 0.3 0 20u UIC
.control
run
wrdata {data} v(pin) v(plate)
quit
.endc
.end
"""


def simulate(name, text):
    BUILD.mkdir(parents=True, exist_ok=True)
    data, cir = BUILD / f"{name}.dat", BUILD / f"{name}.cir"
    data.unlink(missing_ok=True)
    cir.write_text(text.replace("{data}", str(data)) if "{data}" in text else text)
    r = subprocess.run(["ngspice", "-b", str(cir)], capture_output=True, text=True, timeout=120)
    if r.returncode or not data.exists():
        (BUILD / f"{name}.log").write_text(r.stdout + r.stderr)
        raise RuntimeError("ngspice failed: " + name)
    rows = [list(map(float, l.split())) for l in data.read_text().splitlines() if l.strip()]
    return [r[0] for r in rows], [r[1] for r in rows], [r[3] for r in rows]


def case_name(*parts):
    return "_".join(f"{p:g}" if isinstance(p, float) else str(p) for p in parts).replace(".", "p")


def startup(c, rin, bias, vm):
    name = case_name("su", c, rin, bias, vm)
    t, pin, plate = simulate(name + "a", netlist(c, rin, bias, vm, BUILD / f"{name}a.dat", "startup"))
    # Earliest unmute: pin crosses the minimum UV trip (filtered estimate only lags).
    cross = next((ti for ti, v in zip(t, pin) if ti > 12e-3 and v >= WIN["uv_trip_falling_v"][0]), None)
    if cross is None:
        return {"kind": "startup", "c_f": c, "rin": rin, "bias": bias, "vmid": vm, "dc_never_valid": True,
                "pin_min_v": round(min(pin), 4), "pin_max_v": round(max(pin), 4), "ok": min(pin) >= PIN_MIN}
    t2, pin2, plate2 = simulate(name + "b", netlist(c, rin, bias, vm, BUILD / f"{name}b.dat", "startup",
                                                    t_audio=cross + 12e-3))
    lo, hi = min(pin + pin2), max(pin + pin2)
    return {"kind": "startup", "c_f": c, "rin": rin, "bias": bias, "vmid": vm,
            "unmute_s": round(cross + 12e-3, 4), "pin_min_v": round(lo, 4), "pin_max_v": round(hi, 4),
            "plate_abs_max_v": round(max(map(abs, plate + plate2)), 4),
            "ok": PIN_MIN <= lo and hi <= PIN_MAX}


def fault(c, rin, bias, vm, slope, t_open, phase):
    name = case_name("f", c, rin, bias, vm, round(slope), t_open, round(phase, 3))
    t, pin, plate = simulate(name, netlist(c, rin, bias, vm, BUILD / f"{name}.dat", "fault",
                                           t_open=t_open, phase=phase, slope=slope))
    contact = max(abs(a - b) for ti, a, b in zip(t, plate, pin) if ti > T_FAULT + t_open + 2e-4)
    return {"kind": "fault_analog_decay" if slope else "fault_rails_held", "c_f": c, "rin": rin, "bias": bias,
            "vmid": vm, "t_open_s": t_open, "audio_phase_rad": round(phase, 3),
            "pin_min_v": round(min(pin), 4), "pin_max_v": round(max(pin), 4),
            "plate_abs_max_v": round(max(map(abs, plate)), 4), "open_contact_max_v": round(contact, 4),
            "ok": PIN_MIN <= min(pin) and max(pin) <= PIN_MAX and max(map(abs, plate)) <= PLATE_MAX}


def single_fault(c, rin, bias, vm, level, phase):
    name = case_name("sf", c, rin, bias, vm, level, round(phase, 3))
    t, pin, plate = simulate(name, netlist(c, rin, bias, vm, BUILD / f"{name}.dat", "single",
                                           phase=phase, slope=level))
    return {"kind": "single_fault_low" if level == 0 else "single_fault_high", "c_f": c, "rin": rin,
            "bias": bias, "vmid": vm, "driver_after_v": level, "audio_phase_rad": round(phase, 3),
            "pin_min_v": round(min(pin), 4), "pin_max_v": round(max(pin), 4),
            "ok": PIN_MIN <= min(pin) and max(pin) <= PIN_MAX}


def main():
    grid = list(itertools.product(C_COUPLE, R_IN, BIAS, VMID))
    cases = [startup(*g) for g in grid]
    # Audio phase at the fault swept in 45 degree steps (peaks at fault and at opening).
    phases = tuple(k * math.pi / 4 - 2 * math.pi * F_AUDIO * T_FAULT for k in range(8))
    for g in grid:
        for ph in phases:
            cases.append(fault(*g, 0.0, T_OPEN[0], ph))
            for t_open in T_OPEN:
                cases.append(fault(*g, VMID_SLOPE, t_open, ph))
    single = [single_fault(*g, level, ph) for g in grid for level in (0.0, ANALOG_MAX) for ph in phases[::2]]
    ripple = AUDIO_PK / math.sqrt(1 + (2 * math.pi * F_AUDIO * max(TAP_TAU_S.values())) ** 2)
    report = {
        "study": "D-024 relay isolation of TPA INPUT_x, ngspice transient",
        "model": "driver ideal (VMID + audio); C20 swept; Form C BBM; TPA = RIN to ideal bias, bias -> 0 at fault",
        "limits": {"pin_v": [PIN_MIN, PIN_MAX], "plate_abs_v": PLATE_MAX,
                   "source": "TI SLASEA8A Rev A sec.7.1 p.5; D-019 proposed plate excursion"},
        "inputs": {"c_couple_f": C_COUPLE, "rin_ohm": R_IN, "bias_v": BIAS, "vmid_v": VMID,
                   "audio_pk_v": AUDIO_PK, "audio_hz": F_AUDIO, "vmid_slope_v_per_s": round(VMID_SLOPE, 2),
                   "relay_operate_release_max_s": [RELAY_OPERATE_MAX_S, RELAY_RELEASE_MAX_S],
                   "t_open_s": T_OPEN, "dc_window_v": WIN},
        "dc_estimate_ripple_at_20hz_v": round(ripple, 4),
        "worst_pin_min_v": min(c["pin_min_v"] for c in cases),
        "worst_pin_max_v": max(c["pin_max_v"] for c in cases),
        "worst_plate_abs_v": max(c.get("plate_abs_max_v", 0) for c in cases),
        "worst_pin_min_by_scenario_v": {
            f"{k}@{t}": min(c["pin_min_v"] for c in cases if c["kind"] == k and c.get("t_open_s") == t)
            for k, t in sorted({(c["kind"], c.get("t_open_s")) for c in cases}, key=str)
        },
        "all_ok": all(c["ok"] for c in cases),
        "single_fault": {
            "note": "relay closed, driver shorted low or stuck high; BAT54 at datasheet MAX VF; "
                    "TPA internal input clamp not modelled (would only share current)",
            "low_pin_min_v": min(c["pin_min_v"] for c in single if c["driver_after_v"] == 0),
            "high_pin_max_v": max(c["pin_max_v"] for c in single if c["driver_after_v"] > 0),
            "low_ok": all(c["ok"] for c in single if c["driver_after_v"] == 0),
            "high_ok": all(c["ok"] for c in single if c["driver_after_v"] > 0),
            "cases": single,
        },
        "cases": cases,
        "not_covered": [
            "single fault high side: driver stuck at ANALOG_12V while connected (no upper clamp)",
            "real TPA input circuit unpowered/in reset (only RIN to ideal bias)",
            "relay contact bounce, stuck contact, coil drive failure",
            "audio below 20 Hz (front-end subsonic HPF required, ELEC-002)",
        ],
        "hardware_validated": False,
        "manufacturing_approved": False,
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(f"D-019: {len(cases)} cases; pin {report['worst_pin_min_v']}..{report['worst_pin_max_v']} V; "
          f"all_ok={report['all_ok']}; hardware NOT validated")


if __name__ == "__main__":
    main()
