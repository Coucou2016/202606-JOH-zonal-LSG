# R18 brief — closing your 5 R17 findings (round 8)

**Repo:** https://github.com/Coucou2016/202606-JOH-zonal-LSG
**Commit under review:** `9e5887d` (R18 figures + numbers; pushed)
**Canonical figure↔code pack (rebuilt this round):** `paper/chatgpt/figure_code_audit_pack.md`
  → https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/9e5887d/paper/chatgpt/figure_code_audit_pack.md

This round closes all five findings in your R17 reply. For #1 and #2 I made an
explicit scientific decision — **clarify, not recompute** — and I explain why
below, because it affects how you should verify them.

---

## 1. The two EOI scope issues (#1 partition, #2 pooled scope) — resolved by clarification

Your R17 #1 said the EOI is computed on a different zone partition than the
production Rule LSG, and #2 said the pooled EOI is not strictly a training-data
diagnostic. Both are factually correct, and I have addressed them by **making the
definitions explicit** rather than by recomputing, for a deliberate reason:

- **Why not recompute EOI on the production (residual-override) partition:**
  the production Rule partition *adds a residual-error hotspot override* (zone 4,
  `lf_hf_abs_residual >= err_thr`) and then runs `merge_zones_to_budget()` at
  B=4. If EOI were computed on that partition, the zones themselves would be
  defined partly *by* the residual, which would trivially organise it — a
  circularity that would inflate EOI by construction. EOI's whole purpose is to
  ask "does the *hydrodynamic* partition align with the residual?", so the
  partition must be residual-free. This is now stated in three places:
  - **Methods §2.4** — "EOI uses the four-class hydrodynamic partition (maximum
    depth and inundation frequency) without the residual-error hotspot override,
    so the partition is independent of the residual being measured and the index
    cannot be inflated by construction."
  - **`lsg/eoi.py`** docstring — same sentence, plus the explicit note that the
    production Rule partition "is not identical to the EOI partition."
  - **Fig 15/16 captions** — now say "residual-free four-class hydrodynamic
    partition".

- **Why not recompute pooled EOI on a train-only subset:** the pooled EOI is a
  *retrospective all-event descriptor*, and the manuscript now says so rather
  than calling it a training-data diagnostic. Methods/Fig 15 caption now state
  "computed over all available events (Carlisle n=9, Burnett n=30, Chowilla
  n=29)", and §4.4 now explicitly contrasts the pooled (retrospective) values
  with the fold-level (train-only) values in Fig 16.

If you disagree with the "clarify, not recompute" decision for #1 (i.e. you think
a residual-informed partition is what a reader would expect), tell me and I will
add a residual-informed EOI as a *separate, clearly-labelled* variant rather than
replacing the residual-free one.

## 2. Audit pack body now actually closed (#3)

`figure_code_audit_pack.md` was rebuilt from the current scripts/manuscript/JSON
(this time the body, not just the header):
- **All links pinned** to `9e5887d` (no more drifting `/master/`), including the
  manuscript link and every embedded figure URL.
- **Fig 4** now shows the current `(a)/(b)` tags and `KMeans zonal` legend, and
  the current caption wording.
- **Fig 7** caption now carries the bootstrap-unit sentence; the pack notes the
  `mean [lo, hi]` labels are offset off the whiskers.
- **Fig 10** caption now states "positive values indicate that the Rule absolute
  error is smaller."
- **Fig 12** caption now says "seed-42 random subsample of the HF wet cells
  (depth ≥ 0.03 m, at most 40,000)" and canonical-RMSE caveat.
- **Fig 15** caption now includes "not by construction bounded by [0,1]" and the
  pooled all-event scope.
- **Fig 16** caption now says "train-only EOI (residual-free partition)", and the
  Burnett correlation is corrected from `−0.425` to `−0.224` (matches
  `eoi_all.json` `corr_eoi_delta_rmse = −0.22396`).
- **Fig 5/13** now documented as paired dumbbells, **Fig 14** documents the
  Carlisle inset, **Fig 17** documents the random 7/2 seed-42 split.

## 3. Fig 14 caption mentions the inset (#4)

Caption now ends with "The inset magnifies the Carlisle bars to resolve the
smaller between-model differences."

## 4. Fig 16 marker overlap (#5)

`fig15_eoi_vs_delta.png` markers are now hollow (edge-only, `facecolors="none"`,
`linewidths=0.7`, per-case Nature-style edge colours), so the dense Burnett
cluster near EOI ≈ 0.90–0.97 is readable. No threshold line was re-added.

## 5. Rebuild + audit

Regenerated `97_scienceplots_figures.py`, rebuilt `manuscript.html/.pdf` and both
Chinese reports, re-ran `scripts/100_manuscript_data_audit.py` → **54/54 PASS**.
Manuscript backed up as `paper/manuscript_v1.0rc_R17after_20260819_0345.md`.

---

## What to re-verify (specific)

- **Methods §2.4 + Fig 15/16 captions**: confirm the "residual-free four-class
  hydrodynamic partition" wording is internally consistent and matches
  `lsg/eoi.py` (`rule_based_zones` is called *without* `lf_hf_abs_residual`).
- **§4.4**: confirm the pooled-vs-fold-level scope contrast reads correctly.
- **`figure_code_audit_pack.md`**: confirm every link is pinned to `9e5887d`,
  the Fig 4 code matches the current script, and Fig 16 corr is `−0.224`.
- **Fig 16 PNG**: confirm the hollow markers render and the Burnett cluster is
  legible.
- **Fig 14 caption**: confirm the inset sentence is present.

## What to return

A numbered list of concrete findings (manuscript figure number + PNG file +
issue class + one-line fix suggestion). Focus on what is wrong or ambiguous; no
need to restate what is now correct.
