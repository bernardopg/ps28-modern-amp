#!/usr/bin/env python3
"""Physical VMID candidate; steady-state/stability study, explicit unsafe power-down."""

import argparse
import cmath
import hashlib
import itertools
import json
import math
import subprocess

from simulate_analog import CONFIG as ANALOG_CONFIG
from simulate_opa1656 import (
    MODEL,
    MODEL_SHA,
    ROOT,
    audit_model,
    execute_deck,
    fetch_model,
    official_deck,
    require_simulator,
)

CONFIG = ROOT / "simulation/analog/vmid-study.json"
BUILD = ROOT / "build/analog/vmid"


def reference_bounds(c, supply):
    """Independent divider/leakage corners. Leakage is an assumed bound, not an MPN spec."""
    points = []
    for st, sb, leakage in itertools.product(
        [-1, 1], [-1, 1], [0, c["reference_leakage_assumed_max_a"]]
    ):
        top = c["divider_ohm"][0] * (1 + st * c["divider_tolerance_fraction"])
        bot = c["divider_ohm"][1] * (1 + sb * c["divider_tolerance_fraction"])
        rth = top * bot / (top + bot)
        points.append(supply * bot / (top + bot) - leakage * rth)
    return min(points), max(points)


def power_down_counterexample(c, supply, fall):
    """Exact linear passive RC response to rail ramp; no opamp model below rated supply."""
    top, bot = c["divider_ohm"]
    ratio = bot / (top + bot)
    tau = top * bot / (top + bot) * c["reference_capacitance_f"]
    # Vref(t)=ratio*(V0-k*t+k*tau*(1-exp(-t/tau))) for 0<=t<=fall.
    residual = ratio * supply * tau / fall * (-math.expm1(-fall / tau))
    return {
        "aux_fall_s": fall,
        "reference_at_aux_zero_v": residual,
        "noninverting_pin_excess_over_abs_max_at_aux_zero_v": max(0, residual - 0.5),
        "input_abs_max_violated": residual > 0.5,
        "reference_stored_energy_initial_j": 0.5
        * c["reference_capacitance_f"]
        * (ratio * supply) ** 2,
    }


def circuit(c, supply, temperature, resistance, capacitance, esr, data, mode):
    top, bot = c["divider_ohm"]
    output = f"""* VMID candidate: direct REF input; not safe on hard power-down.
* TI SBOS901C fig6-36 supports isolation concept, NOT this uF load qualification.
.include "build/analog/parts/OPA1656.LIB"
.temp {temperature}
VSUP supply 0 DC {supply} AC {1 if mode == "ripple" else 0}
RTOP supply reference {top}
RBOT reference 0 {bot}
CREF reference 0 {c["reference_capacitance_f"]}
XVMID reference feedback supply 0 driver OPA1656
* Second channel of a physical dual is terminated as a follower, not left floating.
XSPARE reference spare supply 0 spare OPA1656
RISO driver mid {resistance if resistance else 0.001}
RESR mid cstorage {esr}
CMID cstorage 0 {capacitance}
"""
    if mode == "startup":
        output += ".ic v(reference)=0 v(cstorage)=0\n"
    if mode == "loop":
        output += "VINJECT feedback driver DC 0 AC 1\nILOAD mid 0 DC 0\n"
        control = f"ac dec 80 1 1g\nlet rr=real(-v(driver)/v(feedback))\nlet ri=imag(-v(driver)/v(feedback))\nwrdata {data} rr ri"
    else:
        output += "VFEEDBACK feedback driver 0\n"
        if mode == "load":
            step = c["load_step_a"]
            output += f"ILOAD mid 0 PWL(0 0 20m 0 20.01m {step} 80m {step} 80.01m {-step} 140m {-step} 140.01m 0 200m 0)\n"
            control = f"tran 2u 200m\nwrdata {data} v(mid) v(driver) v(reference)"
        elif mode == "startup":
            output += "ILOAD mid 0 0\n"
            control = f"tran 10u 500m\nwrdata {data} v(mid) v(driver) v(reference)"
        elif mode == "ripple":
            output += "ILOAD mid 0 0\n"
            control = f"ac lin 1 {c['auxiliary_ripple_test_hz']} {c['auxiliary_ripple_test_hz']}\nlet transfer=mag(v(mid))\nwrdata {data} transfer"
        elif mode == "chain":
            analog = json.loads(ANALOG_CONFIG.read_text())
            base = official_deck(analog, data, supply, temperature, transient=True)
            needle = f"VMID mid 0 {supply / 2}\n"
            if base.count(needle) != 1:
                raise ValueError("Unexpected ideal VMID source in original chain")
            network = output[output.index("RTOP") :]
            base = base.replace(needle, network)
            return base.replace(
                f"wrdata {data} v(buffered) v(positive) v(negative)",
                f"wrdata {data} v(mid) v(positive) v(negative) v(driver)",
            )
        else:
            raise ValueError("Unknown VMID test mode")
    return output + f".control\nset numdgt=15\n{control}\nquit\n.endc\n.end\n"


def reference_startup_settling(c, supply, resistance):
    """Two-pole ideal RC step, not opamp power-on behavior (ESR neglected)."""
    top, bot = c["divider_ohm"]
    tr = top * bot / (top + bot) * c["reference_capacitance_f"]
    tm = resistance * c["reservoir_capacitance_f"]
    target = supply * bot / (top + bot)

    def error(t):
        return target * (tr * math.exp(-t / tr) - tm * math.exp(-t / tm)) / (tr - tm)

    lo, hi = 0, 2
    for _ in range(70):
        mid = (lo + hi) / 2
        if error(mid) > c["proposed_settling_error_v"]:
            lo = mid
        else:
            hi = mid
    return hi


def differential_metrics(rows):
    steady = [r for r in rows if r[0] >= 0.25]
    if len(steady) < 500 or steady[-1][0] < 0.349:
        raise ValueError("Incomplete chain transient")
    duration = steady[-1][0] - steady[0][0]
    mean = power = 0
    for a, b in itertools.pairwise(steady):
        dt = b[0] - a[0]
        if dt <= 0:
            raise ValueError("Nonmonotonic time samples")
        va, vb = a[3] - a[5], b[3] - b[5]
        mean += dt * (va + vb) / 2
        power += dt * (va * va + vb * vb) / 2
    mean /= duration
    return math.sqrt(max(0, power / duration - mean * mean)), mean, steady


def loop_metrics(rows):
    if (
        len(rows) != 721
        or not math.isclose(rows[0][0], 1)
        or not math.isclose(rows[-1][0], 1e9)
    ):
        raise ValueError("Incomplete return-ratio sweep")
    unwrapped = []
    previous = None
    for r in rows:
        value = complex(r[1], r[3])
        angle = cmath.phase(value) * 180 / math.pi
        if previous is not None:
            while angle - previous > 180:
                angle -= 360
            while angle - previous < -180:
                angle += 360
        unwrapped.append(angle)
        previous = angle
    crossings = []
    for i, (a, b) in enumerate(itertools.pairwise(rows)):
        ga, gb = abs(complex(a[1], a[3])), abs(complex(b[1], b[3]))
        if ga >= 1 > gb:
            weight = math.log(ga) / (math.log(ga) - math.log(gb))
            frequency = math.exp(math.log(a[0]) + weight * math.log(b[0] / a[0]))
            phase = unwrapped[i] + weight * (unwrapped[i + 1] - unwrapped[i])
            crossings.append(
                {"crossover_hz": frequency, "phase_margin_deg": 180 + phase}
            )
    if len(crossings) != 1:
        raise ValueError(
            "Ambiguous return ratio; do not report a fabricated phase margin"
        )
    return crossings[0]


def load_metrics(rows, supply, resistance, c):
    if rows[-1][0] < 0.199 or len(rows) < 1000:
        raise ValueError("Incomplete load transient")
    result = {}
    for name, lo, hi, expected in [
        ("sink", 0.06, 0.075, supply / 2 - resistance * c["load_step_a"]),
        ("source", 0.12, 0.135, supply / 2 + resistance * c["load_step_a"]),
    ]:
        values = [r[1] for r in rows if lo <= r[0] <= hi]
        if not values:
            raise ValueError("Missing steady load samples")
        mean = sum(values) / len(values)
        if abs(mean - expected) > 0.002:
            raise ValueError("VMID DC load disagrees with independent Ohm law")
        result[name + "_steady_v"] = mean
    result["max_error_from_half_supply_v"] = max(abs(r[1] - supply / 2) for r in rows)
    result["driver_max_error_from_reference_v"] = max(abs(r[3] - r[5]) for r in rows)
    return result


def run(c, supply, temperature, resistance, capacitance, esr, mode):
    name = f"{mode}-v{supply:g}-t{temperature:g}-r{resistance:g}-c{capacitance:g}-esr{esr:g}"
    data = (BUILD / (name + ".dat")).relative_to(ROOT)
    rows, warnings = execute_deck(
        circuit(c, supply, temperature, resistance, capacitance, esr, data, mode),
        BUILD,
        name,
    )
    return rows, warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fetch-model", action="store_true")
    args = ap.parse_args()
    report = BUILD / "result.json"
    report.unlink(missing_ok=True)
    if args.fetch_model and not MODEL.exists():
        fetch_model()
    if not MODEL.exists():
        raise SystemExit("Missing audited TI model; use --fetch-model")
    audit_model(MODEL.read_bytes())
    version = subprocess.run(
        ["ngspice", "--version"], capture_output=True, text=True, check=True
    )
    ngversion = require_simulator(version.stdout + version.stderr)
    c = json.loads(CONFIG.read_text())
    BUILD.mkdir(parents=True, exist_ok=True)
    loops = []
    loads = []
    warnings = set()
    for supply, temp, resistance, capacitance, esr in itertools.product(
        [10.8, 13.2],
        [0, 70],
        c["isolation_candidates_ohm"],
        c["reservoir_capacitance_candidates_f"],
        c["reservoir_esr_assumed_candidates_ohm"],
    ):
        rows, w = run(c, supply, temp, resistance, capacitance, esr, "loop")
        warnings.update(w)
        m = loop_metrics(rows)
        loops.append(
            {
                "supply_v": supply,
                "temperature_c": temp,
                "isolation_ohm": resistance,
                "reservoir_f": capacitance,
                "assumed_esr_ohm": esr,
                **m,
            }
        )
    for supply in [10.8, 12, 13.2]:
        rows, w = run(c, supply, 27, 25, c["reservoir_capacitance_f"], 0.05, "load")
        warnings.update(w)
        loads.append({"supply_v": supply, **load_metrics(rows, supply, 25, c)})
    rows, w = run(c, 12, 27, 0, c["reservoir_capacitance_f"], 0.05, "loop")
    warnings.update(w)
    no_isolation = loop_metrics(rows)
    if (
        no_isolation["phase_margin_deg"]
        >= c["proposed_return_ratio_phase_margin_min_deg"]
    ):
        raise ValueError("Expected no-isolation counterexample missing")
    rows, w = run(c, 12, 27, 25, c["reservoir_capacitance_f"], 0.05, "ripple")
    warnings.update(w)
    ripple = rows[0][1] * c["auxiliary_ripple_test_peak_v"]
    s = complex(0, 2 * math.pi * c["auxiliary_ripple_test_hz"])
    rt, rb = c["divider_ohm"]
    ct = c["reference_capacitance_f"]
    cm = c["reservoir_capacitance_f"]
    analytical_ripple = (
        abs(
            rb
            / (rt + rb)
            / (1 + s * rt * rb / (rt + rb) * ct)
            * (1 + s * 0.05 * cm)
            / (1 + s * (25 + 0.05) * cm)
        )
        * c["auxiliary_ripple_test_peak_v"]
    )
    if not math.isclose(ripple, analytical_ripple, rel_tol=0.01):
        raise ValueError("Ripple disagrees with independent RC transfer")
    startups = []
    for supply in [10.8, 12, 13.2]:
        rows, w = run(c, supply, 27, 25, c["reservoir_capacitance_f"], 0.05, "startup")
        warnings.update(w)
        if rows[-1][0] < 0.499:
            raise ValueError("Incomplete startup window")
        last_bad = max(
            (
                r[0]
                for r in rows
                if abs(r[1] - supply / 2) > c["proposed_settling_error_v"]
            ),
            default=0,
        )
        analytical = reference_startup_settling(c, supply, 25)
        if abs(last_bad - analytical) > 0.01:
            raise ValueError("Startup disagrees with independent passive step")
        startups.append(
            {
                "supply_v": supply,
                "modeled_last_outside_10mv_window_s": last_bad,
                "ideal_two_pole_settling_s": analytical,
                "driver_current_peak_a": max(abs(r[3] - r[1]) / 25 for r in rows),
                "aux_already_valid_before_test": True,
            }
        )
    chains = []
    for supply in [10.8, 12, 13.2]:
        rows, w = run(c, supply, 27, 25, c["reservoir_capacitance_f"], 0.05, "chain")
        warnings.update(w)
        rms, dc, steady = differential_metrics(rows)
        if not 1.97 < rms < 2.02 or abs(dc) > 0.01:
            raise ValueError("Unexpected full-chain differential RMS/DC")
        chains.append(
            {
                "supply_v": supply,
                "differential_rms_v_time_weighted": rms,
                "differential_dc_v": dc,
                "vmid_driver_current_peak_a": max(
                    abs(r[7] - r[1]) / 25 for r in steady
                ),
                "vmid_peak_error_from_half_supply_v": max(
                    abs(r[1] - supply / 2) for r in steady
                ),
                "biased_input_tracks_vmid_in_this_test": True,
            }
        )
    counterexamples = [
        power_down_counterexample(c, 12, t)
        for t in c["hard_power_down_fall_candidates_s"]
    ]
    minimum_margin = min(x["phase_margin_deg"] for x in loops)
    if minimum_margin < c["proposed_return_ratio_phase_margin_min_deg"]:
        raise ValueError("Candidate model stability criterion failed")
    if max(x["max_error_from_half_supply_v"] for x in loads) > 0.1:
        raise ValueError("Candidate load window failed")
    lower, upper = reference_bounds(c, 13.2)
    worst = (
        max(abs(lower - 6.6), abs(upper - 6.6))
        + max(c["isolation_candidates_ohm"]) * c["load_step_a"]
    )
    if worst > c["proposed_dc_error_limit_v"]:
        raise ValueError("Assumed leakage/divider/load budget failed")
    if not any(x["input_abs_max_violated"] for x in counterexamples):
        raise ValueError("Expected safety counterexample missing")
    output = {
        "status": "STEADY-STATE MODEL STUDY PASS; HARD POWER-DOWN UNSAFE/BLOCKED",
        "ngspice_version": ngversion,
        "manufacturer_model_sha256": MODEL_SHA,
        "config_sha256": hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(
            (ROOT / "scripts/simulate_vmid.py").read_bytes()
        ).hexdigest(),
        "shared_runner_sha256": hashlib.sha256(
            (ROOT / "scripts/simulate_opa1656.py").read_bytes()
        ).hexdigest(),
        "analog_config_sha256": hashlib.sha256(ANALOG_CONFIG.read_bytes()).hexdigest(),
        "return_ratio_cases": loops,
        "minimum_modeled_phase_margin_deg": minimum_margin,
        "load_cases": loads,
        "no_isolation_counterexample": no_isolation,
        "rail_ripple_100mv_peak_100hz_to_vmid_peak_v": ripple,
        "independent_analytical_rail_ripple_to_vmid_peak_v": analytical_ripple,
        "startup_cases_aux_already_valid": startups,
        "coupled_lr4_cases": chains,
        "reference_corner_range_at_13_2_v": [lower, upper],
        "assumed_worst_reference_and_load_dc_error_v": worst,
        "hard_power_down_passive_counterexamples": counterexamples,
        "convergence_warnings": sorted(warnings),
        "macro_below_recommended_supply_used": False,
        "startup_power_down_input_clamps_or_backfeed_qualified": False,
        "exact_mpn_esr_leakage_or_footprint_qualified": False,
        "hardware_validated": False,
        "manufacturing_approved": False,
    }
    report.write_text(json.dumps(output, indent=2) + "\n")
    print(
        f"VMID: {len(loops)} modeled return-ratio cases; min PM={minimum_margin:.2f} deg; power-down BLOCKED"
    )


if __name__ == "__main__":
    main()
