#!/usr/bin/env python3
"""D-018: isolated analog rail and passive VMID; no unpowered opamp macro assumptions."""

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
    official_deck,
    require_simulator,
)
from simulate_vmid import differential_metrics

CONFIG = ROOT / "simulation/analog/vmid-protection.json"
BUILD = ROOT / "build/analog/vmid-protection"


def validate(c):
    names = [
        "maximum_raw_v",
        "input_filter_ohm",
        "raw_bleed_ohm",
        "analog_bleed_ohm",
        "bulk_capacitance_f",
        "bulk_capacitance_min_f",
        "bulk_esr_envelope_max_ohm",
        "mid_capacitance_f",
        "mid_capacitance_envelope_max_f",
        "mid_esr_envelope_max_ohm",
        "total_active_and_bulk_leakage_max_a",
        "mid_total_load_max_a",
        "internal_storage_guard_v",
    ]
    if (
        any(c[n] <= 0 for n in names)
        or c["divider_ohm"][0] != c["divider_ohm"][1]
        or not 0 <= c["divider_tolerance"] < 0.1
        or not 0 <= c["filter_tolerance"] < 0.1
    ):
        raise ValueError("Invalid physical envelope")
    if (
        c["bulk_capacitance_min_f"] > c["bulk_capacitance_f"]
        or c["mid_capacitance_envelope_max_f"] < c["mid_capacitance_f"]
    ):
        raise ValueError("Invalid storage corners")
    rows = {
        s.split()[0]: float(s.split()[3])
        for s in (ROOT / "simulation/analog/vmid-protected.cir")
        .read_text()
        .splitlines()
        if s and s[0] in "RC"
    }
    actual = [
        rows["R201"],
        rows["R202"],
        rows["R203"],
        rows["R204"] + rows["R205"],
        rows["R206"] + rows["R207"],
        rows["C201"] + rows["C202"],
        rows["C203"],
    ]
    expected = [
        c["input_filter_ohm"],
        c["raw_bleed_ohm"],
        c["analog_bleed_ohm"],
        *c["divider_ohm"],
        c["bulk_capacitance_f"],
        c["mid_capacitance_f"],
    ]
    if actual != expected:
        raise ValueError("Safety envelope and independent physical topology disagree")


def invariant(c):
    """Conservative inward vector-field bound for MID capacitor vs analog bulk storage.

    All components positive; AUX<=Vmax, isolated forward path, bounded leakage/load.
    No assumption about a VMID amplifier's state: that amplifier was removed.
    ESR offsets are bounded separately; includes worst charging and discharging.
    """
    vmax = c["maximum_raw_v"]
    tol = c["divider_tolerance"]
    rtmin = c["divider_ohm"][0] * (1 - tol)
    rtmax = c["divider_ohm"][0] * (1 + tol)
    rthmax = rtmax / 2
    ratio_max = (1 + tol) / 2
    rfmin = c["input_filter_ohm"] * (1 - c["filter_tolerance"])
    bleedmin = c["analog_bleed_ohm"] * (1 - tol)
    ea, em = c["bulk_esr_envelope_max_ohm"], c["mid_esr_envelope_max_ohm"]
    il = c["mid_total_load_max_a"]
    ia = c["total_active_and_bulk_leakage_max_a"]
    ir = c["diode_reverse_envelope_a"]
    guard = c["internal_storage_guard_v"]
    # Positive charging current cannot exceed this even with zero diode drop.
    charge_offset = ea * (vmax / rfmin + (vmax + guard) / rtmin)
    # At upper storage boundary, bound top-resistor current (may feed ANA back).
    ratio_min = 1 - ratio_max
    top_delta = max(0, charge_offset - guard) + em / (rtmin / 2 + em) * (
        (1 - ratio_min) * vmax + rthmax * il
    )
    bulk_decay = (ia + vmax / bleedmin + ir + top_delta / rtmin) / c[
        "bulk_capacitance_min_f"
    ]
    mid_decay = (guard - ratio_max * charge_offset - rthmax * il) / (
        (rthmax + em) * c["mid_capacitance_envelope_max_f"]
    )
    # Maximum downward terminal jump from analog bulk's series ESR.
    discharge_current = ia + vmax / bleedmin + ir + vmax / rtmin
    terminal_excess = guard + ea * discharge_current
    lower_inward = (guard - rthmax * il) / (
        (rthmax + em) * c["mid_capacitance_envelope_max_f"]
    )
    passed = (
        mid_decay > bulk_decay
        and terminal_excess < c["input_absolute_allowance_v"]
        and lower_inward > 0
    )
    return {
        "upper_boundary_inward_margin_v_per_s": mid_decay - bulk_decay,
        "mid_upper_boundary_decay_min_v_per_s": mid_decay,
        "bulk_boundary_decay_max_v_per_s": bulk_decay,
        "lower_boundary_inward_v_per_s": lower_inward,
        "max_mid_excess_over_analog_terminal_v": terminal_excess,
        "charging_esr_offset_bound_v": charge_offset,
        "forward_current_bound_a": vmax / rfmin,
        "raw_aux_ghost_voltage_bound_v": ir
        * c["raw_bleed_ohm"]
        * (1 + c["raw_bleed_total_tolerance"]),
        "pass_under_declared_envelope": passed,
    }


def steady(c, raw, active, vf, rt=None, rb=None):
    rt = rt or c["divider_ohm"][0]
    rb = rb or c["divider_ohm"][1]
    rf = c["input_filter_ohm"] * (1 + c["filter_tolerance"])
    return (raw - vf - rf * active) / (
        1
        + rf
        * (1 / (rt + rb) + 1 / (c["analog_bleed_ohm"] * (1 - c["divider_tolerance"])))
    )


def ripple(c, f, bulk, rf, ea, mid, em, rt, rb):
    """Independent nodal transfer, including capacitor ESR and divider loading."""
    s = complex(0, 2 * math.pi * f)
    ya = s * bulk / (1 + s * ea * bulk)
    ym = 1 / rb + s * mid / (1 + s * em * mid)
    a = 1 / rf + 1 / c["analog_bleed_ohm"] + ya + 1 / rt
    d = ym + 1 / rt
    return (1 / rf / rt) / (a * d - 1 / rt**2)


def network(c, name="mid", supply="supply"):
    return f"RTOP {supply} {name} {c['divider_ohm'][0]}\nRBOT {name} 0 {c['divider_ohm'][1]}\nRESR {name} midstore {c['mid_esr_envelope_max_ohm']}\nCMID midstore 0 {c['mid_capacitance_f']}\n"


def passive_deck(c, raw, fall, load, data, bypass=False, stress=False, floating=False):
    # BPATH is an envelope equivalent of diode + series resistor, NOT a vendor model.
    # Active load tapers to zero with voltage; below 4.5 V no TI macro is executed.
    tail = 0.12 + max(fall, 0.000001)
    source = f"VRAW raw 0 PWL(0 {raw} .12 {raw} {tail} 0 .45 0)\n"
    if stress:
        source = f"VRAW raw 0 PWL(0 0 .005 0 .005001 {raw} .05 {raw} .050001 3 .08 3 .080001 {raw} .13 {raw} .130001 0 .30 0 .300001 {raw} .45 {raw})\n.ic V(astore)=0 V(midstore)=0\n"
    if floating:
        source = (
            source.replace("VRAW raw", "VRAW driver")
            + "VCTRL ctrl 0 PWL(0 1 .12 1 .120001 0 .45 0)\nSOPEN driver raw ctrl 0 DISCONNECT\n.model DISCONNECT SW(Ron=.001 Roff=1e12 Vt=.5 Vh=0)\n"
        )
    if bypass:
        path = "VUNSAFE raw supply 0\n"
    else:
        path = f"BPATH raw supply I=max(0,(V(raw,supply)-{c['diode_forward_assumed_max_v']})/{c['input_filter_ohm']})-{c['diode_reverse_envelope_a']}*min(1,max(0,V(supply,raw)/.001))\n"
    return f"""* D-018 envelope study; no manufacturer model in power-down
{source}{path}RAWBLEED raw 0 {c["raw_bleed_ohm"]}
RABLEED supply 0 {c["analog_bleed_ohm"]}
BLOAD supply 0 I={c["total_active_and_bulk_leakage_max_a"]}*min(1,max(0,V(supply)/4.5))
RAESR supply astore {c["bulk_esr_envelope_max_ohm"]}
CA astore 0 {c["bulk_capacitance_min_f"]}
{network({**c, "mid_capacitance_f": c["mid_capacitance_envelope_max_f"]})}BIMID mid 0 I={str(load) if load < 0 else str(load) + "*min(1,max(0,V(mid)/.2))"}
.control
set numdgt=15
tran 10u .45 {"uic" if stress else ""}
wrdata {data} v(supply) v(mid) v(astore) v(raw)
quit
.endc
.end
"""


def metrics(rows, c):
    if len(rows) < 1000 or rows[-1][0] < 0.449:
        raise ValueError("Incomplete passive power-down data")
    return {
        "maximum_mid_above_analog_v": max(r[3] - r[1] for r in rows),
        "minimum_mid_v": min(r[3] for r in rows),
        "maximum_reverse_path_a": max(
            0,
            -min(
                max(
                    0,
                    (r[7] - r[1] - c["diode_forward_assumed_max_v"])
                    / c["input_filter_ohm"],
                )
                - c["diode_reverse_envelope_a"] * min(1, max(0, (r[1] - r[7]) / 0.001))
                for r in rows
            ),
        ),
        "analog_at_end_v": rows[-1][1],
        "mid_at_end_v": rows[-1][3],
        "raw_at_end_v": rows[-1][7],
        "passes_mid_input_abs_limits": all(-0.5 <= r[3] <= r[1] + 0.5 for r in rows),
    }


def run_case(c, raw, fall, load, bypass=False, stress=False, floating=False):
    name = (
        f"loss-v{raw:g}-fall{fall:g}-load{load:g}"
        + ("-unsafe-bypass" if bypass else "")
        + ("-brownout-startup" if stress else "")
        + ("-floating-source" if floating else "")
    )
    data = (BUILD / (name + ".dat")).relative_to(ROOT)
    rows, warnings = execute_deck(
        passive_deck(c, raw, fall, load, data, bypass, stress, floating), BUILD, name
    )
    return {
        "raw_v": raw,
        "fall_s": fall,
        "mid_load_a": load,
        **metrics(rows, c),
    }, warnings


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    report = BUILD / "result.json"
    report.unlink(missing_ok=True)
    audit_model(MODEL.read_bytes())
    v = subprocess.run(
        ["ngspice", "--version"], capture_output=True, text=True, check=True
    )
    ng = require_simulator(v.stdout + v.stderr)
    c = json.loads(CONFIG.read_text())
    validate(c)
    proof = invariant(c)
    if not proof["pass_under_declared_envelope"]:
        raise ValueError("Passive safety invariant failed")
    dc = []
    for raw, st, sb in itertools.product([10.8, 13.2], [-1, 1], [-1, 1]):
        rt = c["divider_ohm"][0] * (1 + st * c["divider_tolerance"])
        rb = c["divider_ohm"][1] * (1 + sb * c["divider_tolerance"])
        va = steady(
            c,
            raw,
            c["total_active_and_bulk_leakage_max_a"],
            c["diode_forward_assumed_max_v"],
            rt,
            rb,
        )
        if va < c["proposed_min_analog_rail_v"]:
            raise ValueError("Protected analog rail budget failed")
        error = (
            abs(va * rb / (rt + rb) - va / 2)
            + rt * rb / (rt + rb) * c["mid_total_load_max_a"]
        )
        if error > c["proposed_dc_mid_error_v"]:
            raise ValueError("Passive divider/load error budget failed")
        dc.append({"raw_v": raw, "analog_worst_v": va, "mid_worst_error_v": error})
    ripples = []
    for bulk, rf, rt, rb in itertools.product(
        [c["bulk_capacitance_min_f"], c["bulk_capacitance_f"] * 1.2],
        [c["input_filter_ohm"] * (1 + c["filter_tolerance"] * s) for s in [-1, 1]],
        [c["divider_ohm"][0] * (1 + c["divider_tolerance"] * s) for s in [-1, 1]],
        [c["divider_ohm"][1] * (1 + c["divider_tolerance"] * s) for s in [-1, 1]],
    ):
        value = (
            abs(
                ripple(
                    c,
                    100,
                    bulk,
                    rf,
                    c["bulk_esr_envelope_max_ohm"],
                    c["mid_capacitance_f"],
                    c["mid_esr_envelope_max_ohm"],
                    rt,
                    rb,
                )
            )
            * 0.1
        )
        if value > c["proposed_ripple_mid_peak_v"]:
            raise ValueError("Aux ripple criterion failed")
        ripples.append(value)
    warnings = set()
    losses = []
    for raw, fall, load in itertools.product(
        [10.8, 13.2], [0.000001, 0.0001, 0.002, 0.02, 0.1], [-0.001, 0, 0.001]
    ):
        result, w = run_case(c, raw, fall, load)
        warnings.update(w)
        if (
            not result["passes_mid_input_abs_limits"]
            or result["maximum_reverse_path_a"] > 0.00005001
        ):
            raise ValueError("Power-down input/backfeed criterion failed")
        losses.append(result)
    stresses = []
    for raw, load, stress, floating in [
        (13.2, x, True, False) for x in [-0.001, 0.001]
    ] + [(12, -0.001, False, True)]:
        r, w = run_case(c, raw, 0.000001, load, stress=stress, floating=floating)
        warnings.update(w)
        if not r["passes_mid_input_abs_limits"]:
            raise ValueError("Startup/brownout/floating-source protection failed")
        if (
            floating
            and r["raw_at_end_v"] > proof["raw_aux_ghost_voltage_bound_v"] + 1e-6
        ):
            raise ValueError("Floating raw AUX ghost-voltage bound failed")
        stresses.append(
            {"startup_brownout": stress, "source_disconnected": floating, **r}
        )
    bad, w = run_case(c, 12, 0.000001, 0, True)
    warnings.update(w)
    if bad["passes_mid_input_abs_limits"]:
        raise ValueError("Expected missing-isolation counterexample absent")
    chains = []
    acfg = json.loads(ANALOG_CONFIG.read_text())
    for raw, temp in itertools.product([10.8, 12, 13.2], [0, 27, 70]):
        va = (
            min(x["analog_worst_v"] for x in dc if x["raw_v"] == raw)
            if raw != 12
            else steady(
                c,
                raw,
                c["total_active_and_bulk_leakage_max_a"],
                c["diode_forward_assumed_max_v"],
            )
        )
        name = f"chain-raw{raw:g}-t{temp:g}"
        data = (BUILD / (name + ".dat")).relative_to(ROOT)
        deck = official_deck(acfg, data, va, temp, True)
        needle = f"VMID mid 0 {va / 2}\n"
        if deck.count(needle) != 1:
            raise ValueError("Unexpected original VMID")
        deck = deck.replace(needle, network(c)).replace(
            f"wrdata {data} v(buffered) v(positive) v(negative)",
            f"wrdata {data} v(mid) v(positive) v(negative) i(VSUP)",
        )
        rows, w = execute_deck(deck, BUILD, name)
        warnings.update(w)
        rms, offset, window = differential_metrics(rows)
        # VSUP also feeds the passive divider; proof's 50 mA budget excludes it.
        max_i = max(-r[7] - (va - r[1]) / c["divider_ohm"][0] for r in window)
        cm_low = min(r[1] - math.sqrt(2) * acfg["input_rms_v"] / 2 for r in window)
        cm_high = max(r[1] + math.sqrt(2) * acfg["input_rms_v"] / 2 for r in window)
        if (
            not 1.97 < rms < 2.02
            or abs(offset) > 0.01
            or max_i > c["total_active_and_bulk_leakage_max_a"]
            or cm_low < 0
            or cm_high > va - 2.25
        ):
            raise ValueError("Protected-rail LR4/headroom/current study failed")
        chains.append(
            {
                "raw_v": raw,
                "analog_model_supply_v": va,
                "temperature_c": temp,
                "differential_rms_v": rms,
                "differential_dc_v": offset,
                "modeled_active_supply_current_peak_a": max_i,
                "buffer_common_mode_margin_v": va - 2.25 - cm_high,
            }
        )
    hashes = {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in [
            "scripts/simulate_vmid_protection.py",
            "simulation/analog/vmid-protection.json",
            "scripts/simulate_opa1656.py",
            "scripts/simulate_vmid.py",
            "simulation/analog/lr4-study.json",
            "simulation/analog/vmid-protected.cir",
        ]
    }
    output = {
        "status": "PASS UNDER DECLARED ENVELOPE; HARDWARE GATES PENDING",
        "ngspice_version": ng,
        "manufacturer_model_sha256": MODEL_SHA,
        "source_hashes": hashes,
        "invariant": proof,
        "dc_corners": dc,
        "max_ripple_100mv_100hz_mid_peak_v": max(ripples),
        "power_loss_cases": losses,
        "startup_brownout_disconnected_source_cases": stresses,
        "missing_isolation_counterexample": bad,
        "coupled_lr4_cases": chains,
        "convergence_warnings": sorted(warnings),
        "macro_used_below_recommended_supply": False,
        "power_loss_vmids_protected_under_declared_envelope": True,
        "all_frontend_external_inputs_poweroff_protected": False,
        "mpn_temperature_esr_and_pulse_qualified": False,
        "hardware_validated": False,
        "manufacturing_approved": False,
    }
    report.write_text(json.dumps(output, indent=2) + "\n")
    print(
        f"Protected VMID: {len(losses)} power-loss cases,9 coupled LR4 cases; invariant inward={proof['upper_boundary_inward_margin_v_per_s']:.1f} V/s; hardware pending"
    )


if __name__ == "__main__":
    main()
