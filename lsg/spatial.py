"""Spatial operations: masking, interpolation, coarsening, flow-path distance."""

from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree


# ---------------------------------------------------------------------------
# Wet-cell masks
# ---------------------------------------------------------------------------


def wet_cell_mask(
    depth: np.ndarray,
    threshold_m: float = 0.03,
    require_variation: bool = True,
) -> np.ndarray:
    """Identify cells that are wet in at least one sample.

    depth: (n_samples, n_cells) or (n_events, n_timesteps, n_cells)
    """
    if depth.ndim == 3:
        flat = depth.reshape(-1, depth.shape[-1])
    else:
        flat = depth
    is_wet = np.nanmax(flat, axis=0) >= threshold_m
    if require_variation:
        has_var = np.nanmax(flat, axis=0) - np.nanmin(flat, axis=0) > 0
        is_wet = is_wet & has_var
    return is_wet


def always_wet_mask(depth: np.ndarray, threshold_m: float = 0.03) -> np.ndarray:
    """Cells that are always wet (never dry)."""
    if depth.ndim == 3:
        flat = depth.reshape(-1, depth.shape[-1])
    else:
        flat = depth
    return flat.min(axis=0) >= threshold_m


def temporary_wet_mask(depth: np.ndarray, threshold_m: float = 0.03) -> np.ndarray:
    """Cells that are sometimes wet, sometimes dry."""
    if depth.ndim == 3:
        flat = depth.reshape(-1, depth.shape[-1])
    else:
        flat = depth
    return (flat.max(axis=0) >= threshold_m) & (flat.min(axis=0) < threshold_m)


def binary_extent(depth: np.ndarray, threshold_m: float = 0.03) -> np.ndarray:
    return (depth >= threshold_m).astype(np.float32)


# ---------------------------------------------------------------------------
# Grid operations
# ---------------------------------------------------------------------------


def coarsen_grid(
    depth_hf: np.ndarray,
    shape_2d: tuple[int, int],
    factor: int,
) -> np.ndarray:
    """Block-average coarsening for structured grids."""
    ny, nx = shape_2d
    d2 = depth_hf.reshape(-1, ny, nx)
    ny_c, nx_c = ny // factor, nx // factor
    d2 = d2[:, : ny_c * factor, : nx_c * factor]
    d2 = d2.reshape(-1, ny_c, factor, nx_c, factor).mean(axis=(2, 4))
    return d2.reshape(-1, ny_c * nx_c)


# ---------------------------------------------------------------------------
# LF -> HF interpolation
# ---------------------------------------------------------------------------


def nearest_interp_lf_to_hf(
    x_lf: np.ndarray,
    y_lf: np.ndarray,
    values_lf: np.ndarray,
    x_hf: np.ndarray,
    y_hf: np.ndarray,
) -> np.ndarray:
    """Nearest-neighbour interpolation from LF to HF grid.

    values_lf: (n_samples, n_lf_cells) or (n_lf_cells,)
    Returns same shape as values_lf but with n_hf_cells in last dim.
    """
    tree = cKDTree(np.column_stack([x_lf, y_lf]))
    _, idx = tree.query(np.column_stack([x_hf, y_hf]), k=1)
    if values_lf.ndim == 1:
        return values_lf[idx]
    return values_lf[:, idx]


def interpolate_lf_to_hf_grid(
    depth_lf: np.ndarray,
    lf_shape: tuple[int, int],
    hf_shape: tuple[int, int],
    terrain_hf: np.ndarray,
    wse_correction: bool = True,
) -> np.ndarray:
    """Grid-based nearest-neighbour upsample: LF depths to HF grid.

    depth_lf: (n_samples, n_lf_cells)
    """
    n_samples = depth_lf.shape[0]
    ny_lf, nx_lf = lf_shape
    ny_hf, nx_hf = hf_shape
    out = np.zeros((n_samples, ny_hf * nx_hf), dtype=np.float64)
    terrain_2d = terrain_hf.reshape(ny_hf, nx_hf)

    yi = (np.arange(ny_hf) * ny_lf // ny_hf).astype(int)
    xi = (np.arange(nx_hf) * nx_lf // nx_hf).astype(int)

    for s in range(n_samples):
        lf_2d = depth_lf[s].reshape(ny_lf, nx_lf)
        hf_2d = lf_2d[np.ix_(yi, xi)]
        if wse_correction and terrain_hf.size == hf_2d.size:
            hf_2d = np.where(hf_2d + terrain_2d >= terrain_2d, hf_2d, 0.0)
        out[s] = hf_2d.ravel()
    return out


# ---------------------------------------------------------------------------
# Cell areas & weights
# ---------------------------------------------------------------------------


def cell_areas_uniform(shape_2d: tuple[int, int], cell_size_m: float) -> np.ndarray:
    ny, nx = shape_2d
    return np.full(ny * nx, cell_size_m**2, dtype=np.float64)


def sqrt_area_weights(areas: np.ndarray) -> np.ndarray:
    return np.sqrt(areas)


# ---------------------------------------------------------------------------
# Flow-path distance (for rule-based zoning)
# ---------------------------------------------------------------------------


def distance_to_path(
    x: np.ndarray,
    y: np.ndarray,
    path_x: np.ndarray,
    path_y: np.ndarray,
) -> np.ndarray:
    """Compute Euclidean distance from each (x, y) point to a polyline path."""
    tree = cKDTree(np.column_stack([path_x, path_y]))
    dist, _ = tree.query(np.column_stack([x, y]), k=1)
    return dist


def densify_polyline(
    path_x: np.ndarray,
    path_y: np.ndarray,
    spacing: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Insert vertices so consecutive samples are at most ``spacing`` apart."""
    px = np.asarray(path_x, dtype=np.float64).reshape(-1)
    py = np.asarray(path_y, dtype=np.float64).reshape(-1)
    if px.size < 2:
        return px, py
    xs: list[float] = [float(px[0])]
    ys: list[float] = [float(py[0])]
    for i in range(1, px.size):
        x0, y0 = xs[-1], ys[-1]
        x1, y1 = float(px[i]), float(py[i])
        dist = float(np.hypot(x1 - x0, y1 - y0))
        n = max(int(np.ceil(dist / max(spacing, 1e-9))), 1)
        for k in range(1, n + 1):
            t = k / n
            xs.append(x0 + t * (x1 - x0))
            ys.append(y0 + t * (y1 - y0))
    return np.asarray(xs), np.asarray(ys)


def approximate_flow_path_from_terrain(
    terrain: np.ndarray,
    shape_2d: tuple[int, int],
) -> tuple[np.ndarray, np.ndarray]:
    """Approximate main flow path from terrain by following steepest descent.

    Returns (path_x, path_y) coordinates.
    """
    ny, nx = shape_2d
    dem = terrain.reshape(ny, nx)

    # Start at upstream boundary (top row centre)
    start_col = nx // 2
    path = [(start_col, 0)]

    for row in range(1, ny - 1):
        col = path[-1][0]
        neighbours = []
        for dc in [-1, 0, 1]:
            nc = col + dc
            if 0 <= nc < nx:
                neighbours.append((nc, dem[row, nc]))
        if neighbours:
            best_col = min(neighbours, key=lambda x: x[1])[0]
            path.append((best_col, row))

    px = np.array([c for c, r in path])
    py = np.array([r for c, r in path])
    return px, py


# ---------------------------------------------------------------------------
# WSE (water surface elevation) terrain masking
# ---------------------------------------------------------------------------


def wse_correct(
    depth: np.ndarray,
    terrain: np.ndarray,
) -> np.ndarray:
    """Set depth to 0 where WSE < terrain elevation."""
    wse = depth + terrain
    corrected = np.where(wse >= terrain, depth, 0.0)
    return corrected


# ---------------------------------------------------------------------------
# Resolution degradation (for input-resolution experiment)
# ---------------------------------------------------------------------------


def degrade_resolution(
    depth_lf: np.ndarray,
    lf_shape: tuple[int, int],
    degradation_factor: int,
) -> tuple[np.ndarray, tuple[int, int]]:
    """Coarsen LF simulation output by block-averaging.

    This simulates using an even coarser low-fidelity model without
    re-running hydrodynamics.
    """
    ny, nx = lf_shape
    ny_c, nx_c = ny // degradation_factor, nx // degradation_factor
    d2 = depth_lf.reshape(-1, ny, nx)
    d2 = d2[:, : ny_c * degradation_factor, : nx_c * degradation_factor]
    d2 = d2.reshape(-1, ny_c, degradation_factor, nx_c, degradation_factor)
    degraded = d2.mean(axis=(2, 4))
    return degraded.reshape(-1, ny_c * nx_c), (ny_c, nx_c)
