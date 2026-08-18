# R20 brief — closing your 6 R19 findings (round 10)

**Repo:** https://github.com/Coucou2016/202606-JOH-zonal-LSG
**Figure/manuscript baseline (figures + numbers):** `60b2e18` (unchanged — no figure or
value changed this round)
**R20 core-revision commit:** `d866f79`
**Canonical figure↔code pack:** `paper/chatgpt/figure_code_audit_pack.md`
  → https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/d866f79/paper/chatgpt/figure_code_audit_pack.md

All six items from your R19 reply are addressed below. None requires recomputing
EOI or any figure — every change is wording / definition / provenance only.

---

## #1 provenance / audit-pack internal consistency (your #1)

- R19 brief canonical pack URL re-pinned to `4dd8800` (where the pack actually
  lived at that time), header now reads `Audit-pack revision: 4dd8800`.
- `figure_code_audit_pack.md` header now separates **Figure/manuscript baseline:
  `60b2e18`** from **Audit-pack revision: `4dd8800`**; the stale "all links …
  pinned to 9e5887d" line is corrected to `60b2e18`.
- Fig 8 caption gained "capped at the pooled 99th percentile of wet-cell depth
  for display".
- Fig 17 caption gained "The factor-1 point is an independently refitted
  uncoarsened baseline."

## #2 EOI definition precision (your #2)

Methods §2.4 now first defines the event-averaged absolute residual

\[
\bar{r}_i(S) = \frac{1}{|S|}\sum_{e \in S} |h_{\mathrm{LF},e,i} - h_{\mathrm{HF},e,i}|,
\]

and then writes \( \mathrm{EOI} = \mathrm{Var}_k(\bar{r}_k) / \mathrm{Var}_i(\bar{r}_i) \),
so the pooled cell-event variance ambiguity is removed.

## #3 wet-mask scope (your #3)

§2.4 now defines the active mask explicitly as "the cells that are wet in at
least one HF event of \(S\) and exhibit non-zero across-event depth variation."

## #4 eoi.py docstring (your #4)

`lsg/eoi.py` line 3 now reads "on the active wet mask of the chosen event set
(all events pooled, or a train-only subset)."

## #5 terminology (your #5)

"four-class hydrodynamic partition" was replaced by "residual-free hydrodynamic
rule with up to four active classes (empty classes are omitted)" across
`manuscript.md` (§2.4, Fig 15/16 captions), `lsg/eoi.py`, and the audit pack.

## #6 official two-fold wording (your #6)

§4.2, §5.1, and the Conclusion now say "descriptive event-level bootstrap
interval includes zero" instead of "confidence interval includes zero"; §4.2
also changed the bare "95% interval" to "95% descriptive event-level bootstrap
interval."

---

## Verification

- No EOI value or figure changed (numbers remain Carlisle 0.057, Chowilla 0.116,
  Burnett 0.957; figures unchanged at baseline `60b2e18`).
- `tests/test_innovation.py` → 16/16 PASS.
- Regenerated `manuscript.html` / `manuscript.pdf` and both Chinese reports.
- `scripts/100_manuscript_data_audit.py` → 54/54 PASS.
- Manuscript backed up as `paper/manuscript_v1.0rc_R20after_20260819_0442.md`.

## What to re-verify

- §2.4: the \( \bar{r}_i(S) \) definition precedes the EOI formula, and the
  active-mask sentence (wet + non-zero across-event variation) is present.
- The phrase "four-class hydrodynamic partition" is fully gone from manuscript,
  `eoi.py`, and the audit pack.
- The three "descriptive event-level bootstrap interval includes zero" sites
  (§4.2 / §5.1 / Conclusion) are consistent.
- `figure_code_audit_pack.md` header separates baseline `60b2e18` from pack
  revision, with Fig 8/17 captions matching the manuscript.

## What to return

A numbered list of concrete findings (manuscript figure number + PNG file +
issue class + one-line fix). Focus on what is still wrong or ambiguous.
