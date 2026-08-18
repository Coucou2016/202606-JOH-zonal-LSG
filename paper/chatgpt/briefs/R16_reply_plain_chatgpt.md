# R16 reply — plain ChatGPT (图片代码双审 马会)

Reviewed `master@cafb58b` (the commit named in the R16 brief). Verdict: the R16
figure edits are present, but the round is **not a clean 10/10** — one old
provenance item is still open at that commit and several new light/moderate
issues were found.

## Findings (ranked)

1. **provenance / audit pack【需修】** — `figure_code_audit_pack.md` header still
   read `e8d012a (latest master)` at `cafb58b`. (Root cause: the header was only
   bumped to `cafb58b` in the follow-up commit `f357c19`.) Fix: point the header
   at the true code/figure commit and always ship the pack header in the same
   commit as the figures it describes.

2. **EOI threshold semantics【建议修】** — `lsg/eoi.py` still defines
   `EOI_HIGH=0.30` / `EOI_MODERATE=0.15` even though the plots no longer draw
   threshold lines and Methods says EOI is not a prospective threshold. Fix:
   delete/rename the constants or mark them "historical / exploratory only".

3. **bootstrap Methods【建议修】** — Fig 7 caption now states the bootstrap
   units (9/9 folds, 2-fold→4 events, 30 folds), but Methods §3.3 only formally
   defines the Carlisle bootstrap; the Burnett 30-fold and official 2-fold
   event-level bootstrap are not defined. Fix: add the two definitions to Methods.

4. **Fig 15 caption self-containment【建议修】** — code now uses `set_ylim(0,None)`
   (R15 fixed), but because the max EOI is 0.957 the axis still ends near 1.0,
   and the caption only says "Max-surface error-organization index" without
   noting EOI is not bounded by [0,1]. Fix: add the not-bounded caveat to the caption.

5. **Fig 12 sample spec【建议修】** — R16 caption says "≤40,000 seed-42 subsample",
   but the code mask is specifically `hf >= 0.03 m` (wet cells). Fix: caption
   should say "HF wet cells (hf ≥ 0.03 m)".

6. **Fig 4 caption completeness【低】** — PNG now has (a)/(b) and "KMeans zonal",
   but the manuscript caption still reads only "MAE and bias versus retained-mode
   budget" without mapping panels. Fix: "(a) MAE, (b) bias".

7. **Fig 7 visual【建议修】** — the R16 `ax.text(m, yy, …)` places the grey
   `mean [lo,hi]` labels on the same line as the marker/whisker, so text sits on
   top of the error bars (esp. Carlisle B=4 and Burnett rows). Fix: offset labels
   above the marker or into reserved right margin.

8. **Fig 10 sign semantics【低，新发现】** — panel (c) is `|Global−HF| − |Rule−HF|`,
   so positive means Rule absolute error is smaller (an improvement); the
   colorbar is named "Improvement (m)" but the caption only says "change in
   absolute error". Fix: caption should state positive = Rule better.

No new numeric misalignment or plotting index/sign bugs were found. Fig 14 inset
works; Fig 5/13 dumbbells are better than lines; Fig 11 zones + coord format are
fine; Fig 17 split is fine. Fig 16 should stay as-is (no threshold lines).

Priority: #1 provenance → #2 EOI threshold semantics → #3 bootstrap Methods;
#4–#8 are small caption/visual polish that can be closed in one pass.
