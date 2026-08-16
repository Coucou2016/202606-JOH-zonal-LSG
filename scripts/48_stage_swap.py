#!/usr/bin/env python
"""Stage-swap mechanism experiment on Carlisle LSG-Max (B=4).

Compares GG / ZZ / GZ / ZG under the same 7/2 seed-42 split used by
scripts/30_carlisle_proper.py and scripts/43_lf_degradation.py.
Optional --loocv runs leave-one-event-out (9 folds).

Writes outputs/evaluation/carlisle/stage_swap.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.experiment import jsonable, mean_area, per_event_area
from lsg.fraehr import load_or_build_carlisle_max, repo_root
from lsg.metrics_area import area_weighted_metrics
from lsg.stage_swap import LIMITATIONS, StageId, fit_predict_stage

OUT = _ROOT / "outputs" / "evaluation" / "carlisle" / "stage_swap.json"
STAGES: list[StageId] = ["GG", "ZZ", "GZ", "ZG"]


def _eval_split(hf_tr, lf_tr, hf_te, lf_te, terrain, xy, areas, budget, stages):
    row = {}
    lf_rows = [area_weighted_metrics(lf_te[i], hf_te[i], areas, 0.03) for i in range(hf_te.shape[0])]
    row["lf_only"] = mean_area(lf_rows)
    for stage in stages:
        pred, meta = fit_predict_stage(
            hf_tr, lf_tr, hf_te, lf_te, terrain, xy, budget, stage
        )
        rows = per_event_area(pred, hf_te, areas)
        row[stage] = {**mean_area(rows), **meta, "per_event": rows}
        print(
            f"    {stage}: RMSE={row[stage]['rmse_area']:.4f} m  "
            f"modes={meta['n_modes']}  t={meta['time_s']:.1f}s",
            flush=True,
        )
    g = row["GG"]["rmse_area"]
    z = row["ZZ"]["rmse_area"]
    row["deltas_vs_GG"] = {
        s: float(g - row[s]["rmse_area"]) for s in stages if s in row
    }
    row["deltas_vs_ZZ"] = {
        s: float(z - row[s]["rmse_area"]) for s in stages if s in row
    }
    return row


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--budget", type=int, default=4)
    p.add_argument("--stages", default="GG,ZZ,GZ,ZG")
    p.add_argument("--loocv", action="store_true", help="Also run 9-fold event LOOCV")
    p.add_argument("--skip-72", action="store_true")
    args = p.parse_args()
    stages: list[StageId] = [s.strip() for s in args.stages.split(",") if s.strip()]  # type: ignore

    root = repo_root()
    print("Loading Carlisle max pack...", flush=True)
    pack = load_or_build_carlisle_max(root)
    hf, lf = pack["hf_max"], pack["lf_max"]
    terrain, areas = pack["terrain_hf"], pack["area_hf"]
    xy = np.column_stack([pack["x_hf"], pack["y_hf"]])
    n_ev = hf.shape[0]
    print(f"  {n_ev} events, {hf.shape[1]:,} cells", flush=True)

    payload = {
        "config": {
            "case": "Carlisle",
            "B": args.budget,
            "stages": stages,
            "stage_defs": {
                "GG": "global EOF + global GP",
                "ZZ": "zonal EOF + zonal GP (rule)",
                "GZ": "global EOF + zonal GP (approx)",
                "ZG": "zonal EOF + global GP (approx)",
            },
            "limitations": LIMITATIONS,
            "hypothesis": (
                "If gain is in GP mapping: GZ ≈ ZZ << GG and ZG ≈ GG. "
                "If gain is in EOF truncation: ZG ≈ ZZ << GG and GZ ≈ GG."
            ),
        },
        "split_7_2": None,
        "loocv": None,
    }

    if not args.skip_72:
        rng = np.random.default_rng(42)
        idx = rng.permutation(n_ev)
        train_idx, test_idx = idx[:7], idx[7:]
        print(f"\n=== 7/2 seed42 train={train_idx.tolist()} test={test_idx.tolist()} ===", flush=True)
        row = _eval_split(
            hf[train_idx], lf[train_idx], hf[test_idx], lf[test_idx],
            terrain, xy, areas, args.budget, stages,
        )
        payload["split_7_2"] = {
            "train_idx": train_idx.tolist(),
            "test_idx": test_idx.tolist(),
            **row,
        }
        # Quick interpretation
        d = row["deltas_vs_GG"]
        print("\n  ΔRMSE vs GG (positive = better than global):", flush=True)
        for s in stages:
            print(f"    {s}: {d[s]:+.4f} m", flush=True)

    if args.loocv:
        folds = []
        print("\n=== 9-fold event LOOCV ===", flush=True)
        for i in range(n_ev):
            train = [j for j in range(n_ev) if j != i]
            print(f"\n  Fold {i} leave-out event {i}", flush=True)
            row = _eval_split(
                hf[train], lf[train], hf[[i]], lf[[i]],
                terrain, xy, areas, args.budget, stages,
            )
            folds.append({"fold": i, **row})
        summary = {}
        for s in stages:
            rmses = np.array([f[s]["rmse_area"] for f in folds], dtype=float)
            summary[s] = {
                "mean_rmse": float(np.mean(rmses)),
                "std_rmse": float(np.std(rmses)),
            }
        if "GG" in summary and "ZZ" in summary:
            d_zz = np.array(
                [f["GG"]["rmse_area"] - f["ZZ"]["rmse_area"] for f in folds]
            )
            d_gz = np.array(
                [f["GG"]["rmse_area"] - f["GZ"]["rmse_area"] for f in folds]
            ) if "GZ" in stages else None
            d_zg = np.array(
                [f["GG"]["rmse_area"] - f["ZG"]["rmse_area"] for f in folds]
            ) if "ZG" in stages else None
            summary["n_folds_ZZ_beats_GG"] = int(np.sum(d_zz > 0))
            summary["mean_delta_ZZ"] = float(np.mean(d_zz))
            if d_gz is not None:
                summary["n_folds_GZ_beats_GG"] = int(np.sum(d_gz > 0))
                summary["mean_delta_GZ"] = float(np.mean(d_gz))
            if d_zg is not None:
                summary["n_folds_ZG_beats_GG"] = int(np.sum(d_zg > 0))
                summary["mean_delta_ZG"] = float(np.mean(d_zg))
        payload["loocv"] = {"per_fold": folds, "summary": summary}
        print("\nLOOCV summary:", json.dumps(summary, indent=2), flush=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(jsonable(payload), indent=2), encoding="utf-8")
    print("\nSaved", OUT, flush=True)


if __name__ == "__main__":
    main()
