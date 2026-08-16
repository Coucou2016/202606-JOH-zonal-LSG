# ChatGPT collaboration log — JOH zonal LSG paper workline

**Date:** 20260617 / 2026-08-17  
**Local executor:** Cursor agent  
**External advisor:** ChatGPT Pro (`pjn xdq Pro`)  
**Active conversation:** https://chatgpt.com/g/g-p-6a1bc25ff4b48191b2804a0ba94a4e4d/c/6a81f0ce-2b50-83ea-bb5d-2930587c3ad5  
**Note:** Preferred URL `.../c/6a812977-...` was contaminated by other projects → clean thread opened in project **LSG WRR paper**.  
**Git:** https://github.com/Coucou2016/202606-JOH-zonal-LSG

---

## Round R1 — Maturity + paper/report separation

| Field | Value |
|---|---|
| URL | https://chatgpt.com/g/g-p-6a1bc25ff4b48191b2804a0ba94a4e4d/c/6a81f0ce-2b50-83ea-bb5d-2930587c3ad5 |
| Brief | https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/paper/chatgpt/briefs/R1_readiness.md |
| Web search | ON |

### Reading proof
- Advisor initially quoted stale Status `v0.4` (browser fetch lag / cache).
- **Local REJECT:** raw master after `ad22ae3`/`330915b` showed **v0.7** and Abstract “computationally expensive…”.

### Adopt / reject
| Item | Decision |
|---|---|
| Stale-public contamination BLOCKER | REJECT (local raw verify) |
| Safer matched-capacity title | ADOPT → v0.8 |
| Case-subset provenance | ADOPT |
| Bootstrap CI detail | ADOPT |
| Full figure renumber | HOLD |
| first zonal LSG | REJECT (already clean) |

---

## Round R2 — Fraehr/Tan style gaps

| Field | Value |
|---|---|
| Brief | `paper/chatgpt/briefs/R2_style_fraehr_tan.md` |
| Proof | Advisor quoted v0.8 title “Hydrodynamic Zoning under Matched EOF Capacity…” |

### Adopt
- §2.2 hierarchy (inherited / zoning change / held equal)
- Results argument order (equal-B first; extreme map diagnostic)
- Self-contained figure captions
- Rename §3.6 secondary analyses
- Soften Limitations; delete Structural-reference / post-ref Scope block
- Expand EOI once in Abstract

Landing: manuscript **v0.9** @ `1a5ebfd`. Tests: audit 43/43; pytest 41.

---

## Round R3 — Data authenticity

| Field | Value |
|---|---|
| Brief | `paper/chatgpt/briefs/R3_data_authenticity.md` |
| Proof | Advisor quoted audit 43/43 PASS + Abstract 0.1464→0.0964 + EOI triple |

### Outcome
- **NONE** numeric inconsistency vs audit JSON.
- ADOPT: soften “existence proof” wording; reduce audit-flavoured prose.
- REJECT inventing data; KEEP Chowilla provenance caveat.

Landing: manuscript **v0.9.1** (this commit).

---

## Round R4 — Gaps triage

| Field | Value |
|---|---|
| Brief | `paper/chatgpt/briefs/R4_gaps_triage.md` |
| Status | **SENT** in same ChatGPT thread; **response not retrieved** because Cursor `cursor-ide-browser` MCP became unavailable mid-run |

---

## Rounds R5–R6

| Round | Brief | Status |
|---|---|---|
| R5 | `briefs/R5_submission_polish.md` | **BLOCKED** (browser MCP down) |
| R6 | `briefs/R6_consistency_refs.md` | **BLOCKED** (browser MCP down) |

Briefs are already on public GitHub for resume.

---

## Local verification snapshot

- `100_manuscript_data_audit.py`: **43/43 PASS**
- `pytest -q`: **41 passed**
- Novelty scan: no “first zonal LSG”
