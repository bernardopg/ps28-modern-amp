#!/usr/bin/env python3
"""Check actual ngspice output against the ideal LR4 analytic response."""

from pathlib import Path
import json
import math
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def lr4_magnitude(frequency, cutoff=80):
    return 1 / (1 + (frequency / cutoff) ** 4)


def output_lc_magnitude(frequency, inductance=10e-6, capacitance=940e-9,
                        load=4.0, winding_dcr=8.76e-3):
    """Balanced differential linear model: series 2L/2DCR, equivalent C/2."""
    s = complex(0, 2 * math.pi * frequency)
    ld, cd, rd = 2 * inductance, capacitance / 2, 2 * winding_dcr
    return abs(1 / (1 + rd / load + s * (ld / load + rd * cd) + s * s * ld * cd))


def verify_output_lc(build):
    data = build / 'output-lc.dat'
    report_path = build / 'output-lc-result.json'
    data.unlink(missing_ok=True)
    report_path.unlink(missing_ok=True)
    result = subprocess.run(['ngspice', '-b', 'simulation/output-lc-ideal.cir'],
                            cwd=ROOT, capture_output=True, text=True, timeout=60)
    (build / 'output-lc.log').write_text(result.stdout + result.stderr)
    if result.returncode or not data.exists():
        raise RuntimeError('LC ngspice failed; see build/output-lc.log')
    rows = [list(map(float, line.split()[:2])) for line in data.read_text().splitlines() if line.strip()]
    if len(rows) < 100 or not math.isclose(rows[0][0], 10) or not math.isclose(rows[-1][0], 1e6):
        raise ValueError('Incomplete LC sweep')
    for frequency, magnitude in rows:
        if not math.isclose(magnitude, output_lc_magnitude(frequency), rel_tol=1e-5):
            raise ValueError(f'LC model disagreement at {frequency} Hz')
    report = {'model': 'Balanced differential passive LC, linear 4 ohm load, 20 C DCR',
              'natural_frequency_hz': 1 / (2 * math.pi * math.sqrt(10e-6 * 940e-9)),
              'q_without_dcr': (4 / 2) * math.sqrt(940e-9 / 10e-6),
              'sweep_points_checked': len(rows),
              'includes_switching_core_loss_woofer_thermal': False,
              'hardware_validated': False}
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(f"LC differential: fn={report['natural_frequency_hz']:.1f} Hz; {len(rows)} SPICE points checked; hardware NOT validated")


def main():
    build = ROOT / "build"
    build.mkdir(exist_ok=True)
    data = build / "lr4-80hz.dat"
    data.unlink(missing_ok=True)  # Prevent false success from stale output.
    result = subprocess.run(
        ["ngspice", "-b", "simulation/lr4-ideal.cir"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    (build / "lr4.log").write_text(result.stdout + result.stderr)
    if result.returncode or not data.exists():
        raise RuntimeError("ngspice failed; see build/lr4.log")
    rows = [line.split() for line in data.read_text().splitlines() if line.strip()]
    frequency, magnitude = map(float, rows[-1][:2])
    expected = lr4_magnitude(frequency)
    if not math.isclose(frequency, 80, abs_tol=0.001) or not math.isclose(
        magnitude, expected, rel_tol=0.001
    ):
        raise ValueError(
            f"LR4 mismatch: f={frequency}, magnitude={magnitude}, expected={expected}"
        )
    report = {
        "model": "Ideal Sallen-Key VCVS, not physical NE5532",
        "frequency_hz": frequency,
        "magnitude": magnitude,
        "gain_db": 20 * math.log10(magnitude),
        "hardware_validated": False,
    }
    (build / "lr4-result.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"LR4 ideal: {report['gain_db']:.4f} dB @ {frequency:g} Hz; hardware NOT validated"
    )
    verify_output_lc(build)


if __name__ == "__main__":
    main()
