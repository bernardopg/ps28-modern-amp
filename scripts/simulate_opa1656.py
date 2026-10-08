#!/usr/bin/env python3
"""Audited official TI model, local-only; no claim of measured hardware performance."""

import argparse
import hashlib
import io
import itertools
import json
import math
import os
import re
import subprocess
import urllib.request
import zipfile

from simulate_analog import CONFIG, ROOT, deck, section_response

URL = "https://www.ti.com/lit/zip/SBOMAW6"
MODEL_SHA = "9847ed60c62e792ee6f1c84899278a3c11ce71a6d21804bdd88f51199f1ba055"
MODEL = ROOT / "build/analog/parts/OPA1656.LIB"


def require_simulator(version_text):
    match = re.search(r"ngspice-(\d+)", version_text)
    if not match or int(match[1]) < 47:
        raise ValueError(
            "Official TI model study requires ngspice >=47; Ubuntu ngspice42 failed operating-point convergence. Do not substitute model or suppress errors."
        )
    return int(match[1])


def audit_model(content):
    if hashlib.sha256(content).hexdigest() != MODEL_SHA:
        raise ValueError("TI model revision/hash changed; review before simulation")
    directives = set()
    for line in content.decode("ascii").splitlines():
        s = line.strip()
        if not s or s.startswith(("*", "+")):
            continue
        if s.startswith("."):
            directive = s.split()[0].upper()
            directives.add(directive)
            if directive not in {".SUBCKT", ".MODEL", ".ENDS"}:
                raise ValueError(
                    "Executable/external or unaudited model directive: " + directive
                )
        elif s[0].upper() not in "CEGHRIVXSD":
            raise ValueError("Unaudited element: " + s)
    if ".SUBCKT OPA1656 IN+ IN- VCC VEE OUT" not in content.decode("ascii"):
        raise ValueError("Unexpected TI pin order")
    return sorted(directives)


def fetch_model():
    # Read exactly one member. Never extract vendor projects, binaries or scripts.
    with urllib.request.urlopen(URL, timeout=45) as response:
        archive = response.read(2_000_001)
    if len(archive) > 2_000_000:
        raise ValueError("Unexpected model archive size")
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        info = z.getinfo("OPA1656.LIB")
        if info.file_size > 100000:
            raise ValueError("Unexpected model size")
        content = z.read(info)
    audit_model(content)
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    MODEL.write_bytes(content)


def official_deck(config, filename, supply, temperature, transient=False):
    config = dict(config, aux_supply_min_v=supply)
    result = deck(config, filename, transient=transient)
    original = ".subckt AMP p n out mid supply\nEAMP out 0 p n 1e9\n.ends AMP"
    replacement = (
        ".subckt AMP p n out mid supply\nXTI p n supply 0 out OPA1656\n.ends AMP\n"
        '.include "build/analog/parts/OPA1656.LIB"\n' + f".temp {temperature}\n"
    )
    if result.count(original) != 1:
        raise ValueError("Unexpected study opamp wrapper")
    return result.replace(original, replacement).replace(
        "NO qualified NE5532/VMID/startup model.",
        "official TI OPA1656 model; ideal external VMID; NOT measured hardware.",
    )


def run(config, directory, supply, temperature, transient):
    name = f"v{supply:g}-t{temperature:g}-" + ("tran" if transient else "ac")
    data = directory / (name + ".dat")
    data.unlink(missing_ok=True)
    circuit = directory / (name + ".cir")
    circuit.write_text(
        official_deck(config, data.relative_to(ROOT), supply, temperature, transient)
    )
    # Isolated startup file: no global ngspice configuration modifications.
    init = directory / "init"
    init.mkdir(exist_ok=True)
    (init / ".spiceinit").write_text("set ngbehavior=psa\n")
    # Older distribution builds may not honor SPICE_USERINIT_DIR. HOME is
    # overridden only for this child process, keeping its startup file isolated.
    env = dict(os.environ, HOME=str(init), SPICE_USERINIT_DIR=str(init))
    result = subprocess.run(
        ["ngspice", "-b", str(circuit.relative_to(ROOT))],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    log = result.stdout + result.stderr
    (directory / (name + ".log")).write_text(log)
    if result.returncode or not data.exists() or "Error:" in log:
        raise RuntimeError(
            "Official-model simulation failed: " + name + "\n" + log[-2000:]
        )
    warnings = [line for line in log.splitlines() if "Warning:" in line]
    approved = {
        "Warning: Dynamic gmin stepping failed",
        "Warning: True gmin stepping failed",
        "Warning: source stepping failed",
    }
    if any(w not in approved for w in warnings):
        raise RuntimeError("New model/tool warning requires review: " + name)
    converged = (
        "Source stepping completed" in log
        or "Transient op finished successfully" in log
    )
    if warnings and not converged:
        raise RuntimeError("No converged fallback operating point: " + name)
    rows = [
        list(map(float, line.split()))
        for line in data.read_text().splitlines()
        if line.strip()
    ]
    if not rows or any(not math.isfinite(v) for row in rows for v in row):
        raise ValueError("Empty/nonfinite official-model output")
    return rows, warnings


def wave_metrics(rows, supply):
    wave = [r for r in rows if r[0] >= 0.25]
    if len(wave) < 500 or wave[-1][0] < 0.349:
        raise ValueError("Incomplete official-model transient")
    duration = wave[-1][0] - wave[0][0]
    mean = power = 0
    for a, b in itertools.pairwise(wave):
        dt = b[0] - a[0]
        if dt <= 0:
            raise ValueError("Nonmonotonic transient time")
        va, vb = a[3] - a[5], b[3] - b[5]
        mean += dt * (va + vb) / 2
        power += dt * (va * va + vb * vb) / 2
    mean /= duration
    rms = math.sqrt(max(0, power / duration - mean * mean))
    peaks = [max(abs(r[i] - supply / 2) for r in wave) for i in [1, 3, 5]]
    return {
        "differential_rms_v": rms,
        "differential_dc_v": mean,
        "buffer_positive_negative_peak_relative_to_vmid_v": peaks,
        "common_mode_input_upper_limit_v": supply - 2.25,
        "worst_signal_max_v": max(r[i] for r in wave for i in [1, 3, 5]),
        "window_s": [wave[0][0], wave[-1][0]],
        "steady_samples": len(wave),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--fetch-model",
        action="store_true",
        help="Explicit TI download; verify hash and safe directives",
    )
    args = ap.parse_args()
    output = ROOT / "build/analog/opa1656/result.json"
    output.unlink(
        missing_ok=True
    )  # Invalidate even when cache/version preflight fails.
    if args.fetch_model and not MODEL.exists():
        fetch_model()
    if not MODEL.exists():
        raise SystemExit(
            "Missing local TI model; run with --fetch-model. No substitute model allowed."
        )
    directives = audit_model(MODEL.read_bytes())
    version = subprocess.run(
        ["ngspice", "--version"], capture_output=True, text=True, check=True
    )
    simulator_version = require_simulator(version.stdout + version.stderr)
    config = json.loads(CONFIG.read_text())
    values = (
        config["stage_ohm"]
        + config["stage_feedback_capacitors_f"]
        + [config["stage_ground_capacitor_f"]]
    )
    directory = ROOT / "build/analog/opa1656"
    directory.mkdir(parents=True, exist_ok=True)
    cases = []
    for supply in [10.8, 12, 13.2]:
        for temperature in [0, 27, 70]:
            ac, warnings = run(config, directory, supply, temperature, False)
            if (
                len(ac) != 151
                or not math.isclose(ac[0][0], 10)
                or not math.isclose(ac[-1][0], 10000)
            ):
                raise ValueError("Incomplete official-model AC sweep")
            effects = [
                abs(20 * math.log10(r[1] / abs(section_response(r[0], values) ** 2)))
                for r in ac
            ]
            if max(effects) > 0.1:
                raise ValueError("Unexpected official-model filter effect")
            transient, twarnings = run(config, directory, supply, temperature, True)
            m = wave_metrics(transient, supply)
            expected = config["input_rms_v"] * abs(section_response(20, values) ** 2)
            if (
                not math.isclose(m["differential_rms_v"], expected, rel_tol=0.01)
                or abs(m["differential_dc_v"]) > 0.01
            ):
                raise ValueError("Unexpected output RMS/DC in official model")
            if m["worst_signal_max_v"] >= m["common_mode_input_upper_limit_v"]:
                raise ValueError(
                    "Model signal exceeds documented common-mode upper limit"
                )
            cases.append(
                {
                    "supply_v": supply,
                    "temperature_c": temperature,
                    "ac_points": len(ac),
                    "max_ac_difference_from_ideal_db": max(effects),
                    "convergence_warnings": sorted(set(warnings + twarnings)),
                    **m,
                }
            )
    report = {
        "status": "OFFICIAL-MODEL STUDY PASS; NOT MEASURED HARDWARE",
        "ngspice_version": simulator_version,
        "model_url": URL,
        "model_sha256": MODEL_SHA,
        "model_version": "TI Final1.3 25AUG2022 / SBOMAW6C",
        "model_pin_order": ["IN+", "IN-", "VCC", "VEE", "OUT"],
        "audit_directives": directives,
        "compatibility": "ngspice psa, child-process HOME and SPICE_USERINIT_DIR isolated",
        "config_sha256": hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
        "cases": cases,
        "VMID_physical_startup_noise_protection_qualified": False,
        "manufacturer_model_does_not_guarantee_production_extremes": True,
        "hardware_validated": False,
        "manufacturing_approved": False,
    }
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"OPA1656 official model: {len(cases)} supply/temperature cases passed; hardware NOT validated"
    )


if __name__ == "__main__":
    main()
