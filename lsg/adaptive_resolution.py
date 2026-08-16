"""Adaptive resolution experiments — input-resolution degradation.

For the JOH paper, this module simulates using coarser low-fidelity
models without re-running actual hydrodynamic simulations.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from lsg import spatial


@dataclass
class ResolutionExperiment:
    original_shape: tuple[int, int]
    degraded_shapes: list[tuple[int, int]]
    degradation_factors: list[int]


def build_resolution_experiment(
    lf_shape: tuple[int, int],
    factors: list[int] = [1, 2, 4],
) -> ResolutionExperiment:
    """Create resolution degradation experiment.

    factor=1: original LF
    factor=2: 2x coarser LF (block-average 2x2)
    factor=4: 4x coarser LF (block-average 4x4)
    """
    shapes = []
    valid_factors = []
    ny, nx = lf_shape
    for f in factors:
        if ny % f == 0 and nx % f == 0:
            shapes.append((ny // f, nx // f))
            valid_factors.append(f)
    return ResolutionExperiment(
        original_shape=lf_shape,
        degraded_shapes=shapes,
        degradation_factors=valid_factors,
    )


def degrade_lf_data(
    lf_depth: np.ndarray,
    lf_shape: tuple[int, int],
    degradation_factor: int,
) -> tuple[np.ndarray, tuple[int, int]]:
    """Degrade LF data by block-averaging.

    lf_depth: (n_events, n_timesteps, n_lf_cells) or (n_samples, n_lf_cells)
    Returns degraded data and new shape.
    """
    return spatial.degrade_resolution(lf_depth, lf_shape, degradation_factor)


def coarsen_unstructured_mesh(
    values: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    factor: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Spatially bin an unstructured mesh and return bin centroids + mean values.

    ``values``: (n_samples, n_cells) or (n_cells,)
    ``factor``: 1 returns the original mesh. 2/4 use bin size = factor × median
    nearest-neighbour spacing (a proxy for a coarser hydrodynamic mesh).
    """
    from scipy.spatial import cKDTree

    vals = np.asarray(values, dtype=np.float64)
    one_d = vals.ndim == 1
    if one_d:
        vals = vals.reshape(1, -1)
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    y = np.asarray(y, dtype=np.float64).reshape(-1)
    n_cells = x.size
    if factor <= 1 or n_cells < 8:
        return (vals[0] if one_d else vals), x, y

    tree = cKDTree(np.column_stack([x, y]))
    nn = tree.query(np.column_stack([x, y]), k=2)[0][:, 1]
    spacing = float(np.median(nn[nn > 0])) if np.any(nn > 0) else 1.0
    bin_size = spacing * float(factor)
    ix = np.floor((x - x.min()) / bin_size).astype(int)
    iy = np.floor((y - y.min()) / bin_size).astype(int)
    keys = np.stack([ix, iy], axis=1)
    _, inv, counts = np.unique(keys, axis=0, return_inverse=True, return_counts=True)
    n_bins = int(counts.size)
    x_c = np.zeros(n_bins, dtype=np.float64)
    y_c = np.zeros(n_bins, dtype=np.float64)
    np.add.at(x_c, inv, x)
    np.add.at(y_c, inv, y)
    x_c /= counts
    y_c /= counts
    out = np.zeros((vals.shape[0], n_bins), dtype=np.float64)
    for s in range(vals.shape[0]):
        acc = np.zeros(n_bins, dtype=np.float64)
        np.add.at(acc, inv, vals[s])
        out[s] = acc / counts
    return (out[0] if one_d else out), x_c, y_c
