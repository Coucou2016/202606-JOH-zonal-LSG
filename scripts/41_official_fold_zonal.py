#!/usr/bin/env python
"""A2: Official 9-fold (leave-one-event-out) LSG-Max vs published 5-model table.

Official Carlisle groups are one event each (Carlisle_event_summary.csv).
Published RMSE/FI are time-series (not comparable). MaxWD_R2, CSI, peak_diff
are evaluated on official wet_idx from Categories_HFdata_ValidateOnGrp_k.npz.

Writes outputs/evaluation/carlisle/official_fold_zonal.json (resumable).
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
from lsg.fraehr import load_or_build_carlisle_max, repo_root
from lsg.fraehr_metrics import PUBLISHED_MODELS, load_published_validation, max_surface_protocol_metrics
from lsg.metrics_area import area_weighted_metrics

OUT = _ROOT / "outputs" / "evaluation" / "carlisle" / "official_fold_zonal.json"
CAT = _ROOT / "data" / "external" / "fraehr2024" / "Carlisle" / "HF_EOF_analysis"


def _wet_idx(group: int) -> np.ndarray:
    z = np.load(CAT / f"Categories_HFdata_ValidateOnGrp_{group}.npz", allow_pickle=True)
    return np.asarray(z["wet_idx"], dtype=int)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--budget", type=int, default=4)
    p.add_argument("--models", default="global,rule,kmeans")
    p.add_argument("--start-fold", type=int, default=0)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    models = [m.strip() for m in args.models.split(",") if m.strip()]

    root = repo_root()
    print("Loading Carlisle max pack...", flush=True)
    pack = load_or_build_carlisle_max(root)
    hf, lf = pack["hf_max"], pack["lf_max"]
    terrain, areas, xy = pack["terrain_hf"], pack["area_hf"], np.column_stack([pack["x_hf"], pack["y_hf"]])
    n_ev = hf.shape[0]
    print(f"  {n_ev} events, {hf.shape[1]:,} cells", flush=True)

    pub = load_published_validation(
        root / "data/external/fraehr2024/Carlisle/Result_data/Validation_results.npz"
    )

    payload = {
        "config": {
            "case": "Carlisle",
            "split": "official_leave_one_event_out",
            "B": args.budget,
            "models": models,
            "note": "LSG-Max vs published MaxWD_R2/CSI/peak_diff on official wet_idx. Published RMSE/FI are LSG-TS.",
        },
        "published_mean": {
            "RMSE": pub.get("RMSE_mean"),
            "CSI": pub.get("CSI_mean"),
            "FI": pub.get("FI_mean"),
            "MaxWD_R2": pub.get("MaxWD_R2_mean"),
            "peak_diff": pub.get("peak_diff_mean"),
        },
        "published_models": list(PUBLISHED_MODELS),
        "per_fold": [],
    }
    folds = [0] if args.dry_run else list(range(args.start_fold, n_ev))
    if OUT.exists() and not args.dry_run:
        try:
            prev = json.loads(OUT.read_text(encoding="utf-8"))
            done = {int(r["fold"]) for r in prev.get("per_fold", [])}
            payload["per_fold"] = prev.get("per_fold", [])
            folds = [i for i in folds if i not in done]
            print(f"  resume: {len(done)} folds saved, {len(folds)} remaining", flush=True)
        except Exception:
            pass

    for i in folds:
        group = i + 1
        train = [j for j in range(n_ev) if j != i]
        wet = _wet_idx(group)
        row = {"fold": i, "group": group, "test_event": pack.get("event_ids", [None] * n_ev)[i], "n_wet": int(wet.size)}
        print(f"\nFold {i} group {group} wet={wet.size:,}", flush=True)
        for name in models:
            pred, meta = fit_predict_max(
                hf[train], lf[train], hf[[i]], lf[[i]],
                terrain, xy, args.budget, method=name,
            )
            area = area_weighted_metrics(pred[0], hf[i], areas, 0.03)
            proto = max_surface_protocol_metrics(pred[0], hf[i], wet_idx=wet)
            lf_proto = max_surface_protocol_metrics(lf[i], hf[i], wet_idx=wet)
            row[name] = {**area, **proto, "n_modes": meta["n_modes"], "time_s": meta["time_s"]}
            row["lf_only"] = {
                **area_weighted_metrics(lf[i], hf[i], areas, 0.03),
                **{f"lf_{k}": v for k, v in lf_proto.items()},
            }
            print(
                f"  {name:8} RMSE_area={area['rmse_area']:.4f}  "
                f"MaxWD_R2={proto['maxwd_r2']:.4f} CSI={proto['csi']:.4f} "
                f"peak={proto['peak_diff']:+.4f} modes={meta['n_modes']} {meta['time_s']:.1f}s",
                flush=True,
            )
        # published scalars for this event
        row["published"] = {
            m: {
                "RMSE": float(pub["RMSE"][i, j]),
                "CSI": float(pub["CSI"][i, j]),
                "FI": float(pub["FI"][i, j]),
                "MaxWD_R2": float(pub["MaxWD_R2"][i, j]),
                "peak_diff": float(pub["peak_diff"][i, j]),
            }
            for j, m in enumerate(PUBLISHED_MODELS)
        }
        payload["per_fold"] = [r for r in payload["per_fold"] if int(r["fold"]) != i] + [row]
        payload["per_fold"].sort(key=lambda r: int(r["fold"]))
        _summarize(payload, models)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(jsonable(payload), indent=2), encoding="utf-8")

    _summarize(payload, models)
    OUT.write_text(json.dumps(jsonable(payload), indent=2), encoding="utf-8")
    print("\nSaved", OUT)
    for name, s in payload.get("summary", {}).items():
        print(f"  {name}: MaxWD_R2={s.get('mean_maxwd_r2')} CSI={s.get('mean_csi')} RMSE_area={s.get('mean_rmse_area')}")


def _summarize(payload, models):
    summary = {}
    rows = payload["per_fold"]
    if not rows:
        return
    for name in models:
        if name not in rows[0]:
            continue
        summary[name] = {
            "n_folds": len(rows),
            "mean_rmse_area": float(np.mean([r[name]["rmse_area"] for r in rows])),
            "mean_maxwd_r2": float(np.mean([r[name]["maxwd_r2"] for r in rows])),
            "mean_csi": float(np.mean([r[name]["csi"] for r in rows])),
            "mean_peak_diff": float(np.mean([r[name]["peak_diff"] for r in rows])),
            "mean_rmse_wet": float(np.mean([r[name]["rmse_wet"] for r in rows])),
        }
    pub_r2 = []
    pub_csi = []
    for r in rows:
        pub_r2.append(r["published"]["LSG"]["MaxWD_R2"])
        pub_csi.append(r["published"]["LSG"]["CSI"])
    summary["published_LSG"] = {
        "mean_maxwd_r2": float(np.mean(pub_r2)),
        "mean_csi": float(np.mean(pub_csi)),
    }
    payload["summary"] = summary


if __name__ == "__main__":
    main()
