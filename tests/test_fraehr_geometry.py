"""Smoke-test real Fraehr geometry (Track B). Skips if data are not extracted."""
from pathlib import Path

import pytest

from lsg.fraehr import load_case_geometry, raw_dir_exists

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(
    not raw_dir_exists(ROOT, "carlisle"),
    reason="Carlisle Geometry_data not extracted",
)
def test_carlisle_real_geometry_cell_count():
    geo = load_case_geometry(ROOT, "carlisle")
    assert geo["n_hf"] == 581061
    assert geo["n_lf"] is not None and geo["n_lf"] > 1000
    assert geo["terrain_hf"].shape[0] == geo["n_hf"]


@pytest.mark.skipif(
    not raw_dir_exists(ROOT, "chowilla"),
    reason="Chowilla Geometry_data not extracted",
)
def test_chowilla_real_geometry_cell_count():
    geo = load_case_geometry(ROOT, "chowilla")
    assert geo["n_hf"] == 109914


@pytest.mark.skipif(
    not raw_dir_exists(ROOT, "burnettrv"),
    reason="BurnettRV Geometry_data not extracted",
)
def test_burnettrv_real_geometry_cell_count():
    geo = load_case_geometry(ROOT, "burnettrv")
    assert geo["n_hf"] == 780785
