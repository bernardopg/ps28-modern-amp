import sys
import unittest
import importlib.util
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_final_design import inventory
from create_core_draft import parse
import integrate_candidate


class FinalInventoryTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("kicad-cli") and importlib.util.find_spec("pcbnew"),
                         "Native KiCad required for integrated generation")
    def test_regenerated_swaps_carry_the_purchase_code_into_schematic(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "candidate"
            integrate_candidate.generate(out)
            rows = parse((out / "system-candidate.kicad_sch").read_text())
            parts = {}
            for node in rows:
                if isinstance(node, list) and node[0] == "symbol":
                    fields = {x[1].strip('"'): x[2].strip('"') for x in node
                              if isinstance(x, list) and x[0] == "property"}
                    parts[fields["Reference"]] = fields
            self.assertEqual(parts["C14"]["MPN"], "UHE1J681MHD")
            self.assertEqual(parts["C15"]["MPN"], "UHE1J681MHD")
            self.assertEqual(parts["J5"]["MPN"], "B2P-VH(LF)(SN)")
            self.assertIn("UHE1J681MHD", parts["C14"]["Source"])
            self.assertIn("pitch3.96mm", parts["J5"]["Source"])
            import json
            manifest = json.loads((out / "system-manifest.json").read_text())
            selected = {p["ref"]: p for p in manifest["parts"]}
            self.assertEqual(selected["J5"]["manufacturer"], "JST")

    def test_missing_purchase_information_is_not_hidden_by_generic_mpn(self):
        rows = inventory('''<export><components>
          <comp ref="R1"><value>10k</value><footprint>Resistor_SMD:R_0603</footprint>
          <fields><field name="MPN">0603 1 %; MPN at BOM</field></fields></comp>
          <comp ref="J3"><property name="dnp"/><fields><field name="MPN">TBD</field></fields></comp>
          <comp ref="TP1"><footprint>TestPoint:TestPoint_Pad</footprint></comp>
          </components></export>''')
        self.assertTrue(rows[0]["Purchase"])
        self.assertIn("MPN", rows[0]["Pending"])
        for row in rows[1:]:
            self.assertFalse(row["Purchase"])
            self.assertFalse(row["Pending"])

    def test_current_purchasing_codes_match_changed_packages_and_values(self):
        root = parse((ROOT / "kicad/system-candidate/system-candidate.kicad_sch").read_text())
        fields = {}
        for node in root:
            if isinstance(node, list) and node[0] == "symbol":
                props = {x[1].strip('"'): x[2].strip('"') for x in node
                         if isinstance(x, list) and x[0] == "property"}
                fields[props["Reference"]] = props
        for ref in ("C14", "C15"):
            self.assertEqual(fields[ref]["MPN"], "UHE1J681MHD")
            self.assertIn("680", fields[ref]["Value"])
            self.assertIn("D12.5mm", fields[ref]["Footprint"])
            self.assertNotIn("UHE1J152MHD", fields[ref]["Source"])
        self.assertEqual(fields["J5"]["MPN"], "B2P-VH(LF)(SN)")
        self.assertIn("pitch3.96mm", fields["J5"]["Source"])
        for ref in ("R101", "R102"):
            self.assertTrue(fields[ref]["MPN"].startswith("CRCW0805"))
            self.assertIn("0805", fields[ref]["Footprint"])
        self.assertEqual(fields["R310"]["MPN"], "RT0603BRD07100KL")


if __name__ == "__main__":
    unittest.main()
