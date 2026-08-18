# R17 reply — plain ChatGPT (图片代码双审 马会)

Reviewed `master@c946e36`, pinning figures back to their parent commit `bcf1fcb`,
cross-checking the 17 PNGs, `97_scienceplots_figures.py` / `97b_spatial_maps.py`,
EOI code, JSON, audit pack, and manuscript. Verdict: R16's #2–#8 are all closed
(EOI threshold logic deleted, §3.3 bootstrap units written, Fig 7 labels off the
whiskers, Fig 4/10/12/15 captions consistent). Fig 7's Burnett
`−0.097 [−0.225, +0.001]` now reads clearly as crossing zero.

## New / residual findings (ranked)

1. **Fig 15 + Fig 16 — `fig14_eoi.png` / `fig15_eoi_vs_delta.png` — code
   correctness + internal consistency【高优先级】.** The EOI is *not* computed on
   the same zone partition the production Rule LSG actually uses. Production
   `ZonalLSG.fit()` computes the training mean |LF−HF| residual and passes it as
   `lf_hf_abs_residual=` into `rule_based_zones()`, then runs
   `merge_zones_to_budget()` at B=4; but `eoi_from_max_surfaces()` computes
   `mean_resid` yet calls zoning with only `max_depth` + `inund_freq` — no
   residual-hotspot override and no B=4 merge. So Fig 16's "in-fold training EOI"
   describes a *different*, residual-free Rule partition. Direct evidence:
   Carlisle Run2's production zone map has 4 zones (0–3) while the EOI JSON for
   the same held-out fold 1 reports `n_zones=3`. Fix: compute EOI from each
   production fold's final `zone_labels`; or, if the residual-independent design
   is intentional, rename it "residual-free hydrodynamic-partition EOI" and state
   it is not the production Rule partition's EOI, then re-examine Fig 15–16.

2. **Fig 15 — `fig14_eoi.png` — statistical scope + wording【高优先级】.** The
   pooled EOI is not strictly a "training-data diagnostic".
   `40_compute_eoi.py` calls `eoi_from_max_surfaces(hf, lf)` with default
   `event_index=None`, i.e. all current events together — Carlisle 9/9, Burnett
   30/30, Chowilla 29/29. But manuscript §2.4 defines EOI as a "training LF-HF
   residual / exploratory training-data diagnostic", while the main three-case
   comparison uses a 12-event Chowilla subset and Burnett has both a 12-event
   fixed split and 30-event LOOCV. Fix: recompute pooled EOI on the same training
   sample as the corresponding performance protocol, or keep the value but label
   Fig 15 explicitly "retrospective pooled all-event EOI (Carlisle n=9; Burnett
   n=30; Chowilla n=29)" and restrict the train-only claim to Fig 16.

3. **Fig 3/4/7/8/10/12/15/16/17 — provenance / audit-pack body【中高优先级】.**
   R16 #1 is only "header closed, body not closed". The header now points at
   `bcf1fcb`, but the pack still claims to give the "exact generating code" while
   its body keeps pre-R17 content, and all embedded image/manuscript URLs still
   point at the drifting `/master/`. Examples: Fig 4 pack still shows the old
   caption and `label="KMeans"` (real code is now `(a)/(b)` + `KMeans zonal`);
   Fig 7/10/12/15/17 pack captions lack the R17 caveats; Fig 16 pack records
   Burnett `corr = −0.425` while the recomputed `eoi_all.json` is `−0.22396`.
   Fix: rebuild the whole audit pack from the `bcf1fcb` scripts/manuscript/JSON
   and pin every `/master/` raw link to `bcf1fcb`, not just the header.

4. **Fig 14 — `fig04_three_case.png` — caption self-containment【低】.** The
   Carlisle magnified inset now works visually, but the caption never mentions
   it. Fix: append "The inset magnifies the Carlisle bars to resolve the smaller
   between-model differences."

5. **Fig 16 — `fig15_eoi_vs_delta.png` — visual quality【低】.** Burnett's 30
   squares cluster at EOI ≈ 0.90–0.97; `s=14, alpha=0.75` makes the center stack
   illegible (how many folds near ΔRMSE≈0?). Fix: smaller hollow squares, lower
   fill alpha (or edge only), optionally a marginal rug/count; do NOT re-add any
   EOI threshold line.

ChatGPT: #1 is the most important new finding (it may change the Fig 15–16 EOI
values themselves), #2 next, #3 is a provenance/engineering issue that does not
affect existing manuscript numbers. No new RMSE/CSI numeric misalignment, sign
inversion, index error, or colourmap/coordinate error was found in the other 17
figures.
