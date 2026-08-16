# When Is Global EOF Reduction Insufficient in Multi-Fidelity Flood Inundation Emulation?

**Working title (methods paper).** Hydrodynamically zoned LSG-Max under equal mode budget, area-weighted metrics, and train-only zoning.

**Status:** English manuscript draft v0.3 (Track B evidence locked; nature-polishing consistency pass; public code at https://github.com/Coucou2016/202606-JOH-zonal-LSG). Figures name existing files under `outputs/figures/` (SciencePlots + Times New Roman for Track B curves; fig02 kept from real geometry export).  
**nature-writing / polishing axes:** `task=manuscript`, `paper_type=methods`, `language=en`, `journal=generic` (JOH primary / WRR methods paradigm).  
**One-sentence argument:** Spatial zoning is not universally advantageous, but a global EOF representation can be performance-sensitive under constrained retained-mode capacity; under an audited retained-mode-budget protocol, zoning value is conditional on how spatial structure enters the coupled reduced-representation and LF-to-HF mapping pipeline, and first-order EOI alone cannot decide when to zone.

---

## Abstract

High-resolution two-dimensional flood models remain expensive for ensembles and real-time use. Multi-fidelity surrogates in the Low-fidelity–Spatial analysis–Gaussian Process (LSG) family upskill coarse hydrodynamic fields by Empirical Orthogonal Function (EOF) reduction and Gaussian Process (GP) coefficient mapping. Baseline LSG formulations commonly employ a global EOF representation over the wet floodplain, while its downstream performance consequence under matched retained-mode capacity has rarely been isolated. We test that consequence with hydrodynamically zoned LSG-Max on the public Fraehr et al. benchmark under an audited retained-mode-budget protocol (primary matched-budget inference at B = 4), area-weighted depth metrics, and train-only zoning/EOF/GP fits. At Carlisle with budget B = 4, rule zoning reduces area-weighted RMSE from 0.1464 m (global) to 0.0964 m, with improvement on 9/9 event leave-one-out folds. The official two-fold split is not significant and is reported as a benchmark-compatible sensitivity check, not as the primary claim. Burnett 30-fold leave-one-out does not favour rule zoning; at Chowilla, LSG degrades relative to the low-fidelity field alone (an upstream applicability boundary for LSG correction). Max-surface residual organization indices (EOI = 0.057 / 0.116 / 0.957) do not rank zoning gains. Second-order diagnostics and EOF×GP stage-swap experiments reject a pure-EOF-truncation explanation and are consistent with zonal structure acting through the coupled representation–mapping pipeline. The contribution is a conditional, mechanism-aware reading of when global EOF capacity is insufficient, not a universal zoning recipe.

**Keywords:** multi-fidelity surrogate; flood inundation; EOF; Gaussian Process; LSG; zonal reduction; equal-budget comparison

---

## 1. Introduction

Fine-grid two-dimensional hydrodynamic models remain the reference for flood extent and depth, yet their cost still limits large ensembles, scenario design, and operational refresh cycles (Teng et al., 2017; Bates, 2022). Multi-fidelity strategies retain a physically based low-fidelity (LF) run and learn a correction toward high-fidelity (HF) fields from a modest training set. The LSG family implements this idea by projecting LF and HF inundation onto EOF spatial modes and training sparse or standard GPs on expansion coefficients (Fraehr et al., 2022, 2023, 2024). Related work spans deep-learning inundation surrogates and hybrid LF–GP pipelines (Bentivoglio et al., 2022; Lu et al., 2025), but most LSG evaluations treat the floodplain as a single EOF domain.

That global basis is convenient; it is not necessarily a performance-neutral representation choice for depth emulation. Channel, frequently inundated shelves, and fringe shallow water can mix into shared leading modes. When the retained-mode budget B is tight, such mixing can waste capacity and bias depth learning even when wet–dry skill looks acceptable. Prior work already shows that spatial reduction, rotated/localized EOF structure, and LSG regionalization can help in focused settings: PCA–ANN downscaling (Carreau and Guinot, 2021), SRR/USRR reconstruction (Zhou et al., 2021, 2022), REOF–sparse-GP flood surrogates that motivate localized EOF structure inside an LF–EOF–SGP pipeline (Wang et al., 2025), and regionalized LSG training for local velocity dimensionality-reduction error (Tan et al., 2025). Those precedents rule out “first zonal LSG” and any broad claim that regionalizing EOF/LSG is itself novel. What remains insufficiently tested under a matched total retained-mode budget is whether zoning still changes LSG-Max depth skill, where any gain originates in the representation–mapping pipeline, and when zoning should be refused.

We therefore ask three methods questions under an audited retained-mode-budget protocol, area-weighted metrics, and train-only partitioning: (RQ1) when does zoning help; (RQ2) why does it help when it does (representation, mapping, or their coupling); and (RQ3) when not, and can a simple training-data diagnostic identify those cases? We implement hydrodynamically zoned LSG-Max (maximum inundation surfaces) with rule and KMeans partitions on Carlisle, Chowilla, and Burnett River, and add residual-organization and stage-swap diagnostics. The contribution is a bounded, falsifiable reading of conditional zoning, not a universal regionalization recipe.

---

## 2. Methods

### 2.1 Cases and data

We use the public Fraehr multi-fidelity inundation benchmark (Figshare 24312658). Carlisle (UK; HF LISFLOOD-FP, LF HEC-RAS 2D) is the primary statistical case (9 events). Chowilla (Australia; MIKE 21) is treated as a boundary case. Burnett River (Australia; HF TUFLOW, LF HEC-RAS 2D) provides a 30-event leave-one-out contrast. Cell counts follow Fraehr geometry (Carlisle HF/LF ≈ 581,061 / 5,681; Chowilla ≈ 109,914 / 1,434; Burnett ≈ 780,785 / 15,256). Synthetic 30×40 Track A trees are excluded from all claims.

**Table 1.** Case roles, geometry, and paper role (Fraehr Figshare 24312658). Max-surface EOI (Carlisle / Chowilla / Burnett) = 0.057 / 0.116 / 0.957.

| Case | Country | Hydro model (HF) | Events used / available | HF / LF cells | Paper role |
|---|---|---|---:|---:|---|
| Carlisle | UK | LISFLOOD-FP | 9 / 9 | 581,061 / 5,681 | Primary; 9-fold LOOCV |
| Chowilla | Australia | MIKE 21 | 12 / 31 | 109,914 / 1,434 | Boundary: LSG degrades vs LF-only |
| BurnettRV | Australia | TUFLOW | 12 / 74 (30-fold LOOCV) | 780,785 / 15,256 | Contrast; Rule not favoured on LOOCV |

### 2.2 Global and zoned LSG-Max

Wet cells use depth threshold 0.03 m. Global LSG-Max fits EOF on the wet HF training stack, projects LF onto the same modes, and maps LF→HF coefficients with sklearn Gaussian Process Regression (GPR). Zoned LSG-Max first partitions wet cells (rule: training max depth and inundation frequency; or KMeans K = 4), then runs per-zone EOF+GP under a shared total mode budget B. Zoning features, EOF bases, and GPs are fit on training events only.

![Fig. 1 Workflow](../outputs/figures/fig01_workflow.png)

![Fig. 2 Zone maps](../outputs/figures/fig02_zone_maps_real.png)

### 2.3 Fair comparison protocol

Audited retained-mode-budget protocol (Carlisle): matched equal total retained-mode budgets at B ∈ {4, 6}; Global B = 8 is retained only as a budget-audit exception (requested 8, realized 7 = MISMATCH), not as a strict equal-B claim. Matched budgets mean equal retained EOF capacity, not equal wall-clock cost or equal GP complexity. Area-weighted RMSE, MAE, bias, and CSI use geometric cell areas. Leakage audit reports CLEAN_PASS (official splits; train-only zoning/EOF/GP; metrics on held-out events).

### 2.4 Residual organization and stage-swap

First-order EOI summarizes between-zone versus within-zone residual structure on max surfaces. We treat the EOI-as-switch test as an exploratory falsification of a plausible first-order training-data diagnostic, not as prospective selector validation. Second-order ZGG and an equal-budget pure-EOF reconstruction oracle test whether zoning improves HF reconstruction without GP learning. Stage-swap arms (GG/ZZ/GZ/ZG) cross global versus zonal EOF coordinates with global versus zonal GP stacks; they are not four competing production models. GZ and ZG are diagnostic approximations rather than algebraically exact stage substitutions; accordingly, the stage-swap is used to reject single-stage explanations, not to estimate a unique causal contribution of each stage.

### 2.5 Statistical claims

Principal Carlisle paired stability analysis: 9-fold event LOOCV at B = 4 (and secondary B = 6). Official two-fold bootstrap is reported as a benchmark-compatible sensitivity check and is not promoted as the primary claim. Burnett uses 30-fold event LOOCV at B = 4. Uncertainty uses bootstrap confidence intervals on ΔRMSE = RMSE_global − RMSE_zonal.

---

## 3. Results

### 3.1 Equal-budget Carlisle curves

At B = 4, Global / Rule / KMeans area-weighted RMSE = 0.1464 / 0.0964 / 0.1015 m (Rule −34.2% vs Global). Empirically, Global RMSE rises from 0.1464 → 0.2588 → 0.3527 m as B grows to 6 and 8; Rule rises more slowly (0.0964 → 0.1256 → 0.1790 m). We report the Global–B rise as an observation under the equal-budget protocol; component-level attribution (for example, event-noise fitting) is not uniquely identified here. CSI does not show a matching zonal win: LF-only CSI (0.9145) exceeds LSG CSI at B = 4, so zoning improves depth RMSE more than wet–dry extent.

![Fig. 3 Mode budget](../outputs/figures/fig03_mode_budget.png)

![Fig. 9 CSI budget](../outputs/figures/fig09_csi_budget.png)

![Fig. 13 MAE/bias](../outputs/figures/fig13_mae_bias.png)

### 3.2 Event-level statistics

Carlisle B = 4 LOOCV: 9/9 folds improved; mean ΔRMSE = 0.0821 m; 95% CI [0.0155, 0.1987]. B = 6: 7/9; mean 0.0606 m; CI [0.0032, 0.1618]. Official two-fold: mean ΔRMSE = 0.0045 m; CI [−0.0073, 0.0134]; significant = false. Burnett B = 4 30-fold: mean Global 1.7479 m vs Rule 1.8260 m; ΔRMSE = −0.0781 m; 6/30; significant = false.

![Fig. 8 Per-event](../outputs/figures/fig08_per_event_bootstrap.png)

![Fig. 11 LOOCV scatter](../outputs/figures/fig11_loocv_scatter.png)

![Fig. 12 Statistical CI](../outputs/figures/fig12_stat_ci.png)

![Fig. 10 Burnett LOOCV](../outputs/figures/fig10_burnett_loocv.png)

### 3.3 Three-case pattern

**Table 2.** Three-case area-weighted depth RMSE (m) at B = 4.

| Case | LF-only | Global B=4 | Rule B=4 | Pattern |
|---|---:|---:|---:|---|
| Carlisle | 0.1602 | 0.1464 | 0.0964 | Zonal > Global > LF (RMSE) |
| Chowilla | 0.3926 | 2.5606 | 2.5614 | LF best; LSG upstream applicability boundary |
| Burnett (12-event split) | 2.2323 | 1.6120 | 1.6122 | Global ≈ Rule |

![Fig. 4 Three-case](../outputs/figures/fig04_three_case.png)

### 3.4 EOI, second-order, and stage-swap

Max-surface EOI: Carlisle 0.057, Chowilla 0.116, Burnett 0.957. Zoning benefit does not increase with EOI. Modal EOI registry shows ZGG > 0 with equal-budget pure-EOF oracle ΔRMSE < 0 on all three cases (ZGG_POSITIVE_ORACLE_LOSS), ruling out “zoning helps merely by truncating HF EOF better.” Stage-swap LOOCV means: GG ≈ 0.180, ZZ ≈ 0.098, GZ ≈ 0.098, ZG ≈ 0.101 m. These results reject a pure-EOF-truncation explanation and are consistent with zonal structure acting through the coupled representation–mapping pipeline; they do not uniquely attribute the gain to one localized stage or identify GP locality alone as the mechanism.

![Fig. 14 EOI](../outputs/figures/fig14_eoi.png)

![Fig. 15 EOI vs Δ](../outputs/figures/fig15_eoi_vs_delta.png)

![Fig. 19 Modal EOI](../outputs/figures/fig19_modal_eoi.png)

### 3.5 Published MaxWD contrast and robustness probes

This comparison is used only as a protocol-level sanity check and is not a head-to-head comparison with a locally reproduced LSG-TS implementation. On the official nine-fold MaxWD R² protocol, rule LSG-Max reaches 0.988 versus published LSG-TS 0.990 (Global Max ≈ 0.915). LF coarsening and channel-distance zoning probes (Figs. 17–18) support robustness narratives but are secondary to the equal-B LOOCV claim.

![Fig. 16 Official MaxWD R²](../outputs/figures/fig16_official_maxwd_r2.png)

![Fig. 17 LF degradation](../outputs/figures/fig17_lf_degradation.png)

![Fig. 18 Channel distance](../outputs/figures/fig18_channel_distance.png)

---

## 4. Discussion

**Thesis.** Spatial zoning is not universally advantageous, but a global EOF representation can be performance-sensitive under constrained retained-mode capacity. Under an audited retained-mode-budget protocol, the value of zoning is conditional on how spatial structure interacts with the coupled reduced-representation and LF-to-HF mapping pipeline; simple field heterogeneity alone is insufficient to decide when zoning should be used.

### Q1. When does zoning help under equal representation capacity?

Carlisle under equal B = 4 shows a large, fold-consistent depth RMSE reduction (9/9 LOOCV). The gain concerns depth-error organization under limited capacity, not inventing wet cells that the LF already captures well (CSI remains LF-led). The official two-fold contrast is non-significant and is kept as a sensitivity check. Burnett 30-fold leave-one-out is the equal-budget non-benefit contrast. This is the conditional claim, not evidence that zoning always wins.

### Q2. Why can zoning help when it does?

First-order EOI does not explain the pattern. The pure-EOF oracle rules out a truncation-only explanation. Stage-swap then points to coupled representation–mapping locality without uniquely attributing the gain to one stage. The non-monotonic Global–B behaviour is reported as a related capacity observation, not as the Discussion spine.

### Q3. When should zoning not be used?

Burnett shows that high first-order EOI does not justify zoning under equal B. EOI therefore has no reliable threshold as a deployable switch. Chowilla shows a more fundamental upstream question: whether LSG correction should be applied at all when LSG is far worse than LF-only. EOI has been ruled out as a sufficient first-order training-data diagnostic, but the present experiments do not yet establish a transferable criterion for choosing between global and zonal LSG.

Rival explanations rejected or weakened: (i) accidental unequal budgets (audited); (ii) test leakage into zoning (CLEAN_PASS); (iii) GP-only localization as the unique cause (ZG ≈ ZZ as well as GZ ≈ ZZ); (iv) official two-fold as primary evidence (CI includes zero).

### Limitations

Results use LSG-Max with sklearn GPR, not the canonical gpflow Sparse GP / LSG-TS path. Brisbane is unused. Only Carlisle is a clear zoning-positive public case. No validated operational zoning selector is claimed. Chowilla archive MD5/datum remain flagged. Burnett KMeans LOOCV and full 74-event panels are incomplete. Historical temporal EOI (≈ 0.51) uses a different protocol and is SI-only.

---

## 5. Conclusions

1. On Carlisle at equal B = 4, the global EOF representation was not performance-neutral for multi-fidelity depth emulation (0.1464 → 0.0964 m; 9/9 LOOCV).
2. In the Carlisle budget sweep, increasing the requested global mode count did not recover the B = 4 zonal advantage; the B = 8 point is retained as an audited mismatch rather than a strict equal-B comparison.
3. Zoning benefit is conditional: Burnett 30-fold does not favour Rule; Chowilla is an upstream LSG-vs-LF applicability boundary.
4. First-order max-surface EOI does not select zoning; mechanism evidence rules out pure-EOF truncation and does not uniquely pin the gain to one stage (stage-swap).
5. Official two-fold non-significance must be stated; it is a sensitivity check, not the principal paired claim.

---

## Data and code availability (draft)

- Data: Fraehr et al. public benchmark, Figshare 24312658.
- Code and artefacts: https://github.com/Coucou2016/202606-JOH-zonal-LSG (public; raw hydrodynamic HDF/NPZ excluded).
- Numbers: `outputs/registry/result_manifest_v4.csv` and evaluation JSON under `outputs/evaluation/`.
- Report generators: `scripts/95_final_submission_report.py`, `scripts/96_research_report_zh.py`, `scripts/99_full_report_zh.py`.
- Figures: `outputs/figures/fig*.png` (SciencePlots + Times New Roman for Track B curves).

---

## References (independently verified seed list)

1. Fraehr, N., Wang, Q. J., Wu, W., & Nathan, R. (2022). Upskilling low-fidelity hydrodynamic models of flood inundation through spatial analysis and Gaussian Process learning. *Water Resources Research*, 58, e2022WR032248. https://doi.org/10.1029/2022WR032248
2. Fraehr, N., Wang, Q. J., Wu, W., & Nathan, R. (2023). Development of a fast and accurate hybrid model for floodplain inundation simulations. *Water Resources Research*, 59, e2022WR033836. https://doi.org/10.1029/2022WR033836
3. Fraehr, N., et al. (2024). Assessment of surrogate models for flood inundation: The physics-guided LSG model vs. state-of-the-art machine learning models. *Water Research*, 252, 121202. https://doi.org/10.1016/j.watres.2024.121202
4. Bentivoglio, R., Isufi, E., Jonkman, S. N., & Taormina, R. (2022). Deep learning methods for flood mapping: a review of existing applications and future research directions. *Hydrology and Earth System Sciences*, 26, 4345–4378. https://doi.org/10.5194/hess-26-4345-2022
5. Teng, J., Jakeman, A. J., Vaze, J., Croke, B. F. W., Dutta, D., & Kim, S. (2017). Flood inundation modelling: A review of methods, recent advances and uncertainty analysis. *Environmental Modelling & Software*, 90, 201–216. https://doi.org/10.1016/j.envsoft.2017.01.006
6. Bates, P. D. (2022). Flood inundation prediction. *Annual Review of Fluid Mechanics*, 54, 287–315. https://doi.org/10.1146/annurev-fluid-030121-113138
7. Lu, J., Wang, Q. J., Fraehr, N., Xiang, X., & Wu, X. (2025). Choice of Gaussian Process kernels used in LSG models for flood inundation predictions. *Journal of Hydrology*, 655, 132949. https://doi.org/10.1016/j.jhydrol.2025.132949
8. Carreau, J., & Guinot, V. (2021). A PCA spatial pattern based artificial neural network downscaling model for urban flood hazard assessment. *Advances in Water Resources*, 147, 103821. https://doi.org/10.1016/j.advwatres.2020.103821
9. Zhou, Y., Wu, W., Nathan, R., & Wang, Q. J. (2021). A rapid flood inundation modelling framework using deep learning with spatial reduction and reconstruction. *Environmental Modelling & Software*, 143, 105112. https://doi.org/10.1016/j.envsoft.2021.105112
10. Zhou, Y., Wu, W., Nathan, R., & Wang, Q. J. (2022). Deep learning-based rapid flood inundation modeling for flat floodplains with complex flow paths. *Water Resources Research*, 58, e2022WR033214. https://doi.org/10.1029/2022WR033214
11. Tan, Z., Xu, D., Taraphdar, S., Ma, J., Bisht, G., & Leung, L. R. (2025). An efficient hybrid downscaling framework to estimate high-resolution river hydrodynamics. *Hydrology and Earth System Sciences*, 29, 3833–3852. https://doi.org/10.5194/hess-29-3833-2025
12. Wang, R., Lian, J., Yuan, X., Tian, F., Li, K., & Liu, Z. (2025). Rapid simulation of floods by considering the spatial and temporal characteristics of inundation. *International Journal of Disaster Risk Science*, 16, 481–495. https://doi.org/10.1007/s13753-025-00642-5
13. Fraehr, N., Wang, Q. J., Wu, W., & Nathan, R. (2023). Supercharging hydrodynamic inundation models for instant flood insight. *Nature Water*, 1, 835–843. https://doi.org/10.1038/s44221-023-00132-2
14. Wang, W., Wang, Q. J., & Nathan, R. (2026). Strategies for predicting flood inundation in a large and complex floodplain based on low-fidelity hydrodynamic models. *Water Resources Research*. https://doi.org/10.1029/2025WR042481

Full ChatGPT literature map + adopt/reject table: `paper/chatgpt/` and `paper/refs/citation_audit.md`.

---

## Assumptions / missing inputs

- GP backend remains sklearn until gpflow/SGPR is installed and re-run.
- Figure binaries may still be regenerating; filenames above are the contract with the figure workline.
- Author list, funding, and exact target journal wording TBD.
