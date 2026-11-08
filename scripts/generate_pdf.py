import subprocess
import os
import sys
from markdown_it import MarkdownIt

def build_pdf():
    with open("SOLUTION_DOC.md", "r", encoding="utf-8") as f:
        md_text = f.read()

    md = MarkdownIt()
    html_body = md.render(md_text)

    # Clean CSS styled for exactly 2 A4 pages
    html_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{
    size: A4;
    margin: 12mm 15mm 12mm 15mm;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 8.8pt;
    line-height: 1.34;
    color: #1a1a1a;
    margin: 0;
    padding: 0;
  }}
  h1 {{
    font-size: 14pt;
    margin: 0 0 3px 0;
    color: #0f172a;
    font-weight: 700;
  }}
  h2 {{
    font-size: 10.2pt;
    margin: 7px 0 3px 0;
    color: #1e293b;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 1px;
    font-weight: 600;
  }}
  p {{
    margin: 0 0 4px 0;
  }}
  ul, ol {{
    margin: 2px 0 4px 16px;
    padding: 0;
  }}
  li {{
    margin-bottom: 2px;
  }}
  strong {{
    color: #0f172a;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 4px 0;
    font-size: 7.8pt;
    line-height: 1.25;
  }}
  th, td {{
    border: 1px solid #cbd5e1;
    padding: 3px 5px;
    text-align: left;
    vertical-align: top;
  }}
  th {{
    background-color: #f1f5f9;
    font-weight: 600;
    color: #334155;
  }}
  code {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 8pt;
    background-color: #f1f5f9;
    padding: 1px 3px;
    border-radius: 2px;
  }}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""

    html_path = "/tmp/solution_doc.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_doc)

    pdf_path = "SOLUTION_DOC.pdf"
    cmd = [
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        f"--print-to-pdf={pdf_path}",
        "--no-pdf-header-footer",
        html_path
    ]
    subprocess.run(cmd, check=True)

    # Check page count
    info = subprocess.check_output(["pdfinfo", pdf_path]).decode("utf-8")
    for line in info.splitlines():
        if line.startswith("Pages:"):
            print(f"Generated {pdf_path}: {line.strip()}")

if __name__ == "__main__":
    build_pdf()
