#!/usr/bin/env python3
"""D-021 study: T1 centre-tap two-diode rectifier into PVDD bulk, ngspice transient.

Inputs are owner measurements (2026-10-09): 34.35 VAC per half at 126.6 VAC mains,
~0.2 ohm per half winding. Leakage inductance, primary resistance and diode
parameters are NOT measured; they are swept or generic. Not hardware validation.
"""

import itertools
import json
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build/power-d021"
REPORT = ROOT / "tests/reports/power-d021-study.json"

RATIO = 34.35 / 126.6  # measured VAC per half winding per VAC mains, no load
R_HALF = 0.2  # ohm, owner DMM after probe offset; 0.1 ohm resolution
MAINS = (108.0, 126.6, 133.0)  # manual p.2 low limit, measured, high-line hypothesis
BULK_UF = (3000, 10000, 15000)
LOAD_A = (0.1, 2.6, 3.9)  # idle; ~100 W and ~150 W out at eta 0.88/~44 V (hypothesis)
LEAK_H = (100e-6, 1e-3)  # per half, unmeasured bound
ESR = 0.02  # ohm total bank, hypothesis
PVDD_MAX = 53.5  # SLASEA8A p.6 sec.7.3, RL = 4 ohm
PVDD_MIN = 18.0
F = 60.0
T_END = 1.0
WINDOW = 5 / F


def netlist(mains, bulk_uf, load, leak, data):
    vpk = mains * RATIO * math.sqrt(2)
    # Worst-case inrush: switch-on at voltage peak (phase 90 deg), bulk at 0 V.
    return f"""* D-021 CT rectifier
VA a0 0 SIN(0 {vpk} {F} 0 0 90)
VB b0 0 SIN(0 {vpk} {F} 0 0 270)
RA a0 a1 {R_HALF}
LA a1 a2 {leak}
RB b0 b1 {R_HALF}
LB b1 b2 {leak}
VIA a2 a3 0
VIB b2 b3 0
DA a3 pv DREC
DB b3 pv DREC
.model DREC D(IS=1e-8 N=1.8 RS=0.01 BV=1000 CJO=100p)
RESR pv c1 {ESR}
CB c1 0 {bulk_uf}u IC=0
ILOAD pv 0 PWL(0 0 0.2 0 0.21 {load})
.tran 20u {T_END} 0 20u UIC
.options method=gear reltol=1e-4
.control
run
wrdata {data} v(pv) i(VIA) i(VIB)
quit
.endc
.end
"""


def run_case(mains, bulk_uf, load, leak):
    name = f"m{mains:g}_c{bulk_uf}_i{load:g}_l{leak:g}".replace(".", "p")
    data = BUILD / f"{name}.dat"
    cir = BUILD / f"{name}.cir"
    data.unlink(missing_ok=True)
    cir.write_text(netlist(mains, bulk_uf, load, leak, data))
    r = subprocess.run(["ngspice", "-b", str(cir)], capture_output=True, text=True, timeout=300)
    if r.returncode or not data.exists():
        (BUILD / f"{name}.log").write_text(r.stdout + r.stderr)
        raise RuntimeError("ngspice failed: " + name)
    rows = [list(map(float, l.split())) for l in data.read_text().splitlines() if l.strip()]
    # wrdata: t v(pv) t i(VIA) t i(VIB)
    t = [x[0] for x in rows]
    v = [x[1] for x in rows]
    ia = [x[3] for x in rows]
    ib = [x[5] for x in rows]
    if t[-1] < T_END * 0.999:
        raise ValueError("Incomplete transient: " + name)
    ss = [i for i, x in enumerate(t) if x >= T_END - WINDOW]
    inrush = [i for i, x in enumerate(t) if x <= 0.1]

    def rms(xs, idx):
        num = sum(xs[i] ** 2 * (t[i] - t[i - 1]) for i in idx[1:])
        return math.sqrt(num / (t[idx[-1]] - t[idx[0]]))

    i2t = sum(max(ia[i], ib[i]) ** 2 * (t[i] - t[i - 1]) for i in inrush[1:])
    vmax = max(v[i] for i in ss)
    vmin = min(v[i] for i in ss)
    return {
        "mains_vac": mains,
        "bulk_uf": bulk_uf,
        "load_a": load,
        "leakage_h_per_half": leak,
        "pvdd_max_v": round(vmax, 3),
        "pvdd_min_v": round(vmin, 3),
        "ripple_vpp": round(vmax - vmin, 3),
        "diode_peak_steady_a": round(max(max(ia[i], ib[i]) for i in ss), 3),
        "half_winding_rms_a": round(rms(ia, ss), 3),
        "inrush_peak_a": round(max(max(ia[i], ib[i]) for i in inrush), 2),
        "inrush_i2t_a2s_first_100ms": round(i2t, 2),
        "within_pvdd_range": PVDD_MIN <= vmin and vmax <= PVDD_MAX,
    }


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    cases = [run_case(*c) for c in itertools.product(MAINS, BULK_UF, LOAD_A, LEAK_H)]
    worst_hi = max(c["pvdd_max_v"] for c in cases)
    report = {
        "study": "D-021 CT two-diode rectifier, ngspice transient",
        "inputs": {
            "measured": "34.35 VAC/half at 126.6 VAC, ~0.2 ohm/half (owner, 2026-10-09)",
            "ratio_vac_per_vac": RATIO,
            "unmeasured_swept_or_generic": [
                "leakage inductance per half (100 uH, 1 mH)",
                "primary resistance and core regulation (omitted: optimistic sag, pessimistic inrush)",
                "generic silicon diode model, not a selected MPN",
                "bank ESR 20 mohm",
                "constant-current load approximating amplifier average draw",
            ],
        },
        "limits": {"pvdd_min_v": PVDD_MIN, "pvdd_max_v": PVDD_MAX,
                   "source": "TI SLASEA8A Rev A p.6 sec.7.3, RL=4 ohm; no PVDD OVP in device (sec.7.5 UVP only)"},
        "diode_piv_required_v": round(2 * max(MAINS) * RATIO * math.sqrt(2), 1),
        "worst_pvdd_max_v": worst_hi,
        "cases": cases,
        "hardware_validated": False,
        "manufacturing_approved": False,
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(f"D-021: {len(cases)} cases; worst PVDD max {worst_hi} V; PIV >= {report['diode_piv_required_v']} V; hardware NOT validated")


if __name__ == "__main__":
    main()
