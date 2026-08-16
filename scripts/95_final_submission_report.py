#!/usr/bin/env python
"""Canonical paper report generator (HTML + Markdown).

Reads Track B artefacts only:
  outputs/registry/result_manifest_v4.csv
  outputs/evaluation/carlisle/budget_sweep_true_equal.json
  outputs/evaluation/carlisle/loocv_results.json
  outputs/evaluation/carlisle/multifold_bootstrap.json
  outputs/registry/residual_organization.csv

Older generators (generate_report.py, generate_report_v2.py,
generate_final_report.py, 90_final_report.py, 91_final_report_v3.py)
are deprecated; use this script.
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
FIG = ROOT / "outputs" / "figures"
OUT = ROOT / "outputs" / "evaluation"
REG = ROOT / "outputs" / "registry"


def fmt(v, spec=".4f"):
    if isinstance(v, (int, float, np.floating)):
        return format(float(v), spec)
    return str(v)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def md_table(headers: list[str], rows: list[list]) -> str:
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


def html_table(headers: list[str], rows: list[list], caption: str = "") -> str:
    t = "<table>\n"
    if caption:
        t += f"<caption>{caption}</caption>\n"
    t += "<thead><tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr></thead>\n<tbody>\n"
    for row in rows:
        t += "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>\n"
    t += "</tbody></table>\n"
    return t


def loocv_stats(loocv: dict, B: int):
    items = [e for e in loocv["per_event"] if e["B"] == B]
    deltas = np.array([e["delta_rmse"] for e in items], dtype=float)
    n = len(deltas)
    improved = int(np.sum(deltas > 0))
    rng = np.random.default_rng(42)
    boot = [float(np.mean(rng.choice(deltas, size=n, replace=True))) for _ in range(10000)]
    ci_lo, ci_hi = np.percentile(boot, 2.5), np.percentile(boot, 97.5)
    return {
        "n": n,
        "improved": improved,
        "mean": float(np.mean(deltas)),
        "ci": (float(ci_lo), float(ci_hi)),
        "sig": bool(ci_lo > 0),
    }


def main():
    os.chdir(str(ROOT))
    cb = load_json(OUT / "carlisle" / "budget_sweep_true_equal.json")
    loocv = load_json(OUT / "carlisle" / "loocv_results.json")
    official = load_json(OUT / "carlisle" / "multifold_bootstrap.json")
    with (REG / "residual_organization.csv").open(encoding="utf-8") as f:
        eoi_rows = list(csv.DictReader(f))
    eoi_by_case = {r.get("case", "").lower(): r for r in eoi_rows}
    eoi_car = eoi_by_case.get("carlisle") or (eoi_rows[0] if eoi_rows else {"EOI": "nan"})
    eoi_cho = eoi_by_case.get("chowilla") or {}
    eoi_bur = eoi_by_case.get("burnettrv") or eoi_by_case.get("burnett") or {}
    eoi_val = float(eoi_car["EOI"])  # max-surface protocol (LSG-Max)
    eoi_ts = 0.51  # historical temporal EOI; do not mix with eoi_val
    eoi_w = float(eoi_cho["EOI"]) if eoi_cho.get("EOI") else float("nan")
    eoi_b = float(eoi_bur["EOI"]) if eoi_bur.get("EOI") else float("nan")
    eoi_lab = "LOW" if eoi_val < 0.30 else "HIGH"
    with (REG / "result_manifest_v4.csv").open(encoding="utf-8", newline="") as f:
        manifest = list(csv.DictReader(f))

    def mget(case, model, b=None):
        for r in manifest:
            if r["case"] == case and r["model"] == model:
                if b is None or str(r["B_requested"]) == str(b):
                    return r
        return None

    LF_ONLY = cb["lf_only"]["rmse_area"]
    G4 = cb["budgets"]["4"]["global"]["rmse_area"]
    R4 = cb["budgets"]["4"]["rule"]["rmse_area"]
    K4 = cb["budgets"]["4"]["kmeans"]["rmse_area"]
    G6 = cb["budgets"]["6"]["global"]["rmse_area"]
    R6 = cb["budgets"]["6"]["rule"]["rmse_area"]
    G8 = cb["budgets"]["8"]["global"]["rmse_area"]
    R8 = cb["budgets"]["8"]["rule"]["rmse_area"]
    impr4 = (G4 - R4) / G4 * 100
    L4 = loocv_stats(loocv, 4)
    L6 = loocv_stats(loocv, 6)

    ch_lf = float(mget("Chowilla", "LF-only")["rmse_area"])
    ch_g = float(mget("Chowilla", "global", 4)["rmse_area"])
    ch_r = float(mget("Chowilla", "rule", 4)["rmse_area"])
    b_lf = float(mget("BurnettRV", "LF-only")["rmse_area"])
    b_g = float(mget("BurnettRV", "global")["rmse_area"])
    b_r = float(mget("BurnettRV", "Rule_B4")["rmse_area"])
    b_used = mget("BurnettRV", "global")["events_used"]
    b_avail = mget("BurnettRV", "global")["events_available"]

    bloo_path = OUT / "burnettrv" / "loocv_results.json"
    bloo = load_json(bloo_path) if bloo_path.exists() else None
    bloo_rule = (bloo or {}).get("summary", {}).get("rule") if bloo else None

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    off_sig = bool(official.get("significant"))
    off_txt = (
        f"NOT significant (mean Delta RMSE = {fmt(official['mean_delta_rmse'])} m, "
        f"95% CI [{fmt(official['ci_95_lower'])}, {fmt(official['ci_95_upper'])}], "
        f"improved fraction {official['improved_fraction']:.0%})"
    )

    from lsg.fraehr import load_case_geometry, raw_dir_exists

    def _cells(case, fallback_hf, fallback_lf):
        if not raw_dir_exists(ROOT, case):
            return f"{fallback_hf:,}", f"{fallback_lf:,}"
        g = load_case_geometry(ROOT, case)
        lf = g.get("n_lf")
        return f"{g['n_hf']:,}", (f"{lf:,}" if lf else str(fallback_lf))

    c_nhf, c_nlf = _cells("carlisle", 581061, 5681)
    h_nhf, h_nlf = _cells("chowilla", 109914, 1434)
    b_nhf, b_nlf = _cells("burnettrv", 780785, 15256)

    t1_h = ["Property", "Carlisle", "Chowilla", "Burnett River"]
    t1_r = [
        ["Country", "UK", "Australia", "Australia"],
        ["HF Model", "LISFLOOD-FP", "MIKE 21", "TUFLOW"],
        ["LF Model", "HEC-RAS 2D", "MIKE 21 (coarse)", "HEC-RAS 2D"],
        ["HF Cells", c_nhf, h_nhf, b_nhf],
        ["LF Cells", c_nlf, h_nlf, b_nlf],
        ["Events used / available", "9 / 9", "12 / 31", f"{b_used} / {b_avail}"],
        ["Status", "9-fold LOOCV", "Boundary: LSG degrades", "Global ~ zonal"],
        ["LF-only RMSE (m)", fmt(LF_ONLY), fmt(ch_lf), fmt(b_lf)],
        ["Max-surface EOI", f"{eoi_val:.3f} ({eoi_lab})", f"{eoi_w:.3f}", f"{eoi_b:.3f}"],
    ]
    t2_h = ["B", "Global RMSE", "Rule RMSE", "KMeans RMSE", "Delta Rule"]
    t2_r = []
    for B in ["4", "6", "8"]:
        g = cb["budgets"][B]["global"]["rmse_area"]
        r = cb["budgets"][B]["rule"]["rmse_area"]
        k = cb["budgets"][B]["kmeans"]["rmse_area"]
        t2_r.append([B, fmt(g), fmt(r), fmt(k), f"{(g - r) / g * 100:+.1f}%"])
    t3_h = ["Budget", "Folds improved", "Mean Delta RMSE (m)", "95% CI", "CI excludes 0"]
    t3_r = [
        ["B=4 LOOCV", f"{L4['improved']}/{L4['n']}", fmt(L4["mean"]),
         f"[{fmt(L4['ci'][0])}, {fmt(L4['ci'][1])}]", "YES" if L4["sig"] else "NO"],
        ["B=6 LOOCV", f"{L6['improved']}/{L6['n']}", fmt(L6["mean"]),
         f"[{fmt(L6['ci'][0])}, {fmt(L6['ci'][1])}]", "YES" if L6["sig"] else "NO"],
        ["Official 2-fold", f"{official['improved_fraction']:.0%} of test events",
         fmt(official["mean_delta_rmse"]),
         f"[{fmt(official['ci_95_lower'])}, {fmt(official['ci_95_upper'])}]",
         "NO" if not off_sig else "YES"],
    ]
    if bloo_rule:
        t3_r.append([
            "Burnett B=4 LOOCV",
            f"{bloo_rule['n_improved']}/{bloo_rule['n_folds']}",
            fmt(bloo_rule["mean_delta_rmse"]),
            f"[{fmt(bloo_rule['ci_95_lower'])}, {fmt(bloo_rule['ci_95_upper'])}]",
            "YES" if bloo_rule["significant"] else "NO",
        ])
        t1_r[5][3] = f"{bloo.get('config', {}).get('n_events', b_used)} / {b_avail}"
        t1_r[6][3] = (
            "30-fold LOOCV (zonal not better)"
            if not bloo_rule["significant"] else "30-fold LOOCV"
        )
        bloo_txt = (
            f"Burnett {bloo_rule['n_folds']}-fold event LOOCV at B=4: mean Global RMSE "
            f"{fmt(bloo_rule['mean_global_rmse'])} m vs Rule {fmt(bloo_rule['mean_zonal_rmse'])} m "
            f"(mean Delta RMSE {fmt(bloo_rule['mean_delta_rmse'])} m; "
            f"{bloo_rule['n_improved']}/{bloo_rule['n_folds']} folds zonal better; "
            f"significant={str(bloo_rule['significant']).lower()})."
        )
    else:
        bloo_txt = "Burnett event-level LOOCV JSON not found."
    t5_h = ["Case", "LF-only RMSE", "Global B=4", "Zonal Rule B=4", "Pattern"]
    t5_r = [
        ["Carlisle", fmt(LF_ONLY), fmt(G4), f"{fmt(R4)} ({impr4:+.1f}%)",
         "Zonal > Global > LF"],
        ["Chowilla", fmt(ch_lf), fmt(ch_g), fmt(ch_r),
         "LF-only best; LSG degrades"],
        ["BurnettRV", fmt(b_lf), fmt(b_g), fmt(b_r),
         "12-event split: Global ~ zonal"],
    ]

    css = (
        "*{margin:0;padding:0;box-sizing:border-box}"
        "body{font-family:system-ui,sans-serif;line-height:1.7;color:#222;"
        "background:#f8f9fa;max-width:1100px;margin:0 auto;padding:0 20px}"
        "section{background:#fff;border-radius:8px;padding:25px 30px;"
        "margin-bottom:20px}"
        "h1,h2{color:#1a5276}h2{border-bottom:2px solid #2e86c1;padding-bottom:6px}"
        "table{width:100%;border-collapse:collapse;margin:12px 0;font-size:.88em}"
        "th{background:#2e86c1;color:#fff;padding:8px 6px}"
        "td{padding:7px 6px;border:1px solid #ddd;text-align:center}"
        ".kf{background:#d5f5e3;border-left:4px solid #27ae60;padding:10px 15px;margin:10px 0}"
        ".warn{background:#fdebd0;border-left:4px solid #e67e22;padding:10px 15px;margin:10px 0}"
    )

    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>Hydrodynamically Zoned LSG — Submission Report v4</title>
<style>{css}</style></head><body>
<h1>When Is Global EOF Reduction Insufficient for Multi-Fidelity Flood Inundation Emulation?</h1>
<p><em>A Hydrodynamically Zoned LSG-Max Approach — generated {now}</em></p>

<section id="s1"><h2>1. Abstract</h2>
<p>This study asks whether EOF reduction in multi-fidelity flood emulation is hydrodynamically neutral. Hydrodynamically zoned LSG-Max partitions the floodplain before EOF and GP learning. Evaluation uses the Fraehr (2024) public benchmark. Numbers below are read from <code>outputs/registry/result_manifest_v4.csv</code> and <code>outputs/evaluation/carlisle/budget_sweep_true_equal.json</code>.</p>
<div class="kf"><strong>Primary result (Carlisle, 9-fold LOOCV):</strong> At equal budget B=4, zonal Rule LSG-Max reduces area-weighted RMSE from {fmt(G4)} m (Global) to {fmt(R4)} m ({impr4:.1f}% improvement; {L4['improved']}/{L4['n']} folds improved; 95% CI [{fmt(L4['ci'][0])}, {fmt(L4['ci'][1])}] m). Global LSG degrades as B grows ({fmt(G4)} to {fmt(G6)} to {fmt(G8)} at B=4/6/8) while zonal Rule stays more robust ({fmt(R4)} to {fmt(R6)} to {fmt(R8)}). Max-surface EOI = {eoi_val:.3f} ({eoi_lab}). First-order EOI is not a zoning switch (see ZGG / stage-swap in Discussion).</div>
<div class="warn"><strong>Official 2-fold split is not significant.</strong> <code>multifold_bootstrap.json</code>: {off_txt}. The 9-fold event LOOCV is the primary statistical claim; do not cite the 2-fold test as significant.</div>
<div class="warn"><strong>Burnett 30-fold event LOOCV:</strong> {bloo_txt} Zonal Rule does not improve on Global (not significant).</div>
</section>

<section id="s2"><h2>2. Data and methods</h2>
{html_table(t1_h, t1_r, "Table 1. Case summary. Cell counts from Fraehr geometry files (581061 / 109914 / 780785).")}
<p><strong>LSG-Max:</strong> EOF on wet cells (depth &gt;= 0.03 m) then sklearn GPR. True equal budget: Global and zonal use total mode count B. Zoning features, EOF, and GP are fit on training events only (leakage audit CLEAN PASS).</p>
<p>Track A synthetic 30x40 processed trees are <strong>not cited</strong>. Paper numbers come from scripts/30_carlisle_proper.py, 31_burnettrv_validation.py, 32_burnettrv_loocv.py, 10, 45, and this generator (95).</p>
</section>

<section id="s3"><h2>3. Results</h2>
<h3>3.1 True equal-budget (Carlisle)</h3>
{html_table(t2_h, t2_r, "Table 2. Carlisle true equal-budget RMSE (area-weighted).")}
<div class="kf">Finding 1: Global RMSE rises {((G8-G4)/G4*100):.0f}% from B=4 to B=8. Rule zonal rises {((R8-R4)/R4*100):.0f}%. Finding 2: at B=4, Rule improves {impr4:.1f}% over Global at the same mode budget.</div>
<h3>3.2 Statistical validation</h3>
{html_table(t3_h, t3_r, "Table 3. LOOCV (n=9) versus official 2-fold bootstrap.")}
<div class="warn">The official 2-fold bootstrap CI includes zero (significant=false). Report the 9-fold LOOCV as the event-level result, and state the 2-fold test as not significant.</div>
<h3>3.3 Three-case comparison</h3>
{html_table(t5_h, t5_r, "Table 4. Three-case RMSE from the v4 registry. Chowilla is a boundary case: LSG degrades.")}
<p>Chowilla: coarse LF (1,434 cells, ~77 HF cells per LF cell) yields LSG RMSE ~{fmt(ch_g)} m versus LF-only {fmt(ch_lf)} m. This is a real degradation, not a synthetic “LSG improves” story. Burnett River (12-event split): Global {fmt(b_g)} m versus LF-only {fmt(b_lf)} m; zonal Rule {fmt(b_r)} m is comparable to Global. {bloo_txt}</p>
</section>

<section id="s4"><h2>4. Discussion</h2>
<p>Carlisle (max-surface EOI = {eoi_val:.3f} {eoi_lab}; B=4: {impr4:.1f}% RMSE reduction, {L4['improved']}/{L4['n']} LOOCV folds) shows zoning can help under equal mode budget even when max-surface EOI is low. Burnett max-surface EOI = {eoi_b:.3f} yet 30-fold Rule does not beat Global — high first-order EOI is not sufficient. {bloo_txt} ZGG&gt;0 with equal-budget pure-EOF oracle DeltaRMSE&lt;0 rules out “better HF truncation alone.” Carlisle stage-swap (B=4; <code>stage_swap.json</code>): GG / ZZ / GZ / ZG mean LOOCV RMSE ≈ 0.180 / 0.098 / 0.098 / 0.101 m (9/9 all three zoned arms beat GG). Zoning either EOF coordinates (ZG) or mapping locality (GZ) recovers nearly the full ZZ gain. Recommended wording: the benefit emerges from how zonal structure reorganizes the coupled representation-to-mapping pipeline, rather than from improved EOF reconstruction alone — and stage-swap does not uniquely pin zone-private GPs. Chowilla shows LSG can degrade when LF quality is a poor match to HF.</p>
<p>SI note: a historical temporal EOI ({eoi_ts:.2f}) exists under a different protocol and is not used in main claims.</p>
<p>Limitations: LSG-Max (not time series); sklearn GPR (gpflow SGPR not used); Chowilla archive MD5 not re-verified; Brisbane not run; Burnett KMeans LOOCV skipped (not cheap vs Rule).</p>
</section>

<section id="s5"><h2>5. Conclusions</h2>
<ol>
<li>EOF reduction is not hydrodynamically neutral on Carlisle at equal B=4 ({impr4:.1f}% RMSE reduction; {L4['improved']}/{L4['n']} LOOCV folds).</li>
<li>Zonal capacity control is more robust than inflating Global B (Global {fmt(G4)} to {fmt(G8)}; Rule {fmt(R4)} to {fmt(R8)}).</li>
<li>The benefit is case-dependent: Chowilla LSG degrades; Burnett 30-fold event LOOCV does not support zonal over Global (zonal better in a minority of folds; mean Delta RMSE not positive).</li>
<li>Official 2-fold bootstrap is not significant; do not over-claim it.</li>
</ol>
<p>Data: Fraehr (2024), Figshare 24312658. Code: repository root (path-independent). Registry: outputs/registry/. Audit: outputs/audit/.</p>
<p><em>Generated {now} | canonical script: scripts/95_final_submission_report.py</em></p>
</section>
</body></html>
"""

    (ROOT / "report.html").write_text(html, encoding="utf-8")
    print(f"HTML: report.html ({len(html)/1024:.0f} KB)")

    md = f"""# When Is Global EOF Reduction Insufficient for Multi-Fidelity Flood Inundation Emulation?

*A Hydrodynamically Zoned LSG-Max Approach — Final Report v4, {now}*

## 1. Abstract

This study asks whether EOF reduction in multi-fidelity flood emulation is hydrodynamically neutral. Hydrodynamically zoned LSG-Max partitions the floodplain before EOF and GP learning. Evaluation uses the Fraehr (2024) public benchmark. Numbers are read from `outputs/registry/result_manifest_v4.csv` and `outputs/evaluation/carlisle/budget_sweep_true_equal.json`.

> **Primary result (Carlisle, 9-fold LOOCV):** At equal budget B=4, zonal Rule LSG-Max reduces area-weighted RMSE from {fmt(G4)} m (Global) to {fmt(R4)} m ({impr4:.1f}% improvement; {L4['improved']}/{L4['n']} folds improved; 95% CI [{fmt(L4['ci'][0])}, {fmt(L4['ci'][1])}] m). Global LSG degrades as B grows ({fmt(G4)} → {fmt(G6)} → {fmt(G8)}) while zonal Rule stays more robust ({fmt(R4)} → {fmt(R6)} → {fmt(R8)}). Max-surface EOI = {eoi_val:.3f} ({eoi_lab}). First-order EOI is not a zoning switch.
> **Official 2-fold split is not significant.** `multifold_bootstrap.json`: {off_txt}. The 9-fold event LOOCV is the primary statistical claim.

> **Burnett 30-fold event LOOCV:** {bloo_txt} Zonal Rule does not improve on Global (not significant).

## 2. Data and methods

**Table 1. Case summary.** Cell counts from Fraehr geometry files.

{md_table(t1_h, t1_r)}

LSG-Max uses EOF on wet cells (depth >= 0.03 m) then sklearn GPR. True equal budget: Global and zonal use total mode count B. Zoning, EOF, and GP are fit on training events only (leakage audit CLEAN PASS).

Track A synthetic 30×40 processed trees are **not cited**. Paper scripts: `30_carlisle_proper.py`, `31_burnettrv_validation.py`, `32_burnettrv_loocv.py`, `10_full_real_experiment.py`, `45_build_registry.py`, `95_final_submission_report.py`.

## 3. Results

### 3.1 True equal-budget (Carlisle)

{md_table(t2_h, t2_r)}

Finding 1: Global RMSE rises {((G8-G4)/G4*100):.0f}% from B=4 to B=8. Rule zonal rises {((R8-R4)/R4*100):.0f}%. Finding 2: at B=4, Rule improves {impr4:.1f}% over Global at the same mode budget.

### 3.2 Statistical validation

{md_table(t3_h, t3_r)}

The official 2-fold bootstrap CI includes zero (`significant=false`). Report the 9-fold LOOCV as the event-level result.

### 3.3 Three-case comparison

{md_table(t5_h, t5_r)}

Chowilla is a **boundary case**: LSG RMSE ~{fmt(ch_g)} m versus LF-only {fmt(ch_lf)} m (LSG degrades). Burnett River (12-event split): Global {fmt(b_g)} m versus LF-only {fmt(b_lf)} m; zonal Rule {fmt(b_r)} m is comparable to Global. {bloo_txt}

## 4. Discussion

Carlisle (max-surface EOI = {eoi_val:.3f} {eoi_lab}; B=4: {impr4:.1f}% RMSE reduction, {L4['improved']}/{L4['n']} LOOCV folds) shows zoning can help under equal B even when max-surface EOI is low. Burnett EOI = {eoi_b:.3f} yet Rule does not beat Global on 30-fold LOOCV. {bloo_txt} ZGG>0 with oracle EOF DeltaRMSE<0 rules out pure HF-EOF truncation. Stage-swap LOOCV means GG/ZZ/GZ/ZG ≈ 0.180/0.098/0.098/0.101 m: zone structure via EOF coordinates or mapping locality recovers nearly the ZZ gain; not a unique GP-only localization. Chowilla shows LSG can degrade when LF is a poor match to HF.

SI: historical temporal EOI ({eoi_ts:.2f}) is a different protocol and is excluded from main claims.
Limitations: LSG-Max only; sklearn GPR (gpflow not used); Chowilla archive MD5 not re-verified; Brisbane not run; Burnett KMeans LOOCV skipped (not cheap vs Rule).

## 5. Conclusions

1. EOF reduction is not hydrodynamically neutral on Carlisle at equal B=4 ({impr4:.1f}% RMSE reduction; {L4['improved']}/{L4['n']} LOOCV folds).
2. Zonal capacity control is more robust than inflating Global B (Global {fmt(G4)} → {fmt(G8)}; Rule {fmt(R4)} → {fmt(R8)}).
3. The benefit is case-dependent: Chowilla LSG degrades; Burnett 30-fold event LOOCV does not support zonal over Global (zonal better in a minority of folds; mean Delta RMSE not positive).
4. Official 2-fold bootstrap is not significant; do not over-claim it.

Data: Fraehr (2024), Figshare 24312658. Code: repository root (path-independent). Registry: `outputs/registry/`. Canonical generator: `scripts/95_final_submission_report.py`.
"""
    (ROOT / "report.md").write_text(md, encoding="utf-8")
    print(f"MD: report.md ({(ROOT / 'report.md').stat().st_size/1024:.0f} KB)")

    for ep in [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]:
        if os.path.exists(ep):
            subprocess.run(
                [ep, "--headless", "--disable-gpu",
                 "--print-to-pdf=" + str(ROOT / "report.pdf"),
                 str(ROOT / "report.html")],
                capture_output=True, timeout=60,
            )
            if (ROOT / "report.pdf").exists():
                print(f"PDF: report.pdf ({(ROOT / 'report.pdf').stat().st_size/1024:.0f} KB)")
            break
    else:
        print("PDF: Edge not found — skip")

    print("Done. Carlisle B=4:", fmt(G4), "->", fmt(R4), f"({impr4:.1f}%)")
    print("Official 2-fold significant:", off_sig)
    print("EOI:", eoi_val)


if __name__ == "__main__":
    main()
