"""Load Fraehr (2024) Figshare benchmark geometry and event max-surfaces.

This is the Track B (citable) data path. Synthetic 30x40 grids under
``data/processed/*/`` are smoke-test fixtures only — do not cite them.

Used by ``scripts/03_prepare_case_data.py``, ``scripts/30_carlisle_proper.py``
patterns, and the geometry smoke test.
"""
from __future__ import annotations

import glob
from pathlib import Path
from typing import Any

import numpy as np

CASE_DIR_NAME = {
    "carlisle": "Carlisle",
    "chowilla": "Chowilla",
    "burnettrv": "BurnettRV",
}

HF_GEOMETRY = {
    "carlisle": "Lisflood_Geometry_data.npz",
    "chowilla": "Geometry_data_HF.npz",
    "burnettrv": "Tuflow_Geometry_data.npz",
}

LF_GEOMETRY = {
    "carlisle": "LF_Geometry_data.npz",
    "chowilla": "Geometry_data_LF.npz",
    "burnettrv": "HECRAS_Geometry_data.npz",
}

# Paper table fallbacks if a geometry file is missing.
EXPECTED_HF_CELLS = {"carlisle": 581061, "chowilla": 109914, "burnettrv": 780785}
EXPECTED_LF_CELLS = {"carlisle": 5681, "chowilla": 1434, "burnettrv": 15256}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def raw_dir(root: Path, case: str) -> Path:
    key = case.lower()
    if key not in CASE_DIR_NAME:
        raise KeyError(f"Unknown case {case!r}; expected one of {list(CASE_DIR_NAME)}")
    return Path(root) / "data" / "external" / "fraehr2024" / CASE_DIR_NAME[key]


def raw_dir_exists(root: Path, case: str) -> bool:
    d = raw_dir(root, case)
    return d.is_dir() and (d / "Geometry_data").is_dir()


def _xy_z_area(geo: Any) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Accept Fraehr NPZ key variants."""
    files = set(geo.files)
    if "XY_coor" in files:
        xy = np.asarray(geo["XY_coor"])
        x, y = xy[:, 0], xy[:, 1]
    elif "x" in files and "y" in files:
        x, y = np.asarray(geo["x"]), np.asarray(geo["y"])
    else:
        raise KeyError(f"No XY coordinates in NPZ keys {sorted(files)}")
    z_key = "Z_coor" if "Z_coor" in files else "z"
    z = np.asarray(geo[z_key]).reshape(-1)
    area = np.asarray(geo["Area"]).reshape(-1) if "Area" in files else np.ones_like(z)
    return x, y, z, area


def load_case_geometry(root: Path, case: str) -> dict[str, Any]:
    """Load HF/LF mesh geometry. Does not load HD event files."""
    case = case.lower()
    raw = raw_dir(root, case)
    hf_path = raw / "Geometry_data" / HF_GEOMETRY[case]
    lf_path = raw / "Geometry_data" / LF_GEOMETRY[case]
    if not hf_path.exists():
        raise FileNotFoundError(hf_path)
    hf = np.load(hf_path, allow_pickle=True)
    x_hf, y_hf, z_hf, area_hf = _xy_z_area(hf)
    result: dict[str, Any] = {
        "case": case,
        "raw_dir": raw,
        "x_hf": x_hf,
        "y_hf": y_hf,
        "terrain_hf": z_hf,
        "area_hf": area_hf,
        "n_hf": int(z_hf.shape[0]),
        "hf_geometry_path": hf_path,
    }
    if lf_path.exists():
        lf = np.load(lf_path, allow_pickle=True)
        x_lf, y_lf, z_lf, area_lf = _xy_z_area(lf)
        result.update(
            x_lf=x_lf,
            y_lf=y_lf,
            terrain_lf=z_lf,
            area_lf=area_lf,
            n_lf=int(z_lf.shape[0]),
            lf_geometry_path=lf_path,
        )
    else:
        result["n_lf"] = None
    return result


def load_carlisle_max_surfaces(root: Path, max_events: int | None = 9) -> dict[str, Any]:
    """Load Carlisle HF/LF maximum depth surfaces (LSG-Max).

    Follows ``scripts/30_carlisle_proper.py``. Reading all Run NPZs is I/O-heavy.
    """
    from lsg.spatial import nearest_interp_lf_to_hf
    import h5py

    geo = load_case_geometry(root, "carlisle")
    raw = geo["raw_dir"]
    terrain = geo["terrain_hf"]
    hf_x, hf_y = geo["x_hf"], geo["y_hf"]

    hf_files = sorted(
        glob.glob(str(raw / "HD_model_data" / "High-fidelity" / "Run[1-9]_alltimesteps.npz"))
    )
    if max_events is not None:
        hf_files = hf_files[:max_events]
    if not hf_files:
        raise FileNotFoundError(f"No Carlisle HF runs in {raw / 'HD_model_data' / 'High-fidelity'}")

    hf_max_list = []
    event_ids = []
    for f in hf_files:
        wse = np.load(f)["wse_data"]
        depth = np.maximum(0, wse - terrain[np.newaxis, :])
        hf_max_list.append(depth.max(axis=0))
        event_ids.append(Path(f).stem.replace("_alltimesteps", ""))
    hf_max = np.stack(hf_max_list)

    lf_files = sorted(
        glob.glob(str(raw / "HD_model_data" / "Low-fidelity" / "Carlisle_LFmodelA.p*.hdf"))
    )[: len(hf_files)]
    lf_max_list = []
    lf_x, lf_y = geo["x_lf"], geo["y_lf"]
    for fp in lf_files:
        with h5py.File(fp, "r") as f:
            wse = f[
                "Results/Unsteady/Output/Output Blocks/"
                "Base Output/Unsteady Time Series/"
                "2D Flow Areas/Carlisle/Water Surface"
            ][:]
        lf_interp = nearest_interp_lf_to_hf(lf_x, lf_y, wse, hf_x, hf_y)
        lf_depth = np.maximum(0, lf_interp - terrain[np.newaxis, :])
        lf_max_list.append(lf_depth.max(axis=0))
    lf_max = np.stack(lf_max_list) if lf_max_list else None

    geo.update(
        hf_max=hf_max,
        lf_max=lf_max,
        event_ids=event_ids,
        n_events=len(event_ids),
        source="fraehr2024",
    )
    return geo


# ---------------------------------------------------------------------------
# Cached LSG-Max packs (HF/LF already on the HF mesh)
# ---------------------------------------------------------------------------

CACHE_NAME = {
    "carlisle": "carlisle_9events.npz",
    "chowilla": "chowilla_29events.npz",
    "burnettrv": "burnettrv_30events.npz",
}

MCL_SHAPE = {
    "carlisle": "Carlisle_MCL.shp",
    "chowilla": "Chowilla_MCL.shp",
}

PUBLISHED_MODELS = ("LSG", "Kabir_1dCNN", "LSTM_SRR", "GP_EOF", "LSTM_EOF")


def processed_dir(root: Path) -> Path:
    return Path(root) / "data" / "processed"


def cache_path(root: Path, case: str) -> Path:
    return processed_dir(root) / CACHE_NAME[case.lower()]


def _atomic_savez(path: Path, **arrays) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.npz")
    np.savez_compressed(tmp, **arrays)
    tmp.replace(path)


def hdf_max_wse(hdf_path: Path, case: str, n_cells: int) -> np.ndarray:
    from lsg.hecras import read_max_wse
    return read_max_wse(hdf_path, case, n_cells=n_cells)


def load_polyline_xy(shp_path: Path) -> tuple[np.ndarray, np.ndarray]:
    import shapefile

    r = shapefile.Reader(str(shp_path))
    xs, ys = [], []
    for s in r.shapes():
        for pt in s.points:
            xs.append(pt[0])
            ys.append(pt[1])
    if not xs:
        raise ValueError(f"No vertices in {shp_path}")
    return np.asarray(xs, dtype=np.float64), np.asarray(ys, dtype=np.float64)


def distance_to_mcl(root: Path, case: str, x: np.ndarray, y: np.ndarray, spacing: float = 5.0) -> np.ndarray:
    """Euclidean distance (m) from each HF cell to the mapped main channel line."""
    from lsg.spatial import densify_polyline, distance_to_path

    raw = raw_dir(root, case)
    shp = raw / "Geometry_data" / MCL_SHAPE[case.lower()]
    if not shp.exists():
        raise FileNotFoundError(shp)
    px, py = load_polyline_xy(shp)
    px, py = densify_polyline(px, py, spacing)
    return distance_to_path(x, y, px, py)


def load_published_npz(root: Path, case: str, extrap: bool = False):
    name = "Validation_results_extrap.npz" if extrap else "Validation_results.npz"
    path = raw_dir(root, case) / "Result_data" / name
    if not path.exists():
        raise FileNotFoundError(path)
    return np.load(path, allow_pickle=True)


def load_burnett_max_pack(root: Path) -> dict[str, Any]:
    """Existing 30-event NPZ (HF/LF already interpolated)."""
    geo = load_case_geometry(root, "burnettrv")
    z = np.load(cache_path(root, "burnettrv"), allow_pickle=True)
    hf_max, lf_max = np.asarray(z["hf_max"]), np.asarray(z["lf_max"])
    if hf_max.shape[1] != geo["n_hf"]:
        raise ValueError(f"Burnett NPZ n_cells={hf_max.shape[1]} != geometry {geo['n_hf']}")
    geo.update(hf_max=hf_max, lf_max=lf_max, n_events=int(hf_max.shape[0]), source="fraehr2024")
    return geo


def build_carlisle_max_pack(root: Path, max_events: int = 9) -> dict[str, Any]:
    """HF max from LISFLOOD NPZ; LF max from HEC-RAS summary WSE → HF interp."""
    from lsg.spatial import nearest_interp_lf_to_hf

    geo = load_case_geometry(root, "carlisle")
    raw = geo["raw_dir"]
    terrain, hf_x, hf_y = geo["terrain_hf"], geo["x_hf"], geo["y_hf"]
    n_hf, n_lf = geo["n_hf"], geo["n_lf"]

    hf_files = sorted(
        glob.glob(str(raw / "HD_model_data" / "High-fidelity" / "Run[1-9]_alltimesteps.npz"))
    )[:max_events]
    lf_files = [
        str(raw / "HD_model_data" / "Low-fidelity" / f"Carlisle_LFmodelA.p{i:02d}.hdf")
        for i in range(1, len(hf_files) + 1)
    ]
    missing = [f for f in lf_files if not Path(f).exists()]
    if missing:
        raise FileNotFoundError(missing[0])

    hf_max_list, lf_max_list, lf_native_list, event_ids = [], [], [], []
    for k, (hf_fp, lf_fp) in enumerate(zip(hf_files, lf_files), start=1):
        print(f"  Carlisle cache {k}/{len(hf_files)} {Path(hf_fp).name}", flush=True)
        wse = np.load(hf_fp)["wse_data"]
        depth = np.maximum(0.0, wse - terrain[np.newaxis, :])
        hf_max_list.append(np.nanmax(depth, axis=0))
        event_ids.append(Path(hf_fp).stem.replace("_alltimesteps", ""))

        wse_lf = hdf_max_wse(Path(lf_fp), "carlisle", n_lf)
        lf_native_list.append(wse_lf)
        lf_interp = nearest_interp_lf_to_hf(
            geo["x_lf"], geo["y_lf"], wse_lf, hf_x, hf_y
        )
        lf_max_list.append(np.maximum(0.0, lf_interp - terrain))

    pack = dict(
        hf_max=np.stack(hf_max_list),
        lf_max=np.stack(lf_max_list),
        lf_max_native=np.stack(lf_native_list),
        event_ids=np.array(event_ids),
        n_hf=n_hf,
        n_lf=n_lf,
        source="fraehr2024",
    )
    _atomic_savez(cache_path(root, "carlisle"), **pack)
    geo.update(**pack, n_events=len(event_ids))
    return geo


def load_or_build_carlisle_max(root: Path, max_events: int = 9) -> dict[str, Any]:
    path = cache_path(root, "carlisle")
    geo = load_case_geometry(root, "carlisle")
    if path.exists():
        z = np.load(path, allow_pickle=True)
        geo.update(
            hf_max=np.asarray(z["hf_max"]),
            lf_max=np.asarray(z["lf_max"]),
            lf_max_native=np.asarray(z["lf_max_native"]) if "lf_max_native" in z.files else None,
            event_ids=np.asarray(z["event_ids"]).tolist(),
            n_events=int(np.asarray(z["hf_max"]).shape[0]),
            source="fraehr2024",
            cache=str(path),
        )
        return geo
    return build_carlisle_max_pack(root, max_events=max_events)


def build_chowilla_max_pack(root: Path, max_events: int | None = None) -> dict[str, Any]:
    """HF/LF max from HEC-RAS summary WSE (29 interpolation events in the CSV)."""
    import csv as _csv

    from lsg.spatial import nearest_interp_lf_to_hf

    geo = load_case_geometry(root, "chowilla")
    raw = geo["raw_dir"]
    n_hf, n_lf = geo["n_hf"], geo["n_lf"]
    terrain, hf_x, hf_y = geo["terrain_hf"], geo["x_hf"], geo["y_hf"]
    summary = raw / "Chowilla_event_summary.csv"
    rows = list(_csv.DictReader(summary.open(encoding="utf-8")))
    if max_events is not None:
        rows = rows[:max_events]

    hf_max_list, lf_max_list, lf_native_list, event_ids = [], [], [], []
    for row in rows:
        plan_hf = row["HEC_RAS_plan_HF"]
        plan_lf = row["HEC_RAS_plan_LF"]
        hf_fp = raw / "HD_model_data" / "High-fidelity" / f"Chow_HF.{plan_hf}.hdf"
        lf_fp = raw / "HD_model_data" / "Low-fidelity" / f"Chow_LF_modelG.{plan_lf}.hdf"
        if not hf_fp.exists() or not lf_fp.exists():
            continue
        wse_hf = hdf_max_wse(hf_fp, "chowilla", n_hf)
        wse_lf = hdf_max_wse(lf_fp, "chowilla", n_lf)
        hf_max_list.append(np.maximum(0.0, wse_hf - terrain))
        lf_native_list.append(wse_lf)
        lf_interp = nearest_interp_lf_to_hf(
            geo["x_lf"], geo["y_lf"], wse_lf, hf_x, hf_y
        )
        lf_max_list.append(np.maximum(0.0, lf_interp - terrain))
        event_ids.append(f"Chow_{plan_hf}")

    if not hf_max_list:
        raise FileNotFoundError(f"No Chowilla HDF pairs under {raw / 'HD_model_data'}")

    pack = dict(
        hf_max=np.stack(hf_max_list),
        lf_max=np.stack(lf_max_list),
        lf_max_native=np.stack(lf_native_list),
        event_ids=np.array(event_ids),
        n_hf=n_hf,
        n_lf=n_lf,
        source="fraehr2024",
    )
    _atomic_savez(cache_path(root, "chowilla"), **pack)
    geo.update(**pack, n_events=len(event_ids))
    return geo


def load_or_build_chowilla_max(root: Path, max_events: int | None = None) -> dict[str, Any]:
    path = cache_path(root, "chowilla")
    geo = load_case_geometry(root, "chowilla")
    if path.exists():
        z = np.load(path, allow_pickle=True)
        n_have = int(np.asarray(z["hf_max"]).shape[0])
        if max_events is None or n_have >= max_events:
            geo.update(
                hf_max=np.asarray(z["hf_max"])[: max_events or n_have],
                lf_max=np.asarray(z["lf_max"])[: max_events or n_have],
                lf_max_native=(
                    np.asarray(z["lf_max_native"])[: max_events or n_have]
                    if "lf_max_native" in z.files else None
                ),
                event_ids=np.asarray(z["event_ids"]).tolist()[: max_events or n_have],
                n_events=max_events or n_have,
                source="fraehr2024",
                cache=str(path),
            )
            return geo
    return build_chowilla_max_pack(root, max_events=max_events)


def load_carlisle_extrap_max(root: Path) -> dict[str, Any]:
    """p10 / p11 extrapolation max surfaces. HF truth from raw NPZ, not stored MaxWD[:,0]."""
    from lsg.spatial import nearest_interp_lf_to_hf

    geo = load_case_geometry(root, "carlisle")
    raw = geo["raw_dir"]
    terrain, hf_x, hf_y = geo["terrain_hf"], geo["x_hf"], geo["y_hf"]
    n_lf = geo["n_lf"]
    specs = [
        ("p10", "Run1_50pc_extrap_alltimesteps.npz", "Carlisle_LFmodelA.p10.hdf"),
        ("p11", "Run9_100pc_extrap_alltimesteps.npz", "Carlisle_LFmodelA.p11.hdf"),
    ]
    hf_max_list, lf_max_list, ids = [], [], []
    for eid, hf_name, lf_name in specs:
        hf_fp = raw / "HD_model_data" / "High-fidelity" / hf_name
        lf_fp = raw / "HD_model_data" / "Low-fidelity" / lf_name
        wse = np.load(hf_fp)["wse_data"]
        hf_max_list.append(np.nanmax(np.maximum(0.0, wse - terrain[np.newaxis, :]), axis=0))
        wse_lf = hdf_max_wse(lf_fp, "carlisle", n_lf)
        lf_interp = nearest_interp_lf_to_hf(geo["x_lf"], geo["y_lf"], wse_lf, hf_x, hf_y)
        lf_max_list.append(np.maximum(0.0, lf_interp - terrain))
        ids.append(eid)
    geo.update(
        hf_max=np.stack(hf_max_list),
        lf_max=np.stack(lf_max_list),
        event_ids=ids,
        n_events=2,
        source="fraehr2024_extrap",
    )
    return geo
