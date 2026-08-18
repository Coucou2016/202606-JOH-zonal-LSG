# R21 brief — closing your 4 R20 findings (round 11)

**Repo:** https://github.com/Coucou2016/202606-JOH-zonal-LSG
**Figure/data baseline:** `60b2e18` (figures + numbers unchanged since R19)
**R21 core-revision commit:** `e608559` (manuscript + eoi.py + audit-pack body)
**Canonical figure↔code pack:** `paper/chatgpt/figure_code_audit_pack.md`
  → https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/6462f90/paper/chatgpt/figure_code_audit_pack.md

All four items from your R20 reply are addressed below. No EOI value or figure
changed — every change is wording / provenance only.

---

## #1 provenance header field split (your #1)

`figure_code_audit_pack.md` header now separates the version chain into four
distinct fields:

```
Figure/data baseline: 60b2e18
Manuscript revision:  e608559
Audit-pack revision:  e608559
Manuscript: (pinned to e608559)
```

This removes the earlier conflation of the figure baseline with the current
text revision.

## #2 Figure 7 caption lead-in (your #2)

The caption now opens with the neutral "95% bootstrap intervals for the mean
paired ΔRMSE …", then names the Carlisle/Burnett LOOCV rows "fold-bootstrap
confidence intervals (nine, nine, and thirty folds, respectively)" and the
official 2-fold row "a descriptive event-level interval bootstrapped over its
four held-out events (two per fold)". The self-conflicting "confidence
intervals … do not provide an independent-sample confidence interval" phrasing
is gone.

## #3 eoi.py top docstring (your #3)

The module docstring now spells out the two-step definition verbatim matching
Methods §2.4:

```
for a chosen event set S define the event-averaged absolute residual
r̄ᵢ(S) = mean_e |LF_e,i − HF_e,i|; then
EOI = Var_k(mean_{i∈zone k} r̄ᵢ(S)) / Var_i(r̄ᵢ(S)),
where the active mask is the set of cells that are wet in at least one HF event
of S (depth ≥ 0.03 m) AND exhibit non-zero across-event depth variation.
```

## #4 Figure 15 caption precision (your #4)

The Fig 15 caption (manuscript + audit pack) now reads "the ratio of the
unweighted variance across zone means of the event-averaged absolute-residual
field \( \bar{r}_i(S) \) to its spatial variance over active cells", replacing
the ambiguous "across-zone-mean residual variance / cellwise residual variance".

---

## Verification

- No EOI value or figure changed (Carlisle 0.057, Chowilla 0.116, Burnett 0.957
  unchanged; figures unchanged at baseline `60b2e18`).
- `tests/test_innovation.py` → 16/16 PASS.
- Regenerated `manuscript.html` / `manuscript.pdf` and both Chinese reports.
- `scripts/100_manuscript_data_audit.py` → 54/54 PASS.
- Manuscript backed up as `paper/manuscript_v1.0rc_R21after_20260819_0458.md`.

## What to return

Confirm whether the figure↔code audit has now closed, or give a new numbered
list of concrete findings (manuscript figure number + PNG file + issue class +
one-line fix).
