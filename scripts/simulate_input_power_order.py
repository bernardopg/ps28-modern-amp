#!/usr/bin/env python3
"""RC hypotheses, unsafe regressions and an UNREALIZED input isolation contract.

No TI opamp/TPA macro is used. Off-state input impedance/bias and driver behavior
are hypotheses, not vendor guarantees. Success means required counterexamples
were found and checked; it NEVER means the existing hardware is protected.
"""

import hashlib
import itertools
import json
import math
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "simulation/analog/input-power-order.json"
CIRCUIT = ROOT / "simulation/analog/input-coupling.cir"
BUILD = ROOT / "build/analog/input-power-order"


def validate(c):
    if c["input_absolute_limits_v"] != [-0.3, 7.0]:
        raise ValueError("TPA input ratings must remain -0.3..7 V relative to GND")
    for key in (
        "hypothesis_capacitances_f",
        "hypothesis_return_resistances_ohm",
        "hypothesis_driver_falls_s",
    ):
        if not c[key] or any(not math.isfinite(v) or v <= 0 for v in c[key]):
            raise ValueError(f"Invalid hypothesis: {key}")
    if any(
        not math.isfinite(v) or v < 0 for v in c["hypothesis_series_resistances_ohm"]
    ):
        raise ValueError("Invalid series resistance")
    for key in (
        "hypothesis_initial_receiver_bias_v",
        "hypothesis_receiver_first_delays_s",
    ):
        if not c[key] or any(not math.isfinite(v) or v < 0 for v in c[key]):
            raise ValueError(f"Invalid hypothesis: {key}")
    if any(v > 7 for v in c["hypothesis_initial_receiver_bias_v"]):
        raise ValueError("Initial bias hypothesis exceeds TPA input absolute rating")
    window = c["startup_qualified_dc_window_v"]
    if (
        len(window) != 2
        or not all(math.isfinite(v) for v in window)
        or not 0 < window[0] < window[1] < 7
    ):
        raise ValueError("Invalid proposed startup DC window")
    if c["coupling_nominal_f"] != 10e-6:
        raise ValueError("Native C20/C21 nominal must remain 10 uF")
    for key in ("signal_peak_v", "signal_frequency_hz", "startup_receiver_bias_v"):
        if not math.isfinite(c[key]) or c[key] <= 0:
            raise ValueError(f"Invalid source/startup hypothesis: {key}")
    if not (0 < c["driver_final_v"] < c["driver_initial_v"]):
        raise ValueError("Driver fall must be positive and decreasing")
    # Even this proxy must not silently extrapolate powered OPA behavior.
    if 2 * c["driver_final_v"] < 4.5:
        raise ValueError("Proxy extends below the powered-supply study boundary")


def advance(v, source_delta, bias_start, bias_delta, dt, capacitance, rin, rs=0):
    """Exact first-order response to linear source and bias segments.

    dv/dt+v/tau = k*dsource/dt+(1-k)*dbias/dt+bias/tau.
    A discontinuity needs the corresponding k*delta_source+(1-k)*delta_bias.
    """
    if not all(
        math.isfinite(x)
        for x in (v, source_delta, bias_start, bias_delta, dt, capacitance, rin, rs)
    ):
        raise ValueError("Nonfinite RC input")
    if min(dt, capacitance, rin) <= 0 or rs < 0:
        raise ValueError("Invalid RC parameters")
    tau, k = (rin + rs) * capacitance, rin / (rin + rs)
    one_minus_a = -math.expm1(-dt / tau)
    return (
        v * (1 - one_minus_a)
        + bias_start * one_minus_a
        + bias_delta / dt * (dt - tau * one_minus_a)
        + (k * source_delta + (1 - k) * bias_delta) * tau / dt * one_minus_a
    )


def loss_case(c, cap, rin, rs, bias, delay, fall):
    k, tau = rin / (rin + rs), (rin + rs) * cap
    # Bias drops instantly from bias to zero; the series R adds feedthrough.
    initial = k * bias * math.exp(-delay / tau)
    end = advance(
        initial, c["driver_final_v"] - c["driver_initial_v"], 0, 0, fall, cap, rin, rs
    )
    low, high = c["input_absolute_limits_v"]
    return {
        "capacitance_f": cap,
        "return_resistance_ohm": rin,
        "series_resistance_ohm": rs,
        "initial_receiver_bias_v": bias,
        "receiver_first_delay_s": delay,
        "driver_fall_s": fall,
        "minimum_input_v": min(initial, end),
        "maximum_input_v": max(bias, initial, end),
        "violates_input_voltage_rating": not (low <= end <= high),
    }


def startup(c, muted_precharge):
    """Cold connection can fail even with a perfectly powered source/receiver.

    Right coupling plate starts at GND. The hypothesized receiver bias has an
    RIN=20k return; actual TI precharge circuitry is NOT modeled. Qualified
    precharge is evaluated as an ideal observation, not a fixed timer.
    """
    cap, rin, rs = c["coupling_nominal_f"], 20000, 0
    bias = c["startup_receiver_bias_v"]
    threshold = c["startup_qualified_dc_window_v"][0]
    if not 0 < threshold < bias:
        raise ValueError("Precharge window unreachable in this hypothesis")
    ready = -rin * cap * math.log1p(-threshold / bias) if muted_precharge else 0
    dt, stop = 10e-6, 0.5
    v, source = 0.0, c["driver_initial_v"]
    if not muted_precharge:
        source += c["signal_peak_v"]  # close at a signal crest, then fall
    values = [v]
    for n in range(1, round(stop / dt) + 1):
        t = n * dt
        next_source = c["driver_initial_v"]
        if t >= ready:
            phase = 0 if muted_precharge else math.pi / 2
            next_source += c["signal_peak_v"] * math.sin(
                2 * math.pi * c["signal_frequency_hz"] * (t - ready) + phase
            )
        v = advance(v, next_source - source, bias, 0, dt, cap, rin, rs)
        values.append(v)
        source = next_source
    low, high = c["input_absolute_limits_v"]
    return {
        "muted_until_ideal_dc_window": muted_precharge,
        "hypothetical_ready_s": ready,
        "minimum_input_v": min(values),
        "maximum_input_v": max(values),
        "violates_input_voltage_rating": not (
            low <= min(values) and max(values) <= high
        ),
    }


def isolation_bound(c):
    """Requirements arithmetic only; no actual switch or supervisor selected."""
    x = c["isolation_contract_requirements_not_measured"]
    if any(not math.isfinite(v) or v < 0 for v in x.values()):
        raise ValueError("Invalid isolation requirement")
    if x["minimum_margin_to_absolute_v"] < 0.05:
        raise ValueError("Do not relax the proposed 50 mV safety margin")
    cp = x["minimum_added_pin_capacitance_f"]
    if cp <= 0:
        raise ValueError("Added receiver-side capacitance must be positive")
    contributions = {
        "driver_step_v": x["maximum_driver_step_v"],
        "latency_slew_v": x["maximum_driver_slew_v_per_s"]
        * x["maximum_detection_and_open_delay_s"],
        "charge_injection_v": x["maximum_charge_injection_c"] / cp,
        "off_feedthrough_v": x["maximum_off_capacitance_f"]
        * x["maximum_isolated_plate_excursion_v"]
        / cp,
        "off_leakage_v": x["maximum_off_leakage_a"]
        * x["maximum_external_return_resistance_ohm"],
        "preclose_plate_error_v": x["maximum_preclose_plate_error_v"],
    }
    excursion = sum(contributions.values())
    low, high = c["input_absolute_limits_v"]
    dc_low, dc_high = c["startup_qualified_dc_window_v"]
    minimum_margin = min(
        -low - excursion,
        dc_low - c["signal_peak_v"] - excursion - low,
        high - dc_high - c["signal_peak_v"] - excursion,
    )
    return {
        "contributions_v": contributions,
        "total_excursion_bound_v": excursion,
        "minimum_margin_to_absolute_v": minimum_margin,
        "passes_if_all_unmeasured_requirements_hold": minimum_margin
        >= x["minimum_margin_to_absolute_v"],
        "hardware_implemented_or_qualified": False,
    }


def audit_interfaces(core, analog):
    parts = {p["ref"]: p for p in core["parts"]}
    for ref, drive, receive in (
        ("C20", "DIFF_P", "INPUT_A_AC"),
        ("C21", "DIFF_N", "INPUT_B_AC"),
    ):
        if parts[ref]["nets"] != {"1": drive, "2": receive} or not parts[ref][
            "value"
        ].startswith("10uF "):
            raise ValueError(f"Core coupling topology changed: {ref}")
    frontend = {p["ref"]: p for p in analog["parts"]}
    if frontend["J102"]["nets"] != {
        "1": "DIFF_POS",
        "2": "DIFF_NEG",
        "3": "VMID",
        "4": "GND",
    }:
        raise ValueError("Differential analog interface changed")
    return {
        "core_refs": ["C20", "C21"],
        "source_ref": "J102",
        "audit_level": "Manifest only; native KiCad electrical audits remain separate",
        "mapping_for_review_only": {"DIFF_POS": "DIFF_P", "DIFF_NEG": "DIFF_N"},
        "schematics_connected_or_modified": False,
    }


def oracle(t, cap, rin, rs):
    """Analytical segments corresponding to the independently authored deck."""
    bias = 3.875
    if t <= 0.02:
        return bias
    d = min(t - 0.02, 1e-6)
    v = advance(bias, 0, bias, -bias * d / 1e-6, d, cap, rin, rs)
    if t <= 0.020001:
        return v
    d = min(t, 0.12) - 0.020001
    v = advance(v, 0, 0, 0, d, cap, rin, rs)
    if t <= 0.12:
        return v
    d = min(t, 0.15) - 0.12
    v = advance(v, -2.75 * d / 0.03, 0, 0, d, cap, rin, rs)
    if t <= 0.15:
        return v
    return advance(v, 0, 0, 0, t - 0.15, cap, rin, rs)


def simulate_passive(name, text, columns, stop):
    """Independent ngspice runner; isolated HOME and no retained success/data."""
    data = BUILD / (name + ".dat")
    data.unlink(missing_ok=True)
    deck = BUILD / (name + ".cir")
    deck.write_text(text)
    with tempfile.TemporaryDirectory(prefix="ps28-rc-spice-") as home:
        Path(home, ".spiceinit").write_text("* Isolated passive RC study\n")
        env = dict(os.environ, HOME=home, SPICE_USERINIT_DIR=home)
        p = subprocess.run(
            ["ngspice", "-b", str(deck)],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )
    (BUILD / (name + ".log")).write_text(p.stdout + p.stderr)
    if p.returncode or not data.exists():
        raise RuntimeError(f"Passive RC simulation failed: {name}")
    rows = [
        tuple(map(float, line.split()))
        for line in data.read_text().splitlines()
        if line.strip()
    ]
    if (
        len(rows) < 1000
        or any(len(r) != columns or not all(map(math.isfinite, r)) for r in rows)
        or rows[-1][0] < stop - 1e-6
        or any(b[0] <= a[0] for a, b in itertools.pairwise(rows))
    ):
        raise ValueError(f"Incomplete or invalid RC output: {name}")
    return rows


def crosscheck():
    results = []
    for cap, rin, rs in [
        (10e-6, 20000, 0),
        (1e-6, 20000, 0),
        (12e-6, 40000, 0),
        (10e-6, 20000, 1000),
    ]:
        name = f"rc-c{cap:g}-r{rin:g}-s{rs:g}"
        data = BUILD / (name + ".dat")
        data.unlink(missing_ok=True)
        text = CIRCUIT.read_text().replace("C20 driver tp 10u", f"C20 driver tp {cap}")
        text = text.replace("RIN tp bias 20k", f"RIN tp bias {rin}")
        if rs:
            text = text.replace("C20 driver tp", "C20 driver store")
            text = text.replace("RIN tp bias", f"RSERIES store tp {rs}\nRIN tp bias")
        control = (
            ".control\nset numdgt=15\nset wr_singlescale\n"
            f"tran 2u .35\nwrdata {data.relative_to(ROOT)} v(tp)\nquit\n.endc\n.end\n"
        )
        rows = simulate_passive(name, text.removesuffix(".end\n") + control, 2, 0.35)
        error = max(abs(v - oracle(t, cap, rin, rs)) for t, v in rows)
        if error > 0.002:
            raise ValueError(f"SPICE/analytical disagreement {name}: {error} V")
        results.append(
            {
                "name": name,
                "points_checked": len(rows),
                "maximum_analytical_error_v": error,
                "minimum_input_v": min(v for _, v in rows),
            }
        )
    return results


def coupled_rail_cases(c):
    """Reuse unchanged D-018 passive supply; analyze receiver proxy at VANA>=4.5.

    BTRACK is a hypothetical follower, not an opamp model. Below 4.5 V no
    prediction about opamp behavior is made and those points are not assessed.
    """
    import simulate_vmid_protection as protection

    pc = json.loads(protection.CONFIG.read_text())
    if not protection.invariant(pc)["pass_under_declared_envelope"]:
        raise ValueError("D-018 rail proof no longer passes")
    results = []
    for bias in (0, 3.875):
        name = f"coupled-bias{bias:g}"
        data = (BUILD / (name + ".dat")).relative_to(ROOT)
        text = protection.passive_deck(pc, 12, 0.0001, 0, data)
        old = f"wrdata {data} v(supply) v(mid) v(astore) v(raw)"
        if text.count(old) != 1 or text.count(".control\n") != 1:
            raise ValueError("D-018 passive deck interface changed")
        extra = (
            "BTRACK driver 0 V=V(mid)\n"
            f"VBIAS bias 0 PWL(0 {bias} .02 {bias} .020001 0 .45 0)\n"
            "C20 driver tp 10u\nRIN tp bias 20k\n"
        )
        text = text.replace(".control\n", extra + ".control\nset wr_singlescale\n")
        text = text.replace(old, f"wrdata {data} v(supply) v(mid) v(tp) v(bias)")
        rows = simulate_passive(name, text, 5, 0.45)
        v, error = rows[0][3], 0.0
        for a, b in itertools.pairwise(rows):
            v = advance(v, b[2] - a[2], a[4], b[4] - a[4], b[0] - a[0], 10e-6, 20000)
            error = max(error, abs(v - b[3]))
        if error > 0.002:
            raise ValueError(
                f"Coupled input RC/independent integration disagreement: {error}"
            )
        valid = [r for r in rows if r[1] >= 4.5]
        if len(valid) < 1000 or not all(-0.5 <= r[2] <= r[1] + 0.5 for r in rows):
            raise ValueError("Incomplete powered window or D-018 VMID violation")
        lowest = min(valid, key=lambda r: r[3])
        results.append(
            {
                "name": name,
                "points_checked": len(rows),
                "receiver_initial_bias_hypothesis_v": bias,
                "minimum_input_at_analog_supply_ge_4_5_v": lowest[3],
                "analog_supply_at_minimum_v": lowest[1],
                "time_at_minimum_s": lowest[0],
                "maximum_independent_integration_error_v": error,
                "vmid_input_voltage_envelope_passes": True,
                "violates_tpa_input_rating_in_powered_analog_window": lowest[3]
                < c["input_absolute_limits_v"][0],
            }
        )
    if not results[0]["violates_tpa_input_rating_in_powered_analog_window"]:
        raise ValueError("Required coupled counterexample vanished")
    return results


def study(c):
    validate(c)
    keys = (
        "hypothesis_capacitances_f",
        "hypothesis_return_resistances_ohm",
        "hypothesis_series_resistances_ohm",
        "hypothesis_initial_receiver_bias_v",
        "hypothesis_receiver_first_delays_s",
        "hypothesis_driver_falls_s",
    )
    cases = [loss_case(c, *args) for args in itertools.product(*(c[k] for k in keys))]
    cold, precharged = startup(c, False), startup(c, True)
    bound = isolation_bound(c)
    native = loss_case(c, 10e-6, 20000, 0, 3.875, 0.1, 0.03)
    series = loss_case(c, 10e-6, 20000, 1000, 0, 0, 0.02)
    # Upstream opening with an unqualified switch clamping the left plate to GND.
    upstream_counterexample = -c["driver_initial_v"]
    if (
        not native["violates_input_voltage_rating"]
        or not series["violates_input_voltage_rating"]
        or not cold["violates_input_voltage_rating"]
        or precharged["violates_input_voltage_rating"]
        or not bound["passes_if_all_unmeasured_requirements_hold"]
        or upstream_counterexample >= c["input_absolute_limits_v"][0]
    ):
        raise ValueError("Required unsafe/safe-hypothesis regression changed")
    return {
        "case_count": len(cases),
        "violating_hypothesis_cases": sum(
            x["violates_input_voltage_rating"] for x in cases
        ),
        "worst_hypothesis": min(cases, key=lambda x: x["minimum_input_v"]),
        "native_value_counterexample": native,
        "series_resistor_counterexample": series,
        "upstream_switch_clamped_plate_counterexample_v": upstream_counterexample,
        "cold_connect_with_audio": cold,
        "muted_observed_precharge": precharged,
        "unrealized_isolation_contract": bound,
    }


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    report = BUILD / "result.json"
    report.unlink(missing_ok=True)
    c = json.loads(CONFIG.read_text())
    core = ROOT / "kicad/core-selected/core-manifest.json"
    analog = ROOT / "kicad/analog-protected/vmid-manifest.json"
    result = study(c)
    result["interfaces"] = audit_interfaces(
        json.loads(core.read_text()), json.loads(analog.read_text())
    )
    result["independent_passive_spice"] = crosscheck()
    result["coupled_d018_rail_receiver_hypotheses"] = coupled_rail_cases(c)
    hashes = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (
            CONFIG,
            CIRCUIT,
            Path(__file__),
            core,
            analog,
            core.with_name("ps28-modern.kicad_sch"),
            analog.with_name("analog-protected.kicad_sch"),
            ROOT / "simulation/analog/vmid-protection.json",
            ROOT / "scripts/simulate_vmid_protection.py",
            ROOT / "scripts/simulate_opa1656.py",
        )
    }
    source_checks = []
    for source in c["sources"]:
        p = ROOT / source["file"]
        present = p.exists()
        if present and hashlib.sha256(p.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError(f"Reviewed primary source changed: {p}")
        source_checks.append({**source, "local_pdf_hash_rechecked": present})
    result.update(
        classification=c["classification"],
        hashes=hashes,
        sources=source_checks,
        actual_poweroff_impedance_bias_driver_behavior_characterized=False,
        vendor_macro_executed=False,
        existing_interface_protected=False,
        hardware_validated=False,
    )
    report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(
        f"RC input: {result['case_count']} hypotheses, four RC comparisons + two coupled passive networks; "
        "required unsafe cases reproduced. Existing interface NOT protected."
    )


if __name__ == "__main__":
    main()
