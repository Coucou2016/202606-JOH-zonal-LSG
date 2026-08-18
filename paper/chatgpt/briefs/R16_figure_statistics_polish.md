# R16 brief — statistics & figure-polish fixes for your R15 findings (round 6)

**Repo:** https://github.com/Coucou2016/202606-JOH-zonal-LSG
**Commit under review:** `<R16_COMMIT>` (latest master, pushed)
**Canonical figure↔code pack:** `paper/chatgpt/figure_code_audit_pack.md`
  → https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/paper/chatgpt/figure_code_audit_pack.md

This round closes every item you flagged in your R15 reply (the EOI definition,
the Burnett CI annotation, the caption bootstrap units, the Fig 14 Carlisle
visibility, the Fig 5/13 line-plot misleading continuity, and the coordinate /
terminology nits). Please re-verify each one, then continue the full visual +
code + prose sweep.

---

## 1. Fixes made this round (R16)

1. **Fig 15 — EOI definition & axis (your #1 priority).** The Methods text now
   states explicitly that the EOI numerator is the **unweighted variance across
   active-zone means** ("each zone is weighted equally regardless of its cell
   count"), and that EOI is *not by construction confined to the unit interval*.
   The plot (`fig14_eoi.png`) no longer hard-codes `ylim(0, 1.05)`; the upper
   limit is now data-driven, and each bar carries its value label (Carlisle
   0.057, Burnett 0.957, Chowilla 0.116). The `lsg/eoi.py` docstring documents
   the same unweighted definition.

2. **Fig 7 — Burnett CI now visually honest.** Each row in `fig12_stat_ci.png`
   now carries an explicit `mean [+lo, +hi]` text label next to the marker, and
   the x-axis is symmetric about zero so the Burnett interval `[-0.225, +0.001]`
   crossing zero is unmistakable.

3. **Fig 7 caption — bootstrap units stated.** The caption now says the Carlisle
   B=4/B=6 LOOCV intervals and the Burnett interval are bootstrapped over folds
   (nine, nine, thirty) while the Carlisle official 2-fold interval is
   bootstrapped over its four held-out events (two per fold).

4. **Fig 12 caption — subsample vs canonical RMSE.** The caption now states the
   scatter points are a seed-42 subsample (≤ 40 000 wet cells) while the RMSE in
   each panel title is the canonical LOOCV all-cell area-weighted value, not a
   statistic of the displayed subsample.

5. **Fig 14 — Carlisle no longer swamped.** `fig04_three_case.png` now adds a
   value label to every bar and a magnified Carlisle inset (upper-left) so the
   Global 0.146 vs Rule 0.096 separation is visible at full scale. The legend
   moved to the bottom to make room.

6. **Fig 17 caption — split documented.** Now reads "… evaluated on the random
   7/2 train-test split (seed 42)."

7. **Fig 5 & Fig 13 — lines → paired dumbbells.** `fig08_per_event_bootstrap.png`
   and `fig10_burnett_loocv.png` no longer draw connecting lines across held-out
   event indices (events are unordered; the polyline implied a false ordering).
   Each event now shows a Global↔Rule vertical stem plus two markers, making the
   per-event zonal-vs-global direction readable at a glance.

8. **Fig 11 — coordinate format unified.** The zone panel of
   `figA4_zones_overlay_*.png` now uses the same scientific tick format as every
   other spatial map (`ticklabel_format(style="sci", …)`).

9. **Fig 4 — panel tags + KMeans terminology.** `fig13_mae_bias.png` now labels
   its two panels (a) and (b), and the legend reads "KMeans zonal" (matching
   "Rule zonal"). The same "KMeans zonal" wording was applied to the runtime
   figure (`fig08_runtime.png`) for consistency.

10. **Rebuild + audit.** Regenerated all statistical figures
    (`97_scienceplots_figures.py`) and all spatial maps (`97b_spatial_maps.py`),
    rebuilt `manuscript.html/.pdf` and the Chinese reports
    (`完整研究报告.html/.pdf`, `研究报告.html/.pdf`), and re-ran the data audit →
    **54/54 PASS**. Manuscript backed up as
    `paper/manuscript_v1.0rc_R16after_20260819_0305.md`.

---

## 2. What to re-verify (specific)

- **Fig 15** (`fig14_eoi.png`): confirm the y-axis is no longer forced to 1.05,
  the value labels are correct, and the Methods wording ("unweighted variance
  across active-zone means", "not by construction confined to the unit
  interval") is internally consistent with the code in `lsg/eoi.py`.
- **Fig 7** (`fig12_stat_ci.png`): confirm the four `mean [lo, hi]` labels are
  legible and the Burnett `[-0.225, +0.001]` interval reads correctly.
- **Fig 14** (`fig04_three_case.png`): confirm the inset doesn't overlap the
  main bars and the value labels are readable.
- **Fig 5 / Fig 13** (`fig08_per_event_bootstrap.png`, `fig10_burnett_loocv.png`):
  confirm the dumbbell form reads clearly and the legend is correct.
- **Fig 4 / Fig 8-runtime**: confirm "(a)/(b)" tags and "KMeans zonal" labels.
- **Fig 11 / Fig 12 / Fig 17 captions**: confirm the new caption wording matches
  the code behaviour exactly.

---

## 3. Continue the sweep

Beyond the above, scan all 17 figures + manuscript prose once more for any
remaining issue in the four classes (internal consistency, visual quality, code
correctness, statistical presentation). We still welcome a definite verdict on
any residual ambiguity (EOI interpretation, EOI-vs-ΔRMSE Fig 16 framing, or
anything new you notice).

---

## 4. Data integrity

All numbers remain machine-audited (`scripts/100_manuscript_data_audit.py` →
54/54 PASS). Burnett corrected matched-capacity values unchanged: mean Global
1.7192 m, Rule 1.8164 m, Δ −0.0972 m, 13/30 folds, 12-event Global 1.6117 m.

---

## 5. What to return

A numbered list of concrete findings (manuscript figure number + PNG file +
issue class + one-line fix suggestion). Focus on what is wrong or ambiguous; no
need to restate what is now correct.
