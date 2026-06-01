#!/usr/bin/env python3
"""
Article Format Converter
========================

Converts the markdown article to PDF and HTML formats.

Author: Fabian Alvarez-Primo, PhD
Date: 2026-06-01
"""

import markdown
import pdfkit
from pathlib import Path
import os

def markdown_to_html(md_file, html_file):
    """Convert markdown to HTML with professional styling."""

    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert to HTML
    md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc'])
    html_content = md.convert(md_content)

    # Add professional HTML template
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Revolutionizing Vaccine Design: Multi-Epitope SARS-CoV-2 Vaccine Development</title>
        <style>
            body {{
                font-family: 'Georgia', 'Times New Roman', serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}

            .container {{
                background-color: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}

            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                font-size: 2.2em;
            }}

            h2 {{
                color: #34495e;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 8px;
                margin-top: 30px;
            }}

            h3 {{
                color: #34495e;
                margin-top: 25px;
            }}

            .author {{
                font-style: italic;
                color: #7f8c8d;
                text-align: center;
                margin-bottom: 30px;
                font-size: 1.1em;
            }}

            .abstract {{
                background-color: #ecf0f1;
                padding: 20px;
                border-left: 4px solid #3498db;
                margin: 20px 0;
                font-size: 0.95em;
            }}

            pre {{
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 15px;
                overflow-x: auto;
            }}

            code {{
                background-color: #f8f9fa;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}

            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}

            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}

            blockquote {{
                border-left: 4px solid #3498db;
                margin: 20px 0;
                padding-left: 20px;
                font-style: italic;
                color: #555;
            }}

            .highlight {{
                background-color: #fff3cd;
                padding: 15px;
                border-radius: 5px;
                border: 1px solid #ffeaa7;
                margin: 15px 0;
            }}

            .footer {{
                margin-top: 50px;
                padding-top: 20px;
                border-top: 2px solid #ecf0f1;
                text-align: center;
                color: #7f8c8d;
                font-size: 0.9em;
            }}

            @media (max-width: 600px) {{
                body {{
                    padding: 10px;
                }}
                .container {{
                    padding: 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {html_content}
            <div class="footer">
                <p>Generated from Multi-Epitope Vaccine Design Pipeline</p>
                <p><a href="https://github.com/fabzy4L/multi-epitope-vaccine-design">GitHub Repository</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    # Write HTML file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"[CONVERTED] HTML version saved: {html_file}")

def html_to_pdf(html_file, pdf_file):
    """Convert HTML to PDF using wkhtmltopdf."""

    try:
        # Configure PDF options
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }

        # Convert to PDF
        pdfkit.from_file(html_file, pdf_file, options=options)
        print(f"[CONVERTED] PDF version saved: {pdf_file}")

    except Exception as e:
        print(f"[ERROR] PDF conversion failed: {e}")
        print("[INFO] You may need to install wkhtmltopdf:")
        print("  Windows: Download from https://wkhtmltopdf.org/downloads.html")
        print("  Linux: sudo apt-get install wkhtmltopdf")
        print("  Mac: brew install wkhtmltopdf")

def main():
    """Convert the article to multiple formats."""

    print("ARTICLE FORMAT CONVERTER")
    print("=" * 40)

    # File paths
    base_dir = Path(".")
    md_file = base_dir / "ARTICLE_Multi_Epitope_Vaccine_Design.md"
    html_file = base_dir / "ARTICLE_Multi_Epitope_Vaccine_Design.html"
    pdf_file = base_dir / "ARTICLE_Multi_Epitope_Vaccine_Design.pdf"

    if not md_file.exists():
        print(f"[ERROR] Markdown file not found: {md_file}")
        return

    try:
        # Convert to HTML
        print("[PROCESSING] Converting Markdown to HTML...")
        markdown_to_html(md_file, html_file)

        # Convert to PDF
        print("[PROCESSING] Converting HTML to PDF...")
        html_to_pdf(html_file, pdf_file)

        print(f"\n[COMPLETE] Article conversion finished!")
        print(f"Generated files:")
        print(f"  - HTML: {html_file}")
        print(f"  - PDF: {pdf_file}")

    except ImportError as e:
        print(f"[ERROR] Missing required packages: {e}")
        print("[INFO] Install required packages:")
        print("  pip install markdown pdfkit")

    except Exception as e:
        print(f"[ERROR] Conversion failed: {e}")

if __name__ == "__main__":
    main()