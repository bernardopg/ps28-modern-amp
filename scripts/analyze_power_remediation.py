#!/usr/bin/env python3
"""Budgets D-021: ramo CT real no modelo e contraprova de OVP. Não valida hardware."""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import simulate_power_d021 as power

ROOT = Path(__file__).resolve().parents[1]


def square_integral(t, values, start, end):
    """Integral exata de quadrado de sinal linear por trecho, com janela recortada."""
    if len(t) != len(values) or len(t) < 2 or start >= end:
        raise ValueError("Invalid waveform/window")
    if any(b <= a for a, b in zip(t, t[1:])) or start < t[0] or end > t[-1]:
        raise ValueError("Nonmonotonic/incomplete waveform")
    if not all(math.isfinite(x) for x in [*t, *values, start, end]):
        raise ValueError("Nonfinite waveform")
    total = 0.0
    for i in range(1, len(t)):
        left, right = max(t[i-1], start), min(t[i], end)
        if right <= left:
            continue
        slope = (values[i] - values[i-1]) / (t[i] - t[i-1])
        a = values[i-1] + slope * (left-t[i-1])
        b = values[i-1] + slope * (right-t[i-1])
        total += (right-left) * (a*a + a*b + b*b) / 3
    return total


def divider_interval(v_normal, v_limit, threshold_min, threshold_max):
    """Vtrip=ratio*Vthreshold. Ideal, sem erro resistivo/bias/atraso: necessário, não suficiente."""
    lower, upper = v_normal/threshold_min, v_limit/threshold_max
    return {"ratio_lower_exclusive": lower, "ratio_upper_inclusive": upper,
            "feasible_even_with_ideal_resistors": lower < upper}


def analyze_wave(t, ia, ib, load):
    ct = [a+b for a, b in zip(ia, ib)]
    cap = [i-load for i in ct]  # carga constante após 0.21 s; só usado em regime
    start, end = power.T_END-power.WINDOW, power.T_END
    rms = lambda x: math.sqrt(square_integral(t, x, start, end)/(end-start))
    return {"ct_rms_a": rms(ct), "half_a_rms_a": rms(ia), "half_b_rms_a": rms(ib),
            "bank_ripple_rms_a": rms(cap), "ct_inrush_i2t_100ms_a2s": square_integral(t, ct, t[0], 0.1)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reuse-waveforms', action='store_true', help='Reutiliza dados completos somente se o .cir casar com o gerador atual')
    args = parser.parse_args()
    power.BUILD.mkdir(parents=True, exist_ok=True)
    cases = []
    for mains, bulk, load, leak in itertools.product(power.MAINS, power.BULK_UF, power.LOAD_A, power.LEAK_H):
        name = f"m{mains:g}_c{bulk}_i{load:g}_l{leak:g}".replace(".", "p")
        path = power.BUILD / f"{name}.dat"
        circuit = path.with_suffix('.cir')
        if args.reuse_waveforms:
            if not circuit.exists() or circuit.read_text() != power.netlist(mains, bulk, load, leak, path):
                raise ValueError(f'Waveform input mismatch: {path}')
        else:
            power.run_case(mains, bulk, load, leak)
        rows = [list(map(float, s.split())) for s in path.read_text().splitlines() if s.strip()]
        result = analyze_wave([r[0] for r in rows], [r[3] for r in rows], [r[5] for r in rows], load)
        cases.append(dict(mains_vac=mains, bulk_uf=bulk, load_a=load, leakage_h=leak,
                          data_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), **result))
    report = {"scope": "Calculation over generic ngspice D-021 model; not selected-device SPICE or measurement",
              "hardware_validated": False, "manufacturing_approved": False, "cases": cases,
              "reused_waveforms": args.reuse_waveforms,
              "worst_ct_rms_a": max(c["ct_rms_a"] for c in cases),
              "worst_bank_ripple_rms_a": max(c["bank_ripple_rms_a"] for c in cases),
              "worst_ct_inrush_i2t_a2s": max(c["ct_inrush_i2t_100ms_a2s"] for c in cases),
              "lm5069_internal_ovlo": divider_interval(49.84, 53.5, 2.4, 2.6),
              "ovlo_source": "TI LM5069 SNVS452G Jan 2020 p.5, OVLOTH 2.4..2.6 V",
              "proposal": "External precision OVP + series disconnect/controlled start requires new design; internal OVLO alone rejected.",
              "limitations": ["Transformer parasitics and diode model generic; no fuse selected from these numbers alone",
                              "Bulk sharing requires ESR/frequency/temperature; bank RMS not divided equally by assumption",
                              "MOSFET SOA, transient slew/delay, fail-short and restart not qualified"],
              "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (Path(__file__), ROOT/'scripts/simulate_power_d021.py')}}
    out = ROOT/'tests/reports/power-remediation-budget.json'
    out.write_text(json.dumps(report, indent=2)+'\n')
    print(f"{len(cases)} simulated cases; CT max {report['worst_ct_rms_a']:.3f} A rms; "
          f"bank max {report['worst_bank_ripple_rms_a']:.3f} A rms; {out}")


if __name__ == '__main__':
    main()
