#!/usr/bin/env python3
"""Isolated labelled analog capture. Never overwrites/merges a PCB or existing schematic."""

import argparse
import json
import math
import tempfile
from pathlib import Path

from create_core_draft import q, render, stock_symbol, uid, walk

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "TI SBOS901C fig.5-3 p.3; SLOA024B fig.5/eq.9 p.4; D-015/D-016 study"


def child(node, tag):
    return next((x for x in node if isinstance(x, list) and x[0] == tag), None)


def opamp_symbol():
    # KiCad OPA1656ID inherits LM2904. Flatten only graphical/pin units locally;
    # physical pin numbering is audited against TI, not inferred from inheritance.
    base = stock_symbol("Amplifier_Operational", "LM2904")
    base[1] = q("PS28_ANALOG:OPA1656ID")
    for n in base:
        if isinstance(n, list) and n[0] == "symbol":
            n[1] = q(n[1].strip('"').replace("LM2904_", "OPA1656ID_"))
    expected = {1: "", 2: "-", 3: "+", 4: "V-", 5: "+", 6: "-", 7: "", 8: "V+"}
    actual = {
        int(child(n, "number")[1].strip('"')): child(n, "name")[1].strip('"')
        for n in walk(base)
        if n[0] == "pin"
    }
    if actual != expected:
        raise ValueError("Library pin mapping differs from reviewed TI SOIC8 pinout")
    for prop in base:
        if isinstance(prop, list) and prop[0] == "property":
            if prop[1] == q("Value"):
                prop[2] = q("OPA1656ID")
            if prop[1] == q("Footprint"):
                prop[2] = q("Package_SO:SOIC-8_3.9x4.9mm_P1.27mm")
            if prop[1] == q("Datasheet"):
                prop[2] = q("https://www.ti.com/lit/ds/symlink/opa1656.pdf")
            if prop[1] == q("Description"):
                prop[2] = q(
                    "OPA1656 dual audio amplifier; TI SBOS901C reviewed pinout; study"
                )
    return base


def parts():
    out = []

    def add(ref, lib, value, nets, units, fp="", mpn="TBD"):
        out.append(
            {
                "ref": ref,
                "lib_id": lib,
                "value": value,
                "nets": nets,
                "units": units,
                "footprint": fp,
                "mpn": mpn,
            }
        )

    add(
        "U2",
        "PS28_ANALOG:OPA1656ID",
        "OPA1656ID",
        {
            "1": "BUFFERED",
            "2": "BUFFERED",
            "3": "DIVIDED",
            "4": "GND",
            "5": "Y1",
            "6": "FILTERED1",
            "7": "FILTERED1",
            "8": "AUX_12V",
        },
        [[1, 45.72, 40.64], [2, 147.32, 40.64], [3, 274.32, 40.64]],
        "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
        "OPA1656ID",
    )
    add(
        "U3",
        "PS28_ANALOG:OPA1656ID",
        "OPA1656ID",
        {
            "1": "DIFF_POS",
            "2": "DIFF_POS",
            "3": "Y2",
            "4": "GND",
            "5": "VMID_EXTERNAL",
            "6": "MINUS",
            "7": "DIFF_NEG",
            "8": "AUX_12V",
        },
        [[1, 45.72, 116.84], [2, 147.32, 116.84], [3, 274.32, 111.76]],
        "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
        "OPA1656ID",
    )
    rn = [
        ("MONO_BIASED", "DIVIDED"),
        ("DIVIDED", "VMID_EXTERNAL"),
        ("BUFFERED", "X1"),
        ("X1", "Y1"),
        ("FILTERED1", "X2"),
        ("X2", "Y2"),
        ("DIFF_POS", "MINUS"),
        ("DIFF_NEG", "MINUS"),
    ]
    for i, (a, b) in enumerate(rn):
        row, col = divmod(i, 4)
        add(
            f"R{101 + i}",
            "Device:R",
            "14k" if i in [2, 3, 4, 5] else "10k",
            {"1": a, "2": b},
            [[1, 30.48 + col * 50.8, 198.12 + row * 30.48]],
            "Resistor_SMD:R_0805_2012Metric",
        )
    cn = [
        ("X1", "FILTERED1"),
        ("X1", "FILTERED1"),
        ("Y1", "VMID_EXTERNAL"),
        ("X2", "DIFF_POS"),
        ("X2", "DIFF_POS"),
        ("Y2", "VMID_EXTERNAL"),
        ("AUX_12V", "GND"),
        ("AUX_12V", "GND"),
    ]
    for i, (a, b) in enumerate(cn):
        row, col = divmod(i, 4)
        add(
            f"C{101 + i}",
            "Device:C",
            "100n",
            {"1": a, "2": b},
            [[1, 233.68 + col * 45.72, 198.12 + row * 30.48]],
            "Capacitor_SMD:C_0805_2012Metric" if i >= 6 else "",
        )
    add(
        "J101",
        "Connector_Generic:Conn_01x03",
        "INPUT_BIASED",
        {"1": "MONO_BIASED", "2": "VMID_EXTERNAL", "3": "GND"},
        [[1, 345.44, 40.64]],
    )
    add(
        "J102",
        "Connector_Generic:Conn_01x04",
        "DIFFERENTIAL_OUT",
        {"1": "DIFF_POS", "2": "DIFF_NEG", "3": "VMID_EXTERNAL", "4": "GND"},
        [[1, 345.44, 111.76]],
    )
    add(
        "J103",
        "Connector_Generic:Conn_01x03",
        "SUPPLY_EXTERNAL",
        {"1": "AUX_12V", "2": "VMID_EXTERNAL", "3": "GND"},
        [[1, 345.44, 157.48]],
    )
    return out


def build(
    inventory=None,
    *,
    project="analog-front-end",
    namespace="analog",
    source=SOURCE,
    title="PS28 ANALOG CAPTURE STUDY - NO POWER/VMID/SUPERVISOR",
    warning="STUDY ONLY - ALL INPUTS BIASED TO EXTERNAL VMID - NO RCA/LINE-LFE/VOLUME/DC PROTECTION - PASSIVE MPN/FOOTPRINT TBD",
    power_flags=("AUX_12V", "VMID_EXTERNAL", "GND"),
    paper="A3",
):
    inventory = parts() if inventory is None else inventory
    symbols = {"PS28_ANALOG:OPA1656ID": opamp_symbol()}
    for p in inventory:
        if p["lib_id"] not in symbols:
            symbols[p["lib_id"]] = stock_symbol(*p["lib_id"].split(":"))
    symbols["power:PWR_FLAG"] = stock_symbol("power", "PWR_FLAG")
    root = uid(namespace + ":root")
    out = [
        f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {q(root)}) (paper {q(paper)})',
        f'(title_block (title {q(title)}) (rev "A-analog-study"))',
        "(lib_symbols " + " ".join(render(x) for x in symbols.values()) + ")",
    ]

    def place(p, unit, x, y):
        lib = p["lib_id"]
        symbol = symbols[lib]
        pins = []
        for sub in symbol:
            if not isinstance(sub, list) or sub[0] != "symbol":
                continue
            suffix = sub[1].strip('"').rsplit("_", 2)
            if len(suffix) == 3 and int(suffix[-2]) in [0, unit]:
                pins.extend(n for n in walk(sub) if n[0] == "pin")
        props = {
            "Reference": p["ref"],
            "Value": p["value"],
            "Footprint": p["footprint"],
            "MPN": p["mpn"],
            "SelectionStatus": "STUDY; passives/interfaces not selected",
            "Source": source,
        }
        property_text = " ".join(
            f"(property {q(k)} {q(v)} (at {x} {y - 5.08 if k == 'Reference' else y + 5.08} 0) "
            f"(effects (font (size 1 1)) {'(hide yes)' if k not in ['Reference', 'Value'] else ''}))"
            for k, v in props.items()
        )
        pid = f"{p['ref']}:u{unit}"
        out.append(
            f"(symbol (lib_id {q(lib)}) (at {x} {y} 0) (unit {unit}) "
            f"(in_bom {'no' if p['ref'].startswith('#') else 'yes'}) (on_board {'no' if p['ref'].startswith('#') else 'yes'}) "
            f"(uuid {q(uid(namespace + ':' + pid))}) {property_text} "
            + " ".join(
                f"(pin {child(n, 'number')[1]} (uuid {q(uid(namespace + ':' + pid + ':pin:' + child(n, 'number')[1]))}))"
                for n in pins
            )
            + f"(instances (project {q(project)} (path {q('/' + root)} (reference {q(p['ref'])}) (unit {unit})))))"
        )
        for n in pins:
            number = child(n, "number")[1].strip('"')
            px, py, angle = map(float, child(n, "at")[1:])
            wx, wy = round(x + px, 4), round(y - py, 4)
            if number not in p["nets"]:
                raise ValueError("Unassigned analog pin: " + p["ref"] + "." + number)
            rad = math.radians(angle + 180)
            lx = round(wx + 3.81 * math.cos(rad), 4)
            ly = round(wy - 3.81 * math.sin(rad), 4)
            out.append(
                f"(wire (pts (xy {wx} {wy}) (xy {lx} {ly})) (stroke (width 0) (type default)) (uuid {q(uid(namespace + ':' + pid + ':wire:' + number))}))"
            )
            justify = "right bottom" if lx < wx else "left bottom"
            out.append(
                f"(label {q(p['nets'][number])} (at {lx} {ly} 0) (effects (font (size .9 .9)) (justify {justify})) (uuid {q(uid(namespace + ':' + pid + ':label:' + number))}))"
            )

    for p in inventory:
        for unit, x, y in p["units"]:
            place(p, unit, x, y)
    for i, net in enumerate(power_flags):
        place(
            {
                "ref": f"#FLG10{i}",
                "lib_id": "power:PWR_FLAG",
                "value": "PWR_FLAG",
                "footprint": "",
                "mpn": "",
                "nets": {"1": net},
            },
            1,
            45.72 + i * 76.2,
            266.7,
        )
    out.append(
        f"(text {q(warning)} "
        f"(at 20.32 12.7 0) (effects (font (size 1.2 1.2)) (justify left)) (uuid {q(uid(namespace + ':warning'))}))"
    )
    out.append(")")
    return "\n".join(out) + "\n", {
        "status": "ISOLATED CAPTURE STUDY",
        "source": source,
        "parts": inventory,
        "hardware_validated": False,
        "manufacturing_approved": False,
        "integrated_with_core": False,
        "unassigned_footprints": [p["ref"] for p in inventory if not p["footprint"]],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=ROOT / "kicad/analog-front-end")
    args = ap.parse_args()
    target = args.output.resolve()
    if target.exists():
        raise ValueError(
            "Refusing to overwrite existing analog capture: " + str(target)
        )
    schematic, manifest = build()
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".analog-stage-", dir=target.parent) as tmp:
        staged = Path(tmp) / target.name
        staged.mkdir()
        (staged / "analog-front-end.kicad_sch").write_text(schematic)
        (staged / "analog-front-end.kicad_pro").write_text(
            json.dumps(
                {"meta": {"filename": "analog-front-end.kicad_pro", "version": 1}},
                indent=2,
            )
            + "\n"
        )
        (staged / "analog-manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n"
        )
        library = opamp_symbol()
        library[1] = q("OPA1656ID")
        (staged / "libraries").mkdir()
        (staged / "libraries/PS28_ANALOG.kicad_sym").write_text(
            '(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '
            + render(library)
            + ")\n"
        )
        (staged / "sym-lib-table").write_text(
            '(sym_lib_table (version 7) (lib (name "PS28_ANALOG") '
            '(type "KiCad") (uri "${KIPRJMOD}/libraries/PS28_ANALOG.kicad_sym") (options "") '
            '(descr "Local flattened symbol; TI OPA1656 pinout audited; analog study")))\n'
        )
        staged.rename(target)
    print(
        f"Captured {len(manifest['parts'])} parts; passives/interfaces TBD; not manufacturing approved"
    )


if __name__ == "__main__":
    main()
