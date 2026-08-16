#!/usr/bin/env python
"""B6: Distance-to-main-channel zoning on Carlisle (Carlisle_MCL.shp).

Same 7/2 seed-42 split as scripts/30 and scripts/43.
Compares: global, rule (depth/freq/residual), rule+channel override,
channel-distance bands, kmeans with distance feature.

Writes outputs/evaluation/carlisle/distance_to_channel.json
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
from lsg.fraehr import distance_to_mcl, load_or_build_carlisle_max, repo_root
from lsg.metrics_area import area_weighted_metrics

OUT = _ROOT / "outputs" / "evaluation" / "carlisle" / "distance_to_channel.json"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--budget", type=int, default=4)
    args = p.parse_args()
    root = repo_root()
    pack = load_or_build_carlisle_max(root)
    hf, lf = pack["hf_max"], pack["lf_max"]
    terrain, areas = pack["terrain_hf"], pack["area_hf"]
    xy = np.column_stack([pack["x_hf"], pack["y_hf"]])

    print("Computing distance to Carlisle_MCL.shp ...", flush=True)
    dist = distance_to_mcl(root, "carlisle", pack["x_hf"], pack["y_hf"], spacing=5.0)
    print(
        f"  distance m: min={dist.min():.1f} p50={np.median(dist):.1f} "
        f"p90={np.percentile(dist, 90):.1f} max={dist.max():.1f}",
        flush=True,
    )

    n_ev = hf.shape[0]
    rng = np.random.default_rng(42)
    idx = rng.permutation(n_ev)
    train_idx, test_idx = idx[:7], idx[7:]
    hf_tr, hf_te = hf[train_idx], hf[test_idx]
    lf_tr, lf_te = lf[train_idx], lf[test_idx]
    print(f"Split train={train_idx.tolist()} test={test_idx.tolist()}", flush=True)

    configs = [
        ("global", "global", False),
        ("rule", "rule", False),
        ("rule_channel", "rule", True),
        ("channel", "channel", False),
        ("kmeans", "kmeans", False),
    ]
    payload = {
        "config": {
            "case": "Carlisle",
            "split": "random_7_2_seed42",
            "train_idx": train_idx.tolist(),
            "test_idx": test_idx.tolist(),
            "B": args.budget,
            "mcl": "Geometry_data/Carlisle_MCL.shp",
            "distance_m": {
                "min": float(dist.min()),
                "p50": float(np.median(dist)),
                "p90": float(np.percentile(dist, 90)),
                "max": float(dist.max()),
            },
        },
        "models": {},
    }
    lf_rows = [area_weighted_metrics(lf_te[i], hf_te[i], areas, 0.03) for i in range(hf_te.shape[0])]
    payload["lf_only"] = {k: float(np.mean([r[k] for r in lf_rows])) for k in lf_rows[0]}

    for tag, method, use_ch in configs:
        print(f"\n=== {tag} ===", flush=True)
        pred, meta = fit_predict_max(
            hf_tr, lf_tr, hf_te, lf_te, terrain, xy, args.budget,
            method=method,
            distance_to_flow=dist,
            use_channel_distance=use_ch,
            return_labels=True,
        )
        rows = [area_weighted_metrics(pred[i], hf_te[i], areas, 0.03) for i in range(hf_te.shape[0])]
        rec = {
            **{k: float(np.mean([r[k] for r in rows])) for k in rows[0]},
            "n_modes": meta["n_modes"],
            "time_s": meta["time_s"],
            "method": method,
            "use_channel_distance": use_ch,
        }
        if "zone_stats" in meta:
            rec["zone_stats"] = meta["zone_stats"]
        payload["models"][tag] = rec
        print(
            f"  RMSE={rec['rmse_area']:.4f} CSI={rec['csi_area']:.4f} "
            f"modes={rec['n_modes']} {rec['time_s']:.1f}s",
            flush=True,
        )
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(jsonable(payload), indent=2), encoding="utf-8")

    g = payload["models"]["global"]["rmse_area"]
    print("\nDelta vs global RMSE (positive = improvement):")
    for tag, rec in payload["models"].items():
        d = g - rec["rmse_area"]
        print(f"  {tag:16} {d:+.4f} m")
    print("Saved", OUT)


if __name__ == "__main__":
    main()
