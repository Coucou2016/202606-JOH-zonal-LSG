"""Tests for automated leakage audit and area-weighted oracle fields."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from lsg.eoi import modal_subspace_diagnostic

ROOT = Path(__file__).resolve().parents[1]


def test_leakage_autofold_json_or_run():
    out = ROOT / "outputs" / "audit" / "leakage_autofold.json"
    if not out.exists():
        import runpy

        runpy.run_path(str(ROOT / "scripts" / "20b_audit_leakage_autofold.py"), run_name="__main__")
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["passed"] is True
    assert report["synthetic_loocv"]["passed"] is True
    assert report["code_contracts"]["passed"] is True


def test_area_weighted_oracle_fields_present():
    rng = np.random.default_rng(0)
    n_ev, n_c = 5, 120
    hf = rng.random((n_ev, n_c)) * 1.5
    hf[:, :30] += 1.0
    areas = np.linspace(1.0, 5.0, n_c)
    out = modal_subspace_diagnostic(hf, budget=4, cell_areas=areas)
    assert out["area_weights_used"] is True
    assert np.isfinite(out["oracle_delta_rmse"])
    assert np.isfinite(out["oracle_delta_rmse_area"])
    out_u = modal_subspace_diagnostic(hf, budget=4, cell_areas=np.ones(n_c))
    assert abs(out_u["oracle_delta_rmse"] - out_u["oracle_delta_rmse_area"]) < 1e-9
