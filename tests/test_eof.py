"""Test EOF decomposition and reconstruction."""
import numpy as np
import pytest

from lsg.eof import (
    fit_eof,
    project_pseudo_ecs,
    reconstruct_from_ecs,
    select_n_modes,
    modes_for_variance,
    temporal_mean,
    center_data,
)


def test_temporal_mean():
    data = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    mean = temporal_mean(data)
    np.testing.assert_array_almost_equal(mean, [3.0, 4.0])


def test_center_data():
    data = np.array([[1.0, 2.0], [3.0, 4.0]])
    mean = np.array([2.0, 3.0])
    centred = center_data(data, mean)
    np.testing.assert_array_almost_equal(centred, [[-1.0, -1.0], [1.0, 1.0]])


def test_eof_roundtrip():
    rng = np.random.default_rng(42)
    data = rng.normal(0, 1, (100, 20))
    pca, mean = fit_eof(data, n_components=10)
    n_modes = select_n_modes(pca, len(data))
    assert 1 <= n_modes <= 10

    modes = pca.components_[:n_modes]
    ecs = project_pseudo_ecs(data, modes, hf_mean=mean)
    recon = reconstruct_from_ecs(ecs, modes, mean)
    err = np.mean((data - recon) ** 2)
    assert err < 1.0


def test_modes_for_variance():
    rng = np.random.default_rng(42)
    data = rng.normal(0, 1, (100, 20))
    pca, _ = fit_eof(data, n_components=10)
    n99 = modes_for_variance(pca, 0.99)
    n80 = modes_for_variance(pca, 0.80)
    assert n80 <= n99 <= pca.n_components_


def test_weighted_eof():
    rng = np.random.default_rng(42)
    data = rng.normal(0, 1, (100, 20))
    weights = np.linspace(0.5, 1.5, 20)
    pca, mean = fit_eof(data, weights=weights, n_components=10)
    assert pca.components_.shape[0] == min(10, 20)
