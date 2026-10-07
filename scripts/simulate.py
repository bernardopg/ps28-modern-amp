#!/usr/bin/env python3
"""Check actual ngspice output against the ideal LR4 analytic response."""

from pathlib import Path
import json
import math
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def lr4_magnitude(frequency, cutoff=80):
    return 1 / (1 + (frequency / cutoff) ** 4)


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


if __name__ == "__main__":
    main()
