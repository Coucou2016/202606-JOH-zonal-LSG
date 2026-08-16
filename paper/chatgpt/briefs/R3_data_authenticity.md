# Round R3 — Data authenticity final audit

**Date:** 2026-08-17  
**Role:** ChatGPT = advisor (web search ON); Cursor = executor (local JSON is ground truth)  
**Repo:** https://github.com/Coucou2016/202606-JOH-zonal-LSG

## Reading proof (required first)

Quote verbatim from:

1. This brief: https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/paper/chatgpt/briefs/R3_data_authenticity.md  
2. Provenance: https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/paper/DATA_PROVENANCE.md  
3. Audit JSON: https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/evaluation/manuscript_data_audit.json  
4. Manuscript Abstract + Table 1/2 region: https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/paper/manuscript.md  

**Proof:** paste (a) audit `n_checks`/`n_pass`/`all_pass`, (b) provenance “Audit result” line, (c) Abstract sentence containing 0.1464→0.0964, (d) EOI triple 0.057/0.116/0.957 as in manuscript.

## Local summary (for your cross-check; do not invent beyond this)

Machine audit (`scripts/100_manuscript_data_audit.py` → JSON): **43/43 PASS; all_pass=true**.

Headline locked values (observed=expected):

| Claim | Value |
|---|---|
| Carlisle B=4 Global RMSE | 0.1464 m |
| Carlisle B=4 Rule RMSE | 0.0964 m |
| Carlisle B=4 KMeans RMSE | 0.1015 m |
| Carlisle LF RMSE / CSI | 0.1602 / 0.9145 |
| Carlisle B=6 Global/Rule | 0.2588 / 0.1256 |
| Carlisle B=8 Global / actual modes | 0.3527 / 7 |
| EOI Carlisle / Chowilla / Burnett | 0.057 / 0.116 / 0.957 |

## Task

Hunt for **inconsistencies** between manuscript wording and the audit JSON / provenance doc:

1. Numeric mismatches (precision, rounding, wrong case attribution).  
2. Over-claims (significance, universality, selector validation).  
3. Mislabelled protocols (Burnett 12-event vs 30-fold; B=8 exception).  
4. Soft process language that should stay report-only.

If you find a conflict, propose manuscript wording that prefers **JSON truth**. If none, say so explicitly.

## Required deliverable

1. Understanding  
2. Reading proof  
3. Inconsistency list (blocker/major/minor) or “NONE found”  
4. Suggested edits (no invented metrics)  
5. Risks  
6. Still uncertain  
