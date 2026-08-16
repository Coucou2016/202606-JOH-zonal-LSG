"""HEC-RAS HDF5 helpers (Fraehr LF / Chowilla HF)."""
from __future__ import annotations

from pathlib import Path

import h5py
import numpy as np

AREA_NAME = {
    "carlisle": "Carlisle",
    "chowilla": "Chowilla",
    "burnettrv": "BurnettRV_region",
}

_TS = (
    "Results/Unsteady/Output/Output Blocks/Base Output/"
    "Unsteady Time Series/2D Flow Areas/{area}/Water Surface"
)
_MAX = (
    "Results/Unsteady/Output/Output Blocks/Base Output/"
    "Summary Output/2D Flow Areas/{area}/Maximum Water Surface"
)


def _area(case: str, area: str | None) -> str:
    if area:
        return area
    return AREA_NAME[case.lower()]


def read_max_wse(
    hdf_path: str | Path,
    case: str,
    n_cells: int | None = None,
    area: str | None = None,
) -> np.ndarray:
    """Maximum water-surface elevation (n_cells,).

    Prefers Summary Output ``Maximum Water Surface`` (row 0), which matches
    the time-series max to ~1e-4 m and avoids reading multi-GB unsteady blocks.
    """
    area_n = _area(case, area)
    with h5py.File(hdf_path, "r") as f:
        max_path = _MAX.format(area=area_n)
        if max_path in f:
            sm = np.asarray(f[max_path], dtype=np.float64)
            wse = sm[0] if sm.ndim == 2 else sm.reshape(-1)
        else:
            ts_path = _TS.format(area=area_n)
            ds = f[ts_path]
            n_t, n_c = ds.shape
            take = n_c if n_cells is None else min(n_c, n_cells)
            wse = np.full(take, -np.inf, dtype=np.float64)
            chunk = 64
            for i in range(0, n_t, chunk):
                block = np.asarray(ds[i : i + chunk, :take], dtype=np.float64)
                wse = np.maximum(wse, np.nanmax(block, axis=0))
        if n_cells is not None:
            wse = wse[:n_cells]
    return np.nan_to_num(wse, nan=0.0)


def read_wse_timeseries(
    hdf_path: str | Path,
    case: str,
    n_cells: int | None = None,
    area: str | None = None,
) -> np.ndarray:
    """Unsteady WSE (n_timesteps, n_cells)."""
    area_n = _area(case, area)
    with h5py.File(hdf_path, "r") as f:
        ds = f[_TS.format(area=area_n)]
        n_c = ds.shape[1] if n_cells is None else min(ds.shape[1], n_cells)
        wse = np.asarray(ds[:, :n_c], dtype=np.float64)
    return np.nan_to_num(wse, nan=0.0)
