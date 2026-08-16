#!/usr/bin/env python
"""
Run LSG on real Carlisle data with REAL LF from HDF5 (using conda Python).

Deprecated for paper numbers — use scripts/30_carlisle_proper.py.
Canonical report: scripts/95_final_submission_report.py.
"""
import sys, time, json, numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lsg.baseline_lsg import GlobalLSG
from lsg.zonal_lsg import ZonalLSG
from lsg.zoning import ZoningConfig
from lsg.metrics import extent_metrics, zone_metrics
from lsg.spatial import nearest_interp_lf_to_hf
import h5py

raw_dir = Path(__file__).resolve().parents[1] / "data/external/fraehr2024/Carlisle"
output_dir = Path(__file__).resolve().parents[1] / "outputs"

print("=== Loading Carlisle Run1 HF ===", flush=True)
t0 = time.perf_counter()

# HF
geo = np.load(raw_dir/"Geometry_data/Lisflood_Geometry_data.npz", allow_pickle=True)
wse = np.load(raw_dir/"HD_model_data/High-fidelity/Run1_alltimesteps.npz")["wse_data"]
terrain = geo["Z_coor"]
hf_x, hf_y = geo["XY_coor"][:, 0], geo["XY_coor"][:, 1]
hf_depth = np.maximum(0, wse - terrain[np.newaxis, :])
n_t, n_hf = hf_depth.shape

# LF from HDF5
print("=== Loading LF from HDF5 ===", flush=True)
lf_geo = np.load(raw_dir/"Geometry_data/LF_Geometry_data.npz", allow_pickle=True)
lf_x, lf_y = lf_geo["XY_coor"][:, 0], lf_geo["XY_coor"][:, 1]

# Load LF Run1 (p01)
with h5py.File(raw_dir/"HD_model_data/Low-fidelity/Carlisle_LFmodelA.p01.hdf", "r") as f:
    lf_wse = f["Results/Unsteady/Output/Output Blocks/"
               "Base Output/Unsteady Time Series/"
               "2D Flow Areas/Carlisle/Water Surface"][:]

print(f"  LF WSE: {lf_wse.shape} (HEC-RAS, {lf_wse.shape[1]} cells)", flush=True)
print(f"  HF cells: {n_hf}, LF cells: {lf_wse.shape[1]}", flush=True)

# Interpolate LF → HF
lf_interp = nearest_interp_lf_to_hf(lf_x, lf_y, lf_wse, hf_x, hf_y)
lf_depth = np.maximum(0, lf_interp - terrain[np.newaxis, :])

# Align timesteps (LF has 274, HF has 266)
min_t = min(n_t, lf_depth.shape[0])
hf_depth = hf_depth[:min_t]
lf_depth = lf_depth[:min_t]
print(f"  Aligned: {min_t} timesteps", flush=True)

# Train/test split
rng = np.random.default_rng(42)
idx = rng.permutation(min_t)
n_train = int(0.8 * min_t)
idx_train, idx_test = idx[:n_train], idx[n_train:]

hf_train, hf_test = hf_depth[idx_train], hf_depth[idx_test]
lf_train, lf_test = lf_depth[idx_train], lf_depth[idx_test]

shape_dummy = (1, n_hf)
results = {}

# LF-only
met_lf = extent_metrics(lf_test, hf_test, 0.03)
print(f"\nLF-only: RMSE={met_lf['rmse']:.4f}, CSI={met_lf['csi']:.4f}", flush=True)

# Compute LF-HF residual for analysis
lf_hf_resid = np.mean(np.abs(lf_depth - hf_depth), axis=0)
print(f"  Mean |LF-HF|: {np.mean(lf_hf_resid):.4f}m, 90p={np.percentile(lf_hf_resid,90):.4f}m", flush=True)

# Global LSG
print("\n=== Global LSG ===", flush=True)
t1 = time.perf_counter()
g = GlobalLSG(variant="ts", max_eof_modes=50, eof_variance=0.99, wet_threshold=0.03)
g.fit(hf_train[np.newaxis,:,:], lf_train[np.newaxis,:,:],
      terrain, shape_dummy, shape_dummy, lf_already_interpolated=True)
g_pred = g.predict(hf_test[np.newaxis,:,:], terrain,
                    shape_dummy, shape_dummy, lf_already_interpolated=True)
g_pred = g_pred.reshape(-1, n_hf)
g_met = extent_metrics(g_pred, hf_test, 0.03)
g_n = g.state.n_modes if g.state else 0
print(f"Global LSG: RMSE={g_met['rmse']:.4f}, CSI={g_met['csi']:.4f}, "
      f"modes={g_n}, time={time.perf_counter()-t1:.1f}s", flush=True)

# Zonal LSG
print("\n=== Zonal LSG (KMeans K=4, equal budget) ===", flush=True)
t1 = time.perf_counter()
zc = ZoningConfig(method="kmeans", n_zones=4, wet_threshold=0.03)
z = ZonalLSG(zoning_config=zc, variant="ts", mode_budget="global_equal",
             max_modes_per_zone=30, eof_variance=0.99, wet_threshold=0.03)
z.fit(hf_train[np.newaxis,:,:], lf_train[np.newaxis,:,:],
      terrain, shape_dummy, shape_dummy, x_hf=hf_x, y_hf=hf_y)
z_pred = z.predict(hf_test[np.newaxis,:,:], terrain,
                    shape_dummy, shape_dummy)
z_pred = z_pred.reshape(-1, n_hf)
z_met = extent_metrics(z_pred, hf_test, 0.03)
z_stats = z.get_zone_statistics() if z.state else {}
z_modes = sum(v["n_modes"] for v in z_stats.values())
z_n = len(z_stats)
print(f"Zonal LSG: RMSE={z_met['rmse']:.4f}, CSI={z_met['csi']:.4f}, "
      f"zones={z_n}, modes={z_modes}, time={time.perf_counter()-t1:.1f}s", flush=True)

# Zone metrics
if z.state:
    zone_met = zone_metrics(z_pred, hf_test, z.state.zone_labels,
                            threshold_m=0.03, active_mask=z.state.active_mask)
    print("Zone-level results:")
    for zid, zm in zone_met.items():
        print(f"  Zone {zid}: RMSE={zm['rmse']:.4f}, CSI={zm['csi']:.4f}")

# Summary
print(f"\n{'='*60}")
print(f"REAL DATA RESULTS — Carlisle (LISFLOOD-FP HF × HEC-RAS LF)")
print(f"{'='*60}")
print(f"Timesteps: {min_t}, HF cells: {n_hf}, LF cells: {lf_wse.shape[1]}")
print(f"Mean |LF-HF| residual: {np.mean(lf_hf_resid):.4f}m")
print(f"")
print(f"LF-only:          RMSE={met_lf['rmse']:.4f}, CSI={met_lf['csi']:.4f}")
print(f"Global LSG-TS:    RMSE={g_met['rmse']:.4f}, CSI={g_met['csi']:.4f} "
      f"({g_n} modes)")
print(f"Zonal LSG-TS:     RMSE={z_met['rmse']:.4f}, CSI={z_met['csi']:.4f} "
      f"({z_modes} modes, {z_n} zones)")
impr = (g_met['rmse'] - z_met['rmse']) / (g_met['rmse'] + 1e-12) * 100
csi_d = (z_met['csi'] - g_met['csi']) * 100
print(f"ΔRMSE: {impr:+.1f}%, ΔCSI: {csi_d:+.1f}pp")
print(f"Total time: {time.perf_counter()-t0:.1f}s", flush=True)

# Save
results = {
    "config": {"case": "carlisle_run1", "n_timesteps": min_t,
               "n_hf": n_hf, "n_train": n_train, "n_test": min_t-n_train,
               "lf_model": "HEC-RAS 2D", "hf_model": "LISFLOOD-FP"},
    "lf_only": met_lf,
    "global_lsg": {**g_met, "n_modes": g_n},
    "zonal_lsg": {**z_met, "total_eof_modes": z_modes, "n_zones": z_n},
    "lf_hf_residual_mean": float(np.mean(lf_hf_resid)),
}
eval_dir = output_dir / "evaluation" / "carlisle"
eval_dir.mkdir(parents=True, exist_ok=True)
with (eval_dir / "real_lf_run1.json").open("w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved: {eval_dir}/real_lf_run1.json")
