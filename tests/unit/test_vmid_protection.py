import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from check_analog_capture import ALIASES
from check_analog_capture import verify as verify_analog
from check_vmid_protection import filtered, verify
from create_vmid_protection import generate, integrated_parts
from simulate_vmid_protection import invariant, ripple, steady

C = json.loads((ROOT / "simulation/analog/vmid-protection.json").read_text())


class ProtectionTests(unittest.TestCase):
    def test_invariant_positive_without_unpowered_macro(self):
        p = invariant(C)
        self.assertTrue(p["pass_under_declared_envelope"])
        self.assertGreater(p["upper_boundary_inward_margin_v_per_s"], 300)
        self.assertLess(p["max_mid_excess_over_analog_terminal_v"], 0.5)
        self.assertAlmostEqual(p["raw_aux_ghost_voltage_bound_v"], 0.0525)

    def test_boundary_against_independent_nodal_vector_field(self):
        import itertools

        # Solve both terminal nodes algebraically, not the proof's inequalities.
        for h, raw, ia, load, rt, rb in itertools.product(
            [0, 0.1, 4.5, 13.2],
            [0, 3, 13.2],
            [0, 0.05],
            [-0.001, 0.001],
            [148.5, 151.5],
            [148.5, 151.5],
        ):
            m = h + 0.4
            ea = 0.5
            em = 2
            rf = 14.25
            bleed = 2178
            for conducting in [False, True]:
                a = 1 / ea + 1 / bleed + 1 / rt + (1 / rf if conducting else 0)
                d = 1 / em + 1 / rt + 1 / rb
                x = (
                    h / ea
                    - ia
                    - (0 if conducting else 0.00005)
                    + ((raw - 1.5) / rf if conducting else 0)
                )
                y = m / em - load
                va = (x * d + y / rt) / (a * d - 1 / rt**2)
                vm = (a * y + x / rt) / (a * d - 1 / rt**2)
                if conducting != (raw - 1.5 > va):
                    continue
                dm = (vm - m) / em / 2e-6
                dh = (va - h) / ea / 0.000752
                self.assertLess(dm - dh, 0)
                self.assertLess(vm - va, 0.5)

    def test_extra_storage_and_missing_hold_up_are_rejected(self):
        for key, value in [
            ("mid_capacitance_envelope_max_f", 47e-6),
            ("bulk_capacitance_min_f", 10e-6),
            ("bulk_esr_envelope_max_ohm", 5),
        ]:
            c = copy.deepcopy(C)
            c[key] = value
            self.assertFalse(invariant(c)["pass_under_declared_envelope"])

    def test_new_domain_has_headroom_and_ripple_budget(self):
        self.assertGreater(steady(C, 10.8, 0.05, 1.5, 148.5, 148.5), 8)
        self.assertLess(
            abs(ripple(C, 100, 0.000752, 14.25, 0.5, 1e-6, 2, 148.5, 151.5)) * 0.1, 0.01
        )

    def test_all_real_opamp_supplies_rebased(self):
        ps = {p["ref"]: p for p in integrated_parts()}
        for ref in ["U2", "U3"]:
            self.assertEqual(ps[ref]["nets"]["8"], "ANALOG_12V")
            self.assertEqual(ps[ref]["nets"]["4"], "GND")
        self.assertEqual(ps["J103"]["nets"], {"1": "AUX_RAW", "2": "VMID", "3": "GND"})
        self.assertEqual(ps["D201"]["nets"], {"1": "ISO_FEED", "2": "AUX_RAW"})

    def test_generator_atomic_refusal_and_original_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "analog-protected"
            generate(out, True)
            original = (out / "analog-protected.kicad_sch").read_bytes()
            with self.assertRaises(FileExistsError):
                generate(out, True)
            self.assertEqual(
                original, (out / "analog-protected.kicad_sch").read_bytes()
            )
        from create_analog_capture import build

        self.assertEqual(
            build()[0],
            (ROOT / "kicad/analog-front-end/analog-front-end.kicad_sch").read_text(),
        )

    def test_native_fixture_independent_domains_and_terminal_topology(self):
        text = (ROOT / "tests/fixtures/analog-protected.xml").read_text()
        manifest = json.loads(
            (ROOT / "kicad/analog-protected/vmid-manifest.json").read_text()
        )
        # Explicit ranges, not value similarity to choose the independent block.
        power = [
            p
            for p in manifest["parts"]
            if p["ref"]
            in {"D201", *[f"R{i}" for i in range(201, 208)], "C201", "C202", "C203"}
        ]
        result = verify(
            filtered(text, {p["ref"] for p in power}),
            {"parts": power},
            (ROOT / "simulation/analog/vmid-protected.cir").read_text(),
        )
        self.assertEqual(result["native_pins_checked"], 22)
        ap = [p for p in manifest["parts"] if p not in power]
        aliases = {**ALIASES, "ANALOG_12V": "supply", "VMID": "mid", "AUX_RAW": "raw"}
        am = {
            "parts": ap,
            "unassigned_footprints": [p["ref"] for p in ap if not p["footprint"]],
        }
        ax = filtered(text, {p["ref"] for p in ap})
        spice = (ROOT / "simulation/analog/lr4-rc.cir").read_text()
        verify_analog(ax, am, spice, aliases)
        # A self-consistent XML+manifest mutation must still fail TI supply audit.
        bad = copy.deepcopy(am)
        for p in bad["parts"]:
            if p["ref"] == "U2":
                p["nets"]["8"] = "AUX_RAW"
        import xml.etree.ElementTree as ET

        tree = ET.fromstring(ax)
        net = next(
            n
            for n in tree.findall("nets/net")
            if n.attrib["name"].rsplit("/", 1)[-1] == "ANALOG_12V"
        )
        node = next(
            n for n in list(net) if n.attrib["ref"] == "U2" and n.attrib["pin"] == "8"
        )
        net.remove(node)
        raw = next(
            n
            for n in tree.findall("nets/net")
            if n.attrib["name"].rsplit("/", 1)[-1] == "AUX_RAW"
        )
        raw.append(node)
        with self.assertRaises(ValueError):
            verify_analog(ET.tostring(tree, encoding="unicode"), bad, spice, aliases)

    def test_native_export_files_exist_and_match_source(self):
        m = json.loads(
            (ROOT / "docs/images/analog-protected/manifest.json").read_text()
        )
        names = m["source_and_exports_sha256"]
        self.assertTrue(any(n.endswith(".svg") for n in names))
        self.assertTrue(any(n.endswith(".pdf") for n in names))
        for name, digest in names.items():
            self.assertEqual(
                hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest
            )
        self.assertFalse(m["pcb_changed"])

    def test_recorded_evidence_binds_sources_and_keeps_gates(self):
        r = json.loads((ROOT / "tests/reports/vmid-protection-study.json").read_text())
        for name, digest in r["source_hashes"].items():
            self.assertEqual(
                hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest
            )
        self.assertEqual(len(r["power_loss_cases"]), 30)
        self.assertEqual(len(r["startup_brownout_disconnected_source_cases"]), 3)
        self.assertEqual(len(r["coupled_lr4_cases"]), 9)
        self.assertFalse(
            r["missing_isolation_counterexample"]["passes_mid_input_abs_limits"]
        )
        for flag in [
            "hardware_validated",
            "manufacturing_approved",
            "all_frontend_external_inputs_poweroff_protected",
            "macro_used_below_recommended_supply",
            "mpn_temperature_esr_and_pulse_qualified",
        ]:
            self.assertFalse(r[flag])
