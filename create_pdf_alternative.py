#!/usr/bin/env python3
"""
Alternative PDF Creator
======================

Creates a PDF version using reportlab (pure Python solution).

Author: Fabian Alvarez-Primo, PhD
Date: 2026-06-01
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import re

def create_pdf_from_markdown(md_file, pdf_file):
    """Create PDF from markdown using reportlab."""

    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create PDF
    doc = SimpleDocTemplate(pdf_file, pagesize=A4,
                           topMargin=0.75*inch,
                           bottomMargin=0.75*inch,
                           leftMargin=0.75*inch,
                           rightMargin=0.75*inch)

    # Get styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50'),
        alignment=1  # Center
    )

    author_style = ParagraphStyle(
        'Author',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=20,
        textColor=colors.HexColor('#7f8c8d'),
        alignment=1,  # Center
        fontName='Helvetica-Oblique'
    )

    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#34495e')
    )

    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=8,
        textColor=colors.HexColor('#34495e')
    )

    # Story (content) list
    story = []

    # Split content into lines
    lines = content.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 12))
            continue

        # Title (first # heading)
        if line.startswith('# ') and 'Revolutionizing Vaccine Design' in line:
            title = line[2:].strip()
            story.append(Paragraph(title, title_style))
            continue

        # Author
        if line.startswith('*By Fabian Alvarez-Primo, PhD*'):
            author = "By Fabian Alvarez-Primo, PhD"
            story.append(Paragraph(author, author_style))
            story.append(Spacer(1, 20))
            continue

        # Section headings
        if line.startswith('## '):
            heading = line[3:].strip()
            story.append(Spacer(1, 20))
            story.append(Paragraph(heading, heading2_style))
            continue

        if line.startswith('### '):
            heading = line[4:].strip()
            story.append(Spacer(1, 15))
            story.append(Paragraph(heading, heading3_style))
            continue

        # Skip horizontal rules and other markdown formatting
        if line.startswith('---') or line.startswith('**Key Results:**'):
            continue

        # Regular paragraphs
        if line and not line.startswith('#') and not line.startswith('*') and not line.startswith('-'):
            # Clean up markdown formatting
            line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)  # Bold
            line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', line)      # Italic
            line = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', line)  # Code

            story.append(Paragraph(line, styles['Normal']))
            story.append(Spacer(1, 6))

    # Build PDF
    doc.build(story)
    print(f"[CREATED] PDF version: {pdf_file}")

def main():
    """Create alternative PDF version."""

    print("ALTERNATIVE PDF CREATOR")
    print("=" * 30)

    try:
        create_pdf_from_markdown(
            "ARTICLE_Multi_Epitope_Vaccine_Design.md",
            "ARTICLE_Multi_Epitope_Vaccine_Design_Simple.pdf"
        )
        print("[SUCCESS] Simple PDF created successfully!")

    except ImportError:
        print("[ERROR] reportlab not installed. Installing...")
        import subprocess
        subprocess.run(["pip", "install", "reportlab"])
        create_pdf_from_markdown(
            "ARTICLE_Multi_Epitope_Vaccine_Design.md",
            "ARTICLE_Multi_Epitope_Vaccine_Design_Simple.pdf"
        )

if __name__ == "__main__":
    main()