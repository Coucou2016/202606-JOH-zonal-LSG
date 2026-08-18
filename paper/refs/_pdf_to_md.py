"""Convert reference PDFs to structured Markdown via PyMuPDF (fitz)."""
from __future__ import annotations

import re
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent
PDF_DIR = ROOT / "pdf"
MD_DIR = ROOT / "md"
MD_DIR.mkdir(parents=True, exist_ok=True)

JOBS = [
    {
        "pdf": "fraehr2022_wrr_lsg.pdf",
        "md": "fraehr2022_wrr_lsg.md",
        "shortname": "fraehr2022_wrr_lsg",
        "cite": "Fraehr et al. (2022) Water Resources Research",
        "doi": "10.1029/2022WR032248",
        "source": "Minerva Access OA bitstream (CC BY-NC); publisher also OA",
    },
    {
        "pdf": "tan2025_hess_regionalized_lsg.pdf",
        "md": "tan2025_hess_regionalized_lsg.md",
        "shortname": "tan2025_hess_regionalized_lsg",
        "cite": "Tan et al. (2025) Hydrology and Earth System Sciences",
        "doi": "10.5194/hess-29-3833-2025",
        "source": "Copernicus publisher OA PDF (CC BY)",
    },
    # Supplied by the user on 2026-08-17; identity confirmed from the PDF text
    # layer (title + DOI) rather than from the file name.
    {
        "pdf": "1-s2.0-S0043135424001027-main.pdf",
        "md": "fraehr2024_watres_lsg_fulltext.md",
        "shortname": "fraehr2024_watres_lsg",
        "cite": "Fraehr et al. (2024) Water Research 252, 121202",
        "doi": "10.1016/j.watres.2024.121202",
        "source": "user-supplied publisher PDF (Elsevier open access, CC BY)",
    },
    {
        "pdf": (
            "Water Resources Research - 2023 - Fraehr - "
            "Development of a Fast and Accurate Hybrid Model for Floodplain Inundation.pdf"
        ),
        "md": "fraehr2023a_wrr_floodplain.md",
        "shortname": "fraehr2023a_wrr_floodplain",
        "cite": "Fraehr et al. (2023a) Water Resources Research 59, e2022WR033836",
        "doi": "10.1029/2022WR033836",
        "source": "user-supplied publisher PDF",
    },
    {
        "pdf": "1-s2.0-S0301479724035564-main.pdf",
        "md": "fraehr2025_jem_training_events.md",
        "shortname": "fraehr2025_jem_training_events",
        "cite": (
            "Fraehr et al. Generation and selection of training events for "
            "surrogate flood inundation models, Journal of Environmental Management"
        ),
        "doi": "10.1016/j.jenvman.2024.123570",
        "source": "user-supplied publisher PDF",
    },
]


def clean_line(s: str) -> str:
    s = s.replace("\x00", "")
    s = re.sub(r"[ \t]+", " ", s)
    return s.rstrip()


def page_to_blocks(page: fitz.Page) -> list[str]:
    blocks = page.get_text("blocks")
    blocks = sorted(blocks, key=lambda b: (round(b[1], 1), round(b[0], 1)))
    out: list[str] = []
    for b in blocks:
        text = clean_line(b[4])
        if not text.strip():
            continue
        out.append(text)
    return out


def looks_like_heading(line: str) -> bool:
    s = line.strip()
    if len(s) < 3 or len(s) > 120:
        return False
    if re.match(r"^\d+(\.\d+)*\s+\S", s):
        return True
    if s.isupper() and len(s.split()) <= 12:
        return True
    keys = (
        "Abstract",
        "Introduction",
        "Methods",
        "Methodology",
        "Results",
        "Discussion",
        "Conclusion",
        "Conclusions",
        "References",
        "Data Availability",
        "Acknowledgments",
        "Acknowledgements",
        "Appendix",
        "Supplementary",
    )
    return s in keys or any(s.startswith(k) for k in keys)


def convert(job: dict) -> Path:
    pdf_path = PDF_DIR / job["pdf"]
    doc = fitz.open(pdf_path)
    lines: list[str] = []
    lines.append(f"# {job['cite']}")
    lines.append("")
    lines.append(f"- **DOI:** https://doi.org/{job['doi']}")
    lines.append(f"- **Local PDF:** `paper/refs/pdf/{job['pdf']}`")
    lines.append(f"- **Access:** full text obtained ({job['source']})")
    lines.append("- **Conversion tool:** PyMuPDF (`fitz`) via `paper/refs/_pdf_to_md.py`")
    lines.append(f"- **Pages:** {doc.page_count}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Extracted full text (OCR-free PDF text layer)")
    lines.append("")

    for i, page in enumerate(doc):
        lines.append(f"### Page {i + 1}")
        lines.append("")
        for block in page_to_blocks(page):
            for raw in block.splitlines():
                line = clean_line(raw)
                if not line.strip():
                    continue
                if looks_like_heading(line):
                    lines.append("")
                    lines.append(f"#### {line.strip()}")
                    lines.append("")
                else:
                    lines.append(line)
            lines.append("")
        # Figure / table captions often appear as short lines containing Fig./Table
        # Keep them inline; no separate image export in this pass.
    md_path = MD_DIR / job["md"]
    md_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    doc.close()
    return md_path


def main() -> None:
    for job in JOBS:
        path = convert(job)
        n = path.stat().st_size
        print(f"OK {job['pdf']} -> {path.name} ({n} bytes)")


if __name__ == "__main__":
    main()
