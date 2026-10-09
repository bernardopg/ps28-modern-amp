#!/usr/bin/env python3
"""Capture D-021 PVDD rectifier block separately; never overwrite existing designs.

Scope: T1 secondary input, CT return fuse, two-diode full-wave rectifier, added bulk,
bleeder and TVS. AUX 12 V buck and PVDD over-voltage supervisor are specified in
docs/power-d021.md but NOT captured: no verified MPN/symbol yet.
"""

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from create_analog_capture import build
from simulate_opa1656 import ROOT

DESIGN = ROOT / "kicad/power-d021"
SOURCE = "D-021: unregulated PVDD from T1 CT two-diode rectifier; study only; no hardware sign-off"


def parts():
    # (ref, lib_id, value, MPN or requirement, footprint, pin->net)
    specs = [
        ("J301", "Connector_Generic:Conn_01x03", "T1_SECONDARY",
         "TBD: mate original T1 harness (3-way, red-black-red, ~3.96 mm pitch, 20 AWG UL1015); >=8 A/pin", "",
         {"1": "T1_A", "2": "T1_CT", "3": "T1_B"}),
        ("F301", "Device:Fuse", "T8A slow",
         "TBD: time-lag, I2t >= 60 A2s inrush margin, >=63 VDC", "",
         {"1": "T1_CT", "2": "GND"}),
        ("D301", "Device:D", "RECT >=400V",
         "TBD: VRRM>=400 V, IF(AV)>=6 A, IFSM>=200 A", "",
         {"1": "PVDD", "2": "T1_A"}),
        ("D302", "Device:D", "RECT >=400V",
         "TBD: VRRM>=400 V, IF(AV)>=6 A, IFSM>=200 A", "",
         {"1": "PVDD", "2": "T1_B"}),
        ("C301", "Device:C_Polarized", "4700u 63V",
         "TBD: >=63 V, 105 C, ripple >=3.5 A at 120 Hz each", "",
         {"1": "PVDD", "2": "GND"}),
        ("C302", "Device:C_Polarized", "4700u 63V",
         "TBD: >=63 V, 105 C, ripple >=3.5 A at 120 Hz each", "",
         {"1": "PVDD", "2": "GND"}),
        ("R301", "Device:R", "4.7k 2W",
         "TBD: >=1 W continuous at 50 V (0.53 W), >=100 V", "",
         {"1": "PVDD", "2": "GND"}),
        ("D303", "Device:D_TVS", "TVS VWM>=51V",
         "TBD: VWM>=51 V (above 49.8 V worst idle), Vc below 69 V abs max at rated pulse", "",
         {"1": "PVDD", "2": "GND"}),
        ("J302", "Connector_Generic:Conn_01x02", "PVDD_TO_CORE",
         "Logical interface to core J1; same PCB, not a new connector", "",
         {"1": "PVDD", "2": "GND"}),
    ]
    return [
        {"ref": r, "lib_id": lib, "value": v, "mpn": m, "footprint": fp, "nets": n,
         "units": [(1, 50.8 + (i % 3) * 88.9, 50.8 + (i // 3) * 55.88)]}
        for i, (r, lib, v, m, fp, n) in enumerate(specs)
    ]


def generate(out):
    if out.exists():
        raise FileExistsError("Refusing to overwrite existing power capture")
    out.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix=".power-d021-", dir=out.parent))
    try:
        sch, manifest = build(
            parts(),
            project="power-d021",
            namespace="power-d021",
            source=SOURCE,
            title="PS28 D-021 PVDD RECTIFIER - STUDY ONLY",
            warning="NEVER BRIDGE T1_A-T1_B (~97 V). AUX 12V BUCK AND PVDD OVP SUPERVISOR NOT CAPTURED. MPN/FOOTPRINTS TBD.",
            power_flags=("PVDD", "GND"),
        )
        manifest["interface_contract"] = {
            "J301": "1=red A, 2=black CT, 3=red B; order photo-confirmed 2026-10-09; ~3.96 mm pitch measured; header series/rating TBD",
            "J302": "PVDD 40-50 V unregulated to core J1; core C14/C15 3000 uF add to C301/C302",
            "not_captured": ["AUX 12 V buck (Vin>=65 V)", "PVDD OVP to RESET/relay supervisor"],
            "new_physical_board": False,
        }
        (staged / "power-d021.kicad_sch").write_text(sch)
        (staged / "power-d021.kicad_pro").write_text("{}\n")
        (staged / "power-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        staged.rename(out)
    except BaseException:
        shutil.rmtree(staged, ignore_errors=True)
        raise


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=DESIGN)
    generate(p.parse_args().output)
