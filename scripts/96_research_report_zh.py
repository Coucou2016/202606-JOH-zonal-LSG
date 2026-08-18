#!/usr/bin/env python
"""Chinese academic research report (parallel to the JOH English pipeline).

Reads Track B JSON/CSV, base64-embeds every PNG under outputs/figures/,
and writes a self-contained HTML plus matching Markdown and (best-effort) PDF.

Does NOT overwrite report.html / report.md / report.pdf.

Run:
  D:\\miniforge3\\envs\\hydromodel\\python.exe scripts/96_research_report_zh.py
"""
from __future__ import annotations

import base64
import csv
import json
import os
import shutil
import subprocess
import sys
from datetime import date
from html import escape
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "outputs" / "figures"
OUT = ROOT / "outputs" / "evaluation"
REG = ROOT / "outputs" / "registry"
AUDIT = ROOT / "outputs" / "audit"
TABLES = ROOT / "outputs" / "tables"

HTML_ZH = ROOT / "研究报告.html"
HTML_EN_NAME = ROOT / "research_report.html"
MD_ZH = ROOT / "研究报告.md"
PDF_ZH = ROOT / "研究报告.pdf"

DATE_STR = "2026-08-16"
PROJECT_PATH = r"I:\Projects\202606-JOH-zonal-LSG"

FIGURE_FILES = [
    "fig01_workflow.png",
    "fig02_zone_maps_real.png",
    "fig03_mode_budget.png",
    "fig09_csi_budget.png",
    "fig04_three_case.png",
    "fig08_per_event_bootstrap.png",
    "fig11_loocv_scatter.png",
    "fig10_burnett_loocv.png",
    "fig08_runtime.png",
    "fig12_stat_ci.png",
    "fig13_mae_bias.png",
    "fig03_eof_variance.png",
    "fig04_metric_boxplots.png",
    "fig06_zone_metrics.png",
    "fig07_budget_zones.png",
    "fig07_training_size.png",
    "fig14_eoi.png",
    "fig15_eoi_vs_delta.png",
    "fig16_official_maxwd_r2.png",
    "fig17_lf_degradation.png",
    "fig18_channel_distance.png",
    "fig19_modal_eoi.png",
]
SYNTHETIC_FIGS = {
    "fig03_eof_variance.png",
    "fig04_metric_boxplots.png",
    "fig06_zone_metrics.png",
    "fig07_budget_zones.png",
    "fig07_training_size.png",
}


def fmt(v, spec=".4f"):
    if isinstance(v, (int, float, np.floating)):
        return format(float(v), spec)
    return str(v)


def fmt_pct(v, spec=".1f"):
    return format(float(v), spec) + "%"


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def b64_png(path: Path) -> str | None:
    if not path.exists():
        return None
    return base64.b64encode(path.read_bytes()).decode("ascii")


def burnett_loocv_means(bloo: dict) -> dict:
    pe = bloo["per_event"]
    return {
        "csi_g": float(np.mean([e["global"]["csi_area"] for e in pe])),
        "csi_z": float(np.mean([e["rule"]["csi_area"] for e in pe])),
        "csi_lf": float(np.mean([e["lf_only"]["csi_area"] for e in pe])),
        "rmse_lf": float(np.mean([e["lf_only"]["rmse_area"] for e in pe])),
    }


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
        "items": items,
        "deltas": deltas,
    }


def html_table(headers, rows, caption, tid=""):
    cap = escape(caption)
    hid = f' id="{tid}"' if tid else ""
    t = f"<table{hid}>\n<caption>{cap}</caption>\n<thead><tr>"
    t += "".join(f"<th>{escape(str(h))}</th>" for h in headers) + "</tr></thead>\n<tbody>\n"
    for row in rows:
        t += "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>\n"
    t += "</tbody></table>\n"
    return t


def md_table(headers, rows):
    lines = [
        "| " + " | ".join(str(h) for h in headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


def img_html(b64: str | None, alt: str, missing_name: str) -> str:
    if not b64:
        return (
            f'<p class="pending">【待补充】图文件缺失：<code>{escape(missing_name)}</code>。'
            "请将 PNG 置于 <code>outputs/figures/</code> 后重新运行本生成脚本。</p>"
        )
    return (
        f'<img src="data:image/png;base64,{b64}" alt="{escape(alt)}" />'
    )


CSS = r"""
:root {
  --ink: #1c2833;
  --muted: #5d6d7e;
  --navy: #1a365d;
  --blue: #2c5282;
  --line: #c5d0dc;
  --paper: #fbfcfd;
  --card: #ffffff;
  --green-bg: #e8f6ef;
  --green: #1e7a4a;
  --warn-bg: #fdf2e6;
  --warn: #b35c00;
  --pend-bg: #f4eef8;
  --pend: #6c3483;
  --note-bg: #eaf2f8;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans SC", "SimSun", sans-serif;
  color: var(--ink);
  background: var(--paper);
  line-height: 1.85;
  font-size: 15.5px;
}
img, svg, table { max-width: 100%; height: auto; }
.wrap { max-width: 980px; margin: 0 auto; padding: 0 22px 64px; }
.running {
  position: sticky; top: 0; z-index: 20;
  background: var(--navy); color: #e8eef5;
  font-size: 12px; letter-spacing: 0.04em;
  padding: 7px 22px; text-align: center;
}
.cover {
  background: linear-gradient(165deg, #12263a 0%, #1a365d 48%, #2c5282 100%);
  color: #fff; text-align: center;
  padding: 72px 36px 56px; margin: 0 -22px 36px;
  border-radius: 0 0 18px 18px;
}
.cover .kicker {
  display: inline-block; border: 1px solid rgba(255,255,255,0.45);
  padding: 4px 14px; border-radius: 999px; font-size: 13px;
  letter-spacing: 0.12em; margin-bottom: 22px;
}
.cover h1 { font-size: 1.85em; font-weight: 700; line-height: 1.45; margin: 0 0 16px; }
.cover .subtitle { font-size: 1.08em; opacity: 0.92; font-weight: 400; margin-bottom: 28px; }
.cover .meta { font-size: 0.92em; opacity: 0.82; line-height: 1.9; }
.toc {
  background: var(--card); border: 1px solid var(--line);
  border-radius: 10px; padding: 22px 28px 18px; margin-bottom: 28px;
}
.toc h2 { font-size: 1.15em; color: var(--navy); margin-bottom: 10px; border: 0; }
.toc ol { padding-left: 22px; }
.toc li { margin: 4px 0; }
.toc a { color: var(--blue); text-decoration: none; }
.toc a:hover { text-decoration: underline; }
section {
  background: var(--card); border: 1px solid var(--line);
  border-radius: 10px; padding: 28px 32px; margin-bottom: 22px;
}
h2 {
  color: var(--navy); font-size: 1.38em;
  border-bottom: 2px solid #2c5282; padding-bottom: 8px; margin: 0 0 16px;
}
h3 { color: var(--blue); font-size: 1.12em; margin: 22px 0 10px; }
h4 { color: #2d4a6f; font-size: 1.02em; margin: 16px 0 8px; }
p { margin-bottom: 12px; text-align: justify; }
p.lead { font-size: 1.02em; }
ul, ol { padding-left: 24px; margin: 8px 0 14px; }
li { margin: 4px 0; }
code {
  font-family: Consolas, "Courier New", monospace;
  font-size: 0.88em; background: #eef3f8; padding: 1px 5px; border-radius: 3px;
}
.kf, .warn, .pend, .note {
  padding: 12px 16px; margin: 12px 0 16px; border-radius: 0 8px 8px 0;
}
.kf { background: var(--green-bg); border-left: 4px solid var(--green); }
.warn { background: var(--warn-bg); border-left: 4px solid var(--warn); }
.pend { background: var(--pend-bg); border-left: 4px solid var(--pend); }
.note { background: var(--note-bg); border-left: 4px solid var(--blue); }
.pending { color: var(--pend); font-weight: 600; }
table {
  width: 100%; border-collapse: collapse; margin: 14px 0 8px; font-size: 0.88em;
}
table caption {
  caption-side: top; text-align: left; font-weight: 700; color: var(--navy);
  margin-bottom: 6px;
}
th {
  background: #1a365d; color: #fff; padding: 8px 6px; font-weight: 600; text-align: center;
}
td { padding: 7px 6px; border: 1px solid #d5dee8; text-align: center; }
tr:nth-child(even) { background: #f4f8fb; }
.figure-block {
  margin: 22px 0 8px; text-align: center;
  page-break-inside: avoid;
}
.figure-block img {
  border: 1px solid var(--line); border-radius: 6px;
  box-shadow: 0 2px 8px rgba(26,54,93,0.08);
}
.fig-caption {
  margin: 8px 0 6px; font-size: 0.92em; color: var(--navy);
  font-weight: 700; text-align: left;
}
.fig-explain, .tbl-explain {
  text-align: justify; font-size: 0.97em; color: #2c3e50; margin-bottom: 12px;
}
.metrics {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px; margin: 14px 0 18px;
}
.metric {
  border: 1px solid var(--line); border-radius: 8px; padding: 12px 10px; text-align: center;
  background: #f7fafc;
}
.metric .v { font-size: 1.35em; font-weight: 700; color: var(--navy); }
.metric .l { font-size: 0.8em; color: var(--muted); margin-top: 2px; }
.metric.good { background: var(--green-bg); }
.metric.bad { background: var(--warn-bg); }
.term { font-weight: 600; }
.footer-note { font-size: 0.85em; color: var(--muted); margin-top: 18px; }
a.ref { color: var(--blue); }
@media print {
  .running { position: static; }
  body { background: #fff; font-size: 11.5pt; }
  .wrap { max-width: 100%; padding: 0; }
  .cover { margin: 0 0 16px; page-break-after: always; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .toc { page-break-after: always; box-shadow: none; }
  section { box-shadow: none; border: 1px solid #ccc; break-inside: avoid; }
  h2, h3, h4 { page-break-after: avoid; }
  .figure-block, table, .kf, .warn, .pend, .note { page-break-inside: avoid; }
  .fig-caption, .fig-explain { page-break-before: avoid; }
  a { color: inherit; text-decoration: none; }
  th { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
@page { size: A4; margin: 16mm 14mm 18mm 14mm; }
"""


def build(data: dict) -> tuple[str, str, list[str], list[str]]:
    """Return (html, markdown, embedded_figs, pending_items)."""
    d = data
    embedded = d["embedded"]
    pending = list(d["pending"])
    figs = d["figs"]

    def fig_block(num, title, fname, alt, explain_html, synthetic=False, conflict=False):
        b64 = figs.get(fname)
        flag = ""
        if synthetic:
            flag = (
                '<div class="warn"><strong>示意/合成管线配图，不可当作论文数字。</strong>'
                "本图来自早期 30×40 合成网格或示意流程，与真实 HDF5 的 Track B 结果不是同一套实验。"
                "正文引用请以 registry 与 JSON 中的面积加权指标为准。</div>"
            )
        if conflict:
            flag = (
                '<div class="warn"><strong>与 Track B 真等预算结果不一致，勿引用本图数字。</strong>'
                "左侧曲线形态与 <code>budget_sweep_true_equal.json</code> 不符"
                "（后者全局 RMSE 随模态预算 B 上升）。请以图 3 与表 3 为准。</div>"
            )
        if b64:
            embedded.append(fname)
        img = img_html(b64, alt, fname)
        return (
            f'<div class="figure-block" id="fig{num}">'
            f"{img}"
            f'<p class="fig-caption">图 {num}　{escape(title)}</p>'
            f"{flag}"
            f'<div class="fig-explain">{explain_html}</div>'
            f"</div>\n"
        )

    def md_fig(num, title, fname, explain, synthetic=False, conflict=False):
        note = ""
        if synthetic:
            note = "\n\n> **示意/合成管线配图，不可当作论文数字。** 二进制图见 HTML 或 `outputs/figures/" + fname + "`。\n"
        if conflict:
            note = "\n\n> **与 Track B 真等预算结果不一致，勿引用本图数字。** 请以图 3 与表 3 为准。\n"
        path = f"outputs/figures/{fname}"
        return (
            f"### 图 {num}　{title}\n\n"
            f"![{title}]({path})\n"
            f"{note}\n"
            f"{explain}\n"
        )

    G4, R4, K4 = d["G4"], d["R4"], d["K4"]
    G6, R6, K6 = d["G6"], d["R6"], d["K6"]
    G8, R8, K8 = d["G8"], d["R8"], d["K8"]
    LF = d["LF"]
    impr4 = d["impr4"]
    L4, L6 = d["L4"], d["L6"]
    official = d["official"]
    eoi_ts = float(d.get("eoi_ts", 0.51))
    eoi_max = d.get("eoi_max") or {}
    eoi_c = float(eoi_max.get("carlisle", float("nan")))
    eoi_w = float(eoi_max.get("chowilla", float("nan")))
    eoi_bmax = float(eoi_max.get("burnettrv", float("nan")))
    eoi = eoi_ts  # 历史时序残差 EOI；最大面用 eoi_c / eoi_w / eoi_bmax
    off = d.get("official_fold") or {}
    deg = d.get("degradation") or {}
    chn = d.get("channel") or {}
    extrap = d.get("extrap") or {}
    modal = d.get("modal_eoi") or {}
    ch_lf, ch_g, ch_r, ch_k = d["ch_lf"], d["ch_g"], d["ch_r"], d["ch_k"]
    b_lf, b_g, b_r = d["b_lf"], d["b_g"], d["b_r"]
    bloo = d["bloo_rule"]
    cb = d["cb"]
    csi = d["csi"]

    t1_h = ["属性", "Carlisle（卡莱尔）", "Chowilla（乔维拉）", "Burnett River（伯内特河）"]
    t1_r = [
        ["国家", "英国", "澳大利亚", "澳大利亚"],
        ["高保真（HF）模型", "LISFLOOD-FP", "MIKE 21", "TUFLOW"],
        ["低保真（LF）模型", "HEC-RAS 2D", "MIKE 21（粗网格）", "HEC-RAS 2D"],
        ["HF 网格单元数", "581,061", "109,914", "780,785"],
        ["LF 网格单元数", "5,681", "1,434", "15,256"],
        ["本文使用 / 库中可用事件数", "9 / 9", "12 / 31", "12（单次划分）或 30（LOOCV） / 74"],
        ["在本文中的角色", "主证据：9 折事件 LOOCV", "边界情形：LSG 劣于仅用 LF", "对照：分区未优于全局"],
        ["仅用 LF 的面积加权 RMSE（m）", fmt(LF), fmt(ch_lf), fmt(b_lf)],
        ["残差组织指数 EOI（最大淹没面，本次）", f"{eoi_c:.3f}（低）", f"{eoi_w:.3f}（低）", f"{eoi_bmax:.3f}（高）"],
        ["时序残差 EOI（历史，7 场训练）", f"{eoi_ts:.2f}（高）", "—", "—"],
    ]
    t2_h = ["编号", "模型", "分区方式", "EOF 模态预算", "目的"]
    t2_r = [
        ["E0", "仅用 LF", "不适用", "不适用", "低保真基线"],
        ["E1", "全局 LSG-Max", "全区（1 区）", "强制 B = 4 / 6 / 8", "等预算对照"],
        ["E2", "规则分区 zLSG-Max", "水深 + 淹没频率规则", "B = 4 / 6 / 8", "物理分区"],
        ["E3", "KMeans 分区 zLSG-Max", "KMeans（K = 4）", "B = 4 / 6 / 8", "数据驱动分区"],
        ["E4", "Carlisle 9 折 LOOCV", "规则 vs 全局", "B = 4 与 B = 6", "事件级显著性"],
        ["E5", "官方 2 折自助法", "规则 vs 全局", "Fraehr 官方划分", "诚实报告：不显著"],
        ["E6", "Chowilla 边界", "全局 / 规则 / KMeans", "B = 4 / 8 / 12", "LSG 退化"],
        ["E7", "BurnettRV 检验", "全局 / 规则 / KMeans", "B = 4 / 8", "高一阶 EOI 但分区无益对照"],
    ]
    t3_h = ["B", "全局 RMSE（m）", "规则分区 RMSE（m）", "KMeans RMSE（m）", "规则相对全局降幅", "全局实际模态数"]
    t3_r = []
    for B, g, r, k, am in [
        ("4", G4, R4, K4, cb["budgets"]["4"]["global"]["actual_modes"]),
        ("6", G6, R6, K6, cb["budgets"]["6"]["global"]["actual_modes"]),
        ("8", G8, R8, K8, cb["budgets"]["8"]["global"]["actual_modes"]),
    ]:
        t3_r.append([B, fmt(g), fmt(r), fmt(k), f"{(g - r) / g * 100:+.1f}%", str(am)])
    t3_r.append(["仅用 LF", fmt(LF), "—", "—", "—", "0"])

    t3c_h = ["B", "全局 CSI", "规则 CSI", "KMeans CSI", "仅用 LF 的 CSI"]
    t3c_r = [
        ["4", fmt(csi["g4"]), fmt(csi["r4"]), fmt(csi["k4"]), fmt(csi["lf"])],
        ["6", fmt(csi["g6"]), fmt(csi["r6"]), fmt(csi["k6"]), fmt(csi["lf"])],
        ["8", fmt(csi["g8"]), fmt(csi["r8"]), fmt(csi["k8"]), fmt(csi["lf"])],
    ]

    t_eoi_h = ["量", "数值", "含义与来源"]
    t_eoi_r = [
        ["Carlisle 时序 EOI（历史）", f"{eoi_ts:.3f}", "7 场训练期时序平均 |LF−HF|；v4 / 原 45 脚本"],
        ["Carlisle 最大面 EOI（本次）", f"{eoi_c:.3f}", "9 场 LSG-Max 面；与模拟器同一协议"],
        ["Chowilla 最大面 EOI", f"{eoi_w:.3f}", "29 场插值事件，HEC-RAS Summary 最大水面"],
        ["BurnettRV 最大面 EOI", f"{eoi_bmax:.3f}", "30 场 burnettrv_30events.npz"],
        ["Carlisle 区间方差（最大面）", f"{float(d.get('eoi_between_max', d['eoi_between'])):.6f}", "各区平均 |LF−HF| 的方差"],
        ["Carlisle 总方差（最大面）", f"{float(d.get('eoi_total_max', d['eoi_total'])):.6f}", "湿单元格子级方差"],
        ["Zone 0（深槽）平均 |LF−HF|", "0.245 m", "2026-06-07 v4 报告，训练期规则分区；本次未重算 HDF5"],
        ["Zone 3（边缘）平均 |LF−HF|", "0.010 m", "与深槽约 25 倍之差；来源同上，不当作新实验"],
    ]
    t_off_h = ["模型", "最大水深 R²", "最大范围 CSI", "面积加权 RMSE（m）"]
    t_off_r = []
    pubm = (off.get("published_mean") or {})
    for key, lab in (
        ("LSG", "已发表 LSG（时序协议）"),
        ("Kabir_1dCNN", "Kabir 1dCNN"),
        ("LSTM_SRR", "LSTM-SRR"),
        ("GP_EOF", "GP-EOF"),
        ("LSTM_EOF", "LSTM-EOF"),
    ):
        r2 = (pubm.get("MaxWD_R2") or {}).get(key)
        cs = (pubm.get("CSI") or {}).get(key)
        if r2 is not None:
            t_off_r.append([lab, fmt(r2), fmt(cs) if cs is not None else "—", "时序 RMSE，不可直接比"])
    for name, lab in (("global", "本文全局 LSG-Max"), ("rule", "本文规则分区 LSG-Max"), ("kmeans", "本文 KMeans LSG-Max")):
        s = (off.get("summary") or {}).get(name)
        if s and "mean_maxwd_r2" in s:
            t_off_r.append([lab, fmt(s["mean_maxwd_r2"]), fmt(s["mean_csi"]), fmt(s["mean_rmse_area"])])
    t_deg_h = ["LF 加粗倍数", "LF 格点数", "仅用 LF RMSE", "全局 RMSE", "规则分区 RMSE"]
    t_deg_r = []
    for fac in sorted((deg.get("factors") or {}), key=lambda x: int(x)):
        rec = deg["factors"][fac]
        t_deg_r.append([
            fac, str(rec.get("n_lf_cells", "")),
            fmt(rec["lf_only"]["rmse_area"]),
            fmt(rec["global"]["rmse_area"]),
            fmt(rec["rule"]["rmse_area"]),
        ])
    t_ch_h = ["分区", "面积加权 RMSE（m）", "CSI"]
    t_ch_r = [["仅用 LF", fmt(chn["lf_only"]["rmse_area"]), fmt(chn["lf_only"]["csi_area"])]] if chn.get("lf_only") else []
    labs_ch = {"global": "全局", "rule": "规则", "rule_channel": "规则+主槽距离", "channel": "主槽距离带", "kmeans": "KMeans+距离"}
    for tag, rec in (chn.get("models") or {}).items():
        t_ch_r.append([labs_ch.get(tag, tag), fmt(rec["rmse_area"]), fmt(rec.get("csi_area", float("nan")))])
    t_modal_h = ["案例", "ZGG（区–全局）", "Oracle RMSE 全局", "Oracle RMSE 分区", "ΔRMSE（G−Z）", "判读"]
    t_modal_r = []
    for case, lab in (("carlisle", "Carlisle"), ("burnettrv", "BurnettRV"), ("chowilla", "Chowilla")):
        rec = (modal.get("cases") or {}).get(case)
        if not rec:
            continue
        p = rec["pooled"]
        t_modal_r.append([
            lab,
            f"{p.get('mean_zgg', float('nan')):+.4f}",
            fmt(p["oracle_rmse_global"]),
            fmt(p["oracle_rmse_zonal"]),
            f"{p['oracle_delta_rmse']:+.4f}",
            p.get("interpretation", ""),
        ])
    t_mae_h = ["B", "全局 MAE", "规则 MAE", "KMeans MAE", "全局偏差", "规则偏差"]
    t_mae_r = []
    for B in ["4", "6", "8"]:
        g, r, k = cb["budgets"][B]["global"], cb["budgets"][B]["rule"], cb["budgets"][B]["kmeans"]
        t_mae_r.append([B, fmt(g["mae_area"]), fmt(r["mae_area"]), fmt(k["mae_area"]),
                        fmt(g["bias_area"]), fmt(r["bias_area"])])
    t_mae_r.append(["仅用 LF", fmt(cb["lf_only"]["mae_area"]), "—", "—",
                    fmt(cb["lf_only"]["bias_area"]), "—"])

    t4_h = ["检验", "改善折数", "平均 ΔRMSE（m）", "95% 自助法区间", "区间是否不含 0"]
    t4_r = [
        [
            "Carlisle B=4 事件 LOOCV",
            f"{L4['improved']}/{L4['n']}",
            fmt(L4["mean"]),
            f"[{fmt(L4['ci'][0])}, {fmt(L4['ci'][1])}]",
            "是（显著）" if L4["sig"] else "否",
        ],
        [
            "Carlisle B=6 事件 LOOCV",
            f"{L6['improved']}/{L6['n']}",
            fmt(L6["mean"]),
            f"[{fmt(L6['ci'][0])}, {fmt(L6['ci'][1])}]",
            "是（显著）" if L6["sig"] else "否",
        ],
        [
            "Carlisle 官方 2 折",
            f"{official['improved_fraction']:.0%} 的检验事件",
            fmt(official["mean_delta_rmse"]),
            f"[{fmt(official['ci_95_lower'])}, {fmt(official['ci_95_upper'])}]",
            "否（significant=false）",
        ],
        [
            "Burnett B=4 的 30 折 LOOCV",
            f"{bloo['n_improved']}/{bloo['n_folds']}",
            fmt(bloo["mean_delta_rmse"]),
            f"[{fmt(bloo['ci_95_lower'])}, {fmt(bloo['ci_95_upper'])}]",
            "否（significant=false）",
        ],
    ]

    t5_h = ["案例", "仅用 LF", "全局 B=4", "规则分区 B=4", "模式"]
    t5_r = [
        ["Carlisle", fmt(LF), fmt(G4), f"{fmt(R4)}（{impr4:+.1f}%）", "分区优于全局，二者均优于仅用 LF（就 RMSE 而言）"],
        ["Chowilla", fmt(ch_lf), fmt(ch_g), fmt(ch_r), "仅用 LF 最好；LSG 显著退化"],
        ["BurnettRV（12 事件单次划分）", fmt(b_lf), fmt(b_g), fmt(b_r), "全局 ≈ 分区，二者均改善 RMSE"],
    ]

    t6_h = ["留出事件", "全局 RMSE（m）", "规则分区 RMSE（m）", "ΔRMSE（全局−分区）", "分区是否更优"]
    t6_r = []
    for e in L4["items"]:
        better = "是" if e["delta_rmse"] > 0 else "否"
        t6_r.append([
            str(e["test_event"]),
            fmt(e["global_rmse"]),
            fmt(e["zonal_rmse"]),
            fmt(e["delta_rmse"]),
            better,
        ])

    t7_h = ["案例", "模型", "请求的 B", "实际模态数", "区数", "状态"]
    t7_r = []
    for row in d["mode_audit"]:
        t7_r.append([
            row["case"], row["model"], row["B_requested"],
            row["B_actual"], row["n_zones"], row["status"],
        ])

    t8_h = ["检查项", "状态", "要点"]
    t8_r = [
        ["划分来源", "OK", "官方 npz；训练 1893 步、检验 211 步、重叠 0"],
        ["分区特征", "OK", "最大水深、淹没频率、残差、KMeans 标准化器均仅用训练事件"],
        ["EOF 与 GP", "OK", "EOF 基、HF 均值、GP 仅在训练 LF/HF 系数上拟合"],
        ["指标", "OK", "全部在检验集计算；面积权来自几何，不依赖标签"],
        ["总体", "CLEAN_PASS", "passed=true；随机种子 42"],
    ]

    t9_h = ["案例", "B", "全局 RMSE", "规则 RMSE", "KMeans RMSE", "仅用 LF"]
    t9_r = []
    chb = d["ch_full"]["budgets"]
    for B in ["4", "8", "12"]:
        if B not in chb:
            continue
        t9_r.append([
            "Chowilla", B,
            fmt(chb[B]["global"]["rmse_area"]),
            fmt(chb[B]["rule"]["rmse_area"]),
            fmt(chb[B]["kmeans"]["rmse_area"]),
            fmt(ch_lf),
        ])

    t10_h = ["模型", "面积加权 RMSE（m）", "面积加权 CSI", "实际模态数", "说明"]
    vs = d["burnett_std"]
    t10_r = [
        ["仅用 LF", fmt(vs["lf_only"]["rmse_area"]), fmt(vs["lf_only"]["csi_area"]), "0", "12 事件单次划分基线"],
        ["全局", fmt(vs["global"]["rmse_area"]), fmt(vs["global"]["csi_area"]), str(vs["global"]["n_modes"]), "强制 B=4（与分区等容量）"],
        ["KMeans B=4", fmt(vs["KMeans_B4"]["rmse_area"]), fmt(vs["KMeans_B4"]["csi_area"]), str(vs["KMeans_B4"]["total_modes"]), "与规则几乎相同"],
        ["规则 B=4", fmt(vs["Rule_B4"]["rmse_area"]), fmt(vs["Rule_B4"]["csi_area"]), str(vs["Rule_B4"]["total_modes"]), "与 KMeans 数值重合"],
        ["规则 B=8", fmt(vs["Rule_B8"]["rmse_area"]), fmt(vs["Rule_B8"]["csi_area"]), str(vs["Rule_B8"]["total_modes"]), "略差于 B=4"],
        ["全局 30 折均值", fmt(bloo["mean_global_rmse"]), fmt(d["bloo_means"]["csi_g"]), "4", "事件 LOOCV"],
        ["规则 30 折均值", fmt(bloo["mean_zonal_rmse"]), fmt(d["bloo_means"]["csi_z"]), "4", f"{bloo['n_improved']}/{bloo['n_folds']} 折优于全局"],
        ["仅用 LF 的 30 折均值", fmt(d["bloo_means"]["rmse_lf"]), fmt(d["bloo_means"]["csi_lf"]), "0", "与 12 事件划分基线不同协议"],
    ]

    scripts_h = ["脚本", "轨道", "作用"]
    scripts_r = [
        ["<code>scripts/30_carlisle_proper.py</code>", "B（可引用）", "Carlisle 真等预算、面积加权、防泄漏"],
        ["<code>scripts/31_burnettrv_validation.py</code>", "B", "Burnett 12 事件标准网格检验"],
        ["<code>scripts/32_burnettrv_loocv.py</code>", "B", "Burnett 30 事件 LOOCV"],
        ["<code>scripts/40_compute_eoi.py</code>", "B", "三案例最大面 EOI"],
        ["<code>scripts/46_modal_eoi.py</code>", "B", "二阶 ZGG + 等预算纯 EOF oracle"],
        ["<code>scripts/41_official_fold_zonal.py</code>", "B", "官方 9 折 vs 已发表五模型"],
        ["<code>scripts/42_extrap_zonal.py</code>", "B", "外推 p10/p11 与湿掩膜"],
        ["<code>scripts/43_lf_degradation.py</code>", "B", "LF 网格加粗"],
        ["<code>scripts/44_distance_to_channel.py</code>", "B", "主槽距离分区"],
        ["<code>scripts/10_full_real_experiment.py</code>", "B", "三案例真实数据实验入口"],
        ["<code>scripts/20_audit_leakage.py</code>", "B", "Carlisle 泄漏审计"],
        ["<code>scripts/45_build_registry.py</code>", "B", "从 JSON 重建 result_manifest_v4"],
        ["<code>scripts/08_make_figures.py</code>", "B 配图（旧）", "已由 97 接管可引用图；保留以免旧文档断链"],
        ["<code>scripts/09_make_tables.py</code>", "B", "表 1–4 CSV"],
        ["<code>scripts/95_final_submission_report.py</code>", "英文 JOH", "英文 report.html / .md（请勿覆盖）"],
        ["<code>scripts/97_scienceplots_figures.py</code>", "B 配图（2026 IEEE / 英文标签）", "SciencePlots 2.2：science+ieee+no-latex，Times New Roman，英文轴注"],
        ["<code>scripts/96_research_report_zh.py</code>", "中文平行稿", "本文件：中文 HTML / MD / PDF"],
        ["<code>scripts/03–09_*.py</code>（含 --synthetic）", "A（不可引用）", "30×40 合成冒烟测试"],
    ]

    pend_h = ["编号", "事项", "为何标记「待补充」"]
    pend_r = [
        ["P1", "gpflow Sparse GP（SGPR）正式结果", "现用 sklearn GPR，与原 LSG 论文后端不同"],
        ["P2", "Brisbane（布里斯班）案例", "未运行；需昆士兰数据许可"],
        ["P3", "Chowilla 高程基准（datum）修正", "LSG 退化可能与基准/LF 质量有关，尚未做对照实验"],
        ["P4", "Chowilla 压缩包 MD5 复验", "历史上校验失败；现用已解压的 31 HF + 31 LF"],
        ["P5", "把官方 2 折当作主结论", "multifold_bootstrap.json 中 significant=false，不能当作主声称"],
        ["P6", "真实数据上的 LSG-TS", "Track B 仅为最大淹没面 LSG-Max"],
        ["P7", "gpflow Sparse GP（与 sklearn 对照）", "环境无 TensorFlow/gpflow；现用 sklearn GPR"],
        ["P7b", "Burnett 二阶 EOI 的 30 折", "已算池化 ZGG/oracle；折级仅 Carlisle 完整"],
        ["P8", "Burnett 的 KMeans 30 折 LOOCV", "计算更贵，未跑"],
        ["P9", "Burnett 全部 74 场事件", "LOOCV 用 30 场；单次划分用 12 场"],
        ["P10", "Chowilla 实际模态数", "manifest 中 modes_actual=unknown"],
        ["P11", "full31_3fold.json 与 registry 的差异", "该文件 RMSE 量级约 0.75 m，与 v4 的约 2.56 m 不一致，本文不引用"],
    ]

    # ---------- HTML sections ----------
    cover = f"""
<div class="cover">
  <div class="kicker">内部研究报告 / 与 JOH 投稿平行文档</div>
  <h1>全局 EOF 降维何时不足以支撑<br>多保真洪水淹没模拟？</h1>
  <p class="subtitle">水动力分区 LSG-Max：等模态预算、面积加权指标与训练期分区</p>
  <div class="meta">
    <p>项目路径：{escape(PROJECT_PATH)}</p>
    <p>日期：{DATE_STR}　·　文档类型：中文学术研究报告（非英文投稿稿替换件）</p>
    <p>数据登记：<code>outputs/registry/result_manifest_v4.csv</code></p>
    <p>生成脚本：<code>scripts/96_research_report_zh.py</code></p>
  </div>
</div>
"""
    toc = """
<nav class="toc" id="toc">
  <h2>目录</h2>
  <ol>
    <li><a href="#s1">摘要</a></li>
    <li><a href="#s2">研究背景与目的</a>
      <ol>
        <li><a href="#s2-0">文献脉络与投稿稿对齐</a></li>
        <li><a href="#s2-1">科学问题</a></li>
        <li><a href="#s2-2">术语约定</a></li>
      </ol>
    </li>
    <li><a href="#s3">数据与方法</a>
      <ol>
        <li><a href="#s3-1">三个案例</a></li>
        <li><a href="#s3-2">LSG-Max 与水动力分区</a></li>
        <li><a href="#s3-3">真等预算、面积加权与防泄漏</a></li>
        <li><a href="#s3-4">指标公式与残差组织</a></li>
      </ol>
    </li>
    <li><a href="#s4">研究过程</a>
      <ol>
        <li><a href="#s4-1">双轨管线</a></li>
        <li><a href="#s4-2">泄漏审计</a></li>
      </ol>
    </li>
    <li><a href="#s5">结果展示</a>
      <ol>
        <li><a href="#s5-1">Carlisle 等预算</a></li>
        <li><a href="#s5-2">事件级 LOOCV 与官方 2 折</a></li>
        <li><a href="#s5-3">三案例对照</a></li>
        <li><a href="#s5-4">Burnett 30 折与计算代价</a></li>
      </ol>
    </li>
    <li><a href="#s6">分析与讨论</a>
      <ol>
        <li><a href="#s6-1">分区何时有用</a></li>
        <li><a href="#s6-2">全局为何随模态变差</a></li>
        <li><a href="#s6-3">分区何时无益或有害</a></li>
        <li><a href="#s6-4">官方划分与 CSI</a></li>
        <li><a href="#s6-5">EOI 诊断、官方 9 折、外推、LF 加粗与主槽距离</a></li>
      </ol>
    </li>
    <li><a href="#s7">主要结论</a></li>
    <li><a href="#s8">不足与展望</a></li>
    <li><a href="#s9">附录</a>
      <ol>
        <li><a href="#s9-1">数据来源</a></li>
        <li><a href="#s9-2">脚本索引</a></li>
        <li><a href="#s9-3">待补充清单</a></li>
        <li><a href="#s9-4">合成/历史配图备查</a></li>
        <li><a href="#s9-5">参考文献</a></li>
      </ol>
    </li>
  </ol>
</nav>
"""

    s1 = f"""
<section id="s1">
<h2>1　摘要</h2>
<p class="lead">本文问的是一个很具体的方法学问题：在多保真洪水淹没代理模型里，把整个泛滥平原当作一块“均匀布”去做经验正交函数降维，是否在水动力学上保持中性？若残差在空间上是分块组织的，全局降维就可能把河道、常淹滩地与边缘浅水搅在同一组模态里，从而在模态预算紧张时学偏。</p>
<p>针对这一问题，本文在 Fraehr 等人（2024）公开基准上实现<strong>水动力分区的 LSG-Max</strong>。LSG 是「低保真—空间分析—高斯过程」（Low-fidelity, Spatial analysis, Gaussian Process）的缩写，指先用粗网格水动力模型给出快速但粗糙的淹没面，再在高保真网格上学一层修正。LSG-Max 只预测一场洪水的<strong>最大淹没水深面</strong>，而不是全时段过程。分区在经验正交函数（Empirical Orthogonal Function，EOF：把高维淹没场分解成少数空间模态与时间/事件系数）和高斯过程回归（Gaussian Process，GP：在低维系数空间学习低保真系数到高保真系数的映射）之前完成。评价使用<strong>真等模态预算 B</strong>（Global 与分区模型的总模态数相同）、<strong>面积加权指标</strong>（按网格单元面积加权，而不是把大小格子一视同仁）以及<strong>仅用训练事件做分区</strong>（检验事件不参与画区、拟合 EOF 或 GP）。</p>
<div class="kf"><strong>Carlisle（卡莱尔）主结果。</strong>在真等预算 B = 4 时，规则分区把面积加权均方根误差（Root Mean Square Error，RMSE：水深误差，单位米）从全局模型的 {fmt(G4)} m 降到 {fmt(R4)} m，相对降幅 {impr4:.1f}%。9 折事件留一交叉验证（Leave-One-Out Cross-Validation，LOOCV：每次留出一场事件做检验）中 9/9 折分区更优，ΔRMSE 均值 {fmt(L4['mean'])} m，95% 自助法区间 [{fmt(L4['ci'][0])}, {fmt(L4['ci'][1])}] m。历史<strong>时序</strong>残差组织指数为 {eoi_ts:.2f}；与 LSG-Max 同一协议的<strong>最大淹没面</strong> EOI 仅为 {eoi_c:.3f}。全局模型随 B 增大而变差（{fmt(G4)} → {fmt(G6)} → {fmt(G8)} m），规则分区更稳健（{fmt(R4)} → {fmt(R6)} → {fmt(R8)} m）。</div>
<div class="warn"><strong>官方 2 折并不显著。</strong>Fraehr 官方两折划分上的自助法给出平均 ΔRMSE = {fmt(official['mean_delta_rmse'])} m，95% 区间 [{fmt(official['ci_95_lower'])}, {fmt(official['ci_95_upper'])}]，<code>significant=false</code>。这是小样本官方划分的局限，不是把不显著结果改写成显著。事件级 9 折 LOOCV 才是本文的统计主声称。</div>
<div class="warn"><strong>Burnett 30 折：分区没有帮忙。</strong>B = 4 时，30 折平均全局 RMSE {fmt(bloo['mean_global_rmse'])} m，规则分区 {fmt(bloo['mean_zonal_rmse'])} m，平均 ΔRMSE = {fmt(bloo['mean_delta_rmse'])} m（负值表示分区更差），仅 {bloo['n_improved']}/{bloo['n_folds']} 折分区更好，区间 [{fmt(bloo['ci_95_lower'])}, {fmt(bloo['ci_95_upper'])}]，<code>significant=false</code>。最大面 EOI 却高达 {eoi_bmax:.3f}：一阶残差成块<strong>并不保证</strong>等预算分区 EOF 获益。</div>
<p>Chowilla（乔维拉）是边界情形：LSG 的 RMSE 约 {fmt(ch_g)} m，而仅用低保真（Low-Fidelity，LF：粗网格或简化水动力模型）为 {fmt(ch_lf)} m。低保真网格仅 1,434 格，相对高保真（High-Fidelity，HF）约 77:1。本文<strong>不把 Chowilla 写成成功案例</strong>。高斯过程后端是 scikit-learn 的 GPR，不是 gpflow 的稀疏高斯过程（SGPR），这一点记为方法局限。</p>
</section>
"""

    s2 = f"""
<section id="s2">
<h2>2　研究背景与目的</h2>
<h3 id="s2-0">2.1　文献脉络：对照英文投稿稿补上的“为什么要做”</h3>
<p>英文 JOH 稿把问题写成一句：经验正交函数降维在多保真淹没模拟里是不是水动力中性的。中文研究报告若只复述数字表，会丢掉原稿的问题意识。本节按投稿稿的论证顺序补全来龙去脉，不增加未登记的实验。</p>
<p>Fraehr 等人（2022, 2023, 2024）建立了 LSG：对高保真淹没场做经验正交函数，把低保真场投影到同一空间基，再用高斯过程学习系数映射。公开基准见 Figshare 24312658。Wang 等人（2026）在《Water Resources Research》中比较了全时段 LSG-TS 与最大面 LSG-Max，指出复杂泛滥平原上最大面变体更稳、也更贴近预警常用的峰值淹没。英文稿的创新点不是再发明一种高斯过程，而是问：<strong>全局经验正交函数把河道、滩地与边缘浅水绑在同一组模态里，是否已经在降维阶段丢掉了水动力结构？</strong></p>
<p>对照英文稿，此前中文稿缺了三块现在一并补上：（1）面积加权均方根误差、临界成功指数与残差组织指数的定义式；（2）训练期分区平均绝对残差（深槽相对边缘约 25 倍）——这是“为什么分区”的机制表；（3）讨论按“何时有用 / 为何加模态会变差 / 何时无益”三条展开，而不是把三案例揉成一段。卷期页码若仓库未收录，参考文献中标【待补充】，不编造 DOI。</p>
<h3 id="s2-1">2.2　科学问题</h3>
<p>细网格二维水动力模型可以给出可信的淹没水深与范围，但单场洪水往往要算数小时到数日，难以支撑预警、规划中的大批量情景。多保真思路是：用便宜的低保真模型先跑出一张“轮廓”，再用少量高保真样本学习两者之间的系统偏差，从而在新情景上快速逼近高保真结果。</p>
<p>Fraehr 等人把这一思路写成 LSG：对高保真淹没场做 EOF 降维，把低保真场投影到同一套空间基上得到伪展开系数，再用 GP 学习「低保真系数 → 高保真系数」。代理一旦离线训练好，新一场低保真模拟可以在数秒内映射成高保真风格的淹没面。Wang 等人（2026）在复杂泛滥平原上比较了 LSG-TS（全时段序列）与 LSG-Max（最大面）等变体。</p>
<p>若低保真相对高保真的残差在空间上成块，全局模态就可能把不同力学区的信号平均掉——但这只是<strong>动机</strong>，不是充分条件。一阶 EOI（最大面）事后被证明不能单独预测分区增益。本文的问题因此可以写成一句：</p>
<div class="note"><strong>核心问题：</strong>当模态预算 B 被公平地限制、指标按面积加权、分区只用训练事件时，全局 EOF 降维在什么条件下已经不够，而水动力分区能够稳定地降低水深 RMSE？</div>
<p>相应的工作假说原先写成：分区收益是<strong>一阶残差空间组织 × 有限模态容量</strong>的合取。最大面 EOI 重算后，该合取被证伪为充分条件。修订叙事：Carlisle 是“分区 LSG 有用、但最大面一阶 EOI 并不高”的正例；Burnett 是“最大面一阶 EOI 极高、等预算分区仍无益”的反例；Chowilla 是“低保真与高保真匹配过差、LSG 会帮倒忙”的边界。二阶 oracle（图 19）排除“等预算纯 EOF 截断变好”；stage-swap（E13）进一步表明：在耦合的 LF→HF 管线里引入分区结构（EOF 坐标或映射局部性）即可收回几乎全部 ZZ 增益，但<strong>不能</strong>把收益唯一钉死在区私有 GP 上。</p>
<h3 id="s2-2">2.3　术语约定（首次出现时的读法）</h3>
<ul>
<li><span class="term">EOF</span>（经验正交函数，Empirical Orthogonal Function）：把多场淹没水深矩阵分解为空间模态与系数。模态数越多，重建越细，也越容易在小样本上过拟合。</li>
<li><span class="term">LSG</span>（低保真—空间分析—高斯过程）：Fraehr 框架的三步——EOF、低保真投影、GP 映射。</li>
<li><span class="term">LSG-Max / LSG-TS</span>：Max 只学最大淹没面；TS 学全时段。本文 Track B <strong>只有 Max</strong>；真实数据上的 TS 为【待补充】。</li>
<li><span class="term">GP / GPR / SGPR</span>：高斯过程回归。本文生产数字来自 sklearn GPR；gpflow SGPR 为【待补充】。</li>
<li><span class="term">RMSE</span>：水深均方根误差（m），越小越好。</li>
<li><span class="term">CSI</span>（临界成功指数，Critical Success Index）：以 0.03 m 为湿润阈值的范围命中率，越大越好。它惩罚漏报与空报。</li>
<li><span class="term">EOI</span>：残差组织指数，区间方差 / 总方差。主文只用与 LSG-Max 同协议的<strong>最大面</strong> EOI（Carlisle {eoi_c:.3f}）。历史时序 EOI 见附录 SI，不可与最大面混用。一阶 EOI 不能单独作为分区开关。</li>
<li><span class="term">LOOCV</span>：按事件留一交叉验证，避免把“碰巧分到的两场检验洪水”当成普遍规律。</li>
<li><span class="term">LF / HF</span>：低保真 / 高保真水动力模型及其网格。</li>
<li><span class="term">模态预算 B</span>：全局模型与分区模型允许使用的 EOF 模态总数上限。真等预算要求两边实际用到的总模态数对齐。</li>
<li><span class="term">规则分区 vs KMeans 分区</span>：规则按最大水深与淹没频率切出深槽、常淹、间歇、边缘；KMeans 在训练期特征上做 K=4 聚类。</li>
<li><span class="term">面积加权指标</span>：误差按网格面积加权，避免小格子与大格子被当成同等重要。</li>
<li><span class="term">ΔRMSE</span>：本文事件级统计定义为全局 RMSE 减分区 RMSE。正值表示分区更好；Burnett 均值为负，表示分区平均更差。</li>
</ul>
</section>
"""

    s3 = f"""
<section id="s3">
<h2>3　数据与方法</h2>
<h3 id="s3-1">3.1　三个案例</h3>
<p>数据来自 Fraehr（2024）公开基准（Figshare 记录 24312658）。网格单元数来自几何文件，而不是合成 30×40 玩具网格：Carlisle 581,061 / 5,681，Chowilla 109,914 / 1,434，Burnett River 780,785 / 15,256。Carlisle 的 LF 格点数 5,681 由几何直接读取，不是凭记忆填写。</p>
{html_table(t1_h, t1_r, "表 1　案例摘要。HF/LF 格点来自 Fraehr 几何；RMSE 来自 registry v4 与对应 JSON。", "tbl1")}
<p class="tbl-explain">请这样读表 1。每一列是一个独立流域，不可把三列的 RMSE 直接比大小来论输赢：Carlisle 的误差在分米量级，Burnett 在米量级，这首先反映洪水尺度与模型结构，而不是分区算法的绝对精度。真正要横着看的是<strong>同一列内部</strong>：仅用 LF、全局 LSG、分区 LSG 谁更好。最大淹没面 EOI 已三案齐全：Carlisle {eoi_c:.3f}、Chowilla {eoi_w:.3f}、Burnett {eoi_bmax:.3f}。历史时序 EOI（Carlisle {eoi_ts:.2f}）与最大面 EOI 不是同一个量，正文 6.1 节分开解释。</p>
{html_table(t2_h, t2_r, "表 2　实验矩阵。E1–E3 共享真等预算；E4 为统计主声称；E5 必须如实写不显著；E8–E12 为本次平行推进的诊断与扩展。", "tbl2")}
<p class="tbl-explain">表 2 不是“我们跑过很多模型”的清单，而是公平比较的纪律。若全局模型可以自由取很多模态、分区模型却被限制，分区看起来更好可能只是参数更多。E1–E3 因此锁住总预算 B。E4 把“某一折上好看”升级为“每一场留出事件是否都更好”。E5 专门对应审稿人可能引用的官方 2 折：结果不显著，就写不显著。</p>
<h3 id="s3-2">3.2　LSG-Max 与水动力分区</h3>
<p>湿润阈值取 0.03 m：低于此值的格子视为干，不进入 EOF 的湿单元集合。LSG-Max 对每场洪水的最大水深面建模。规则分区（Rule）用训练期高保真最大水深的高分位数识别深槽/近河道，用淹没频率阈值划分常淹滩地、间歇滩地与边缘；若提供 LF–HF 绝对残差，还可叠加误差热点。KMeans 分区在标准化后的空间坐标、水深统计、淹没频率等特征上聚成 K=4 类。两种分区都只在训练事件上估计阈值或拟合聚类器，再映射到检验事件——这是防泄漏的核心。</p>
{fig_block(1, "全局 LSG 与分区 LSG 的流程对照（示意图）", "fig01_workflow.png",
"图1 全局与分区 LSG 流程",
"<p>左列是基线：把低保真场插值到高保真网格后，对<strong>全部湿单元</strong>做一次全局 EOF，再用一个 GP 把低保真展开系数映射到高保真系数，最后重建最大淹没面。右列是本文方法：先按水动力规则或聚类把泛滥平原切开，然后<strong>每个区自己做 EOF、自己做 GP</strong>，最后把各区重建结果拼回一张完整水面。读者不必在这张示意图里寻找 RMSE 数字——它只说明“分区发生在降维之前”，而不是发生在事后对误差地图上色。</p>"
+ "<p>为何这一点重要？若先做全局 EOF 再按区看误差，分区只是诊断，不能改变模态所张成的空间。本文把分区放进学习管线，让深槽的模态不必去解释边缘浅水的开关行为。后面所有可引用数字，都建立在右列这条路径上。</p>",
synthetic=True)}
{fig_block(2, "Carlisle 真实地形与 KMeans 四区（LISFLOOD-FP，581,061 格）", "fig02_zone_maps_real.png",
"图2 Carlisle 真实分区图",
"<p>本图来自真实 Carlisle 几何，不是 30×40 玩具网格。子图 (a) 是地形：东西向的深色河道是主输送通道，两侧黄褐为滩地与阶地。读图时先沿河道走一遍，再看南北两侧高地，心里要有“水从哪来、往哪摊”的方向感。</p>"
+ "<p>子图 (b) 是 K=4 的 KMeans 分区（仅显示湿区）。颜色块并不等于行政边界：蓝色区大致贴着主槽，粉红细带更紧地追随河道，青色大块出现在北侧连续滩地，红色区破碎，对应深浅交错的滩地。子图 (c) 给出湿单元计数：四区合计湿单元 238,946，约占 581,061 总格点的四成；0 区约 42.0%，3 区约 27.1%，1 区约 23.5%，2 区仅约 7.4%。小区不是“不重要”，而往往是水动力最特殊、全局模态最容易牺牲的地方。</p>"
+ f"<p>图题中的 |LF−HF|=0.039 m 是该次制图所用的平均绝对差量级，与表 3 中仅用 LF 的 RMSE {fmt(LF)} m 同属“低保真已经不太差、但仍有结构误差”的故事，不要把两个统计量当成同一个指标。规则分区的地图未单独成图，其物理含义见表 2 的 E2：按水深与频率切区，而不是按像素颜色聚类。</p>")}
<h3 id="s3-3">3.3　真等预算、面积加权与防泄漏</h3>
<p>真等预算的操作定义是：请求 B 个模态时，全局模型用 <code>force_n_modes</code> 对齐到 B；分区模型各区模态数之和为 B。Carlisle 在 B=8 时全局实际模态为 7（审计表记为 MISMATCH），因为方差阈值与湿单元秩限制使全局凑不满 8；分区一侧仍达到 8。比较 B=8 时应对这一不对称保持清醒：即便全局少用了 1 个模态，它的 RMSE 仍然明显更差，说明问题不是“全局模态不够多”。</p>
<p>面积加权 RMSE / CSI 使用几何面积向量，不随训练检验划分改变。湿润阈值 0.03 m 同时用于 CSI 的命中、空报、漏报计数。高斯过程为 sklearn <code>GaussianProcessRegressor</code>，不是 gpflow SGPR（【待补充】）。</p>
<h3 id="s3-4">3.4　指标公式与残差组织（对照英文稿补全）</h3>
<p>英文投稿稿把面积加权写进方法节，中文稿若只说“按面积加权”而不给式子，审稿人无法核对实现。下列符号中，<span class="term">h<sub>i</sub></span> 是高保真最大水深，<span class="term">ĥ<sub>i</sub></span> 是预测水深，<span class="term">A<sub>i</sub></span> 是第 i 个高保真格子的平面面积，全部来自几何文件，不随划分改变。</p>
<p class="eq" style="text-align:center;margin:14px 0;font-family:Cambria,'Times New Roman',serif;">
RMSE<sub>area</sub> = {{ Σ<sub>i</sub> A<sub>i</sub> (ĥ<sub>i</sub> − h<sub>i</sub>)<sup>2</sup> / Σ<sub>i</sub> A<sub>i</sub> }}<sup>1/2</sup>
</p>
<p>临界成功指数把格子先按 0.03 m 变成湿/干。命中（Hit）是两边都湿的面积，漏报（Miss）是高保真湿而预测干，空报（False Alarm，FA）相反。面积加权 CSI = Hit / (Hit + Miss + FA)。它不奖励“把已经干的地方继续判干”，因此对边缘浅水更敏感。</p>
<p>残差组织指数在<strong>训练事件</strong>上计算：先对每个湿格子求多场平均 |LF − HF|，再按规则分区把格子归入各区。分子是各区均值的方差，分母是格子级方差。EOI 接近 0 表示残差像空间白噪声，全局经验正交函数足够；EOI 高表示误差成块，分区才有力学理由。Carlisle 的 EOI = {eoi:.2f} 已写入 registry；Burnett 与 Chowilla 未算，仍标【待补充】。</p>
{html_table(t_eoi_h, t_eoi_r, "表 R　Carlisle 残差组织。EOI 与方差来自 residual_organization.csv；分区平均绝对残差引自 2026-06-07 v4 报告的训练期计算，本次未重载约 9 GB 的 HDF5，故不称为新结果。", "tblR")}
<p class="tbl-explain">请先读 EOI=0.51：大约一半的残差方差来自“区与区不同”，而不是格子间的随机抖动。v4 报告进一步给出深槽 0.245 m 对边缘 0.010 m，约 25 倍。这就是英文稿所说“全局模态必须同时迁就深槽与浅滩”的定量版本。因为分区分量没有进入当前 CSV，正文只把它当作机制说明，统计主声称仍然只依赖表 3 与表 4。</p>
</section>
"""

    s4 = f"""
<section id="s4">
<h2>4　研究过程</h2>
<h3 id="s4-1">4.1　双轨管线：哪些数字可以写进论文</h3>
<p>仓库里同时存在两条历史轨道，读者若把它们叠在一起，会得到互相矛盾的 RMSE。必须先分清。</p>
<p><strong>轨道 A（合成冒烟，scripts/03–09，<code>--synthetic</code>）。</strong>在 30×40 的玩具网格上生成高斯型洪水过程，用来在真实 HDF5 到来之前把 EOF、GP、分区、作图跑通。这些 RMSE 往往在数厘米量级，箱线图、分区柱状图、训练比例曲线多半来自这里。它们<strong>不是</strong> Fraehr 真实案例的结果，本文凡引用轨道 A 配图，都会在图注标明“不可当作论文数字”。</p>
<p><strong>轨道 B（真实数据，可引用）。</strong>Carlisle 由 <code>30_carlisle_proper.py</code> 读取 LISFLOOD-FP 高保真 npz 与 HEC-RAS HDF5 低保真；Burnett 由 <code>31_</code> 与 <code>32_</code> 读取标准网格与 30 场事件 npz；登记表由 <code>45_build_registry.py</code> 从 JSON 重建。英文投稿稿由 <code>95_final_submission_report.py</code> 生成 <code>report.html</code>。本中文报告是平行文档，不覆盖那三件英文产物。</p>
<p>Chowilla 压缩包历史上 MD5 校验失败；分析使用已解压的 31 场 HF + 31 场 LF，并保留损坏副本（Chowilla.bad）以免再次误用。本文评价子集为 12/31 场。高程基准是否错位，尚未做专门对照，故 LSG 退化的机制解释到“粗网格 LF 与可能的基准问题”为止，不往更具体的故事里编。</p>
<h3 id="s4-2">4.2　泄漏审计</h3>
{html_table(t8_h, t8_r, "表 8　Carlisle 泄漏审计摘要（outputs/audit/carlisle_leakage_audit.json）。", "tbl8")}
<p class="tbl-explain">审计文件记录时间戳 2026-08-14 21:05:55，<code>passed=true</code>。官方划分文件中训练 1893 个时间步、检验 211 步、重叠为零。分区特征、EOF 基与 GP 均不得看见检验事件。面积权来自几何。随机种子 42。若没有这一步，分区模型可能通过“用检验洪水的最大水深来画区”而偷看答案；那会把表 3 的 34.2% 变成不可信的数字。</p>
{html_table(t7_h, t7_r, "表 7　模态预算审计。Carlisle 全局 B=8 时实际模态为 7（MISMATCH）。", "tbl7")}
</section>
"""

    rise_g = (G8 - G4) / G4 * 100
    rise_r = (R8 - R4) / R4 * 100

    s5 = f"""
<section id="s5">
<h2>5　结果展示</h2>
<div class="metrics">
  <div class="metric good"><div class="v">{fmt(G4)}→{fmt(R4)}</div><div class="l">Carlisle B=4 RMSE（m）全局→规则</div></div>
  <div class="metric good"><div class="v">{impr4:.1f}%</div><div class="l">等预算相对降幅</div></div>
  <div class="metric good"><div class="v">{L4['improved']}/{L4['n']}</div><div class="l">B=4 LOOCV 改善折数</div></div>
  <div class="metric"><div class="v">{eoi:.2f}</div><div class="l">Carlisle EOI（结构化残差）</div></div>
  <div class="metric bad"><div class="v">不显著</div><div class="l">官方 2 折自助法</div></div>
  <div class="metric bad"><div class="v">{bloo['n_improved']}/{bloo['n_folds']}</div><div class="l">Burnett 分区更优的折数</div></div>
</div>
<h3 id="s5-1">5.1　Carlisle：真等预算下全局变差、分区更稳</h3>
{html_table(t3_h, t3_r, "表 3　Carlisle 真等预算面积加权 RMSE（budget_sweep_true_equal.json）。", "tbl3")}
<p class="tbl-explain">先看 B=4 这一行：全局 {fmt(G4)} m，规则 {fmt(R4)} m，KMeans {fmt(K4)} m。规则相对全局降低 {impr4:.1f}%，KMeans 也明显优于全局但略逊于规则。再看行间变化：全局从 B=4 到 B=8 升高 {rise_g:.0f}%（{fmt(G4)} → {fmt(G8)}），规则升高 {rise_r:.0f}%（{fmt(R4)} → {fmt(R8)}）。“加模态一定更好”在这个等预算实验里不成立。最后看实际模态数列：B=8 全局只有 7 个模态，分区为 8；即便给全局少算一个模态的便宜，它仍然最差。仅用 LF 的 RMSE 为 {fmt(LF)} m，全局 B=4 已经略优于仅用 LF，但规则分区的改善幅度大得多。</p>
{html_table(t3c_h, t3c_r, "表 3b　同一实验的面积加权 CSI（湿润阈值 0.03 m）。", "tbl3b")}
<p class="tbl-explain">CSI 必须单独说，避免只报 RMSE。仅用 LF 的 CSI 为 {fmt(csi['lf'])}，高于任何 LSG 变体（全局 B=4 为 {fmt(csi['g4'])}，规则为 {fmt(csi['r4'])}）。结合原始 JSON：LSG 的探测率（POD）接近 1，但空报率（FAR）高于仅用 LF。含义是：分区主要把<strong>水深数值</strong>校准得更准，同时可能把一些浅水格判湿。本文主指标仍是面积加权 RMSE；不把 CSI 写成“全面胜利”。</p>
{html_table(t_mae_h, t_mae_r, "表 3c　同一实验的面积加权平均绝对误差（MAE）与偏差（budget_sweep_true_equal.json）。", "tbl3c")}
<p class="tbl-explain">英文稿讨论“过拟合”时主要看 RMSE 随 B 上升。表 3c 把平均绝对误差与偏差补上：全局 B=4 的偏差为 {fmt(cb['budgets']['4']['global']['bias_area'])} m，B=8 变为 {fmt(cb['budgets']['8']['global']['bias_area'])} m（符号翻转并增大），说明多出来的模态不只是加细结构，而是把系统偏差推偏。规则分区的偏差始终更接近 0。这与“分区提供隐式容量约束”一致。</p>
{fig_block(3, "Carlisle 真等预算：面积加权 RMSE 随模态预算 B 的变化（SciencePlots 2.2 / IEEE）", "fig03_mode_budget.png",
"图3 真等预算 RMSE–B 曲线",
f"<p>横轴是模态预算 B=4、6、8，纵轴是面积加权 RMSE。圆点实线为全局，方点虚线为规则分区，三角点线为 KMeans。三条线都向上，但斜率不同。B=4 时三者最低点靠近：全局约 {fmt(G4)} m，KMeans 约 {fmt(K4)} m，规则约 {fmt(R4)} m。B=6 时全局已经跳到约 {fmt(G6)} m，分区仍在 0.12–0.14 m。B=8 时全局约 {fmt(G8)} m，KMeans 约 {fmt(K8)} m，规则约 {fmt(R8)} m 仍为三者最低。</p>"
+ "<p>如何用这张图回答标题中的“何时不够”？在 Carlisle、残差成块、预算有限时，<strong>增加全局模态不是补救，反而是过拟合</strong>。分区把有限的 B 个模态分配到力学更均匀的子域，相当于给每个子问题更合适的秩。KMeans 在 B=8 恶化快于规则，说明“切成四块”还不够，切的方式也要符合水深–频率结构。</p>"
+ "<p>作图规范：SciencePlots 2.2 的 <code>science+ieee+no-latex</code>，600 dpi，色盲友好循环；图内 Latin/数字为正文字体 <strong>Times New Roman</strong>，轴注与图例为英文（与英文投稿稿共用同一套 PNG）。中文报告正文解说仍为中文。横轴只标 4、6、8，与实验矩阵一致，不把曲线光滑成连续函数。</p>")}
{fig_block(4, "Carlisle 真等预算：面积加权 CSI 随 B 的变化", "fig09_csi_budget.png",
"图4 CSI–B 曲线",
f"<p>纵轴是临界成功指数，越大越好。灰点划线是仅用低保真（{fmt(csi['lf'])}），三条 LSG 曲线都在它下方。请先看 B=4：全局 {fmt(csi['g4'])}、规则 {fmt(csi['r4'])}、KMeans {fmt(csi['k4'])}，三者几乎重叠，且都低于仅用低保真。再看 B=6：KMeans 的 CSI 略升到 {fmt(csi['k6'])}，规则 {fmt(csi['r6'])}，全局落到 {fmt(csi['g6'])}。结论与表 3b 相同：分区赢在水深 RMSE，不赢在湿干范围。</p>"
+ "<p>读图时不要把 CSI 曲线的“谁在上面”直接抄进摘要当主结果。主声称仍是图 3 的 RMSE。本图的作用是防止只展示对自己有利的指标。</p>")}
{fig_block(5, "Carlisle 真等预算：平均绝对误差与偏差", "fig13_mae_bias.png",
"图5 MAE 与偏差",
"<p>左图纵轴为面积加权平均绝对误差（Mean Absolute Error，MAE：绝对误差的面积平均，对极端格子不如 RMSE 敏感）。右图纵轴为面积加权偏差（正值表示预测偏深）。左图形态与 RMSE 图相似：全局随 B 上升最快。右图更有诊断价值：全局在 B=6、B=8 变成明显的负偏差（整体偏浅），规则分区的偏差始终靠近零线。这说明多出来的全局模态不是把局部峰值补准，而是把整个水面推离高保真。</p>")}
<h3 id="s5-2">5.2　事件级 LOOCV 与官方 2 折：主声称与诚实的不显著</h3>
{html_table(t4_h, t4_r, "表 4　ΔRMSE 的事件级检验。Δ = 全局 RMSE − 分区 RMSE；正值表示分区更好。", "tbl4")}
<p class="tbl-explain">表 4 把四种协议放在同一口径下。Carlisle B=4：9/9 折改善，均值 {fmt(L4['mean'])} m，区间 [{fmt(L4['ci'][0])}, {fmt(L4['ci'][1])}]，不含 0。B=6：7/9 折改善，区间仍不含 0，但均值从 {fmt(L4['mean'])} 降到 {fmt(L6['mean'])}，与“更大 B 并不自动更好”一致。官方 2 折：平均 Δ 只有 {fmt(official['mean_delta_rmse'])} m，区间跨过 0，<code>significant=false</code>。Burnett 30 折：均值 {fmt(bloo['mean_delta_rmse'])} m，区间跨过 0，仅 {bloo['n_improved']}/{bloo['n_folds']} 折分区更好。自助法重复 10,000 次、种子 42，与英文稿 <code>95_*.py</code> 相同。</p>
{html_table(t6_h, t6_r, "表 6　Carlisle B=4 九折 LOOCV 逐事件 RMSE（loocv_results.json）。", "tbl6")}
<p class="tbl-explain">逐事件看，分区在每一折都更低。事件 1 是全局的灾难点：全局 RMSE {fmt(L4['items'][1]['global_rmse'])} m，规则分区 {fmt(L4['items'][1]['zonal_rmse'])} m，单折 Δ 约 {fmt(L4['items'][1]['delta_rmse'])} m。若只做官方 2 折且不幸没抽到这类事件，均值会被拉平——这正是表 4 里官方 2 折不显著、9 折显著可以同时成立的原因。事件 0、4、7 上两者都已经很小（约 0.05–0.07 m），分区仍有分厘米级改善，但不是故事的主角。</p>
{fig_block(6, "Carlisle 九折事件 LOOCV（B=4）：逐场 RMSE", "fig08_per_event_bootstrap.png",
"图6 Carlisle LOOCV 折线",
"<p>横轴是被留出的事件编号 0–8，纵轴是该折检验事件的面积加权 RMSE。实线圆点为全局 B=4，虚线方点为规则分区 B=4。请逐点确认分区线始终在全局线下方，这对应表 6 的 9/9。</p>"
+ f"<p>事件 1 的全局尖峰（约 {fmt(L4['items'][1]['global_rmse'])} m）是读图关键：全局经验正交函数在某一场洪水上会把误差放大到接近 0.7 m，而分区把同一场压回约 {fmt(L4['items'][1]['zonal_rmse'])} m。其余八场两条线较近，但方向一致。本图按 IEEE 轴样式重绘，文件名仍含 bootstrap，实际绘制的是逐折 RMSE；区间数字以表 4 与图 8 为准。</p>")}
{fig_block(7, "Carlisle B=4：全局 RMSE 对规则分区 RMSE（1:1 散点）", "fig11_loocv_scatter.png",
"图7 LOOCV 1:1 散点",
"<p>每个点是一场留出事件。横轴全局 RMSE，纵轴规则分区 RMSE。虚线是 1:1。点若落在虚线下方，表示分区更好。九个点全部在下方，且事件 1 远离原点，说明改善不是“每场都小幅磨一点”，而是包含一场全局失败被分区救回。等轴比例避免把 0.05 m 与 0.7 m 的点视觉上压扁。</p>")}
{fig_block(8, "四种检验协议下平均 ΔRMSE 及其 95% 区间", "fig12_stat_ci.png",
"图8 森林图",
f"<p>横轴是平均 ΔRMSE（全局减分区），竖虚线为 0。须向右表示分区更好，须向左表示分区更差；须若跨过 0，则该协议下不能声称显著。自上而下：Carlisle B=4 的须完全在 0 右侧（[{fmt(L4['ci'][0])}, {fmt(L4['ci'][1])}]）；B=6 仍在右侧但更靠近 0；官方 2 折紧贴 0 且跨线；Burnett 30 折均值在左侧但须跨 0。这张图把表 4 四行画成一眼能读的“谁能当主声称”。</p>"
+ "<p>英文稿把官方 2 折写进摘要，就是为了对应这张图的第三行：不是藏起来，而是让读者看见检验力不足。</p>")}
<div class="warn"><strong>不要把官方 2 折写成“也显著”。</strong>四场检验事件中 3/4 分区更好（improved_fraction=0.75），但均值只有 {fmt(official['mean_delta_rmse'])} m，95% 区间 [{fmt(official['ci_95_lower'])}, {fmt(official['ci_95_upper'])}] 包含 0。n 太小，检验力不足。本文明确：官方 2 折<strong>不是</strong>主声称。</div>
<h3 id="s5-3">5.3　三案例：成功、无增益、帮倒忙</h3>
{html_table(t5_h, t5_r, "表 5　三案例面积加权 RMSE（registry v4）。Chowilla 为边界情形。", "tbl5")}
<p class="tbl-explain">表 5 是全文的“地图”。Carlisle：分区 &gt; 全局 &gt; 仅用 LF（就 RMSE）。Burnett 12 事件单次划分：全局 {fmt(b_g)} m 与规则 {fmt(b_r)} m 几乎相同，二者都明显低于仅用 LF 的 {fmt(b_lf)} m——LSG 有用，但分区没有额外好处。Chowilla：仅用 LF {fmt(ch_lf)} m，LSG 约 {fmt(ch_g)} m，差一个数量级。把三列都说成“分区成功”会直接与数据冲突。</p>
{fig_block(9, "三案例面积加权 RMSE（registry v4 / SciencePlots）", "fig04_three_case.png",
"图5 三案例柱状图",
f"<p>每组三根柱：蓝为仅用 LF，橙为全局 LSG（B=4，Burnett 全局强制 B=4 与分区等容量），绿为规则分区 B=4。Carlisle 组最矮，绿柱明显低于橙柱与蓝柱，对应 {fmt(LF)} / {fmt(G4)} / {fmt(R4)} m。Chowilla 组蓝柱约 {fmt(ch_lf)} m，橙绿两柱冲到约 2.56 m，几乎重叠——分区救不了低保真与高保真之间的结构性错位。Burnett 组蓝柱约 {fmt(b_lf)} m，橙绿都在约 1.61 m，肉眼难分。</p>"
+ "<p>纵轴到 2.5 m 是为了容纳 Chowilla 与 Burnett；因此 Carlisle 的 0.05 m 级差异看起来很小，必须回到表 3 读精确值。本图来自 registry，属于可引用配图。</p>")}
{html_table(t9_h, t9_r, "表 9　Chowilla 预算扫描（budget_sweep_full.json）。LSG 在 B=4/8/12 均约 2.56 m。", "tbl9")}
<p class="tbl-explain">无论 B 取 4、8 还是 12，全局、规则、KMeans 都停在约 2.56 m，CSI 约 0.26，而仅用 LF 的 CSI 为 {fmt(d['ch_full']['lf_only']['csi_area'])}。加模态、换分区都改变不了“LSG 重建面远离高保真”这一事实。粗网格 1,434 格相对 109,914 格约 77:1；JSON 备注写明会产生极端水位。加上历史上 MD5 失败与未做的基准修正，Chowilla 只作为边界情形。</p>
{html_table(t10_h, t10_r, "表 10　Burnett River：12 事件单次划分与 30 折 LOOCV。", "tbl10")}
<p class="tbl-explain">上五行为 <code>validation_std.json</code>（9 训 3 检，780,785 格）。全局与两个 B=4 分区模型的 RMSE 都在 1.612 m 左右，规则与 KMeans 在该划分上数值重合，说明此次切分下分区几乎没有改变预测。30 折均值则显示规则略差（{fmt(bloo['mean_zonal_rmse'])} vs {fmt(bloo['mean_global_rmse'])}）。30 折 CSI 已由逐折 <code>csi_area</code> 平均补上：全局 {fmt(d['bloo_means']['csi_g'])}，规则 {fmt(d['bloo_means']['csi_z'])}，仅用 LF {fmt(d['bloo_means']['csi_lf'])}。两套协议都支持同一句话：在 Burnett，分区不是必要补丁。</p>
<h3 id="s5-4">5.4　Burnett 30 折逐场曲线与 Carlisle 计算代价</h3>
{fig_block(10, "Burnett River 30 折事件 LOOCV（B=4）", "fig10_burnett_loocv.png",
"图10 Burnett 逐场 RMSE",
f"<p>横轴 0–29 为留出事件，纵轴面积加权 RMSE。与 Carlisle 图 6 对照着读：这里两条线纠缠，分区并不系统更低，若干场上分区明显高于全局。平均后全局 {fmt(bloo['mean_global_rmse'])} m、规则 {fmt(bloo['mean_zonal_rmse'])} m，对应表 4 最后一行的负 Δ 与跨 0 区间。纵轴到数米，是洪水尺度使然，不要和 Carlisle 的 0.1 m 级纵轴直接比绝对高度。</p>"
+ "<p>若残差在空间上不像河道那样成条带，切开四区只会把本已有限的事件样本切碎。本图是“负例”的主图，不是失败的实验记录。</p>")}
{fig_block(11, "Carlisle 精度–耗时：规则 B=4 位于较优前沿", "fig08_runtime.png",
"图11 精度与运行时间",
f"<p>横轴为训练+预测时间（秒），纵轴为面积加权 RMSE。叉号为仅用低保真，接近 0 秒、RMSE 约 {fmt(LF)} m。全局约 0.7–0.9 秒、B=4 时约 {fmt(G4)} m。规则 B=4 约 1.3 秒、RMSE 约 {fmt(R4)} m，是“稍慢一点、明显更准”的点；规则 B=8 时间相近但 RMSE 升到约 {fmt(R8)} m。KMeans 在 7–9 秒，B=4 精度接近规则，B=8 则又慢又差。</p>"
+ f"<p>JSON 中的墙钟时间可与此对照：B=4 全局 {fmt(cb['budgets']['4']['global']['time_s'], '.2f')} s，规则 {fmt(cb['budgets']['4']['rule']['time_s'], '.2f')} s，KMeans {fmt(cb['budgets']['4']['kmeans']['time_s'], '.2f')} s。规则分区几乎不增加计算负担。本图按 IEEE 样式重绘，可引用其定性结论。合成管线遗留图见附录 9.4，不进入结果节。</p>")}
</section>
"""

    s6 = f"""
<section id="s6">
<h2>6　分析与讨论</h2>
<p>英文投稿稿的讨论分三问：分区何时提供价值、全局为何随额外模态变差、分区何时无必要甚至有害。中文稿此前把三案例揉成一段，下面按原稿结构展开，所有数字仍只来自 Track B。</p>
<h3 id="s6-1">6.1　何时分区经验正交函数提供价值</h3>
<p>条件原先写成合取：残差空间成块（EOI 高）且总模态容量被公平限制。本次把 EOI 按<strong>与 LSG-Max 相同的最大淹没面</strong>重算后，合取式被证伪为充分条件：Carlisle 最大面 EOI 仅 {eoi_c:.3f}（低），分区仍然把 RMSE 从 {fmt(G4)} m 降到 {fmt(R4)} m（{impr4:.1f}%），9/9 折改善；Burnett 最大面 EOI 高达 {eoi_bmax:.3f}（高），30 折规则分区却不优于全局。历史时序 EOI = {eoi_ts:.2f} 仍说明 Carlisle 的<strong>过程残差</strong>按区成块（v4 训练期深槽 0.245 m 对边缘 0.010 m），但它度量的不是 LSG-Max 所拟合的那张最大面。一阶区间方差（EOI）太粗，抓不住“各区 EOF 子空间是否不同”。</p>
<p>规则分区略优于 KMeans（{fmt(R4)} vs {fmt(K4)} m），说明切区应当像水流结构（水深与淹没频率），而不是只像像素聚类。英文稿把这一点叫作“水动力分区”，不是“任意聚类”。</p>
<h3 id="s6-2">6.2　为何全局模型会随额外模态变差</h3>
<p>强迫全局使用 B=8 个模态，RMSE 从 {fmt(G4)} m 升到 {fmt(G8)} m（+{rise_g:.0f}%），偏差由略正变为 {fmt(cb['budgets']['8']['global']['bias_area'])} m。这是经典过拟合：多出来的模态在训练事件上解释噪声，检验事件上变成系统偏差。规则分区把同一笔 B 分到各区且每区至少 1 个模态，相当于给每个子问题加上秩约束，因此同一区间只升高 {rise_r:.0f}%（{fmt(R4)} → {fmt(R8)} m）。英文稿称之为<strong>隐式正则</strong>：分区不是多给参数，而是不许全局把容量花在错误的方向上。审计表显示全局 B=8 实际只有 7 个模态，即便少用 1 个，它仍然最差，所以不能用“模态不够”来开脱。</p>
<h3 id="s6-3">6.3　何时分区无必要或有害</h3>
<p><strong>一阶残差成块但分区仍失败：Burnett。</strong>12 事件单次划分上全局与规则 RMSE 为 {fmt(b_g)} 与 {fmt(b_r)} m；30 折留一交叉验证上规则平均更差（{fmt(bloo['mean_zonal_rmse'])} vs {fmt(bloo['mean_global_rmse'])} m），仅 {bloo['n_improved']}/{bloo['n_folds']} 折占优，区间跨 0。最大面 EOI = {eoi_bmax:.3f}，深槽区平均 |LF−HF| 约 3.99 m、边缘约 0.07 m——误差极度成块，但等预算 B=4 把总秩切成每区约 1 个模态，无法消化米级偏差。高 EOI 在这里度量的是<strong>低保真系统性偏移的空间组织</strong>，不是“分区 EOF 能修好它”。</p>
<p><strong>低保真与高保真匹配失败：Chowilla。</strong>仅用低保真 {fmt(ch_lf)} m 并不荒唐；LSG 约 {fmt(ch_g)} m 说明在错误流形上做高斯过程会把水面推离高保真。最大面 EOI = {eoi_w:.3f}（低），与“分区改变不了错误流形”一致。临界成功指数从约 0.88 掉到约 0.26。网格比约 77:1。英文稿把 Chowilla 写成边界条件：LSG 需要低保真仍能抓住主导地形。</p>
<h3 id="s6-4">6.4　官方 2 折、CSI 与投稿策略</h3>
<p>官方两折只有四场检验事件，平均 ΔRMSE = {fmt(official['mean_delta_rmse'])} m，区间跨 0。事件 1 那种半米级差异若没被抽中，显著性就消失。这是功效问题。英文稿因此把 9 折作为统计主声称，并把 2 折不显著写进摘要——中文稿保持同一纪律。</p>
<p>Carlisle 上 RMSE 大降、CSI 却略低于仅用低保真。LSG 倾向宁湿勿干。若产品形态是淹没范围多边形，仅用低保真在 Carlisle 仍有竞争力。主指标选 RMSE，是因为假说针对局部水深结构，不是二值湿干图。</p>
<h3 id="s6-5">6.5　EOI 诊断、官方 9 折、外推、LF 加粗与主槽距离</h3>
<p>下列结果全部来自本次平行实验（scripts/40–44、46），JSON 在 <code>outputs/evaluation/</code>。最大面一阶 EOI 与已有 9/30 折 ΔRMSE 的折级相关分别为 Carlisle −0.58、Burnett −0.43：EOI 更高的折并不对应更大的分区增益。</p>
{fig_block(14, "三案例最大淹没面残差组织指数", "fig14_eoi.png",
"图14 三案例 EOI",
f"<p>横虚线为预先设定的高结构阈值 0.30。Burnett {eoi_bmax:.3f} 远高于阈值，Chowilla {eoi_w:.3f} 与 Carlisle {eoi_c:.3f} 低于阈值。若以该图为先验筛选，会预测 Burnett 该分区、Carlisle 不该分区——与表 3 / 30 折 LOOCV 恰好相反。因此一阶 EOI 只能作为残差地图的描述统计，不能单独充当“是否分区”的开关。</p>")}
{fig_block(15, "折内训练期 EOI 与规则分区 ΔRMSE", "fig15_eoi_vs_delta.png",
"图15 EOI 对增益散点",
"<p>纵轴为正表示分区优于全局。点云不呈正斜率。这是对“高 EOI → 分区获益”的直接否证（在最大面、等预算 B=4 协议下）。</p>")}
{html_table(t_modal_h, t_modal_r, "表 E8b　二阶模态诊断：区–全局解释方差缺口（ZGG）与等预算纯 EOF 重建（无 GP）。正 ΔRMSE 表示分区更好。", "tblE8b") if t_modal_r else ""}
{fig_block(19, "二阶诊断：ZGG 与等预算纯 EOF", "fig19_modal_eoi.png",
"图19 模态 EOI",
"<p>三案例 ZGG 均为正：各区局部基解释的方差高于同秩全局基在该区的限制。但等预算纯 EOF 重建的 ΔRMSE 均为<strong>负</strong>（Carlisle −0.076 m，Burnett −0.198 m，Chowilla −0.066 m）——把总预算 B=4 切开会损失全局秩。因此 Carlisle 上 LSG 分区的增益来自<strong>分区 GP（低保真→高保真系数映射）</strong>，而不是来自“分区 EOF 把高保真场重建得更好”。Carlisle 折级 corr(ZGG, LSG ΔRMSE)=+0.36，弱正相关，仍不足以当开关。</p>")}
{html_table(t_off_h, t_off_r, "表 E9　官方 9 折（一场一折）上已发表五模型的最大水深 R² / CSI，对照本文 LSG-Max。已发表 RMSE 为湿网格时序指标，不可与 LSG-Max 的面积加权 RMSE 混比。", "tblE9") if t_off_r else ""}
{fig_block(16, "官方湿网格上的最大水深 R²", "fig16_official_maxwd_r2.png",
"图16 官方协议 MaxWD R2",
"<p>已发表 LSG-TS 的最大水深 R² 为 0.990。本文规则分区 LSG-Max 为 0.988，在最大面协议上接近其时序模型；全局 LSG-Max 被事件 1 拉到 0.915。CSI 上已发表 LSG-TS（0.937）仍高于本文规则分区（0.905），因其另有独立的淹没范围模型。</p>")}
<p>外推事件 p10（50%）与 p11（100%）的高保真真值从原始 NPZ 重算；库内 <code>MaxWD[:,0]</code> 两场完全相同，已弃用。训练期湿网格 239,482 格，官方外推湿网格 290,458 格（+21.3%）。p10 上规则分区面积加权 RMSE 0.609 m、训练湿网格 R² 0.735，全局为 1.085 m / 0.104；p11 上规则 1.124 m、全局 1.633 m（R² 为负）。分区改善外推，但绝对误差仍远大于插值事件，且两场上仅用 LF 的面积加权 RMSE 约 0.10 m——外推时 LSG-Max 尚未打败低保真。湿掩膜放宽后 R² 上升，因为多进来的格子更容易被“预测为干/浅”蒙对；比较外推必须预先登记掩膜，不能事后选用。</p>
{html_table(t_deg_h, t_deg_r, "表 E11　Carlisle 低保真网格空间加粗（B=4，7/2 划分，种子 42）。", "tblE11") if t_deg_r else ""}
{fig_block(17, "低保真网格加粗后的面积加权 RMSE", "fig17_lf_degradation.png",
"图17 LF 分辨率退化",
"<p>×1：仅用 LF 0.160 m，全局 0.146 m，规则 0.094 m。×2：LF 恶化到 0.274 m，规则几乎不动（0.094 m）。×4：LF 0.667 m，规则 0.103 m。分区 LSG 对低保真网格变粗不敏感，因为 EOF+GP 学的是系统偏差，不是复制低保真细节。</p>")}
{html_table(t_ch_h, t_ch_r, "表 E12　距 Carlisle_MCL 主槽线的物理分区（同一 7/2 划分）。", "tblE12") if t_ch_r else ""}
{fig_block(18, "主槽距离分区与规则分区", "fig18_channel_distance.png",
"图18 主槽距离",
"<p>规则+主槽距离 0.094 m，略优于纯规则 0.096 m；仅用距离四分位带 0.112 m，仍明显优于全局 0.146 m。物理河道距离不使用检验期残差，泄漏风险低于残差热点叠加，是可公开复现的备选切区。</p>")}
</section>
"""

    s7 = f"""
<section id="s7">
<h2>7　主要结论</h2>
<ol>
<li><strong>在 Carlisle、真等预算 B=4 时，全局 EOF 降维不是水动力中性的。</strong>规则分区将面积加权 RMSE 从 {fmt(G4)} m 降至 {fmt(R4)} m（{impr4:.1f}%），9/9 折 LOOCV 改善。时序 EOI = {eoi_ts:.2f}；最大面 EOI = {eoi_c:.3f}，二者不可混用。</li>
<li><strong>用分区消化有限容量，比把全局 B 加大更稳健。</strong>全局 {fmt(G4)} → {fmt(G8)} m（+{rise_g:.0f}%），规则 {fmt(R4)} → {fmt(R8)} m（+{rise_r:.0f}%）。加模态不是自动正则。</li>
<li><strong>收益依案例而定；最大面 EOI 不能单独预测分区增益。</strong>Chowilla EOI={eoi_w:.3f}（低）且 LSG 相对仅用 LF 退化（约 {fmt(ch_g)} vs {fmt(ch_lf)} m）。Burnett EOI={eoi_bmax:.3f}（高）但 30 折规则不优于全局（ΔRMSE {fmt(bloo['mean_delta_rmse'])} m，{bloo['n_improved']}/{bloo['n_folds']}，区间含 0）。</li>
<li><strong>官方 2 折自助法不显著，不能当作主声称。</strong>均值 {fmt(official['mean_delta_rmse'])} m，区间跨 0。事件级 9 折才是可辩护的统计陈述。</li>
<li><strong>官方 9 折最大水深 R²：</strong>规则分区 LSG-Max 0.988，已发表 LSG-TS 0.990；全局 LSG-Max 0.915。CSI 上已发表 LSG-TS 仍高（0.937 vs 0.905）。</li>
<li><strong>外推、LF 加粗、主槽距离：</strong>分区改善 p10/p11 相对全局，但未击败仅用 LF；规则分区对 LF 网格×2/×4 加粗稳健；主槽距离带可替代残差热点，规则+距离 0.094 m 略优于纯规则 0.096 m。</li>
<li><strong>二阶模态诊断：</strong>三案例 ZGG&gt;0 但等预算纯 EOF 的 ΔRMSE&lt;0。Carlisle 分区 LSG 的好处来自分区 GP，不是来自更好的 HF-EOF 截断。</li>
</ol>
</section>
"""

    s8 = f"""
<section id="s8">
<h2>8　不足与展望</h2>
<ul>
<li><strong>GP 后端：</strong>sklearn GPR，而非原 LSG 论文的 gpflow SGPR。诱导点稀疏化是否改变表 3，【待补充】。</li>
<li><strong>仅有 LSG-Max：</strong>真实数据上的分区 LSG-TS【待补充】。合成箱线图中的 TS 不可替代。</li>
<li><strong>Chowilla：</strong>MD5 历史上失败；基准修正实验未做；<code>modes_actual=unknown</code>；另有 <code>full31_3fold.json</code> 与 registry 量级冲突，未采信。</li>
<li><strong>Burnett：</strong>未跑 KMeans 30 折；未用满 74 场。最大面 EOI 已算（0.957）。</li>
<li><strong>Brisbane：</strong>未运行【待补充】。</li>
<li><strong>官方 2 折：</strong>检验力不足。未来若要与 Fraehr 原文完全对齐，需要更多折或预先登记的多折协议，而不是把当前不显著结果解释成显著。</li>
<li><strong>CSI：</strong>水深变准不等于范围变准。后续可把空报格的空间分布作为分区是否过湿的诊断。</li>
<li><strong>配图：</strong>正文可引用图已按 SciencePlots 2.2（<code>science+ieee+no-latex</code>、Times New Roman、英文轴注、600 dpi）重绘；中文报告以中文图题/解说嵌入同一套英文标签图。附录 9.4 的合成图未重绘，仅作历史备查。</li>
<li><strong>分区分量残差：</strong>深槽 0.245 m / 边缘 0.010 m 引自 v4 报告训练期，未在本次重载 HDF5 复核，机制讨论可用，不作为新的独立实验。</li>
<li><strong>外推：</strong>LSG-Max 在 p10/p11 上未击败仅用 LF；与已发表 LSG-TS 外推不是同一协议。</li>
<li><strong>模态诊断：</strong>二阶 ZGG 与等预算纯 EOF oracle 已写入 <code>modal_eoi.json</code>。结论是分区增益在 GP 映射，不在纯 EOF 截断。零填充主角度因支撑不相交恒为 90°，已弃用。</li>
<li><strong>GP 后端：</strong>sklearn GPR；gpflow/TensorFlow 未装入本环境【待补充】。</li>
</ul>
<p>展望上，最有信息量的下一步是：(1) 用区际 EOF 子空间夹角代替一阶 EOI；(2) 在 gpflow 稀疏高斯过程下重跑 Carlisle B=4；(3) 若数据许可，把假说拿到 Brisbane 作预注册式检验；(4) 外推协议预先登记湿掩膜，并与仅用 LF 公平对比。</p>
</section>
"""

    s9 = f"""
<section id="s9">
<h2>9　附录</h2>
<h3 id="s9-1">9.1　数据来源</h3>
<ul>
<li>Fraehr 等（2024）多保真洪水基准，Figshare 24312658。</li>
<li>方法来源：Fraehr 等（2022, 2023, 2024）LSG；Wang 等（2026）WRR 中的 LSG-TS / LSG-Max。</li>
<li>数字登记：<code>outputs/registry/result_manifest_v4.csv</code>、<code>residual_organization.csv</code>（三案例最大面 EOI）、<code>mode_budget_audit.csv</code>。</li>
<li>Carlisle：<code>budget_sweep_true_equal.json</code>、<code>loocv_results.json</code>、<code>official_fold_zonal.json</code>、<code>extrap_zonal.json</code>、<code>lf_degradation.json</code>、<code>distance_to_channel.json</code>。</li>
<li>EOI：<code>outputs/evaluation/eoi/eoi_all.json</code>。</li>
<li>Burnett：<code>validation_std.json</code>（12 事件）、<code>loocv_results.json</code>（30 折）。</li>
<li>Chowilla：<code>budget_sweep.json</code> 与 <code>budget_sweep_full.json</code>。</li>
<li>审计：<code>outputs/audit/carlisle_leakage_audit.json</code>（CLEAN_PASS）。</li>
<li>表格 CSV：<code>outputs/tables/table01–04_*.csv</code>（由 registry 再生；表 1 格点 581061 / 109914 / 780785，Carlisle LF=5681）。</li>
<li>英文平行稿：<code>report.md</code> / <code>report.html</code>（本脚本不覆盖）。</li>
</ul>
<h3 id="s9-2">9.2　脚本索引</h3>
{html_table(scripts_h, scripts_r, "表 11　脚本索引。轨道 A 的合成结果不可引用。", "tbl11")}
<p>复现配图与中文报告（不重新训练模型）：</p>
<pre style="background:#f4f6f8;padding:12px;overflow:auto;font-size:0.85em;">D:\\miniforge3\\envs\\hydromodel\\python.exe scripts\\97_scienceplots_figures.py
D:\\miniforge3\\envs\\hydromodel\\python.exe scripts\\96_research_report_zh.py</pre>
<h3 id="s9-3">9.3　待补充清单</h3>
{html_table(pend_h, pend_r, "表 12　凡表中事项均未在本文中编造数字。", "tbl12")}
<h3 id="s9-4">9.4　合成或历史配图备查（不可引用数字）</h3>
<p>下列 PNG 来自轨道 A 或与真等预算冲突的历史作图，按“有图即嵌、结果节不出现”处理。不要把图上的 0.07 m 或 “+25.4%” 抄进摘要。</p>
{fig_block("A1", "EOF 累计解释方差：全局 vs 分区（合成/示意）", "fig03_eof_variance.png",
"附图 A1 EOF 解释方差",
"<p>纵轴为累计解释方差 0–1，横轴为模态数 1–50，灰虚线为 99% 阈值。教学含义是分区后局部场更简单。真实等预算锁在 B=4/6/8，不能用本图声称 Carlisle 需要 38 个全局模态。</p>",
synthetic=True)}
{fig_block("A2", "多模型 RMSE 与 CSI 箱线（合成管线，含 LSG-TS）", "fig04_metric_boxplots.png",
"附图 A2 合成箱线图",
"<p>图上出现了真实 Track B 没有作为主结果的 LSG-TS。真实数据上的全时段分区为【待补充】。不要用本图中位数替换表 3。</p>",
synthetic=True)}
{fig_block("A3", "分区分 RMSE（合成示意）", "fig06_zone_metrics.png",
"附图 A3 分区误差分解（合成）",
"<p>热点区相对降幅最大的方向与假说一致，但柱上数值来自 30×40 合成网格，不是 581,061 格的面积加权结果。</p>",
synthetic=True)}
{fig_block("A4", "历史预算图（与真等预算冲突）", "fig07_budget_zones.png",
"附图 A4 历史预算图",
f"<p>左图全局几乎水平停在约 0.13 m，而真等预算中全局从 {fmt(G4)} 升到 {fmt(G8)}。请以正文图 3 与表 3 为准。</p>",
conflict=True)}
{fig_block("A5", "训练样本比例（合成 Carlisle）", "fig07_training_size.png",
"附图 A5 训练比例曲线",
f"<p>JSON 中全局 RMSE 约 0.03–0.05 m，与真实 Carlisle 仅用低保真的 {fmt(LF)} m 不在同一实验。不能用来声称真实案例上分区更样本高效。</p>",
synthetic=True)}
<h3 id="s9-5">9.5　参考文献</h3>
<ol>
<li>Fraehr, N., et al. (2022). Physics-guided multi-fidelity flood inundation emulation (LSG). 期刊卷期页【待补充】。</li>
<li>Fraehr, N., et al. (2023). LSG 方法后续发展。期刊卷期页【待补充】。</li>
<li>Fraehr, N., et al. (2024). 多保真洪水淹没公开基准。University of Melbourne Figshare，记录 24312658。</li>
<li>Wang, et al. (2026). LSG-TS and LSG-Max for complex floodplains. <em>Water Resources Research</em>. 卷期页【待补充】。</li>
<li>本仓库英文平行稿：<code>report.md</code>（由 <code>scripts/95_final_submission_report.py</code> 生成）。</li>
</ol>
<p class="footer-note">生成日期 {DATE_STR}。打开方式：用浏览器直接双击 <code>研究报告.html</code> 或 <code>research_report.html</code>（无需联网）。正文中文可用 Microsoft YaHei / 宋体；图内字体为 Times New Roman（英文标签）。英文 JOH 稿件仍为 <code>report.html</code>。正文图由 <code>scripts/97_scienceplots_figures.py</code> 按 SciencePlots 2.2 IEEE + Times New Roman 规范绘制。</p>
</section>
"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>全局 EOF 降维何时不足以支撑多保真洪水淹没模拟？— 内部研究报告</title>
<style>
{CSS}
</style>
</head>
<body>
<div class="running">内部研究报告 · 水动力分区 LSG-Max · {DATE_STR} · 与 JOH 投稿平行 · 请勿覆盖英文 report.html</div>
<div class="wrap">
{cover}
{toc}
{s1}
{s2}
{s3}
{s4}
{s5}
{s6}
{s7}
{s8}
{s9}
</div>
</body>
</html>
"""

    # ---------- Markdown ----------
    def strip_tags(s: str) -> str:
        return (
            s.replace("<p>", "").replace("</p>", "\n\n")
            .replace("<strong>", "**").replace("</strong>", "**")
            .replace("<code>", "`").replace("</code>", "`")
        )

    md_parts = []
    md_parts.append(f"""# 全局 EOF 降维何时不足以支撑多保真洪水淹没模拟？

**副标题：** 水动力分区 LSG-Max：等模态预算、面积加权指标与训练期分区

**文档类型：** 内部研究报告 / 与 JOH 投稿平行文档（非英文 `report.md` 的替换件）

**项目路径：** `{PROJECT_PATH}`

**日期：** {DATE_STR}

**生成脚本：** `scripts/96_research_report_zh.py`

图的二进制请在 `研究报告.html` 中查看（已 Base64 内嵌），或打开 `outputs/figures/` 下的 PNG。下文保留全部数字与解说。

---

## 目录

1. [摘要](#1-摘要)
2. [研究背景与目的](#2-研究背景与目的)
3. [数据与方法](#3-数据与方法)
4. [研究过程](#4-研究过程)
5. [结果展示](#5-结果展示)
6. [分析与讨论](#6-分析与讨论)
7. [主要结论](#7-主要结论)
8. [不足与展望](#8-不足与展望)
9. [附录](#9-附录)

---

## 1 摘要

本文问的是一个很具体的方法学问题：在多保真洪水淹没代理模型里，把整个泛滥平原当作一块“均匀布”去做经验正交函数降维，是否在水动力学上保持中性？若残差在空间上是分块组织的，全局降维就可能把河道、常淹滩地与边缘浅水搅在同一组模态里，从而在模态预算紧张时学偏。

针对这一问题，本文在 Fraehr 等人（2024）公开基准上实现**水动力分区的 LSG-Max**。LSG 是「低保真—空间分析—高斯过程」（Low-fidelity, Spatial analysis, Gaussian Process）的缩写。LSG-Max 只预测一场洪水的**最大淹没水深面**。分区在经验正交函数（Empirical Orthogonal Function，EOF）和高斯过程回归（Gaussian Process，GP）之前完成。评价使用**真等模态预算 B**、**面积加权指标**以及**仅用训练事件做分区**。

> **Carlisle 主结果。** 真等预算 B = 4 时，规则分区把面积加权 RMSE 从 {fmt(G4)} m 降到 {fmt(R4)} m（{impr4:.1f}%）。9 折事件 LOOCV 中 9/9 折分区更优，ΔRMSE 均值 {fmt(L4['mean'])} m，95% 区间 [{fmt(L4['ci'][0])}, {fmt(L4['ci'][1])}] m。时序 EOI = {eoi_ts:.2f}；最大面 EOI = {eoi_c:.3f}。全局随 B 增大而变差（{fmt(G4)} → {fmt(G6)} → {fmt(G8)} m），规则更稳健（{fmt(R4)} → {fmt(R6)} → {fmt(R8)} m）。

> **官方 2 折并不显著。** 平均 ΔRMSE = {fmt(official['mean_delta_rmse'])} m，95% 区间 [{fmt(official['ci_95_lower'])}, {fmt(official['ci_95_upper'])}]，`significant=false`。9 折 LOOCV 才是统计主声称。

> **Burnett 30 折：分区没有帮忙。** 全局均值 {fmt(bloo['mean_global_rmse'])} m，规则 {fmt(bloo['mean_zonal_rmse'])} m，ΔRMSE = {fmt(bloo['mean_delta_rmse'])} m，{bloo['n_improved']}/{bloo['n_folds']} 折，区间 [{fmt(bloo['ci_95_lower'])}, {fmt(bloo['ci_95_upper'])}]，`significant=false`。

Chowilla 为边界情形：LSG RMSE 约 {fmt(ch_g)} m，仅用 LF 为 {fmt(ch_lf)} m。不把 Chowilla 写成成功。GP 后端为 sklearn GPR，非 gpflow SGPR。

## 2 研究背景与目的

### 2.1 科学问题

细网格二维水动力模型可信但昂贵。多保真思路用低保真给出轮廓，再用少量高保真样本学习系统偏差。Fraehr 等人的 LSG 对高保真场做 EOF，将低保真投影到同一空间基，再用 GP 学习系数映射。全局 EOF 默认整张泛滥平原共享模态；当 LF–HF 残差空间成块（EOI 高）时，这一默认并不中性。

**核心问题：** 当模态预算 B 被公平限制、指标按面积加权、分区只用训练事件时，全局 EOF 在什么条件下已经不够，而水动力分区能够稳定降低水深 RMSE？

工作假说：分区收益是**残差空间组织 × 有限模态容量**的函数。Carlisle 为正例，Burnett 为反例，Chowilla 为“LSG 帮倒忙”的边界。

### 2.2 术语约定

- **EOF**（经验正交函数）：高维淹没场的空间降维。
- **LSG**：低保真—空间分析—高斯过程。
- **LSG-Max / LSG-TS**：最大面 / 全时段；本文 Track B 只有 Max，真实 TS 为【待补充】。
- **GP / GPR / SGPR**：高斯过程；本文为 sklearn GPR，gpflow 为【待补充】。
- **RMSE / CSI / EOI / LOOCV / LF / HF / B / 规则分区 / KMeans / 面积加权 / ΔRMSE**：含义与 HTML 第 2.2 节相同。

## 3 数据与方法

### 3.1 三个案例

网格单元数来自 Fraehr 几何：581,061 / 5,681（Carlisle），109,914 / 1,434（Chowilla），780,785 / 15,256（Burnett）。

**表 1　案例摘要**

{md_table(t1_h, t1_r)}

请按列比较仅用 LF、全局与分区，不要把三流域 RMSE 直接比绝对值。最大面 EOI：Carlisle {eoi_c:.3f}，Chowilla {eoi_w:.3f}，Burnett {eoi_bmax:.3f}。时序 EOI（Carlisle）为 {eoi_ts:.2f}。

**表 2　实验矩阵**

{md_table(t2_h, t2_r)}

### 3.2 LSG-Max 与水动力分区

湿润阈值 0.03 m。规则分区按训练期最大水深与淹没频率切深槽、常淹、间歇与边缘；KMeans 为 K=4。分区、EOF、GP 均只在训练事件上拟合。

{md_fig(1, "全局 LSG 与分区 LSG 的流程对照（示意图）", "fig01_workflow.png",
"左列全局 EOF+GP；右列先分区再分区 EOF+GP。示意图不含可引用 RMSE。", True)}

{md_fig(2, "Carlisle 真实地形与 KMeans 四区", "fig02_zone_maps_real.png",
"(a) 地形；(b) K=4 湿区；(c) 湿单元 238,946，四区约 42.0% / 23.5% / 7.4% / 27.1%。真实几何，非 30×40。")}

### 3.3 真等预算、面积加权与防泄漏

全局在 B=8 时实际模态为 7（MISMATCH）。面积权来自几何。GP 为 sklearn GPR。

## 4 研究过程

### 4.1 双轨管线

轨道 A（`scripts/03–09 --synthetic`）是 30×40 冒烟测试，**不可引用**。轨道 B（`30/31/32/10/45/95`）才是论文数字。本中文稿为平行文档，不覆盖 `report.html`。

Chowilla 压缩包历史上 MD5 失败；使用已解压 31 HF+31 LF，保留 Chowilla.bad。评价子集 12/31。高程基准修正为【待补充】。

### 4.2 泄漏审计

**表 8　泄漏审计**

{md_table(t8_h, t8_r)}

**表 7　模态预算审计**

{md_table(t7_h, t7_r)}

## 5 结果展示

### 5.1 Carlisle 真等预算

**表 3　面积加权 RMSE**

{md_table(t3_h, t3_r)}

全局 B=4→B=8 升高 {rise_g:.0f}%，规则升高 {rise_r:.0f}%。B=4 规则相对全局 {impr4:.1f}%。

**表 3b　CSI**

{md_table(t3c_h, t3c_r)}

仅用 LF 的 CSI（{fmt(csi['lf'])}）高于 LSG。分区主要改善水深 RMSE，范围 CSI 并非全面胜利。

{md_fig(3, "Carlisle 真等预算 RMSE–B 曲线（SciencePlots IEEE）", "fig03_mode_budget.png",
"全局随 B 上升最快；规则始终最低。可引用。SciencePlots 2.2：science+ieee+no-latex，Times New Roman，英文轴注，600 dpi。")}

**表 3c　MAE 与偏差**

{md_table(t_mae_h, t_mae_r)}

**表 R　残差组织**

{md_table(t_eoi_h, t_eoi_r)}

{md_fig(4, "CSI 随 B 变化", "fig09_csi_budget.png",
"LSG 的 CSI 低于仅用低保真；分区赢在 RMSE 而非湿干范围。")}

{md_fig(5, "MAE 与偏差", "fig13_mae_bias.png",
"全局 B 增大后偏差变负；规则偏差靠近 0。")}

### 5.2 LOOCV 与官方 2 折

**表 4　事件级检验**

{md_table(t4_h, t4_r)}

**表 6　B=4 逐事件**

{md_table(t6_h, t6_r)}

事件 1 上全局约 {fmt(L4['items'][1]['global_rmse'])} m、分区约 {fmt(L4['items'][1]['zonal_rmse'])} m。官方 2 折 `significant=false`，不是主声称。

{md_fig(6, "Carlisle 九折 LOOCV（B=4）", "fig08_per_event_bootstrap.png",
"规则线在全部 9 个留出事件上低于全局。")}

{md_fig(7, "1:1 散点", "fig11_loocv_scatter.png",
"九点均在 1:1 线下方；事件 1 远离原点。")}

{md_fig(8, "四种协议的 ΔRMSE 森林图", "fig12_stat_ci.png",
"仅 Carlisle 9 折 B=4/6 的须不跨 0；官方 2 折与 Burnett 跨 0。")}

### 5.3 三案例

**表 5**

{md_table(t5_h, t5_r)}

{md_fig(9, "三案例 RMSE 柱状图", "fig04_three_case.png",
"Carlisle 分区最好；Chowilla 的 LSG 柱远高于仅用 LF；Burnett 全局与分区几乎等高。")}

{md_fig(10, "Burnett 30 折逐场 RMSE", "fig10_burnett_loocv.png",
"两条线纠缠；分区不系统更优。")}

{md_fig(11, "Carlisle 精度–耗时", "fig08_runtime.png",
"规则 B=4 在约 1.3 s 处给出最低 RMSE；KMeans 慢约 7–9 s。")}

**表 9　Chowilla 预算扫描**

{md_table(t9_h, t9_r)}

**表 10　Burnett**

{md_table(t10_h, t10_r)}

## 6 分析与讨论

英文稿讨论分三问。**何时有用：** Carlisle 规则分区 RMSE {fmt(G4)}→{fmt(R4)} m，9/9 折改善；时序 EOI={eoi_ts:.2f}，最大面 EOI={eoi_c:.3f}（二者不同协议）。**为何加模态变差：** 全局 {fmt(G4)}→{fmt(G8)} m 是过拟合，分区把容量锁在各区。**何时无益：** Burnett 最大面 EOI={eoi_bmax:.3f} 但 30 折规则不优于全局；Chowilla EOI={eoi_w:.3f} 且 LSG 相对仅用 LF 退化。官方 2 折不显著是功效问题。一阶 EOI 不能单独作为分区开关。

**官方 9 折 MaxWD R²：** 已发表 LSG-TS 0.990，本文规则 LSG-Max 0.988，全局 0.915。CSI：已发表 0.937 vs 规则 0.905。外推 p10/p11 分区优于全局但未击败仅用 LF（约 0.10 m）。LF 网格 ×2/×4 加粗后规则 RMSE 仍约 0.094–0.103 m。主槽距离+规则 0.094 m，略优于纯规则 0.096 m。

{md_fig(14, "三案例最大淹没面 EOI", "fig14_eoi.png", "Burnett 高、Carlisle/Chowilla 低；与分区是否获益方向相反。")}
{md_fig(17, "LF 网格加粗", "fig17_lf_degradation.png", "仅用 LF 随加粗急剧变差；规则分区几乎不动。")}
{md_fig(18, "主槽距离分区", "fig18_channel_distance.png", "物理河道距离可替代残差热点。")}

## 7 主要结论

1. Carlisle、B=4：全局 EOF 非中性；规则分区 RMSE {fmt(G4)}→{fmt(R4)} m（{impr4:.1f}%），9/9 LOOCV。
2. 加大全局 B 不如分区消化容量（全局 {fmt(G4)}→{fmt(G8)}；规则 {fmt(R4)}→{fmt(R8)}）。
3. 收益依案例；最大面 EOI 不能预测增益：Chowilla {eoi_w:.3f}（低）且 LSG 退化；Burnett {eoi_bmax:.3f}（高）但 30 折分区不优。
4. 官方 2 折不显著，不得当作主声称。
5. 官方 9 折 MaxWD R²：规则 LSG-Max 0.988，已发表 LSG-TS 0.990。
6. LF 加粗时规则分区稳健；主槽距离可作物理切区；外推改善相对全局但未击败仅用 LF。
7. 二阶诊断：ZGG>0 但纯 EOF oracle ΔRMSE<0 —— 分区 LSG 增益在 GP 映射，不在 HF-EOF 截断。

## 8 不足与展望

sklearn GPR 而非 gpflow SGPR【待补充】；无真实 LSG-TS【待补充】；Chowilla MD5/基准【待补充】；Burnett KMeans LOOCV 与 74 场【待补充】；Brisbane 未运行【待补充】；分区分量残差未重算 HDF5。一阶 EOI 已算完。正文图已按 SciencePlots 2.2 IEEE + Times New Roman（英文轴注）重绘。

## 9 附录

### 9.1 数据来源

Fraehr（2024）Figshare 24312658。数字来自 `outputs/registry/result_manifest_v4.csv` 及第 9.1 节 HTML 所列 JSON。英文稿 `report.md` 为平行叙事，本文件不覆盖它。

### 9.2 脚本索引

**表 11**

{md_table(["脚本", "轨道", "作用"], [[r[0].replace("<code>", "`").replace("</code>", "`") if isinstance(r[0], str) else r[0], r[1], r[2]] for r in scripts_r])}

复现：`D:\\miniforge3\\envs\\hydromodel\\python.exe scripts\\96_research_report_zh.py`

### 9.3 待补充清单

**表 12**

{md_table(pend_h, pend_r)}
""")

    md = "\n".join(md_parts)
    pending.extend([r[1] for r in pend_r])
    return html, md, sorted(set(embedded)), pending


def try_pdf(html_path: Path, pdf_path: Path) -> tuple[bool, str]:
    browsers = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(os.environ.get("LOCALAPPDATA", "")) / r"Microsoft\Edge\Application\msedge.exe",
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    ]
    browser = next((p for p in browsers if p and p.exists()), None)
    if browser is None:
        return False, "未找到 Edge/Chrome。请用浏览器打开 HTML 后 Ctrl+P 另存为 PDF，打印机选 Microsoft YaHei。"
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
        proc = subprocess.run(args, capture_output=True, timeout=180, cwd=str(ROOT))
    except subprocess.TimeoutExpired:
        return False, "浏览器无头打印超时（180 s）。"
    if pdf_path.exists() and pdf_path.stat().st_size > 10_000:
        return True, f"使用 {browser.name} 无头打印成功"
    err = (proc.stderr or b"").decode("utf-8", errors="replace")[-500:]
    return False, f"浏览器已调用但未得到有效 PDF。stderr: {err}"


def main():
    os.chdir(str(ROOT))
    cb = load_json(OUT / "carlisle" / "budget_sweep_true_equal.json")
    loocv = load_json(OUT / "carlisle" / "loocv_results.json")
    official = load_json(OUT / "carlisle" / "multifold_bootstrap.json")
    bloo = load_json(OUT / "burnettrv" / "loocv_results.json")
    vs = load_json(OUT / "burnettrv" / "validation_std.json")
    ch_full = load_json(OUT / "chowilla" / "budget_sweep_full.json")
    eoi_all_p = OUT / "eoi" / "eoi_all.json"
    eoi_all = load_json(eoi_all_p) if eoi_all_p.exists() else {"cases": {}}
    eoi_max = {}
    eoi_between_max = eoi_total_max = 0.51
    for case, rec in eoi_all.get("cases", {}).items():
        eoi_max[case] = float(rec["pooled"]["eoi"])
        if case == "carlisle":
            eoi_between_max = float(rec["pooled"]["between_zone_var"])
            eoi_total_max = float(rec["pooled"]["total_var"])
    eoi_rows = load_csv(REG / "residual_organization.csv")
    eoi_row = next((r for r in eoi_rows if r.get("case", "").lower() == "carlisle"), eoi_rows[0] if eoi_rows else {"EOI": "0.51", "between_zone_var": "0", "total_var": "0"})
    def _opt(name):
        p = OUT / "carlisle" / name
        return load_json(p) if p.exists() else None
    official_fold = _opt("official_fold_zonal.json")
    extrap = _opt("extrap_zonal.json")
    degradation = _opt("lf_degradation.json")
    channel = _opt("distance_to_channel.json")
    modal_p = OUT / "eoi" / "modal_eoi.json"
    modal_eoi = load_json(modal_p) if modal_p.exists() else {}
    manifest = load_csv(REG / "result_manifest_v4.csv")
    mode_audit = load_csv(REG / "mode_budget_audit.csv")

    def mget(case, model, b=None):
        for r in manifest:
            if r["case"] == case and r["model"] == model:
                if b is None or str(r["B_requested"]) == str(b):
                    return r
        return None

    G4 = cb["budgets"]["4"]["global"]["rmse_area"]
    R4 = cb["budgets"]["4"]["rule"]["rmse_area"]
    K4 = cb["budgets"]["4"]["kmeans"]["rmse_area"]
    G6 = cb["budgets"]["6"]["global"]["rmse_area"]
    R6 = cb["budgets"]["6"]["rule"]["rmse_area"]
    K6 = cb["budgets"]["6"]["kmeans"]["rmse_area"]
    G8 = cb["budgets"]["8"]["global"]["rmse_area"]
    R8 = cb["budgets"]["8"]["rule"]["rmse_area"]
    K8 = cb["budgets"]["8"]["kmeans"]["rmse_area"]
    LF = cb["lf_only"]["rmse_area"]

    figs = {name: b64_png(FIG / name) for name in FIGURE_FILES}
    missing = [n for n, v in figs.items() if v is None]
    pending = []
    if missing:
        pending.append("缺失配图: " + ", ".join(missing))

    data = {
        "cb": cb,
        "G4": G4, "R4": R4, "K4": K4,
        "G6": G6, "R6": R6, "K6": K6,
        "G8": G8, "R8": R8, "K8": K8,
        "LF": LF,
        "impr4": (G4 - R4) / G4 * 100,
        "L4": loocv_stats(loocv, 4),
        "L6": loocv_stats(loocv, 6),
        "official": official,
        "eoi": 0.51,
        "eoi_ts": 0.51,
        "eoi_max": eoi_max,
        "eoi_between_max": eoi_between_max,
        "eoi_total_max": eoi_total_max,
        "official_fold": official_fold or {},
        "extrap": extrap or {},
        "degradation": degradation or {},
        "channel": channel or {},
        "modal_eoi": modal_eoi,
        "ch_lf": float(mget("Chowilla", "LF-only")["rmse_area"]),
        "ch_g": float(mget("Chowilla", "global", 4)["rmse_area"]),
        "ch_r": float(mget("Chowilla", "rule", 4)["rmse_area"]),
        "ch_k": float(mget("Chowilla", "kmeans", 4)["rmse_area"]),
        "b_lf": float(mget("BurnettRV", "LF-only")["rmse_area"]),
        "b_g": float(mget("BurnettRV", "global")["rmse_area"]),
        "b_r": float(mget("BurnettRV", "Rule_B4")["rmse_area"]),
        "bloo_rule": bloo["summary"]["rule"],
        "bloo_means": burnett_loocv_means(bloo),
        "eoi_between": float(eoi_row["between_zone_var"]),
        "eoi_total": float(eoi_row["total_var"]),
        "ch_full": ch_full,
        "burnett_std": vs,
        "mode_audit": mode_audit,
        "csi": {
            "lf": cb["lf_only"]["csi_area"],
            "g4": cb["budgets"]["4"]["global"]["csi_area"],
            "r4": cb["budgets"]["4"]["rule"]["csi_area"],
            "k4": cb["budgets"]["4"]["kmeans"]["csi_area"],
            "g6": cb["budgets"]["6"]["global"]["csi_area"],
            "r6": cb["budgets"]["6"]["rule"]["csi_area"],
            "k6": cb["budgets"]["6"]["kmeans"]["csi_area"],
            "g8": cb["budgets"]["8"]["global"]["csi_area"],
            "r8": cb["budgets"]["8"]["rule"]["csi_area"],
            "k8": cb["budgets"]["8"]["kmeans"]["csi_area"],
        },
        "figs": figs,
        "embedded": [],
        "pending": pending,
    }

    html, md, embedded, pending_items = build(data)
    HTML_ZH.write_text(html, encoding="utf-8")
    shutil.copyfile(HTML_ZH, HTML_EN_NAME)
    MD_ZH.write_text(md, encoding="utf-8")

    print(f"HTML: {HTML_ZH} ({HTML_ZH.stat().st_size / 1024 / 1024:.2f} MB)")
    print(f"HTML copy: {HTML_EN_NAME} ({HTML_EN_NAME.stat().st_size / 1024 / 1024:.2f} MB)")
    print(f"MD: {MD_ZH} ({MD_ZH.stat().st_size / 1024:.0f} KB)")
    print("Embedded figures:")
    for n in FIGURE_FILES:
        mark = "yes" if n in embedded else "MISSING"
        print(f"  {n}: {mark}")

    ok, msg = try_pdf(HTML_ZH, PDF_ZH)
    if ok:
        print(f"PDF: {PDF_ZH} ({PDF_ZH.stat().st_size / 1024 / 1024:.2f} MB) — {msg}")
    else:
        print(f"PDF FAILED: {msg}")
        print("HTML+MD 已交付。")

    print("待补充事项数:", len([p for p in pending_items if p]))
    print("English artefacts untouched: report.html / report.md / report.pdf")
    print("Done.")


if __name__ == "__main__":
    main()
