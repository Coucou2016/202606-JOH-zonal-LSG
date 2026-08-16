# Round R1 — Manuscript v0.7 maturity audit + paper/report separation

**Date:** 2026-08-17  
**Role:** ChatGPT = advisor (enable **web search**); Cursor = sole executor  
**Repo (public):** https://github.com/Coucou2016/202606-JOH-zonal-LSG  
**Conversation preference:** continue https://chatgpt.com/c/6a812977-6814-83ea-9a9d-f27c1dbd8a8f

## Reading proof (required first)

Before any advice, open **and quote verbatim** from these raw URLs (do not invent; if fetch fails, say so):

1. Manuscript: https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/paper/manuscript.md  
2. This brief: https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/paper/chatgpt/briefs/R1_readiness.md  
3. Collaboration log (tail): https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/paper/chatgpt/collaboration_log.md  

**Proof format:** paste (a) the manuscript Status line (v0.7), (b) Abstract first sentence, (c) the one-sentence argument line, (d) the exact heading of §4 Limitations or Data availability as present on raw.

## Task

Audit current English manuscript draft **v0.7** for submission readiness and **paper vs research-report duty separation**.

### A. Maturity score (advisory)

Score 0–10 for Journal of Hydrology methods-paper readiness and for WRR-style methods clarity. Justify with concrete gaps (structure, evidence, novelty boundary, SI).

### B. Paper vs report separation checklist

Flag any remaining manuscript violations of:

| Rule | Paper must | Report may |
|---|---|---|
| Local paths | No `I:\`, no workspace paths | Yes |
| Scripts / JSON piles | No `scripts/*.py` stacks; no evaluation JSON inventories | Yes |
| Collaboration meta | No ChatGPT / nature-polishing / Track A process notes | Yes |
| Novelty | No “first zonal LSG” | Process notes OK if accurate |

Local pre-scan (Cursor, 2026-08-17): `paper/manuscript.md` grep for `scripts/`, ChatGPT, nature-polishing, Track A, Windows paths → **no matches**. Please re-check on raw and list any residual soft violations (e.g., overly process-flavoured Scope boundaries, figure path style `../outputs/figures/...`).

### C. What is still missing / untrue / must change

Distinguish:

1. **Must-fix in manuscript** (wording, claim scope, figure/table clarity)  
2. **Must remain Scope/Limitation** (cannot invent experiments)  
3. **Report-only detail** (keep out of paper)

Known honest boundaries already in draft: gpflow not run; Brisbane absent; no real zonal LSG-TS headline; no transferable EOI selector; Fraehr 2024 full PDF access blocked.

### D. Novelty boundary

Confirm manuscript does **not** claim first zonal/regionalized LSG. Novelty must stay: equal-budget diagnosis + cross-case boundary map (Tan 2025 / Wang 2025 already regionalize).

## Required deliverable structure

1. **Understanding** (≤8 lines)  
2. **Reading proof** (verbatim quotes)  
3. **Problem list** (numbered; severity: blocker / major / minor)  
4. **Suggested edits** (paste-ready where useful; no invented numbers)  
5. **Risks**  
6. **Still uncertain**  

Do **not** invent metrics. If a number is needed, cite only what appears in the raw manuscript or say “needs local JSON verify”.
