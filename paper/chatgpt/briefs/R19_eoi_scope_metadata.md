# R19 brief — closing your 5 R18 findings (round 9)

**Repo:** https://github.com/Coucou2016/202606-JOH-zonal-LSG
**Figure/manuscript baseline (figures + numbers):** `60b2e18` (pushed)
**Audit-pack revision:** `4dd8800` (this brief's commit; pack links pin to `60b2e18`)
**Canonical figure↔code pack:** `paper/chatgpt/figure_code_audit_pack.md`
  → https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/4dd8800/paper/chatgpt/figure_code_audit_pack.md

> Note on the version-chain fix you asked for (#1 last round): I now separate
> **figure/manuscript baseline = `60b2e18`** from **audit-pack revision = this
> commit**. The pack's internal links all pin to `60b2e18` (not `/master/`), and
> the manuscript link in the brief pins to `60b2e18`. The previous R18 brief
> mis-pinned the pack/manuscript links to `9e5887d` (where the rebuilt pack did
> not yet exist and the brief itself 404'd) — that is corrected here.

---

## 1. Methods §2.4 now defines EOI over a general event set (#2)

§2.4 no longer calls EOI a "training-data diagnostic". It now reads (verbatim):

- "an error-organization index (EOI) measures how strongly the magnitude of the
  LF-HF residual varies between zones **for a chosen set of events**" (the word
  "training" is gone from the definition sentence);
- the denominator is "the variance of cellwise absolute residuals over the wet
  mask **of the same event set**";
- it ends "EOI is an exploratory diagnostic … It is evaluated in two ways: as a
  retrospective pooled descriptor over all available events for each case
  (Figure 15), and as a strictly train-only value on each leave-one-out training
  fold (Figure 16)."

## 2. Code metadata: `n_events_used` + `scope` (#3)

`lsg/eoi.py`:
- the file-level docstring is now a neutral "residual-organisation diagnostic"
  (the word "training-data" was removed);
- `eoi_from_max_surfaces()` now writes `n_events_used` (was `n_train_events`) and
  a new `scope` field — `"train_only"` when `event_index` is given, otherwise
  `"all_event_pooled"`.
- `eoi_all.json` was regenerated, so the pooled bars now carry
  `scope="all_event_pooled"` and each per-fold record carries `scope="train_only"`.
- `tests/test_innovation.py` updated to assert the new fields (16/16 pass).

## 3. Chowilla cross-pool caveat in §4.4 (#4)

§4.4 now states "This cross-case comparison is descriptive rather than
protocol-matched: the Chowilla pooled EOI uses all 29 available events, whereas
its performance comparison (Figure 14, Table 2) uses the 12-event fixed subset."

## 4. Official 2-fold interval labelled descriptive (#5)

Both §3.3 and the Fig 7 caption now state that the Carlisle official 2-fold
interval is a **descriptive event-level bootstrap** over four held-out events
(two per fold) "which share each fitted fold model and therefore do not provide
an independent-sample confidence interval." The three LOOCV intervals remain
described as fold-level bootstrap confidence intervals.

## 5. Rebuild + audit

Regenerated `97_scienceplots_figures.py`, `40_compute_eoi.py` (new metadata),
rebuilt `manuscript.html/.pdf` and both Chinese reports, re-ran
`scripts/100_manuscript_data_audit.py` → **54/54 PASS**. The audit pack was
rebuilt with every link pinned to `60b2e18`, the Fig 7 caption updated, and the
Fig 15 metadata note added. Manuscript backed up as
`paper/manuscript_v1.0rc_R18after_20260819_0400.md`.

---

## What to re-verify (specific)

- **§2.4**: confirm the "chosen set of events" wording replaced "training", and
  the two-way (pooled vs train-only) evaluation sentence is present.
- **`lsg/eoi.py`**: confirm `n_events_used` + `scope` are present and the
  docstring no longer says "training-data".
- **`eoi_all.json`**: confirm pooled records carry `scope="all_event_pooled"` and
  per-fold records `scope="train_only"`.
- **§4.4** Chowilla sentence and **Fig 7 / §3.3** official-2-fold wording.
- **`figure_code_audit_pack.md`**: confirm every link pins to `60b2e18`, and the
  header separates baseline `60b2e18` from pack revision.

## What to return

A numbered list of concrete findings (manuscript figure number + PNG file +
issue class + one-line fix suggestion). Focus on what is wrong or ambiguous; no
need to restate what is now correct.
