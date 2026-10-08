#!/usr/bin/env python3
"""Native KiCad 3D previews, clearly labelled, never manufacturing outputs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from check_core import text
from create_core_draft import parse

ROOT = Path(__file__).resolve().parents[1]
VIEWS = {'isometric': ('top', '325,0,25', True),
         'top': ('top', '0,0,0', False), 'bottom': ('bottom', '0,0,0', False)}
DESIGNS = {'selected': ROOT / 'kicad/core-selected/ps28-modern.kicad_pcb',
           'oem': ROOT / 'kicad/core-oem-refined/ps28-modern.kicad_pcb'}


def audit_models(board):
    records = []
    for fp in parse(board.read_text()):
        if not isinstance(fp, list) or fp[0] != 'footprint':
            continue
        ref = next(text(p[2]) for p in fp if isinstance(p, list) and p[:2] == ['property', '"Reference"'])
        models = [text(n[1]) for n in fp if isinstance(n, list) and n[0] == 'model']
        missing = []
        for model in models:
            resolved = model.replace('${KIPRJMOD}', str(board.parent))
            for version in [10, 9, 8]:
                key = f'KICAD{version}_3DMODEL_DIR'
                resolved = resolved.replace('${' + key + '}', os.environ.get(key, '/usr/share/kicad/3dmodels'))
            if not Path(resolved).is_file():
                missing.append(model)
        records.append({'reference': ref, 'footprint': text(fp[1]), 'models': models,
                        'missing_models': missing, 'has_available_model': bool(models) and not missing})
    return records


def main():
    from PIL import Image, ImageDraw, ImageFont
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--frames', type=int, default=16)
    ap.add_argument('--output', type=Path, default=ROOT / 'docs/images/kicad-3d')
    args = ap.parse_args()
    if not 8 <= args.frames <= 72:
        ap.error('--frames must be between 8 and 72')
    if shutil.which('kicad-cli') is None:
        ap.error('kicad-cli is required; no substitutes for native rendering')
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
    build = ROOT / 'build/renders/native'; build.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf', 18)
    small = ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf', 13)
    manifest = {'renderer': subprocess.check_output(['kicad-cli', '--version'], text=True).strip(),
                'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'method': 'kicad-cli pcb render; Pillow adds status bands and encodes GIFs only',
                'hardware_validated': False, 'manufacturing_approved': False, 'designs': {}}

    def native(board, path, side, rotation, perspective, width, height):
        command = ['kicad-cli', 'pcb', 'render', '--width', str(width), '--height', str(height),
                   '--quality', 'high', '--background', 'opaque', '--side', side,
                   '--rotate', rotation, '--output', str(path)]
        if perspective:
            command.append('--perspective')
        command.append(str(board))
        path.unlink(missing_ok=True)
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=180)
        path.with_suffix('.log').write_text(result.stdout + result.stderr)
        if result.returncode or not path.is_file():
            raise RuntimeError(f'Native render failed: {path}; see its .log')
        # Record portable replay commands relative to the repository root.
        return [arg.replace(str(ROOT) + '/', '') for arg in command]

    def labelled(path, title, unavailable, target):
        with Image.open(path) as raw:
            image = raw.convert('RGB')
        canvas = Image.new('RGB', (image.width, image.height + 78), '#101821')
        canvas.paste(image, (0, 48))
        draw = ImageDraw.Draw(canvas)
        draw.text((18, 8), title, font=font, fill='#eef4f8')
        draw.text((18, 30), 'ESTUDO / NAO ROTEADA / SEM APROVACAO PARA FABRICACAO', font=small, fill='#ffcf78')
        draw.text((18, image.height + 54), '3D ausente: ' + ', '.join(unavailable), font=small, fill='#ffcf78')
        if target:
            canvas.save(target)
        return canvas

    for name, board in DESIGNS.items():
        records = audit_models(board)
        unavailable = sorted(r['reference'] for r in records if not r['has_available_model'])
        entry = {'pcb': str(board.relative_to(ROOT)), 'pcb_sha256': hashlib.sha256(board.read_bytes()).hexdigest(),
                 'footprints': len(records), 'without_available_model': unavailable, 'model_audit': records,
                 'native_commands': [], 'images': [], 'gif': f'{name}-orbit.gif', 'frames': args.frames,
                 'frame_duration_ms': 140, 'models_are_visual_not_manufacturer_qualification': True}
        for view, (side, rotation, perspective) in VIEWS.items():
            path = build / f'{name}-{view}.png'
            entry['native_commands'].append(native(board, path, side, rotation, perspective, 1280, 800))
            target = output / path.name
            labelled(path, f'PS28 | {name.upper()} | KiCad 3D | {view}', unavailable, target)
            entry['images'].append(target.name)
        frames = []
        for i in range(args.frames):
            path = build / f'{name}-frame-{i:03d}.png'
            angle = 360 * i / args.frames
            entry['native_commands'].append(native(board, path, 'top', f'325,0,{angle:g}', True, 800, 500))
            frames.append(labelled(path, f'PS28 | {name.upper()} | KiCad 3D', unavailable, None))
        # Every frame above is an independent KiCad camera render, not a 2D image rotation.
        frames[0].save(output / entry['gif'], save_all=True, append_images=frames[1:],
                       duration=140, loop=0, optimize=True, disposal=2)
        entry['gif_size_pixels'] = list(frames[0].size)
        with Image.open(output / entry['images'][0]) as preview:
            entry['png_size_pixels'] = list(preview.size)
        manifest['designs'][name] = entry
        print(f'{name}: 3 PNG + {args.frames} native frames; missing models: {unavailable}', flush=True)
    assets = sorted(p for p in output.iterdir() if p.suffix in ['.png', '.gif'])
    manifest['asset_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in assets}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
