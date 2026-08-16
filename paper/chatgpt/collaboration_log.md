# ChatGPT collaboration log — JOH zonal LSG paper workline

**Date:** 2026-08-17  
**Local executor:** Cursor agent  
**External advisor:** ChatGPT Pro (`pjn xdq Pro`)  
**Active conversation (clean; prior preferred URL contaminated):** https://chatgpt.com/g/g-p-6a1bc25ff4b48191b2804a0ba94a4e4d/c/6a81f0ce-2b50-83ea-bb5d-2930587c3ad5  
**Project:** LSG WRR paper  
**Git:** public https://github.com/Coucou2016/202606-JOH-zonal-LSG (commit + push allowed)

---

## Round R1 — Maturity + paper/report separation (2026-08-17)

| Field | Value |
|---|---|
| URL | https://chatgpt.com/g/g-p-6a1bc25ff4b48191b2804a0ba94a4e4d/c/6a81f0ce-2b50-83ea-bb5d-2930587c3ad5 |
| Brief | `paper/chatgpt/briefs/R1_readiness.md` |
| Web search | Enabled (GitHub raw chips) |
| Push before ask | `ad22ae3` / `330915b` (v0.7 + briefs) |

### Reading proof
- Advisor initially quoted **stale** public Status `v0.4` and an old Abstract opener.
- **Local independent verify** of raw master after push: Status **v0.7**; Abstract opener “computationally expensive…”. → **REJECT stale-public BLOCKER**.

### Adopt / reject
| Item | Decision | Landing |
|---|---|---|
| Stale-public v0.4 / process contamination still in raw | **REJECT** | Local urllib + `git show` prove v0.7 clean of scripts/ChatGPT |
| Safer title (matched-capacity diagnostic) | **ADOPT** | `paper/manuscript.md` → v0.8 |
| Case-subset provenance (Chowilla 12/31; Burnett 12 vs 30) | **ADOPT** | §2.1 |
| Bootstrap CI resampling detail | **ADOPT** | §2.5 |
| Front-matter Status/one-sentence-argument cleanup | **ADOPT** | title block |
| Full contiguous figure renumber 1…N | **HOLD** | large churn; keep A1–A5 + existing fig IDs |
| first zonal LSG | **REJECT** | novelty PASS already |

Tests after landing: `100_manuscript_data_audit.py` **43/43 PASS**; `pytest` **41 passed**. Commit: `7c349b6`.

---

## Round R2 — Fraehr/Tan style gaps (in progress)

| Field | Value |
|---|---|
| Brief | `paper/chatgpt/briefs/R2_style_fraehr_tan.md` |
| Cache-bust MS | `.../7c349b6/paper/manuscript.md` |

---

## Prior archived rounds

See git history of this file for R1–R9 (2026-08-16) and Rounds A/B style polish notes.
