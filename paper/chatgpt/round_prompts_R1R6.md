# CONTEXT packs for ChatGPT formal rounds (desensitized; no secrets)

Public repo: https://github.com/Coucou2016/202606-JOH-zonal-LSG  
Current master commit after sync: `679d6b7`  
Raw manuscript: https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/paper/manuscript.md

## Locked Track B facts (must not contradict)

- Carlisle B=4 Rule RMSE 0.1464 → 0.0964; 9/9 LOOCV; mean ΔRMSE 0.0821; CI [0.0155, 0.1987]
- Official 2-fold: mean Δ 0.0045; CI [-0.0073, 0.0134]; significant=false
- Burnett 30-fold: Global 1.7479 vs Rule 1.8260; Δ=-0.0781; 6/30; significant=false
- Chowilla: LF 0.3926; Global≈2.5606; Rule≈2.5614 (LSG ≤ LF-only boundary)
- EOI max-surface: 0.057 / 0.116 / 0.957 (Carlisle/Chowilla/Burnett)
- stage-swap LOOCV means: GG 0.180 / ZZ 0.098 / GZ 0.098 / ZG 0.101
- MaxWD R² rule 0.988 vs published TS 0.990 (sanity only; not head-to-head)
- Novelty ≠ first zonal LSG; = equal-B conditional zoning + EOI falsification + stage-swap + honest boundaries
- Pending: gpflow/SGPR, Brisbane, true zonal LSG-TS

## R1 prompt (maturity score + GitHub read proof)

You are the external academic advisor. **Enable web search.**

Please OPEN and quote evidence from these raw URLs (prove you read the current master, commit `679d6b7` or later):
1. https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/paper/manuscript.md
2. https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/679d6b7/paper/manuscript.md (if master cache stale)
3. https://github.com/Coucou2016/202606-JOH-zonal-LSG

Tasks:
A) Reading proof: quote (i) Status line version, (ii) §2.3 budget protocol wording for B=8, (iii) stage-swap LOOCV means line, (iv) Ref 14 author line.
B) Maturity score 0–10 for JOH/WRR methods submission readiness.
C) Gap list ranked by blocking risk (claim overreach / missing method detail / data inconsistency / literature / language).
D) Do NOT invent numbers. If unsure, mark 【待补充】.
E) Forbid “first zonal LSG”. Search Tan 2025 HESS and Wang 2025 REOF–SGP.

Return concise A–E with adopt/reject ready bullets.
