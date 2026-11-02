"""Render huong_dan/*.md to PDF with Edge. Needs the `markdown` package: build_pdf.py [lib_dir]."""

import subprocess
import sys
import tempfile
from pathlib import Path

if len(sys.argv) > 1:
    sys.path.insert(0, sys.argv[1])
import markdown

ROOT = Path(__file__).resolve().parents[1]
GUIDES = ROOT / "huong_dan"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CSS = """
@page { size: A4; margin: 17mm 16mm; }
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5pt; line-height: 1.5; color: #1a1a1a; }
h1 { font-size: 20pt; line-height: 1.25; margin: 0 0 10pt; color: #17365d; }
h2 { font-size: 14pt; margin: 18pt 0 6pt; padding-bottom: 3pt; border-bottom: 1px solid #b8c4d6; color: #17365d; break-after: avoid; }
h3 { font-size: 11.5pt; margin: 12pt 0 4pt; color: #17365d; break-after: avoid; }
p, ul, ol { margin: 5pt 0; }
table { width: 100%; border-collapse: collapse; margin: 7pt 0; font-size: 9.5pt; break-inside: avoid; }
thead { display: table-header-group; }
p:has(+ table), p:has(+ pre), p:has(+ figure) { break-after: avoid; }
figure { margin: 8pt 0; break-inside: avoid; }
tr { break-inside: avoid; }
th { background: #e8edf4; text-align: left; font-weight: 600; }
th, td { border: 1px solid #b8c4d6; padding: 3.5pt 5pt; vertical-align: top; }
td:has(> code:only-child) code { white-space: nowrap; }
td:has(> code:only-child) { font-size: 8.5pt; }
code { font-family: Consolas, monospace; font-size: 0.95em; background: #f1f3f6; padding: 0 2pt; }
pre { background: #f1f3f6; padding: 6pt 8pt; border-left: 3px solid #b8c4d6; break-inside: avoid; white-space: pre-wrap; }
pre code { background: none; padding: 0; }
blockquote { margin: 7pt 0; padding: 5pt 9pt; background: #fff6e0; border-left: 3px solid #d9a400; }
blockquote p { margin: 0; }
"""


def render(source):
    body = markdown.markdown(source.read_text(encoding="utf-8"), extensions=["tables", "fenced_code", "sane_lists"])
    html = f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>{source.stem}</title><style>{CSS}</style></head><body>{body}</body></html>'
    with tempfile.TemporaryDirectory() as folder:
        page = Path(folder) / "page.html"
        page.write_text(html, encoding="utf-8")
        target = source.with_suffix(".pdf")
        subprocess.run([EDGE, "--headless=new", "--disable-gpu", f"--user-data-dir={folder}\\edge",
                        "--no-pdf-header-footer", f"--print-to-pdf={target}", page.as_uri()],
                       check=True, capture_output=True, timeout=120)
    print(target.name, target.stat().st_size)


for path in sorted(GUIDES.glob("*.md")):
    render(path)
