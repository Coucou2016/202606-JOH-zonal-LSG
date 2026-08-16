#!/usr/bin/env python
"""
Prepare real Carlisle benchmark data for the JOH zonal LSG pipeline.

Deprecated as the paper entry point — use scripts/03_prepare_case_data.py
(real ingest) or scripts/30_carlisle_proper.py. Canonical report: scripts/95_final_submission_report.py.

Loads Fraehr (2024) Carlisle data from the raw NPZ + HDF5 files and converts
to the unified format expected by scripts/04-09.

Data structure (after Fraehr et al.):
  HF: LISFLOOD-FP unstructured mesh, 581,061 cells, 266 timesteps per event
  LF: HEC-RAS 2D unstructured mesh, 5,991 cells, 274 timesteps per event
  9 validation groups (folds)

Usage:
  python scripts/03b_prepare_carlisle_real.py [--fold 1] [--use-preprocessed]
"""
import argparse
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.io import save_geometry, save_event, save_max_surface, save_split


def load_hf_geometry(raw_dir: Path) -> dict:
    """Load HF (LISFLOOD-FP) geometry."""
    geo = np.load(raw_dir / "Geometry_data" / "Lisflood_Geometry_data.npz",
                  allow_pickle=True)
    return {
        "xy": geo["XY_coor"],          # (581061, 2)
        "z": geo["Z_coor"],             # (581061,)
        "area": geo["Area"],            # (581061,)
    }


def load_lf_geometry(raw_dir: Path) -> dict:
    """Load LF (HEC-RAS) geometry."""
    geo = np.load(raw_dir / "Geometry_data" / "LF_Geometry_data.npz",
                  allow_pickle=True)
    return {
        "xy": geo["XY_coor"],           # (5681, 2)
        "z": geo["Z_coor"],             # (5681,)
        "area": geo["Area"],            # (5681,)
    }


def load_hf_runs(raw_dir: Path, event_ids: list[str] | None = None) -> dict:
    """Load all HF simulation runs.

    Each run has wse_data: (n_timesteps, 581061).
    Returns stacked arrays and run boundaries.
    """
    hf_dir = raw_dir / "HD_model_data" / "High-fidelity"
    if event_ids is None:
        # Default: load all standard runs
        npz_files = sorted(hf_dir.glob("Run[1-9]_alltimesteps.npz"))
    else:
        npz_files = [hf_dir / f"{eid}.npz" for eid in event_ids]

    wse_list, run_sizes, ids = [], [], []
    for f in npz_files:
        if not f.exists():
            print(f"  [skip] {f.name} not found")
            continue
        data = np.load(f, allow_pickle=True)
        wse = data["wse_data"]  # (n_t, n_cells)
        wse_list.append(wse)
        run_sizes.append(wse.shape[0])
        ids.append(f.stem.replace("_alltimesteps", ""))

    if not wse_list:
        raise FileNotFoundError(f"No HF runs found in {hf_dir}")

    all_wse = np.vstack(wse_list)  # (total_timesteps, n_cells)
    return {
        "wse": all_wse,
        "run_sizes": run_sizes,
        "event_ids": ids,
        "n_timesteps": all_wse.shape[0],
        "n_cells": all_wse.shape[1],
    }


def load_lf_wse_hdf5(raw_dir: Path, lf_files: list[str]) -> np.ndarray:
    """Load LF WSE from HEC-RAS HDF5 files using h5py."""
    try:
        import h5py
    except ImportError:
        raise ImportError("h5py required for LF HDF5 reading. "
                          "Install: conda install h5py")

    lf_dir = raw_dir / "HD_model_data" / "Low-fidelity"
    wse_list = []
    for fname in lf_files:
        fpath = lf_dir / fname
        if not fpath.exists():
            print(f"  [warn] {fname} not found")
            continue
        with h5py.File(fpath, "r") as f:
            wse = f["Results/Unsteady/Output/Output Blocks/"
                     "Base Output/Unsteady Time Series/"
                     "2D Flow Areas/Carlisle/Water Surface"][:]
            wse_list.append(wse)  # (n_t, n_lf_cells)

    return np.vstack(wse_list)


def load_train_test_split(raw_dir: Path, fold: int = 1) -> dict:
    """Load train/test split for a given fold."""
    split_path = (raw_dir / "Train_test_split_data" /
                  f"Train_test_split_ValidateOnGrp_{fold}.npz")
    data = np.load(split_path, allow_pickle=True)
    return {
        "train": data["idx_train"].astype(int),
        "test": data["idx_test"].astype(int),
    }


def load_categories(raw_dir: Path, fold: int = 1) -> dict:
    """Load pre-computed wet/dry cell categories."""
    cat_path = (raw_dir / "HF_EOF_analysis" /
                f"Categories_HFdata_ValidateOnGrp_{fold}.npz")
    data = np.load(cat_path, allow_pickle=True)
    return {
        "wet_idx": data["wet_idx"],       # wet cells (always+temporary)
        "af_idx": data["AF_idx"],          # always-flooded
        "tf_idx": data["TF_idx"],          # temporarily-flooded
        "ad_idx": data["AD_idx"],          # always-dry
    }


def process_fold(
    raw_dir: Path,
    processed_dir: Path,
    fold: int = 1,
    use_preprocessed: bool = False,
) -> None:
    """Process one validation fold into the unified format."""
    print(f"\n{'='*60}")
    print(f"Processing Carlisle fold {fold}...")
    print(f"{'='*60}")

    # Load geometry
    hf_geo = load_hf_geometry(raw_dir)
    lf_geo = load_lf_geometry(raw_dir)
    n_hf = hf_geo["xy"].shape[0]
    n_lf = lf_geo["xy"].shape[0]
    print(f"  HF cells: {n_hf}, LF cells: {n_lf}")

    # Load categories
    cats = load_categories(raw_dir, fold)
    wet_idx = cats["wet_idx"]
    n_wet = len(wet_idx)
    print(f"  Wet cells: {n_wet} / {n_hf} ({100*n_wet/n_hf:.1f}%)")

    # Load HF runs
    hf_data = load_hf_runs(raw_dir)
    hf_wse = hf_data["wse"]  # (total_t, n_hf)
    total_t = hf_data["n_timesteps"]
    print(f"  HF total timesteps: {total_t} across {len(hf_data['event_ids'])} runs")

    # Compute depth from WSE
    terrain = hf_geo["z"]
    hf_depth = np.maximum(0, hf_wse - terrain[np.newaxis, :])  # (T, n_hf)

    # Load split
    split = load_train_test_split(raw_dir, fold)
    idx_train = split["train"]
    idx_test = split["test"]
    print(f"  Train timesteps: {len(idx_train)}, Test: {len(idx_test)}")

    # --- Save geometry ---
    out_geo_dir = processed_dir / "geometry"
    out_geo_dir.mkdir(parents=True, exist_ok=True)
    save_geometry(
        out_geo_dir / f"fold_{fold:02d}.npz",
        x_hf=hf_geo["xy"][:, 0],
        y_hf=hf_geo["xy"][:, 1],
        terrain_hf=terrain,
        area_hf=hf_geo["area"],
        x_lf=lf_geo["xy"][:, 0],
        y_lf=lf_geo["xy"][:, 1],
        area_lf=lf_geo["area"],
        meta={
            "case": "carlisle",
            "fold": fold,
            "n_hf_cells": n_hf,
            "n_lf_cells": n_lf,
            "n_wet_cells": n_wet,
        },
    )

    # --- Save train/test depth data ---
    events_dir = processed_dir / "events"
    events_dir.mkdir(parents=True, exist_ok=True)

    # We'll save the full time series as a single "event" for now
    # (real event-by-event separation would need the run boundaries)
    save_event(
        events_dir / f"fold_{fold:02d}_HF_ts.npz",
        depth=hf_depth,
        event_id=f"carlisle_fold{fold}",
        is_hf=True,
    )
    save_max_surface(
        events_dir / f"fold_{fold:02d}_HF_max.npz",
        max_depth=hf_depth.max(axis=0),
        event_id=f"carlisle_fold{fold}",
        is_hf=True,
    )

    # --- Save splits ---
    splits_dir = processed_dir / "splits"
    splits_dir.mkdir(parents=True, exist_ok=True)
    save_split(
        splits_dir / f"fold_{fold:02d}.json",
        train_indices=idx_train,
        val_indices=idx_test,
    )

    # --- Save metadata ---
    import json
    meta = {
        "case": "carlisle",
        "fold": fold,
        "n_hf_cells": n_hf,
        "n_lf_cells": n_lf,
        "n_wet_cells": n_wet,
        "n_timesteps": total_t,
        "n_train": len(idx_train),
        "n_test": len(idx_test),
        "hf_runs": hf_data["event_ids"],
        "run_sizes": hf_data["run_sizes"],
        "source": "Fraehr 2024 benchmark",
    }
    with (processed_dir / f"metadata_fold{fold:02d}.json").open("w") as f:
        json.dump(meta, f, indent=2)

    print(f"  Saved to {processed_dir}")
    print(f"  Fold {fold} complete.")


def main():
    parser = argparse.ArgumentParser(
        description="Prepare real Carlisle data for JOH pipeline"
    )
    parser.add_argument("--fold", type=int, default=1, choices=range(1, 10))
    parser.add_argument("--all-folds", action="store_true")
    parser.add_argument("--raw-dir", default=None)
    parser.add_argument("--processed-dir", default=None)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    raw_dir = Path(args.raw_dir) if args.raw_dir else (
        root / "data" / "external" / "fraehr2024" / "Carlisle"
    )
    processed_dir = Path(args.processed_dir) if args.processed_dir else (
        root / "data" / "processed" / "carlisle"
    )

    folds = range(1, 10) if args.all_folds else [args.fold]

    for fold in folds:
        try:
            process_fold(raw_dir, processed_dir, fold=fold)
        except Exception as e:
            print(f"  [ERROR] Fold {fold}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
