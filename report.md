# When Is Global EOF Reduction Insufficient for Multi-Fidelity Flood Inundation Emulation?

*A Hydrodynamically Zoned LSG-Max Approach — Final Report v4, 2026-08-16 11:09*

## 1. Abstract

This study asks whether EOF reduction in multi-fidelity flood emulation is hydrodynamically neutral. Hydrodynamically zoned LSG-Max partitions the floodplain before EOF and GP learning. Evaluation uses the Fraehr (2024) public benchmark. Numbers are read from `outputs/registry/result_manifest_v4.csv` and `outputs/evaluation/carlisle/budget_sweep_true_equal.json`.

> **Primary result (Carlisle, 9-fold LOOCV):** At equal budget B=4, zonal Rule LSG-Max reduces area-weighted RMSE from 0.1464 m (Global) to 0.0964 m (34.2% improvement; 9/9 folds improved; 95% CI [0.0155, 0.1987] m). Global LSG degrades as B grows (0.1464 → 0.2588 → 0.3527) while zonal Rule stays more robust (0.0964 → 0.1256 → 0.1790). Max-surface EOI = 0.057 (LOW). First-order EOI is not a zoning switch.
> **Official 2-fold split is not significant.** `multifold_bootstrap.json`: NOT significant (mean Delta RMSE = 0.0045 m, 95% CI [-0.0073, 0.0134], improved fraction 75%). The 9-fold event LOOCV is the primary statistical claim.

> **Burnett 30-fold event LOOCV:** Burnett 30-fold event LOOCV at B=4: mean Global RMSE 1.7479 m vs Rule 1.8260 m (mean Delta RMSE -0.0781 m; 6/30 folds zonal better; significant=false). Zonal Rule does not improve on Global (not significant).

## 2. Data and methods

**Table 1. Case summary.** Cell counts from Fraehr geometry files.

| Property | Carlisle | Chowilla | Burnett River |
|---|---|---|---|
| Country | UK | Australia | Australia |
| HF Model | LISFLOOD-FP | MIKE 21 | TUFLOW |
| LF Model | HEC-RAS 2D | MIKE 21 (coarse) | HEC-RAS 2D |
| HF Cells | 581,061 | 109,914 | 780,785 |
| LF Cells | 5,681 | 1,434 | 15,256 |
| Events used / available | 9 / 9 | 12 / 31 | 30 / 74 |
| Status | 9-fold LOOCV | Boundary: LSG degrades | 30-fold LOOCV (zonal not better) |
| LF-only RMSE (m) | 0.1602 | 0.3926 | 2.2323 |
| Max-surface EOI | 0.057 (LOW) | 0.116 | 0.957 |

LSG-Max uses EOF on wet cells (depth >= 0.03 m) then sklearn GPR. True equal budget: Global and zonal use total mode count B. Zoning, EOF, and GP are fit on training events only (leakage audit CLEAN PASS).

Track A synthetic 30×40 processed trees are **not cited**. Paper scripts: `30_carlisle_proper.py`, `31_burnettrv_validation.py`, `32_burnettrv_loocv.py`, `10_full_real_experiment.py`, `45_build_registry.py`, `95_final_submission_report.py`.

## 3. Results

### 3.1 True equal-budget (Carlisle)

| B | Global RMSE | Rule RMSE | KMeans RMSE | Delta Rule |
|---|---|---|---|---|
| 4 | 0.1464 | 0.0964 | 0.1015 | +34.2% |
| 6 | 0.2588 | 0.1256 | 0.1367 | +51.5% |
| 8 | 0.3527 | 0.1790 | 0.2980 | +49.3% |

Finding 1: Global RMSE rises 141% from B=4 to B=8. Rule zonal rises 86%. Finding 2: at B=4, Rule improves 34.2% over Global at the same mode budget.

### 3.2 Statistical validation

| Budget | Folds improved | Mean Delta RMSE (m) | 95% CI | CI excludes 0 |
|---|---|---|---|---|
| B=4 LOOCV | 9/9 | 0.0821 | [0.0155, 0.1987] | YES |
| B=6 LOOCV | 7/9 | 0.0606 | [0.0032, 0.1618] | YES |
| Official 2-fold | 75% of test events | 0.0045 | [-0.0073, 0.0134] | NO |
| Burnett B=4 LOOCV | 6/30 | -0.0781 | [-0.2116, 0.0405] | NO |

The official 2-fold bootstrap CI includes zero (`significant=false`). Report the 9-fold LOOCV as the event-level result.

### 3.3 Three-case comparison

| Case | LF-only RMSE | Global B=4 | Zonal Rule B=4 | Pattern |
|---|---|---|---|---|
| Carlisle | 0.1602 | 0.1464 | 0.0964 (+34.2%) | Zonal > Global > LF |
| Chowilla | 0.3926 | 2.5606 | 2.5614 | LF-only best; LSG degrades |
| BurnettRV | 2.2323 | 1.6120 | 1.6122 | 12-event split: Global ~ zonal |

Chowilla is a **boundary case**: LSG RMSE ~2.5606 m versus LF-only 0.3926 m (LSG degrades). Burnett River (12-event split): Global 1.6120 m versus LF-only 2.2323 m; zonal Rule 1.6122 m is comparable to Global. Burnett 30-fold event LOOCV at B=4: mean Global RMSE 1.7479 m vs Rule 1.8260 m (mean Delta RMSE -0.0781 m; 6/30 folds zonal better; significant=false).

## 4. Discussion

Carlisle (max-surface EOI = 0.057 LOW; B=4: 34.2% RMSE reduction, 9/9 LOOCV folds) shows zoning can help under equal B even when max-surface EOI is low. Burnett EOI = 0.957 yet Rule does not beat Global on 30-fold LOOCV. Burnett 30-fold event LOOCV at B=4: mean Global RMSE 1.7479 m vs Rule 1.8260 m (mean Delta RMSE -0.0781 m; 6/30 folds zonal better; significant=false). ZGG>0 with oracle EOF DeltaRMSE<0 rules out pure HF-EOF truncation. Stage-swap LOOCV means GG/ZZ/GZ/ZG ≈ 0.180/0.098/0.098/0.101 m: zone structure via EOF coordinates or mapping locality recovers nearly the ZZ gain; not a unique GP-only localization. Chowilla shows LSG can degrade when LF is a poor match to HF.

SI: historical temporal EOI (0.51) is a different protocol and is excluded from main claims.
Limitations: LSG-Max only; sklearn GPR (gpflow not used); Chowilla archive MD5 not re-verified; Brisbane not run; Burnett KMeans LOOCV skipped (not cheap vs Rule).

## 5. Conclusions

1. EOF reduction is not hydrodynamically neutral on Carlisle at equal B=4 (34.2% RMSE reduction; 9/9 LOOCV folds).
2. Zonal capacity control is more robust than inflating Global B (Global 0.1464 → 0.3527; Rule 0.0964 → 0.1790).
3. The benefit is case-dependent: Chowilla LSG degrades; Burnett 30-fold event LOOCV does not support zonal over Global (zonal better in a minority of folds; mean Delta RMSE not positive).
4. Official 2-fold bootstrap is not significant; do not over-claim it.

Data: Fraehr (2024), Figshare 24312658. Code: repository root (path-independent). Registry: `outputs/registry/`. Canonical generator: `scripts/95_final_submission_report.py`.
