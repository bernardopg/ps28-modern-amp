"""Native KiCad regression tests for the annotation-only postprocessor."""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from pcb_model import parse
from organize_assembly_labels import organize

HAS_PCBNEW = importlib.util.find_spec("pcbnew") is not None


def without_label_style(tree):
    if not isinstance(tree, list):
        return tree
    if len(tree) > 2 and tree[0] == "property" and tree[1] in ('"Reference"', '"Value"'):
        return tree[:3]
    return [without_label_style(x) for x in tree
            if not (isinstance(x, list) and x[:3] == ['fp_text', 'user', '"${REFERENCE}"'])]


@unittest.skipUnless(HAS_PCBNEW, "Native KiCad Python module required")
class AssemblyLabelsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pcbnew
        cls.kicad = pcbnew
        cls.source = ROOT / "kicad/system-candidate/system-candidate.kicad_pcb"

    def test_layout_is_annotation_only_separated_and_repeatable(self):
        pcbnew = self.kicad
        board = pcbnew.LoadBoard(str(self.source))
        silk_layers = (pcbnew.F_SilkS, pcbnew.B_SilkS)
        def silk():
            return [(f.GetReference(), t.GetText(), t.IsVisible(),
                     pcbnew.ToMM(t.GetPosition()), pcbnew.ToMM(t.GetTextSize()))
                    for f in board.GetFootprints() for t in (f.Reference(), f.Value())
                    if t.GetLayer() in silk_layers]
        initial_silk = silk()
        organize(board, pcbnew)
        self.assertEqual(initial_silk, silk())
        bounds = board.GetBoardEdgesBoundingBox()
        occupied = {}
        for fp in board.GetFootprints():
            for graphic in fp.GraphicalItems():
                if graphic.GetClass() == 'PCB_TEXT' and graphic.GetLayer() in (pcbnew.F_Fab, pcbnew.B_Fab):
                    self.assertNotEqual(graphic.GetText(), '${REFERENCE}')
                    if graphic.IsVisible():
                        occupied.setdefault(graphic.GetLayer(), []).append(graphic.GetBoundingBox())
        for fp in board.GetFootprints():
            text = fp.Reference()
            if text.GetLayer() not in (pcbnew.F_Fab, pcbnew.B_Fab):
                continue
            self.assertTrue(text.IsVisible())
            box = text.GetBoundingBox()
            self.assertTrue(bounds.Contains(box), fp.GetReference())
            for other in occupied.get(text.GetLayer(), []):
                self.assertFalse(box.Intersects(other), fp.GetReference())
            occupied.setdefault(text.GetLayer(), []).append(box)
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.kicad_pcb"
            second = Path(tmp) / "second.kicad_pcb"
            pcbnew.SaveBoard(str(first), board)
            self.assertEqual(without_label_style(parse(self.source.read_text())),
                             without_label_style(parse(first.read_text())))
            organize(board, pcbnew)
            pcbnew.SaveBoard(str(second), board)
            self.assertEqual(first.read_text(), second.read_text())


if __name__ == "__main__":
    unittest.main()
