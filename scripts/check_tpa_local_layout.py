#!/usr/bin/env python3
"""Métricas CAD de desacoplamento local; não substituem DRC nem ensaio de EMI."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "kicad/system-candidate/system-candidate.kicad_pcb"
# Limites de regressão escolhidos para este layout, NÃO limites publicados pela TI.
LOCAL = {"C16": "44", "C17": "43", "C18": "24", "C19": "23",
         "C4": "1", "C5": "22", "C6": "4", "C7": "14", "C9": "20",
         "C2": "2", "C8": "15", "C13": "37", "C10": "30"}


def inspect_board(path=BOARD):
    import pcbnew
    board = pcbnew.LoadBoard(str(path))
    mm = pcbnew.ToMM
    def pad(ref, number):
        fp = board.FindFootprintByReference(ref)
        return next(p for p in fp.Pads() if p.GetNumber() == number)
    rows = {}
    for ref, pin in LOCAL.items():
        fp = board.FindFootprintByReference(ref)
        a, b = pad(ref, "1"), pad("U1", pin)
        if a.GetNetCode() != b.GetNetCode():
            raise ValueError(f"Net divergente em {ref}.1 / U1.{pin}")
        rows[ref] = {"pin": pin, "net": a.GetNetname(), "side": fp.GetLayerName(),
                     "pad_to_pin_mm": round(mm((a.GetPosition() - b.GetPosition()).EuclideanNorm()), 4),
                     "position_mm": [mm(fp.GetPosition().x), mm(fp.GetPosition().y)],
                     "rotation_deg": fp.GetOrientationDegrees()}
    bootstrap_lengths = {}
    for net in ("/BST_A", "/BST_B", "/BST_C", "/BST_D"):
        tracks = [t for t in board.GetTracks() if t.GetNetname() == net]
        bootstrap_lengths[net] = {
            "track_length_mm": round(sum(mm(t.GetLength()) for t in tracks if t.GetClass() == "PCB_TRACK"), 4),
            "vias": sum(t.GetClass() == "PCB_VIA" for t in tracks),
            "layers": sorted({t.GetLayerName() for t in tracks if t.GetClass() == "PCB_TRACK"})}
    return {"board_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
            "distance_metric": "Distância planar entre centros; não inclui espessura/vias nem prova indutância de laço.",
            "local_components": rows, "bootstrap_copper": bootstrap_lengths,
            "in1_signal_tracks": sum(t.GetClass() == "PCB_TRACK" and t.GetLayer() == pcbnew.In1_Cu
                                      and t.GetNetname() != "/GND" for t in board.GetTracks()),
            "manufacturing_approved": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", type=Path, default=BOARD)
    parser.add_argument("--output", type=Path, default=ROOT / "build/tpa-local-layout.json")
    args = parser.parse_args()
    report = inspect_board(args.board)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
