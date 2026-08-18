# R14 brief — figure↔code dual-line review (round 4)

**Repo:** https://github.com/Coucou2016/202606-JOH-zonal-LSG
**Commit under review:** `4cca918` (latest master)
**Canonical figure↔code pack:** `paper/chatgpt/figure_code_audit_pack.md`
  → https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/paper/chatgpt/figure_code_audit_pack.md

This round asks you to do a **visual review of the figures** together with a
**code review of the generating scripts**, and to check both against the
manuscript prose. Everything is on GitHub at stable raw URLs, so you can open
each image directly.

---

## 1. How to read the figures

The manuscript numbers figures 1…17, but the PNG files keep their pre-renumbering
names, so **manuscript figure number ≠ file name**. The mapping (also in the audit
pack) is:

| Manuscript | PNG | Manuscript | PNG |
|---|---|---|---|
| Fig 1 | `fig01_workflow.png` | Fig 10 | `figA3_residuals_carlisle_ev1.png` |
| Fig 2 | `fig03_mode_budget.png` | Fig 11 | `figA4_zones_overlay_carlisle_ev1.png` |
| Fig 3 | `fig09_csi_budget.png` | Fig 12 | `figA5_obs_vs_pred_carlisle_ev1.png` |
| Fig 4 | `fig13_mae_bias.png` | Fig 13 | `fig10_burnett_loocv.png` |
| Fig 5 | `fig08_per_event_bootstrap.png` | Fig 14 | `fig04_three_case.png` |
| Fig 6 | `fig11_loocv_scatter.png` | Fig 15 | `fig14_eoi.png` |
| Fig 7 | `fig12_stat_ci.png` | Fig 16 | `fig15_eoi_vs_delta.png` |
| Fig 8 | `figA1_inundation_maps_carlisle_ev1.png` | Fig 17 | `fig17_lf_degradation.png` |
| Fig 9 | `figA2_csi_hitmiss_carlisle_ev1.png` | | |

Raw URL pattern (works in a browser / for your image fetch):
`https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/<name>.png`

Generating code:
- statistical figures → `scripts/97_scienceplots_figures.py`
- spatial maps → `scripts/97b_spatial_maps.py`

---

## 2. What changed this round (R14)

1. The audit pack was stale in two ways and is now fixed:
   - the commit hash is updated to `4cca918`;
   - the Figure 1 code block now matches the actual code (the zonal workflow
     correctly lists "LF interpolate to HF grid" as step 1 and combines
     "Zonal EOF + zonal GP mapping" into one step).
2. Added a manuscript↔PNG mapping table (above) and exact line references for
   the five spatial-map functions (`fig_inundation` 297–326, `fig_csi_spatial`
   338–377, `fig_residuals` 388–422, `fig_zones_overlay` 432–489,
   `fig_obs_pred_scatter` 494–530).
3. `fig03_mode_budget.png` and `fig09_csi_budget.png`: the "7 modes realized"
   annotation at the nominal B=8 Global point was tight against the top of the
   axes and could clip; we added explicit y-axis headroom.

---

## 3. What to review (please, visual + code + prose)

For **each of the 17 figures**, report any of these four classes of issue:

1. **Internal consistency** — does the image match its caption and the numbers
   quoted in `paper/manuscript.md`?
2. **Visual quality** — overlapping legend/text, clipped annotations, misleading
   axes or truncated labels, colour inconsistency between figures, panel layout.
3. **Code correctness** — does the code actually plot what the caption claims?
   Any sign / unit / indexing error?
4. **Statistical presentation** — are 1:1 lines, error bars, baselines, and
   colour mappings drawn correctly?

We are specifically still unsure about (please give a definite verdict):

- **Fig 7** (`fig12_stat_ci.png`): the Burnett 30-fold CI [−0.2249, +0.0014] has
  an upper bound that barely touches zero — is the error bar rendered so that it
  is honest (i.e. visibly crosses or touches zero) without implying significance?
- **Fig 14** (`fig04_three_case.png`): the Chowilla/Burnett bars (~2.5 / ~2.2 m)
  dwarf the Carlisle bars (~0.16 m), so the Carlisle "Global 0.1464 → Rule
  0.0964" improvement is nearly invisible. Is this acceptable, or should we add
  a broken axis / log scale / inset for Carlisle? We currently explain it in
  prose but have not changed the figure.
- **Fig 16** (`fig15_eoi_vs_delta.png`): after removing the EOI threshold line,
  is the "EOI does not rank the cases" message still visually clear, or does the
  figure now look unfinished?

---

## 4. Data integrity note

All numbers are machine-audited (`scripts/100_manuscript_data_audit.py` → 54/54
PASS) and traced in `paper/REVIEW_AUDIT.md` and `paper/DATA_PROVENANCE.md`. The
Burnett values are the corrected matched-capacity ones (mean Global 1.7192 m,
Rule 1.8164 m, Δ −0.0972 m, 13/30 folds, 12-event Global 1.6117 m). Please flag
any figure or prose that still shows a stale Burnett value.

---

## 5. What to return

A numbered list of concrete findings, each with:
- the manuscript figure number (and PNG file),
- the issue class (1–4 above),
- a one-line fix suggestion (we prefer small, non-structural edits).

No need to restate what is already correct — focus on what is wrong or
ambiguous.
