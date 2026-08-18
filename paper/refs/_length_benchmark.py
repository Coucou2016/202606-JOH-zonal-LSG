"""Benchmark our manuscript's section lengths against Fraehr et al. (2024).

Fraehr 2024 is the structural template for this study. Its full text only became
available locally on 2026-08-17, so earlier length targets were extrapolated from
Fraehr 2022 / Tan 2025 instead. This script measures the template directly.

Section boundaries come from the numbered headings in the PDF text layer; running
text is counted while references, captions, and front/back matter are excluded.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import fitz

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "paper" / "refs" / "pdf" / "1-s2.0-S0043135424001027-main.pdf"

# Top-level headings in reading order, as confirmed by paper/refs/_outline.py.
TOP = [
    "1. Introduction",
    "2. Surrogate models for comparison",
    "3. Evaluation",
    "4. Case studies",
    "5. Results",
    "6. Discussion",
    "7. Conclusion",
    "Open research",
]

SKIP = re.compile(
    r"^(Fig\.?\s*\d|Figure\s*\d|Table\s*\d|https?://|doi:|\d+\s*$|"
    r"Water Research|N\. Fraehr)",
    re.I,
)


def collect_lines() -> list[str]:
    doc = fitz.open(PDF)
    lines: list[str] = []
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                text = "".join(s["text"] for s in line.get("spans", [])).strip()
                if text:
                    lines.append(text)
    doc.close()
    return lines


def words(chunk: list[str]) -> int:
    total = 0
    for line in chunk:
        if SKIP.match(line):
            continue
        total += len(line.split())
    return total


lines = collect_lines()
idx: dict[str, int] = {}
for name in TOP:
    for i, line in enumerate(lines):
        if line.strip().startswith(name) and name not in idx:
            idx[name] = i
            break

print("=== Fraehr et al. (2024) Water Research — measured section lengths ===")
ordered = [n for n in TOP if n in idx]
ref_counts: dict[str, int] = {}
for a, b in zip(ordered, ordered[1:] + [None]):
    start = idx[a]
    end = idx[b] if b else len(lines)
    n = words(lines[start:end])
    ref_counts[a] = n
    print(f"  {a:<34} {n:>6} words")

body = sum(v for k, v in ref_counts.items() if k != "Open research")
print(f"  {'BODY TOTAL (1-7)':<34} {body:>6} words")

# Our manuscript, counted with the same "running prose only" rule.
ms = (ROOT / "paper" / "manuscript.md").read_text(encoding="utf-8")
sections: dict[str, list[str]] = {}
current = "front"
for line in ms.splitlines():
    if line.startswith("## "):
        current = line[3:].strip()
        sections.setdefault(current, [])
        continue
    if line.startswith("!["):  # figure caption
        continue
    if line.startswith("|") or line.startswith("**Table"):  # tables
        continue
    sections.setdefault(current, []).append(line)

print("\n=== This manuscript — comparable sections ===")
mapping = {
    "1. Introduction": "1. Introduction",
    "2. Methods": "2. Surrogate models + 3. Evaluation + 4. Case studies",
    "3. Results": "5. Results",
    "4. Discussion": "6. Discussion",
    "5. Conclusions": "7. Conclusion",
}
ours_body = 0
for ours, ref in mapping.items():
    n = len(" ".join(sections.get(ours, [])).split())
    ours_body += n
    print(f"  {ours:<18} {n:>6} words   (template: {ref})")
print(f"  {'BODY TOTAL':<18} {ours_body:>6} words")

print("\n=== Ratio ===")
print(f"  ours/template body = {ours_body / body:.2f}x  ({ours_body} vs {body})")
