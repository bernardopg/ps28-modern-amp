#!/usr/bin/env python3
"""D-029 Rev A bench bring-up candidate: the system candidate without the T1 rectifier
block, PVDD from a current-limited bench supply through the audited core terminal J1.

Placed in staging for PCB-001/PCB-002 review: NOT routed, NOT approved for fabrication.
integrate_candidate.py stays untouched (its hash binds the routed study candidate).
"""

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import integrate_candidate as base

# Unqualified parts (docs/pcb-readiness-review.md) whose ratings depend on BENCH-001
# T1 inrush/I2t measurements (D-027): deferred to Rev B, no copper reserved here.
DEFERRED = {"J301", "F301", "D301", "D302", "C301", "C302"}
# Bench feed path that must replace the rectifier join: J1 -> bulk -> TPA PVDD.
JOINS = [(("J1", "1"), ("U1", "36")), (("J1", "1"), ("C14", "1")), (("J1", "1"), ("U302", "2")),
         (("J1", "2"), ("C14", "2")), (("L301", "2"), ("C1", "1")),
         (("R408", "2"), ("U1", "18")), (("U407", "1"), ("U1", "19")), (("U406", "2"), ("U1", "21"))]


def bench_parts(parts):
    return [p for p in parts if p["ref"] not in DEFERRED]


def check_bench(staged):
    xml = ET.parse(staged / "candidate.xml")
    native = {(n.get("ref"), n.get("pin")): net.get("name")
              for net in xml.findall(".//nets/net") for n in net.findall("node")}
    refs = {r for r, _ in native}
    if refs & DEFERRED:
        raise ValueError(f"Deferred Rev B parts present: {sorted(refs & DEFERRED)}")
    for a, b in JOINS:
        if native.get(a) is None or native.get(a) != native.get(b):
            raise ValueError(f"Bench join missing {a}-{b}")
    if native["J1", "1"] == native["J1", "2"]:
        raise ValueError("Bench terminal shorted")
    return native


def generate(out):
    system_parts, validate = base.system_parts, base.validate_staged

    def validate_bench(staged, inventory):
        native = check_bench(staged)
        try:
            return validate(staged, inventory)
        except KeyError as error:
            # The base check ends with the D-021 rectifier join (D301); every earlier
            # pad/net/D-019 check already passed when that lookup fails.
            if error.args != (("D301", "1"),):
                raise
        return {"native_pad_net_matches": len(native), "footprints": len(inventory),
                "signal_bridge_via_relay_only": "K501" in {r for r, _ in native},
                "bench_joins_checked": len(JOINS)}

    # shortcut: patches two module seams instead of forking 700 lines; fold a variant
    # argument into integrate_candidate.py when the routed study candidate is retired.
    base.system_parts = lambda: bench_parts(system_parts())
    base.validate_staged = validate_bench
    try:
        base.generate(out)
    finally:
        base.system_parts, base.validate_staged = system_parts, validate
    manifest_path = out / "system-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest.update(
        variant="D-029 Rev A bench bring-up",
        status="PLACED STUDY, UNROUTED; PVDD FROM CURRENT-LIMITED BENCH SUPPLY VIA J1",
        deferred_to_rev_b=sorted(DEFERRED),
        rectifier_d021_integrated=False,
        pvdd_source="J1 691137710002 from current-limited bench supply; limits per BENCH-001",
        routed=False,
    )
    manifest["source_sha256"][str(Path(__file__).resolve().relative_to(base.ROOT))] = (
        hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=base.ROOT / "kicad/rev-a-bench")
    generate(parser.parse_args().output)
