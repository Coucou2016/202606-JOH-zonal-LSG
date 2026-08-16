# Supplementary Information — Hyperparameters and protocol defaults

Extracted from repository source/config (not guessed). Production Track B numbers use **sklearn GPR**; gpflow paths exist in code but are inactive when TensorFlow/gpflow are absent.

## S1. Shared hydrodynamic / evaluation defaults

| Parameter | Value | Source |
|---|---|---|
| Wet-cell depth threshold | 0.03 m | config/cases/*.yaml hydrodynamic.depth_threshold_m; CSI/POD/FAR |
| Random seed | 42 | config/experiments/joh_main.yaml lsg.random_seed; leakage audit |
| Area weighting (metrics) | geometric Area from Fraehr geometry NPZ | lsg/fraehr.py _xy_z_area; Carlisle Area≡25 m²; Burnett≡400 m²; Chowilla variable |
| EOF cell-area weights in fit | uniform cell_areas_uniform(..., 1.0) in baseline/zonal fit path | lsg/baseline_lsg.py, lsg/zonal_lsg.py |
| Primary matched budgets (Carlisle) | B ∈ {4, 6}; nominal B=8 audited MISMATCH (realized 7) | outputs/evaluation/carlisle/budget_sweep_true_equal.json |

## S2. Zoning defaults (Track B production)

| Parameter | Value | Source |
|---|---|---|
| Rule features | training max depth; inundation frequency; optional LF–HF mean abs residual hotspot override | lsg/zoning.py 
ule_based_zones |
| Rule deep / error percentiles | 80 / 80 | ZoningConfig.deep_percentile, error_percentile |
| Rule frequent / intermittent thresholds | 0.7 / 0.1 | ZoningConfig |
| KMeans K | 4 (paper primary); config also lists 6 | Track B scripts; joh_main.yaml 
_zones: [4, 6] |
| KMeans scaler | StandardScaler fit on **train** active cells only | lsg/zoning.py kmeans_zones |
| KMeans 
_init / max_iter / 
andom_state | 20 / 500 / 42 | lsg/zoning.py |

## S3. GP coefficient mapping (production sklearn path)

| Parameter | Value | Source |
|---|---|---|
| Backend (production) | sklearn.gaussian_process.GaussianProcessRegressor | lsg/gp.py 	rain_sparse_gp_sklearn |
| Kernel (sklearn) | RBF(length_scale=1.0) + WhiteKernel(noise_level=0.05) | lsg/gp.py |
| 
_restarts_optimizer | 3 | lsg/gp.py |
| lpha | 1e-6 | lsg/gp.py |
| Input/output scaling | per-mode StandardScaler (sklearn if available, else numpy) | lsg/gp.py make_scaler |
| gpflow SGPR (code path only) | Exponential/Matern32/SE kernel; inducing fraction 0.02; two-phase L-BFGS-B (maxiter=100 each) | lsg/gp.py 	rain_sparse_gp_gpflow; **not executed** in hydromodel env (no gpflow/TF) |
| Config inducing fraction / named kernel | 0.02 / exponential | joh_main.yaml (intended for gpflow path) |

## S4. Statistical protocols

| Protocol | Setting | Artefact |
|---|---|---|
| Carlisle primary paired test | 9-fold event LOOCV at B=4 (secondary B=6) | loocv_results.json, loocv_bootstrap_ci.json |
| Bootstrap CI | mean ΔRMSE; rng=42; n=10000 | loocv_bootstrap_ci.json method field |
| Official 2-fold | sensitivity only; significant=false | multifold_bootstrap.json |
| Burnett contrast | 30-fold event LOOCV at B=4 | urnettrv/loocv_results.json |
| Leakage autofold audit | synthetic corruption + official split disjointness | outputs/audit/leakage_autofold.json |
| Area-weighted pure-EOF oracle | pooled HF-only; cell areas from geometry | modal_eoi.json oracle_*_area |

## S5. Scope boundaries (not missing hyperparameters)

- Brisbane: licensed TUFLOW/URBS data not present (config/cases/brisbane.yaml).
- Track B headline claims are **LSG-Max** with sklearn GPR; real-data zonal LSG-TS is out of scope for this manuscript.
- No transferable operational zoning selector is claimed after EOI falsification.
