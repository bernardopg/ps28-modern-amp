import sys
import unittest
import importlib.util
import shutil
import csv
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_final_design import inventory
from pcb_model import parse


class FinalInventoryTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("kicad-cli") and importlib.util.find_spec("pcbnew"),
                         "Native KiCad required for integrated generation")
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

    def test_all_purchase_positions_are_selected_and_resistor_codes_match_values(self):
        rows = list(csv.DictReader((ROOT / "bom/system-candidate-selection.csv").read_text().splitlines()))
        self.assertEqual(len(rows), 235)
        self.assertEqual(len({r["Reference"] for r in rows}), 235)
        actual = list(csv.DictReader((ROOT / "bom/system-candidate-inventory.csv").read_text().splitlines()))
        self.assertEqual({r["Reference"] for r in rows},
                         {r["Reference"] for r in actual if r["Purchase"] == "True"})
        self.assertFalse([r for r in actual if r["Pending"]])
        accessories = list(csv.DictReader((ROOT / "bom/system-candidate-accessories.csv").read_text().splitlines()))
        extra = {r["Association"]: r for r in accessories}
        self.assertEqual(extra["F301-FUSE"]["MPN"], "021806.3MXP")
        self.assertEqual(next(r for r in rows if r["Reference"] == "F301")["MPN"], "0031.8201")
        self.assertIn("W7.2mm", next(r for r in rows if r["Reference"] == "C109")["Footprint"])
        current = {}
        for extension, tag in (("kicad_sch", "symbol"), ("kicad_pcb", "footprint")):
            tree = parse((ROOT / "kicad/system-candidate" / ("system-candidate." + extension)).read_text())
            current[extension] = {}
            for node in tree:
                if isinstance(node, list) and node[0] == tag:
                    fields = {x[1].strip('"'): x[2].strip('"') for x in node
                              if isinstance(x, list) and x[0] == "property"}
                    current[extension][fields["Reference"]] = fields
        for row in rows:
            for key in ("MPN", "Manufacturer", "Footprint", "Datasheet", "SelectionNotes"):
                self.assertTrue(row[key], (row["Reference"], key))
                if key != "Footprint":
                    for extension in current:
                        self.assertEqual(current[extension][row["Reference"]][key], row[key],
                                         (extension, row["Reference"], key))
            mpn = row["MPN"]
            if mpn.startswith(("RT0603", "RT1206")):
                code = mpn.split("07", 1)[1][:-1]
                marker = next(c for c in code if c in "RKM")
                resistance = Decimal(code.replace(marker, ".")) * {"R":1,"K":1000,"M":1000000}[marker]
                value = row["Value"].split()[0].lower()
                multiplier = {"k":1000,"m":1000000}.get(value[-1], 1)
                expected = Decimal(value[:-1] if multiplier != 1 else value) * multiplier
                self.assertEqual(resistance, expected, row["Reference"])
                self.assertIn("BRD07", mpn)  # 0.1 percent, 25 ppm/K
                self.assertIn(mpn[2:6], row["Footprint"])

    def test_omron_coil_voltage_suffix_is_exact_but_generic_prose_is_rejected(self):
        xml = '''<export><components><comp ref="K501"><footprint>Relay_SMD:G6K</footprint>
        <fields><field name="Manufacturer">Omron</field><field name="MPN">{}</field></fields>
        </comp></components></export>'''
        self.assertFalse(inventory(xml.format("G6K-2F DC12"))[0]["Pending"])
        self.assertTrue(inventory(xml.format("G6K-2F DC12 equivalent relay"))[0]["Pending"])

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
