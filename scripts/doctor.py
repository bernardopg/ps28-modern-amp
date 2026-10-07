#!/usr/bin/env python3
"""Read-only inventory; no secrets, installs or hardware assumptions."""
from pathlib import Path
import importlib.util
import json
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ['kicad-cli', 'ngspice', 'python3', 'git', 'make']
OPTIONAL = ['gh', 'uv', 'pdftotext', 'curl', 'freecad', 'FreeCAD', 'openscad', 'pulseview']


def main():
    tools = {name: shutil.which(name) for name in REQUIRED + OPTIONAL}
    versions = {}
    for name, args in [('kicad-cli', ['version']), ('ngspice', ['--version']), ('git', ['--version'])]:
        if tools[name]:
            try:
                result = subprocess.run([name, *args], capture_output=True, text=True, timeout=15)
                versions[name] = (result.stdout + result.stderr).strip()
            except subprocess.TimeoutExpired:
                versions[name] = 'TIMEOUT'
    plugin = Path.home() / '.local/share/kicad/10.0/scripting/plugins/kicad_ai_assistant/VERSION'
    report = {
        'platform': platform.platform(), 'python': platform.python_version(),
        'tools': tools, 'versions': versions,
        'python_modules': {name: importlib.util.find_spec(name) is not None
                           for name in ['numpy', 'scipy', 'matplotlib', 'kipy', 'pypdf']},
        'system_kicad_libraries': {name: (Path('/usr/share/kicad') / name).is_dir()
                                 for name in ['symbols', 'footprints', '3dmodels']},
        'ai_assistant_version': plugin.read_text().strip() if plugin.exists() else None,
        'ipc': 'Not pinged here; use kcaa_check_kicad_ipc_connection with editor running',
        'physical_bench': 'UNKNOWN - manual inventory required',
        'missing_required': [name for name in REQUIRED if not tools[name]],
    }
    (ROOT / 'build').mkdir(exist_ok=True)
    (ROOT / 'build/doctor.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return bool(report['missing_required'])


if __name__ == '__main__':
    sys.exit(main())
