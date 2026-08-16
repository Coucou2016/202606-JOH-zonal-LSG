# Executable manuscript framework (JOH / WRR methods paradigm)

**Target venue (working):** Journal of Hydrology (primary) or Water Resources Research (methods).  
**Paper type (nature-writing):** methods.  
**One-sentence argument:** In multi-fidelity flood inundation emulation, a global EOF representation can be performance-sensitive under constrained retained-mode capacity; under an audited budget protocol, hydrodynamically zoned LSG-Max can reduce area-weighted depth RMSE conditionally, but first-order EOI is not a zoning switch.

**Imitated architecture:** Fraehr et al. WRR/Water Research LSG papers (problem → method modules → multi-case results → honest boundary cases) + Lu et al. 2025 JOH kernel-design paper (fixed LSG frame → internal design choice) + Wang et al. WRR Brisbane strategies (design questions, not “new model only”).

**Novelty boundary (from ChatGPT + local verify):** Do **not** claim first zonal/regionalized LSG — Tan et al. (2025, HESS) already use regionalized LSG training for local velocity DR error; Wang et al. (2025) use REOF–SGP localization inside an LF–EOF–SGP flood surrogate. Prefer “performance-neutral representation choice” over loose “hydrodynamically neutral.” Claim conditional equal total retained-mode budget zoning diagnostics instead.

---

## Section map & argument chain

| Section | Job | Evidence hooks | Figures/tables |
|---|---|---|---|
| Title/Abstract | Bounded claim: neutrality fails; zoning benefit conditional | Carlisle B=4; Burnett/Chowilla boundaries | — |
| 1 Introduction | Stake → bottleneck (global EOF) → gap (no equal-B zoning test) → this study | Literature (verified DOIs) | Fig01 workflow |
| 2 Methods | LSG-Max; zoning; equal-B; metrics; EOI; stage-swap; leakage | Protocol only | Fig02 zones; Table1–2 |
| 3 Results | Equal-B curves; LOOCV; three cases; EOI; stage-swap; published contrast | Track B numbers | Fig03–16,18 |
| 4 Discussion | Three questions (when/why/when-not) + mechanism | Interpret, not re-list | Fig14,19 |
| 5 Conclusions | 4–6 bounded bullets | No over-claim 2-fold | — |
| SI | Temporal EOI protocol note; audits; extra tables | CLEAN_PASS; MISMATCH B=8 | — |

---

## Novelty statements (evidence-locked)

1. **Conditional zoning benefit under equal mode budget** — Carlisle Rule 0.1464→0.0964 m (9/9 LOOCV); Burnett 30-fold Rule not better; Chowilla LSG degrades vs LF-only.
2. **First-order EOI is not a zoning switch** — EOI 0.057 / 0.116 / 0.957 does not rank zoning gains.
3. **Mechanism via second-order + stage-swap** — ZGG>0 but pure-EOF oracle ΔRMSE<0; LOOCV GG/ZZ/GZ/ZG ≈ 0.180/0.098/0.098/0.101 → gain from zoning structure into representation→mapping pipeline.
4. **Fair-comparison protocol** — true equal B, area-weighted metrics, train-only zoning/EOF/GP, leakage audit CLEAN_PASS; official 2-fold n.s. reported honestly.

---

## Discussion three questions

1. **When does zoning help?** Carlisle equal-B + event LOOCV.
2. **Why can zoning help when it does?** First-order EOI insufficient → pure-EOF truncation rejected → approximate stage-swap implicates coupled representation–mapping structure (not a unique causal stage).
3. **When does it fail / what does EOI mean?** Burnett high EOI no gain; Chowilla LSG worse than LF; EOI not switch; Global–B non-monotonicity is a related observation, not the Discussion spine.

---

## Out of scope (state in paper)

sklearn GPR (not gpflow SGPR); LSG-Max only (not real LSG-TS); Brisbane not run; Burnett KMeans LOOCV skipped.
