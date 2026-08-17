# Data provenance — JOH zonal LSG manuscript

Machine audit: `scripts/100_manuscript_data_audit.py` → `outputs/evaluation/manuscript_data_audit.json`.

**Audit result:** 54/54 PASS; ALL PASS

## Primary numeric sources (Track B)

| Claim family | Source artefact |
|---|---|
| Carlisle equal-B RMSE/CSI | `outputs/evaluation/carlisle/budget_sweep_true_equal.json` |
| Carlisle LOOCV / CI | `.../loocv_results.json`, `.../loocv_bootstrap_ci.json` |
| Official 2-fold | `.../multifold_bootstrap.json` |
| Burnett 30-fold | `outputs/evaluation/burnettrv/loocv_results.json` |
| Chowilla / three-case | `outputs/evaluation/chowilla/budget_sweep*.json`, Burnett validation |
| EOI | `outputs/evaluation/eoi/eoi_all.json` |
| Modal EOI / oracle | `outputs/evaluation/eoi/modal_eoi.json` |
| Stage-swap | `outputs/evaluation/carlisle/stage_swap.json` |
| Spatial maps | `outputs/figures/spatial_maps_manifest.json` + `scripts/97b_spatial_maps.py` |

## Failed or soft checks

- None.

## Scope boundaries (not numeric errors)

- gpflow/SGPR backend not run in this environment (sklearn GPR production numbers).
- Brisbane licensed data absent (`config/cases/brisbane.yaml`).
- Real zonal LSG-TS on Fraehr packs not claimed as Track B headline.
- Fraehr 2024 full PDF obtained 2026-08-17 (user-supplied publisher PDF, CC BY); used for structure/length benchmarking only, not as a numeric source.
- Burnett HF cells = 780,785 in the analysed max-surface subset; the benchmark reports a ~3.7M-cell native grid.

## Cell areas

- Carlisle HF Area ≡ 25 m² (uniform); Burnett ≡ 400 m² (uniform).
- Chowilla HF Area varies (~139–25628 m²) → area-weighted oracle sensitivity is informative.

