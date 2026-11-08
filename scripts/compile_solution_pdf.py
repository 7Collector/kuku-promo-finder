import os
import subprocess
import sys
from pathlib import Path
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent.parent
md_file = ROOT / "SOLUTION_DOC.md"
html_file = ROOT / "solution_doc.html"
pdf_file = ROOT / "SOLUTION_DOC.pdf"

text = md_file.read_text(encoding="utf-8")
md = MarkdownIt().enable("table")
html_body = md.render(text)

css = """
@page {
    size: A4;
    margin: 12mm 14mm 12mm 14mm;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 8.4pt;
    line-height: 1.28;
    color: #111;
    margin: 0;
    padding: 0;
}
h1 {
    font-size: 13.5pt;
    margin: 0 0 4px 0;
    padding-bottom: 2px;
    border-bottom: 1.5px solid #222;
}
h2 {
    font-size: 9.8pt;
    margin: 6px 0 3px 0;
    padding-bottom: 1px;
    border-bottom: 0.5px solid #ccc;
    color: #0b3d91;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}
p {
    margin: 0 0 4px 0;
}
ul, ol {
    margin: 0 0 4px 0;
    padding-left: 15px;
}
li {
    margin-bottom: 1.5px;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 4px 0 5px 0;
    font-size: 7.8pt;
}
th, td {
    border: 0.5px solid #bbb;
    padding: 2.5px 4.5px;
    text-align: left;
}
th {
    background-color: #f0f4f8;
    font-weight: 600;
}
code {
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
    font-size: 7.8pt;
    background-color: #f3f4f6;
    padding: 1px 3px;
    border-radius: 2px;
}
strong {
    color: #111;
}
em {
    color: #444;
}
"""

html_full = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>SOLUTION_DOC</title>
<style>{css}</style>
</head>
<body>
{html_body}
</body>
</html>
"""

html_file.write_text(html_full, encoding="utf-8")

cmd = [
    "google-chrome",
    "--headless",
    "--disable-gpu",
    f"--print-to-pdf={pdf_file}",
    "--no-pdf-header-footer",
    str(html_file),
]
subprocess.run(cmd, check=True)

# Verify page count
info_out = subprocess.check_output(["pdfinfo", str(pdf_file)]).decode("utf-8")
pages = 0
for line in info_out.splitlines():
    if line.startswith("Pages:"):
        pages = int(line.split()[1])
        break

print(f"Compiled {pdf_file.name}: {pages} pages")
if pages != 2:
    print(f"WARNING: Expected 2 pages, got {pages}")
    sys.exit(1)
print("SUCCESS: Exactly 2 pages!")
