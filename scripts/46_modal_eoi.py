#!/usr/bin/env python
"""Second-order modal EOI: zone EOF subspace angles + equal-budget oracle EOF.

Complements scripts/40_compute_eoi.py (first-order residual EOI). Uses only HF
max-surfaces and rule zones — no LF, no GP.

Writes outputs/evaluation/eoi/modal_eoi.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.eoi import modal_diagnostic_loocv, modal_subspace_diagnostic
from lsg.experiment import jsonable
from lsg.fraehr import (
    load_burnett_max_pack,
    load_or_build_carlisle_max,
    load_or_build_chowilla_max,
    repo_root,
)

OUT = _ROOT / "outputs" / "evaluation" / "eoi" / "modal_eoi.json"


def _attach_delta(folds: list[dict], loocv_path: Path) -> None:
    if not loocv_path.exists():
        return
    raw = json.loads(loocv_path.read_text(encoding="utf-8"))
    by_fold = {}
    for row in raw.get("per_event") or []:
        b = row.get("B", 4)
        if b != 4:
            continue
        fid = int(row.get("fold", row.get("test_event", -1)))
        d = row.get("delta_rmse")
        if d is None and "global" in row and "rule" in row:
            d = row["global"]["rmse_area"] - row["rule"]["rmse_area"]
        by_fold[fid] = d
    for rec in folds:
        rec["delta_rmse_rule_B4"] = by_fold.get(int(rec["fold"]))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cases", default="carlisle,burnettrv,chowilla")
    p.add_argument("--budget", type=int, default=4)
    p.add_argument("--skip-per-fold", action="store_true")
    args = p.parse_args()
    root = repo_root()
    cases = [c.strip().lower() for c in args.cases.split(",") if c.strip()]

    payload = {"config": {"B": args.budget, "protocol": "HF_oracle_EOF_plus_principal_angles"}, "cases": {}}
    if OUT.exists():
        try:
            payload = json.loads(OUT.read_text(encoding="utf-8"))
            payload.setdefault("cases", {})
        except Exception:
            pass

    for case in cases:
        print(f"\n=== modal EOI {case} ===", flush=True)
        if case == "burnettrv":
            pack = load_burnett_max_pack(root)
        elif case == "carlisle":
            pack = load_or_build_carlisle_max(root)
        elif case == "chowilla":
            pack = load_or_build_chowilla_max(root)
        else:
            raise SystemExit(f"unknown case {case}")

        hf = pack["hf_max"]
        print(f"  {hf.shape[0]} events, {hf.shape[1]:,} cells", flush=True)
        pooled = modal_subspace_diagnostic(hf, budget=args.budget)
        print(
            f"  ZGG={pooled['mean_zgg']:+.4f}  "
            f"oracle RMSE G={pooled['oracle_rmse_global']:.4f} Z={pooled['oracle_rmse_zonal']:.4f} "
            f"d={pooled['oracle_delta_rmse']:+.4f}  {pooled['interpretation']}",
            flush=True,
        )
        for zid, gap in (pooled.get("zone_zgg") or {}).items():
            print(f"    zone {zid}: ZGG={gap:+.4f}", flush=True)

        rec = {
            "case": case,
            "n_events": int(hf.shape[0]),
            "n_cells": int(hf.shape[1]),
            "pooled": pooled,
        }

        if not args.skip_per_fold:
            folds = modal_diagnostic_loocv(hf, budget=args.budget)
            loocv = _ROOT / "outputs" / "evaluation" / case / "loocv_results.json"
            _attach_delta(folds, loocv)
            rec["per_fold"] = folds
            zggs = np.array([f["mean_zgg"] for f in folds], dtype=float)
            deltas_o = np.array([f["oracle_delta_rmse"] for f in folds], dtype=float)
            rec["per_fold_zgg_mean"] = float(np.nanmean(zggs))
            rec["per_fold_oracle_delta_mean"] = float(np.nanmean(deltas_o))
            paired = [(f["mean_zgg"], f.get("delta_rmse_rule_B4")) for f in folds]
            paired = [(a, b) for a, b in paired if b is not None and np.isfinite(a)]
            if len(paired) >= 4:
                a = np.array([x[0] for x in paired])
                b = np.array([x[1] for x in paired], dtype=float)
                rec["corr_zgg_delta_rmse"] = float(np.corrcoef(a, b)[0, 1])
                print(
                    f"  per-fold ZGG mean={rec['per_fold_zgg_mean']:+.4f}  "
                    f"oracle dRMSE mean={rec['per_fold_oracle_delta_mean']:+.4f}  "
                    f"corr(ZGG, LSG dRMSE)={rec['corr_zgg_delta_rmse']:.3f}",
                    flush=True,
                )

        payload["cases"][case] = rec
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(jsonable(payload), indent=2), encoding="utf-8")

    print("\nSaved", OUT)
    for case, rec in payload["cases"].items():
        p_ = rec.get("pooled") or {}
        zgg = p_.get("mean_zgg", float("nan"))
        d_rmse = p_.get("oracle_delta_rmse", float("nan"))
        interp = p_.get("interpretation", "?")
        zgg_s = f"{zgg:+.4f}" if isinstance(zgg, (int, float)) else str(zgg)
        d_s = f"{d_rmse:+.4f}" if isinstance(d_rmse, (int, float)) else str(d_rmse)
        note = ""
        if "per_fold" not in rec:
            note = "  [pooled only; per-fold not run]"
        print(f"  {case}: ZGG={zgg_s} oracle_dRMSE={d_s} {interp}{note}")


if __name__ == "__main__":
    main()
