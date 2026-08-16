#!/usr/bin/env python
"""Run baseline Global LSG (TS and Max variants) on prepared case data."""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.baseline_lsg import GlobalLSG
from lsg.metrics import extent_metrics, max_surface_metrics, paired_improvement
from lsg.spatial import interpolate_lf_to_hf_grid


def load_case_data(processed_dir: Path) -> dict:
    """Load all events from processed case directory."""
    events_dir = processed_dir / "events"
    hf_ts_list, lf_ts_list, hf_max_list, lf_max_list, ids = [], [], [], [], []

    for f in sorted(events_dir.glob("*_HF_ts.npz")):
        data = np.load(f, allow_pickle=True)
        hf_ts_list.append(data["depth"])
        ids.append(str(data["event_id"]))

    for f in sorted(events_dir.glob("*_LF_ts.npz")):
        data = np.load(f, allow_pickle=True)
        lf_ts_list.append(data["depth"])

    for f in sorted(events_dir.glob("*_HF_max.npz")):
        data = np.load(f, allow_pickle=True)
        hf_max_list.append(data["max_depth"])

    for f in sorted(events_dir.glob("*_LF_max.npz")):
        data = np.load(f, allow_pickle=True)
        lf_max_list.append(data["max_depth"])

    hf_ts = np.stack(hf_ts_list)
    lf_ts = np.stack(lf_ts_list)
    hf_max = np.stack(hf_max_list)
    lf_max = np.stack(lf_max_list)

    geo = np.load(processed_dir / "geometry.npz", allow_pickle=True)
    shape_hf = geo.get("shape_hf")
    shape_lf = geo.get("shape_lf")
    if shape_hf is not None:
        shape_hf = tuple(shape_hf.tolist())
    else:
        shape_hf = (30, 40)
    if shape_lf is not None:
        shape_lf = tuple(shape_lf.tolist())
    else:
        shape_lf = (7, 10)

    return {
        "hf_ts": hf_ts, "lf_ts": lf_ts,
        "hf_max": hf_max, "lf_max": lf_max,
        "terrain_hf": geo["terrain_hf"],
        "shape_hf": shape_hf, "shape_lf": shape_lf,
        "event_ids": ids,
    }


def run_global_lsg(
    case_name: str,
    variant: str = "ts",
    fold: str = "all",
    processed_dir: Path | None = None,
    output_dir: Path | None = None,
) -> dict:
    """Run global LSG and return metrics."""
    root = Path(__file__).resolve().parents[1]
    processed_dir = processed_dir or (root / "data" / "processed" / case_name)
    output_dir = output_dir or (root / "outputs")

    data = load_case_data(processed_dir)
    hf_ts, lf_ts = data["hf_ts"], data["lf_ts"]
    hf_max, lf_max = data["hf_max"], data["lf_max"]
    terrain = data["terrain_hf"]
    shape_hf, shape_lf = data["shape_hf"], data["shape_lf"]
    n_events = len(data["event_ids"])

    # Train/val split
    splits_dir = processed_dir / "splits"
    if (splits_dir / "fold_00.json").exists():
        split_data = np.load(splits_dir / "fold_00.json", allow_pickle=True)
        train_idx = split_data["train"].astype(int)
        val_idx = split_data["val"].astype(int)
    else:
        rng = np.random.default_rng(42)
        idx = rng.permutation(n_events)
        n_train = int(0.8 * n_events)
        train_idx = idx[:n_train]
        val_idx = idx[n_train:]

    train_idx_all = train_idx if fold == "all" else train_idx
    val_idx_all = val_idx if fold == "all" else val_idx

    # Prepare training data
    hf_train = hf_ts[train_idx_all]
    lf_train = lf_ts[train_idx_all]
    hf_val = hf_ts[val_idx_all]
    lf_val = lf_ts[val_idx_all]

    results = {}

    # --- LF-only baseline ---
    t0 = time.perf_counter()
    lf_val_interp = interpolate_lf_to_hf_grid(
        lf_val.reshape(-1, lf_val.shape[-1]), shape_lf, shape_hf, terrain
    )
    hf_val_flat = hf_val.reshape(-1, hf_val.shape[-1])
    lf_time = time.perf_counter() - t0
    lf_metrics = extent_metrics(lf_val_interp, hf_val_flat, 0.03)
    lf_metrics["runtime_s"] = lf_time
    results["lf_only"] = lf_metrics

    # --- Global LSG ---
    model = GlobalLSG(
        variant=variant,
        weight_by_cell_area=True,
        max_eof_modes=100,
        eof_variance=0.99,
        inducing_point_fraction=0.02,
        wet_threshold=0.03,
    )

    print(f"Fitting Global LSG-{variant.upper()} on {case_name} ({len(train_idx_all)} train events)...")
    model.fit(hf_train, lf_train, terrain, shape_hf, shape_lf)

    print(f"Predicting on {len(val_idx_all)} validation events...")
    if variant == "ts":
        pred = model.predict(lf_val, terrain, shape_hf, shape_lf)
        pred_flat = pred.reshape(-1, shape_hf[0] * shape_hf[1])
        ts_metrics = extent_metrics(pred_flat, hf_val_flat, 0.03)
        max_metrics = max_surface_metrics(pred, hf_val, 0.03)
        metrics = {f"ts_{k}": v for k, v in ts_metrics.items()}
        metrics.update({f"max_{k}": v for k, v in max_metrics.items()})
    else:
        pred = model.predict(lf_val, terrain, shape_hf, shape_lf)
        hf_val_max = hf_val.max(axis=1)
        metrics = extent_metrics(pred, hf_val_max, 0.03)

    metrics["runtime_s"] = model.state.training_time_s if model.state else 0
    metrics["n_modes"] = model.state.n_modes if model.state else 0
    results[f"global_lsg_{variant}"] = metrics

    # --- Save ---
    pred_dir = output_dir / "predictions" / case_name
    pred_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        pred_dir / f"global_lsg_{variant}_fold{fold}.npz",
        predictions=pred.reshape(-1, shape_hf[0] * shape_hf[1]),
        event_ids=np.array(data["event_ids"])[val_idx_all],
    )

    eval_dir = output_dir / "evaluation" / case_name
    eval_dir.mkdir(parents=True, exist_ok=True)
    with (eval_dir / f"global_lsg_{variant}_fold{fold}_metrics.json").open("w") as f:
        json.dump(results, f, indent=2)

    print(f"Global LSG-{variant.upper()} results for {case_name}:")
    for k, v in results.items():
        if isinstance(v, dict):
            rmse_val = v.get("rmse", v.get("ts_rmse", "N/A"))
            csi_val = v.get("csi", v.get("ts_csi", "N/A"))
            print(f"  {k}: RMSE={rmse_val:.4f}, CSI={csi_val:.4f}")
        else:
            print(f"  {k}: {v:.4f}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Run global LSG baseline")
    parser.add_argument("--case", required=True,
                        choices=["carlisle", "chowilla", "burnettrv", "brisbane", "all"])
    parser.add_argument("--variant", default="ts", choices=["ts", "max"])
    parser.add_argument("--fold", default="all")
    args = parser.parse_args()

    cases = ["carlisle", "chowilla", "burnettrv"] if args.case == "all" else [args.case]

    for case in cases:
        run_global_lsg(case, variant=args.variant, fold=args.fold)


if __name__ == "__main__":
    main()
