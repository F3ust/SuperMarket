"""Dựng báo cáo Word phân tích đa nguồn (tiếng Việt)."""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT  # noqa: F401
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

sys.path.insert(0, str(Path(__file__).parent))
import build_html as H  # noqa: E402  (tái dùng số liệu và câu chữ đã kiểm)

n, p, mil = H.n, H.p, H.mil
CJ, BA, CL, LG, M5 = H.CJ, H.BA, H.CL, H.LG, H.M5
FIG = H.OUT / "figures"
OUTF = H.OUT / "Bao_cao_phan_tich_da_nguon.docx"

BRAND = RGBColor(0x17, 0x3E, 0x35)
ACCENT = RGBColor(0xB0, 0x70, 0x2A)
DATA = RGBColor(0x3F, 0x6F, 0x95)
MUTED = RGBColor(0x5D, 0x6F, 0x68)
FONT = "Calibri"

doc = Document()
sec = doc.sections[0]
sec.page_height, sec.page_width = Cm(29.7), Cm(21)
sec.left_margin = sec.right_margin = Cm(2.2)
sec.top_margin, sec.bottom_margin = Cm(2), Cm(2)

st = doc.styles["Normal"]
st.font.name = FONT
st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
st.paragraph_format.space_after = Pt(6)
st.paragraph_format.line_spacing = 1.2
for lvl, size, col in [(1, 18, BRAND), (2, 14, BRAND), (3, 12, ACCENT)]:
    s = doc.styles[f"Heading {lvl}"]
    s.font.name = FONT
    s.font.size = Pt(size)
    s.font.bold = True
    s.font.color.rgb = col
    s.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    s.element.rPr.rFonts.set(qn("w:ascii"), FONT)
    s.element.rPr.rFonts.set(qn("w:hAnsi"), FONT)
    s.paragraph_format.space_before = Pt(18 if lvl == 1 else 12)
    s.paragraph_format.space_after = Pt(6)
    s.paragraph_format.keep_with_next = True


def shade(cell, hexcol):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), hexcol)
    tcPr.append(sh)


def para(text="", bold=False, italic=False, size=None, color=None, align=None, after=None):
    pa = doc.add_paragraph()
    if text:
        add_runs(pa, text, bold, italic, size, color)
    if align:
        pa.alignment = align
    if after is not None:
        pa.paragraph_format.space_after = Pt(after)
    return pa


def add_runs(pa, text, bold=False, italic=False, size=None, color=None):
    """Hỗ trợ **đậm** đơn giản."""
    parts = text.split("**")
    for i, t in enumerate(parts):
        if not t:
            continue
        r = pa.add_run(t)
        r.bold = bold or (i % 2 == 1)
        r.italic = italic
        if size:
            r.font.size = Pt(size)
        if color:
            r.font.color.rgb = color
    return pa


def bullet(text):
    pa = doc.add_paragraph(style="List Bullet")
    add_runs(pa, text)
    pa.paragraph_format.space_after = Pt(3)
    return pa


def lens(data_text, econ_text):
    t = doc.add_table(rows=2, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for row, (lab, txt, fill, col) in zip(t.rows, [("GÓC DỮ LIỆU", data_text, "EAF1F7", DATA), ("GÓC KINH TẾ", econ_text, "F8EFE3", ACCENT)]):
        c = row.cells[0]
        shade(c, fill)
        c.paragraphs[0].paragraph_format.space_after = Pt(2)
        r = c.paragraphs[0].add_run(lab)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = col
        pa = c.add_paragraph()
        add_runs(pa, txt, size=10.5)
        pa.paragraph_format.space_after = Pt(4)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def figure(name, caption, width=16):
    doc.add_picture(str(FIG / name), width=Cm(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    para(caption, italic=True, size=9, color=MUTED, align=WD_ALIGN_PARAGRAPH.CENTER, after=10)


def table(header, rows, widths=None, font=9.5):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        shade(c, "173E35")
        c.paragraphs[0].text = ""
        r = c.paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = Pt(font)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for k, row in enumerate(rows):
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].paragraphs[0].text = ""
            add_runs(cells[i].paragraphs[0], str(v), size=font)
            if k % 2:
                shade(cells[i], "F1F5F2")
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return t


def toc():
    pa = doc.add_paragraph()
    r = pa.add_run()
    for tag, txt in [("begin", None), (None, 'TOC \\o "1-2" \\h \\z \\u'), ("separate", None), (None, None), ("end", None)]:
        if tag:
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), tag)
            r._r.append(fc)
        elif txt:
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = txt
            r._r.append(it)
        else:
            t = OxmlElement("w:t")
            t.text = "Nhấp chuột phải → Update Field để cập nhật mục lục."
            r._r.append(t)


def footer_page():
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    rr = fp.add_run("Phân tích bán lẻ đa nguồn · trang ")
    rr.font.size = Pt(8.5)
    rr.font.color.rgb = MUTED
    r = fp.add_run()
    for tag, txt in [("begin", None), (None, "PAGE"), ("end", None)]:
        if tag:
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), tag)
            r._r.append(fc)
        else:
            it = OxmlElement("w:instrText")
            it.text = txt
            r._r.append(it)
    r.font.size = Pt(8.5)


footer_page()

exec((Path(__file__).parent / "word_body.py").read_text(encoding="utf-8"))

doc.save(OUTF)
print(OUTF)
