#!/usr/bin/env python3
"""Native KiCad 3D views of the product board; previews, never manufacturing outputs.

kicad-cli renders the board on a transparent background; Pillow only composites it
on the graphite studio backdrop used by the Blender renders and encodes the GIF.
The thermal block WRL is written with inverted face winding (renders black in
KiCad), so rendering uses a temporary board copy whose block model adds `ccw FALSE`.
shortcut: the source WRL keeps its hash for the thermal reports; fix the exporter
in scripts/blender_thermal_block.py when those reports are regenerated.
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "kicad/system-candidate/system-candidate.kicad_pcb"
VIEWS = {  # name: (side, rotation, perspective)
    "isometric": ("top", "-38,0,32", True),
    "top": ("top", "0,0,0", False),
    "bottom": ("bottom", "0,0,0", False),
}
STILL, ORBIT = (2400, 1500), (1200, 750)


def missing_models(board):
    """References whose footprint has no resolvable 3D model."""
    text = board.read_text()
    missing = []
    for block in re.split(r"\n\t\(footprint ", text)[1:]:
        ref = re.search(r'\(property "Reference" "([^"]+)"', block).group(1)
        models = re.findall(r'\(model "([^"]+)"', block)
        resolved = [m.replace("${KIPRJMOD}", str(board.parent))
                    .replace("${KICAD10_3DMODEL_DIR}", "/usr/share/kicad/3dmodels") for m in models]
        if not resolved or not all(Path(m).is_file() for m in resolved):
            missing.append(ref)
    return sorted(missing)


def staged_board(tmp):
    """Copy the board and models; fix the block winding only in the copy."""
    shutil.copytree(BOARD.parent, tmp / "board", ignore=shutil.ignore_patterns("*-backups", "*.lck"))
    shutil.copytree(ROOT / "kicad/models", tmp / "models")
    wrl = tmp / "models/ps28-bodies/thermal_block.wrl"
    wrl.write_text(wrl.read_text().replace(
        "material Material { diffuseColor .68 .71 .74 }",
        "material Material { diffuseColor .74 .76 .78 specularColor .45 .45 .45 shininess .3 }").replace(
        "geometry IndexedFaceSet {", "geometry IndexedFaceSet { ccw FALSE creaseAngle .5", 1))
    return tmp / "board" / BOARD.name


def native(board, path, side, rotation, perspective, size, quality):
    command = ["kicad-cli", "pcb", "render", "--width", str(size[0]), "--height", str(size[1]),
               "--side", side, "--background", "transparent", "--quality", quality,
               "--rotate", rotation, "--zoom", "0.92", "-o", str(path), str(board)]
    if perspective:
        command.insert(3, "--perspective")
    subprocess.run(command, check=True, capture_output=True, text=True)
    return command[:-2] + ["<output>", "<board>"]


def backdrop(cutout):
    """Graphite vertical gradient plus soft contact shadow from the alpha channel."""
    from PIL import Image, ImageFilter
    w, h = cutout.size
    top, bottom = (34, 37, 42), (10, 11, 13)
    grad = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / (h - 1)
        grad.putpixel((0, y), tuple(round(a + (b - a) * t) for a, b in zip(top, bottom)))
    canvas = grad.resize((w, h)).convert("RGBA")
    alpha = cutout.getchannel("A")
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shadow.putalpha(alpha.point(lambda a: a * .55))
    shadow = shadow.transform((w, h), Image.AFFINE, (1, 0, -w * .006, 0, 1, -h * .02))
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(w / 90)))
    canvas.alpha_composite(cutout)
    return canvas.convert("RGB")


def render(frames, output):
    from PIL import Image
    build = ROOT / "build/renders/native"
    build.mkdir(parents=True, exist_ok=True)
    commands = []
    with tempfile.TemporaryDirectory(prefix="ps28-kicad-") as tmp:
        board = staged_board(Path(tmp))
        for name, (side, rotation, perspective) in VIEWS.items():
            raw = build / f"{name}.png"
            commands.append(native(board, raw, side, rotation, perspective, STILL, "high"))
            backdrop(Image.open(raw).convert("RGBA")).save(output / f"system-{name}.png", optimize=True)
        orbit = []
        for i in range(frames):
            raw = build / f"orbit-{i:02d}.png"
            commands.append(native(board, raw, "top", f"-38,0,{i * 360 / frames:g}", True, ORBIT, "basic"))
            orbit.append(backdrop(Image.open(raw).convert("RGBA")).quantize(colors=255))
        orbit[0].save(output / "system-orbit.gif", save_all=True, append_images=orbit[1:],
                      duration=180, loop=0, optimize=True)
    assets = [f"system-{v}.png" for v in VIEWS] + ["system-orbit.gif"]
    manifest = {
        "renderer": subprocess.check_output(["kicad-cli", "--version"], text=True).strip(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "method": "kicad-cli pcb render; Pillow composites the backdrop and encodes the GIF only",
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "pcb": str(BOARD.relative_to(ROOT)),
        "pcb_sha256": hashlib.sha256(BOARD.read_bytes()).hexdigest(),
        "frames": frames,
        "without_available_model": missing_models(BOARD),
        "native_commands": commands,
        "hardware_validated": False,
        "manufacturing_approved": False,
        "asset_sha256": {a: hashlib.sha256((output / a).read_bytes()).hexdigest() for a in assets},
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--frames", type=int, default=16)
    ap.add_argument("--output", type=Path, default=ROOT / "docs/images/kicad-3d")
    args = ap.parse_args()
    if not 8 <= args.frames <= 72:
        ap.error("--frames must be between 8 and 72")
    if shutil.which("kicad-cli") is None:
        ap.error("kicad-cli is required; no substitutes for native rendering")
    args.output.mkdir(parents=True, exist_ok=True)
    render(args.frames, args.output.resolve())


if __name__ == "__main__":
    main()
