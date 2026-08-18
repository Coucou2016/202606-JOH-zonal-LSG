# R15 brief — fixes for your R14 findings (round 5)

**Repo:** https://github.com/Coucou2016/202606-JOH-zonal-LSG
**Commit under review:** `1c0e0b3` (latest master, pushed)
**Canonical figure↔code pack:** `paper/chatgpt/figure_code_audit_pack.md`
  → https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/paper/chatgpt/figure_code_audit_pack.md

This round closes every item you flagged in R14. Please re-verify each one and
then continue the same visual + code + prose sweep for anything still wrong.

---

## 1. Fixes made this round (R15)

1. **Figure 11 ghost zone-ID colorbar (fixed).** The rule-zoning merge step
   (`lsg/zoning.py → merge_zones_to_budget`) could leave non-contiguous zone IDs
   (e.g. {0,1,2,4}) after merging away a zone, so the colourbar rendered 5 ticks
   for 4 real zones. The function now remaps active IDs to a contiguous
   `0..K-1` range. All four cases (`carlisle` Run2/Run1, `burnettrv`, `chowilla`)
   now report `n_zones = 4`, and the colourbar shows exactly the active zones.

2. **Figure 12 0.001 m RMSE drift (fixed).** The obs-vs-pred scatter titles now
   quote the **canonical LOOCV RMSE** read from `outputs/evaluation/<case>/loocv_results.json`
   (new helper `_canonical_loocv_rmse` in `scripts/97b_spatial_maps.py`), so the
   title is byte-identical to the prose. Carlisle Run2 now shows
   Global 0.695 m / Rule 0.167 m. (Chowilla has no canonical B=4 LOOCV record,
   so it falls back to the freshly refit metric and is labelled accordingly.)

3. **Caption caveats added** in `paper/manuscript.md`:
   - Fig 3 and Fig 4: "As in Figure 2, the nominal B=8 global point realized seven modes."
   - Fig 7: "95% bootstrap confidence intervals …".
   - Fig 8: "… common depth scale capped at the pooled 99th percentile of wet-cell depth for display."
   - Fig 10: "… colour limits are symmetric and capped at the 98th percentile of wet-cell absolute residual magnitude."
   - Fig 17: "The factor-1 point is an independently refitted uncoarsened baseline."

4. **Audit pack commit hash** bumped `bbdb46d → e8d012a` (and the pack is
   committed in `1c0e0b3`).

5. Regenerated the affected spatial maps and the full Chinese report
   (`完整研究报告.html/.pdf`); re-ran the data audit → **54/54 PASS**.

---

## 2. What to re-verify (specific)

- **Fig 11** (`figA4_zones_overlay_carlisle_ev1.png`): confirm the colourbar now
  shows exactly the active zones (4) with integer ticks, no ghost entry.
- **Fig 12** (`figA5_obs_vs_pred_carlisle_ev1.png`): confirm the titles read the
  canonical 0.695 m / 0.167 m and no longer drift by 0.001 m.
- **Fig 3 / 4 captions**: confirm the "seven modes" caveat reads naturally and
  matches Figure 2.
- **Fig 8 / 10 captions**: confirm the percentile wording matches what the code
  actually does (Fig 8 `depth_vmax(q=99.0)`; Fig 10 `np.percentile(..., 98)`).

---

## 3. Continue the sweep

Beyond the items above, please scan all 17 figures + manuscript prose once more
for any remaining issue in the four classes (internal consistency, visual
quality, code correctness, statistical presentation). We still want a definite
verdict on the three questions left open from R14 (Fig 7 CI honesty, Fig 14
Carlisle-bar visibility, Fig 16 "EOI does not rank" clarity), plus anything new.

---

## 4. Data integrity

All numbers remain machine-audited (`scripts/100_manuscript_data_audit.py` →
54/54 PASS). Burnett corrected matched-capacity values are unchanged: mean
Global 1.7192 m, Rule 1.8164 m, Δ −0.0972 m, 13/30 folds, 12-event Global
1.6117 m.

---

## 5. What to return

A numbered list of concrete findings (manuscript figure number + PNG file +
issue class + one-line fix suggestion). Focus on what is wrong or ambiguous; no
need to restate what is now correct.
