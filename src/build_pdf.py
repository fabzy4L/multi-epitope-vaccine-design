#!/usr/bin/env python3
"""
Convert ARTICLE_Multi_Epitope_Vaccine_Design.md to PDF using reportlab.
Parses Markdown → HTML (via python-markdown) → reportlab Platypus flowables.
"""

import re
import markdown
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Tag

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, Preformatted, KeepTogether,
    ListFlowable, ListItem,
)

ROOT    = Path(__file__).parent.parent
MD_FILE = ROOT / "ARTICLE_Multi_Epitope_Vaccine_Design.md"
PDF_OUT = ROOT / "ARTICLE_Multi_Epitope_Vaccine_Design.pdf"

# ── Colour palette ──────────────────────────────────────────────────────────
C_TITLE   = colors.HexColor("#1a2a4a")
C_H2      = colors.HexColor("#2c3e50")
C_H3      = colors.HexColor("#34495e")
C_ACCENT  = colors.HexColor("#3498db")
C_CODE_BG = colors.HexColor("#f4f6f8")
C_BORDER  = colors.HexColor("#b0bec5")
C_TH_BG   = colors.HexColor("#eaf0f6")
C_ROW_ALT = colors.HexColor("#f9fbfd")
C_TEXT    = colors.HexColor("#222222")
C_MUTED   = colors.HexColor("#555555")


def make_styles():
    base = getSampleStyleSheet()

    def ps(name, parent="Normal", **kw):
        return ParagraphStyle(name, parent=base[parent], **kw)

    return {
        "h1": ps("h1", "Heading1",
                 fontSize=20, leading=26, textColor=C_TITLE,
                 fontName="Times-Bold", spaceBefore=6, spaceAfter=10,
                 borderPadding=(0, 0, 4, 0)),
        "h2": ps("h2", "Heading2",
                 fontSize=14, leading=19, textColor=C_H2,
                 fontName="Times-Bold", spaceBefore=18, spaceAfter=6),
        "h3": ps("h3", "Heading3",
                 fontSize=12, leading=16, textColor=C_H3,
                 fontName="Times-BoldItalic", spaceBefore=12, spaceAfter=4),
        "body": ps("body", "Normal",
                   fontSize=11, leading=17, textColor=C_TEXT,
                   fontName="Times-Roman", alignment=TA_JUSTIFY,
                   spaceAfter=8),
        "bullet": ps("bullet", "Normal",
                     fontSize=11, leading=16, textColor=C_TEXT,
                     fontName="Times-Roman", leftIndent=18, spaceAfter=3),
        "code_inline": ps("code_inline", "Normal",
                          fontSize=9, fontName="Courier",
                          textColor=colors.HexColor("#c7254e")),
        "code_block": ps("code_block", "Normal",
                         fontSize=8.5, leading=12, fontName="Courier",
                         textColor=colors.HexColor("#1a1a1a"),
                         backColor=C_CODE_BG, borderPadding=8,
                         leftIndent=8, rightIndent=8,
                         spaceBefore=8, spaceAfter=8),
        "table_cell": ps("table_cell", "Normal",
                         fontSize=9.5, leading=14, fontName="Times-Roman"),
        "table_header": ps("table_header", "Normal",
                           fontSize=9.5, leading=14, fontName="Times-Bold"),
        "caption": ps("caption", "Normal",
                      fontSize=9, leading=13, textColor=C_MUTED,
                      fontName="Times-Italic", spaceAfter=6),
        "author": ps("author", "Normal",
                     fontSize=11, leading=15, textColor=C_MUTED,
                     fontName="Times-Italic", spaceAfter=4, alignment=TA_CENTER),
    }


# ── Inline HTML → reportlab XML conversion ──────────────────────────────────

def inline_to_rl(node, style_key="body"):
    """Recursively convert inline HTML nodes to reportlab paragraph XML."""
    parts = []
    for child in node.children:
        if isinstance(child, NavigableString):
            parts.append(_escape(str(child)))
        elif isinstance(child, Tag):
            tag = child.name
            inner = inline_to_rl(child, style_key)
            if tag in ("strong", "b"):
                parts.append(f"<b>{inner}</b>")
            elif tag in ("em", "i"):
                parts.append(f"<i>{inner}</i>")
            elif tag == "code":
                text = _escape(child.get_text())
                parts.append(
                    f'<font name="Courier" size="9" color="#c7254e">{text}</font>'
                )
            elif tag == "a":
                parts.append(f'<u><font color="#2980b9">{inner}</font></u>')
            elif tag == "br":
                parts.append("<br/>")
            else:
                parts.append(inner)
    return "".join(parts)


def _escape(text):
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


# ── Block element handlers ───────────────────────────────────────────────────

def handle_table(tag, styles):
    rows_data = []
    for row in tag.find_all("tr"):
        cells = []
        for cell in row.find_all(["th", "td"]):
            s = styles["table_header"] if cell.name == "th" else styles["table_cell"]
            txt = inline_to_rl(cell)
            cells.append(Paragraph(txt, s))
        if cells:
            rows_data.append(cells)

    if not rows_data:
        return []

    # Column widths: distribute evenly
    n_cols = max(len(r) for r in rows_data)
    col_w = [5.5 * inch / n_cols] * n_cols

    tbl = Table(rows_data, colWidths=col_w, repeatRows=1)

    # Determine header row count
    header_rows = sum(1 for row in tag.find_all("tr")
                      if row.find("th"))

    cmd = [
        ("GRID",        (0, 0), (-1, -1), 0.5, C_BORDER),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",(0, 0), (-1, -1), 8),
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND",  (0, 0), (-1, header_rows - 1), C_TH_BG),
    ]
    # Alternating row shading (body rows only)
    for i in range(header_rows, len(rows_data)):
        if (i - header_rows) % 2 == 1:
            cmd.append(("BACKGROUND", (0, i), (-1, i), C_ROW_ALT))

    tbl.setStyle(TableStyle(cmd))
    return [tbl, Spacer(1, 6)]


def handle_list(tag, styles, depth=0):
    """Return a list of flowables for ul/ol."""
    items = []
    for li in tag.find_all("li", recursive=False):
        # Inline content of this li (excluding nested lists)
        inline_parts = []
        nested_lists = []
        for child in li.children:
            if isinstance(child, Tag) and child.name in ("ul", "ol"):
                nested_lists.append(child)
            else:
                if isinstance(child, NavigableString):
                    inline_parts.append(_escape(str(child)))
                elif isinstance(child, Tag):
                    inline_parts.append(inline_to_rl(child))

        txt = "".join(inline_parts).strip()
        if txt:
            para = Paragraph(txt, styles["bullet"])
            items.append(para)

        for nested in nested_lists:
            items.extend(handle_list(nested, styles, depth + 1))

    return items


def soup_to_flowables(soup, styles):
    flowables = []

    for tag in soup.body.children if soup.body else soup.children:
        if isinstance(tag, NavigableString):
            continue
        if not isinstance(tag, Tag):
            continue

        name = tag.name

        if name == "h1":
            txt = inline_to_rl(tag)
            flowables.append(Spacer(1, 8))
            flowables.append(Paragraph(txt, styles["h1"]))
            flowables.append(HRFlowable(
                width="100%", thickness=2, color=C_ACCENT,
                spaceAfter=6))

        elif name == "h2":
            txt = inline_to_rl(tag)
            flowables.append(Paragraph(txt, styles["h2"]))
            flowables.append(HRFlowable(
                width="100%", thickness=0.5, color=C_BORDER,
                spaceAfter=4))

        elif name == "h3":
            txt = inline_to_rl(tag)
            flowables.append(Paragraph(txt, styles["h3"]))

        elif name == "p":
            # Check for italic-only paragraph (author / caption)
            txt = inline_to_rl(tag)
            if not txt.strip():
                continue
            raw = tag.get_text()
            # Detect "By Author" line
            if raw.strip().startswith("*By ") or raw.strip().startswith("By "):
                flowables.append(Paragraph(txt, styles["author"]))
            # Detect italic-wrapped caption (starts and ends with *)
            elif raw.strip().startswith("*") and raw.strip().endswith("*"):
                flowables.append(Paragraph(txt, styles["caption"]))
            else:
                flowables.append(Paragraph(txt, styles["body"]))

        elif name in ("ul", "ol"):
            items = handle_list(tag, styles)
            if items:
                flowables.append(Spacer(1, 4))
                flowables.extend(items)
                flowables.append(Spacer(1, 6))

        elif name == "pre":
            code_tag = tag.find("code")
            text = (code_tag or tag).get_text()
            # Keep line breaks; wrap long lines
            flowables.append(Preformatted(text, styles["code_block"]))

        elif name == "table":
            flowables.extend(handle_table(tag, styles))

        elif name == "hr":
            flowables.append(Spacer(1, 6))
            flowables.append(HRFlowable(
                width="100%", thickness=0.75, color=C_BORDER))
            flowables.append(Spacer(1, 6))

        elif name == "blockquote":
            txt = inline_to_rl(tag)
            bq_style = ParagraphStyle(
                "bq", parent=styles["body"],
                leftIndent=18, rightIndent=18,
                textColor=C_MUTED, fontName="Times-Italic",
                borderPadding=(0, 0, 0, 12),
                borderColor=C_ACCENT, borderWidth=2,
            )
            flowables.append(Paragraph(txt, bq_style))

    return flowables


def build_pdf():
    md_text = MD_FILE.read_text(encoding="utf-8")

    md = markdown.Markdown(extensions=["tables", "fenced_code"])
    body_html = md.convert(md_text)
    html = f"<html><body>{body_html}</body></html>"

    soup = BeautifulSoup(html, "html.parser")
    styles = make_styles()
    flowables = soup_to_flowables(soup, styles)

    doc = SimpleDocTemplate(
        str(PDF_OUT),
        pagesize=letter,
        leftMargin=1.0 * inch,
        rightMargin=1.0 * inch,
        topMargin=1.0 * inch,
        bottomMargin=0.9 * inch,
        title="Advancing Vaccine Design: Multi-Epitope SARS-CoV-2 Vaccine Development",
        author="Fabian Alvarez-Primo, PhD",
    )
    doc.build(flowables)

    size_kb = PDF_OUT.stat().st_size // 1024
    print(f"PDF: {PDF_OUT}  ({size_kb} KB, {len(flowables)} elements)")


if __name__ == "__main__":
    build_pdf()
