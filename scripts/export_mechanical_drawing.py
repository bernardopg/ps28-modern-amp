"""Dimensioned 1:1 board drawing from actual Edge.Cuts and mounting pads."""
import hashlib
from pathlib import Path


def stamp_draft(path, board_sha256):
    """Label native plots without inheriting the historical core's title block."""
    import io
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen.canvas import Canvas

    reader = PdfReader(str(path))
    writer = PdfWriter()
    for page in reader.pages:
        overlay = io.BytesIO()
        canvas = Canvas(overlay, pagesize=(float(page.mediabox.width), float(page.mediabox.height)))
        canvas.setFont("Helvetica", 8)
        canvas.drawString(24, 30, f"PS28 SYSTEM CANDIDATE | {path.stem} | DRAFT / NOT RELEASED | 1:1 - print 100%")
        canvas.setFont("Helvetica", 6)
        canvas.drawString(24, 18, f"PCB SHA256: {board_sha256}")
        canvas.save()
        overlay.seek(0)
        page.merge_page(PdfReader(overlay).pages[0])
        writer.add_page(page)
    with path.open("wb") as stream:
        writer.write(stream)


def export(board_path, output):
    import pcbnew
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import mm
    from reportlab.pdfgen.canvas import Canvas

    board = pcbnew.LoadBoard(str(board_path))
    edges = [g for g in board.GetDrawings() if g.GetLayer() == pcbnew.Edge_Cuts]
    points = [(pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)) for g in edges
              for p in (g.GetStart(), g.GetEnd())]
    x0, y0 = min(p[0] for p in points), min(p[1] for p in points)
    width = max(p[0] for p in points) - x0
    height = max(p[1] for p in points) - y0
    assert abs(width - 154) < .01 and abs(height - 81) < .01
    holes = []
    for fp in board.GetFootprints():
        if fp.GetReference() not in {f"H{i}" for i in range(1, 7)}:
            continue
        for pad in fp.Pads():
            diameter = pcbnew.ToMM(pad.GetDrillSize().x)
            if diameter > 3:
                holes.append((fp.GetReference(), pcbnew.ToMM(pad.GetPosition().x) - x0,
                              pcbnew.ToMM(pad.GetPosition().y) - y0, diameter,
                              "NPTH" if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH else "PTH/GND"))
    assert len(holes) == 6
    canvas = Canvas(str(output), pagesize=landscape(A4))
    canvas.setTitle("PS28 - gabarito cotado 1:1 - rascunho")
    canvas.setFont("Helvetica-Bold", 13)
    canvas.drawString(18 * mm, 194 * mm, "PS28 | PCB 154 x 81 mm | GABARITO COTADO 1:1")
    canvas.setFont("Helvetica", 9)
    canvas.drawString(18 * mm, 185 * mm, "RASCUNHO - imprimir em 100%, sem ajustar a pagina. Fit fisico e G2/G3 pendentes.")
    ox, oy = 25 * mm, 163 * mm
    pos = lambda x, y: (ox + x * mm, oy - y * mm)
    canvas.setLineWidth(.15 * mm)
    for edge in edges:
        assert edge.GetShape() == pcbnew.SHAPE_T_SEGMENT, "Drawing needs arc support"
        a, b = edge.GetStart(), edge.GetEnd()
        canvas.line(*pos(pcbnew.ToMM(a.x) - x0, pcbnew.ToMM(a.y) - y0),
                    *pos(pcbnew.ToMM(b.x) - x0, pcbnew.ToMM(b.y) - y0))
    for ref, x, y, diameter, kind in sorted(holes):
        px, py = pos(x, y)
        canvas.circle(px, py, diameter / 2 * mm)
        canvas.line(px - 3 * mm, py, px + 3 * mm, py)
        canvas.line(px, py - 3 * mm, px, py + 3 * mm)
        canvas.drawString(px + 3 * mm, py + 3 * mm, ref)
    canvas.drawString(ox + 65 * mm, oy + 5 * mm, f"{width:.2f} mm")
    canvas.saveState()
    canvas.translate(ox + (width + 6) * mm, oy - height / 2 * mm)
    canvas.rotate(90)
    canvas.drawCentredString(0, 0, f"{height:.2f} mm")
    canvas.restoreState()
    canvas.drawString(195 * mm, 166 * mm, "DATUM: canto superior esquerdo")
    canvas.drawString(195 * mm, 160 * mm, "X para direita / Y para baixo (mm)")
    canvas.drawString(195 * mm, 150 * mm, "Ref    X       Y       furo / tipo")
    for i, (ref, x, y, diameter, kind) in enumerate(sorted(holes)):
        canvas.drawString(195 * mm, (143 - 7 * i) * mm,
                          f"{ref}   {x:.2f}   {y:.2f}   {diameter:.2f} {kind}")
    canvas.drawString(18 * mm, 62 * mm, "H5/H6: ilhas aterradas com vias PTH de 0,5 mm; consultar Excellon para TODOS os furos.")
    canvas.drawString(18 * mm, 55 * mm, "Espessura nominal: 1,6 mm. Tolerancias, cobre e acabamento: confirmar na cotacao, sem inferir aceite da fabrica.")
    canvas.drawString(18 * mm, 48 * mm, "SPK+ e SPK- ativos. Ligacao do dissipador ao GND por J6. Nao energizar com base neste desenho.")
    canvas.line(25 * mm, 30 * mm, 75 * mm, 30 * mm)
    canvas.line(25 * mm, 28 * mm, 25 * mm, 32 * mm)
    canvas.line(75 * mm, 28 * mm, 75 * mm, 32 * mm)
    canvas.drawString(28 * mm, 24 * mm, "CONFERIR COM REGUA: 50 mm")
    canvas.setFont("Helvetica", 7)
    digest = hashlib.sha256(Path(board_path).read_bytes()).hexdigest()
    canvas.drawString(18 * mm, 14 * mm, f"PCB SHA256: {digest}")
    canvas.save()
