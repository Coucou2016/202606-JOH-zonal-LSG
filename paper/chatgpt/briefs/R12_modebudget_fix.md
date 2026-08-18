# R12 brief — mode-budget bug fix + Burnett regeneration (Round 2 figure/code re-audit)

**Repo:** https://github.com/Coucou2016/202606-JOH-zonal-LSG
**Commits under review:** `0f9dc22` (fix + regeneration), `b04a367` (docs)
**Manuscript:** https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/paper/manuscript.md

This round reports the fixes for the matched-capacity bug you flagged in the
previous audit, and asks you to re-review the affected figures and numbers.

---

## 1. What was fixed

Three code changes, all aimed at making the Global-vs-zonal comparison a *true
equal-capacity* comparison and making the GPR reproducible:

| # | File | Fix |
|---|---|---|
| 1 | `lsg/zoning.py` | New `merge_zones_to_budget()`: when rule-based zoning yields more zones than the mode budget `B`, the smallest zones are merged into the largest until `n_zones <= B`. |
| 2 | `lsg/zonal_eof.py` + `lsg/zonal_lsg.py` | Call the merge before zonal EOF fitting; assert `K <= mode_budget`. Previously, when `K > B`, the code silently allocated `[1]*K` modes, so the zonal model used **more** modes than Global (e.g. 5 vs 4) and the "improvement" was partly an unfair capacity advantage. |
| 3 | `lsg/gp.py` | Pin `random_state=42` on the sklearn `GaussianProcessRegressor` so the 3 optimizer restarts are deterministic. |
| 4 | `scripts/31_burnettrv_validation.py` | Force the Global fixed-split model to `B=4` (`force_n_modes=4`) so it matches the zonal budget (previously the Global fixed-split realized 3 modes). |

## 2. New Burnett numbers (before → after)

The Burnett case is where the bug was detected (rule zoning produced 5 zones
under `B=4`). Both Burnett protocols were regenerated.

**30-fold LOOCV (`B=4`):**

| Quantity | Before | After |
|---|---:|---:|
| mean Global RMSE | 1.7479 m | **1.7192 m** |
| mean Rule RMSE | 1.8260 m | **1.8164 m** |
| mean ΔRMSE (Global − zonal) | −0.0781 m | **−0.0972 m** |
| folds favouring Rule | 6 / 30 | **13 / 30** |
| 95% CI | [−0.2116, +0.0405] | **[−0.2249, +0.0014]** |
| significant | no | no (unchanged) |

**12-event fixed split (`B=4`):**

| Quantity | Before | After |
|---|---:|---:|
| LF-only | 2.2323 | 2.2323 |
| Global | 1.6120 | **1.6117** |
| Rule | 1.6122 | 1.6122 |

The conclusion is unchanged — **Burnett does not favour Rule zoning** — and the
effect is now slightly *more* negative (−0.0972 vs −0.0781). Note the
`improved` count moved 6 → 13 even though the mean moved more negative: more
folds are now marginally positive, while a smaller number of folds are more
clearly negative.

## 3. Carlisle robustness check (not regenerated, verified stable)

The mode-budget bug does **not** affect Carlisle because rule zoning there
already yields 4 zones under `B=4` (the primary result `budget_sweep_true_equal.json`
records `actual_modes=4` for Global/Rule/KMeans). To confirm the `random_state`
change did not shift Carlisle, the spatial-map script re-fitted the Run2 fold:

| Quantity | Before (loocv_results.json) | After (re-fit, seed=42) |
|---|---:|---:|
| Run2 Global RMSE | 0.6953 | 0.6945 |
| Run2 Rule RMSE | 0.1662 | 0.1662 |

Negligible (~0.1%). Carlisle numbers are therefore left as-is and remain the
paper's primary result (Global 0.1464 → Rule 0.0964 at `B=4`).

## 4. Figures regenerated

All 17 statistical figures (`scripts/97_scienceplots_figures.py`) and all 20
spatial maps (`scripts/97b_spatial_maps.py`) were regenerated. The data-bearing
figures whose values changed are:

- **Fig 7** (`fig12_stat_ci.png`) — Burnett CI now [−0.2249, +0.0014].
- **Fig 13** (`fig10_burnett_loocv.png`) — Burnett LOOCV scatter, new means.
- **Fig 14** (`fig04_three_case.png`) — Burnett Global 1.6117.

Style fixes already applied (from your earlier feedback) and now re-rendered:

- **Fig 1** (`fig01_workflow.png`) — Zonal workflow now lists "LF interpolate to
  HF grid" explicitly and combines "Zonal EOF + zonal GP mapping".
- **Fig 2 / 3** — annotated "7 modes realized" on the nominal `B=8` Global point.
- **Fig 15** (`fig14_eoi.png`) — removed the colour-coded bars and the 0.15/0.30
  reference lines (EOI is exploratory, not a calibrated threshold).
- **Fig 16** (`fig15_eoi_vs_delta.png`) — removed the vertical line at EOI=0.30.
- **Fig 11** (`figA4_zones_overlay_*.png`) — integer zone colourbar ticks,
  lighter contours.
- **Fig 12** (`figA5_obs_vs_pred_*.png`) — common x/y limits across panels;
  title now says "all-cell area-wtd RMSE".

## 5. What to re-review

Please re-check, visually + against the code:

1. **Fig 7 / 13 / 14** — do the new Burnett numbers plot correctly and match the
   prose in §4.3 and Table 2? Any sign/labelling issue with the negative ΔRMSE?
2. **Fig 15 / 16** — after removing the EOI thresholds, is the "EOI does not rank
   the cases" narrative visually clear without implying a decision boundary?
3. **Fig 2 / 3** — does the "7 modes realized" annotation sit correctly and not
   overlap other marks?
4. **Fig 1** — is the zonal workflow now accurate (implicit LF interpolation is
   shown for both Global and Zonal)?
5. **Burnett `improved 6→13` vs mean `−0.078→−0.097`** — is the prose in §4.3
   ("Rule improves thirteen of the 30 folds, and the paired difference is not
   significant") internally consistent with the CI and the mean?

## 6. Full figure-code correspondence

The figure-by-figure pack is unchanged from the previous round except for the
data values updated above:
`paper/chatgpt/figure_code_audit_pack.md` (regenerated figures live at
`https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/<name>.png`).
