#!/usr/bin/env python3
"""Atomic core + D-018/D-021/D-020/D-024 review candidate; signal bridge only via the
D-019 relay (iso-d019), no overwrite."""

import copy
import ctypes
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

from create_analog_capture import build, child
from create_core_draft import parse, q, render, uid, walk
from create_pre_interface import analog_changes, parts as pre_parts, symbols as pre_symbols
from create_debug_io import parts as debug_parts, symbols as debug_symbols
from create_iso_d019 import dgk_footprint, local_symbols as iso_symbols, parts as iso_parts
from create_power_d021 import parts as power_parts, tps3700_symbol, write_local_library
from create_seq_d020 import lp2985_symbol, parts as seq_parts
from create_vmid_protection import integrated_parts

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "kicad/core-oem-refined"
MODELS = ROOT / "kicad/models/vendor-wurth"
PROJECT = "system-candidate"
# D-021: core PVDD_36V is no longer a 36 V regulated rail.
RENAMES = {"AUX_12V": "AUX_RAW", "PVDD_36V": "PVDD"}
# Bench/external control access stays on the board but is not populated: the on-board
# D-020 subset drives RESET and the TPA FAULT/CLIP_OTW internal pull-ups suffice.
# J3 (bench differential input) would parallel the OPA drivers once the bridge closes.
DNP = {"J3", "J4", "R7", "R8"}
LOGICAL = {"J302", "J303", "J402", "J501"}  # same-PCB interfaces, not connectors
# D-031: woofer harness is a 2-way JST VH plug (P102 in the PS28 manual p.14); the
# header replaces the core screw terminal so the OEM harness plugs in without splicing.
# C14/C15 shrink to D12.5 so the thermal block area stays free; bulk stays >= 10 mF
# with C301/C302 (Nichicon UHE CAT.8100M: UHE1J681MHD 680 uF/63 V 12.5x40, 0.071 ohm).
SWAPS = {
    "J5": ("Connector_JST", "JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "B2P-VH(LF)(SN)",
           "B2P-VH(LF)(SN)"),
    "C14": ("Capacitor_THT", "CP_Radial_D12.5mm_P5.00mm", "680uF 63V", "UHE1J681MHD"),
    "C15": ("Capacitor_THT", "CP_Radial_D12.5mm_P5.00mm", "680uF 63V", "UHE1J681MHD"),
}
SWAP_SOURCES = {
    "J5": "JST VH eVH-new p.3: B2P-VH(LF)(SN), 2 circuits, pitch3.96mm; D-031 OEM woofer harness",
    "C14": "Nichicon UHE CAT.8100M: UHE1J681MHD 680uF 63V D12.5x40 P5; Zmax0.071ohm at100kHz/20C; ripple1280mA at100kHz/105C; D-031",
    "C15": "Nichicon UHE CAT.8100M: UHE1J681MHD 680uF 63V D12.5x40 P5; Zmax0.071ohm at100kHz/20C; ripple1280mA at100kHz/105C; D-031",
}
# D-024: preamp drivers reach C20/C21; their TPA-side plates go to the relay COM.
BRIDGE = {"DIFF_POS": "DIFF_P", "DIFF_NEG": "DIFF_N"}
PLATES = {("C20", "2"): "INA_ISO", ("C21", "2"): "INB_ISO"}


def system_parts():
    """D-021 power and D-020 sequencing captures, minus logical interfaces."""
    out = []
    for group, source in (("power", power_parts()), ("seq", seq_parts()), ("iso", iso_parts()),
                          ("pre", pre_parts()), ("dbg", debug_parts())):
        for p in source:
            if p["ref"] in LOGICAL:
                continue
            p["group"] = group
            p["selection"] = "STUDY CANDIDATE; footprint not audited; MPN per capture"
            out.append(p)
    return out


def bank_position(p, index):
    """Import banks OUTSIDE the OEM outline: unplaced, never a fit claim."""
    group = p.get("group", "analog")
    x0, y0, dx, dy, cols = {
        "analog": (190, 25, 30, 22, 6),
        "power": (190, 130, 40, 32, 6),
        "seq": (420, 25, 22, 18, 8),
        "iso": (420, 185, 22, 20, 8),
        "pre": (420, 300, 22, 20, 8),
        "dbg": (600, 25, 18, 16, 8),
    }[group]
    return x0 + (index % cols) * dx, y0 + (index // cols) * dy


def candidates():
    parts = [p for p in integrated_parts() if not p["ref"].startswith("J")]
    for p in parts:
        p["nets"] = {k: BRIDGE.get(v, v) for k, v in p["nets"].items()}
        ref = p["ref"]
        if ref in {f"C{i}" for i in range(101, 107)}:
            p.update(
                mpn="MKP2D031001F00JSSD",
                footprint="Capacitor_THT:C_Rect_L7.2mm_W5.0mm_P5.00mm",
            )
        elif ref == "C203":
            p.update(
                mpn="MKP2C041001N00JSSD",
                footprint="Capacitor_THT:C_Rect_L7.2mm_W11.0mm_P5.00mm_FKS2_FKP2_MKS2_MKP2",
            )
        elif ref == "R201":
            p.update(
                mpn="AC03000001509JAC00",
                footprint="Resistor_THT:R_Axial_DIN0617_L17.0mm_D6.0mm_P5.08mm_Vertical",
            )
        elif ref in ("R202", "R203"):
            p.update(
                mpn="TNPW12061K00BEEA" if ref == "R202" else "TNPW12062K20BEEA",
                footprint="PS28_ANALOG:TNPW1206_IPC_Reflow",
            )
        p["selection"] = (
            "ENGINEERING CANDIDATE; pulse/ESR/temp/fit/power-off qualification pending"
        )
        p["group"] = "analog"
    # D-032: the OEM preamp/limiter do the crossover; IN arrives via C109 (pre group).
    return analog_changes(parts)


def replace_strings(node, mapping):
    for i, value in enumerate(node):
        if isinstance(value, list):
            replace_strings(value, mapping)
        elif value in mapping:
            node[i] = mapping[value]


def move(node, dy, dx=0):
    for item in walk(node):
        if item[0] in ("at", "xy") and len(item) >= 3:
            item[1] = str(round(float(item[1]) + dx, 4))
            item[2] = str(round(float(item[2]) + dy, 4))


def block(parts, namespace, warning):
    sch, _ = build(
        parts,
        project=PROJECT,
        namespace=namespace,
        source="D-021/D-020 captures; see docs/power-d021.md and docs/seq-d020.md",
        power_flags=(),
        paper="A0",
        warning=warning,
        extra_symbols={
            "PS28_POWER:TPS3700DDC": tps3700_symbol(),
            "PS28_SEQ:LP2985-33DBV": lp2985_symbol(),
            **{x[1].strip('"'): x for x in iso_symbols()},
            **pre_symbols(),
            **debug_symbols(),
        },
    )
    return parse(sch)


def set_property(symbol, name, value):
    prop = next(
        p
        for p in symbol
        if isinstance(p, list) and p[0] == "property" and p[1] == q(name)
    )
    prop[2] = q(value)


def schematic(parts, extra=()):
    root = parse((SOURCE / "ps28-modern.kicad_sch").read_text())
    if any(p.get("group") == "iso" for p in extra):
        # Core labels are deterministic (create_core_draft uid(ref:label:pin)).
        labels = {q(uid(f"{r}:label:{n}")): net for (r, n), net in PLATES.items()}
        for node in root:
            if isinstance(node, list) and node[0] == "label" and child(node, "uuid")[1] in labels:
                node[1] = q(labels.pop(child(node, "uuid")[1]))
        if labels:
            raise ValueError("Core C20/C21 plate labels not found")
    analog, _ = build(
        parts,
        project=PROJECT,
        namespace="system-analog",
        source="D-020 candidate; primary parts/landpattern refs in docs/integration-protection-review.md",
        power_flags=("ANALOG_12V",),
        paper="A1",
        warning="D-024: DRIVERS REACH TPA ONLY THROUGH RELAY K501 (iso-d019); DO NOT ENERGIZE",
    )
    analog = parse(analog)
    original_root = child(root, "uuid")[1]
    new_root = q(uid(PROJECT + ":root"))
    child(root, "uuid")[1] = new_root
    paper = child(root, "paper")
    paper[1:] = [q("User"), "1400", "841"] if extra else [q("A1")]
    child(child(root, "title_block"), "title")[1] = q(
        "PS28 CORE + ANALOG + D-021 POWER + D-020 SEQ SUBSET - INCOMPLETE SAFETY REVIEW"
        if extra
        else "PS28 CORE + PROTECTED ANALOG - INCOMPLETE SAFETY REVIEW CANDIDATE"
    )
    replace_strings(
        root,
        {
            **{q(a): q(b) for a, b in RENAMES.items()},
            q("ps28-modern"): q(PROJECT),
            q("/" + original_root.strip('"')): q("/" + new_root.strip('"')),
        },
    )
    replace_strings(
        analog,
        {
            q("/" + child(analog, "uuid")[1].strip('"')): q("/" + new_root.strip('"')),
            q("#FLG100"): q("#FLG901"),
        },
    )
    symbols = child(root, "lib_symbols")
    known = {x[1] for x in symbols[1:]}
    symbols.extend(x for x in child(analog, "lib_symbols")[1:] if x[1] not in known)
    if extra:
        # PBTL (TI SLASEA8A Fig 31): OUT_A/OUT_C and OUT_B/OUT_D are paralleled per bridge and
        # each output has two package pins. One driver pin per bridge net stays power_out;
        # the paralleled/duplicate pins become passive so ERC does not flag the intended tie.
        tpa = next(x for x in symbols[1:] if x[1] == q("PS28:TPA3255DDV"))
        for pin in walk(tpa):
            if pin[0] == "pin" and child(pin, "number")[1] in (q("27"), q("28"), q("32"), q("40")):
                pin[1] = "passive"
    for item in analog:
        if isinstance(item, list) and item[0] in (
            "symbol",
            "wire",
            "label",
            "text",
            "junction",
            "no_connect",
        ):
            move(item, 304.8)
            root.append(item)
    for group, dx, dy, warning in (
        ("power", 558.8, 0, "D-021 POWER: FOOTPRINTS NOT AUDITED; NEVER BRIDGE T1_A-T1_B"),
        ("seq", 558.8, 330.2, "D-020/D-024 DISCRETE SEQUENCER"),
        ("iso", 990.6, 0, "D-024 INPUT ISOLATION RELAY / MUTE / DC WINDOWS"),
        ("pre", 990.6, 381, "D-032 OEM PREAMP/LIMITER INTERFACE: P101, +/-15 V, LIMIT FROM CLIP_OTW"),
        ("dbg", 1270, 0, "PCB-004 TEST POINTS, STATUS LEDS, FAN OUTPUT (NO LOAD ON TPA/AUDIO NODES)"),
    ):
        members = [p for p in extra if p["group"] == group]
        if not members:
            continue
        sub = block(members, "system-" + group, warning)
        replace_strings(
            sub, {q("/" + child(sub, "uuid")[1].strip('"')): q("/" + new_root.strip('"'))}
        )
        known = {x[1] for x in symbols[1:]}
        symbols.extend(x for x in child(sub, "lib_symbols")[1:] if x[1] not in known)
        for item in sub:
            if isinstance(item, list) and item[0] in (
                "symbol", "wire", "label", "text", "junction", "no_connect",
            ):
                move(item, dy, dx)
                root.append(item)
    for item in root:
        if isinstance(item, list) and item[0] == "symbol":
            ref = next(
                x[2].strip('"')
                for x in item
                if isinstance(x, list) and x[0] == "property" and x[1] == q("Reference")
            )
            if ref == "R9":
                set_property(item, "Value", "4.7k 1%")
                set_property(item, "MPN", "CRCW06034K70FKEA")
            if ref in DNP and extra:
                flags = [x for x in item if isinstance(x, list) and x[0] == "on_board"]
                item.insert(item.index(flags[0]) + 1, ["dnp", "yes"])
            if ref in {p["ref"] for p in parts}:
                set_property(
                    item,
                    "SelectionStatus",
                    "CANDIDATE; NOT PULSE/ESR/POWER-OFF/FIT QUALIFIED",
                )
    return render(root) + "\n"


def tnpw_footprint():
    return """(footprint "TNPW1206_IPC_Reflow" (version 20241229) (generator "ps28")
(layer "F.Cu") (attr smd)
(descr "Vishay doc28950 rev12-Jul-2022 p1 IPC reflow recommendation; nominal body; no production approval")
(property "Reference" "REF**" (at 0 -2 0) (layer "F.SilkS") (effects(font(size 1 1)(thickness 0.15))))
(property "Value" "TNPW1206" (at 0 2 0) (layer "F.Fab") (effects(font(size 1 1)(thickness 0.15))))
(fp_rect(start -1.65 -0.875)(end 1.65 0.875)(stroke(width 0.1)(type default))(fill none)(layer "F.Fab"))
(fp_rect(start -2.275 -1.15)(end 2.275 1.15)(stroke(width 0.05)(type default))(fill none)(layer "F.CrtYd"))
(pad "1" smd roundrect(at -1.45 0)(size 1.15 1.80)(layers "F.Cu" "F.Paste" "F.Mask")(roundrect_rratio 0.2))
(pad "2" smd roundrect(at 1.45 0)(size 1.15 1.80)(layers "F.Cu" "F.Paste" "F.Mask")(roundrect_rratio 0.2))
(model "${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_1206_3216Metric.step" (offset(xyz 0 0 0))(scale(xyz 1 1 1))(rotate(xyz 0 0 0))))\n"""


def oem_mechanics():
    """Measured OEM main-PCB frame (MECH-001, owner tape measurements, ~1 mm error).

    KiCad frame: origin (20, 20); x along the backplate from the UPPER board edge
    (OEM relay/woofer end) to the lower edge (transformer end); y from the free edge
    to the backplate edge. Orientation confirmed by the owner (2026-10-10).
    """
    m = json.loads((ROOT / "mechanical/oem-heatsink-measurements.json").read_text())
    pcb, u = m["main_pcb"], m["u_profile"]
    x0, y0 = 20.0, 20.0
    w, h = pcb["length_mm"], pcb["depth_mm"]
    back = y0 + h  # backplate edge
    edge = pcb["mounting_holes"]["from_edge_mm"]
    holes = [(x, back - d) for x in (x0 + edge, x0 + w - edge)
             for d in pcb["mounting_holes"]["from_backplate_mm"]]
    top_gap = pcb["profile_gaps_mm"]["top"]
    keepout = (x0 + top_gap, back - u["outer_width"], x0 + top_gap + u["length"], back)
    to3p = [(x0 + top_gap + d, back - u["outer_width"]) for d in
            (u["to3p_holes"]["from_profile_ends_mm"], u["length"] - u["to3p_holes"]["from_profile_ends_mm"])]
    # D-031: two plated M3 holes at the pinless ends of U1 (90.5, 60.5) clamp the thermal
    # block onto the PowerPAD from below, as on the TI EVM; block is GND (SLASEA8A pin table).
    block_holes = [(79.0, 60.5), (102.0, 60.5)]
    return {"outline": (x0, y0, x0 + w, back), "holes": holes, "profile_keepout": keepout,
            "to3p_holes_at_leg_face": to3p, "hole_thread": pcb["mounting_holes"]["thread"],
            "block_holes": block_holes}


BODY_MODELS = {"U1": "HTSSOP-44_TopEP_DDV.wrl", "J301": "JST_VH_B3P-VH.wrl",
               "J1": "WE_WR-TBL_691137710002.wrl", "J5": "JST_VH_B2P-VH.wrl"}


def set_body_model(fp, pcbnew, name):
    """Replace a missing/absent model with a datasheet envelope (scripts/make_body_models.py)."""
    fp.Models().clear()
    model = pcbnew.FP_3DMODEL()
    model.m_Filename = "${KIPRJMOD}/../models/ps28-bodies/" + name
    fp.Models().push_back(model)


def apply_oem_mechanics(pcb, pcbnew):
    """Replace the inferred 153 x 79.1 study outline and reservations with measured data."""
    mech = oem_mechanics()
    # Delete (not Remove): Remove leaves orphaned C++ items that corrupt later SWIG calls.
    for zone in [pcb.GetArea(i) for i in range(pcb.GetAreaCount())]:
        if zone.GetIsRuleArea():
            pcb.Delete(zone)
    for obj in list(pcb.GetDrawings()):
        pcb.Delete(obj)

    def point(x, y):
        return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))

    def rect(box, layer, width=0.05):
        x1, y1, x2, y2 = box
        corners = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        for a, b in zip(corners, corners[1:] + corners[:1]):
            seg = pcbnew.PCB_SHAPE(pcb)
            seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
            seg.SetStart(point(*a))
            seg.SetEnd(point(*b))
            seg.SetLayer(layer)
            seg.SetWidth(pcbnew.FromMM(width))
            pcb.Add(seg)

    def note(text, x, y):
        t = pcbnew.PCB_TEXT(pcb)
        t.SetText(text)
        t.SetPosition(point(x, y))
        t.SetLayer(pcbnew.Dwgs_User)
        t.SetTextSize(point(1, 1))
        t.SetTextThickness(pcbnew.FromMM(0.15))
        pcb.Add(t)

    rect(mech["outline"], pcbnew.Edge_Cuts)
    # Aluminium U-profile base rests on the component side: no parts/pads/copper on top.
    x1, y1, x2, y2 = mech["profile_keepout"]
    zone = pcbnew.ZONE(pcb)
    zone.SetLayer(pcbnew.F_Cu)
    zone.SetIsRuleArea(True)
    zone.SetZoneName("OEM_U_PROFILE")
    zone.SetDoNotAllowFootprints(True)
    zone.SetDoNotAllowPads(True)
    zone.SetDoNotAllowTracks(True)
    zone.SetDoNotAllowVias(True)
    zone.SetDoNotAllowZoneFills(True)
    poly = pcbnew.SHAPE_POLY_SET()
    poly.NewOutline()
    for x, y in [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]:
        poly.Append(point(x, y))
    zone.SetOutline(poly)
    poly.thisown = False  # ZONE takes ownership of the polygon.
    pcb.Add(zone)
    rect(mech["profile_keepout"], pcbnew.Dwgs_User, 0.15)
    note("OEM U PROFILE 65x33 - BASE ON PCB - NO TOP PARTS", (x1 + x2) / 2, y1 - 2)
    for x, y in mech["to3p_holes_at_leg_face"]:
        note("TO-3P M3 (LEG FACE)", x, y - 5)
    library = "/usr/share/kicad/footprints/MountingHole.pretty"
    for i, (x, y) in enumerate(mech["holes"], 1):
        hole = pcbnew.FootprintLoad(library, "MountingHole_3.2mm_M3")
        hole.SetReference(f"H{i}")
        hole.SetValue("OEM L-bracket M3")
        hole.SetFPID(pcbnew.LIB_ID("MountingHole", "MountingHole_3.2mm_M3"))
        hole.SetPosition(point(x, y))
        hole.SetBoardOnly(True)
        hole.SetExcludedFromBOM(True)
        hole.SetExcludedFromPosFiles(True)
        set_body_model(hole, pcbnew, "M3_pan_head.wrl")
        pcb.Add(hole)
    for i, (x, y) in enumerate(mech["block_holes"], len(mech["holes"]) + 1):
        hole = pcbnew.FootprintLoad(library, "MountingHole_3.2mm_M3_Pad_Via")
        hole.SetReference(f"H{i}")
        hole.SetValue("Thermal block clamp M3 (GND)")
        hole.SetFPID(pcbnew.LIB_ID("MountingHole", "MountingHole_3.2mm_M3_Pad_Via"))
        hole.SetPosition(point(x, y))
        hole.SetBoardOnly(True)
        hole.SetExcludedFromBOM(True)
        hole.SetExcludedFromPosFiles(True)
        gnd = pcb.FindNet("/GND")
        for pad in hole.Pads():
            pad.SetNet(gnd)
        if i == len(mech["holes"]) + 1:  # block model origin = H5 (scripts/blender_thermal_block.py)
            set_body_model(hole, pcbnew, "thermal_block.wrl")
        pcb.Add(hole)
    rect((64.0, 52.0, 117.0, 68.0), pcbnew.Dwgs_User, 0.15)
    note("THERMAL BLOCK (mechanical/thermal-block.md)", 90.5, 51)
    note("MEASURED OEM 154x81 (TAPE, ~1 mm) - NOT FABRICATION", 97, 16)
    return mech


def board(staged, parts, inventory):
    import pcbnew

    pcb = pcbnew.LoadBoard(str(SOURCE / "ps28-modern.kicad_pcb"))
    apply_oem_mechanics(pcb, pcbnew)
    for net in list(pcb.GetNetsByName().values()):
        name = net.GetNetname().lstrip("/")
        if name in RENAMES:
            net.SetNetname("/" + RENAMES[name])
    nets = dict(pcb.GetNetsByName())
    for ref, (nick, name, value, _) in SWAPS.items():
        old = pcb.FindFootprintByReference(ref)
        fp = pcbnew.FootprintLoad(f"/usr/share/kicad/footprints/{nick}.pretty", name)
        fp.SetReference(ref)
        fp.SetValue(value)
        fp.SetFPID(pcbnew.LIB_ID(nick, name))
        for pad in fp.Pads():
            pad.SetNet(next(x for x in old.Pads() if x.GetNumber() == pad.GetNumber()).GetNet())
        fp.SetPosition(old.GetPosition())
        pcb.Remove(old)
        pcb.Add(fp)
    counters = {}
    for fp in pcb.GetFootprints():
        if fp.GetReference() in DNP and any(p.get("group") for p in parts):
            fp.SetDNP(True)
    if any(p.get("group") == "iso" for p in parts):
        for (ref, number), name in PLATES.items():
            if "/" + name not in nets:
                nets["/" + name] = pcbnew.NETINFO_ITEM(pcb, "/" + name)
                pcb.Add(nets["/" + name])
            pad = next(x for x in pcb.FindFootprintByReference(ref).Pads() if x.GetNumber() == number)
            pad.SetNet(nets["/" + name])
    for p in parts:
        for plain_name in filter(None, p["nets"].values()):
            name = "/" + plain_name
            if name not in nets:
                n = pcbnew.NETINFO_ITEM(pcb, name)
                pcb.Add(n)
                nets[name] = n
        nick, name = p["footprint"].split(":")
        directory = (
            staged
            / (
                "libraries/PS28.pretty"
                if nick == "PS28"
                else "libraries/PS28_ANALOG.pretty"
            )
            if nick in ("PS28", "PS28_ANALOG")
            else Path("/usr/share/kicad/footprints") / (nick + ".pretty")
        )
        fp = pcbnew.FootprintLoad(str(directory), name)
        if fp is None:
            raise ValueError("Missing candidate footprint: " + p["footprint"])
        fp.SetReference(p["ref"])
        fp.SetValue(p["value"])
        fp.SetFPID(pcbnew.LIB_ID(nick, name))
        # Import bank OUTSIDE OEM outline: intentionally unplaced, never claim fit.
        group = p.get("group", "analog")
        i = counters[group] = counters.get(group, -1) + 1
        x, y = bank_position(p, i)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        for pad in fp.Pads():
            number = pad.GetNumber()
            if number and p["nets"].get(number):
                plain = p["nets"][number]
                pad.SetNet(nets["/" + plain])
        pcb.Add(fp)
    result = subprocess.run(
        [
            "kicad-cli",
            "sch",
            "export",
            "netlist",
            "--format",
            "kicadxml",
            "--output",
            str(staged / "candidate.xml"),
            str(staged / (PROJECT + ".kicad_sch")),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise ValueError(result.stderr)
    components = {
        c.get("ref"): c
        for c in ET.parse(staged / "candidate.xml").findall(".//components/comp")
    }
    native_nets = {
        (node.get("ref"), node.get("pin")): net.get("name")
        for net in ET.parse(staged / "candidate.xml").findall(".//nets/net")
        for node in net.findall("node")
    }
    by_ref = {p["ref"]: p for p in parts}
    for fp in pcb.GetFootprints():
        p = by_ref.get(fp.GetReference())
        for pad in fp.Pads() if p else ():
            number = pad.GetNumber()
            if number in p["nets"] and p["nets"][number] is None:
                name = native_nets[(p["ref"], number)]
                if name not in nets:
                    nets[name] = pcbnew.NETINFO_ITEM(pcb, name)
                    pcb.Add(nets[name])
                pad.SetNet(nets[name])
    sch = parse((staged / (PROJECT + ".kicad_sch")).read_text())
    for fp in pcb.GetFootprints():
        ref = fp.GetReference()
        if fp.IsBoardOnly():
            continue
        unit = next(
            n
            for n in sch
            if isinstance(n, list)
            and n[0] == "symbol"
            and child(n, "unit")[1] == "1"
            and any(
                isinstance(p, list) and p[:3] == ["property", q("Reference"), q(ref)]
                for p in n
            )
        )
        ids = [child(sch, "uuid")[1].strip('"'), child(unit, "uuid")[1].strip('"')]
        exported = components[ref].findtext("tstamps").split()
        if ids[1] not in exported:
            raise ValueError("Invalid multiunit identity: " + ref)
        path = pcbnew.KIID_PATH()
        for part in ids:
            uuid.UUID(
                part
            )  # reject invalid IDs instead of C++ creating new random ones
            path.push_back(pcbnew.KIID(part))
        fp.SetPath(path)
        if ref == "R9":
            fp.SetValue("4.7k 1%")
        for field in components[ref].findall("property"):
            fp.SetField(field.get("name"), field.get("value") or "")
            fp.GetField(field.get("name")).SetVisible(False)
    from place_system_candidate import place

    place(pcb, pcbnew, oem_mechanics(), inventory)
    for fp in pcb.GetFootprints():
        if fp.GetReference().startswith("TP"):
            fp.SetExcludedFromBOM(False)  # follow the symbol (stock TestPoint footprint is BOM-excluded)
        if fp.GetReference().startswith("TP1") or fp.GetFPID().GetLibItemName().wx_str().startswith("LED_"):
            # PCB-004: probe/LED name readable on the board (value = net label).
            fp.Value().SetLayer(pcbnew.B_SilkS if fp.IsFlipped() else pcbnew.F_SilkS)
            fp.Value().SetVisible(True)
            fp.Value().SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8)))
            fp.Value().SetTextThickness(pcbnew.FromMM(0.12))
        # Dense board: reference designators go to the assembly (Fab) layer, not silkscreen.
        fp.Reference().SetLayer(pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab)
    for fp in pcb.GetFootprints():
        if fp.GetReference() in BODY_MODELS:
            set_body_model(fp, pcbnew, BODY_MODELS[fp.GetReference()])
    pcbnew.SaveBoard(str(staged / (PROJECT + ".kicad_pcb")), pcb)
    # Add manufacturer models without replacing audited pads or assigning HCF tab.
    tree = parse((staged / (PROJECT + ".kicad_pcb")).read_text())
    for fp in tree:
        if not isinstance(fp, list) or fp[0] != "footprint":
            continue
        ref = next(
            x[2].strip('"')
            for x in fp
            if isinstance(x, list) and x[0] == "property" and x[1] == q("Reference")
        )
        model = (
            ("CP_Wurth_WCAP-ATG5-P5D10L16.step", 0)
            if ref in ("C1", "C201", "C202")
            else ("L_Wurth_WE-HCF-2013.step", 90)
            if ref in ("L1", "L2")
            else None
        )
        if model:
            fp[:] = [x for x in fp if not isinstance(x, list) or x[0] != "model"]
            fp.append(
                [
                    "model",
                    q("${KIPRJMOD}/../models/vendor-wurth/" + model[0]),
                    ["offset", ["xyz", "0", "0", "0"]],
                    ["scale", ["xyz", "1", "1", "1"]],
                    ["rotate", ["xyz", "0", "0", str(model[1])]],
                ]
            )
    (staged / (PROJECT + ".kicad_pcb")).write_text(render(tree) + "\n")


def validate_staged(staged, inventory):
    xml = ET.parse(staged / "candidate.xml")
    native = {
        (node.get("ref"), node.get("pin")): net.get("name")
        for net in xml.findall(".//nets/net")
        for node in net.findall("node")
    }
    pcb = parse((staged / (PROJECT + ".kicad_pcb")).read_text())
    seen = set()
    checked = set()
    pads = 0
    for fp in pcb:
        if not isinstance(fp, list) or fp[0] != "footprint":
            continue
        ref = next(
            p[2].strip('"')
            for p in fp
            if isinstance(p, list) and p[:2] == ["property", q("Reference")]
        )
        if ref.startswith("H") and ref[1:].isdigit():
            continue  # board-only OEM mounting holes, not in the schematic
        if ref in seen:
            raise ValueError("Duplicate footprint " + ref)
        seen.add(ref)
        for pad in fp:
            if not isinstance(pad, list) or pad[0] != "pad":
                continue
            key = (ref, pad[1].strip('"'))
            if key not in native:
                continue
            actual = child(pad, "net")[-1].strip('"')
            if actual != native[key]:
                raise ValueError(f"Native pad-net mismatch {key}: {actual} != {native[key]}")
            pads += 1
            checked.add(key)
    if seen != {p["ref"] for p in inventory} or checked != set(native):
        raise ValueError(
            f"Incomplete staged import: refs {seen ^ {p['ref'] for p in inventory}}, pads {pads}/{len(native)} "
            f"{sorted(set(native) - checked)[:12]}"
        )
    if native["U2", "8"] != "/ANALOG_12V" or native["U3", "8"] != "/ANALOG_12V":
        raise ValueError("OPA rail changed")
    refs = {r for r, _ in native}
    bridged = native["U3", "1"] == native["C20", "1"] or native["U3", "7"] == native["C21", "1"]
    if bridged and "K501" not in refs:
        raise ValueError("Signal bridge without D-019 isolation relay")
    if "K501" in refs:
        # Drivers -> C20/C21 -> relay COM; NO -> TPA pins; NC -> discharge. Never plate-to-pin.
        joins = [(("U3", "1"), ("C20", "1")), (("U3", "7"), ("C21", "1")),
                 (("C20", "2"), ("K501", "3")), (("C21", "2"), ("K501", "6")),
                 (("R517", "2"), ("U1", "5")), (("R518", "2"), ("U1", "6")),
                 (("K501", "4"), ("R517", "1")), (("K501", "5"), ("R518", "1")),
                 (("D503", "3"), ("U1", "5")), (("D504", "3"), ("U1", "6")),
                 (("U503", "1"), ("R101", "2")), (("U503", "2"), ("U3", "5"))]
        for a, b in joins:
            if native[a] != native[b]:
                raise ValueError(f"D-019 join missing {a}-{b}")
        if native["C20", "2"] == native["U1", "5"] or native["C21", "2"] == native["U1", "6"]:
            raise ValueError("Coupling plate bypasses the isolation relay")
    if {"U302", "U303", "U401"} <= refs:
        # D-021/D-020 joins: rectifier feeds core PVDD, buck feeds AUX_RAW, seq drives RESET.
        joins = [(("D301", "1"), ("U1", "36")), (("L301", "2"), ("C1", "1")),
                 (("R408", "2"), ("U1", "18")), (("U407", "1"), ("U1", "19")),
                 (("U406", "2"), ("U1", "21"))]
        for a, b in joins:
            if native[a] != native[b]:
                raise ValueError(f"Integration join missing {a}-{b}")
        if native["D301", "2"] == native["D302", "2"]:
            raise ValueError("T1 ends bridged")
    return {
        "native_pad_net_matches": len(checked),
        "copper_pads_checked": pads,
        "footprints": len(seen),
        "signal_bridge_open": "K501" not in refs,
        "signal_bridge_via_relay_only": "K501" in refs,
    }


def publish_noreplace(staged, out):
    if os.name == "nt":
        os.rename(staged, out)  # Windows rejects existing directory atomically
        return
    library = ctypes.CDLL(None, use_errno=True)
    rename = getattr(library, "renameat2", None)
    if rename is None:
        raise NotImplementedError("Safe no-replace publication unavailable on this OS")
    rename.argtypes = [
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    ]
    rename.restype = ctypes.c_int
    if rename(-100, os.fsencode(staged), -100, os.fsencode(out), 1) != 0:
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code), str(out))


def generate(out):
    if os.path.lexists(out):
        raise FileExistsError("Refusing to overwrite integration candidate")
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".system-stage-", dir=out.parent))
    try:
        parts = candidates()
        added = system_parts()
        core = copy.deepcopy(
            json.loads((SOURCE / "core-manifest.json").read_text())["parts"]
        )
        for p in core:
            p["nets"] = {k: PLATES.get((p["ref"], k), RENAMES.get(v, v)) for k, v in p["nets"].items()}
            if p["ref"] == "R9":
                p.update(value="4.7k 1%", mpn="CRCW06034K70FKEA")
            if p["ref"] in DNP:
                p["dnp"] = True
            if p["ref"] in SWAPS:
                nick, name, value, mpn = SWAPS[p["ref"]]
                p.update(value=value, mpn=mpn, footprint=f"{nick}:{name}")
                p["source"] = SWAP_SOURCES[p["ref"]]
                p["manufacturer"] = "JST" if p["ref"] == "J5" else "Nichicon"
        inventory = core + parts + added
        tree = parse(schematic(parts, added))
        for ref, (nick, name, value, mpn) in SWAPS.items():
            symbol = next(n for n in tree if isinstance(n, list) and n[0] == "symbol" and any(
                isinstance(x, list) and x[:3] == ["property", q("Reference"), q(ref)] for x in n))
            set_property(symbol, "Footprint", f"{nick}:{name}")
            set_property(symbol, "Value", value)
            set_property(symbol, "MPN", mpn)
            set_property(symbol, "Manufacturer", "JST" if ref == "J5" else "Nichicon")
            set_property(symbol, "Source", SWAP_SOURCES[ref])
        (stage / (PROJECT + ".kicad_sch")).write_text(render(tree) + "\n")
        shutil.copytree(SOURCE / "libraries", stage / "libraries")
        for nickname, symbols in (("PS28_POWER", [tps3700_symbol()]), ("PS28_SEQ", [lp2985_symbol()]),
                                  ("PS28_ISO", iso_symbols()),
                                  ("PS28_PRE", list(pre_symbols().values()) + list(debug_symbols().values()))):
            libs = []
            for symbol in symbols:
                library = list(symbol)
                library[1] = q(symbol[1].strip('"').split(":")[-1])
                libs.append(render(library))
            (stage / f"libraries/{nickname}.kicad_sym").write_text(
                '(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '
                + " ".join(libs) + ")\n"
            )
        for filename, model_name, rotation in [
            ("WE_860020575014.kicad_mod", "CP_Wurth_WCAP-ATG5-P5D10L16.step", 0),
            ("WE_HCF2013_7443631000.kicad_mod", "L_Wurth_WE-HCF-2013.step", 90),
        ]:
            target = stage / "libraries/PS28.pretty" / filename
            tree = parse(target.read_text())
            tree[:] = [n for n in tree if not isinstance(n, list) or n[0] != "model"]
            tree.append(
                [
                    "model",
                    q("${KIPRJMOD}/../models/vendor-wurth/" + model_name),
                    ["offset", ["xyz", "0", "0", "0"]],
                    ["scale", ["xyz", "1", "1", "1"]],
                    ["rotate", ["xyz", "0", "0", str(rotation)]],
                ]
            )
            target.write_text(render(tree) + "\n")
        extra = stage / "libraries/PS28_ANALOG.pretty"
        extra.mkdir()
        (extra / "TNPW1206_IPC_Reflow.kicad_mod").write_text(tnpw_footprint())
        (extra / "TI_DGK0008A.kicad_mod").write_text(dgk_footprint())
        shutil.copy(
            ROOT / "kicad/analog-protected/libraries/PS28_ANALOG.kicad_sym",
            stage / "libraries",
        )
        (stage / "sym-lib-table").write_text(
            '(sym_lib_table(version 7)(lib(name "PS28")(type "KiCad")(uri "${KIPRJMOD}/libraries/PS28.kicad_sym")(options "")(descr "Existing core"))(lib(name "PS28_ANALOG")(type "KiCad")(uri "${KIPRJMOD}/libraries/PS28_ANALOG.kicad_sym")(options "")(descr "Existing flattened OPA"))(lib(name "PS28_POWER")(type "KiCad")(uri "${KIPRJMOD}/libraries/PS28_POWER.kicad_sym")(options "")(descr "TI TPS3700 SBVS187G p.4"))(lib(name "PS28_SEQ")(type "KiCad")(uri "${KIPRJMOD}/libraries/PS28_SEQ.kicad_sym")(options "")(descr "TI LP2985 SLVS522S Table 4-1"))(lib(name "PS28_ISO")(type "KiCad")(uri "${KIPRJMOD}/libraries/PS28_ISO.kicad_sym")(options "")(descr "TI SCDS420E, Diodes DS30036"))(lib(name "PS28_PRE")(type "KiCad")(uri "${KIPRJMOD}/libraries/PS28_PRE.kicad_sym")(options "")(descr "onsemi BCP56/BCP53/BSS138")))\n'
        )
        (stage / "fp-lib-table").write_text(
            '(fp_lib_table(version 7)(lib(name "PS28")(type "KiCad")(uri "${KIPRJMOD}/libraries/PS28.pretty")(options "")(descr "Existing audited core lands"))(lib(name "PS28_ANALOG")(type "KiCad")(uri "${KIPRJMOD}/libraries/PS28_ANALOG.pretty")(options "")(descr "Candidate passives")))\n'
        )
        # Keep all original project-local stock library registrations; no global edits.
        for table, kinds in [("sym-lib-table", "sym"), ("fp-lib-table", "fp")]:
            tree = parse((SOURCE / table).read_text())
            rows = {
                child(n, "name")[1].strip('"')
                for n in tree
                if isinstance(n, list) and n[0] == "lib"
            }
            additions = parse((stage / table).read_text())
            tree.extend(
                n
                for n in additions
                if isinstance(n, list)
                and n[0] == "lib"
                and child(n, "name")[1].strip('"') not in rows
            )
            if kinds == "fp":
                for nick in sorted(
                    {p["footprint"].split(":")[0] for p in inventory}
                    - rows
                    - {"PS28_ANALOG"}
                ):
                    tree.append(
                        [
                            "lib",
                            ["name", q(nick)],
                            ["type", q("KiCad")],
                            [
                                "uri",
                                q("/usr/share/kicad/footprints/" + nick + ".pretty"),
                            ],
                            ["options", q("")],
                            ["descr", q("Installed stock; candidate")],
                        ]
                    )
            (stage / table).write_text(render(tree) + "\n")
        project = json.loads((SOURCE / "ps28-modern.kicad_pro").read_text())
        project["meta"]["filename"] = PROJECT + ".kicad_pro"
        # top_level_sheets is copied from the source project; retarget it to the
        # candidate schematic or the generated .kicad_pro points at ps28-modern.
        for sheet in project.get("schematic", {}).get("top_level_sheets", []):
            sheet["filename"] = PROJECT + ".kicad_sch"
            sheet["name"] = PROJECT
        (stage / (PROJECT + ".kicad_pro")).write_text(
            json.dumps(project, indent=2) + "\n"
        )
        board(stage, parts + added, inventory)
        validation = validate_staged(stage, inventory)
        manifest = {
            "staged_validation": validation,
            "parts": inventory,
            "source_sha256": {
                str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in [
                    SOURCE / "ps28-modern.kicad_sch",
                    ROOT / "kicad/analog-protected/analog-protected.kicad_sch",
                    ROOT / "scripts/integrate_candidate.py",
                    ROOT / "kicad/power-d021/power-d021.kicad_sch",
                    ROOT / "kicad/seq-d020/seq-d020.kicad_sch",
                    ROOT / "scripts/create_power_d021.py",
                    ROOT / "scripts/create_seq_d020.py",
                ]
            },
            "status": "CORE + D018 + D021 POWER + D020 SEQ SUBSET IMPORT BANKS; SIGNAL SAFETY BRIDGE OPEN",
            "power_d021_integrated": True,
            "seq_d020_subset_integrated": True,
            "dnp": sorted(DNP),
            "logical_interfaces_removed": sorted(LOGICAL),
            "physical_interfaces_removed": ["J101", "J102", "J103"],
            "signal_bridge_connected": True,  # only through K501 (D-024)
            "isolation_mute_supervisor_implemented": True,  # captured study, not validated
            "rails_fault_supervisor_implemented": True,
            "analog_placement_inside_oem": False,
            "unassigned_footprints": [
                p["ref"] for p in inventory if not p.get("footprint")
            ],
            "hardware_validated": False,
            "manufacturing_approved": False,
        }
        (stage / "system-manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n"
        )
        publish_noreplace(stage, out)
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "kicad/system-candidate")
    generate(parser.parse_args().output)
