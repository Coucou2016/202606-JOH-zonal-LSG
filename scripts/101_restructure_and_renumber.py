"""Move the qualitative spatial subsection to the front of Results and renumber
all main-text figures contiguously in citation order.

Pipeline-derived file names (fig01, fig03, fig08-fig19, figA1-figA5) are kept as
is on disk; only the manuscript-facing labels become Figure 1..N in the order the
reader meets them. Relabelling goes through sentinel tokens so that old and new
numbers can never collide during substitution. Run from the repository root.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MS = ROOT / "paper" / "manuscript.md"

SPATIAL_START = "### 3.3 Qualitative spatial diagnosis"
SPATIAL_END = "### 3.4 Three-case pattern"
MARKER = "<!--SPATIAL_BLOCK-->"

# Matches a figure label after Fig./Figs./Figure, or a bare label continuing a
# list such as "Figs. 3, 9, and 13".
LABEL = r"A?\d+"


def move_spatial_block(text: str) -> str:
    """Relocate the spatial subsection body into the placeholder near Results."""
    start = text.index(SPATIAL_START)
    end = text.index(SPATIAL_END)
    body = text[start:end].split("\n", 1)[1].strip("\n")
    text = text[:start] + text[end:]
    return text.replace(MARKER, body)


def caption_order(text: str) -> list[str]:
    """Figure labels in order of first caption appearance."""
    order: list[str] = []
    for match in re.finditer(rf"!\[Fig\. ({LABEL})\.", text):
        if match.group(1) not in order:
            order.append(match.group(1))
    return order


def relabel(text: str, mapping: dict[str, str]) -> str:
    """Rewrite captions and inline cross-references via sentinel tokens."""
    token = {old: f"\x00{new}\x00" for old, new in mapping.items()}

    def to_token(match: re.Match[str]) -> str:
        label = match.group(0)
        return token.get(label, label)

    # Captions: ![Fig. N. ...]
    text = re.sub(
        rf"(?<=!\[Fig\. )({LABEL})(?=\.)",
        to_token,
        text,
    )

    # Single inline references: "Fig. 3", "Figure 1".
    text = re.sub(rf"(?<=\bFig\. )({LABEL})", to_token, text)
    text = re.sub(rf"(?<=\bFigure )({LABEL})", to_token, text)

    # Multi-figure citations: "Figs. 3, 9, and 13" or "Figs. 17-18".
    def sub_group(match: re.Match[str]) -> str:
        return "Figs. " + re.sub(LABEL, to_token, match.group(1))

    text = re.sub(
        rf"\bFigs\. ((?:{LABEL})(?:(?:,| and|, and|–|-) ?(?:{LABEL}))*)",
        sub_group,
        text,
    )

    return text.replace("\x00", "")


def main() -> None:
    text = MS.read_text(encoding="utf-8")
    text = move_spatial_block(text)

    # Section headings shift once the spatial block moves to 3.1.
    text = text.replace("### 3.2 Event-level statistics", "### 3.3 Event-level statistics")

    order = caption_order(text)
    mapping = {old: str(i) for i, old in enumerate(order, start=1)}
    text = relabel(text, mapping)

    MS.write_text(text, encoding="utf-8")

    print("figure relabel map (old -> new):")
    for old, new in mapping.items():
        print(f"  Fig. {old} -> Figure {new}")


if __name__ == "__main__":
    main()
