#!/usr/bin/env python
"""Track B figures in SciencePlots 2.2 (IEEE, English labels, Times New Roman).

House style for paper + Chinese report embeds:
  plt.style.use(['science', 'ieee', 'no-latex'])
  serif = Times New Roman (Latin / digits); English axis labels
  600 dpi PNG, pdf.fonttype=42

Chinese report body stays Chinese; figure glyphs are English so one PNG set
serves both the English manuscript and the Chinese parallel report.

Does not overwrite fig02_zone_maps_real.png.
Does not plot synthetic 30x40 artefacts.

Run:
  D:\\miniforge3\\envs\\hydromodel\\python.exe scripts/97_scienceplots_figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import numpy as np

import scienceplots  # noqa: F401  — registers styles

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "outputs" / "figures"
EVAL = ROOT / "outputs" / "evaluation"
REG = ROOT / "outputs" / "registry"

# IEEE single / double column (inch)
W1, W2 = 3.5, 7.16
DPI = 600

STYLE = ["science", "ieee", "no-latex"]

# Resolved at apply_style(); exposed for report footnotes
ACTIVE_SERIF = "Times New Roman"
SKIPPED: list[str] = []


def _pick_serif() -> str:
    """Prefer Times New Roman; fall back to a similar serif if missing."""
    avail = {f.name for f in fm.fontManager.ttflist}
    for name in ("Times New Roman", "Times", "Liberation Serif", "DejaVu Serif"):
        if name in avail:
            return name
    return "DejaVu Serif"


def apply_style():
    global ACTIVE_SERIF
    ACTIVE_SERIF = _pick_serif()
    plt.style.use(STYLE)
    # Submission-readable sizes (IEEE single-column still readable when scaled)
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": [ACTIVE_SERIF, "DejaVu Serif", "Times", "serif"],
        "mathtext.fontset": "stix",
        "axes.labelsize": 9,
        "axes.titlesize": 10,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 7,
        "figure.titlesize": 10,
        "axes.unicode_minus": False,
        "figure.dpi": 150,
        "savefig.dpi": DPI,
        "savefig.bbox": "tight",
        "savefig.facecolor": "white",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })
    print(f"Figure serif font: {ACTIVE_SERIF}")
    return ACTIVE_SERIF


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save(fig, name: str):
    FIG.mkdir(parents=True, exist_ok=True)
    out = FIG / name
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved {out} ({out.stat().st_size / 1024:.0f} KB)")


def fig01_workflow():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(W2, 3.15))
    steps_g = [
        "LF interpolate to HF grid",
        "Global EOF",
        "GP: LF coeffs → HF coeffs",
        "Reconstruct max. inundation",
    ]
    steps_z = [
        "LF interpolate to HF grid",
        "Hydrodynamic zoning (train only)",
        "Zonal EOF + zonal GP mapping",
        "Stitch zonal max. surfaces",
    ]
    yg = [0.82, 0.58, 0.34, 0.10]
    for ax, title, steps, fc, ec in (
        (ax1, "Global LSG-Max (baseline)", steps_g, "#d9e8f5", "#2c5d8c"),
        (ax2, "Zonal LSG-Max (this work)", steps_z, "#dcefe4", "#1e7a4a"),
    ):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.set_title(title)
        for y, text in zip(yg, steps):
            ax.add_patch(plt.Rectangle((0.08, y - 0.08), 0.84, 0.16,
                                       facecolor=fc, edgecolor=ec, linewidth=0.8, zorder=2))
            ax.text(0.50, y, text, ha="center", va="center", fontsize=7.5, zorder=3)
        for i in range(len(yg) - 1):
            ax.annotate("", xy=(0.50, yg[i + 1] + 0.08), xytext=(0.50, yg[i] - 0.08),
                        arrowprops=dict(arrowstyle="-|>", color=ec, lw=0.9), zorder=1)
    save(fig, "fig01_workflow.png")


def fig03_mode_budget(cb: dict):
    Bs = [4, 6, 8]
    g = [cb["budgets"][str(b)]["global"]["rmse_area"] for b in Bs]
    r = [cb["budgets"][str(b)]["rule"]["rmse_area"] for b in Bs]
    k = [cb["budgets"][str(b)]["kmeans"]["rmse_area"] for b in Bs]
    lf = cb["lf_only"]["rmse_area"]
    fig, ax = plt.subplots(figsize=(W1, 2.55))
    ax.plot(Bs, g, "o-", label="Global", markersize=4)
    ax.plot(Bs, r, "s--", label="Rule zonal", markersize=4)
    ax.plot(Bs, k, "^:", label="KMeans zonal", markersize=4)
    ax.axhline(lf, color="0.45", ls="-.", lw=0.8, label="LF only")
    ax.set_xlabel("Mode budget $B$")
    ax.set_ylabel("Area-weighted RMSE (m)")
    ax.set_xticks(Bs)
    ax.set_ylim(0, 1.30 * max(g + r + k + [lf]))
    ax.legend(frameon=False, fontsize=7)
    ax.annotate("7 modes\nrealized", (8, g[2]), textcoords="offset points",
                xytext=(8, 10), fontsize=6, color="0.35", ha="center")
    save(fig, "fig03_mode_budget.png")

    fig, ax = plt.subplots(figsize=(W1, 2.55))
    ax.plot(Bs, [cb["budgets"][str(b)]["global"]["csi_area"] for b in Bs], "o-", label="Global", markersize=4)
    ax.plot(Bs, [cb["budgets"][str(b)]["rule"]["csi_area"] for b in Bs], "s--", label="Rule zonal", markersize=4)
    ax.plot(Bs, [cb["budgets"][str(b)]["kmeans"]["csi_area"] for b in Bs], "^:", label="KMeans zonal", markersize=4)
    ax.axhline(cb["lf_only"]["csi_area"], color="0.45", ls="-.", lw=0.8, label="LF only")
    ax.set_xlabel("Mode budget $B$")
    ax.set_ylabel("Area-weighted CSI")
    ax.set_xticks(Bs)
    _csi_all = [cb["budgets"][str(b)][m]["csi_area"] for b in Bs for m in ("global", "rule", "kmeans")]
    ax.set_ylim(0, 1.08 * max(_csi_all + [cb["lf_only"]["csi_area"]]))
    ax.legend(frameon=False, fontsize=7)
    ax.annotate("7 modes\nrealized", (8, cb["budgets"]["8"]["global"]["csi_area"]),
                textcoords="offset points", xytext=(8, 10), fontsize=6,
                color="0.35", ha="center")
    save(fig, "fig09_csi_budget.png")


def fig04_three_case(cb: dict, ch: dict, vs: dict):
    labels = ["Carlisle", "Chowilla", "Burnett"]
    lf = [cb["lf_only"]["rmse_area"], ch["lf_only"]["rmse_area"], vs["lf_only"]["rmse_area"]]
    glob = [cb["budgets"]["4"]["global"]["rmse_area"], ch["budgets"]["4"]["global"]["rmse_area"], vs["global"]["rmse_area"]]
    zonal = [cb["budgets"]["4"]["rule"]["rmse_area"], ch["budgets"]["4"]["rule"]["rmse_area"], vs["Rule_B4"]["rmse_area"]]
    x = np.arange(len(labels))
    w = 0.26
    fig, ax = plt.subplots(figsize=(W2, 2.8))
    colors = ["#abd9e9", "#2c7bb6", "#d7191c"]  # Nature-style: LF, Global, Zonal
    bars_lf = ax.bar(x - w, lf, w, label="LF only", color=colors[0])
    bars_g = ax.bar(x, glob, w, label="Global LSG-Max", color=colors[1])
    bars_z = ax.bar(x + w, zonal, w, label="Rule zonal $B{=}4$", color=colors[2])
    for bars in (bars_lf, bars_g, bars_z):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{b.get_height():.3f}",
                    ha="center", va="bottom", fontsize=5.5, rotation=90)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Area-weighted RMSE (m)")
    ax.legend(frameon=False, ncol=3, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.14))

    # Carlisle inset (magnified) to resolve the zonal-vs-global difference
    axins = ax.inset_axes([0.08, 0.50, 0.32, 0.42])
    ci = ["LF only", "Global", "Rule zonal"]
    cv = [lf[0], glob[0], zonal[0]]
    ib = axins.bar(np.arange(len(ci)), cv, 0.55, color=colors)
    for b, v in zip(ib, cv):
        axins.text(b.get_x() + b.get_width() / 2, v, f"{v:.3f}",
                   ha="center", va="bottom", fontsize=6)
    axins.set_xticks(np.arange(len(ci)))
    axins.set_xticklabels(ci, fontsize=6, rotation=20)
    axins.set_ylim(0, max(cv) * 1.25)
    axins.set_ylabel("RMSE (m)", fontsize=6)
    axins.set_title("Carlisle (magnified)", fontsize=7)
    axins.tick_params(labelsize=6)

    save(fig, "fig04_three_case.png")


def fig_carlisle_loocv(loocv: dict):
    items = [e for e in loocv["per_event"] if e["B"] == 4]
    folds = [e["fold"] for e in items]
    g = [e["global_rmse"] for e in items]
    z = [e["zonal_rmse"] for e in items]
    fig, ax = plt.subplots(figsize=(W2, 2.7))
    for xi, gv, zv in zip(folds, g, z):
        ax.plot([xi, xi], [gv, zv], color="0.6", lw=0.7, zorder=1)
    ax.scatter(folds, g, s=28, marker="o", zorder=3, label="Global $B{=}4$")
    ax.scatter(folds, z, s=28, marker="s", zorder=3, label="Rule zonal $B{=}4$")
    ax.set_xlabel("Held-out event index")
    ax.set_ylabel("Area-weighted RMSE (m)")
    ax.set_xticks(folds)
    ax.legend(frameon=False)
    save(fig, "fig08_per_event_bootstrap.png")

    fig, ax = plt.subplots(figsize=(W1, 2.7))
    ax.plot([0, max(g)], [0, max(g)], color="0.5", lw=0.7, ls="--", label="1:1")
    ax.scatter(g, z, s=22, zorder=3)
    ax.set_xlabel("Global RMSE (m)")
    ax.set_ylabel("Rule zonal RMSE (m)")
    ax.set_aspect("equal", adjustable="box")
    ax.legend(frameon=False, fontsize=7)
    save(fig, "fig11_loocv_scatter.png")


def fig_burnett_loocv(bloo: dict):
    events = bloo["per_event"]
    x = [e["test_event"] for e in events]
    g = [e["global"]["rmse_area"] for e in events]
    z = [e["rule"]["rmse_area"] for e in events]
    fig, ax = plt.subplots(figsize=(W2, 2.7))
    for xi, gv, zv in zip(x, g, z):
        ax.plot([xi, xi], [gv, zv], color="0.6", lw=0.5, zorder=1)
    ax.scatter(x, g, s=16, marker="o", zorder=3, label="Global $B{=}4$")
    ax.scatter(x, z, s=16, marker="s", zorder=3, label="Rule zonal $B{=}4$")
    ax.set_xlabel("Held-out event index")
    ax.set_ylabel("Area-weighted RMSE (m)")
    ax.legend(frameon=False)
    save(fig, "fig10_burnett_loocv.png")


def fig_runtime(cb: dict):
    fig, ax = plt.subplots(figsize=(W1, 2.7))
    ax.scatter([0.01], [cb["lf_only"]["rmse_area"]], marker="x", s=36, label="LF only", zorder=3)
    for B, mk in [("4", "o"), ("6", "s"), ("8", "^")]:
        g = cb["budgets"][B]["global"]
        r = cb["budgets"][B]["rule"]
        k = cb["budgets"][B]["kmeans"]
        lab_g = "Global" if B == "4" else None
        lab_r = "Rule zonal" if B == "4" else None
        lab_k = "KMeans zonal" if B == "4" else None
        ax.scatter(g["time_s"], g["rmse_area"], marker=mk, label=lab_g)
        ax.scatter(r["time_s"], r["rmse_area"], marker=mk, label=lab_r)
        ax.scatter(k["time_s"], k["rmse_area"], marker=mk, label=lab_k)
        ax.annotate(f"$B{B}$", (g["time_s"], g["rmse_area"]), textcoords="offset points", xytext=(4, 4), fontsize=6)
        ax.annotate(f"$B{B}$", (r["time_s"], r["rmse_area"]), textcoords="offset points", xytext=(4, 4), fontsize=6)
    ax.set_xlabel("Train+predict wall time (s)")
    ax.set_ylabel("Area-weighted RMSE (m)")
    ax.legend(frameon=False, fontsize=7)
    save(fig, "fig08_runtime.png")


def fig_stat_ci(car_b4, car_b6, official: dict, burn: dict):
    names = ["Carlisle\n$B{=}4$ LOOCV", "Carlisle\n$B{=}6$ LOOCV", "Carlisle\nofficial 2-fold", "Burnett\n30-fold $B{=}4$"]
    means = [car_b4["mean"], car_b6["mean"], official["mean_delta_rmse"], burn["mean_delta_rmse"]]
    lo = [car_b4["ci"][0], car_b6["ci"][0], official["ci_95_lower"], burn["ci_95_lower"]]
    hi = [car_b4["ci"][1], car_b6["ci"][1], official["ci_95_upper"], burn["ci_95_upper"]]
    y = np.arange(len(names))[::-1]
    fig, ax = plt.subplots(figsize=(W2, 2.6))
    xerr = np.vstack([np.array(means) - np.array(lo), np.array(hi) - np.array(means)])
    ax.errorbar(means, y, xerr=xerr, fmt="o", capsize=2.5, markersize=4)
    ax.axvline(0.0, color="0.4", lw=0.7, ls="--")
    for yy, m, l, h in zip(y, means, lo, hi):
        ax.text(m, yy + 0.3, f"{m:+.3f}  [{l:+.3f}, {h:+.3f}]",
                va="bottom", ha="left", fontsize=6, color="0.25")
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.set_xlabel(r"Mean $\Delta$RMSE (m)  (global $-$ zonal; $>0$ zonal better)")
    xmax = 1.55 * max(abs(v) for v in means + lo + hi)
    ax.set_xlim(-xmax, xmax)
    ax.set_ylim(-0.7, len(names) - 0.5 + 1.1)
    save(fig, "fig12_stat_ci.png")


def fig_mae_bias(cb: dict):
    Bs = [4, 6, 8]
    fig, axes = plt.subplots(1, 2, figsize=(W2, 2.55))
    for ax, key, ylab, tag in (
        (axes[0], "mae_area", "Area-weighted MAE (m)", "(a)"),
        (axes[1], "bias_area", "Area-weighted bias (m)", "(b)"),
    ):
        ax.plot(Bs, [cb["budgets"][str(b)]["global"][key] for b in Bs], "o-", label="Global")
        ax.plot(Bs, [cb["budgets"][str(b)]["rule"][key] for b in Bs], "s--", label="Rule zonal")
        ax.plot(Bs, [cb["budgets"][str(b)]["kmeans"][key] for b in Bs], "^:", label="KMeans zonal")
        ax.axhline(cb["lf_only"][key], color="0.45", ls="-.", lw=0.8, label="LF only")
        ax.set_xlabel("Mode budget $B$")
        ax.set_ylabel(ylab)
        ax.set_xticks(Bs)
        ax.set_title(tag, fontsize=9, loc="left")
        if key == "bias_area":
            ax.axhline(0.0, color="0.6", lw=0.5)
    axes[0].legend(frameon=False, fontsize=6)
    save(fig, "fig13_mae_bias.png")


def fig_eoi(eoi_all: dict):
    cases = ["carlisle", "burnettrv", "chowilla"]
    labels = ["Carlisle", "Burnett", "Chowilla"]
    vals = []
    for c in cases:
        rec = eoi_all.get("cases", {}).get(c)
        vals.append(np.nan if rec is None else rec["pooled"]["eoi"])
    fig, ax = plt.subplots(figsize=(W1, 2.4))
    bars = ax.bar(labels, vals, color="#4d6a8f", edgecolor="0.2", lw=0.4)
    for b, v in zip(bars, vals):
        if np.isfinite(v):
            ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.3f}",
                    ha="center", va="bottom", fontsize=6)
    ax.set_ylabel("Error organization index (EOI)")
    ax.set_ylim(0, None)
    save(fig, "fig14_eoi.png")


def fig_eoi_vs_delta(eoi_all: dict):
    fig, ax = plt.subplots(figsize=(W1, 2.5))
    markers = {"carlisle": "o", "burnettrv": "s", "chowilla": "^"}
    colors = {"carlisle": "#2c7bb6", "burnettrv": "#d7191c", "chowilla": "#4d6a8f"}
    names = {"carlisle": "Carlisle", "burnettrv": "Burnett", "chowilla": "Chowilla"}
    for case, rec in eoi_all.get("cases", {}).items():
        folds = rec.get("per_fold") or []
        xs, ys = [], []
        for f in folds:
            d = f.get("delta_rmse_rule_B4")
            if d is None:
                continue
            xs.append(f["eoi"])
            ys.append(d)
        if not xs:
            continue
        ax.scatter(
            xs, ys, s=22, marker=markers.get(case, "o"),
            facecolors="none", edgecolors=colors.get(case, "0.3"),
            linewidths=0.7, label=names.get(case, case), alpha=0.9,
        )
    ax.axhline(0.0, color="0.5", lw=0.6)
    ax.set_xlabel("In-fold train-only EOI (residual-free partition)")
    ax.set_ylabel(r"$\Delta$RMSE (global$-$zonal, m)")
    ax.legend(frameon=False, fontsize=6)
    save(fig, "fig15_eoi_vs_delta.png")


def fig_official_protocol(off: dict):
    pub = off.get("published_mean", {}).get("MaxWD_R2") or {}
    sm = off.get("summary") or {}
    labels, r2s = [], []
    for m in ["LSG", "Kabir_1dCNN", "LSTM_SRR", "GP_EOF", "LSTM_EOF"]:
        if m in pub:
            labels.append(m.replace("_", "-"))
            r2s.append(pub[m])
    for name, lab in [("global", "This work–Global"), ("rule", "This work–Rule"), ("kmeans", "This work–KMeans")]:
        if name in sm and "mean_maxwd_r2" in sm[name]:
            labels.append(lab)
            r2s.append(sm[name]["mean_maxwd_r2"])
    if not labels:
        SKIPPED.append("fig16_official_maxwd_r2.png (no labels)")
        return
    fig, ax = plt.subplots(figsize=(W2, 2.5))
    ax.bar(range(len(labels)), r2s, color="#2c5d8c", edgecolor="0.2", lw=0.3)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylabel(r"Max. water depth $R^2$ (official wet cells)")
    ax.set_ylim(min(0.5, min(r2s) - 0.05), 1.01)
    save(fig, "fig16_official_maxwd_r2.png")


def fig_degradation(deg: dict):
    facs = sorted(deg.get("factors", {}), key=lambda x: int(x))
    if not facs:
        SKIPPED.append("fig17_lf_degradation.png (empty factors)")
        return
    fig, ax = plt.subplots(figsize=(W1, 2.4))
    for name, lab in [("lf_only", "LF only"), ("global", "Global LSG"), ("rule", "Rule zonal")]:
        ys = []
        for f in facs:
            rec = deg["factors"][f]
            src = rec["lf_only"] if name == "lf_only" else rec.get(name)
            ys.append(src["rmse_area"] if src else np.nan)
        ax.plot([int(f) for f in facs], ys, marker="o", label=lab)
    ax.set_xlabel("LF grid coarsening factor")
    ax.set_ylabel("Area-weighted RMSE (m)")
    ax.legend(frameon=False, fontsize=6)
    save(fig, "fig17_lf_degradation.png")


def fig_channel(ch: dict):
    models = ch.get("models") or {}
    if not models:
        SKIPPED.append("fig18_channel_distance.png (no models)")
        return
    order = [k for k in ["global", "rule", "rule_channel", "channel", "kmeans"] if k in models]
    labs = {
        "global": "Global",
        "rule": "Rule",
        "rule_channel": "Rule+channel dist.",
        "channel": "Channel-distance",
        "kmeans": "KMeans+dist.",
    }
    ys = [models[k]["rmse_area"] for k in order]
    fig, ax = plt.subplots(figsize=(W1, 2.55))
    ax.bar([labs[k] for k in order], ys, color="#1e7a4a", edgecolor="0.2", lw=0.3)
    ax.set_ylabel("Area-weighted RMSE (m)")
    ax.tick_params(axis="x", rotation=18)
    save(fig, "fig18_channel_distance.png")


def fig_modal_eoi(modal: dict):
    cases = ["carlisle", "burnettrv", "chowilla"]
    labels = ["Carlisle", "Burnett", "Chowilla"]
    zggs, deltas = [], []
    for c in cases:
        rec = modal.get("cases", {}).get(c)
        if rec is None:
            zggs.append(np.nan)
            deltas.append(np.nan)
            continue
        p = rec["pooled"]
        zggs.append(p.get("mean_zgg", np.nan))
        deltas.append(p["oracle_delta_rmse"])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(W2, 2.5))
    ax1.bar(labels, zggs, color="#2c5d8c", edgecolor="0.2", lw=0.3)
    ax1.axhline(0.0, color="0.5", lw=0.6)
    ax1.set_ylabel("Zone–global gap (ZGG)")
    ax1.set_title("Local vs global basis")
    ax2.bar(labels, deltas, color="#1e7a4a", edgecolor="0.2", lw=0.3)
    ax2.axhline(0.0, color="0.5", lw=0.6)
    ax2.set_ylabel(r"Oracle $\Delta$RMSE (global$-$zonal, m)")
    ax2.set_title("Equal-budget pure EOF")
    save(fig, "fig19_modal_eoi.png")


def loocv_stats(loocv: dict, B: int) -> dict:
    items = [e for e in loocv["per_event"] if e["B"] == B]
    deltas = np.array([e["delta_rmse"] for e in items], dtype=float)
    n = len(deltas)
    rng = np.random.default_rng(42)
    boot = [float(np.mean(rng.choice(deltas, size=n, replace=True))) for _ in range(10000)]
    ci_lo, ci_hi = np.percentile(boot, 2.5), np.percentile(boot, 97.5)
    return {"mean": float(np.mean(deltas)), "ci": (float(ci_lo), float(ci_hi))}


def _require(path: Path, fig_hint: str) -> dict | None:
    if not path.exists():
        SKIPPED.append(f"{fig_hint} (missing {path.relative_to(ROOT)})")
        print(f"SKIP: missing {path}")
        return None
    return load_json(path)


def main():
    apply_style()
    SKIPPED.clear()

    cb = _require(EVAL / "carlisle" / "budget_sweep_true_equal.json", "fig03/04/08/09/13")
    loocv = _require(EVAL / "carlisle" / "loocv_results.json", "fig08/11/12")
    official = _require(EVAL / "carlisle" / "multifold_bootstrap.json", "fig12")
    bloo = _require(EVAL / "burnettrv" / "loocv_results.json", "fig10/12")
    vs = _require(EVAL / "burnettrv" / "validation_std.json", "fig04")
    ch = _require(EVAL / "chowilla" / "budget_sweep_full.json", "fig04")

    if cb is not None:
        fig01_workflow()
        fig03_mode_budget(cb)
        fig_runtime(cb)
        fig_mae_bias(cb)
    if cb is not None and ch is not None and vs is not None:
        fig04_three_case(cb, ch, vs)
    if loocv is not None:
        fig_carlisle_loocv(loocv)
    if bloo is not None:
        fig_burnett_loocv(bloo)
    if loocv is not None and official is not None and bloo is not None:
        fig_stat_ci(loocv_stats(loocv, 4), loocv_stats(loocv, 6), official, bloo["summary"]["rule"])

    eoi_p = EVAL / "eoi" / "eoi_all.json"
    if eoi_p.exists():
        eoi_all = load_json(eoi_p)
        fig_eoi(eoi_all)
        fig_eoi_vs_delta(eoi_all)
    else:
        SKIPPED.append("fig14/15 (missing eoi_all.json)")

    off_p = EVAL / "carlisle" / "official_fold_zonal.json"
    if off_p.exists():
        fig_official_protocol(load_json(off_p))
    else:
        SKIPPED.append("fig16_official_maxwd_r2.png (missing official_fold_zonal.json)")

    deg_p = EVAL / "carlisle" / "lf_degradation.json"
    if deg_p.exists():
        fig_degradation(load_json(deg_p))
    else:
        SKIPPED.append("fig17_lf_degradation.png (missing lf_degradation.json)")

    ch_p = EVAL / "carlisle" / "distance_to_channel.json"
    if ch_p.exists():
        fig_channel(load_json(ch_p))
    else:
        SKIPPED.append("fig18_channel_distance.png (missing distance_to_channel.json)")

    modal_p = EVAL / "eoi" / "modal_eoi.json"
    if modal_p.exists():
        fig_modal_eoi(load_json(modal_p))
    else:
        SKIPPED.append("fig19_modal_eoi.png (missing modal_eoi.json)")

    fig02 = FIG / "fig02_zone_maps_real.png"
    if fig02.exists():
        print("Kept existing fig02_zone_maps_real.png (not regenerated)")
    else:
        SKIPPED.append("fig02_zone_maps_real.png (not produced by this script; file missing)")
        print("fig02 missing — not generated here (requires real DEM/zone maps)")

    meta = FIG / "figure_style_meta.json"
    meta.write_text(
        json.dumps(
            {
                "serif_font": ACTIVE_SERIF,
                "style": STYLE,
                "dpi": DPI,
                "labels": "English",
                "skipped": SKIPPED,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {meta}")
    if SKIPPED:
        print("Skipped:")
        for s in SKIPPED:
            print(f"  - {s}")
    print("Done.")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()
