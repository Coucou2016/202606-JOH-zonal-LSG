#!/usr/bin/env python
"""LSG-Max ablation on BurnettRV real data (TUFLOW x HEC-RAS, 76 events)."""
import json, sys, time, h5py, glob
from pathlib import Path
import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.baseline_lsg import GlobalLSG
from lsg.zonal_lsg import ZonalLSG
from lsg.zoning import ZoningConfig
from lsg.metrics import extent_metrics, zone_metrics, error_hotspot_metrics
from lsg.spatial import nearest_interp_lf_to_hf

RAW = _ROOT / "data/external/fraehr2024/BurnettRV"
OUT = _ROOT / "outputs"

def load_burnettrv():
    """Load all BurnettRV events as max depth surfaces."""
    print("Loading BurnettRV...", flush=True)

    # Geometry
    hf_geo = np.load(RAW/"Geometry_data/Tuflow_Geometry_data.npz", allow_pickle=True)
    lf_geo = np.load(RAW/"Geometry_data/HECRAS_Geometry_data.npz", allow_pickle=True)
    terrain = hf_geo["Z_coor"]
    hf_xy = hf_geo["XY_coor"]
    lf_xy = lf_geo["XY_coor"]

    # HF: NPZ format
    hf_files = sorted(glob.glob(str(RAW/"HD_model_data/High-fidelity/*.npz")))
    hf_max = []
    for f in hf_files:
        wl = np.load(f)["wl_data"]  # water level
        depth = np.maximum(0, wl - terrain[np.newaxis, :])
        hf_max.append(depth.max(axis=0))
    hf_max = np.stack(hf_max)
    n_ev, n_hf = hf_max.shape
    n_hf_cells_orig = n_hf

    # LF: HDF5 format
    lf_files = sorted(glob.glob(str(RAW/"HD_model_data/Low-fidelity/*.hdf")))
    lf_max = []
    for fp in lf_files:
        with h5py.File(fp, "r") as f:
            wse = f["Results/Unsteady/Output/Output Blocks/"
                     "Base Output/Unsteady Time Series/"
                     "2D Flow Areas/BurnettRV_region/Water Surface"][:]
        lf_interp = nearest_interp_lf_to_hf(
            lf_xy[:, 0], lf_xy[:, 1], wse, hf_xy[:, 0], hf_xy[:, 1]
        )
        lf_depth = np.maximum(0, lf_interp - terrain[np.newaxis, :])
        lf_max.append(lf_depth.max(axis=0))
    # Align LF count with HF
    lf_max = lf_max[:n_ev]
    lf_max = np.stack(lf_max)

    resid = np.mean(np.abs(lf_max - hf_max), axis=0)
    print(f"  HF max: {hf_max.shape} ({hf_max.nbytes/1e9:.1f} GB)")
    print(f"  LF max: {lf_max.shape}")
    print(f"  Mean |LF-HF|: {np.mean(resid):.4f}m")
    print(f"  Wet cells: {(hf_max.max(axis=0)>=0.03).sum():,}", flush=True)

    return hf_max, lf_max, terrain, hf_xy, resid

def run_exp(hf_max, lf_max, terrain, hf_xy, method, k, budget, train_idx, test_idx):
    """Run one LSG-Max config."""
    hf_tr, hf_te = hf_max[train_idx], hf_max[test_idx]
    lf_tr, lf_te = lf_max[train_idx], lf_max[test_idx]
    n_hf = hf_max.shape[1]
    shape_d = (1, n_hf)

    # LF-only
    lf_m = extent_metrics(lf_te, hf_te, 0.03)

    # Global LSG-Max
    g = GlobalLSG(variant="max", max_eof_modes=30, eof_variance=0.99, wet_threshold=0.03)
    g.fit(hf_tr, lf_tr, terrain, shape_d, shape_d, lf_already_interpolated=True)
    g_p = g.predict(lf_te, terrain, shape_d, shape_d, lf_already_interpolated=True)
    g_m = extent_metrics(g_p, hf_te, 0.03)
    g_n = g.state.n_modes if g.state else 0

    # Zonal LSG-Max
    zc = ZoningConfig(method=method, n_zones=k, wet_threshold=0.03)
    budget = None if budget == "free" else "global_equal"
    z = ZonalLSG(zoning_config=zc, variant="max", mode_budget=budget,
                 max_modes_per_zone=20, eof_variance=0.99, wet_threshold=0.03)
    z.fit(hf_tr, lf_tr, terrain, shape_d, shape_d,
          x_hf=hf_xy[:, 0], y_hf=hf_xy[:, 1])
    z_p = z.predict(lf_te, terrain, shape_d, shape_d)
    z_m = extent_metrics(z_p, hf_te, 0.03)
    zs = z.get_zone_statistics() if z.state else {}
    z_modes = sum(v["n_modes"] for v in zs.values())
    zn = len(zs)

    # Zone metrics & hotspot
    zone_met = {}
    hotspot = {}
    if z.state:
        zone_met = zone_metrics(z_p, hf_te, z.state.zone_labels,
                                threshold_m=0.03, active_mask=z.state.active_mask)
        hotspot = error_hotspot_metrics(z_p, hf_te,
                                        error_baseline=np.abs(lf_te-hf_te),
                                        hotspot_percentile=90)

    return {
        "lf_rmse": lf_m["rmse"], "lf_csi": lf_m["csi"],
        "g_rmse": g_m["rmse"], "g_csi": g_m["csi"], "g_modes": g_n,
        "z_rmse": z_m["rmse"], "z_csi": z_m["csi"],
        "z_modes": z_modes, "z_zones": zn,
        "zone_metrics": {str(k2): v for k2, v in zone_met.items()},
        "hotspot": hotspot,
    }

def main():
    print("="*60)
    print("BurnettRV LSG-Max Ablation (76 events, 781k cells)")
    print("="*60)

    hf_max, lf_max, terrain, hf_xy, resid = load_burnettrv()
    n_ev = hf_max.shape[0]

    # 80/20 split by event
    rng = np.random.default_rng(42)
    idx = rng.permutation(n_ev)
    n_train = int(0.8 * n_ev)
    train_idx = idx[:n_train]
    test_idx = idx[n_train:]

    results = {"config": {"case": "BurnettRV", "n_events": n_ev,
                           "n_train": n_train, "n_test": n_ev-n_train,
                           "n_hf": hf_max.shape[1],
                           "mean_lf_hf_resid": float(np.mean(resid))},
               "experiments": {}}

    configs = []
    for method in ["kmeans", "rule"]:
        for k in [2, 4, 6]:
            for budget in ["free", "global_equal"]:
                configs.append((method, k, budget))

    print(f"\nRunning {len(configs)} configs...", flush=True)
    for method, k, budget in configs:
        tag = f"{method}_k{k}_{budget}"
        t0 = time.perf_counter()
        try:
            r = run_exp(hf_max, lf_max, terrain, hf_xy, method, k, budget, train_idx, test_idx)
            d_rmse = (r["g_rmse"] - r["z_rmse"]) / (r["g_rmse"] + 1e-12) * 100
            d_csi = (r["z_csi"] - r["g_csi"]) * 100
            results["experiments"][tag] = r
            print(f"  {tag:<25} G: RMSE={r['g_rmse']:.4f} CSI={r['g_csi']:.4f} | "
                  f"Z: RMSE={r['z_rmse']:.4f} CSI={r['z_csi']:.4f} | "
                  f"dRMSE={d_rmse:+.1f}% dCSI={d_csi:+.1f}pp | {time.perf_counter()-t0:.0f}s", flush=True)
        except Exception as e:
            print(f"  {tag}: FAILED - {e}", flush=True)

    # Save
    eval_dir = OUT / "evaluation" / "burnettrv"
    eval_dir.mkdir(parents=True, exist_ok=True)
    with (eval_dir / "lsg_max_ablation.json").open("w") as f:
        json.dump(results, f, indent=2)

    # Summary
    print(f"\n=== BurnettRV Summary ===")
    for tag, exp in results["experiments"].items():
        if "global_equal" in tag:
            d = (exp["g_rmse"]-exp["z_rmse"])/(exp["g_rmse"]+1e-12)*100
            print(f"  {tag}: dRMSE={d:+.1f}%")

    print(f"\nSaved: {eval_dir}/lsg_max_ablation.json")

if __name__ == "__main__":
    main()
