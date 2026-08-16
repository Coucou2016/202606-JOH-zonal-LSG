"""Test zonal EOF decomposition and reconstruction."""
import numpy as np

from lsg.eof import fit_eof, project_pseudo_ecs, reconstruct_from_ecs
from lsg.zonal_eof import fit_zonal_eof, project_zonal_ecs, reconstruct_zonal
from lsg.zoning import kmeans_zones, build_cell_features


def test_zonal_eof_fit():
    rng = np.random.default_rng(42)
    n_samples, n_cells = 100, 80
    hf_wet = rng.normal(0.5, 0.3, (n_samples, n_cells))
    hf_wet = np.maximum(hf_wet, 0)
    lf_wet = hf_wet + rng.normal(0, 0.05, hf_wet.shape)

    active = np.ones(n_cells, dtype=bool)
    x = np.linspace(0, 1, n_cells)
    y = np.linspace(0, 1, n_cells)

    features = build_cell_features(x, y, hf_wet)
    zone_labels = kmeans_zones(features, active, n_zones=4, random_state=42)

    state = fit_zonal_eof(
        hf_wet, lf_wet, zone_labels, active,
        max_modes_per_zone=20,
        variance_threshold=0.99,
        mode_budget=None,
    )

    assert len(state.zones) == 4
    assert state.total_eof_modes > 0
    for zr in state.zones:
        assert zr.n_modes > 0
        assert zr.n_cells > 0


def test_zonal_roundtrip():
    rng = np.random.default_rng(42)
    n_samples, n_cells = 80, 60
    hf_wet = rng.normal(0.5, 0.3, (n_samples, n_cells))
    hf_wet = np.maximum(hf_wet, 0)
    lf_wet = hf_wet + rng.normal(0, 0.03, hf_wet.shape)

    active = np.ones(n_cells, dtype=bool)
    x = np.linspace(0, 1, n_cells)
    y = np.linspace(0, 1, n_cells)

    features = build_cell_features(x, y, hf_wet)
    zone_labels = kmeans_zones(features, active, n_zones=3, random_state=42)

    state = fit_zonal_eof(
        hf_wet, lf_wet, zone_labels, active,
        max_modes_per_zone=15,
        variance_threshold=0.99,
    )

    # Project and reconstruct
    ecs_dict = project_zonal_ecs(hf_wet, state, active)
    recon = reconstruct_zonal(ecs_dict, state, active, n_samples)

    # Check reconstruction error is reasonable
    err = np.mean((hf_wet - recon) ** 2)
    assert err < 0.5, f"Reconstruction error too high: {err}"
