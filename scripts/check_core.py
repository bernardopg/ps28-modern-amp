#!/usr/bin/env python3
"""Check captured pin connectivity and placed-pad nets, without requiring KiCad.
This is a graph consistency check, not electrical/thermal/manufacturing approval.
"""

from pathlib import Path
import json

from create_core_draft import parse, library_pins, walk

ROOT = Path(__file__).resolve().parents[1]


def child(node, tag):
    return next((x for x in node if isinstance(x, list) and x and x[0] == tag), None)


def text(token):
    return json.loads(token) if token.startswith('"') else token


def position(node):
    return tuple(round(float(v), 4) for v in node[1:3])


def design_dir(root=ROOT):
    selected = root / "kicad/core-selected"
    return selected if (selected / "core-manifest.json").exists() else root / "kicad"


def check(root=ROOT):
    errors = []
    directory = design_dir(root)
    manifest = json.loads((directory / "core-manifest.json").read_text())
    schematic = parse((directory / "ps28-modern.kicad_sch").read_text())
    board = parse((directory / "ps28-modern.kicad_pcb").read_text())
    layer_names = {text(x[1]) for x in child(board, "layers")[1:]}
    for node in walk(board):
        if node and node[0] == "layer" and text(node[1]) not in layer_names:
            errors.append(f"Undefined PCB layer: {text(node[1])}")
    cache = {text(x[1]): x for x in child(schematic, "lib_symbols")[1:]}
    parent = {}

    def find(point):
        parent.setdefault(point, point)
        if parent[point] != point:
            parent[point] = find(parent[point])
        return parent[point]

    def union(a, b):
        parent[find(a)] = find(b)

    labels = []
    for item in schematic:
        if not isinstance(item, list):
            continue
        if item[0] == "wire":
            points = child(item, "pts")
            union(position(points[1]), position(points[2]))
        elif item[0] == "label":
            labels.append((position(child(item, "at")), text(item[1])))
    label_groups = {}
    for point, name in labels:
        label_groups.setdefault(find(point), set()).add(name)
    for names in label_groups.values():
        if len(names) > 1:
            errors.append(f"Conflicting labels: {sorted(names)}")
    captured = {}
    values = {}
    for item in schematic:
        if (
            not isinstance(item, list)
            or item[0] != "symbol"
            or not child(item, "lib_id")
        ):
            continue
        properties = {
            text(x[1]): text(x[2])
            for x in item
            if isinstance(x, list) and x[0] == "property"
        }
        ref = properties["Reference"]
        if ref.startswith("#"):
            continue
        values[ref] = properties["Value"]
        at = child(item, "at")
        if float(at[3]) != 0:
            errors.append(f"Checker only handles unrotated schematic symbols: {ref}")
            continue
        x, y = position(at)
        symbol = cache[text(child(item, "lib_id")[1])]
        for number, px, py, _ in library_pins(symbol):
            point = (round(x + px, 4), round(y - py, 4))
            names = label_groups.get(find(point), set())
            captured[(ref, number)] = next(iter(names)) if len(names) == 1 else None
    expected = {
        (p["ref"], pin): net
        for p in manifest["parts"]
        for pin, net in p["nets"].items()
    }
    if captured != expected:
        for key in expected.keys() | captured.keys():
            if (
                key not in captured
                or key not in expected
                or captured.get(key) != expected.get(key)
            ):
                errors.append(
                    f"Pin mismatch {key}: {captured.get(key)} != {expected.get(key)}"
                )
    for part in manifest["parts"]:
        if values.get(part["ref"]) != part["value"]:
            errors.append(f"Value mismatch: {part['ref']}")
    # Independent reference invariants: TI p.4 table1 / p.28 figure31.
    for pin in ["39", "40", "32"]:
        if captured.get(("U1", pin)) != "PWM_AC":
            errors.append(f"PBTL AC parallel mismatch: U1.{pin}")
    for pin in ["35", "27", "28"]:
        if captured.get(("U1", pin)) != "PWM_BD":
            errors.append(f"PBTL BD parallel mismatch: U1.{pin}")
    for pin, name in {
        "3": "GND",
        "4": "DVDD_INTERNAL",
        "11": "DVDD_INTERNAL",
        "16": "GND",
        "17": "GND",
        "18": "RESET",
        "2": "AUX_12V",
    }.items():
        if captured.get(("U1", pin)) != name:
            errors.append(f"Mode/supply/control mismatch: U1.{pin}")
    if captured.get(("J5", "1")) != "SPK_P" or captured.get(("J5", "2")) != "SPK_N":
        errors.append("Speaker must be floating, SPK_P/SPK_N")
    footprints = {}
    placed_pads = 0
    for item in board:
        if not isinstance(item, list) or item[0] != "footprint":
            continue
        props = {
            text(x[1]): text(x[2])
            for x in item
            if isinstance(x, list) and x[0] == "property"
        }
        ref = props["Reference"]
        footprints[ref] = text(item[1])
        pads = set()
        for pad in item:
            if not isinstance(pad, list) or pad[0] != "pad" or not text(pad[1]):
                continue
            number = text(pad[1])
            pads.add(number)
            net = child(pad, "net")
            name = text(net[-1]) if net else None
            if name and name.startswith("/"):
                name = name[1:]
            expected_net = captured.get((ref, number))
            is_no_connect = (
                expected_net is None
                and name is not None
                and name.startswith("unconnected-")
            )
            if name != expected_net and not is_no_connect:
                errors.append(
                    f"PCB pad mismatch {ref}.{number}: {name} != {captured.get((ref, number))}"
                )
            placed_pads += 1
        if ref == "U1" and pads != {str(i) for i in range(1, 45)}:
            errors.append(
                "DDV top PowerPAD must have 44 solder pads, not an invented PCB pad 45"
            )
    for part in manifest["parts"]:
        if part["footprint"] and footprints.get(part["ref"]) != part["footprint"]:
            errors.append(f"PCB footprint mismatch: {part['ref']}")
        if not part["footprint"] and part["ref"] in footprints:
            errors.append(f"Unselected footprint unexpectedly present: {part['ref']}")
    if "TopEP" not in footprints.get("U1", ""):
        errors.append("Wrong DDV PowerPAD orientation/footprint")
    return errors, {
        "components": len(values),
        "placed_footprints": len(footprints),
        "placed_pads_checked": placed_pads,
        "manufacturing_approved": False,
    }


if __name__ == "__main__":
    failures, report = check()
    print(json.dumps(report, indent=2))
    for error in failures:
        print("ERROR:", error)
    raise SystemExit(bool(failures))
