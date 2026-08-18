# R15 reply — plain-ChatGPT review (JOH project, master@5c137ac)

Verified against the actual 17 figures + code + audit pack + manuscript.

## Confirmed fixed (this round)
- Fig 11 zone-ID colorbar now shows exactly zones {0,1,2,3}.
- Fig 12 title reads canonical LOOCV: Global 0.695 m / Rule 0.167 m.
- Fig 3/4/7/8/10/17 caveats written into manuscript.
- Burnett numbers consistent: Global 1.7192, Rule 1.8164, Δ −0.0972, 13/30, CI upper +0.00142 m.

## Verdicts on the three open questions
- Fig 7: numerically honest, but Burnett CI "slightly crosses 0" is visually invisible.
- Fig 14: Carlisle gain is swamped by Chowilla/Burnett large bars.
- Fig 16: removing EOI threshold lines is fine; message still clear.

## Remaining findings (by priority)
1. **[HIGH] Fig 15 (fig14_eoi.png) — code correctness + stats.** EOI numerator is
   `np.var(zone_means)` (equal-weight across zone means), denominator is cellwise
   residual variance. Not a cell-count-weighted between-group variance fraction,
   so not bounded to [0,1], yet the plot hard-codes `ylim(0, 1.05)`. Fix: either
   document "unweighted variance across active-zone means" and drop the 0–1.05
   limit, OR switch numerator to cell-count-weighted between-zone variance and
   re-audit EOI values.
2. **[HIGH] Fig 7 (fig12_stat_ci.png) — stats + visual.** Burnett CI
   [−0.2249, +0.0014] m: the right cap sits almost on the grey zero line, easy to
   misread as "upper bound = 0". Fix: annotate the Burnett row with the CI text,
   or add a local zero inset.
3. **[MID-HIGH] Fig 7 — stats.** "Carlisle official 2-fold" is actually 2 folds /
   4 held-out events. Clarify in Methods/caption the bootstrap resampling unit.
4. **[MID-HIGH] Fig 12 (figA5_obs_vs_pred_carlisle_ev1.png) — consistency.** Points
   are a seed-42 subsample of ≤40k HF-wet cells, but the title RMSE is canonical
   all-cell area-weighted. Caption must state the subsample and that title RMSE is
   not computed from the displayed subset.
5. **[MID-HIGH] Fig 14 (fig04_three_case.png) — visual.** Carlisle bars
   (0.1602/0.1464/0.0964 m) sit at the bottom of a 2.6 m axis. Fix: add 3–4-digit
   value labels + a Carlisle inset (preferred over broken axis).
6. **[MID] Fig 17 (fig17_lf_degradation.png) — provenance.** Whole sensitivity uses
   random 7/2 split (seed 42); caption should say so.
7. **[MID] Fig 5 & 13 — visual + stats.** Lines connect independent held-out event
   indices, implying a false "trajectory". Fix: markers only, or Global–Rule paired
   dumbbells.
8. **[LOW] Fig 11 (figA4_zones_overlay) — visual.** Left panel full coords
   (339000), right panel scientific offset (3.39e5). Unify ticklabel_format.
9. **[LOW] Fig 4 (fig13_mae_bias.png) — consistency.** No (a)/(b) tags; KMeans vs
   "KMeans zonal" terminology drift. Add (a) MAE / (b) bias tags.
10. **[NON-FIG] audit pack provenance.** Header still "Commit under review:
    e8d012a". Suggest "Audit conducted at 5c137ac; figure/number baseline
    e8d012a, incorporated via 1c0e0b3".

## Top-4 to fix before submission (most likely JoH reviewer flags)
1. EOI definition/axis
2. Fig 7 Burnett CI
3. Fig 12 scatter-vs-RMSE wording
4. Fig 14 scale
