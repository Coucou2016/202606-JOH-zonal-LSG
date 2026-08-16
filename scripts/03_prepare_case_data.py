#!/usr/bin/env python
"""Standardise benchmark data into the unified NPZ schema.

Default: ingest real Fraehr (2024) geometry (and optional max-surfaces).
Synthetic 30x40 grids are opt-in via ``--synthetic`` and must not be cited.

Canonical paper experiments use scripts/30_carlisle_proper.py and
scripts/31_burnettrv_validation.py rather than this processed-tree path.
"""
import argparse
import csv
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.fraehr import load_carlisle_max_surfaces, load_case_geometry, raw_dir_exists
from lsg.io import (
    save_event,
    save_geometry,
    save_max_surface,
    save_split,
)
from lsg.spatial import (
    cell_areas_uniform,
    coarsen_grid,
)


def generate_synthetic_case(
    case_name: str,
    n_events: int = 12,
    n_timesteps: int = 48,
    hf_shape: tuple = (30, 40),
    lf_factor: int = 4,
    seed: int = 42,
) -> dict:
    """Generate synthetic HF/LF data for smoke-testing a case."""
    rng = np.random.default_rng(seed)
    ny, nx = hf_shape
    ny_lf, nx_lf = ny // lf_factor, nx // lf_factor

    x = np.linspace(0, 1, nx)
    y = np.linspace(0, 1, ny)
    xx, yy = np.meshgrid(x, y)
    terrain = 10.0 + 5.0 * yy + 0.5 * np.sin(4 * np.pi * xx) * np.cos(2 * np.pi * yy)

    x_hf = xx.ravel().astype(np.float64)
    y_hf = yy.ravel().astype(np.float64)
    terrain_hf = terrain.ravel().astype(np.float64)

    x_lf_coarse = np.linspace(0, 1, nx_lf)
    y_lf_coarse = np.linspace(0, 1, ny_lf)
    xx_lf, yy_lf = np.meshgrid(x_lf_coarse, y_lf_coarse)
    x_lf = xx_lf.ravel().astype(np.float64)
    y_lf = yy_lf.ravel().astype(np.float64)

    hf_events, lf_events, event_ids = [], [], []
    for e in range(n_events):
        amplitude = 0.5 + 1.5 * rng.random()
        peak_t = int(n_timesteps * (0.3 + 0.4 * rng.random()))
        ts = np.arange(n_timesteps)
        hydro = amplitude * np.exp(
            -0.5 * ((ts - peak_t) / (0.15 * n_timesteps + 1)) ** 2
        )
        spatial_pattern = np.exp(
            -((xx - 0.3 - 0.1 * e / n_events) ** 2 + (yy - 0.5) ** 2) / 0.08
        )
        depth_hf = np.outer(hydro, spatial_pattern.ravel())
        depth_hf = np.clip(
            depth_hf - np.maximum(terrain_hf - 12.0, 0) * 0.1, 0, None
        ).astype(np.float64)
        depth_lf = coarsen_grid(depth_hf, hf_shape, lf_factor).astype(np.float64)
        hf_events.append(depth_hf)
        lf_events.append(depth_lf)
        event_ids.append(f"{case_name}_event_{e:02d}")

    return {
        "x_hf": x_hf, "y_hf": y_hf,
        "x_lf": x_lf, "y_lf": y_lf,
        "terrain_hf": terrain_hf,
        "shape_hf": hf_shape, "shape_lf": (ny_lf, nx_lf),
        "hf_events": hf_events, "lf_events": lf_events,
        "event_ids": event_ids,
        "source": "synthetic",
    }


def _write_synthetic_tree(case_name: str, data: dict, processed_dir: Path) -> None:
    processed_dir.mkdir(parents=True, exist_ok=True)
    areas_hf = cell_areas_uniform(data["shape_hf"], 1.0)
    areas_lf = cell_areas_uniform(data["shape_lf"], 1.0)
    save_geometry(
        processed_dir / "geometry.npz",
        x_hf=data["x_hf"],
        y_hf=data["y_hf"],
        terrain_hf=data["terrain_hf"],
        area_hf=areas_hf,
        x_lf=data["x_lf"],
        y_lf=data["y_lf"],
        area_lf=areas_lf,
        meta={"case": case_name, "source": "synthetic"},
    )

    events_dir = processed_dir / "events"
    events_dir.mkdir(exist_ok=True)
    for i, eid in enumerate(data["event_ids"]):
        save_event(
            events_dir / f"{eid}_HF_ts.npz",
            depth=data["hf_events"][i],
            event_id=eid,
            is_hf=True,
        )
        save_event(
            events_dir / f"{eid}_LF_ts.npz",
            depth=data["lf_events"][i],
            event_id=eid,
            is_hf=False,
        )
        save_max_surface(
            events_dir / f"{eid}_HF_max.npz",
            max_depth=data["hf_events"][i].max(axis=0),
            event_id=eid,
            is_hf=True,
        )
        save_max_surface(
            events_dir / f"{eid}_LF_max.npz",
            max_depth=data["lf_events"][i].max(axis=0),
            event_id=eid,
            is_hf=False,
        )

    n = len(data["event_ids"])
    rng = np.random.default_rng(42)
    idx = rng.permutation(n)
    n_train = int(0.8 * n)
    splits_dir = processed_dir / "splits"
    splits_dir.mkdir(exist_ok=True)
    save_split(
        splits_dir / "fold_00.json",
        train_indices=idx[:n_train],
        val_indices=idx[n_train:],
    )

    meta_path = processed_dir / "metadata.csv"
    with meta_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "value"])
        writer.writerow(["case_name", case_name])
        writer.writerow(["n_events", n])
        writer.writerow(["n_timesteps", 48])
        writer.writerow(["hf_shape", f"{data['shape_hf']}"])
        writer.writerow(["lf_shape", f"{data['shape_lf']}"])
        writer.writerow(["n_hf_cells", data["shape_hf"][0] * data["shape_hf"][1]])
        writer.writerow(["source", "synthetic"])
        writer.writerow(["do_not_cite", "true"])

    print(f"Prepared SYNTHETIC {case_name}: {n} events -> {processed_dir}")
    print("  WARNING: synthetic 30x40 grids are not citable paper results.")


def _write_real_geometry(case_name: str, geo: dict, processed_dir: Path) -> None:
    processed_dir.mkdir(parents=True, exist_ok=True)
    save_geometry(
        processed_dir / "geometry.npz",
        x_hf=geo["x_hf"],
        y_hf=geo["y_hf"],
        terrain_hf=geo["terrain_hf"],
        area_hf=geo["area_hf"],
        x_lf=geo.get("x_lf"),
        y_lf=geo.get("y_lf"),
        terrain_lf=geo.get("terrain_lf"),
        area_lf=geo.get("area_lf"),
        meta={
            "case": case_name,
            "source": "fraehr2024",
            "n_hf_cells": geo["n_hf"],
            "n_lf_cells": geo.get("n_lf"),
        },
    )
    meta_path = processed_dir / "metadata.csv"
    with meta_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "value"])
        writer.writerow(["case_name", case_name])
        writer.writerow(["n_hf_cells", geo["n_hf"]])
        writer.writerow(["n_lf_cells", geo.get("n_lf", "")])
        writer.writerow(["source", "fraehr2024"])
        writer.writerow(["events", "geometry_only" if "hf_max" not in geo else geo.get("n_events", "")])
    print(f"Wrote real Fraehr geometry for {case_name}: "
          f"HF={geo['n_hf']:,} LF={geo.get('n_lf')}")


def ingest_real_case(
    case_name: str,
    raw_dir: Path,
    processed_dir: Path,
    with_events: bool = False,
    max_events: int | None = None,
) -> None:
    """Ingest real Fraehr data. Geometry is always written; events are opt-in."""
    if not raw_dir_exists(_ROOT, case_name) and not (raw_dir / "Geometry_data").is_dir():
        raise FileNotFoundError(
            f"Raw Fraehr directory not found: {raw_dir}. "
            "Pass --synthetic for the 30x40 smoke-test grids (not citable)."
        )

    if with_events:
        if case_name != "carlisle":
            raise NotImplementedError(
                f"--with-events is implemented for Carlisle only. "
                f"Use scripts/30_carlisle_proper.py or scripts/31_burnettrv_validation.py "
                f"for paper runs. Geometry-only ingest is available for {case_name}."
            )
        print(f"Ingesting Carlisle max-surfaces (slow I/O)...")
        geo = load_carlisle_max_surfaces(_ROOT, max_events=max_events)
        _write_real_geometry(case_name, geo, processed_dir)
        events_dir = processed_dir / "events"
        events_dir.mkdir(exist_ok=True)
        for i, eid in enumerate(geo["event_ids"]):
            save_max_surface(
                events_dir / f"{eid}_HF_max.npz",
                max_depth=geo["hf_max"][i],
                event_id=eid,
                is_hf=True,
            )
            if geo.get("lf_max") is not None:
                save_max_surface(
                    events_dir / f"{eid}_LF_max.npz",
                    max_depth=geo["lf_max"][i],
                    event_id=eid,
                    is_hf=False,
                )
        print(f"  Saved {len(geo['event_ids'])} max-surfaces -> {events_dir}")
        return

    geo = load_case_geometry(_ROOT, case_name)
    _write_real_geometry(case_name, geo, processed_dir)


def prepare_from_raw(
    case_name: str,
    raw_dir: Path,
    processed_dir: Path,
    use_synthetic: bool = False,
    with_events: bool = False,
    max_events: int | None = None,
) -> None:
    processed_dir = Path(processed_dir)
    if use_synthetic:
        print(f"Generating synthetic data for {case_name} (--synthetic)...")
        data = generate_synthetic_case(case_name, seed=hash(case_name) % 10000)
        _write_synthetic_tree(case_name, data, processed_dir)
        return

    ingest_real_case(
        case_name, Path(raw_dir), processed_dir,
        with_events=with_events, max_events=max_events,
    )


def main():
    parser = argparse.ArgumentParser(description="Prepare case data")
    parser.add_argument("--case", required=True,
                        choices=["carlisle", "chowilla", "burnettrv", "brisbane", "all"])
    parser.add_argument(
        "--synthetic",
        action="store_true",
        default=False,
        help="Generate 30x40 synthetic grids (NOT citable). Default is real Fraehr ingest.",
    )
    parser.add_argument(
        "--with-events",
        action="store_true",
        default=False,
        help="Also write HF/LF max-surfaces (Carlisle only; slow). Default: geometry+metadata.",
    )
    parser.add_argument("--max-events", type=int, default=None)
    parser.add_argument("--raw-dir", default=None,
                        help="Override raw data directory")
    args = parser.parse_args()

    if args.case == "brisbane" and not args.synthetic:
        raise SystemExit("Brisbane real ingest is not in this pipeline. Use --synthetic for a toy grid.")

    root = Path(__file__).resolve().parents[1]
    cases = ["carlisle", "chowilla", "burnettrv"] if args.case == "all" else [args.case]

    for case in cases:
        raw_dir = Path(args.raw_dir) if args.raw_dir else (
            root / "data" / "external" / "fraehr2024" / case.capitalize()
        )
        if case == "burnettrv":
            raw_dir = root / "data" / "external" / "fraehr2024" / "BurnettRV"
        processed_dir = root / "data" / "processed" / case
        prepare_from_raw(
            case, raw_dir, processed_dir,
            use_synthetic=args.synthetic,
            with_events=args.with_events,
            max_events=args.max_events,
        )


if __name__ == "__main__":
    main()
