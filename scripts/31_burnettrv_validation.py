#!/usr/bin/env python
"""BurnettRV standard-mesh LSG validation — 20+ events, area-weighted, B=4/8.

Event-level LOOCV: scripts/32_burnettrv_loocv.py on
data/processed/burnettrv_30events.npz. This script is the 12-event
single-split validation that produced validation_std.json.
"""
import json, sys, time, glob
from pathlib import Path
import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.baseline_lsg import GlobalLSG
from lsg.zonal_lsg import ZonalLSG
from lsg.zoning import ZoningConfig
from lsg.metrics import extent_metrics
from lsg.metrics_area import area_weighted_metrics
from lsg.spatial import nearest_interp_lf_to_hf
import h5py

RAW = _ROOT / "data/external/fraehr2024/BurnettRV"
OUT = _ROOT / "outputs"

def load_burnettrv_std(max_events=20):
    """Load standard-mesh BurnettRV events as max surfaces."""
    print("Loading BurnettRV standard-mesh events...", flush=True)
    geo = np.load(RAW/"Geometry_data/Tuflow_Geometry_data.npz", allow_pickle=True)
    terrain, hf_xy, areas = geo["Z_coor"], geo["XY_coor"], geo["Area"]
    n_hf = 780785

    lf_geo = np.load(RAW/"Geometry_data/HECRAS_Geometry_data.npz", allow_pickle=True)
    lf_xy = lf_geo["XY_coor"]

    # Filter standard-mesh HF events
    hf_files = sorted(glob.glob(str(RAW/"HD_model_data/High-fidelity/*.npz")))
    lf_files = sorted(glob.glob(str(RAW/"HD_model_data/Low-fidelity/*.hdf")))

    hf_max_list, lf_max_list = [], []
    count = 0
    t0 = time.perf_counter()

    for hf_fp in hf_files:
        if count >= max_events:
            break
        # Skip extrapolation
        if "extrap" in hf_fp.lower():
            continue
        try:
            wl = np.load(hf_fp)["wl_data"]
            if wl.shape[1] != n_hf:
                continue
            depth = np.nan_to_num(np.maximum(0, wl - terrain[np.newaxis, :]), nan=0.0)
            hf_max_list.append(np.nanmax(depth, axis=0))

            # Match LF by index
            lf_idx = count % len(lf_files)
            with h5py.File(lf_files[lf_idx], "r") as f:
                wse_full = f["Results/Unsteady/Output/Output Blocks/"
                         "Base Output/Unsteady Time Series/"
                         "2D Flow Areas/BurnettRV_region/Water Surface"][:]
            # Trim to geometry cell count
            n_lf_geo = len(lf_geo["Z_coor"])
            wse = wse_full[:, :n_lf_geo]
            lf_interp = nearest_interp_lf_to_hf(
                lf_xy[:, 0], lf_xy[:, 1], wse, hf_xy[:, 0], hf_xy[:, 1]
            )
            lf_depth = np.nan_to_num(np.maximum(0, lf_interp - terrain[np.newaxis, :]), nan=0.0)
            lf_max_list.append(np.nanmax(lf_depth, axis=0))

            count += 1
            if count % 5 == 0:
                print(f"  {count} events loaded ({time.perf_counter()-t0:.0f}s)...", flush=True)
        except Exception as e:
            continue

    hf_max = np.stack(hf_max_list)
    lf_max = np.stack(lf_max_list)
    n_ev = hf_max.shape[0]
    load_time = time.perf_counter() - t0
    print(f"  {n_ev} events in {load_time:.0f}s ({load_time/n_ev:.0f}s/event)", flush=True)

    return hf_max, lf_max, terrain, areas, hf_xy, n_hf


def main():
    print("="*60)
    print("BurnettRV Standard-Mesh Validation")
    print("TUFLOW HF (781k cells) x HEC-RAS 2D LF")
    print("="*60)

    hf_max, lf_max, terrain, areas, hf_xy, n_hf = load_burnettrv_std(max_events=12)
    n_ev = hf_max.shape[0]
    wet = int((hf_max.max(axis=0) >= 0.03).sum())
    resid = np.mean(np.abs(lf_max - hf_max))
    print(f"\n{n_ev} events, {wet:,} wet, |LF-HF|={resid:.4f}m")

    # Split: 80/20
    rng = np.random.default_rng(42)
    idx = rng.permutation(n_ev)
    n_tr = int(0.8 * n_ev)
    train_idx, test_idx = idx[:n_tr], idx[n_tr:]
    sd = (1, n_hf)

    hf_tr, hf_te = hf_max[train_idx], hf_max[test_idx]
    lf_tr, lf_te = lf_max[train_idx], lf_max[test_idx]
    n_te = hf_te.shape[0]

    results = {"config": {"case": "BurnettRV", "n_events": n_ev,
               "n_train": n_tr, "n_test": n_te, "n_cells": n_hf,
               "n_wet": wet, "lf_hf_resid": float(resid)},
               "experiments": {}}

    # LF-only
    print("\n--- LF-only ---", flush=True)
    lf_as = [area_weighted_metrics(lf_te[i], hf_te[i], areas, 0.03) for i in range(n_te)]
    lf_m = {k: np.mean([m[k] for m in lf_as]) for k in lf_as[0]}
    lf_cell = extent_metrics(lf_te, hf_te, 0.03)
    print(f"  RMSE_area={lf_m['rmse_area']:.4f}, CSI_area={lf_m['csi_area']:.4f}")
    results["lf_only"] = {**lf_m, "rmse_cell": lf_cell["rmse"], "csi_cell": lf_cell["csi"]}

    configs = [
        ("Global", None, None, None),
        ("KMeans", "kmeans", 4, 4),
        ("Rule", "rule", 4, 4),
        ("Rule", "rule", 4, 8),
    ]

    for name, method, nz, budget in configs:
        print(f"\n--- {name} {'B='+str(budget) if budget else 'auto'} ---", flush=True)
        t0 = time.perf_counter()

        if name == "Global":
            g = GlobalLSG(variant="max", max_eof_modes=20, eof_variance=0.99, wet_threshold=0.03)
            g.force_n_modes = 4  # match the zonal B=4 budget for equal-capacity comparison
            g.fit(hf_tr, lf_tr, terrain, sd, sd, lf_already_interpolated=True)
            g_p = g.predict(lf_te, terrain, sd, sd, lf_already_interpolated=True)
            g_as = [area_weighted_metrics(g_p[i], hf_te[i], areas, 0.03) for i in range(n_te)]
            g_m = {k: np.mean([m[k] for m in g_as]) for k in g_as[0]}
            g_cell = extent_metrics(g_p, hf_te, 0.03)
            g_n = g.state.n_modes if g.state else 0
            dt = time.perf_counter() - t0
            results["global"] = {**g_m, "rmse_cell": g_cell["rmse"], "csi_cell": g_cell["csi"],
                                "n_modes": g_n, "time_s": dt, "time_per_event_s": dt/n_te}
            print(f"  RMSE_area={g_m['rmse_area']:.4f}, CSI_area={g_m['csi_area']:.4f}, "
                  f"modes={g_n}, time={dt:.1f}s")
        else:
            zc = ZoningConfig(method=method, n_zones=nz, wet_threshold=0.03)
            z = ZonalLSG(zoning_config=zc, variant="max", mode_budget=budget,
                         max_modes_per_zone=10, eof_variance=0.99, wet_threshold=0.03)
            z.fit(hf_tr, lf_tr, terrain, sd, sd, x_hf=hf_xy[:, 0], y_hf=hf_xy[:, 1])
            z_p = z.predict(lf_te, terrain, sd, sd)
            z_as = [area_weighted_metrics(z_p[i], hf_te[i], areas, 0.03) for i in range(n_te)]
            z_m = {k: np.mean([m[k] for m in z_as]) for k in z_as[0]}
            z_cell = extent_metrics(z_p, hf_te, 0.03)
            zs = z.get_zone_statistics() if z.state else {}
            zm = sum(v["n_modes"] for v in zs.values())
            dt = time.perf_counter() - t0
            tag = f"{name}_B{budget}" if budget else name
            results[tag] = {**z_m, "rmse_cell": z_cell["rmse"], "csi_cell": z_cell["csi"],
                           "total_modes": zm, "n_zones": len(zs), "time_s": dt,
                           "time_per_event_s": dt/n_te}

            g_rmse = results["global"]["rmse_area"]
            d_rmse = (g_rmse - z_m["rmse_area"]) / (g_rmse + 1e-12) * 100
            print(f"  RMSE_area={z_m['rmse_area']:.4f}, CSI_area={z_m['csi_area']:.4f}, "
                  f"zones={len(zs)}, modes={zm}, time={dt:.1f}s, dRMSE={d_rmse:+.1f}%")

    # Save
    eval_dir = OUT / "evaluation/burnettrv"
    eval_dir.mkdir(parents=True, exist_ok=True)
    with (eval_dir / "validation_std.json").open("w") as f:
        json.dump(results, f, indent=2)

    # Summary
    print(f"\n{'='*60}")
    print("BurnettRV Validation Summary")
    print(f"{'='*60}")
    g_rmse = results["global"]["rmse_area"]
    for tag, r in results.items():
        if tag in ("config", "lf_only", "global") or "experiments" in tag:
            continue
        if "rmse_area" not in r:
            continue
        z_rmse = r["rmse_area"]
        d = (g_rmse - z_rmse) / (g_rmse + 1e-12) * 100
        print(f"  {tag:<20} RMSE={z_rmse:.4f} dRMSE={d:+.1f}% modes={r['total_modes']} "
              f"zones={r['n_zones']} time={r['time_s']:.1f}s")
    print(f"\nGlobal: RMSE={g_rmse:.4f}, LF-only: RMSE={results['lf_only']['rmse_area']:.4f}")
    print(f"Saved: {eval_dir}/validation_std.json")


if __name__ == "__main__":
    main()
