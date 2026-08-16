#!/usr/bin/env python
"""
Comprehensive real-data experiments on Carlisle benchmark.
All 9 events, real LF from HEC-RAS HDF5, both LSG-Max and LSG-TS.
"""
import json, sys, time, h5py
from pathlib import Path
import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.baseline_lsg import GlobalLSG
from lsg.zonal_lsg import ZonalLSG
from lsg.zoning import ZoningConfig, build_cell_features
from lsg.metrics import extent_metrics, zone_metrics, error_hotspot_metrics
from lsg.spatial import nearest_interp_lf_to_hf, wet_cell_mask

RAW = _ROOT / "data/external/fraehr2024/Carlisle"
OUT = _ROOT / "outputs"

def load_all_data():
    """Load all 9 Carlisle events: HF from NPZ, LF from HDF5."""
    print("Loading HF geometry...", flush=True)
    geo = np.load(RAW/"Geometry_data/Lisflood_Geometry_data.npz", allow_pickle=True)
    terrain = geo["Z_coor"]
    hf_x, hf_y = geo["XY_coor"][:, 0], geo["XY_coor"][:, 1]

    print("Loading HF events (9 runs)...", flush=True)
    hf_files = sorted((RAW/"HD_model_data/High-fidelity").glob("Run[1-9]_alltimesteps.npz"))
    hf_depth_list, hf_max_list = [], []
    for f in hf_files:
        wse = np.load(f)["wse_data"]  # (n_t, 581061)
        depth = np.maximum(0, wse - terrain[np.newaxis, :])
        hf_depth_list.append(depth)
        hf_max_list.append(depth.max(axis=0))
    hf_all_ts = np.vstack(hf_depth_list)  # (total_t, n_hf)
    hf_max = np.stack(hf_max_list)        # (9, n_hf)
    n_ev, n_hf = hf_max.shape
    total_t = hf_all_ts.shape[0]
    print(f"  HF: {n_ev} events, {total_t} total timesteps, {n_hf} cells", flush=True)

    # LF geometry
    lf_geo = np.load(RAW/"Geometry_data/LF_Geometry_data.npz", allow_pickle=True)
    lf_x, lf_y = lf_geo["XY_coor"][:, 0], lf_geo["XY_coor"][:, 1]

    print("Loading LF HDF5 files (HEC-RAS 2D)...", flush=True)
    lf_files = sorted((RAW/"HD_model_data/Low-fidelity").glob("Carlisle_LFmodelA.p*.hdf"))
    lf_depth_list, lf_max_list = [], []
    for fp in lf_files[:9]:  # Match 9 HF runs
        with h5py.File(fp, "r") as f:
            wse = f["Results/Unsteady/Output/Output Blocks/"
                     "Base Output/Unsteady Time Series/"
                     "2D Flow Areas/Carlisle/Water Surface"][:]
        # Interpolate LF -> HF grid
        lf_interp = nearest_interp_lf_to_hf(lf_x, lf_y, wse, hf_x, hf_y)
        lf_depth = np.maximum(0, lf_interp - terrain[np.newaxis, :])
        # Align timesteps: take min(HF_t, LF_t)
        hf_ts_for_this = hf_depth_list[len(lf_depth_list)]  # corresponding HF
        min_t = min(hf_ts_for_this.shape[0], lf_depth.shape[0])
        lf_depth_list.append(lf_depth[:min_t])
        lf_max_list.append(lf_depth.max(axis=0))
    lf_max = np.stack(lf_max_list)
    print(f"  LF: {len(lf_depth_list)} events loaded, interpolated to HF grid", flush=True)

    # Compute LF-HF residual statistics
    lf_hf_resid = np.mean(np.abs(lf_max - hf_max), axis=0)
    print(f"  Mean |LF-HF| residual: {np.mean(lf_hf_resid):.4f}m", flush=True)

    return {
        "hf_max": hf_max, "lf_max": lf_max,
        "hf_depth_list": hf_depth_list, "lf_depth_list": lf_depth_list,
        "terrain": terrain, "hf_x": hf_x, "hf_y": hf_y,
        "n_hf": n_hf, "n_ev": n_ev,
        "lf_hf_resid": lf_hf_resid,
    }


def run_lsg_max_experiment(data, train_idx, test_idx, zoning_method, n_zones, mode_budget):
    """Run LSG-Max experiment."""
    hf_tr = data["hf_max"][train_idx]
    hf_te = data["hf_max"][test_idx]
    lf_tr = data["lf_max"][train_idx]
    lf_te = data["lf_max"][test_idx]
    terrain = data["terrain"]
    n_hf = data["n_hf"]
    shape_d = (1, n_hf)

    results = {}

    # LF-only
    lf_m = extent_metrics(lf_te, hf_te, 0.03)
    results["lf_only"] = lf_m

    # Global LSG-Max
    t0 = time.perf_counter()
    g = GlobalLSG(variant="max", max_eof_modes=30, eof_variance=0.99, wet_threshold=0.03)
    g.fit(hf_tr, lf_tr, terrain, shape_d, shape_d, lf_already_interpolated=True)
    g_p = g.predict(lf_te, terrain, shape_d, shape_d, lf_already_interpolated=True)
    g_m = extent_metrics(g_p, hf_te, 0.03)
    g_n = g.state.n_modes if g.state else 0
    results["global_lsg"] = {**g_m, "n_modes": g_n, "time_s": time.perf_counter()-t0}

    # Zonal LSG-Max
    t0 = time.perf_counter()
    zc = ZoningConfig(method=zoning_method, n_zones=n_zones, wet_threshold=0.03)
    budget = None if mode_budget == "free" else "global_equal"
    z = ZonalLSG(zoning_config=zc, variant="max", mode_budget=budget,
                 max_modes_per_zone=20, eof_variance=0.99, wet_threshold=0.03)
    z.fit(hf_tr, lf_tr, terrain, shape_d, shape_d,
          x_hf=data["hf_x"], y_hf=data["hf_y"])
    z_p = z.predict(lf_te, terrain, shape_d, shape_d)
    z_m = extent_metrics(z_p, hf_te, 0.03)

    # Zone stats
    zs = z.get_zone_statistics() if z.state else {}
    z_modes = sum(v["n_modes"] for v in zs.values())
    z_nz = len(zs)

    # Zone-level metrics
    zone_met = {}
    if z.state:
        zone_met = zone_metrics(z_p, hf_te, z.state.zone_labels,
                                threshold_m=0.03, active_mask=z.state.active_mask)

    # Error hotspot
    hotspot = error_hotspot_metrics(
        z_p, hf_te, error_baseline=np.abs(lf_te - hf_te), hotspot_percentile=90
    )

    # Save zone labels for spatial plotting
    zone_labels = z.state.zone_labels if z.state else None
    active_mask = z.state.active_mask if z.state else None

    results["zonal_lsg"] = {
        **z_m, "total_eof_modes": z_modes, "n_zones": z_nz,
        "time_s": time.perf_counter()-t0,
    }
    results["zone_metrics"] = {str(k): v for k, v in zone_met.items()}
    results["hotspot"] = hotspot

    return results, zone_labels, active_mask


def main():
    print("=" * 60)
    print("COMPREHENSIVE REAL-DATA EXPERIMENT — Carlisle")
    print("HF: LISFLOOD-FP (581k cells) × LF: HEC-RAS 2D (6k cells)")
    print("=" * 60)

    data = load_all_data()
    n_ev = data["n_ev"]

    # Train/test split: 7 train, 2 test (leave-last-2-out)
    rng = np.random.default_rng(42)
    idx = rng.permutation(n_ev)
    train_idx = idx[:7]
    test_idx = idx[7:]

    all_results = {
        "config": {
            "case": "Carlisle (real)", "n_events": n_ev,
            "n_train": len(train_idx), "n_test": len(test_idx),
            "n_hf_cells": data["n_hf"],
            "hf_model": "LISFLOOD-FP", "lf_model": "HEC-RAS 2D",
            "train_events": train_idx.tolist(),
            "test_events": test_idx.tolist(),
            "lf_hf_mean_residual": float(np.mean(data["lf_hf_resid"])),
        },
        "experiments": {},
    }

    # --- Experiment 1: LSG-Max, full ablation ---
    print("\n" + "=" * 60)
    print("EXPERIMENT 1: LSG-Max Ablation (real data)")
    print("=" * 60)

    for zoning_method in ["kmeans", "rule"]:
        for n_zones in [2, 4, 6]:
            for mode_budget in ["free", "global_equal"]:
                tag = f"max_{zoning_method}_k{n_zones}_{mode_budget}"
                print(f"\n  {tag}...", flush=True)
                try:
                    res, zl, am = run_lsg_max_experiment(
                        data, train_idx, test_idx,
                        zoning_method, n_zones, mode_budget
                    )
                    all_results["experiments"][tag] = {
                        "lf_only_rmse": res["lf_only"]["rmse"],
                        "lf_only_csi": res["lf_only"]["csi"],
                        "global_rmse": res["global_lsg"]["rmse"],
                        "global_csi": res["global_lsg"]["csi"],
                        "global_modes": res["global_lsg"]["n_modes"],
                        "zonal_rmse": res["zonal_lsg"]["rmse"],
                        "zonal_csi": res["zonal_lsg"]["csi"],
                        "zonal_modes": res["zonal_lsg"]["total_eof_modes"],
                        "zonal_n_zones": res["zonal_lsg"]["n_zones"],
                        "zone_metrics": res["zone_metrics"],
                        "hotspot": res["hotspot"],
                    }
                    d_rmse = (res["global_lsg"]["rmse"] - res["zonal_lsg"]["rmse"]) / (res["global_lsg"]["rmse"] + 1e-12) * 100
                    d_csi = (res["zonal_lsg"]["csi"] - res["global_lsg"]["csi"]) * 100
                    print(f"    Global: RMSE={res['global_lsg']['rmse']:.4f}, CSI={res['global_lsg']['csi']:.4f}", flush=True)
                    print(f"    Zonal:  RMSE={res['zonal_lsg']['rmse']:.4f}, CSI={res['zonal_lsg']['csi']:.4f}", flush=True)
                    print(f"    ΔRMSE={d_rmse:+.1f}%, ΔCSI={d_csi:+.1f}pp", flush=True)
                except Exception as e:
                    print(f"    FAILED: {e}", flush=True)
                    import traceback; traceback.print_exc()

    # --- Save results ---
    eval_dir = OUT / "evaluation" / "carlisle"
    eval_dir.mkdir(parents=True, exist_ok=True)
    out_path = eval_dir / "full_real_experiment.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n\nResults saved: {out_path}")

    # --- Print summary ---
    print("\n" + "=" * 60)
    print("FINAL SUMMARY — Carlisle Real Data")
    print("=" * 60)
    for tag, exp in all_results["experiments"].items():
        if "global_equal" in tag and "kmeans" in tag:
            d_rmse = (exp["global_rmse"] - exp["zonal_rmse"]) / (exp["global_rmse"] + 1e-12) * 100
            d_csi = (exp["zonal_csi"] - exp["global_csi"]) * 100
            print(f"  {tag}:")
            print(f"    Global: RMSE={exp['global_rmse']:.4f}, CSI={exp['global_csi']:.4f} ({exp['global_modes']} modes)")
            print(f"    Zonal:  RMSE={exp['zonal_rmse']:.4f}, CSI={exp['zonal_csi']:.4f} ({exp['zonal_modes']} modes, {exp['zonal_n_zones']} zones)")
            print(f"    ΔRMSE={d_rmse:+.1f}%, ΔCSI={d_csi:+.1f}pp")

    # Save zone spatial data for mapping
    print("\nSaving zone spatial data...")
    # Re-run best config to get zone labels
    res, zl, am = run_lsg_max_experiment(
        data, train_idx, test_idx, "kmeans", 4, "global_equal"
    )
    np.savez_compressed(
        eval_dir / "zone_labels_kmeans_k4.npz",
        zone_labels=zl if zl is not None else np.array([]),
        active_mask=am if am is not None else np.array([]),
        hf_x=data["hf_x"], hf_y=data["hf_y"],
    )
    print(f"  Zone labels saved: {eval_dir}/zone_labels_kmeans_k4.npz")


if __name__ == "__main__":
    main()
