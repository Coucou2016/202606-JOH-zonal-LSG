# Hydrodynamically Zoned EOF-LSG for Rapid Flood Inundation Prediction

Journal of Hydrology submission: **Improving physics-guided multi-fidelity flood inundation emulation using hydrodynamic zonal EOF decomposition**

## Overview

This repository implements *hydrodynamically zoned LSG* — a spatial extension of the physics-guided LSG (Low-fidelity, Spatial analysis, Gaussian Process) framework for rapid flood inundation emulation in complex floodplains.

Key innovation: partitioning the floodplain into hydrodynamic zones before EOF reduction and GP learning, improving local depth and extent prediction accuracy without sacrificing speed.

**Cite Track B (real Fraehr 2024 data) only.** Primary numbers live in `outputs/registry/result_manifest_v4.csv` and `outputs/evaluation/carlisle/budget_sweep_true_equal.json`. Carlisle Rule B=4: area-weighted RMSE 0.1464 → 0.0964 m (−34.2%), 9/9 LOOCV. Official 2-fold `multifold_bootstrap.json` has `significant=false`. Burnett 30-fold event LOOCV (`outputs/evaluation/burnettrv/loocv_results.json`) does **not** show zonal Rule beating Global. Git commit of the staged tree still needs `user.name` / `user.email` (this repo does not set git config).

Synthetic 30×40 grids under `data/processed/*/` (scripts/03–09 with `--synthetic`) are smoke-test fixtures. They are **not** paper results.

## Quick Start

Prefer CPython 3.11. If `lsg-joh` is not installed (conda-forge SSL), use `D:\miniforge3\envs\hydromodel\python.exe`. The default `python` on some machines is PyPy — do not use it. Git commit of the staged tree still needs `user.name` / `user.email` (this repo does not set git config).

```bash
conda activate lsg-joh
pip install -r requirements.txt

# Geometry smoke-test (no synthetic grids)
python -c "from lsg.fraehr import load_case_geometry; from pathlib import Path; g=load_case_geometry(Path('.'),'carlisle'); print(g['n_hf'], g['n_lf'])"
pytest

# Paper tables + report from existing Track B artefacts (no model re-run)
python scripts/09_make_tables.py
python scripts/95_final_submission_report.py
```

### Paper pipeline (Track B — cite this)

```bash
# Carlisle real LF (HEC-RAS HDF5), equal-budget, area-weighted
python scripts/30_carlisle_proper.py

# BurnettRV standard-mesh validation
python scripts/31_burnettrv_validation.py
python scripts/32_burnettrv_loocv.py   # 30-event LOOCV from burnettrv_30events.npz

# Rebuild registry from evaluation JSON (skip EOI recompute)
python scripts/45_build_registry.py --skip-eoi

# Canonical report
python scripts/95_final_submission_report.py
```

Related: `scripts/10_full_real_experiment.py`, `scripts/20_audit_leakage.py`.

### Synthetic smoke-test only (do not cite)

```bash
python scripts/03_prepare_case_data.py --case carlisle --synthetic
python scripts/04_run_global_lsg.py --case carlisle --variant ts --fold all
python scripts/05_run_zonal_lsg.py --case carlisle --variant ts --zoning kmeans --n-zones 4 --mode-budget free --fold all
```

Real Fraehr ingest (geometry; default is **not** synthetic):

```bash
python scripts/03_prepare_case_data.py --case carlisle
# optional, slow: also write max-surfaces
python scripts/03_prepare_case_data.py --case carlisle --with-events
```

If the raw directory exists, omitting `--synthetic` will not silently invent 30×40 data.

## Project Structure

```
├── config/           # Case and experiment YAML configs
├── data/             # External downloads + processed case data
├── lsg/              # Core library (EOF, GP, zoning, metrics, Fraehr loader)
├── scripts/          # 30/31/45/95 = paper; 03–09 = synthetic unless noted
├── outputs/          # evaluation JSON + registry CSV are the paper numbers
├── notebooks/        # Exploratory notebooks
└── tests/            # Pytest suite
```

## Environment

- Conda env name: `lsg-joh` (CPython 3.11). See `environment.lock.txt` when present.
- `gpflow` / TensorFlow are optional and **not** required for the sklearn GPR results in the registry.
- Brisbane and Chowilla re-download are out of scope for the artefact rebuild.

## Reference

Based on the LSG framework from:
- Fraehr et al. (2022, 2023, 2024) — LSG methodology and benchmark datasets
- Wang et al. (2026) WRR — LSG-TS and LSG-Max variants for complex floodplains

## License

MIT License. See LICENSE file for details.
