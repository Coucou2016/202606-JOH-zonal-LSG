# -*- coding: utf-8 -*-
from pathlib import Path
import re
import subprocess

ROOT = Path(r"I:\Projects\202606-JOH-zonal-LSG")
html = ROOT / "完整研究报告.html"
md = ROOT / "完整研究报告.md"
pdf = ROOT / "完整研究报告.pdf"
text = html.read_text(encoding="utf-8")

print("HTML_MB", round(html.stat().st_size / 1024 / 1024, 2))
print("MD_KB", round(md.stat().st_size / 1024, 1))
print("PDF_MB", round(pdf.stat().st_size / 1024 / 1024, 2) if pdf.exists() else "MISSING")
print("charset", ("charset=\"UTF-8\"" in text) or ("charset=\"utf-8\"" in text))
print("YaHei", "Microsoft YaHei" in text)
print("base64_imgs", text.count("data:image/png;base64,"))
print("tables", text.count("<table"))
ext = re.findall(r"<(?:link|script)[^>]+(?:href|src)=[\"']https?://[^\"']+", text, re.I)
print("external_link_script", len(ext))
imgs = re.findall(r"<img[^>]+src=[\"']([^\"']+)[\"']", text)
non_data = [s for s in imgs if not s.startswith("data:")]
print("non_data_img", non_data)
for lib in ["echarts", "plotly", "d3.js", "cdn.jsdelivr", "unpkg.com", "cdnjs"]:
    print(lib, lib in text.lower())
print("stage_swap", "stage-swap" in text.lower() or "stage_swap" in text.lower())
print("GZ_ZG", "GZ≈ZG≈ZZ" in text or "GZ" in text and "ZG" in text)
print("pending_marker", text.count("待补充"))
print("old_html_MB", round((ROOT / "研究报告.html").stat().st_size / 1024 / 1024, 2))
print("max-width", "max-width:100%" in text or "max-width: 100%" in text)
r = subprocess.run(["git", "status", "--short"], cwd=str(ROOT), capture_output=True, text=True)
print("--- git status (first 30) ---")
print("\n".join(r.stdout.splitlines()[:30]))
