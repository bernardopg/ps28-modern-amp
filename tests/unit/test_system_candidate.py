import hashlib
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import integrate_candidate as candidate
from create_core_draft import parse


class SystemCandidateTests(unittest.TestCase):
    def test_review_import_has_parts_but_no_fake_protection_or_fit(self):
        d = json.loads(
            (ROOT / "kicad/system-candidate/system-manifest.json").read_text()
        )
        self.assertEqual(len(d["parts"]), 205)
        self.assertEqual(d["unassigned_footprints"], [])
        self.assertTrue(d["signal_bridge_connected"])  # only via K501, checked below
        self.assertTrue(d["isolation_mute_supervisor_implemented"])
        self.assertTrue(d["staged_validation"]["signal_bridge_via_relay_only"])
        self.assertFalse(d["analog_placement_inside_oem"])
        self.assertFalse(d["hardware_validated"])
        refs = {p["ref"]: p for p in d["parts"]}
        self.assertFalse({"J101", "J102", "J103"} & set(refs))
        for ref in ["U2", "U3"]:
            self.assertEqual(refs[ref]["nets"]["8"], "ANALOG_12V")
        self.assertEqual(refs["R9"]["value"], "4.7k 1%")
        self.assertEqual(refs["C20"]["nets"], {"1": "DIFF_P", "2": "INA_ISO"})
        self.assertEqual(refs["C20"]["nets"]["1"], refs["U3"]["nets"]["1"])
        self.assertEqual(refs["K501"]["nets"]["3"], "INA_ISO")
        self.assertEqual(refs["K501"]["nets"]["4"], refs["R517"]["nets"]["1"])
        self.assertEqual(refs["R517"]["nets"]["2"], refs["U1"]["nets"]["5"])
        self.assertEqual(refs["D503"]["nets"], {"1": "GND", "2": None, "3": refs["U1"]["nets"]["5"]})
        self.assertNotEqual(refs["C20"]["nets"]["2"], refs["U1"]["nets"]["5"])
        self.assertNotEqual(refs["C21"]["nets"]["2"], refs["U1"]["nets"]["6"])
        for name, expected in d["source_sha256"].items():
            self.assertEqual(
                hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected
            )

    def test_power_and_sequencer_join_core_without_external_control(self):
        d = json.loads((ROOT / "kicad/system-candidate/system-manifest.json").read_text())
        refs = {p["ref"]: p for p in d["parts"]}
        self.assertTrue(d["power_d021_integrated"] and d["seq_d020_subset_integrated"])
        self.assertFalse({"J302", "J303", "J402", "J501"} & set(refs))
        self.assertNotIn("PVDD_36V", {n for p in d["parts"] for n in p["nets"].values()})
        self.assertEqual(refs["D301"]["nets"]["1"], refs["U1"]["nets"]["36"])
        self.assertEqual(refs["R408"]["nets"]["2"], refs["U1"]["nets"]["18"])
        self.assertEqual(refs["L301"]["nets"]["2"], refs["C1"]["nets"]["1"])
        self.assertNotEqual(refs["D301"]["nets"]["2"], refs["D302"]["nets"]["2"])
        for ref in ("J3", "J4", "R7", "R8"):
            self.assertTrue(refs[ref]["dnp"], ref)
        pcb = (ROOT / "kicad/system-candidate/system-candidate.kicad_pcb").read_text()
        self.assertNotIn("PVDD_36V", pcb)

    def test_measured_oem_outline_holes_and_profile_keepout(self):
        m = candidate.oem_mechanics()
        self.assertEqual(m["outline"], (20.0, 20.0, 174.0, 101.0))  # 154 x 81 mm measured
        self.assertEqual(sorted(m["holes"]), [(24.5, 48.0), (24.5, 91.0), (169.5, 48.0), (169.5, 91.0)])
        self.assertEqual(m["profile_keepout"], (58.0, 68.0, 123.0, 101.0))  # 65 x 33 at 38 mm
        pcb = (ROOT / "kicad/system-candidate/system-candidate.kicad_pcb").read_text()
        self.assertIn('"OEM_U_PROFILE"', pcb)
        self.assertEqual(pcb.count('(footprint "MountingHole:MountingHole_3.2mm_M3"'), 4)

    def test_every_footprint_inside_outline_and_none_on_profile(self):
        import re
        m = candidate.oem_mechanics()
        x0, y0, x1, y1 = m["outline"]
        kx0, ky0, kx1, ky1 = m["profile_keepout"]
        pcb = (ROOT / "kicad/system-candidate/system-candidate.kicad_pcb").read_text()
        blocks = re.findall(r'\(footprint "[^"]+"\s*\(layer "([FB])\.Cu"\)(?:.|\n)*?\(at ([-\d.]+) ([-\d.]+)', pcb)
        self.assertEqual(len(blocks), 209)
        for side, x, y in blocks:
            x, y = float(x), float(y)
            self.assertTrue(x0 < x < x1 and y0 < y < y1, (x, y))
            if side == "F":
                self.assertFalse(kx0 < x < kx1 and ky0 < y < ky1, (x, y))

    def test_d030_power_parts_and_unrouted_board_for_manual_layout(self):
        d = json.loads((ROOT / "kicad/system-candidate/system-manifest.json").read_text())
        refs = {p["ref"]: p for p in d["parts"]}
        self.assertIn("B3P-VH", refs["J301"]["mpn"])
        self.assertEqual(refs["D301"]["value"], "P600J")
        self.assertIn("D30.0mm", refs["C301"]["footprint"])
        self.assertEqual(refs["TP101"]["nets"], {"1": "MONO_BIASED"})
        # D-030: autoroute study discarded; routing is manual (PCB-002).
        pcb = (ROOT / "kicad/system-candidate/system-candidate.kicad_pcb").read_text()
        self.assertEqual(pcb.count("(segment"), 0)

    def test_native_capture_and_actual_pad_nets_are_equal(self):
        folder = ROOT / "kicad/system-candidate"
        xml = ET.parse(folder / "candidate.xml")
        nets = {
            (n.get("ref"), n.get("pin")): net.get("name")
            for net in xml.findall(".//nets/net")
            for n in net.findall("node")
        }
        pcb = parse((folder / "system-candidate.kicad_pcb").read_text())
        checked = 0
        for fp in pcb:
            if not isinstance(fp, list) or fp[0] != "footprint":
                continue
            ref = next(
                x[2].strip('"')
                for x in fp
                if isinstance(x, list) and x[0] == "property" and x[1] == '"Reference"'
            )
            for pad in fp:
                if not isinstance(pad, list) or pad[0] != "pad":
                    continue
                number = pad[1].strip('"')
                if not number or (ref, number) not in nets:
                    continue
                net = next(x for x in pad if isinstance(x, list) and x[0] == "net")[
                    -1
                ].strip('"')
                self.assertEqual(net, nets[ref, number], ref + "." + number)
                checked += 1
        self.assertEqual(checked, 581)

    def test_multiunit_paths_and_no_replace_publication(self):
        folder = ROOT / "kicad/system-candidate"
        sch = parse((folder / "system-candidate.kicad_sch").read_text())
        rootid = candidate.child(sch, "uuid")[1].strip('"')
        symbols = {
            next(
                p[2].strip('"')
                for p in n
                if isinstance(p, list) and p[:2] == ["property", '"Reference"']
            ): candidate.child(n, "uuid")[1].strip('"')
            for n in sch
            if isinstance(n, list)
            and n[0] == "symbol"
            and candidate.child(n, "unit")[1] == "1"
        }
        pcb = parse((folder / "system-candidate.kicad_pcb").read_text())
        for fp in pcb:
            if not isinstance(fp, list) or fp[0] != "footprint":
                continue
            ref = next(
                p[2].strip('"')
                for p in fp
                if isinstance(p, list) and p[:2] == ["property", '"Reference"']
            )
            if ref.startswith("H") and ref[1:].isdigit():
                continue  # board-only OEM mounting holes
            self.assertEqual(
                candidate.child(fp, "path")[1].strip('"'),
                "/" + rootid + "/" + symbols[ref],
            )
        with tempfile.TemporaryDirectory() as temp:
            stage = Path(temp) / "stage"
            stage.mkdir()
            target = Path(temp) / "target"
            target.mkdir()  # destination appears after preflight
            with self.assertRaises(FileExistsError):
                candidate.publish_noreplace(stage, target)
            self.assertTrue(stage.exists())
            self.assertTrue(target.exists())
            link = Path(temp) / "broken"
            link.symlink_to(Path(temp) / "missing")
            with self.assertRaises(FileExistsError):
                candidate.generate(link)

    def test_atomic_refusal_and_official_model_identity(self):
        with tempfile.TemporaryDirectory() as temp, self.assertRaises(FileExistsError):
            candidate.generate(Path(temp))
        for name, expected in {
            "CP_Wurth_WCAP-ATG5-P5D10L16.step": "11f68e0547f6812b472a84f3d5affd6a70778d47113482db6f6786ac86b0a0c6",
            "L_Wurth_WE-HCF-2013.step": "f8b342ac40cd4caa08067c027411c74c2abb560f562cbca932eca4cabaa6e739",
        }.items():
            data = (ROOT / "kicad/models/vendor-wurth" / name).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), expected)
            self.assertTrue(data.startswith(b"ISO-10303-21;"))
        self.assertIn(
            "Creative Commons Attribution-ShareAlike 4.0",
            (ROOT / "kicad/models/vendor-wurth/LICENSE.txt").read_text(),
        )


if __name__ == "__main__":
    unittest.main()
