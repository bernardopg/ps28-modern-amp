#!/usr/bin/env python3
"""Container parsing smoke test. Does NOT run or approve design-rule checks."""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    build = ROOT / 'build'
    build.mkdir(exist_ok=True)
    commands = {
        'schematic': ['kicad-cli', 'sch', 'export', 'netlist', '--output',
                      'build/container.net', 'kicad/ps28-modern.kicad_sch'],
        'pcb': ['kicad-cli', 'pcb', 'export', 'svg', '--layers', 'F.Cu',
                '--mode-single', '--output', 'build/container.svg',
                'kicad/ps28-modern.kicad_pcb'],
    }
    reports = {}
    for name, command in commands.items():
        expected = build / ('container.net' if name == 'schematic' else 'container.svg')
        expected.unlink(missing_ok=True)
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        (build / f'{name}-smoke.log').write_text(output)
        reports[name] = {'exit_code': result.returncode,
                         'assertion_warning': 'No enum choices defined' in output}
        if result.returncode or not expected.exists() or expected.stat().st_size == 0:
            raise RuntimeError(f'{name} parse/export failed; see build/{name}-smoke.log')
    reports['hardware_validated'] = False
    (build / 'eda-smoke.json').write_text(json.dumps(reports, indent=2) + '\n')
    print(json.dumps(reports, indent=2))
    print('Parsing only. Known installed-build warnings are recorded, not suppressed.')


if __name__ == '__main__':
    main()
