# Desensitized brief for ChatGPT (Track B paper writing)

No secrets, paths-as-local-only, no code dumps. Paste as CONTEXT blocks.

## Project one-liner
Multi-fidelity flood inundation emulation (LSG-Max): test whether global EOF reduction is hydrodynamically neutral, and when hydrodynamically zoned EOF+GP helps under equal mode budget.

## Established Track B facts (cite only these numbers)
- Core claim: global EOF is NOT hydrodynamically neutral; zoning benefit is conditional.
- Carlisle B=4 equal budget: Rule RMSE 0.1464 → 0.0964 m (−34.2%); 9/9 LOOCV improved; mean ΔRMSE 0.0821 m, 95% CI [0.0155, 0.1987].
- Official 2-fold bootstrap: mean ΔRMSE 0.0045 m, CI [−0.0073, 0.0134], significant=false (report honestly; not primary claim).
- Burnett 30-fold LOOCV B=4: Global mean 1.7479 vs Rule 1.8260; ΔRMSE −0.0781; 6/30; significant=false.
- Chowilla boundary: LSG ~2.5606 m vs LF-only 0.3926 m (LSG degrades).
- First-order max-surface EOI: Carlisle 0.057 / Chowilla 0.116 / Burnett 0.957 → first-order EOI is NOT a zoning switch.
- Second-order: ZGG>0 but equal-budget pure-EOF oracle ΔRMSE<0 (rules out pure truncation benefit).
- Stage-swap LOOCV means (m): GG≈0.180 / ZZ≈0.098 / GZ≈0.098 / ZG≈0.101 → gain from zoning structure into representation→mapping pipeline, not pure EOF truncation alone.
- Published 5-model contrast (official 9-fold MaxWD R²): Rule LSG-Max 0.988 vs published LSG-TS 0.990.
- Gaps: no gpflow/SGPR; no real LSG-TS; Brisbane not run.

## Fair-comparison protocol
True equal mode budget B; area-weighted RMSE/CSI; zoning/EOF/GP fit on training events only; leakage audit CLEAN_PASS.

## Ask of ChatGPT
1) Enable web search; survey primary literature (DOI/journal/year).
2) Propose JOH/WRR-style executable manuscript architecture.
3) Help refine novelty statements grounded in evidence above.
