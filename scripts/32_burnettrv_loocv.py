#!/usr/bin/env python
"""BurnettRV event-level LOOCV on the real 30-event max-surface NPZ.

Loads data/processed/burnettrv_30events.npz (HF/LF already on the HF mesh)
plus TUFLOW/HEC-RAS geometry. Writes outputs/evaluation/burnettrv/loocv_results.json
incrementally so a run can resume.

Usage:
  python scripts/32_burnettrv_loocv.py --dry-run
  python scripts/32_burnettrv_loocv.py --with-kmeans
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.baseline_lsg import GlobalLSG
from lsg.metrics_area import area_weighted_metrics
from lsg.zonal_lsg import ZonalLSG
from lsg.zoning import ZoningConfig

NPZ = _ROOT / "data" / "processed" / "burnettrv_30events.npz"
RAW = _ROOT / "data" / "external" / "fraehr2024" / "BurnettRV"
OUT = _ROOT / "outputs" / "evaluation" / "burnettrv" / "loocv_results.json"


def load_pack():
    z = np.load(NPZ, allow_pickle=True)
    hf_max, lf_max = z["hf_max"], z["lf_max"]
    geo = np.load(RAW / "Geometry_data" / "Tuflow_Geometry_data.npz", allow_pickle=True)
    terrain, hf_xy, areas = geo["Z_coor"], geo["XY_coor"], geo["Area"]
    n_hf = int(terrain.shape[0])
    if hf_max.shape[1] != n_hf:
        raise ValueError(f"NPZ n_cells={hf_max.shape[1]} != geometry {n_hf}")
    return hf_max, lf_max, terrain, areas, hf_xy, n_hf


def _one_model(hf_tr, lf_tr, hf_te, lf_te, terrain, areas, hf_xy, n_hf, name, budget):
    sd = (1, n_hf)
    t0 = time.perf_counter()
    if name == "global":
        m = GlobalLSG(variant="max", max_eof_modes=30, eof_variance=0.99, wet_threshold=0.03)
        m.force_n_modes = budget
        m.fit(hf_tr, lf_tr, terrain, sd, sd, lf_already_interpolated=True)
        pred = m.predict(lf_te, terrain, sd, sd, lf_already_interpolated=True)
        n_modes = int(m.state.n_modes) if m.state else 0
    else:
        zc = ZoningConfig(method=name, n_zones=4, wet_threshold=0.03)
        m = ZonalLSG(
            zoning_config=zc, variant="max", mode_budget=budget,
            max_modes_per_zone=10, eof_variance=0.99, wet_threshold=0.03,
        )
        m.fit(hf_tr, lf_tr, terrain, sd, sd, x_hf=hf_xy[:, 0], y_hf=hf_xy[:, 1])
        pred = m.predict(lf_te, terrain, sd, sd)
        zs = m.get_zone_statistics() if m.state else {}
        n_modes = int(sum(v["n_modes"] for v in zs.values())) if zs else 0
    met = area_weighted_metrics(pred[0], hf_te[0], areas, 0.03)
    met["n_modes"] = n_modes
    met["time_s"] = time.perf_counter() - t0
    return met


def _summarize(per_event, models):
    summary = {}
    for name in models:
        deltas = np.array(
            [e["global"]["rmse_area"] - e[name]["rmse_area"] for e in per_event],
            dtype=float,
        )
        n = len(deltas)
        rng = np.random.default_rng(42)
        boot = [float(np.mean(rng.choice(deltas, size=n, replace=True))) for _ in range(10000)]
        ci_lo, ci_hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
        summary[name] = {
            "n_folds": n,
            "mean_global_rmse": float(np.mean([e["global"]["rmse_area"] for e in per_event])),
            "mean_zonal_rmse": float(np.mean([e[name]["rmse_area"] for e in per_event])),
            "mean_delta_rmse": float(np.mean(deltas)),
            "improved_fraction": float(np.mean(deltas > 0)),
            "n_improved": int(np.sum(deltas > 0)),
            "ci_95_lower": ci_lo,
            "ci_95_upper": ci_hi,
            "significant": bool(ci_lo > 0),
        }
    return summary


def save(payload):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def main():
    p = argparse.ArgumentParser(description="BurnettRV event-level LOOCV")
    p.add_argument("--dry-run", action="store_true", help="Run fold 0 only")
    p.add_argument("--n-events", type=int, default=None, help="Use first N events (default: all 30)")
    p.add_argument("--with-kmeans", action="store_true")
    p.add_argument("--budget", type=int, default=4)
    p.add_argument("--start-fold", type=int, default=0)
    args = p.parse_args()

    if not NPZ.exists():
        raise SystemExit(f"Missing {NPZ}; fall back to scripts/31_burnettrv_validation.py loader")

    print("Loading", NPZ, flush=True)
    t_load = time.perf_counter()
    hf_max, lf_max, terrain, areas, hf_xy, n_hf = load_pack()
    n_all = hf_max.shape[0]
    n_ev = args.n_events or n_all
    hf_max, lf_max = hf_max[:n_ev], lf_max[:n_ev]
    print(f"  {n_ev}/{n_all} events, {n_hf:,} cells in {time.perf_counter()-t_load:.1f}s", flush=True)

    models = ["rule"]
    if args.with_kmeans:
        models.append("kmeans")

    folds = [0] if args.dry_run else list(range(args.start_fold, n_ev))
    payload = {
        "config": {
            "case": "BurnettRV",
            "source_npz": str(NPZ.relative_to(_ROOT)),
            "n_events": n_ev,
            "n_events_in_npz": n_all,
            "n_cells": n_hf,
            "B": args.budget,
            "models": ["global"] + models,
            "dry_run": bool(args.dry_run),
            "area_weighted": True,
        },
        "per_event": [],
    }
    if OUT.exists() and not args.dry_run and args.start_fold == 0:
        try:
            prev = json.loads(OUT.read_text(encoding="utf-8"))
            done = {e["fold"] for e in prev.get("per_event", [])}
            payload["per_event"] = [e for e in prev["per_event"] if e["fold"] < n_ev]
            folds = [i for i in folds if i not in done]
            print(f"  resume: {len(done)} folds already saved, {len(folds)} remaining", flush=True)
        except Exception:
            pass

    for i in folds:
        train = [j for j in range(n_ev) if j != i]
        hf_tr, lf_tr = hf_max[train], lf_max[train]
        hf_te, lf_te = hf_max[[i]], lf_max[[i]]
        row = {"fold": i, "test_event": i, "B": args.budget}
        print(f"\nFold {i}/{n_ev-1} (train {len(train)})", flush=True)
        g = _one_model(hf_tr, lf_tr, hf_te, lf_te, terrain, areas, hf_xy, n_hf, "global", args.budget)
        row["global"] = g
        row["lf_only"] = area_weighted_metrics(lf_te[0], hf_te[0], areas, 0.03)
        print(f"  global RMSE={g['rmse_area']:.4f} CSI={g['csi_area']:.4f} "
              f"modes={g['n_modes']} {g['time_s']:.1f}s", flush=True)
        for name in models:
            z = _one_model(hf_tr, lf_tr, hf_te, lf_te, terrain, areas, hf_xy, n_hf, name, args.budget)
            row[name] = z
            d = g["rmse_area"] - z["rmse_area"]
            print(f"  {name:6} RMSE={z['rmse_area']:.4f} CSI={z['csi_area']:.4f} "
                  f"modes={z['n_modes']} dRMSE={d:+.4f} {z['time_s']:.1f}s", flush=True)
        payload["per_event"] = [e for e in payload["per_event"] if e["fold"] != i] + [row]
        payload["per_event"].sort(key=lambda e: e["fold"])
        payload["summary"] = _summarize(payload["per_event"], models)
        save(payload)

    payload["summary"] = _summarize(payload["per_event"], models)
    save(payload)
    print("\nSaved", OUT)
    for name, s in payload["summary"].items():
        print(f"  {name}: n={s['n_folds']} mean_dRMSE={s['mean_delta_rmse']:+.4f} "
              f"improved={s['n_improved']}/{s['n_folds']} sig={s['significant']} "
              f"CI=[{s['ci_95_lower']:+.4f},{s['ci_95_upper']:+.4f}]")


if __name__ == "__main__":
    main()
