#!/usr/bin/env python3
"""Regenerate ARTICLE_Multi_Epitope_Vaccine_Design.html from the markdown source."""

import markdown
from pathlib import Path

ROOT = Path(__file__).parent.parent

with open(ROOT / "ARTICLE_Multi_Epitope_Vaccine_Design.md", encoding="utf-8") as f:
    md_content = f.read()

md = markdown.Markdown(extensions=["tables", "fenced_code"])
body_html = md.convert(md_content)

CSS = """
        body {
            font-family: 'Georgia', 'Times New Roman', serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }
        .container {
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; font-size: 2.2em; }
        h2 { color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 8px; margin-top: 30px; }
        h3 { color: #34495e; margin-top: 25px; }
        pre { background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 4px; padding: 15px; overflow-x: auto; }
        code { background-color: #f8f9fa; padding: 2px 4px; border-radius: 3px; font-family: 'Courier New', monospace; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f2f2f2; font-weight: bold; }
        blockquote { border-left: 4px solid #3498db; margin: 20px 0; padding-left: 20px; font-style: italic; color: #555; }
        .footer { margin-top: 50px; padding-top: 20px; border-top: 2px solid #ecf0f1; text-align: center; color: #7f8c8d; font-size: 0.9em; }
        @media (max-width: 600px) { body { padding: 10px; } .container { padding: 20px; } }
"""

html = (
    "<!DOCTYPE html>\n"
    '<html lang="en">\n'
    "<head>\n"
    '    <meta charset="UTF-8">\n'
    '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    "    <title>Advancing Vaccine Design: Multi-Epitope SARS-CoV-2 Vaccine Development</title>\n"
    "    <style>" + CSS + "\n    </style>\n"
    "</head>\n"
    "<body>\n"
    '    <div class="container">\n'
    + body_html
    + "\n    </div>\n"
    "</body>\n"
    "</html>\n"
)

out = ROOT / "ARTICLE_Multi_Epitope_Vaccine_Design.html"
out.write_text(html, encoding="utf-8")
print(f"HTML regenerated: {out} ({len(html):,} bytes)")
