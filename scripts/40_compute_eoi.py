#!/usr/bin/env python
"""Step 0 / A1: Error Organisation Index on real Fraehr max-surfaces.

Writes:
  outputs/evaluation/eoi/eoi_all.json
  outputs/registry/residual_organization.csv  (all cases)

Burnett uses data/processed/burnettrv_30events.npz.
Carlisle / Chowilla build compressed max-surface caches on first run.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.eoi import eoi_from_max_surfaces, eoi_loocv_folds
from lsg.experiment import jsonable
from lsg.fraehr import (
    load_burnett_max_pack,
    load_or_build_carlisle_max,
    load_or_build_chowilla_max,
    repo_root,
)

OUT = _ROOT / "outputs" / "evaluation" / "eoi" / "eoi_all.json"
CSV = _ROOT / "outputs" / "registry" / "residual_organization.csv"


def _attach_loocv(case: str, folds: list[dict], loocv_path: Path) -> None:
    if not loocv_path.exists():
        return
    raw = json.loads(loocv_path.read_text(encoding="utf-8"))
    per = raw.get("per_event") or []
    by_fold = {}
    for row in per:
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
    p.add_argument("--cases", default="burnettrv,chowilla,carlisle")
    p.add_argument("--chowilla-events", type=int, default=None)
    p.add_argument("--skip-per-fold", action="store_true")
    args = p.parse_args()
    root = repo_root()
    cases = [c.strip().lower() for c in args.cases.split(",") if c.strip()]
    payload = {"cases": {}}
    if OUT.exists():
        try:
            payload = json.loads(OUT.read_text(encoding="utf-8"))
            payload.setdefault("cases", {})
        except Exception:
            payload = {"cases": {}}

    for case in cases:
        print(f"\n=== EOI {case} ===", flush=True)
        if case == "burnettrv":
            pack = load_burnett_max_pack(root)
        elif case == "carlisle":
            pack = load_or_build_carlisle_max(root)
        elif case == "chowilla":
            pack = load_or_build_chowilla_max(root, max_events=args.chowilla_events)
        else:
            raise SystemExit(f"unknown case {case}")

        hf, lf = pack["hf_max"], pack["lf_max"]
        print(f"  {hf.shape[0]} events, {hf.shape[1]:,} cells", flush=True)
        pooled = eoi_from_max_surfaces(hf, lf)
        rec = {
            "case": case,
            "n_events": int(hf.shape[0]),
            "n_cells": int(hf.shape[1]),
            "source": pack.get("source"),
            "pooled": pooled,
        }
        print(
            f"  pooled EOI={pooled['eoi']:.3f} ({pooled['interpretation']}) "
            f"zones={pooled['n_zones']} mean|LF-HF|={pooled['mean_abs_residual_domain']:.4f} m",
            flush=True,
        )
        for zid, mu in pooled["zone_mean_abs_residual"].items():
            print(f"    zone {zid}: n={pooled['zone_n_cells'][zid]:,}  |LF-HF|={mu:.4f} m", flush=True)

        if not args.skip_per_fold:
            folds = eoi_loocv_folds(hf, lf)
            loocv = _ROOT / "outputs" / "evaluation" / case / "loocv_results.json"
            _attach_loocv(case, folds, loocv)
            rec["per_fold"] = folds
            eois = np.array([f["eoi"] for f in folds], dtype=float)
            rec["per_fold_eoi_mean"] = float(np.nanmean(eois))
            rec["per_fold_eoi_std"] = float(np.nanstd(eois))
            paired = [(f["eoi"], f.get("delta_rmse_rule_B4")) for f in folds]
            paired = [(a, b) for a, b in paired if b is not None]
            if len(paired) >= 4:
                a = np.array([x[0] for x in paired])
                b = np.array([x[1] for x in paired], dtype=float)
                rec["corr_eoi_delta_rmse"] = float(np.corrcoef(a, b)[0, 1])
                print(
                    f"  per-fold EOI mean={rec['per_fold_eoi_mean']:.3f}  "
                    f"corr(EOI, dRMSE)={rec['corr_eoi_delta_rmse']:.3f}  n={len(paired)}",
                    flush=True,
                )

        payload["cases"][case] = rec
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(jsonable(payload), indent=2), encoding="utf-8")

    CSV.parent.mkdir(parents=True, exist_ok=True)
    with CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["case", "n_events", "between_zone_var", "total_var", "EOI", "n_zones", "interpretation"]
        )
        for case, rec in payload["cases"].items():
            p_ = rec["pooled"]
            w.writerow(
                [
                    case,
                    rec["n_events"],
                    f"{p_['between_zone_var']:.6f}",
                    f"{p_['total_var']:.6f}",
                    f"{p_['eoi']:.3f}",
                    p_["n_zones"],
                    p_["interpretation"],
                ]
            )
    print("\nSaved", OUT)
    print("Saved", CSV)
    for case, rec in payload["cases"].items():
        p_ = rec["pooled"]
        print(f"  {case}: EOI={p_['eoi']:.3f} {p_['interpretation']}")


if __name__ == "__main__":
    main()
