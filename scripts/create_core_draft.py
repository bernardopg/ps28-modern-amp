#!/usr/bin/env python3
"""Create the initial TPA3255 fig.31 capture, only over an empty schematic.
Outputs to build/core-draft by default. --apply installs the initial capture.
No routing, supply design, manufacturing export or sign-off.
"""

from pathlib import Path
import argparse
import copy
import json
import math
import re
import shutil
import uuid

ROOT = Path(__file__).resolve().parents[1]
NS = uuid.UUID("633a57e0-e137-445b-bc4c-cd5e22e3f782")
SOURCE = "TI SLASEA8A: p.3-4 pins; p.28 fig.31/table11; DDV0044D top PowerPAD"
TPA_FP = "Package_SO:HTSSOP-44_6.1x14mm_P0.635mm_TopEP4.14x7.01mm"


def uid(name):
    return str(uuid.uuid5(NS, name))


def q(value):
    return json.dumps(str(value), ensure_ascii=False)


def parse(text):
    tokens = iter(re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text))

    def body():
        result = []
        for token in tokens:
            if token == "(":
                result.append(body())
            elif token == ")":
                return result
            else:
                result.append(token)
        raise ValueError("unbalanced S-expression")

    if next(tokens) != "(":
        raise ValueError("expected S-expression")
    return body()


def render(node):
    return "(" + " ".join(render(x) if isinstance(x, list) else x for x in node) + ")"


def walk(node):
    yield node
    for child in node:
        if isinstance(child, list):
            yield from walk(child)


def stock_symbol(library, name):
    tree = parse(
        (Path("/usr/share/kicad/symbols") / f"{library}.kicad_sym").read_text()
    )
    symbol = next(
        copy.deepcopy(x)
        for x in tree
        if isinstance(x, list) and x[:2] == ["symbol", q(name)]
    )
    if any(x[0] == "extends" for x in symbol if isinstance(x, list)):
        raise ValueError(f"Inheritance not supported: {library}:{name}")
    symbol[1] = q(f"{library}:{name}")
    return symbol


PIN_NAMES = {
    1: "GVDD_AB",
    2: "VDD",
    3: "M1",
    4: "M2",
    5: "INPUT_A",
    6: "INPUT_B",
    7: "OC_ADJ",
    8: "FREQ_ADJ",
    9: "OSC_IOM",
    10: "OSC_IOP",
    11: "DVDD",
    12: "GND",
    13: "GND",
    14: "AVDD",
    15: "C_START",
    16: "INPUT_C",
    17: "INPUT_D",
    18: "~{RESET}",
    19: "~{FAULT}",
    20: "VBG",
    21: "~{CLIP_OTW}",
    22: "GVDD_CD",
    23: "BST_D",
    24: "BST_C",
    25: "GND",
    26: "GND",
    27: "OUT_D",
    28: "OUT_D",
    29: "PVDD_CD",
    30: "PVDD_CD",
    31: "PVDD_CD",
    32: "OUT_C",
    33: "GND",
    34: "GND",
    35: "OUT_B",
    36: "PVDD_AB",
    37: "PVDD_AB",
    38: "PVDD_AB",
    39: "OUT_A",
    40: "OUT_A",
    41: "GND",
    42: "GND",
    43: "BST_B",
    44: "BST_A",
}


def tpa_symbol():
    pins = []
    for number, name in PIN_NAMES.items():
        if name == "GND" or name.startswith(("PVDD", "GVDD", "BST")) or name == "VDD":
            electrical = "power_in"
        elif name.startswith("OUT_") or name in {"DVDD", "AVDD", "VBG"}:
            electrical = "power_out"
        elif number in {19, 21}:
            electrical = "open_collector"
        elif number in {10, 15, 8}:
            electrical = "output"
        elif number in {7, 9}:
            electrical = "bidirectional"
        else:
            electrical = "input"
        x = -22.86 if number <= 22 else 22.86
        y = (
            26.67 - (number - 1) * 2.54
            if number <= 22
            else (number - 23) * 2.54 - 26.67
        )
        angle = 0 if number <= 22 else 180
        pins.append(
            f"(pin {electrical} line (at {x} {y:.2f} {angle}) (length 5.08) "
            f"(name {q(name)} (effects (font (size 1 1)))) "
            f"(number {q(number)} (effects (font (size 1 1)))))"
        )
    return parse(f"""(symbol "PS28:TPA3255DDV" (pin_names (offset 1.016))
      (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 33.02 0) (effects (font (size 1.27 1.27))))
      (property "Value" "TPA3255DDV" (at 0 -33.02 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" {q(TPA_FP)} (at 0 0 0) (effects (font (size 1 1)) (hide yes)))
      (property "Datasheet" "https://www.ti.com/lit/ds/symlink/tpa3255.pdf" (at 0 0 0) (effects (font (size 1 1)) (hide yes)))
      (symbol "TPA3255DDV_0_1" (rectangle (start -17.78 30.48) (end 17.78 -30.48)
        (stroke (width 0.254) (type default)) (fill (type background))))
      (symbol "TPA3255DDV_1_1" {" ".join(pins)}))""")


def library_pins(symbol):
    result = []
    for node in walk(symbol):
        if node and node[0] == "pin":
            at = next(x for x in node if isinstance(x, list) and x[0] == "at")
            number = next(x for x in node if isinstance(x, list) and x[0] == "number")
            result.append(
                (json.loads(number[1]), float(at[1]), float(at[2]), float(at[3]))
            )
    return result


def components():
    parts = []

    def add(
        ref, lib, value, nets, footprint="", pos=None, selection="MPN/ratings pending"
    ):
        parts.append(
            {
                "ref": ref,
                "lib_id": lib,
                "value": value,
                "nets": {str(k): v for k, v in nets.items()},
                "footprint": footprint,
                "pcb_position": pos,
                "selection": selection,
            }
        )

    pin_nets = {}
    for number, name in PIN_NAMES.items():
        if name.startswith("OUT_"):
            net = "PWM_AC" if name in {"OUT_A", "OUT_C"} else "PWM_BD"
        elif name.startswith("PVDD"):
            net = "PVDD_36V"
        elif number == 3 or number in {16, 17} or name == "GND":
            net = "GND"
        elif number in {4, 11}:
            net = "DVDD_INTERNAL"
        elif number == 2:
            net = "AUX_12V"
        elif number in {9, 10}:
            net = None
        elif number in {5, 6}:
            net = f"INPUT_{'A' if number == 5 else 'B'}_AC"
        else:
            net = name.replace("~{", "").replace("}", "")
        pin_nets[number] = net
    add(
        "U1",
        "PS28:TPA3255DDV",
        "TPA3255DDV",
        pin_nets,
        TPA_FP,
        [75, 60],
        "TI package/pinout checked; order MPN TBD",
    )
    resistor_count = 0
    capacitor_count = 0

    def resistor(value, a, b, x, y, size="0603"):
        nonlocal resistor_count
        resistor_count += 1
        add(
            f"R{resistor_count}",
            "Device:R",
            value,
            {1: a, 2: b},
            f"Resistor_SMD:R_{size}_{'1608' if size == '0603' else '3216'}Metric",
            [x, y],
        )

    def capacitor(value, a, b, x=None, y=None, size="0603", polarized=False):
        nonlocal capacitor_count
        capacitor_count += 1
        # Output filter dielectric/package must not be silently committed to MLCC.
        fp = (
            ""
            if polarized or value.startswith("470nF")
            else f"Capacitor_SMD:C_{size}_{'1608' if size == '0603' else '3216'}Metric"
        )
        add(
            f"C{capacitor_count}",
            "Device:C_Polarized" if polarized else "Device:C",
            value,
            {1: a, 2: b},
            fp,
            [x, y] if x is not None else None,
        )

    resistor("3.3R", "AUX_12V", "GVDD_AB", 64, 48)
    resistor("3.3R", "AUX_12V", "GVDD_CD", 64, 73)
    resistor("22k 1%", "OC_ADJ", "GND", 55, 64)
    resistor("30k 1%", "FREQ_ADJ", "GND", 55, 68)
    capacitor("470uF voltage/ripple TBD", "AUX_12V", "GND", polarized=True)
    capacitor("100nF 25V X7R", "AUX_12V", "GND", 66, 52)
    capacitor("10uF 25V X7R", "AUX_12V", "GND", 61, 52, size="1206")
    capacitor("100nF 25V X7R", "GVDD_AB", "GND", 65, 56)
    capacitor("100nF 25V X7R", "GVDD_CD", "GND", 65, 69)
    capacitor("1uF 16V X7R", "DVDD_INTERNAL", "GND", 61, 60)
    capacitor("1uF 16V X7R", "AVDD", "GND", 56, 56)
    capacitor("47nF 25V X7R", "C_START", "GND", 56, 60)
    capacitor("1uF 16V X7R", "VBG", "GND", 60, 72)
    for index, position in enumerate([(84, 55), (84, 60), (84, 65), (84, 70)]):
        capacitor("1uF 100V X7R", "PVDD_36V", "GND", *position, size="1206")
    # The bulk and magnetic footprints deliberately remain unassigned until MPN selection.
    capacitor("470uF 63V ripple TBD", "PVDD_36V", "GND", polarized=True)
    capacitor("470uF 63V ripple TBD", "PVDD_36V", "GND", polarized=True)
    for name, net, x, y in [
        ("A", "PWM_AC", 85, 48),
        ("B", "PWM_BD", 89, 57),
        ("C", "PWM_AC", 89, 66),
        ("D", "PWM_BD", 85, 77),
    ]:
        capacitor("33nF 25V X7R", f"BST_{name}", net, x, y)
    capacitor("10uF 16V X7R", "DIFF_P", "INPUT_A_AC", 55, 46, size="1206")
    capacitor("10uF 16V X7R", "DIFF_N", "INPUT_B_AC", 55, 50, size="1206")
    add("L1", "Device:L", "10uH Isat/Irms/MPN TBD", {1: "PWM_AC", 2: "SPK_P"})
    add("L2", "Device:L", "10uH Isat/Irms/MPN TBD", {1: "PWM_BD", 2: "SPK_N"})
    # Fig.31 uses 2 x 470nF per leg, plus 1nF and 10nF/3.3R networks.
    for net, y in [("SPK_P", 45), ("SPK_N", 80)]:
        capacitor("470nF 100V dielectric TBD", net, "GND", 132, y, size="1206")
        capacitor("470nF 100V dielectric TBD", net, "GND", 132, y + 5, size="1206")
        capacitor("1nF 100V C0G", net, "GND", 139, y)
        snubber = net + "_SNUB"
        capacitor("10nF 100V dielectric TBD", net, snubber, 144, y, size="1206")
        resistor("3.3R power TBD", snubber, "GND", 144, y + 5, size="1206")
    # External control interface, low-power pull-ups; no external loads on internal DVDD.
    resistor("10k", "VIO_3V3_EXTERNAL", "FAULT", 40, 90)
    resistor("10k", "VIO_3V3_EXTERNAL", "CLIP_OTW", 40, 94)
    resistor("10k RESET safe-low", "RESET", "GND", 40, 98)
    add(
        "J1",
        "Connector_Generic:Conn_01x02",
        "36V regulated input - connector TBD",
        {1: "PVDD_36V", 2: "GND"},
    )
    add(
        "J2",
        "Connector_Generic:Conn_01x02",
        "12V auxiliary",
        {1: "AUX_12V", 2: "GND"},
        "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
        [35, 35],
    )
    add(
        "J3",
        "Connector_Generic:Conn_01x03",
        "Differential audio interface",
        {1: "DIFF_P", 2: "DIFF_N", 3: "GND"},
        "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
        [35, 65],
    )
    add(
        "J4",
        "Connector_Generic:Conn_01x05",
        "Control: 3V3 RESET FAULT CLIP GND",
        {1: "VIO_3V3_EXTERNAL", 2: "RESET", 3: "FAULT", 4: "CLIP_OTW", 5: "GND"},
        "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical",
        [35, 85],
    )
    add(
        "J5",
        "Connector_Generic:Conn_01x02",
        "Floating speaker - connector TBD",
        {1: "SPK_P", 2: "SPK_N"},
    )
    add(
        "J6",
        "Connector_Generic:Conn_01x01",
        "Grounded top heatsink bond - mechanical TBD",
        {1: "GND"},
    )
    return parts


def build_capture():
    parts = components()
    symbols = {"PS28:TPA3255DDV": tpa_symbol()}
    for lib_id in sorted({p["lib_id"] for p in parts} | {"power:PWR_FLAG"}):
        if lib_id not in symbols:
            symbols[lib_id] = stock_symbol(*lib_id.split(":"))
    root_uuid = uid("schematic-root")
    out = [
        f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {q(root_uuid)}) (paper "A3")',
        '(title_block (title "PS28 - TPA3255 CORE DRAFT - NOT FOR FABRICATION") (rev "A-core-draft"))',
        "(lib_symbols " + " ".join(render(s) for s in symbols.values()) + ")",
    ]
    passive_index = 0
    connectors = 0
    symbol_positions = {}

    def place(ref, lib_id, value, nets, x, y, footprint="", selection="not a BOM part"):
        x, y = round(round(x / 1.27) * 1.27, 4), round(round(y / 1.27) * 1.27, 4)
        symbol_positions[ref] = [x, y]
        sym_uuid = uid("symbol:" + ref)
        properties = [
            ("Reference", ref, x, y - 4, False),
            ("Value", value, x, y + 4, False),
            ("Footprint", footprint, x, y, True),
            ("SelectionStatus", selection, x, y, True),
            ("Source", SOURCE, x, y, True),
        ]
        prop_text = " ".join(
            f"(property {q(name)} {q(text)} (at {px} {py} 0) "
            f"(effects (font (size 1 1)) {'(hide yes)' if hidden else ''}))"
            for name, text, px, py, hidden in properties
        )
        pins = library_pins(symbols[lib_id])
        pin_text = " ".join(
            f"(pin {q(number)} (uuid {q(uid(ref + ':pin:' + number))}))"
            for number, *_ in pins
        )
        included = "no" if ref.startswith("#") else "yes"
        out.append(
            f"(symbol (lib_id {q(lib_id)}) (at {x} {y} 0) (unit 1) (in_bom {included}) (on_board {included}) "
            f"(uuid {q(sym_uuid)}) {prop_text} {pin_text} "
            f'(instances (project "ps28-modern" (path {q("/" + root_uuid)} '
            f"(reference {q(ref)}) (unit 1)))))"
        )
        for number, px, py, angle in pins:
            wx, wy = round(x + px, 4), round(y - py, 4)
            net = nets.get(number)
            if net is None:
                out.append(
                    f"(no_connect (at {wx} {wy}) (uuid {q(uid(ref + ':nc:' + number))}))"
                )
                continue
            rad = math.radians(angle + 180)
            lx, ly = (
                round(wx + 2.54 * math.cos(rad), 4),
                round(wy - 2.54 * math.sin(rad), 4),
            )
            out.append(
                f"(wire (pts (xy {wx} {wy}) (xy {lx} {ly})) "
                f"(stroke (width 0) (type default)) (uuid {q(uid(ref + ':wire:' + number))}))"
            )
            justify = "right bottom" if lx < wx else "left bottom"
            out.append(
                f"(label {q(net)} (at {lx} {ly} 0) "
                f"(effects (font (size 0.9 0.9)) (justify {justify})) (uuid {q(uid(ref + ':label:' + number))}))"
            )

    for part in parts:
        if part["ref"] == "U1":
            x, y = 65, 80
        elif part["ref"].startswith("J"):
            x, y = 35 + connectors * 70, 175
            connectors += 1
        else:
            x, y = 150 + (passive_index % 7) * 35.56, 25.4 + (passive_index // 7) * 25.4
            passive_index += 1
        place(
            part["ref"],
            part["lib_id"],
            part["value"],
            part["nets"],
            x,
            y,
            part["footprint"],
            part["selection"],
        )
    for i, net in enumerate(
        ["GND", "PVDD_36V", "AUX_12V", "VIO_3V3_EXTERNAL", "GVDD_AB", "GVDD_CD"]
    ):
        place(
            f"#FLG0{i + 1}", "power:PWR_FLAG", "PWR_FLAG", {"1": net}, 40 + i * 45, 220
        )
    out.append(
        f'(text "CORE ONLY - RESET DEFAULT LOW - NO SUPPLY/FRONT-END - NO MANUFACTURING" '
        f"(at 25 245 0) (effects (font (size 1.5 1.5)) (justify left)) (uuid {q(uid('warning'))}))"
    )
    out.append(")")
    manifest = {
        "source": SOURCE,
        "schematic_uuid": root_uuid,
        "core_only": True,
        "parts": parts,
        "symbol_positions": symbol_positions,
        "unassigned_footprints": [p["ref"] for p in parts if not p["footprint"]],
    }
    custom = copy.deepcopy(symbols["PS28:TPA3255DDV"])
    custom[1] = q("TPA3255DDV")
    lib = (
        '(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '
        + render(custom)
        + ")\n"
    )
    return "\n".join(out) + "\n", lib, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    target = ROOT / "kicad/ps28-modern.kicad_sch"
    if args.apply and re.search(r"\(symbol\s+\(lib_id", target.read_text()):
        raise SystemExit(
            "Refusing to replace a nonempty schematic. Use KiCad for subsequent edits."
        )
    schematic, library, manifest = build_capture()
    build = ROOT / "build/core-draft"
    build.mkdir(parents=True, exist_ok=True)
    (build / "ps28-modern.kicad_sch").write_text(schematic)
    (build / "PS28.kicad_sym").write_text(library)
    (build / "core-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if args.apply:
        local = ROOT / "kicad/libraries"
        local.mkdir(exist_ok=True)
        if (ROOT / "kicad/sym-lib-table").exists():
            raise SystemExit("Refusing to replace existing local symbol table")
        shutil.copy2(build / "PS28.kicad_sym", local / "PS28.kicad_sym")
        (ROOT / "kicad/sym-lib-table").write_text(
            "(sym_lib_table (version 7)\n"
            ' (lib (name "PS28") (type "KiCad") (uri "${KIPRJMOD}/libraries/PS28.kicad_sym") (options "") (descr "TPA3255DDV custom pinout; top PowerPAD")))\n'
        )
        shutil.copy2(build / "ps28-modern.kicad_sch", target)
        shutil.copy2(build / "core-manifest.json", ROOT / "kicad/core-manifest.json")
    print(
        f"{len(manifest['parts'])} components captured; not manufacturing ready. Apply={args.apply}"
    )


if __name__ == "__main__":
    main()
