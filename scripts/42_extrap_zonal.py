#!/usr/bin/env python
"""A4: Carlisle extrapolation (p10 / p11) + wet-mask ablation + zonal error of published MaxWD.

HF truth is recomputed from raw ``*_alltimesteps.npz``. Stored MaxWD[:,0] is
duplicated across events and must not be used as truth.

Writes outputs/evaluation/carlisle/extrap_zonal.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.experiment import fit_predict_max, jsonable
from lsg.fraehr import load_carlisle_extrap_max, load_or_build_carlisle_max, load_published_npz, repo_root
from lsg.fraehr_metrics import load_published_validation, max_surface_protocol_metrics
from lsg.metrics import zone_metrics
from lsg.metrics_area import area_weighted_metrics
from lsg.spatial import wet_cell_mask

OUT = _ROOT / "outputs" / "evaluation" / "carlisle" / "extrap_zonal.json"
CAT = _ROOT / "data" / "external" / "fraehr2024" / "Carlisle" / "HF_EOF_analysis"
PUBLISHED_MAXWD = ("HF_stored", "LSG", "Kabir_1dCNN", "LSTM_SRR", "GP_EOF", "LSTM_EOF")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--budget", type=int, default=4)
    p.add_argument("--models", default="global,rule")
    args = p.parse_args()
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    root = repo_root()

    print("Loading interpolation pack (train)...", flush=True)
    train_pack = load_or_build_carlisle_max(root)
    print("Loading extrapolation p10/p11 (recompute HF max from NPZ)...", flush=True)
    extrap = load_carlisle_extrap_max(root)

    hf_tr, lf_tr = train_pack["hf_max"], train_pack["lf_max"]
    hf_te, lf_te = extrap["hf_max"], extrap["lf_max"]
    terrain = train_pack["terrain_hf"]
    areas = train_pack["area_hf"]
    xy = np.column_stack([train_pack["x_hf"], train_pack["y_hf"]])

    train_wet = np.where(wet_cell_mask(hf_tr, 0.03))[0]
    cat_std = np.load(CAT / "Categories_HFdata_ValidateOnGrp_1.npz", allow_pickle=True)
    cat_ex = np.load(CAT / "Categories_HFdata_ValidateOnGrp_1_extrap.npz", allow_pickle=True)
    wet_std = np.asarray(cat_std["wet_idx"], dtype=int)
    wet_ex = np.asarray(cat_ex["wet_idx"], dtype=int)
    print(
        f"  train_wet={train_wet.size:,}  official_interp_wet={wet_std.size:,}  "
        f"official_extrap_wet={wet_ex.size:,}  (+{(wet_ex.size/wet_std.size-1)*100:.1f}%)",
        flush=True,
    )

    pub_ex = load_published_validation(
        root / "data/external/fraehr2024/Carlisle/Result_data/Validation_results_extrap.npz"
    )
    maxwd = np.asarray(load_published_npz(root, "carlisle", extrap=True)["MaxWD"])
    hf_dup = bool(np.allclose(maxwd[0, 0], maxwd[1, 0]))
    print(f"  stored MaxWD HF duplicated across events: {hf_dup} (ignored; using raw NPZ)", flush=True)

    payload = {
        "config": {
            "case": "Carlisle",
            "events": extrap["event_ids"],
            "B": args.budget,
            "models": models,
            "hf_truth": "raw_npz_max",
            "stored_MaxWD_HF_duplicated": hf_dup,
            "n_wet": {
                "train_only": int(train_wet.size),
                "official_interp": int(wet_std.size),
                "official_extrap": int(wet_ex.size),
                "all_cells": int(terrain.size),
            },
        },
        "published_extrap_mean": {
            "RMSE": pub_ex.get("RMSE_mean"),
            "CSI": pub_ex.get("CSI_mean"),
            "MaxWD_R2": pub_ex.get("MaxWD_R2_mean"),
            "peak_diff": pub_ex.get("peak_diff_mean"),
        },
        "per_event": [],
    }

    zone_labels = None
    for name in models:
        print(f"\nTraining {name} B={args.budget} on 9 interpolation events...", flush=True)
        pred, meta = fit_predict_max(
            hf_tr, lf_tr, hf_te, lf_te, terrain, xy, args.budget,
            method=name, return_labels=True,
        )
        if name == "rule":
            zone_labels = meta.get("zone_labels")
        for i, eid in enumerate(extrap["event_ids"]):
            row = next((r for r in payload["per_event"] if r["event"] == eid), None)
            if row is None:
                row = {"event": eid, "index": i}
                payload["per_event"].append(row)
            block = {
                "n_modes": meta["n_modes"],
                "time_s": meta["time_s"],
                **area_weighted_metrics(pred[i], hf_te[i], areas, 0.03),
            }
            for idx, tag in (
                (train_wet, "mask_train"),
                (wet_std, "mask_official_interp"),
                (wet_ex, "mask_official_extrap"),
                (None, "mask_all"),
            ):
                proto = max_surface_protocol_metrics(pred[i], hf_te[i], wet_idx=idx)
                block[tag] = proto
            lf_block = {
                **area_weighted_metrics(lf_te[i], hf_te[i], areas, 0.03),
                "mask_train": max_surface_protocol_metrics(lf_te[i], hf_te[i], wet_idx=train_wet),
                "mask_official_extrap": max_surface_protocol_metrics(lf_te[i], hf_te[i], wet_idx=wet_ex),
            }
            row[name] = block
            row["lf_only"] = lf_block
            print(
                f"  {eid} {name}: RMSE_area={block['rmse_area']:.4f}  "
                f"R2_trainwet={block['mask_train']['maxwd_r2']:.4f}  "
                f"R2_extrapwet={block['mask_official_extrap']['maxwd_r2']:.4f}",
                flush=True,
            )

            # published MaxWD vs recomputed HF truth (full domain)
            pub_block = {}
            for j, mname in enumerate(PUBLISHED_MAXWD):
                if j == 0:
                    continue  # skip duplicated stored HF
                pred_pub = maxwd[i, j]
                pub_block[mname] = {
                    "rmse_area": area_weighted_metrics(pred_pub, hf_te[i], areas, 0.03)["rmse_area"],
                    "mask_train": max_surface_protocol_metrics(pred_pub, hf_te[i], wet_idx=train_wet),
                    "mask_official_extrap": max_surface_protocol_metrics(pred_pub, hf_te[i], wet_idx=wet_ex),
                }
                if zone_labels is not None:
                    zm = zone_metrics(pred_pub, hf_te[i], zone_labels, threshold_m=0.03)
                    pub_block[mname]["zone_rmse"] = {str(k): v["rmse"] for k, v in zm.items()}
            row["published_maxwd_vs_raw_hf"] = pub_block

            if zone_labels is not None:
                zm_ours = zone_metrics(pred[i], hf_te[i], zone_labels, threshold_m=0.03)
                row[name]["zone_rmse"] = {str(k): v["rmse"] for k, v in zm_ours.items()}

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(jsonable(payload), indent=2), encoding="utf-8")
    print("\nSaved", OUT)


if __name__ == "__main__":
    main()
