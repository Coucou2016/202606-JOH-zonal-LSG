# R13 brief — repo-wide Burnett number sync (Round 3 consistency re-audit)

**Repo:** https://github.com/Coucou2016/202606-JOH-zonal-LSG
**Commit under review:** `69e0342` (Sync Burnett numbers across reports, registry, tables, audit)
**Manuscript:** https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/paper/manuscript.md

R12 reported the corrected Burnett numbers and regenerated the figures. This round
(R13) is the *other* half of the dual-line audit: we swept every non-archive
deliverable in the repo and confirmed the R12 numbers are now propagated
everywhere — and we fixed three half-updated spots that still mixed the new mean
with the old fold count.

---

## 1. What this round fixed

R12 changed the Burnett 30-fold numbers to:

| Quantity | R12 value |
|---|---:|
| mean Global RMSE | 1.7192 m |
| mean Rule RMSE | 1.8164 m |
| mean ΔRMSE (Global − zonal) | −0.0972 m |
| folds favouring Rule | 13 / 30 |
| 12-event Global | 1.6117 m |

Those were applied to `manuscript.md` and the figures, but a repo-wide sweep
found the *old* numbers (1.7479 / 1.8260 / 1.6120 / 6/30) still living in:

- the two Chinese reports (`完整研究报告.*` from `scripts/99_full_report_zh.py`,
  `研究报告.*` from `scripts/96_research_report_zh.py`);
- the deep figure-explanation library `scripts/_deep_fig_zh.py`;
- the registry `outputs/registry/result_manifest_v4.csv`;
- the generated tables `outputs/tables/table03_main_results.csv`,
  `table04_ablation.csv`;
- the audit document `paper/REVIEW_AUDIT.md`;
- the English short report `report.md`.

## 2. The subtle bug worth a second pair of eyes

Three spots in `scripts/_deep_fig_zh.py` / `scripts/96_research_report_zh.py`
were **half-updated**: they showed the new mean (−0.0972 m) *next to* the old
`6/30` fold count (e.g. "mean ΔRMSE −0.0972 m, only 6/30 folds better"). This is
exactly the kind of inconsistency that is easy to miss because each field in
isolation looks plausible. We replaced all of them with a dynamic
`{n_improved}/{n_folds}` so the two fields can never drift again.

**Ask:** please do the same sweep from your side — search the repo (excluding the
`paper/manuscript_v1.0rc_*.md` archives, `paper/chatgpt/*` logs, and
`outputs/evaluation/burnettrv/_backup_*/`) for any remaining `1.7479`, `1.8260`,
`1.6120`, `-0.0781`, or `6/30` next to a *new* value, and flag any you find.

## 3. Confirm the two reports agree with the manuscript

The regenerated `完整研究报告.md` (comprehensive Chinese) and `report.md`
(English short) should now state, for Burnett 30-fold `B=4`:

> mean Global RMSE 1.7192 m vs Rule 1.8164 m; mean ΔRMSE −0.0972 m; 13/30 folds
> favour Rule; 95% CI [−0.2249, +0.0014]; significant = false.

and for the 12-event fixed split: Global 1.6117 m vs Rule 1.6122 m.

Please confirm these match `paper/manuscript.md` §4.3 and Table 2 exactly.

## 4. Figure review from R12 still stands

The figures themselves did not change this round (they were already regenerated
in R12). The R12 figure-review asks (§5 of `R12_modebudget_fix.md`) remain open
— in particular the visual check of Fig 7 / 13 / 14 (new Burnett numbers) and
Fig 15 / 16 (EOI with no threshold lines). If you are able to open the PNGs,
they live at:

`https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/<name>.png`

## 5. What to return

1. Any remaining old-number/next-to-new inconsistency you can find (file + line).
2. Any place where the three reports disagree on a Burnett number.
3. A short confirmation (or list of issues) on the R12 figure-review points.
