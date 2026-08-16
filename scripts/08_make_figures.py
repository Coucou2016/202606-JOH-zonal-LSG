#!/usr/bin/env python
"""Generate paper figures from Track B evaluation JSON + registry.

Deprecated for citable figures: use scripts/97_scienceplots_figures.py
(SciencePlots 2.2, science+ieee+no-latex, Times New Roman, English labels).
This file is kept so older docs do not break.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))


plt.rcParams.update({
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def fig01_workflow(output_dir: Path):
    """Figure 1: Method framework diagram (schematic)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.set_title("Global LSG (Baseline)", fontweight="bold")
    steps = [
        "LF → HF grid\nprojection",
        "Global EOF\n(all cells)",
        "GP: LF ECs\n→ HF ECs",
        "HF\nreconstruction",
    ]
    y_positions = [0.8, 0.6, 0.4, 0.2]
    colors = ["#E8F5E9", "#C8E6C9", "#A5D6A7", "#81C784"]
    for y, step, color in zip(y_positions, steps, colors):
        ax1.add_patch(plt.Rectangle((0.1, y - 0.07), 0.8, 0.12, facecolor=color,
                                      edgecolor="black", linewidth=1))
        ax1.text(0.5, y, step, ha="center", va="center", fontsize=9)
    for i in range(len(steps) - 1):
        ax1.annotate("", xy=(0.5, y_positions[i + 1] + 0.07),
                      xytext=(0.5, y_positions[i] - 0.07),
                      arrowprops=dict(arrowstyle="->", lw=1.5))
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis("off")

    ax2.set_title("Zonal LSG (Proposed)", fontweight="bold")
    steps_z = [
        "Hydrodynamic\nzoning",
        "Zone-specific\nEOF",
        "Zone-specific\nGP mapping",
        "Merged HF\nreconstruction",
    ]
    colors_z = ["#E3F2FD", "#BBDEFB", "#90CAF9", "#64B5F6"]
    for y, step, color in zip(y_positions, steps_z, colors_z):
        ax2.add_patch(plt.Rectangle((0.1, y - 0.07), 0.8, 0.12, facecolor=color,
                                      edgecolor="black", linewidth=1))
        ax2.text(0.5, y, step, ha="center", va="center", fontsize=9)
    for i in range(len(steps_z) - 1):
        ax2.annotate("", xy=(0.5, y_positions[i + 1] + 0.07),
                      xytext=(0.5, y_positions[i] - 0.07),
                      arrowprops=dict(arrowstyle="->", lw=1.5))
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis("off")

    fig.suptitle("Figure 1: Comparison of Global LSG and Zonal LSG workflows",
                 fontweight="bold", y=1.01)
    plt.tight_layout()
    out = output_dir / "figures" / "fig01_workflow.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved {out}")


def fig03_mode_budget(output_dir: Path, eval_dir: Path):
    """Carlisle true equal-budget RMSE vs B from budget_sweep_true_equal.json."""
    path = eval_dir / "carlisle" / "budget_sweep_true_equal.json"
    if not path.exists():
        print(f"Skip fig03_mode_budget: missing {path}")
        return
    cb = _load_json(path)
    Bs, g, r, k = [], [], [], []
    for B in ["4", "6", "8"]:
        Bs.append(int(B))
        g.append(cb["budgets"][B]["global"]["rmse_area"])
        r.append(cb["budgets"][B]["rule"]["rmse_area"])
        k.append(cb["budgets"][B]["kmeans"]["rmse_area"])
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(Bs, g, "o-", label="Global", linewidth=2)
    ax.plot(Bs, r, "s--", label="Rule zonal", linewidth=2)
    ax.plot(Bs, k, "^:", label="KMeans zonal", linewidth=2)
    ax.set_xlabel("Mode budget B")
    ax.set_ylabel("Area-weighted RMSE (m)")
    ax.set_title("Carlisle true equal-budget RMSE vs B")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xticks(Bs)
    out = output_dir / "figures" / "fig03_mode_budget.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved {out}")


def fig04_three_case(output_dir: Path, registry: Path):
    """Three-case RMSE from result_manifest_v4.csv."""
    if not registry.exists():
        print(f"Skip fig04_three_case: missing {registry}")
        return
    with registry.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    def pick(case, model, b=None):
        for r in rows:
            if r["case"] == case and r["model"] == model:
                if b is None or str(r["B_requested"]) == str(b):
                    return float(r["rmse_area"])
        return np.nan

    cases = ["Carlisle", "Chowilla", "BurnettRV"]
    lf = [pick(c, "LF-only") for c in cases]
    glob = [pick("Carlisle", "global", 4), pick("Chowilla", "global", 4),
            pick("BurnettRV", "global")]
    zonal = [pick("Carlisle", "rule", 4), pick("Chowilla", "rule", 4),
             pick("BurnettRV", "Rule_B4")]

    x = np.arange(len(cases))
    w = 0.25
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - w, lf, w, label="LF-only")
    ax.bar(x, glob, w, label="Global LSG (B=4)")
    ax.bar(x + w, zonal, w, label="Zonal Rule (B=4)")
    ax.set_xticks(x)
    ax.set_xticklabels(cases)
    ax.set_ylabel("Area-weighted RMSE (m)")
    ax.set_title("Three-case RMSE (registry v4)")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    out = output_dir / "figures" / "fig04_three_case.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved {out}")


def fig08_loocv(output_dir: Path, eval_dir: Path):
    """Per-event LOOCV deltas from loocv_results.json (B=4)."""
    path = eval_dir / "carlisle" / "loocv_results.json"
    if not path.exists():
        print(f"Skip fig08_loocv: missing {path}")
        return
    loocv = _load_json(path)
    items = [e for e in loocv["per_event"] if e["B"] == 4]
    folds = [e["fold"] for e in items]
    g = [e["global_rmse"] for e in items]
    z = [e["zonal_rmse"] for e in items]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(folds, g, "o-", label="Global B=4")
    ax.plot(folds, z, "s--", label="Rule zonal B=4")
    ax.set_xlabel("Left-out event")
    ax.set_ylabel("Area-weighted RMSE (m)")
    ax.set_title("Carlisle 9-fold LOOCV (B=4)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    out = output_dir / "figures" / "fig08_per_event_bootstrap.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved {out}")


def make_all_figures(output_dir: Path, eval_dir: Path, registry: Path):
    fig01_workflow(output_dir)
    fig03_mode_budget(output_dir, eval_dir)
    fig04_three_case(output_dir, registry)
    fig08_loocv(output_dir, eval_dir)
    skip = output_dir / "figures" / "fig02_zone_maps_real.png"
    if skip.exists():
        print(f"Kept existing {skip} (not overwritten)")


def main():
    parser = argparse.ArgumentParser(description="Generate paper figures from Track B artefacts")
    parser.add_argument("--case", default="all",
                        choices=["carlisle", "chowilla", "burnettrv", "all"])
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    output_dir = Path(args.output_dir) if args.output_dir else (root / "outputs")
    eval_dir = output_dir / "evaluation"
    registry = output_dir / "registry" / "result_manifest_v4.csv"
    make_all_figures(output_dir, eval_dir, registry)
    print(f"Figures in {output_dir / 'figures'}")


if __name__ == "__main__":
    main()
