#!/usr/bin/env python3
"""Nominal/tolerance CAD and lumped thermal budget, NOT a measured or FEM result."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "mechanical/thermal-fit.json"
PCB = ROOT / "kicad/system-candidate/system-candidate.kicad_pcb"


def resistance_mm(length_mm, conductivity, area_mm2):
    if min(length_mm, conductivity, area_mm2) <= 0:
        raise ValueError("Positive thickness, conductivity and contact area required")
    return length_mm * 1e-3 / (conductivity * area_mm2 * 1e-6)


def budget(config):
    p, t, i = config["pedestal"], config["thermal"], config["interface"]
    a = i["top_tim_contact_area_mm2"]
    pedestal = resistance_mm(p["step_from_body_bottom_mm"], i["al_conductivity_assumed_W_mK"], a)
    top = [resistance_mm(d, i["tim_conductivity_min_assumed_W_mK"], a) for d in i["top_tim_gap_range_mm"]]
    side = i["side_tim_layers"] * resistance_mm(i["side_tim_each_mm"], i["tim_conductivity_min_assumed_W_mK"], i["side_effective_area_assumed_mm2"])
    side += resistance_mm(i["side_shim_nominal_mm"], i["al_conductivity_assumed_W_mK"], i["side_effective_area_assumed_mm2"])
    local = [t["rjc_top_K_W"] + pedestal + top[k] + side + i["body_spreading_resistance_assumed_K_W"][k] for k in (0, 1)]
    cases = []
    limits = []
    for ambient in t["ambient_scenarios_C"]:
        for loss in t["loss_scenarios_W"]:
            limits.append({"ambient_C": ambient, "loss_W": loss,
                           "profile_max_C_for_design_target": t["design_target_assumed_C"] - loss * local[1],
                           "legacy_path_max_K_W_for_design_target": (t["design_target_assumed_C"] - ambient) / loss - local[1]})
            for legacy in t["legacy_path_to_ambient_scenarios_K_W"]:
                junction = [ambient + loss * (r + legacy) for r in local]
                cases.append({"ambient_C": ambient, "loss_W": loss, "legacy_path_K_W": legacy,
                              "junction_range_C": junction,
                              "worst_meets_design_target": junction[1] <= t["design_target_assumed_C"],
                              "worst_within_recommended_range": junction[1] <= t["junction_recommended_max_C"]})
    return {"method": "1D lumped steady-state sensitivity; NOT FEM; full loss scenario allocated to U1 conservatively",
            "rjc_top_K_W": t["rjc_top_K_W"], "r_pedestal_K_W": pedestal,
            "r_top_tim_range_K_W": top, "r_side_interfaces_and_shim_K_W": side,
            "r_junction_to_profile_range_K_W": local, "cases": cases, "required_limits": limits,
            "legacy_path_measured": False, "thermal_performance_validated": False}


def circle_rect_distance(center, rect):
    x, y = center
    x0, y0, x1, y1 = rect
    return math.hypot(max(x0 - x, 0, x - x1), max(y0 - y, 0, y - y1))


def inspect(config, pcb_path=PCB):
    import pcbnew
    pcb = pcbnew.LoadBoard(str(pcb_path))
    mm = pcbnew.ToMM
    xy = lambda f: [mm(f.GetPosition().x), mm(f.GetPosition().y)]
    device = pcb.FindFootprintByReference("U1")
    assert xy(device) == config["pedestal"]["center_xy_mm"], "U1 moved; update fit before changing model"
    assert device.GetOrientationDegrees() == 90 and not device.IsFlipped()
    assert [xy(pcb.FindFootprintByReference(r)) for r in ("H5", "H6")] == config["clamp_holes_xy_mm"]
    assert math.isclose(mm(pcb.GetDesignSettings().GetBoardThickness()), config["stops"]["pcb_thickness_mm"])
    owner = json.loads((ROOT / "mechanical/oem-heatsink-measurements.json").read_text())
    holes = owner["u_profile"]["to3p_holes"]
    x0 = 20 + owner["main_pcb"]["profile_gaps_mm"]["top"]
    expected = [x0 + holes["from_profile_ends_mm"], x0 + owner["u_profile"]["length"] - holes["from_profile_ends_mm"]]
    assert config["side_holes"]["x_mm"] == expected
    assert config["side_holes"]["z_mm"] == holes["height_above_pcb_mm"]
    assert config['stops']['oem_pcb_thickness_mm'] == owner['main_pcb']['thickness_mm']
    assert config['side_holes']['combined_alignment_budget_xz_mm'][1] >= 1.0 + abs(config['stops']['pcb_thickness_mm']-config['stops']['oem_pcb_thickness_mm']) + .2 - 1e-9
    error = config["device"]["relative_xy_error_budget_mm"]
    pad = config["device"]["exposed_pad_min_xy_world_mm"]
    foot = config["pedestal"]["size_xy_mm"]
    margins = [(a-b)/2-error for a,b in zip(pad,foot)]
    assert min(margins) > 0, "Pedestal can reach epoxy/overhang at tolerance corner"
    side = config["side_holes"]
    dx, dz = side["combined_alignment_budget_xz_mm"]
    radius = (side["slot_width_mm"] - 3.0)/2
    straight_half = (side["slot_total_height_mm"]-side["slot_width_mm"])/2
    slot_margin = radius - math.hypot(dx, max(0, dz-straight_half))
    assert slot_margin >= .20, 'Insufficient residual slot/machining margin'
    stop_min = config["stops"]["selection_range_mm"][0] - config["stops"]["stop_plane_tolerance_mm"]
    body = config["body_mm"]
    low_parts, hardware = [], []
    for f in pcb.GetFootprints():
        ref = f.GetReference()
        if ref in ("U1", "H5", "H6"):
            continue
        layer = pcbnew.B_CrtYd if f.IsFlipped() else pcbnew.F_CrtYd
        bb = f.GetCourtyard(layer).BBox()
        rect = [mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())]
        for hole in config["clamp_holes_xy_mm"]:
            diameter = config["stops"]["bottom_head_diameter_max_mm"] if f.IsFlipped() else config["stops"]["outer_diameter_max_mm"]
            clearance = circle_rect_distance(hole, rect) - diameter/2
            if clearance < 1.5:
                hardware.append({"reference": ref, "side": "bottom" if f.IsFlipped() else "top",
                                 "clearance_mm": clearance, "clearance_after_xy_budget_mm": clearance-error, "head_or_stop_xy_mm": hole})
                assert clearance-error >= .15, f"Clamp head/stop collides with {ref} at budget"
        overlap = (rect[2] > body["x"][0] and rect[0] < body["x"][1] and rect[3] > body["y"][0] and rect[1] < body["y"][1])
        if f.IsFlipped() or not overlap:
            continue
        envelope = config["height_envelopes"]["D303_catalog_max_mm"] if ref == "D303" else config["height_envelopes"]["generic_low_smd_max_mm"]
        height = envelope + config["height_envelopes"]["solder_allowance_mm"]
        clearance = stop_min - height
        assert clearance >= config["height_envelopes"]["minimum_body_clearance_mm"], ref
        low_parts.append({"reference": ref, "value": f.GetValue(), "footprint": f.GetFPID().GetLibItemName().wx_str(),
                          "courtyard_xy_mm": rect, "height_envelope_mm": height, "worst_body_clearance_mm": clearance,
                          "height_source": "Littelfuse SMCJ D(max) + assumed solder" if ref == "D303" else "design envelope, NOT individually qualified MPN height"})
    external = []
    for f in pcb.GetFootprints():
        if f.IsFlipped() or f.GetReference() in ('U1','H5','H6'):
            continue
        ref=f.GetReference();bb=f.GetCourtyard(pcbnew.F_CrtYd).BBox()
        rect=[mm(bb.GetLeft()),mm(bb.GetTop()),mm(bb.GetRight()),mm(bb.GetBottom())]
        h=config['height_envelopes']['L1_L2_catalog_max_mm'] if ref in ('L1','L2') else config['height_envelopes']['D303_catalog_max_mm'] if ref=='D303' else config['height_envelopes']['generic_low_smd_max_mm']
        h+=config['height_envelopes']['solder_allowance_mm']
        for x in side['x_mm']:
            for label,half_width,ya,yb,lowest in [('load_spreader',6,53,54,side['z_mm']-side['spreader_hole_from_bottom_mm']),('screw_head',2.75,50,53,side['z_mm']-2.75)]:
                # Apply the explicitly allowed OEM/slot X/Z displacement.
                projected=[x-half_width-dx,ya,x+half_width+dx,yb]
                if rect[2]>projected[0] and rect[0]<projected[2] and rect[3]>projected[1] and rect[1]<projected[3]:
                    fpname=f.GetFPID().GetLibItemName().wx_str()
                    if ref not in ('L1','L2','D303') and not fpname.startswith(('C_','R_','D_','LED_')):
                        raise ValueError('Qualify external hardware height envelope: '+ref)
                    gap=lowest-dz-h
                    assert gap>=.2, 'External side fastener hits '+ref
                    external.append({'reference':ref,'hardware':label,'courtyard_xy_mm':rect,'height_envelope_mm':h,'worst_vertical_clearance_mm':gap})
    step = config["pedestal"]["step_from_body_bottom_mm"]
    package = config["device"]["height_range_mm"]
    assembly = config["device"]["assembly_height_allowance_mm"]
    tim = config["interface"]["top_tim_gap_range_mm"]
    needed = [package[0]+tim[0]+step, package[1]+assembly+tim[1]+step]
    selected = config["stops"]["selection_range_mm"]
    assert needed[0] >= selected[0]-1e-9 and needed[1] <= selected[1]+1e-9
    return {"nominal_fit_pass": True, "physical_fit_validated": False, "pedestal_min_pad_margin_after_xy_budget_mm": margins,
            "slot_combined_error_margin_mm": slot_margin, "required_stop_selection_mm": needed,
            "upper_assembly_envelope_with_budgets_mm": max(body['z'][1]+selected[1]-config['stops']['nominal_mm'], side['z_mm']+dz+side['external_load_spreader_mm'][1]-side['spreader_hole_from_bottom_mm']),
            "required_housing_clearance_mm": 32.0,
            "under_body_parts": low_parts, "clamp_hardware_clearances": hardware,
            "external_side_hardware_clearances": external,
            "old_side_hole_height_error_mm": holes["height_above_pcb_mm"] - 6.35,
            "local_clearances_to_confirm": ["housing >=32 mm above PCB at the block; not inferred from capacitor photos",
                                            "bottom screw heads >=5 mm clearance around H5/H6",
                                            "actual top TIM gap and lateral shim; useful OEM M3 thread depth"]}


def mesh_geometry(model_path, anchor_xy):
    """Read THIS single-shape VRML artifact; no generic VRML parser assumption."""
    text = Path(model_path).read_text()
    point = re.search(r'point\s*\[([^]]*)\]', text, re.S).group(1)
    numbers = [float(v) for v in re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?', point)]
    vertices = [(numbers[k]*2.54+anchor_xy[0], -numbers[k+1]*2.54+anchor_xy[1], numbers[k+2]*2.54) for k in range(0,len(numbers),3)]
    indices = [int(v) for v in re.findall(r'-?\d+', re.search(r'coordIndex\s*\[([^]]*)\]', text, re.S).group(1))]
    triangles, face = [], []
    for i in indices:
        if i == -1:
            if len(face) != 3:
                raise ValueError('Expected triangulated main block only')
            triangles.append(tuple(face));face=[]
        else:face.append(i)
    return vertices, triangles


def mesh_ray_hits(vertices, triangles, origin, direction):
    """Moller-Trumbore, forward ray; enough for explicit mesh regression probes."""
    sub=lambda a,b:tuple(x-y for x,y in zip(a,b))
    cross=lambda a,b:(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
    dot=lambda a,b:sum(x*y for x,y in zip(a,b))
    hits=[]
    for ia,ib,ic in triangles:
        a,b,c=vertices[ia],vertices[ib],vertices[ic]
        e1,e2=sub(b,a),sub(c,a);p=cross(direction,e2);det=dot(e1,p)
        if abs(det)<1e-9:continue
        t=sub(origin,a);u=dot(t,p)/det
        if not -1e-7<=u<=1+1e-7:continue
        q=cross(t,e1);v=dot(direction,q)/det
        if v < -1e-7 or u+v > 1+1e-7:continue
        distance=dot(e2,q)/det
        if distance>=0:hits.append(distance)
    return sorted(hits)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=ROOT / "tests/reports/thermal-fit-review.json")
    p.add_argument("--skip-mesh", action="store_true", help="Pre-generation only; never final mesh evidence")
    args = p.parse_args()
    c = json.loads(CONFIG.read_text())
    report = {"revision": c["revision"], "scope": "CAD/envelope + calculated thermal sensitivity, not hardware sign-off",
              "fit": inspect(c), "thermal": budget(c), "manufacturing_approved": False}
    model=ROOT/'kicad/models/ps28-bodies/thermal_block.wrl'
    if not args.skip_mesh and not model.is_file():
        raise FileNotFoundError('Generate the study model first: make thermal-model')
    if model.exists() and not args.skip_mesh:
        vertices,triangles=mesh_geometry(model,c['clamp_holes_xy_mm'][0])
        side=[bool(mesh_ray_hits(vertices,triangles,(x,40,c['side_holes']['z_mm']),(0,1,0))) for x in c['side_holes']['x_mm']]
        old=[bool(mesh_ray_hits(vertices,triangles,(x,40,6.35),(0,1,0))) for x in c['side_holes']['x_mm']]
        assert not any(side) and all(old), 'Stale/incorrect thermal-block mesh'
        report['mesh']={'bounds_world_mm':[[min(v[k] for v in vertices),max(v[k] for v in vertices)] for k in range(3)],'side_holes_blocked':side,'old_wrong_height_is_solid':old}
    sources = [CONFIG, PCB, Path(__file__), ROOT/"mechanical/oem-heatsink-measurements.json",
               ROOT/"mechanical/owner-clearance-20261012.json", ROOT/"reference/ti/tpa3255.pdf",
               ROOT/"reference/parts/littelfuse-smcj51a.pdf", ROOT/'reference/parts/we-hcf-7443631000.pdf', model,
               ROOT/'mechanical/thermal-block.stl', ROOT/'scripts/blender_thermal_block.py']
    report['mesh_checked'] = not args.skip_mesh
    report["source_sha256"] = {str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest() for f in sources if f.is_file()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n")
    print(args.output)
    print("R junction-to-profile scenario range:", report["thermal"]["r_junction_to_profile_range_K_W"])


if __name__ == "__main__":
    main()
