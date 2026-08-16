#!/usr/bin/env python
"""Run Zonal LSG experiments with multiple zoning methods and mode budgets."""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.zonal_lsg import ZonalLSG
from lsg.zoning import ZoningConfig
from lsg.metrics import (
    extent_metrics,
    max_surface_metrics,
    zone_metrics,
    error_hotspot_metrics,
    paired_improvement,
)
from lsg.spatial import interpolate_lf_to_hf_grid


def load_case_data(processed_dir: Path) -> dict:
    events_dir = processed_dir / "events"
    hf_ts_list, lf_ts_list, ids = [], [], []

    for f in sorted(events_dir.glob("*_HF_ts.npz")):
        data = np.load(f, allow_pickle=True)
        hf_ts_list.append(data["depth"])
        ids.append(str(data["event_id"]))
    for f in sorted(events_dir.glob("*_LF_ts.npz")):
        lf_ts_list.append(np.load(f, allow_pickle=True)["depth"])

    hf_ts = np.stack(hf_ts_list)
    lf_ts = np.stack(lf_ts_list)
    geo = np.load(processed_dir / "geometry.npz", allow_pickle=True)
    shape_hf = tuple(geo.get("shape_hf", np.array([30, 40])).tolist())
    shape_lf = tuple(geo.get("shape_lf", np.array([7, 10])).tolist())

    return {
        "hf_ts": hf_ts, "lf_ts": lf_ts,
        "terrain_hf": geo["terrain_hf"],
        "x_hf": geo.get("x_hf", np.arange(shape_hf[0] * shape_hf[1])),
        "y_hf": geo.get("y_hf", np.arange(shape_hf[0] * shape_hf[1])),
        "shape_hf": shape_hf, "shape_lf": shape_lf,
        "event_ids": ids,
    }


def run_zonal_lsg(
    case_name: str,
    variant: str = "ts",
    zoning_method: str = "kmeans",
    n_zones: int = 4,
    mode_budget: str = "free",  # "free" or "global_equal"
    fold: str = "all",
    processed_dir: Path | None = None,
    output_dir: Path | None = None,
) -> dict:
    root = Path(__file__).resolve().parents[1]
    processed_dir = processed_dir or (root / "data" / "processed" / case_name)
    output_dir = output_dir or (root / "outputs")

    data = load_case_data(processed_dir)
    hf_ts, lf_ts = data["hf_ts"], data["lf_ts"]
    terrain = data["terrain_hf"]
    shape_hf, shape_lf = data["shape_hf"], data["shape_lf"]
    n_events = len(data["event_ids"])

    # Split
    splits_dir = processed_dir / "splits"
    if (splits_dir / "fold_00.json").exists():
        split_data = np.load(splits_dir / "fold_00.json", allow_pickle=True)
        train_idx = split_data["train"].astype(int)
        val_idx = split_data["val"].astype(int)
    else:
        rng = np.random.default_rng(42)
        idx = rng.permutation(n_events)
        train_idx = idx[:int(0.8 * n_events)]
        val_idx = idx[int(0.8 * n_events):]

    hf_train = hf_ts[train_idx]
    lf_train = lf_ts[train_idx]
    hf_val = hf_ts[val_idx]
    lf_val = lf_ts[val_idx]

    # Build zoning config
    zc = ZoningConfig(
        method=zoning_method,
        n_zones=n_zones,
        wet_threshold=0.03,
        random_state=42,
    )

    # Determine mode budget
    budget = None if mode_budget == "free" else "global_equal"

    # Fit zonal LSG
    print(f"Fitting Zonal LSG-{variant.upper()} [{zoning_method}, K={n_zones}, "
          f"budget={mode_budget}] on {case_name}...")
    t0 = time.perf_counter()

    model = ZonalLSG(
        zoning_config=zc,
        variant=variant,
        mode_budget=budget,
        wet_threshold=0.03,
    )
    model.fit(
        hf_train, lf_train, terrain, shape_hf, shape_lf,
        x_hf=data["x_hf"], y_hf=data["y_hf"],
    )

    fit_time = time.perf_counter() - t0

    # Predict
    t1 = time.perf_counter()
    pred = model.predict(lf_val, terrain, shape_hf, shape_lf)
    pred_time = time.perf_counter() - t1

    # Metrics
    hf_val_flat = hf_val.reshape(-1, shape_hf[0] * shape_hf[1])
    pred_flat = pred.reshape(-1, shape_hf[0] * shape_hf[1])

    if variant == "ts":
        ts_metrics = extent_metrics(pred_flat, hf_val_flat, 0.03)
        max_metrics = max_surface_metrics(pred, hf_val, 0.03)
        metrics = {f"ts_{k}": v for k, v in ts_metrics.items()}
        metrics.update({f"max_{k}": v for k, v in max_metrics.items()})
    else:
        metrics = extent_metrics(pred, hf_val.max(axis=1), 0.03)

    metrics["fit_time_s"] = fit_time
    metrics["pred_time_s"] = pred_time

    # Zone-level metrics
    if model.state is not None:
        zone_labels = model.state.zone_labels
        active = model.state.active_mask
        zone_met = zone_metrics(
            pred_flat, hf_val_flat, zone_labels, threshold_m=0.03, active_mask=active
        )
        metrics["zone_metrics"] = {str(k): v for k, v in zone_met.items()}

        # Error hotspot metrics (vs LF-only as baseline error)
        lf_val_interp = interpolate_lf_to_hf_grid(
            lf_val.reshape(-1, lf_val.shape[-1]), shape_lf, shape_hf, terrain
        )
        hotspot_met = error_hotspot_metrics(
            pred_flat[0], hf_val_flat[0],
            error_baseline=np.abs(lf_val_interp[0] - hf_val_flat[0]),
            hotspot_percentile=90,
        )
        metrics["hotspot_metrics"] = hotspot_met

        # Zone statistics
        zone_stats = model.get_zone_statistics()
        metrics["zone_stats"] = {str(k): v for k, v in zone_stats.items()}
        total_modes = sum(v["n_modes"] for v in zone_stats.values())
        metrics["total_eof_modes"] = total_modes

    # Save predictions
    pred_dir = output_dir / "predictions" / case_name
    pred_dir.mkdir(parents=True, exist_ok=True)
    tag = f"zonal_lsg_{variant}_{zoning_method}_k{n_zones}_{mode_budget}_fold{fold}"
    np.savez_compressed(
        pred_dir / f"{tag}.npz",
        predictions=pred_flat,
        zone_labels=model.state.zone_labels if model.state else np.array([]),
        event_ids=np.array(data["event_ids"])[val_idx],
    )

    # Save metrics
    eval_dir = output_dir / "evaluation" / case_name
    eval_dir.mkdir(parents=True, exist_ok=True)
    with (eval_dir / f"{tag}_metrics.json").open("w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Zonal LSG results for {case_name} [{zoning_method} K={n_zones} "
          f"budget={mode_budget}]:")
    print(f"  TS RMSE={metrics.get('ts_rmse', 'N/A'):.4f}, "
          f"TS CSI={metrics.get('ts_csi', 'N/A'):.4f}")
    print(f"  Total EOF modes: {metrics.get('total_eof_modes', 'N/A')}")
    print(f"  Fit: {fit_time:.1f}s, Predict: {pred_time:.1f}s")

    return metrics


def main():
    parser = argparse.ArgumentParser(description="Run zonal LSG experiments")
    parser.add_argument("--case", required=True,
                        choices=["carlisle", "chowilla", "burnettrv", "brisbane", "all"])
    parser.add_argument("--variant", default="ts", choices=["ts", "max"])
    parser.add_argument("--zoning", default="kmeans",
                        choices=["kmeans", "rule", "agglomerative", "global"])
    parser.add_argument("--n-zones", type=int, default=4)
    parser.add_argument("--mode-budget", default="free",
                        choices=["free", "global_equal"])
    parser.add_argument("--fold", default="all")
    args = parser.parse_args()

    cases = ["carlisle", "chowilla", "burnettrv"] if args.case == "all" else [args.case]

    for case in cases:
        run_zonal_lsg(
            case,
            variant=args.variant,
            zoning_method=args.zoning,
            n_zones=args.n_zones,
            mode_budget=args.mode_budget,
            fold=args.fold,
        )


if __name__ == "__main__":
    main()
