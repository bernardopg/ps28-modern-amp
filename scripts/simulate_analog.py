#!/usr/bin/env python3
"""Verify physical R/C LR4 values; behavioural opamps are NOT a NE5532 macromodel."""
from pathlib import Path
import hashlib
import itertools
import json
import math
import random
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'simulation/analog/lr4-study.json'


def section_response(frequency, values):
    r1, r2, cf1, cf2, cg = values
    cf = cf1 + cf2
    s = complex(0, 2 * math.pi * frequency)
    return 1 / (1 + s * cg * (r1 + r2) + s * s * r1 * r2 * cf * cg)


def metrics(values):
    r1, r2, cf1, cf2, cg = values
    root = math.sqrt(r1 * r2 * (cf1 + cf2) * cg)
    return {'natural_frequency_hz': 1 / (2 * math.pi * root),
            'q': root / (cg * (r1 + r2))}


def db(value):
    return 20 * math.log10(abs(value))


def tolerance_study(config):
    nominal = config['stage_ohm'] + config['stage_feedback_capacitors_f'] + [config['stage_ground_capacitor_f']]
    tol = [config['resistor_tolerance_fraction']] * 2 + [config['capacitor_tolerance_fraction']] * 3
    gains, frequencies, qs = [], [], []
    # Ten filter components plus divider/inverter resistors; not proof of continuous extrema.
    for signs in itertools.product([-1, 1], repeat=14):
        sections = [[v * (1 + t * sign) for v, t, sign in zip(nominal, tol, signs[j:j+5])]
                    for j in [0, 5]]
        rt = config['resistor_tolerance_fraction']
        top, bottom = [v * (1 + rt * sign) for v, sign in zip(config['attenuator_ohm'], signs[10:12])]
        inverter_gain = (1 + rt * signs[13]) / (1 + rt * signs[12])
        gains.append(db(bottom / (top + bottom) * (1 + inverter_gain)
                        * section_response(80, sections[0]) * section_response(80, sections[1])))
        for section in sections:
            m = metrics(section); frequencies.append(m['natural_frequency_hz']); qs.append(m['q'])
    rng = random.Random(config['monte_carlo_seed'])
    mc = []
    for _ in range(config['monte_carlo_samples']):
        sections = [[v * (1 + rng.uniform(-t, t)) for v, t in zip(nominal, tol)] for _ in range(2)]
        rt = config['resistor_tolerance_fraction']
        top, bottom = [v * (1 + rng.uniform(-rt, rt)) for v in config['attenuator_ohm']]
        inverter_gain = (1 + rng.uniform(-rt, rt)) / (1 + rng.uniform(-rt, rt))
        mc.append(db(bottom / (top + bottom) * (1 + inverter_gain)
                     * section_response(80, sections[0]) * section_response(80, sections[1])))
    return {'distribution': 'independent uniform, not a measured production distribution',
            'seed': config['monte_carlo_seed'], 'monte_carlo_samples': len(mc),
            'corner_combinations': len(gains), 'corner_gain_db_80hz_range': [min(gains), max(gains)],
            'section_fn_hz_corner_range': [min(frequencies), max(frequencies)],
            'section_q_corner_range': [min(qs), max(qs)],
            'monte_carlo_gain_db_80hz_range': [min(mc), max(mc)],
            'corner_window_is_proposed_not_customer_approval': True}


def deck(config, filename, mode='ideal', transient=False, bypass_attenuation=False):
    supply = config['aux_supply_min_v']
    vmid = supply / 2
    rtop, rbottom = config['attenuator_ohm']
    if bypass_attenuation:
        rtop = .001  # Diagnostic counterexample, NOT the proposed circuit.
    r1, r2 = config['stage_ohm']
    cf1, cf2 = config['stage_feedback_capacitors_f']; cg = config['stage_ground_capacitor_f']
    if mode == 'ideal':
        model = '.subckt AMP p n out mid supply\nEAMP out 0 p n 1e9\n.ends AMP'
    else:
        aol = config['assumed_opamp_aol']; gbw = config['assumed_opamp_gbw_hz']
        cpole = aol / (2 * math.pi * gbw * 1000)
        margin = config['assumed_rail_margin_v_NOT_guaranteed_at_12V']
        rout = config['assumed_opamp_output_resistance_ohm']
        model = (f'.subckt AMP p n out mid supply\nEAMP raw 0 p n {aol}\n'
                 f'RPOLE raw pole 1000\nCPOLE pole 0 {cpole:.12g}\n'
                 f'BCLAMP drive 0 V=V(mid)+max(-max(0,V(supply)/2-{margin}),min(max(0,V(supply)/2-{margin}),V(pole)))\n'
                 f'ROUT drive out {rout}\n.ends AMP')
    circuit = f'''* PS28 LR4 physical R/C study. NO qualified NE5532/VMID/startup model.
* CFB is TI SLOA024B C2; CG is TI C1, fig.5/eq.9 p.4.
VSUP supply 0 {supply}
VMID mid 0 {vmid}
VIN input mid DC 0 AC 1 SIN(0 {config['input_rms_v'] * math.sqrt(2):.12g} 20)
RATT input divided {rtop}
RBIAS divided mid {rbottom}
XBUF divided buffered buffered mid supply AMP
R11 buffered x1 {r1}
R12 x1 y1 {r2}
CF11 x1 filtered1 {cf1}
CF12 x1 filtered1 {cf2}
CG1 y1 mid {cg}
XLP1 y1 filtered1 filtered1 mid supply AMP
R21 filtered1 x2 {r1}
R22 x2 y2 {r2}
CF21 x2 positive {cf1}
CF22 x2 positive {cf2}
CG2 y2 mid {cg}
XLP2 y2 positive positive mid supply AMP
RINV positive minus 10000
RF negative minus 10000
XINV mid minus negative mid supply AMP
RLOADP positive mid {config['assumed_next_stage_load_ohm']}
RLOADN negative mid {config['assumed_next_stage_load_ohm']}
{model}
'''
    if transient:
        control = f'.control\ntran 10u 350m\nwrdata {filename} v(buffered) v(positive) v(negative)\nquit\n.endc\n.end\n'
    else:
        control = f'.control\nac dec 50 10 10k\nlet gain=mag(v(positive,negative))\nlet phase=57.2957795131*ph(v(positive,negative))\nwrdata {filename} gain phase\nquit\n.endc\n.end\n'
    return circuit + control


def run_spice(config, build, name, **options):
    data = build / (name + '.dat'); data.unlink(missing_ok=True)
    circuit = build / (name + '.cir')
    circuit.write_text(deck(config, data.relative_to(ROOT), **options))
    result = subprocess.run(['ngspice', '-b', str(circuit.relative_to(ROOT))], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    (build / (name + '.log')).write_text(result.stdout + result.stderr)
    if result.returncode or not data.exists():
        raise RuntimeError(f'Analog SPICE failed: {name}')
    rows = [list(map(float, line.split())) for line in data.read_text().splitlines() if line.strip()]
    if not rows or any(not math.isfinite(v) for row in rows for v in row):
        raise ValueError(f'Invalid analog output: {name}')
    return rows


def main():
    config = json.loads(CONFIG.read_text()); build = ROOT / 'build/analog'; build.mkdir(parents=True, exist_ok=True)
    report_path = build / 'lr4-study-result.json'; report_path.unlink(missing_ok=True)
    nominal = config['stage_ohm'] + config['stage_feedback_capacitors_f'] + [config['stage_ground_capacitor_f']]
    canonical = ROOT / 'simulation/analog/lr4-rc.cir'
    if canonical.read_text() != deck(config, 'build/analog/rc-ideal.dat'):
        raise ValueError('Canonical RC netlist is stale relative to configuration')
    rows = run_spice(config, build, 'rc-ideal')
    if len(rows) != 151 or not math.isclose(rows[0][0], 10) or not math.isclose(rows[-1][0], 10000):
        raise ValueError('Incomplete physical-RC AC sweep')
    ratio = config['attenuator_ohm'][1] / sum(config['attenuator_ohm'])
    for row in rows:
        frequency, magnitude, phase = row[0], row[1], row[3]
        expected_complex = 2 * ratio * section_response(frequency, nominal) ** 2
        expected = abs(expected_complex)
        actual_complex = magnitude * complex(math.cos(math.radians(phase)), math.sin(math.radians(phase)))
        if abs(actual_complex - expected_complex) > expected * 1e-5:
            raise ValueError(f'Physical RC disagreement at {frequency} Hz')
    finite = run_spice(config, build, 'rc-finite', mode='bounded')
    if len(finite) != len(rows) or any(not math.isclose(a[0], b[0]) for a, b in zip(finite, rows)):
        raise ValueError('Finite-model sweep frequency mismatch')
    discrepancy = max(abs(db(a[1] / b[1])) for a, b in zip(finite, rows))
    if discrepancy > .1:
        raise ValueError('Unexpected small-signal effect of the assumed opamp model')
    transients = {}
    vmid = config['aux_supply_min_v'] / 2
    allowed = vmid - config['assumed_rail_margin_v_NOT_guaranteed_at_12V']
    for bypass in [False, True]:
        name = 'transient-no-attenuation' if bypass else 'transient-attenuated'
        wave = run_spice(config, build, name, mode='bounded', transient=True, bypass_attenuation=bypass)
        steady = [r for r in wave if r[0] >= .25]
        if len(steady) < 500:
            raise ValueError('Incomplete analog transient')
        peak = max(abs(r[1] - vmid) for r in steady)
        # wrdata uses one time/value pair for each vector: t,buf,t,pos,t,neg.
        clipped = sum(abs(r[1] - vmid) >= allowed * .999 for r in steady) / len(steady)
        transients[name] = {'input_rms_v': config['input_rms_v'], 'test_frequency_hz': 20,
                            'buffer_peak_v_relative_to_vmid': peak,
                            'buffer_clip_sample_fraction': clipped,
                            'steady_samples': len(steady),
                            'bounded_model_not_actual_NE5532_clipping': True}
        if (not bypass and clipped > 0) or (bypass and clipped < .01):
            raise ValueError('Headroom counterexample did not match the assumed bounded model')
    corners = tolerance_study(config)
    lo, hi = config['study_window_gain_db_at_80hz']
    if not lo <= corners['corner_gain_db_80hz_range'][0] <= corners['corner_gain_db_80hz_range'][1] <= hi:
        raise ValueError('RC tolerance exceeds proposed study window')
    report = {'status': 'PASS FOR STUDY ONLY', 'config_sha256': hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
              'ngspice_version': subprocess.check_output(['ngspice', '--version'], text=True).strip(),
              'nominal_section': metrics(nominal), 'nominal_filter_gain_db_at_80hz': db(section_response(80, nominal)**2),
              'canonical_netlist_sha256': hashlib.sha256(canonical.read_bytes()).hexdigest(),
              'magnitude_and_phase_checked': True,
              'physical_rc_spice_points_checked': len(rows), 'max_assumed_opamp_effect_db_10hz_to_10khz': discrepancy,
              'tolerances': corners, 'transients': transients,
              'models': 'ideal VCVS / custom single-pole bounded behavioural; NOT manufacturer NE5532 model',
              'VMID_startup_noise_slew_offset_bias_thermal_qualified': False,
              'exact_mpn_and_footprint_selected': False, 'hardware_validated': False}
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
