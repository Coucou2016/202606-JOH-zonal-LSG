# Completion audit — 2026-08-16 (maturation pass)

**Local executor:** Cursor  
**Advisor thread:** https://chatgpt.com/c/6a812977-6814-83ea-9a9d-f27c1dbd8a8f  
**Git:** local changes only; **no commit / push / PR / deploy** this round.

## 1. Baseline

| Item | Value |
|---|---|
| Branch | `master` @ `0677209` (origin/master) |
| Uncommitted before | manuscript HTML/MD/PDF + 98/99/_deep_fig_zh + spatial figs (untracked) |
| Python | `D:\miniforge3\envs\hydromodel\python.exe` |
| Fraehr 2024 full text | ScienceDirect CAPTCHA stopped; Adelaide OA claimed by advisor but local URL probes 404 — **cannot claim exact full-text length matching** |

## 2. Section length (EN words; approximate)

| Section | Pre (v0.5) | Post (v0.6) | R7 target |
|---|---:|---:|---:|
| Abstract | ~289 | **~192** (≤250 JOH) | ≤250 |
| Intro | ~428 | ~548 | ~825 |
| Methods (2.1–2.5) | ~623 | **~1100+** | ~1700 |
| Results | ~971 | ~1130+ | ~1400 |
| Discussion | ~515 | ~950+ | ~1250 |
| Conclusions | ~163 | ~163 | 180–220 |
| Body target | ~3.0k science | ~4.0–4.3k | ~5.6k |

**Precision note:** Still short of R7’s ~5.6k body target; further expansion should add Methods metrics/reproducibility and Discussion Q-depth without inventing numbers. Fraehr 2022 (~15k) / Tan 2025 (~13k) are **not** chased per R7 ACCEPT.

## 3. TODO / limitation disposition

| Item | Status | Evidence |
|---|---|---|
| All-fold leakage autofold | **COMPLETED** | `scripts/20b_audit_leakage_autofold.py`, `outputs/audit/leakage_autofold.json`, `tests/test_leakage_and_oracle.py` |
| Area-weighted oracle | **COMPLETED** | `lsg/eoi.py` + `scripts/46_modal_eoi.py`; Chowilla area ΔRMSE=−0.0543 (still neg.) |
| Methods/SI hyperparams | **COMPLETED** | `paper/si_hyperparameters.md` |
| Manuscript numeric audit | **COMPLETED** | `scripts/100_manuscript_data_audit.py` **43/43 PASS**; `paper/DATA_PROVENANCE.md` |
| Spatial maps provenance | **COMPLETED** | `outputs/figures/spatial_maps_manifest.json` (20 figs) |
| gpflow/SGPR | **FORMALIZED LIMITATION** | no TF/gpflow in env; acceptance criterion in Limitations |
| Brisbane | **FORMALIZED SCOPE BOUNDARY** | no licensed data |
| Real zonal LSG-TS Track B | **FORMALIZED SCOPE BOUNDARY** | Max-only headlines |
| Transferable selector | **SCIENCE-SHOULD-NOT-FORCE** | EOI falsified |
| Burnett KMeans/74 | **FORMALIZED LIMITATION** | 30-fold Rule LOOCV sufficient for non-benefit claim |
| Chowilla MD5/datum | **FORMALIZED LIMITATION** | no authoritative hash |
| Fraehr 2024 full PDF | **BLOCKED/HOLD** | CAPTCHA; Adelaide probe unverified |

## 4. Data authenticity

- Checks: **43/43 PASS**
- Inconsistencies fixed in *audit parser* (JSON schema), not by altering evaluation JSON
- Chowilla Rule RMSE sourced from `budget_sweep_full.json` (2.5614), not ambiguous `zonal` arm in `budget_sweep.json`

## 5. Tests

```text
pytest -q  →  41 passed
```

## 6. Regenerated artefacts

- `paper/manuscript.md/.html/.pdf` (via `98_paper_html.py`)
- `完整研究报告.*` (via `99_full_report_zh.py`)
- `outputs/evaluation/eoi/modal_eoi.json` (area oracle fields)
- `outputs/evaluation/manuscript_data_audit.json`
- `paper/DATA_PROVENANCE.md`
- `paper/si_hyperparameters.md`

## 7. Remaining risks

- Body length still below R7 editorial target (~5.6k)
- Fraehr 2024 structural mimicry remains **abstract/metadata-limited** until OA PDF is confirmed locally
- Brisbane / SGPR / LSG-TS / selector not done — correctly scoped, but external reviewers may still ask
- Public GitHub may lag local spatial-map + v0.6 edits (no push this round)
