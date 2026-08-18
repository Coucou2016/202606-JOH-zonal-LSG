"""Extract a section outline plus figure/table captions from a reference PDF.

Two-column journal PDFs defeat naive line-based heading detection, so headings
are identified from font size and boldness instead.

Usage: python paper/refs/_outline.py <pdf-name-or-substring>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import fitz

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PDF_DIR = Path(__file__).resolve().parent / "pdf"

needle = sys.argv[1] if len(sys.argv) > 1 else ""
matches = [p for p in sorted(PDF_DIR.glob("*.pdf")) if needle.lower() in p.name.lower()]
if not matches:
    raise SystemExit(f"no PDF matching {needle!r}")
pdf = matches[0]

doc = fitz.open(pdf)
print("FILE:", pdf.name, f"({doc.page_count} pages)")

body_sizes: dict[float, int] = {}
spans: list[tuple[int, float, bool, str]] = []
for pno, page in enumerate(doc, start=1):
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            text = "".join(s["text"] for s in line.get("spans", [])).strip()
            if not text:
                continue
            first = line["spans"][0]
            size = round(first["size"], 1)
            bold = "bold" in first["font"].lower() or "black" in first["font"].lower()
            body_sizes[size] = body_sizes.get(size, 0) + len(text)
            spans.append((pno, size, bold, text))

body = max(body_sizes, key=lambda k: body_sizes[k])
print("body font size:", body)
print("\n--- section outline (numbered headings / larger-or-bold short lines) ---")
seen: set[str] = set()
for pno, size, bold, text in spans:
    if len(text) > 95:
        continue
    numbered = re.match(r"^\d+(\.\d+)*\.?\s+[A-Z]", text)
    prominent = size > body + 0.4 or (bold and size >= body)
    if not (numbered or (prominent and len(text.split()) <= 10)):
        continue
    if text in seen:
        continue
    seen.add(text)
    print(f"  p{pno:>3}  {size:>4}  {'B' if bold else ' '}  {text}")

print("\n--- figure / table captions ---")
for pno, _size, _bold, text in spans:
    if re.match(r"^(Fig\.?|Figure|Table)\s*\d+", text):
        print(f"  p{pno:>3}  {text[:150]}")
doc.close()
