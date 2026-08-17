#!/usr/bin/env python
"""Self-contained English manuscript HTML (+ best-effort PDF).

Reads paper/manuscript.md, embeds outputs/figures/fig*.png as base64 PNG,
writes paper/manuscript.html and (if Edge/Chrome available) paper/manuscript.pdf.

Same PDF toolchain as scripts/95_final_submission_report.py and
scripts/96_research_report_zh.py: Chromium/Edge headless --print-to-pdf.

Run:
  D:\\miniforge3\\envs\\hydromodel\\python.exe scripts/98_paper_html.py
"""
from __future__ import annotations

import base64
import os
import re
import subprocess
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "paper" / "manuscript.md"
HTML_PATH = ROOT / "paper" / "manuscript.html"
PDF_PATH = ROOT / "paper" / "manuscript.pdf"
FIG_DIR = ROOT / "outputs" / "figures"

# Captions are taken from the manuscript image alt text so that figure numbers
# cannot drift between manuscript.md and the rendered HTML/PDF. Add an entry here
# only to override a caption that cannot be expressed in the markdown alt text.
FIGURE_CAPTIONS: dict[str, str] = {}

CSS = r"""
:root {
  --ink: #1a1a1a;
  --muted: #4a5568;
  --accent: #1a365d;
  --line: #cbd5e0;
  --paper: #ffffff;
  --bg: #f7f8fa;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  font-family: "Times New Roman", Times, "Liberation Serif", Georgia, serif;
  color: var(--ink);
  background: var(--bg);
  line-height: 1.65;
  font-size: 11.5pt;
}
.wrap {
  max-width: 820px;
  margin: 0 auto;
  padding: 36px 28px 72px;
  background: var(--paper);
  box-shadow: 0 0 0 1px var(--line);
}
header.masthead {
  text-align: center;
  border-bottom: 2px solid var(--accent);
  padding-bottom: 22px;
  margin-bottom: 26px;
}
header.masthead .running {
  font-size: 0.78em;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 14px;
}
h1 {
  font-size: 1.55em;
  font-weight: 700;
  line-height: 1.3;
  color: var(--accent);
  margin-bottom: 12px;
}
.subtitle {
  font-size: 1.02em;
  font-style: italic;
  color: var(--muted);
  margin-bottom: 10px;
}
.meta {
  font-size: 0.88em;
  color: var(--muted);
  line-height: 1.55;
}
h2 {
  font-size: 1.22em;
  color: var(--accent);
  margin: 1.55em 0 0.55em;
  padding-bottom: 0.2em;
  border-bottom: 1px solid var(--line);
}
h3 {
  font-size: 1.05em;
  color: #2c5282;
  margin: 1.2em 0 0.45em;
}
p { margin: 0.65em 0; text-align: justify; hyphens: auto; }
strong { font-weight: 700; }
em { font-style: italic; }
code {
  font-family: Consolas, "Courier New", monospace;
  font-size: 0.88em;
  background: #edf2f7;
  padding: 0.05em 0.28em;
}
ul, ol { margin: 0.5em 0 0.8em 1.4em; }
li { margin: 0.25em 0; }
.keywords {
  margin: 0.9em 0 1.2em;
  font-size: 0.95em;
}
.keywords strong { color: var(--accent); }
figure {
  margin: 1.35em 0;
  text-align: center;
}
figure img {
  display: block;
  max-width: 100%;
  width: auto;
  height: auto;
  margin: 0 auto;
}
figcaption {
  margin-top: 0.55em;
  font-size: 0.92em;
  color: var(--ink);
  text-align: left;
  line-height: 1.45;
}
table {
  width: 100%;
  max-width: 100%;
  border-collapse: collapse;
  margin: 1em 0 1.3em;
  font-size: 0.9em;
}
caption {
  caption-side: top;
  text-align: left;
  font-weight: 700;
  margin-bottom: 0.45em;
  color: var(--ink);
}
th, td {
  border: 1px solid #a0aec0;
  padding: 6px 8px;
  vertical-align: top;
}
th {
  background: #edf2f7;
  font-weight: 700;
  text-align: center;
}
td.num, th.num { text-align: right; }
td.center { text-align: center; }
.refs ol {
  margin-left: 1.6em;
  padding-left: 0.2em;
}
.refs li {
  margin: 0.45em 0;
  text-align: justify;
  font-size: 0.92em;
  word-break: break-word;
}
.note {
  font-size: 0.88em;
  color: var(--muted);
  border-left: 3px solid var(--line);
  padding: 6px 12px;
  margin: 0.8em 0;
  background: #fafbfc;
}
.pending {
  background: #fff5f5;
  border: 1px dashed #c53030;
  color: #9b2c2c;
  padding: 10px 12px;
  margin: 0.8em 0;
  font-size: 0.92em;
}
hr {
  border: 0;
  border-top: 1px solid var(--line);
  margin: 1.4em 0;
}
@media print {
  body { background: #fff; font-size: 10.5pt; }
  .wrap { box-shadow: none; max-width: none; padding: 12mm 14mm; }
  figure { break-inside: avoid; page-break-inside: avoid; }
  table { break-inside: avoid; }
  h2, h3 { break-after: avoid; }
}
"""


def b64_png(path: Path) -> str | None:
    if not path.exists():
        return None
    return base64.b64encode(path.read_bytes()).decode("ascii")


def resolve_fig(src: str) -> Path | None:
    """Map markdown image src to a local PNG under outputs/figures/."""
    name = Path(src).name
    candidates = [
        FIG_DIR / name,
        ROOT / src.lstrip("./"),
        (MD_PATH.parent / src).resolve(),
    ]
    for c in candidates:
        try:
            if c.exists() and c.is_file():
                return c
        except OSError:
            continue
    return None


def inline_md(text: str) -> str:
    """Minimal inline markdown: code, bold, italic, links."""
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    # Keep URLs as plain text only (self-contained HTML must not embed http/https links).
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1 (\2)", text)
    return text


def figure_html(src: str, alt: str) -> str:
    path = resolve_fig(src)
    name = Path(src).name
    caption = FIGURE_CAPTIONS.get(name)
    if caption is None:
        # Fall back to alt text as caption body.
        cap_body = alt.strip() or name
        if not cap_body.lower().startswith("figure"):
            m = re.match(r"[Ff]ig\.?\s*(A?\d+[a-z]?)\s*\.?\s*(.*)", cap_body)
            if m:
                rest = m.group(2).strip(" .-:")
                cap_body = f"Figure {m.group(1)}. {rest}" if rest else f"Figure {m.group(1)}."
            else:
                cap_body = f"Figure. {cap_body}"
        caption = cap_body
    if path is None:
        return (
            f'<p class="pending">Missing figure file: <code>{escape(name)}</code>. '
            "Place PNG under <code>outputs/figures/</code> and re-run "
            "<code>scripts/98_paper_html.py</code>.</p>"
        )
    b64 = b64_png(path)
    assert b64 is not None
    return (
        f"<figure>\n"
        f'  <img src="data:image/png;base64,{b64}" alt="{escape(alt or name)}" />\n'
        f"  <figcaption>{escape(caption)}</figcaption>\n"
        f"</figure>"
    )


def parse_table(lines: list[str], start: int) -> tuple[str, int]:
    """Parse a GitHub-flavoured markdown table starting at start; return HTML + next index."""
    rows: list[list[str]] = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|"):
        raw = lines[i].strip()
        cells = [c.strip() for c in raw.strip("|").split("|")]
        # Skip separator row
        if all(re.fullmatch(r":?-{3,}:?", c or "") for c in cells):
            i += 1
            continue
        rows.append(cells)
        i += 1
    if not rows:
        return "", start + 1
    headers = rows[0]
    body = rows[1:]
    # Detect numeric columns for alignment (optional: right-align if most look numeric)
    html = ["<table>", "<thead><tr>"]
    html.append("".join(f"<th>{inline_md(h)}</th>" for h in headers))
    html.append("</tr></thead><tbody>")
    for row in body:
        # Pad short rows
        while len(row) < len(headers):
            row.append("")
        html.append("<tr>" + "".join(f"<td>{inline_md(c)}</td>" for c in row[: len(headers)]) + "</tr>")
    html.append("</tbody></table>")
    return "\n".join(html), i


def is_table_caption_line(line: str) -> bool | str:
    """Return caption string if line looks like 'Table N. …' or '**Table N** …'."""
    s = line.strip()
    m = re.match(r"^\*\*?Table\s+(\d+)[.:)]?\*?\*?\s*(.*)$", s, re.I)
    if m:
        rest = m.group(2).strip().strip("*").strip()
        return f"Table {m.group(1)}. {rest}".rstrip(". ") + ("." if rest and not rest.endswith(".") else "")
    m = re.match(r"^Table\s+(\d+)\s*[\.:)]\s*(.*)$", s, re.I)
    if m:
        rest = m.group(2).strip()
        # Skip pure placeholders that are not captions for an adjacent table
        if "placeholder" in rest.lower() and "see `" in rest.lower():
            return False
        return f"Table {m.group(1)}. {rest}" if rest else f"Table {m.group(1)}."
    return False


def md_to_html_body(md: str) -> tuple[str, list[str], list[str]]:
    """Convert manuscript markdown to HTML body fragments.

    Returns (html, embedded_basenames, missing_basenames).
    """
    # Normalize newlines; drop a leading YAML-ish status block handled separately.
    lines = md.replace("\r\n", "\n").split("\n")
    embedded: list[str] = []
    missing: list[str] = []
    out: list[str] = []
    i = 0
    in_refs = False
    ref_items: list[str] = []
    title_done = False
    pending_table_caption: str | None = None

    def flush_refs():
        nonlocal ref_items, in_refs
        if not ref_items:
            return
        out.append('<div class="refs"><ol>')
        for item in ref_items:
            # Strip leading "N. "; keep DOI URLs as visible plain text (no href).
            body = re.sub(r"^\d+\.\s*", "", item)
            out.append(f"<li>{inline_md(body)}</li>")
        out.append("</ol></div>")
        ref_items = []
        in_refs = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Horizontal rule
        if stripped == "---":
            flush_refs()
            out.append("<hr />")
            i += 1
            continue

        # Empty
        if not stripped:
            flush_refs()
            i += 1
            continue

        # ATX headings
        hm = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if hm:
            flush_refs()
            level = len(hm.group(1))
            text = hm.group(2).strip()
            # Title (# ...) only once at top → already in masthead; skip duplicate h1
            if level == 1 and not title_done:
                title_done = True
                i += 1
                # Skip following working-title / status paragraphs until blank+content section
                # Keep them for meta in masthead — handled outside. Consume italic/bold meta lines.
                while i < len(lines):
                    s2 = lines[i].strip()
                    if not s2:
                        i += 1
                        break
                    if s2.startswith("#"):
                        break
                    if s2.startswith("**") or s2.startswith("*") or s2.startswith("Working"):
                        i += 1
                        continue
                    break
                continue
            if "References" in text:
                in_refs = True
                out.append(f"<h{level}>{escape(text)}</h{level}>")
                i += 1
                continue
            in_refs = False
            out.append(f"<h{level}>{escape(text)}</h{level}>")
            i += 1
            continue

        # Image
        im = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", stripped)
        if im:
            flush_refs()
            alt, src = im.group(1), im.group(2)
            path = resolve_fig(src)
            name = Path(src).name
            if path is None:
                missing.append(name)
            else:
                embedded.append(name)
            out.append(figure_html(src, alt))
            i += 1
            continue

        # Table
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\|?\s*:?-{3,}", lines[i + 1].strip()):
            flush_refs()
            table_html, ni = parse_table(lines, i)
            if pending_table_caption:
                # Inject caption
                table_html = table_html.replace(
                    "<table>",
                    f"<table>\n<caption>{escape(pending_table_caption)}</caption>",
                    1,
                )
                pending_table_caption = None
            elif not table_html.startswith("<table>\n<caption>"):
                # Auto-caption three-case table if unlabeled
                if "Case" in table_html and "LF-only" in table_html:
                    table_html = table_html.replace(
                        "<table>",
                        "<table>\n<caption>Table 2. Three-case area-weighted depth RMSE (m) at B = 4.</caption>",
                        1,
                    )
            out.append(table_html)
            i = ni
            continue

        # Explicit table caption line (store for next table, or emit as note)
        cap = is_table_caption_line(stripped)
        if cap:
            flush_refs()
            pending_table_caption = cap if isinstance(cap, str) else None
            # If next non-empty is not a table, emit as paragraph
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j >= len(lines) or not lines[j].strip().startswith("|"):
                out.append(f"<p><strong>{escape(str(cap))}</strong></p>")
                pending_table_caption = None
            i += 1
            continue

        # Keywords line
        if stripped.lower().startswith("**keywords:**") or stripped.lower().startswith("**keywords**:"):
            flush_refs()
            rest = re.sub(r"^\*\*Keywords:\*\*\s*", "", stripped, flags=re.I)
            out.append(f'<p class="keywords"><strong>Keywords:</strong> {inline_md(rest)}</p>')
            i += 1
            continue

        # Numbered reference list under References
        if in_refs and re.match(r"^\d+\.\s+", stripped):
            # Possibly multi-line? keep single-line for this manuscript
            ref_items.append(stripped)
            i += 1
            continue

        # Bullet / numbered lists (non-ref)
        if re.match(r"^[-*]\s+", stripped) or re.match(r"^\d+\.\s+", stripped):
            flush_refs()
            ordered = bool(re.match(r"^\d+\.\s+", stripped))
            tag = "ol" if ordered else "ul"
            items = []
            while i < len(lines):
                s = lines[i].strip()
                if ordered:
                    m = re.match(r"^\d+\.\s+(.*)$", s)
                else:
                    m = re.match(r"^[-*]\s+(.*)$", s)
                if not m:
                    break
                items.append(f"<li>{inline_md(m.group(1))}</li>")
                i += 1
            out.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue

        # Paragraph (merge consecutive non-blank non-special lines)
        flush_refs()
        para_parts = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt:
                break
            if nxt.startswith("#") or nxt.startswith("|") or nxt.startswith("![") or nxt == "---":
                break
            if re.match(r"^[-*]\s+", nxt) or re.match(r"^\d+\.\s+", nxt):
                break
            if nxt.startswith("**Keywords"):
                break
            para_parts.append(nxt)
            i += 1
        text = " ".join(para_parts)
        # Soft note styling for draft/status/assumptions
        lower = text.lower()
        if lower.startswith("full chatgpt") or lower.startswith("- gp backend") or "tbd" in lower[:40]:
            out.append(f'<p class="note">{inline_md(text)}</p>')
        else:
            out.append(f"<p>{inline_md(text)}</p>")

    flush_refs()
    return "\n".join(out), embedded, missing


def extract_title_meta(md: str) -> tuple[str, str, str]:
    """Return (title, subtitle, meta_html)."""
    lines = md.replace("\r\n", "\n").split("\n")
    title = "Manuscript"
    subtitle = ""
    meta_bits: list[str] = []
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("# ") and not s.startswith("##"):
            title = s[2:].strip()
            # following lines until --- or ##
            for j in range(i + 1, min(i + 12, len(lines))):
                t = lines[j].strip()
                if not t or t == "---":
                    break
                if t.startswith("##"):
                    break
                if t.startswith("**Working title") or t.lower().startswith("working title"):
                    subtitle = re.sub(r"^\*?\*?Working title[^:]*:\*?\*?\s*", "", t).strip()
                elif t.startswith("**Status:**") or t.startswith("**nature-writing"):
                    meta_bits.append(re.sub(r"^\*\*([^*]+)\*\*\s*", r"\1 ", t))
                elif t.startswith("**One-sentence"):
                    meta_bits.append(re.sub(r"^\*\*([^*]+)\*\*\s*", r"\1 ", t))
            break
    meta_html = "<br />\n".join(escape(m) for m in meta_bits)
    return title, subtitle, meta_html


def scrub_external_urls(html: str) -> str:
    """Remove http(s) protocol tokens while preserving DOI / host readability."""
    html = re.sub(r"https?://doi\.org/", "doi:", html, flags=re.I)
    # Any remaining absolute URLs → host/path only (no scheme), for self-containment greps.
    html = re.sub(r"https?://", "", html, flags=re.I)
    return html


def build_html(md: str) -> tuple[str, list[str], list[str]]:
    title, subtitle, meta_html = extract_title_meta(md)
    body, embedded, missing = md_to_html_body(md)
    sub_block = f'<p class="subtitle">{escape(subtitle)}</p>' if subtitle else ""
    meta_block = f'<p class="meta">{meta_html}</p>' if meta_html else ""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{escape(title)}</title>
<style>
{CSS}
</style>
</head>
<body>
<div class="wrap">
<header class="masthead">
  <div class="running">Journal of Hydrology — methods manuscript (local draft)</div>
  <h1>{escape(title)}</h1>
  {sub_block}
  {meta_block}
</header>
{body}
</div>
</body>
</html>
"""
    html = scrub_external_urls(html)
    return html, embedded, missing



def try_pdf(html_path: Path, pdf_path: Path) -> tuple[bool, str]:
    """Chromium/Edge headless print-to-pdf (same as scripts 95/96)."""
    browsers = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(os.environ.get("LOCALAPPDATA", "")) / r"Microsoft\Edge\Application\msedge.exe",
    ]
    browser = next((p for p in browsers if p and p.exists()), None)
    if browser is None:
        return False, "未找到 Edge/Chrome。请用浏览器打开 HTML 后 Ctrl+P 另存为 PDF。"
    if pdf_path.exists():
        try:
            pdf_path.unlink()
        except OSError:
            pass
    uri = html_path.resolve().as_uri()
    args = [
        str(browser),
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        "--allow-file-access-from-files",
        uri,
    ]
    try:
        proc = subprocess.run(args, capture_output=True, timeout=240, cwd=str(ROOT))
    except subprocess.TimeoutExpired:
        return False, "浏览器无头打印超时（240 s）。"
    if pdf_path.exists() and pdf_path.stat().st_size > 10_000:
        return True, f"使用 {browser.name} 无头 --print-to-pdf 成功"
    err = (proc.stderr or b"").decode("utf-8", errors="replace")[-500:]
    return False, f"浏览器已调用但未得到有效 PDF。stderr: {err}"


def main() -> int:
    os.chdir(str(ROOT))
    if not MD_PATH.exists():
        print(f"ERROR: missing {MD_PATH}")
        return 1
    md = MD_PATH.read_text(encoding="utf-8")
    html, embedded, missing = build_html(md)
    HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    HTML_PATH.write_text(html, encoding="utf-8")

    print(f"HTML: {HTML_PATH} ({HTML_PATH.stat().st_size / 1024 / 1024:.2f} MB)")
    print(f"MD:   {MD_PATH} ({MD_PATH.stat().st_size / 1024:.1f} KB)")
    print("Embedded figures:")
    for n in sorted(set(embedded)):
        print(f"  {n}: yes")
    if missing:
        print("Missing figures:")
        for n in sorted(set(missing)):
            print(f"  {n}: MISSING")

    # Self-containment sanity (no external CSS/CDN; no relative figure paths in img src)
    bad_http = re.findall(r'(?:href|src)=["\']https?://', html, flags=re.I)
    bad_rel = re.findall(r'src=["\'](?:\.\./|outputs/)', html)
    bad_css = re.findall(r'<link[^>]+stylesheet', html, flags=re.I)
    n_data = len(re.findall(r'data:image/png;base64,', html))
    print(f"Sanity: data-uri images={n_data}, external http src/href={len(bad_http)}, "
          f"relative fig src={len(bad_rel)}, external stylesheet links={len(bad_css)}")

    ok, msg = try_pdf(HTML_PATH, PDF_PATH)
    if ok:
        print(f"PDF: {PDF_PATH} ({PDF_PATH.stat().st_size / 1024 / 1024:.2f} MB) — {msg}")
    else:
        print(f"PDF: 未运行成功 — {msg}")
    print("Done.")
    return 0 if not missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
