#!/usr/bin/env python3
"""Native KiCad 3D previews, clearly labelled, never manufacturing outputs."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path

from check_core import text
from create_core_draft import parse

ROOT = Path(__file__).resolve().parents[1]
VIEWS = {
    "isometric": ("top", "325,0,25", True),
    "top": ("top", "0,0,0", False),
    "bottom": ("bottom", "0,0,0", False),
}
DESIGNS = {
    "selected": ROOT / "kicad/core-selected/ps28-modern.kicad_pcb",
    "oem": ROOT / "kicad/core-oem-refined/ps28-modern.kicad_pcb",
    "system": ROOT / "kicad/system-candidate/system-candidate.kicad_pcb",
}
# Camera framing so the off-outline import banks of the system candidate are visible.
CAMERA = {
    "system": {
        "isometric": ["--zoom", "0.34", "--pan", "-14,-3,0"],
        "top": ["--zoom", "0.40", "--pan", "-13,7,0"],
        "bottom": ["--zoom", "0.40", "--pan", "13,7,0"],
        "orbit": ["--zoom", "0.26"],
    }
}
FOOTERS = {
    "selected": "NUCLEO APENAS | D-018/D-019 SEM PCB INTEGRADA",
    "oem": "NUCLEO APENAS | D-018/D-019 SEM PCB INTEGRADA",
    "system": "NUCLEO NO CONTORNO + BANCOS D-018/D-021/D-020 FORA DO CONTORNO, SEM FIT | D-019 ABERTA",
}


def audit_models(board):
    records = []
    for fp in parse(board.read_text()):
        if not isinstance(fp, list) or fp[0] != "footprint":
            continue
        ref = next(
            text(p[2])
            for p in fp
            if isinstance(p, list) and p[:2] == ["property", '"Reference"']
        )
        models = [text(n[1]) for n in fp if isinstance(n, list) and n[0] == "model"]
        missing = []
        for model in models:
            resolved = model.replace("${KIPRJMOD}", str(board.parent))
            for version in [10, 9, 8]:
                key = f"KICAD{version}_3DMODEL_DIR"
                resolved = resolved.replace(
                    "${" + key + "}", os.environ.get(key, "/usr/share/kicad/3dmodels")
                )
            if not Path(resolved).is_file():
                missing.append(model)
        records.append(
            {
                "reference": ref,
                "footprint": text(fp[1]),
                "models": models,
                "missing_models": missing,
                "has_available_model": bool(models) and not missing,
            }
        )
    return records


def electrical_context():
    """Capture exists without PCB integration; never invent geometry for it."""
    capture = ROOT / "kicad/analog-protected/analog-protected.kicad_sch"
    inventory = ROOT / "kicad/analog-protected/vmid-manifest.json"
    parts = json.loads(inventory.read_text())["parts"]
    if capture.with_suffix(".kicad_pcb").exists():
        raise ValueError(
            "Analog PCB now exists: review the gallery scope before rendering"
        )
    sources = [
        capture,
        inventory,
        ROOT / "simulation/analog/vmid-protection.json",
        ROOT / "simulation/analog/input-power-order.json",
    ]
    return {
        "scope": "POWER_CORE_PLUS_SYSTEM_CANDIDATE_IMPORT_BANKS",
        "analog_protection_integrated_in_rendered_pcbs": False,
        "system_candidate_rendered": True,
        "system_candidate_banks_inside_oem_outline": False,
        "protected_analog_capture_components": len(parts),
        "protected_analog_unassigned_footprints": sorted(
            p["ref"] for p in parts if not p.get("footprint")
        ),
        "notes": [
            "D-018 captured separately; no analog PCB",
            "system-candidate: D-018/D-021/D-020 footprints in unplaced banks outside OEM outline",
            "D-019 isolation/precharge contract not implemented",
            "No added mounts, routing or fabricated 3D substitutes",
        ],
        "source_sha256": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sources
        },
    }


@contextmanager
def staged_assets(output):
    """Render/verify the whole set before touching published assets; manifest last."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".ps28-gallery-", dir=output.parent
    ) as temporary:
        staging = Path(temporary)
        yield staging
        manifest = json.loads((staging / "manifest.json").read_text())
        expected = {
            f"{key}-{view}.{extension}"
            for key in DESIGNS
            for view, extension in [
                ("isometric", "png"),
                ("top", "png"),
                ("bottom", "png"),
                ("orbit", "gif"),
            ]
        }
        if set(manifest["asset_sha256"]) != expected:
            raise ValueError("Incomplete generated gallery")
        for name, digest in manifest["asset_sha256"].items():
            if Path(name).name != name or not name.endswith((".png", ".gif")):
                raise ValueError("Invalid generated asset name")
            if hashlib.sha256((staging / name).read_bytes()).hexdigest() != digest:
                raise ValueError("Generated asset hash mismatch")
        output.mkdir(parents=True, exist_ok=True)
        for name in manifest["asset_sha256"]:
            (staging / name).replace(output / name)
        (staging / "manifest.json").replace(output / "manifest.json")
        # Existing README/custom files are never generated or overwritten here.


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--frames", type=int, default=16)
    ap.add_argument("--output", type=Path, default=ROOT / "docs/images/kicad-3d")
    args = ap.parse_args()
    if not 8 <= args.frames <= 72:
        ap.error("--frames must be between 8 and 72")
    if shutil.which("kicad-cli") is None:
        ap.error("kicad-cli is required; no substitutes for native rendering")
    with staged_assets(args.output.resolve()) as output:
        render(args.frames, output)


def render(frame_count, output):
    from PIL import Image, ImageDraw, ImageFont

    build = ROOT / "build/renders/native"
    build.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 18)
    small = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 13)
    manifest = {
        "renderer": subprocess.check_output(
            ["kicad-cli", "--version"], text=True
        ).strip(),
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "method": "kicad-cli pcb render; Pillow adds status bands and encodes GIFs only",
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "electrical_context": electrical_context(),
        "hardware_validated": False,
        "manufacturing_approved": False,
        "designs": {},
    }

    def native(board, path, side, rotation, perspective, width, height, camera=()):
        command = [
            "kicad-cli",
            "pcb",
            "render",
            "--width",
            str(width),
            "--height",
            str(height),
            "--quality",
            "high",
            "--background",
            "opaque",
            "--side",
            side,
            "--rotate",
            rotation,
            "--output",
            str(path),
        ]
        if perspective:
            command.append("--perspective")
        command.extend(camera)
        command.append(str(board))
        path.unlink(missing_ok=True)
        result = subprocess.run(
            command, cwd=ROOT, capture_output=True, text=True, timeout=180, check=False
        )
        path.with_suffix(".log").write_text(result.stdout + result.stderr)
        if result.returncode or not path.is_file():
            raise RuntimeError(f"Native render failed: {path}; see its .log")
        # Record portable replay commands relative to the repository root.
        return [arg.replace(str(ROOT) + "/", "") for arg in command]

    def labelled(path, title, unavailable, target, footer):
        with Image.open(path) as raw:
            image = raw.convert("RGB")
        canvas = Image.new("RGB", (image.width, image.height + 98), "#101821")
        canvas.paste(image, (0, 48))
        draw = ImageDraw.Draw(canvas)
        draw.text((18, 8), title, font=font, fill="#eef4f8")
        draw.text(
            (18, 30),
            "ESTUDO / NAO ROTEADA / SEM APROVACAO PARA FABRICACAO",
            font=small,
            fill="#ffcf78",
        )
        draw.text(
            (18, image.height + 54),
            "3D ausente: " + (", ".join(unavailable) if len(unavailable) <= 12
                              else ", ".join(unavailable[:12]) + f" +{len(unavailable) - 12}"),
            font=small,
            fill="#ffcf78",
        )
        draw.text(
            (18, image.height + 74),
            footer,
            font=small,
            fill="#ffcf78",
        )
        if target:
            canvas.save(target)
        return canvas

    for name, board in DESIGNS.items():
        records = audit_models(board)
        unavailable = sorted(
            r["reference"] for r in records if not r["has_available_model"]
        )
        entry = {
            "pcb": str(board.relative_to(ROOT)),
            "pcb_sha256": hashlib.sha256(board.read_bytes()).hexdigest(),
            "footprints": len(records),
            "without_available_model": unavailable,
            "model_audit": records,
            "native_commands": [],
            "images": [],
            "gif": f"{name}-orbit.gif",
            "frames": frame_count,
            "frame_duration_ms": 140,
            "models_are_visual_not_manufacturer_qualification": True,
        }
        for view, (side, rotation, perspective) in VIEWS.items():
            path = build / f"{name}-{view}.png"
            entry["native_commands"].append(
                native(board, path, side, rotation, perspective, 1280, 800,
                       CAMERA.get(name, {}).get(view, ()))
            )
            target = output / path.name
            labelled(
                path, f"PS28 | {name.upper()} | KiCad 3D | {view}", unavailable, target,
                FOOTERS[name],
            )
            entry["images"].append(target.name)
        frames = []
        for i in range(frame_count):
            path = build / f"{name}-frame-{i:03d}.png"
            angle = 360 * i / frame_count
            entry["native_commands"].append(
                native(board, path, "top", f"325,0,{angle:g}", True, 800, 500,
                       CAMERA.get(name, {}).get("orbit", ()))
            )
            frames.append(
                labelled(path, f"PS28 | {name.upper()} | KiCad 3D", unavailable, None, FOOTERS[name])
            )
        # Every frame above is an independent KiCad camera render, not a 2D image rotation.
        frames[0].save(
            output / entry["gif"],
            save_all=True,
            append_images=frames[1:],
            duration=140,
            loop=0,
            optimize=True,
            disposal=2,
        )
        entry["gif_size_pixels"] = list(frames[0].size)
        with Image.open(output / entry["images"][0]) as preview:
            entry["png_size_pixels"] = list(preview.size)
        manifest["designs"][name] = entry
        print(
            f"{name}: 3 PNG + {frame_count} native frames; missing models: {unavailable}",
            flush=True,
        )
    assets = sorted(p for p in output.iterdir() if p.suffix in [".png", ".gif"])
    manifest["asset_sha256"] = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in assets
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
