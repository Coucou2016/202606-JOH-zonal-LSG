"""Print title/DOI/journal evidence from the first page of each reference PDF.

Used to confirm what a file actually is before trusting its file name.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import fitz

# Windows consoles default to GBK here, which cannot encode glyphs such as ©.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PDF_DIR = Path(__file__).resolve().parent / "pdf"

for pdf in sorted(PDF_DIR.glob("*.pdf")):
    doc = fitz.open(pdf)
    head = doc[0].get_text("text")
    meta_title = (doc.metadata or {}).get("title") or ""
    dois = re.findall(r"10\.\d{4,9}/[^\s\"'<>,;)\]]+", head)
    print("=" * 78)
    print("FILE :", pdf.name)
    print("PAGES:", doc.page_count)
    print("META :", meta_title.strip()[:110])
    print("DOIs :", sorted({d.rstrip('.') for d in dois})[:4])
    print("--- first page head ---")
    lines = [ln.strip() for ln in head.splitlines() if ln.strip()]
    for ln in lines[:16]:
        print("  ", ln[:100])
    doc.close()
