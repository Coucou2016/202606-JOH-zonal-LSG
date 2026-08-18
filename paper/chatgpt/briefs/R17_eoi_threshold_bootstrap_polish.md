# R17 brief — closing your 8 R16 findings (round 7)

**Repo:** https://github.com/Coucou2016/202606-JOH-zonal-LSG
**Commit under review:** `bcf1fcb` (R17 figures + numbers; pushed)
**Canonical figure↔code pack:** `paper/chatgpt/figure_code_audit_pack.md`
  → https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/paper/chatgpt/figure_code_audit_pack.md

This round closes all eight items in your R16 reply, in the priority order you
gave (provenance → EOI threshold semantics → bootstrap Methods → the caption /
visual polish batch). Please re-verify each, then continue the full visual +
code + prose sweep for anything new.

---

## 1. Fixes made this round (R17)

1. **Provenance header (your #1).** `figure_code_audit_pack.md` now points at
   `bcf1fcb` — the *same commit* that contains the figures it describes. The
   pack header is shipped in the same commit as the figures.

2. **EOI threshold semantics (your #2).** `lsg/eoi.py` no longer defines
   `EOI_HIGH` / `EOI_MODERATE`, and `interpret_eoi()` is deleted. `compute_eoi`
   now returns `interpretation = "exploratory_diagnostic_no_threshold"`, and a
   comment states EOI is an exploratory diagnostic, never a decision switch.
   `scripts/40_compute_eoi.py` and `scripts/45_build_registry.py` no longer
   import or call `interpret_eoi`; `tests/test_innovation.py` asserts the new
   interpretation string. Re-ran the tests → **16/16 PASS**.

3. **Bootstrap Methods (your #3).** Methods §3.3 now defines all three bootstrap
   procedures: Carlisle 9-fold LOOCV (nine fold-level differences), Carlisle
   official 2-fold (four held-out event-level differences, two per fold), and
   Burnett 30-fold LOOCV (thirty fold-level differences) — all 10,000 replicates,
   seed 42, percentile CI.

4. **Fig 15 caption self-containment (your #4).** Caption now states EOI "is the
   ratio of the unweighted across-zone-mean residual variance to the cellwise
   residual variance and is not by construction bounded by [0,1]."

5. **Fig 12 sample spec (your #5).** Caption now reads "a seed-42 random subsample
   of the HF wet cells (depth ≥ 0.03 m, at most 40,000)."

6. **Fig 4 caption completeness (your #6).** Caption now reads "area-weighted
   (a) MAE and (b) bias versus retained-mode budget."

7. **Fig 7 visual (your #7).** `fig12_stat_ci.png` value labels are now offset
   *above* the marker (`va="bottom"`, y-offset) so the grey `mean [lo, hi]` text
   no longer sits on the error bars / whiskers.

8. **Fig 10 sign semantics (your #8).** Caption now states panel (c) is
   `|G−HF| − |R−HF|`, "where positive values indicate that the Rule absolute
   error is smaller."

9. **Rebuild + audit.** Regenerated `97_scienceplots_figures.py`, rebuilt
   `manuscript.html/.pdf` and both Chinese reports (`完整研究报告`, `研究报告`),
   recomputed EOI tables (`eoi_all.json`, `residual_organization.csv`), and
   re-ran `scripts/100_manuscript_data_audit.py` → **54/54 PASS**.

---

## 2. What to re-verify (specific)

- **Fig 7** (`fig12_stat_ci.png`): confirm the four `mean [lo, hi]` labels are
  offset above their markers and no longer overlap the whiskers (Carlisle B=4 and
  Burnett rows especially).
- **`lsg/eoi.py`**: confirm `EOI_HIGH`/`EOI_MODERATE`/`interpret_eoi` are gone
  and no other module imports them.
- **Methods §3.3**: confirm the Burnett 30-fold and official 2-fold bootstrap
  definitions now read correctly alongside the Carlisle one.
- **Fig 15 / Fig 12 / Fig 4 / Fig 10 captions**: confirm the new wording matches
  the code behaviour exactly.
- **`figure_code_audit_pack.md`**: confirm the header commit is `bcf1fcb` and
  matches the pushed HEAD.

---

## 3. Continue the sweep

Scan all 17 figures + manuscript prose once more for any remaining issue in the
four classes (internal consistency, visual quality, code correctness, statistical
presentation). We welcome a definite verdict on any residual ambiguity, and any
new finding you notice — especially anything where a figure still does not match
its caption or the numbers quoted in the text.

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
