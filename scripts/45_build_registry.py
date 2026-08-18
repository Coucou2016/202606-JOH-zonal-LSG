#!/usr/bin/env python
"""Build result manifest + mode budget audit + optional EOI computation.

Canonical paper numbers: outputs/registry/result_manifest_v4.csv
EOI recompute loads Carlisle HD files — skip with --skip-eoi.
"""
import json, csv, os, sys, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(str(ROOT))

parser = argparse.ArgumentParser(description="Rebuild result registry from evaluation JSON")
parser.add_argument(
    "--skip-eoi",
    action="store_true",
    help="Do not reload Carlisle HD files to recompute EOI (keep residual_organization.csv)",
)
args, _unknown = parser.parse_known_args()

manifest_rows = []

# ---- Carlisle TRUE equal budget ----
with open("outputs/evaluation/carlisle/budget_sweep_true_equal.json") as f:
    cb = json.load(f)

for B in ["4", "6", "8"]:
    r = cb["budgets"][B]
    for model in ["global", "kmeans", "rule"]:
        d = r[model]
        manifest_rows.append(dict(
            case="Carlisle", events_used=9, events_available=9,
            split_type="random_7_2", fold_id="fold_a",
            model=model, zoning="none" if model == "global" else model,
            B_requested=int(B), modes_actual=d.get("actual_modes", B),
            area_weighted=True, leakage_audit="CLEAN_PASS",
            gp_backend="sklearn_GPR", lf_data_type="real_HDF5",
            rmse_area=round(d["rmse_area"], 4), csi_area=round(d.get("csi_area", 0), 4),
            status="complete",
            notes="TRUE equal budget: force_n_modes for Global"
        ))

# ---- Chowilla ----
with open("outputs/evaluation/chowilla/budget_sweep_full.json") as f:
    ch = json.load(f)
for B in ["4", "8", "12"]:
    r = ch["budgets"][B]
    for model in ["global", "kmeans", "rule"]:
        d = r[model]
        manifest_rows.append(dict(
            case="Chowilla", events_used=12, events_available=31,
            split_type="random_10_2", fold_id="fold_a",
            model=model, zoning="none" if model == "global" else model,
            B_requested=int(B), modes_actual="unknown",
            area_weighted=True, leakage_audit="PENDING",
            gp_backend="sklearn_GPR", lf_data_type="real_HDF5",
            rmse_area=round(d["rmse_area"], 4), csi_area=round(d.get("csi_area", 0), 4),
            status="valid_boundary_case",
            notes="Coarse LF (1434 cells, 77:1 ratio) produces extreme WSE. LSG degradation is real; LF quality boundary."
        ))

# ---- BurnettRV ----
with open("outputs/evaluation/burnettrv/validation_std.json") as f:
    bv = json.load(f)
_bv_n = int(bv.get("config", {}).get("n_events", 12))
for tag in ["global", "KMeans_B4", "Rule_B4", "Rule_B8"]:
    if tag in bv:
        d = bv[tag]
        manifest_rows.append(dict(
            case="BurnettRV", events_used=_bv_n, events_available=74,
            split_type="random_10_2", fold_id="fold_a",
            model=tag, zoning="none" if tag == "global" else tag.split("_")[0],
            B_requested=8 if "B8" in tag else 4,
            modes_actual=d.get("total_modes", d.get("n_modes", "?")),
            area_weighted=True, leakage_audit="PENDING",
            gp_backend="sklearn_GPR", lf_data_type="real_HDF5",
            rmse_area=round(d["rmse_area"], 4), csi_area=round(d.get("csi_area", 0), 4),
            status=f"partial_{_bv_n}of74",
            notes="RMSE from validation_std.json (12-event single split). Event LOOCV: scripts/32_burnettrv_loocv.py."
        ))

# ---- BurnettRV event LOOCV (30-event NPZ) ----
_loocv_p = Path("outputs/evaluation/burnettrv/loocv_results.json")
if _loocv_p.exists():
    bloo = json.loads(_loocv_p.read_text(encoding="utf-8"))
    sm = bloo.get("summary", {})
    n_loo = int(bloo.get("config", {}).get("n_events", 0))
    B_loo = bloo.get("config", {}).get("B", 4)
    if "rule" in sm:
        rs = sm["rule"]
        manifest_rows.append(dict(
            case="BurnettRV", events_used=n_loo, events_available=74,
            split_type="loocv_event", fold_id="loocv",
            model="global_loocv", zoning="none",
            B_requested=B_loo, modes_actual=B_loo,
            area_weighted=True, leakage_audit="PENDING",
            gp_backend="sklearn_GPR", lf_data_type="real_HDF5",
            rmse_area=round(rs["mean_global_rmse"], 4),
            csi_area="",
            status=f"loocv_{n_loo}",
            notes=f"Mean over {rs['n_folds']} LOOCV folds. Rule dRMSE={rs['mean_delta_rmse']:+.4f}; improved {rs['n_improved']}/{rs['n_folds']}; significant={rs['significant']}.",
        ))
        manifest_rows.append(dict(
            case="BurnettRV", events_used=n_loo, events_available=74,
            split_type="loocv_event", fold_id="loocv",
            model="rule_loocv", zoning="rule",
            B_requested=B_loo, modes_actual=B_loo,
            area_weighted=True, leakage_audit="PENDING",
            gp_backend="sklearn_GPR", lf_data_type="real_HDF5",
            rmse_area=round(rs["mean_zonal_rmse"], 4),
            csi_area="",
            status=f"loocv_{n_loo}",
            notes=f"Mean Rule RMSE over {rs['n_folds']} folds from burnettrv_30events.npz.",
        ))

def _maybe_json(path):
    p = Path(path)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None

_off = _maybe_json("outputs/evaluation/carlisle/official_fold_zonal.json")
if _off and "summary" in _off:
    for name, s in _off["summary"].items():
        if "mean_rmse_area" not in s:
            continue
        manifest_rows.append(dict(
            case="Carlisle", events_used=s.get("n_folds", 9), events_available=9,
            split_type="official_loocv_event", fold_id="official",
            model=f"{name}_official", zoning="none" if name == "global" else name,
            B_requested=_off.get("config", {}).get("B", 4),
            modes_actual=_off.get("config", {}).get("B", 4),
            area_weighted=True, leakage_audit="CLEAN_PASS",
            gp_backend="sklearn_GPR", lf_data_type="real_HDF5",
            rmse_area=round(s["mean_rmse_area"], 4),
            csi_area=round(s.get("mean_csi", 0), 4),
            status="complete",
            notes=f"Official 9-fold LSG-Max. MaxWD_R2={s.get('mean_maxwd_r2', float('nan')):.4f}.",
        ))

_deg = _maybe_json("outputs/evaluation/carlisle/lf_degradation.json")
if _deg and "factors" in _deg:
    for fac, rec in _deg["factors"].items():
        for model in ["global", "rule"]:
            if model not in rec:
                continue
            manifest_rows.append(dict(
                case="Carlisle", events_used=9, events_available=9,
                split_type="random_7_2", fold_id=f"lf_factor_{fac}",
                model=f"{model}_degraded_x{fac}", zoning="none" if model == "global" else "rule",
                B_requested=_deg.get("config", {}).get("B", 4),
                modes_actual=rec[model].get("n_modes", ""),
                area_weighted=True, leakage_audit="CLEAN_PASS",
                gp_backend="sklearn_GPR", lf_data_type="real_HDF5_coarsened",
                rmse_area=round(rec[model]["rmse_area"], 4),
                csi_area=round(rec[model].get("csi_area", 0), 4),
                status="complete",
                notes=f"B5 LF coarsen factor={fac}, n_lf={rec.get('n_lf_cells')}.",
            ))

_ch = _maybe_json("outputs/evaluation/carlisle/distance_to_channel.json")
if _ch and "models" in _ch:
    for tag, rec in _ch["models"].items():
        manifest_rows.append(dict(
            case="Carlisle", events_used=9, events_available=9,
            split_type="random_7_2", fold_id="mcl_distance",
            model=tag, zoning=rec.get("method", tag),
            B_requested=_ch.get("config", {}).get("B", 4),
            modes_actual=rec.get("n_modes", ""),
            area_weighted=True, leakage_audit="CLEAN_PASS",
            gp_backend="sklearn_GPR", lf_data_type="real_HDF5",
            rmse_area=round(rec["rmse_area"], 4),
            csi_area=round(rec.get("csi_area", 0), 4),
            status="complete",
            notes="B6 distance-to-Carlisle_MCL zoning.",
        ))

_ex = _maybe_json("outputs/evaluation/carlisle/extrap_zonal.json")
if _ex and "per_event" in _ex:
    for row in _ex["per_event"]:
        for model in _ex.get("config", {}).get("models", ["global", "rule"]):
            if model not in row:
                continue
            manifest_rows.append(dict(
                case="Carlisle", events_used=9, events_available=9,
                split_type="extrapolation", fold_id=str(row.get("event")),
                model=model, zoning="none" if model == "global" else model,
                B_requested=_ex.get("config", {}).get("B", 4),
                modes_actual=row[model].get("n_modes", ""),
                area_weighted=True, leakage_audit="CLEAN_PASS",
                gp_backend="sklearn_GPR", lf_data_type="real_HDF5",
                rmse_area=round(row[model]["rmse_area"], 4),
                csi_area=round(row[model].get("csi_area", 0) if "csi_area" in row[model] else row[model].get("mask_official_extrap", {}).get("csi", 0), 4),
                status="complete",
                notes="A4 extrap; HF truth from raw NPZ not stored MaxWD[:,0].",
            ))

# ---- LF-only baselines (from the same JSON files as the model rows) ----
_lf_specs = [
    ("Carlisle", cb, 9, 9, "complete", "Baseline from budget_sweep_true_equal.json"),
    ("Chowilla", ch, 12, 31, "valid_boundary_case", "LF-only is best on Chowilla; LSG degrades."),
    ("BurnettRV", bv, _bv_n, 74, f"partial_{_bv_n}of74", "Baseline from validation_std.json"),
]
for case, src, n_used, n_avail, status, notes in _lf_specs:
    lf = src["lf_only"]
    manifest_rows.append(dict(
        case=case, events_used=n_used, events_available=n_avail,
        split_type="random", fold_id="N/A",
        model="LF-only", zoning="none", B_requested=0, modes_actual=0,
        area_weighted=True, leakage_audit="N/A", gp_backend="N/A",
        lf_data_type="real_HDF5",
        rmse_area=round(lf["rmse_area"], 4),
        csi_area=round(lf.get("csi_area", 0), 4),
        status=status, notes=notes
    ))

# Write manifest
os.makedirs("outputs/registry", exist_ok=True)
with open("outputs/registry/result_manifest_v4.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(manifest_rows[0].keys()))
    w.writeheader()
    w.writerows(manifest_rows)
print(f"Registry: {len(manifest_rows)} entries saved")

# ---- Mode budget audit ----
with open("outputs/registry/mode_budget_audit.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["case", "fold", "model", "B_requested", "B_actual", "n_zones", "min_per_zone", "status"])
    for B in ["4", "6", "8"]:
        r = cb["budgets"][B]
        for model, key in [("Global", "global"), ("KMeans", "kmeans"), ("Rule", "rule")]:
            d = r[key]
            actual = d.get("actual_modes", B)
            w.writerow(["Carlisle", "fold_a", model, B, actual,
                       "N/A" if model == "Global" else 4,
                       "N/A" if model == "Global" else 1,
                       "OK" if str(actual) == str(B) else f"MISMATCH"])
print("Mode budget audit saved")

# ---- Modal EOI / ZGG (second-order; from scripts/46_modal_eoi.py) ----
_modal_p = Path("outputs/evaluation/eoi/modal_eoi.json")
if _modal_p.exists():
    _modal = json.loads(_modal_p.read_text(encoding="utf-8"))
    with open("outputs/registry/modal_eoi.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "case", "n_events", "n_zones", "budget", "mean_zgg",
            "oracle_rmse_global", "oracle_rmse_zonal", "oracle_delta_rmse",
            "interpretation", "per_fold_status", "corr_zgg_delta_rmse",
        ])
        for case, rec in (_modal.get("cases") or {}).items():
            p_ = rec.get("pooled") or {}
            has_folds = "per_fold" in rec and bool(rec["per_fold"])
            w.writerow([
                case,
                rec.get("n_events", ""),
                p_.get("n_zones", ""),
                p_.get("budget", ""),
                f"{float(p_.get('mean_zgg', float('nan'))):.6f}",
                f"{float(p_.get('oracle_rmse_global', float('nan'))):.6f}",
                f"{float(p_.get('oracle_rmse_zonal', float('nan'))):.6f}",
                f"{float(p_.get('oracle_delta_rmse', float('nan'))):+.6f}",
                p_.get("interpretation", ""),
                "complete" if has_folds else "pooled_only",
                "" if rec.get("corr_zgg_delta_rmse") is None else f"{float(rec['corr_zgg_delta_rmse']):.4f}",
            ])
    print("Modal EOI registry: outputs/registry/modal_eoi.csv")
else:
    print("modal_eoi.json missing; skip modal_eoi.csv")

# ---- EOI (prefer scripts/40_compute_eoi.py output; optional Carlisle HD recompute) ----
_eoi_json = Path("outputs/evaluation/eoi/eoi_all.json")
if _eoi_json.exists():
    eoi_all = json.loads(_eoi_json.read_text(encoding="utf-8"))
    with open("outputs/registry/residual_organization.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case", "n_events", "between_zone_var", "total_var", "EOI", "n_zones", "interpretation"])
        for case, rec in eoi_all.get("cases", {}).items():
            p_ = rec["pooled"]
            w.writerow([
                case, rec.get("n_events", ""),
                f"{p_['between_zone_var']:.6f}", f"{p_['total_var']:.6f}",
                f"{p_['eoi']:.3f}", p_["n_zones"], p_["interpretation"],
            ])
    print("EOI table from outputs/evaluation/eoi/eoi_all.json")
elif args.skip_eoi:
    print("Skipping EOI recompute (--skip-eoi); keeping outputs/registry/residual_organization.csv")
else:
    import glob
    import h5py
    import numpy as np
    from lsg.spatial import nearest_interp_lf_to_hf
    from lsg.zoning import rule_based_zones

    RAW = "data/external/fraehr2024/Carlisle"
    geo = np.load(f"{RAW}/Geometry_data/Lisflood_Geometry_data.npz", allow_pickle=True)
    terrain, areas, hf_xy = geo["Z_coor"], geo["Area"], geo["XY_coor"]
    lf_geo = np.load(f"{RAW}/Geometry_data/LF_Geometry_data.npz", allow_pickle=True)

    hf_files = sorted(glob.glob(f"{RAW}/HD_model_data/High-fidelity/Run[1-9]_alltimesteps.npz"))
    lf_files = sorted(glob.glob(f"{RAW}/HD_model_data/Low-fidelity/Carlisle_LFmodelA.p*.hdf"))

    residuals = []
    for i in range(7):
        wse = np.load(hf_files[i])["wse_data"]
        with h5py.File(lf_files[i], "r") as f:
            wse_lf = f["Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/2D Flow Areas/Carlisle/Water Surface"][:]
        min_t = min(wse.shape[0], wse_lf.shape[0])
        depth_hf = np.maximum(0, wse[:min_t] - terrain[np.newaxis, :])
        lf_interp = nearest_interp_lf_to_hf(
            lf_geo["XY_coor"][:, 0], lf_geo["XY_coor"][:, 1],
            wse_lf[:min_t], hf_xy[:, 0], hf_xy[:, 1],
        )
        depth_lf = np.maximum(0, lf_interp - terrain[np.newaxis, :])
        residuals.append(np.mean(np.abs(depth_lf - depth_hf), axis=0))
    mean_resid = np.mean(residuals, axis=0)

    max_depth_train = np.max(
        [np.maximum(0, np.load(hf_files[i])["wse_data"] - terrain[np.newaxis, :]).max(axis=0) for i in range(7)],
        axis=0,
    )
    active = max_depth_train >= 0.03
    inund_freq_train = np.mean(
        [(np.maximum(0, np.load(hf_files[i])["wse_data"] - terrain[np.newaxis, :]) >= 0.03).mean(axis=0) for i in range(7)],
        axis=0,
    )
    zone_labels = rule_based_zones(max_depth_train, inund_freq_train, active_mask=active)

    zone_ids = sorted(set(zone_labels[active]))
    zone_means = [np.mean(mean_resid[active][zone_labels[active] == z]) for z in zone_ids]
    between_var = np.var(zone_means)
    total_var = np.var(mean_resid[active])
    EOI = between_var / (total_var + 1e-12)

    print(f"\nResidual Organization Index (Carlisle):")
    print(f"  Zones: {len(zone_ids)}, Between-zone var: {between_var:.6f}, Total var: {total_var:.6f}")
    print(f"  EOI = {EOI:.3f} -> {'HIGH - zonal EOF likely beneficial' if EOI > 0.3 else 'LOW'}")
    for z in zone_ids:
        n = (zone_labels[active] == z).sum()
        m = np.mean(mean_resid[active][zone_labels[active] == z])
        print(f"  Zone {z}: {n:,} cells, mean |LF-HF| = {m:.4f}m")

    with open("outputs/registry/residual_organization.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case", "between_zone_var", "total_var", "EOI", "n_zones", "interpretation"])
        w.writerow(["Carlisle", f"{between_var:.6f}", f"{total_var:.6f}", f"{EOI:.3f}", len(zone_ids),
                    "HIGH_structured_residual" if EOI > 0.3 else "LOW_diffuse_residual"])
    print("EOI saved")

# ---- Final summary for report ----
print("\n=== MANIFEST SUMMARY ===")
for case in ["Carlisle", "Chowilla", "BurnettRV"]:
    entries = [r for r in manifest_rows if r["case"] == case and r["model"] != "LF-only"]
    statuses = set(e["status"] for e in entries)
    print(f"  {case}: {len(entries)} experiments, status={statuses}")
