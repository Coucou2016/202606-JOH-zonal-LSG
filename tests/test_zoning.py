"""Test hydrodynamic zoning methods."""
import numpy as np
import pytest

from lsg.zoning import (
    build_cell_features,
    rule_based_zones,
    kmeans_zones,
    global_zones,
    ZoningConfig,
)


def test_build_cell_features():
    rng = np.random.default_rng(42)
    n_cells = 100
    x = np.linspace(0, 1, n_cells)
    y = np.linspace(0, 1, n_cells)
    depth_hf = rng.normal(0.5, 0.3, (50, n_cells))
    depth_hf = np.maximum(depth_hf, 0)

    features = build_cell_features(x, y, depth_hf)

    assert features.shape == (n_cells, 7)  # x, y, max, mean, std, freq, ttp
    assert not np.any(np.isnan(features))
    assert not np.any(np.isinf(features))


def test_global_zones():
    active = np.ones(100, dtype=bool)
    labels = global_zones(100, active)
    assert labels.shape == (100,)
    assert np.all(labels[active] == 0)
    assert np.all(labels[~active] == -1)


def test_rule_based_zones():
    n = 100
    max_depth = np.linspace(0, 5, n)
    inund_freq = np.linspace(0, 1, n)
    active = max_depth >= 0.03

    labels = rule_based_zones(max_depth, inund_freq, active_mask=active)

    assert labels.shape == (n,)
    assert np.all(labels[active] >= 0)
    assert np.all(labels[~active] == -1)
    assert len(set(labels[active])) <= 5


def test_kmeans_zones():
    rng = np.random.default_rng(42)
    n = 100
    features = rng.normal(0, 1, (n, 5))
    active = np.ones(n, dtype=bool)

    labels = kmeans_zones(features, active, n_zones=4, random_state=42)

    assert labels.shape == (n,)
    assert len(set(labels[active])) == 4
    assert np.all(labels[~active] == -1)


def test_zoning_config():
    zc = ZoningConfig(method="kmeans", n_zones=6)
    assert zc.method == "kmeans"
    assert zc.n_zones == 6
    assert zc.wet_threshold == 0.03
