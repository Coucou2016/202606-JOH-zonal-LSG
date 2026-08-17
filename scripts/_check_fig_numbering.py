# -*- coding: utf-8 -*-
"""Check that figure numbering is contiguous and in reading order.

Checks the English manuscript (Figure 1..N) and the Chinese report, whose
statistical series (图 N) and spatial series (图 SN) are numbered separately.
Exits non-zero if a gap, duplicate, or out-of-order label is found.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

failures: list[str] = []


def check_sequence(name: str, labels: list[str], expected_start: int = 1) -> None:
    numbers = [int(x) for x in labels]
    expected = list(range(expected_start, expected_start + len(numbers)))
    if numbers != expected:
        failures.append(f"{name}: got {numbers}, expected {expected}")
    else:
        print(f"{name}: OK ({len(numbers)} figures, 1..{numbers[-1]})")


ms = (ROOT / "paper" / "manuscript.md").read_text(encoding="utf-8")
check_sequence("manuscript captions", re.findall(r"!\[(?:Fig|Figure)\.? (\d+)\.", ms))

# Inline references must point at an existing figure.
declared = {int(x) for x in re.findall(r"!\[(?:Fig|Figure)\.? (\d+)\.", ms)}
for ref in re.findall(r"\b(?:Fig|Figure)(?:s)?\.? (\d+)", ms):
    if int(ref) not in declared:
        failures.append(f"manuscript cites missing Figure {ref}")

import glob
import os

report_html_path = None
for f in glob.glob(os.path.join(str(ROOT), "*研究报告*.html")):
    report_html_path = f
    break
if report_html_path and os.path.exists(report_html_path):
    with open(report_html_path, encoding="utf-8") as fh:
        html = fh.read()
    captions = re.findall(r'class="fig-caption">图 (S?\d+)', html)
    check_sequence(
        "report statistical captions",
        [c for c in captions if not c.startswith("S")],
    )
    check_sequence(
        "report spatial captions",
        [c[1:] for c in captions if c.startswith("S")],
    )
else:
    print("report HTML not found, skipping Chinese report figure check")

if failures:
    print("\nFAIL")
    for line in failures:
        print("  " + line)
    sys.exit(1)

print("\nPASS: figure numbering contiguous and in reading order")
