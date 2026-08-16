#!/usr/bin/env python
"""
Run LSG experiments on real Carlisle benchmark data.

Handles unstructured grids (581k cells) by pre-interpolating LF→HF.
Uses 2D data format: (n_timesteps, n_cells).
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.baseline_lsg import GlobalLSG
from lsg.zonal_lsg import ZonalLSG
from lsg.zoning import ZoningConfig
from lsg.metrics import extent_metrics, zone_metrics
from lsg.spatial import nearest_interp_lf_to_hf


def load_hf_data(raw_dir: Path) -> tuple:
    """Load all HF runs and return (wse, terrain, x, y, area)."""
    geo = np.load(
        raw_dir / "Geometry_data" / "Lisflood_Geometry_data.npz",
        allow_pickle=True,
    )
    hf_dir = raw_dir / "HD_model_data" / "High-fidelity"
    npz_files = sorted(hf_dir.glob("Run[1-9]_alltimesteps.npz"))
    wse_list = [np.load(f)["wse_data"] for f in npz_files]
    wse = np.vstack(wse_list)
    terrain = geo["Z_coor"]
    depth = np.maximum(0, wse - terrain[np.newaxis, :])
    return depth, terrain, geo["XY_coor"][:, 0], geo["XY_coor"][:, 1]


def load_lf_interpolated(
    raw_dir: Path,
    hf_x: np.ndarray,
    hf_y: np.ndarray,
    lf_x: np.ndarray,
    lf_y: np.ndarray,
    lf_z: np.ndarray,
) -> np.ndarray:
    """Load LF WSE from HDF5 and interpolate to HF grid using nearest-neighbour."""
    import h5py

    lf_dir = raw_dir / "HD_model_data" / "Low-fidelity"
    hdf_files = sorted(lf_dir.glob("Carlisle_LFmodelA.p*.hdf"))

    wse_list = []
    for fp in hdf_files:
        with h5py.File(fp, "r") as f:
            wse = f["Results/Unsteady/Output/Output Blocks/"
                     "Base Output/Unsteady Time Series/"
                     "2D Flow Areas/Carlisle/Water Surface"][:]
            wse_list.append(wse)

    lf_wse = np.vstack(wse_list)
    lf_interp = nearest_interp_lf_to_hf(
        lf_x, lf_y, lf_wse, hf_x, hf_y,
    )
    # Convert WSE to depth
    lf_depth = np.maximum(0, lf_interp - lf_z[np.newaxis, :])
    return lf_depth


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fold", type=int, default=1)
    parser.add_argument("--variant", default="ts", choices=["ts", "max"])
    parser.add_argument("--zoning", default="kmeans",
                        choices=["kmeans", "rule", "global"])
    parser.add_argument("--n-zones", type=int, default=4)
    parser.add_argument("--mode-budget", default="global_equal",
                        choices=["free", "global_equal"])
    parser.add_argument("--skip-lf", action="store_true",
                        help="Skip LF HDF5 loading (use noisy HF as LF)")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    raw_dir = root / "data" / "external" / "fraehr2024" / "Carlisle"
    output_dir = root / "outputs"

    # --- Load HF ---
    print("Loading HF data...")
    t0 = time.perf_counter()
    hf_depth, terrain, hf_x, hf_y = load_hf_data(raw_dir)
    n_t, n_hf = hf_depth.shape
    print(f"  HF: {n_t} timesteps, {n_hf} cells ({hf_depth.nbytes/1024**3:.1f} GB)")

    # --- Load LF (pre-interpolated to HF grid) ---
    if args.skip_lf:
        print("  Skipping LF load (using noisy-HF placeholder)")
        rng = np.random.default_rng(42)
        lf_depth = hf_depth + rng.normal(0, 0.05, hf_depth.shape)
        lf_depth = np.maximum(lf_depth, 0)
    else:
        print("Loading LF HDF5 data...")
        lf_geo = np.load(
            raw_dir / "Geometry_data" / "LF_Geometry_data.npz",
            allow_pickle=True,
        )
        lf_x, lf_y, lf_z = lf_geo["XY_coor"][:, 0], lf_geo["XY_coor"][:, 1], lf_geo["Z_coor"]
        lf_depth = load_lf_interpolated(raw_dir, hf_x, hf_y, lf_x, lf_y, terrain)
        print(f"  LF interpolated: {lf_depth.shape}")

    print(f"  Data load time: {time.perf_counter()-t0:.1f}s")

    # --- Train/test split ---
    split = np.load(
        raw_dir / "Train_test_split_data" /
        f"Train_test_split_ValidateOnGrp_{args.fold}.npz",
        allow_pickle=True,
    )
    idx_train = split["idx_train"].astype(int)
    idx_test = split["idx_test"].astype(int)
    print(f"  Train: {len(idx_train)}, Test: {len(idx_test)}")

    hf_train = hf_depth[idx_train]  # (n_train, n_hf)
    hf_test = hf_depth[idx_test]
    lf_train = lf_depth[idx_train]
    lf_test = lf_depth[idx_test]

    # Use dummy shapes (1D row) since data is unstructured
    shape_dummy = (1, n_hf)

    # --- LF-only baseline ---
    print("\n--- LF-only ---")
    lf_metrics = extent_metrics(lf_test, hf_test, 0.03)
    print(f"  RMSE={lf_metrics['rmse']:.4f}, CSI={lf_metrics['csi']:.4f}")

    # --- Global LSG ---
    print("\n--- Global LSG-TS ---")
    t0 = time.perf_counter()
    g_model = GlobalLSG(
        variant=args.variant,
        max_eof_modes=50,
        eof_variance=0.99,
        wet_threshold=0.03,
    )
    g_model.fit(
        hf_train[np.newaxis, :, :],
        lf_train[np.newaxis, :, :],
        terrain, shape_dummy, shape_dummy,
        lf_already_interpolated=True,
    )
    g_pred = g_model.predict(
        hf_test[np.newaxis, :, :],
        terrain, shape_dummy, shape_dummy,
        lf_already_interpolated=True,
    )
    g_pred_2d = g_pred.reshape(-1, n_hf)
    g_metrics = extent_metrics(g_pred_2d, hf_test, 0.03)
    g_time = time.perf_counter() - t0
    n_g_modes = g_model.state.n_modes if g_model.state else 0
    print(f"  RMSE={g_metrics['rmse']:.4f}, CSI={g_metrics['csi']:.4f}, "
          f"modes={n_g_modes}, time={g_time:.1f}s")

    # --- Zonal LSG ---
    print(f"\n--- Zonal LSG [{args.zoning}, K={args.n_zones}, "
          f"budget={args.mode_budget}] ---")
    t0 = time.perf_counter()
    zc = ZoningConfig(
        method=args.zoning,
        n_zones=args.n_zones,
        wet_threshold=0.03,
    )
    budget = None if args.mode_budget == "free" else "global_equal"

    z_model = ZonalLSG(
        zoning_config=zc,
        variant=args.variant,
        mode_budget=budget,
        max_modes_per_zone=30,
        eof_variance=0.99,
        wet_threshold=0.03,
    )
    z_model.fit(
        hf_train[np.newaxis, :, :],
        lf_train[np.newaxis, :, :],
        terrain, shape_dummy, shape_dummy,
        x_hf=hf_x, y_hf=hf_y,
    )
    z_pred = z_model.predict(
        hf_test[np.newaxis, :, :],
        terrain, shape_dummy, shape_dummy,
    )
    z_pred_2d = z_pred.reshape(-1, n_hf)
    z_metrics = extent_metrics(z_pred_2d, hf_test, 0.03)
    z_time = time.perf_counter() - t0

    # Zone stats
    zone_stats = z_model.get_zone_statistics() if z_model.state else {}
    total_z_modes = sum(v["n_modes"] for v in zone_stats.values())
    n_zones_actual = len(zone_stats)

    # Zone-level metrics
    zone_met = {}
    if z_model.state:
        zl = z_model.state.zone_labels
        am = z_model.state.active_mask
        zone_met = zone_metrics(z_pred_2d, hf_test, zl, threshold_m=0.03, active_mask=am)

    print(f"  RMSE={z_metrics['rmse']:.4f}, CSI={z_metrics['csi']:.4f}, "
          f"zones={n_zones_actual}, modes={total_z_modes}, time={z_time:.1f}s")

    # --- Summary ---
    print(f"\n{'='*60}")
    print(f"RESULTS SUMMARY — Carlisle Fold {args.fold}")
    print(f"{'='*60}")
    print(f"  LF-only:         RMSE={lf_metrics['rmse']:.4f}, CSI={lf_metrics['csi']:.4f}")
    print(f"  Global LSG:      RMSE={g_metrics['rmse']:.4f}, CSI={g_metrics['csi']:.4f} "
          f"({n_g_modes} modes)")
    print(f"  Zonal LSG:       RMSE={z_metrics['rmse']:.4f}, CSI={z_metrics['csi']:.4f} "
          f"({total_z_modes} modes, {n_zones_actual} zones)")
    impr_rmse = (g_metrics['rmse'] - z_metrics['rmse']) / g_metrics['rmse'] * 100
    impr_csi = (z_metrics['csi'] - g_metrics['csi']) * 100
    print(f"  Improvement:     ΔRMSE={impr_rmse:+.1f}%, ΔCSI={impr_csi:+.1f}pp")

    # --- Save ---
    tag = f"fold{args.fold}_{args.variant}_{args.zoning}_k{args.n_zones}_{args.mode_budget}"
    results = {
        "lf_only": lf_metrics,
        "global_lsg": {**g_metrics, "n_modes": n_g_modes, "runtime_s": g_time},
        "zonal_lsg": {
            **z_metrics,
            "total_eof_modes": total_z_modes,
            "n_zones": n_zones_actual,
            "runtime_s": z_time,
        },
        "zone_metrics": {str(k): v for k, v in zone_met.items()} if zone_met else {},
        "config": {
            "fold": args.fold,
            "variant": args.variant,
            "zoning": args.zoning,
            "n_zones": args.n_zones,
            "mode_budget": args.mode_budget,
            "n_hf_cells": n_hf,
            "n_train": len(idx_train),
            "n_test": len(idx_test),
        },
    }
    eval_dir = output_dir / "evaluation" / "carlisle"
    eval_dir.mkdir(parents=True, exist_ok=True)
    with (eval_dir / f"real_{tag}.json").open("w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Saved: {eval_dir}/real_{tag}.json")


if __name__ == "__main__":
    main()
