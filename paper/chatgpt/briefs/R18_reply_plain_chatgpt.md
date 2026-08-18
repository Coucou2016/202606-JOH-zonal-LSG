# R18 reply — plain ChatGPT (图片代码双审 马会)

Reviewed `9e5887d` figures/manuscript plus HEAD `01fefcb` brief + rebuilt audit
pack. Verdict: the R17 EOI residual-free decision is internally consistent
(`eoi_from_max_surfaces()` really calls `rule_based_zones()` with only
max-depth + inundation frequency, no residual hotspot; the code states the
production Rule partition differs from the EOI partition). Fig 14 inset, Fig 16
hollow markers, and Fig 7 label-off-whisker are all visually closed.

## New / residual findings (ranked)

1. **Fig 1–17 — provenance / audit-pack version chain【中高】.** The rebuilt
   pack in `01fefcb` is correct (Fig 4 is `(a)/(b)` + `KMeans zonal`, Fig 16 is
   Burnett corr −0.224, links pinned to `9e5887d`), **but** the R18 brief points
   the canonical pack at `9e5887d/.../figure_code_audit_pack.md`, which is still
   the *old* R17 pack (header `bcf1fcb`, `/master/` links, old Fig 4 code, Fig 16
   −0.425), and the brief's own URL `9e5887d/.../R18_eoi_scope_clarification.md`
   is a 404 (the brief + rebuilt pack were only committed in `01fefcb`). Fix:
   pin the canonical pack URL in the brief to `01fefcb`, and separate
   "figure/manuscript baseline = 9e5887d" from "audit-pack revision = 01fefcb".

2. **Fig 15–16 — Methods §2.4 still says "training-data diagnostic"【中高】.**
   R18 fixed Fig 15 caption + §4.4 to all-event retrospective, but §2.4 still
   defines EOI unconditionally as "training LF-HF residual / training wet mask /
   exploratory training-data diagnostic". Fix: define EOI over a general event
   set S, then state "Fig 15 uses all available events retrospectively; Fig 16
   evaluates the same diagnostic on each training fold".

3. **Fig 15–16 — code metadata scope drift【中】.** `eoi.py` file docstring still
   says "training-data residual-organisation diagnostic"; both pooled and
   train-only paths write `result["n_train_events"] = hf.shape[0]`, so the 9/30/29
   all-event counts are still labelled `n_train_events`. Fix: rename to
   `n_events_used`, add `scope = "all_event_pooled" / "train_only"`, and make the
   file docstring a neutral "residual-organisation diagnostic".

4. **Fig 15 — cross-case comparability【中】.** Chowilla pooled EOI uses all 29
   events while its Fig 14/Table 2 performance uses the 12-event fixed subset, so
   "EOI ordering does not match the observed zoning benefit" is a descriptive
   cross-pool comparison, not a protocol-matched test. Fix: add to §4.4 "the
   cross-case comparison is descriptive; the Chowilla pooled EOI uses all 29
   available events whereas its performance comparison uses the 12-event fixed
   subset".

5. **Fig 7 — official 2-fold bootstrap inference【中，新发现】.** The official
   2-fold interval treats 4 held-out event differences (2 per fold) as 4
   bootstrap units, but the two events in a fold share one fitted model, so
   event-level resampling does not preserve within-fold dependence. No recompute
   needed (the manuscript already frames the split as a low-information
   sensitivity). Fix: in §3.3/Fig 7 caption label this item "descriptive
   event-level bootstrap interval for the official-split sensitivity; two
   held-out events share each fitted fold model".

ChatGPT: no new figure numeric misalignment, sign error, colorbar/coordinate
issue, or occlusion. R19 priority order: #2 → #3 → #1 → #4 → #5. #2/#3 are the
same pooled-vs-train-only scope, still open at the "paper definition" and
"machine metadata" ends; none of them change any EOI value.
