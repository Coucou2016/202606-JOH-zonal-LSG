#!/usr/bin/env python
"""B5: LF mesh coarsening (information degradation) on Carlisle LSG-Max.

Native LF WSE maxima are spatially binned (factor 1/2/4), interpolated to the
HF mesh, then Global and Rule LSG-Max are trained on the official-style 7/2
split used in scripts/30_carlisle_proper.py (seed 42).

Writes outputs/evaluation/carlisle/lf_degradation.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.adaptive_resolution import coarsen_unstructured_mesh
from lsg.experiment import fit_predict_max, jsonable
from lsg.fraehr import load_or_build_carlisle_max, repo_root
from lsg.metrics_area import area_weighted_metrics
from lsg.spatial import nearest_interp_lf_to_hf

OUT = _ROOT / "outputs" / "evaluation" / "carlisle" / "lf_degradation.json"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--budget", type=int, default=4)
    p.add_argument("--factors", default="1,2,4")
    p.add_argument("--models", default="global,rule")
    args = p.parse_args()
    factors = [int(x) for x in args.factors.split(",") if x.strip()]
    models = [m.strip() for m in args.models.split(",") if m.strip()]

    root = repo_root()
    pack = load_or_build_carlisle_max(root)
    if pack.get("lf_max_native") is None:
        raise SystemExit("carlisle_9events.npz missing lf_max_native; rebuild with scripts/40_compute_eoi.py")

    hf = pack["hf_max"]
    native = pack["lf_max_native"]
    terrain = pack["terrain_hf"]
    areas = pack["area_hf"]
    xy = np.column_stack([pack["x_hf"], pack["y_hf"]])
    n_ev = hf.shape[0]
    rng = np.random.default_rng(42)
    idx = rng.permutation(n_ev)
    train_idx, test_idx = idx[:7], idx[7:]
    print(f"Split train={train_idx.tolist()} test={test_idx.tolist()}", flush=True)

    payload = {
        "config": {
            "case": "Carlisle",
            "split": "random_7_2_seed42",
            "train_idx": train_idx.tolist(),
            "test_idx": test_idx.tolist(),
            "B": args.budget,
            "factors": factors,
            "models": models,
        },
        "factors": {},
    }

    for fac in factors:
        print(f"\n=== factor={fac} ===", flush=True)
        if fac <= 1:
            lf_hf = pack["lf_max"]
            n_lf_used = int(native.shape[1])
        else:
            coarse, xc, yc = coarsen_unstructured_mesh(native, pack["x_lf"], pack["y_lf"], fac)
            n_lf_used = int(xc.size)
            rows = []
            for i in range(coarse.shape[0]):
                wse_hf = nearest_interp_lf_to_hf(xc, yc, coarse[i], pack["x_hf"], pack["y_hf"])
                rows.append(np.maximum(0.0, wse_hf - terrain))
            lf_hf = np.stack(rows)
        print(f"  LF cells {native.shape[1]} → {n_lf_used}", flush=True)

        hf_tr, hf_te = hf[train_idx], hf[test_idx]
        lf_tr, lf_te = lf_hf[train_idx], lf_hf[test_idx]
        rec = {
            "factor": fac,
            "n_lf_cells": n_lf_used,
            "lf_only": {},
        }
        lf_rows = [area_weighted_metrics(lf_te[i], hf_te[i], areas, 0.03) for i in range(hf_te.shape[0])]
        rec["lf_only"] = {k: float(np.mean([r[k] for r in lf_rows])) for k in lf_rows[0]}
        print(f"  LF-only RMSE_area={rec['lf_only']['rmse_area']:.4f}", flush=True)

        for name in models:
            pred, meta = fit_predict_max(
                hf_tr, lf_tr, hf_te, lf_te, terrain, xy, args.budget, method=name,
            )
            rows = [area_weighted_metrics(pred[i], hf_te[i], areas, 0.03) for i in range(hf_te.shape[0])]
            rec[name] = {
                **{k: float(np.mean([r[k] for r in rows])) for k in rows[0]},
                "n_modes": meta["n_modes"],
                "time_s": meta["time_s"],
            }
            print(
                f"  {name:8} RMSE={rec[name]['rmse_area']:.4f} CSI={rec[name]['csi_area']:.4f} "
                f"modes={meta['n_modes']} {meta['time_s']:.1f}s",
                flush=True,
            )
        payload["factors"][str(fac)] = rec
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(jsonable(payload), indent=2), encoding="utf-8")

    print("\nSaved", OUT)


if __name__ == "__main__":
    main()
