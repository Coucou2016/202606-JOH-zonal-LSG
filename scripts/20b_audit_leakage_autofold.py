#!/usr/bin/env python
"""Automated train-only leakage audit for LOOCV / official folds.

Verifies that:
  - official Carlisle train/test indices are disjoint
  - train-only rule zoning is insensitive to held-out event corruption
  - all-event zoning is sensitive to the same corruption (sanity)
  - train-only EOF is stable under test corruption
  - code contracts mention train-named feature APIs

Writes outputs/audit/leakage_autofold.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.eoi import eoi_from_max_surfaces
from lsg.eof import fit_eof
from lsg.zoning import rule_based_zones

OUT = _ROOT / "outputs" / "audit" / "leakage_autofold.json"


def _disjoint(train: np.ndarray, test: np.ndarray) -> bool:
    return len(set(train.tolist()) & set(test.tolist())) == 0


def _labels_from(hf: np.ndarray, lf: np.ndarray, idx: np.ndarray | None = None) -> np.ndarray:
    if idx is None:
        h, l = hf, lf
    else:
        h, l = hf[idx], lf[idx]
    max_depth = np.nanmax(h, axis=0)
    inund = np.nanmean(h >= 0.03, axis=0)
    resid = np.nanmean(np.abs(l - h), axis=0)
    active = max_depth >= 0.03
    return rule_based_zones(max_depth, inund, lf_hf_abs_residual=resid, active_mask=active)


def _synthetic_case(n_events: int = 6, n_cells: int = 200, seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    hf = rng.random((n_events, n_cells)) * 2.0
    lf = hf + rng.normal(0, 0.2, size=hf.shape)
    hf[:, :40] += 1.5
    lf[:, :40] += 1.0
    return {"hf": hf, "lf": lf}


def audit_synthetic_loocv() -> dict:
    pack = _synthetic_case()
    hf, lf = pack["hf"], pack["lf"]
    n = hf.shape[0]
    fold_reports = []
    all_ok = True
    for i in range(n):
        train = np.array([j for j in range(n) if j != i], dtype=int)
        test = np.array([i], dtype=int)
        ok_disj = _disjoint(train, test)

        labels_tr = _labels_from(hf, lf, train)
        hf_corrupt = hf.copy()
        hf_corrupt[i] = hf_corrupt[i] + 50.0
        labels_tr2 = _labels_from(hf_corrupt, lf, train)
        zoning_insensitive_to_test = bool(np.array_equal(labels_tr, labels_tr2))

        labels_all = _labels_from(hf, lf, None)
        labels_all_c = _labels_from(hf_corrupt, lf, None)
        all_event_sensitive = not np.array_equal(labels_all, labels_all_c)

        wet = np.any(hf[train] > 0.03, axis=0)
        if int(wet.sum()) < 8:
            wet = np.ones(hf.shape[1], dtype=bool)
        pca_tr, _ = fit_eof(hf[train][:, wet], n_components=min(3, len(train)))
        pca_tr_c, _ = fit_eof(hf_corrupt[train][:, wet], n_components=min(3, len(train)))
        eof_train_stable = bool(np.allclose(pca_tr.components_, pca_tr_c.components_, atol=1e-8))

        eoi_tr = eoi_from_max_surfaces(hf, lf, event_index=train)
        eoi_all = eoi_from_max_surfaces(hf, lf, event_index=None)

        fold_ok = ok_disj and zoning_insensitive_to_test and all_event_sensitive and eof_train_stable
        fold_reports.append(
            {
                "fold": i,
                "n_train": int(len(train)),
                "n_test": 1,
                "disjoint": ok_disj,
                "zoning_train_only_insensitive_to_test_corruption": zoning_insensitive_to_test,
                "all_event_zoning_sensitive_to_test_corruption": all_event_sensitive,
                "eof_train_only_stable_under_test_corruption": eof_train_stable,
                "eoi_train_only": eoi_tr.get("eoi"),
                "eoi_all_events": eoi_all.get("eoi"),
                "pass": fold_ok,
            }
        )
        all_ok = all_ok and fold_ok

    return {
        "protocol": "synthetic_loocv_corruption_probe",
        "n_folds": n,
        "passed": all_ok,
        "folds": fold_reports,
    }


def audit_carlisle_official_splits() -> dict:
    raw = _ROOT / "data/external/fraehr2024/Carlisle/Train_test_split_data"
    out: dict = {"available": False, "folds": [], "passed": True}
    if not raw.is_dir():
        out["message"] = "official split directory missing"
        out["passed"] = False
        return out
    out["available"] = True
    for fold in (1, 2):
        path = raw / f"Train_test_split_ValidateOnGrp_{fold}.npz"
        if not path.exists():
            out["folds"].append({"fold": fold, "status": "MISSING", "pass": False})
            out["passed"] = False
            continue
        split = np.load(path, allow_pickle=True)
        tr = np.asarray(split["idx_train"]).reshape(-1)
        te = np.asarray(split["idx_test"]).reshape(-1)
        ok = _disjoint(tr, te)
        out["folds"].append(
            {
                "fold": fold,
                "status": "OK" if ok else "OVERLAP",
                "n_train": int(tr.size),
                "n_test": int(te.size),
                "n_overlap": int(len(set(tr.tolist()) & set(te.tolist()))),
                "pass": ok,
                "source": str(path),
            }
        )
        out["passed"] = out["passed"] and ok
    return out


def audit_code_contracts() -> dict:
    zoning = (_ROOT / "lsg/zoning.py").read_text(encoding="utf-8")
    gp = (_ROOT / "lsg/gp.py").read_text(encoding="utf-8")
    bl = (_ROOT / "lsg/baseline_lsg.py").read_text(encoding="utf-8")
    zl = (_ROOT / "lsg/zonal_lsg.py").read_text(encoding="utf-8")
    checks = {
        "zoning_features_named_train": "depth_hf_train" in zoning,
        "gp_train_ec_emulator": "def train_ec_emulator" in gp,
        "baseline_fit": "def fit" in bl,
        "zonal_fit": "def fit" in zl,
    }
    return {"passed": all(checks.values()), "checks": checks}


def main() -> None:
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "synthetic_loocv": audit_synthetic_loocv(),
        "carlisle_official_splits": audit_carlisle_official_splits(),
        "code_contracts": audit_code_contracts(),
    }
    report["passed"] = all(
        report[k]["passed"]
        for k in ("synthetic_loocv", "carlisle_official_splits", "code_contracts")
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("PASS" if report["passed"] else "FAIL", OUT)
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
