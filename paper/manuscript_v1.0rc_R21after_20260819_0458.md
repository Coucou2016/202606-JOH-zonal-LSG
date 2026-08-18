# Hydrodynamic Zoning with Matched EOF Capacity in Multi-Fidelity Flood-Inundation Emulation

## Abstract

High-resolution two-dimensional hydrodynamic models are computationally expensive for many ensemble and real-time flood applications. The Low-fidelity, Spatial analysis, and Gaussian Process learning (LSG) framework reduces this cost by representing inundation fields with Empirical Orthogonal Functions (EOFs) and learning a mapping from low-fidelity to high-fidelity expansion coefficients. Existing LSG applications have generally used a single EOF domain. This study examines whether partitioning that domain can improve LSG-Max water-depth prediction when the total retained-mode capacity is held fixed. Rule-based and KMeans zoning are evaluated on the public Fraehr benchmark, with Carlisle used for the primary matched-capacity analysis and Chowilla and Burnett used to examine transferability. At Carlisle, Rule zoning reduced area-weighted RMSE from 0.1464 to 0.0964 m at \(B=4\) and improved all nine leave-one-out folds. The corresponding official two-fold sensitivity analysis was not statistically significant. Burnett 30-fold leave-one-out did not favour zoning, and at Chowilla the LSG predictions were less accurate than the low-fidelity field alone. The tested error-organization index did not rank the cases in the same order as the observed zoning benefit, indicating that residual organization alone is not a reliable predictor of when zoning will help. Pure-EOF reconstruction and Carlisle stage-swap analyses provide no evidence for a truncation-only explanation and instead indicate that the benefit is associated with changes to the combined reduced representation and coefficient mapping. Hydrodynamic zoning can therefore improve LSG depth prediction under limited representation capacity, but the benefit is case dependent and should be established against both global LSG and low-fidelity baselines.

**Keywords:** flood inundation; multi-fidelity surrogate; empirical orthogonal functions; Gaussian process; LSG; hydrodynamic zoning; mode capacity

---

## 1. Introduction

High-resolution two-dimensional hydrodynamic models are widely used to estimate flood extent and water depth because they resolve the spatial structure of inundation directly. Their computational cost, however, remains a practical constraint when many simulations are required for ensemble forecasting, uncertainty analysis, scenario testing, or rapid updating (Teng et al., 2017; Bates, 2022). This limitation has motivated a broad class of surrogate and reduced-order approaches that seek to retain the spatial information provided by hydrodynamic models while reducing the cost of repeated high-fidelity simulations (Bentivoglio et al., 2022).

One such approach is the Low-fidelity, Spatial analysis, and Gaussian Process learning (LSG) framework (Fraehr et al., 2022, 2023a, 2023b, 2024). LSG combines a computationally inexpensive low-fidelity (LF) hydrodynamic simulation with EOF-based dimensionality reduction and Gaussian process (GP) learning. The LF field provides the event-specific hydrodynamic structure, EOF analysis compresses the spatial field into a small number of expansion coefficients, and GP models learn the relationship between LF and high-fidelity (HF) coefficients. The predicted HF coefficients are then used to reconstruct a high-resolution inundation field. Recent work has examined several aspects of this framework, including water-depth prediction, model comparison, and the choice of GP kernel (Fraehr et al., 2023a, 2024; Lu et al., 2025).

A practical feature of EOF reduction is that it uses a deliberately compact representation. The retained number of modes therefore controls how much spatial variability is available to the subsequent mapping. In a global EOF basis, channel cells, frequently inundated floodplain areas, intermittent wetting regions, and shallow fringe cells all contribute to the same sequence of leading modes. This is efficient when a small set of modes describes the domain well, but it can be restrictive when hydrodynamically distinct parts of the floodplain exhibit different spatial patterns.

Spatial localization provides one way to address this problem. Related flood-surrogate studies have used spatial reduction and reconstruction (Zhou et al., 2021, 2022), PCA-based downscaling (Carreau and Guinot, 2021), rotated or localized EOF structures within EOF-GP frameworks (Wang et al., 2025), and regionalized LSG training to reduce local dimensionality-reduction errors in velocity prediction (Tan et al., 2025). These studies show that spatially structured representations can be useful, but they do not directly answer the narrower question considered here. If a zonal model is allowed to retain more modes than a global model, any improvement may reflect greater representation capacity rather than zoning itself. A matched-capacity comparison is needed to isolate the effect of changing the spatial organization of the representation.

A second question is where zoning helps in the LSG pipeline. A zonal model changes both the EOF decomposition and the subsequent coefficient-mapping problem. Better performance could arise because local EOFs reconstruct the HF field more efficiently within each zone, because the LF-to-HF mapping becomes easier when the GP operates on spatially restricted regions, or because the two effects interact. A third question is whether a simple diagnostic derived from training data can indicate when zoning is likely to help. These questions are important because spatial partitioning introduces additional modelling choices and should not be adopted when a global representation is already adequate.

Accordingly, this study evaluates global and zonal LSG-Max under a matched total retained-mode budget. Three public benchmark cases are used for complementary purposes. Carlisle provides the primary event-level comparison, Burnett tests whether the Carlisle behaviour transfers to a larger leave-one-out sample, and Chowilla provides a case in which the LF-to-HF correction itself is problematic under the evaluation protocol used here. The analysis has three objectives: (1) to quantify the effect of hydrodynamic zoning on water-depth accuracy when total EOF capacity is held fixed; (2) to examine whether the observed differences are associated with EOF reconstruction, GP mapping, or their combination; and (3) to test whether residual organization provides a useful first-order indicator of zoning benefit. Rule-based and KMeans partitions are fitted from training events only, and model performance is assessed with area-weighted depth and inundation metrics. Pure-EOF reconstruction, residual-organization measures, and a Carlisle stage-swap analysis are used to interpret the results. The study therefore focuses on what hydrodynamic zoning changes when representation capacity is controlled, rather than presenting regionalization itself as a new concept.

---

## 2. Methodology

### 2.1. Global LSG-Max

The global and zonal models considered here follow the same basic LSG-Max sequence: the LF simulation is represented on the HF grid, the inundation field is reduced using EOFs, GP models map LF expansion coefficients to HF expansion coefficients, and the predicted HF coefficients are used to reconstruct the maximum water depth surface. Figure 1 summarizes the two workflows.

For all analyses, wet cells are identified using a water-depth threshold of 0.03 m. In the global model, the EOF basis is fitted to the wet HF training fields. The LF training fields are projected onto the same spatial modes so that LF and HF expansion coefficients are defined in a common coordinate system. A GP model is then fitted for the coefficient mapping. The reported LSG-Max results use scikit-learn Gaussian process regression with an RBF kernel and white-noise term, three optimizer restarts, a ridge value of \(1\times10^{-6}\), and per-mode standardization. A sparse GPflow/SGPR path is available in the public implementation, but it was not used to generate the results reported here. The LSG-Max variant uses the maximum water depth surface as the single prediction target, whereas LSG-TS (Fraehr et al., 2023a, 2024) uses the full time series. The MaxWD \(R^2\) protocol comparison in Table 5 should therefore be read as a scheme-level sensitivity check rather than a direct LSG-TS reproduction.

![Figure 1. Global and zonal LSG-Max workflows. Both models use the same LF-to-HF sequence, but the zonal model partitions the wet domain before EOF reduction and GP mapping. The total retained-mode budget is matched in the primary comparisons.](../outputs/figures/fig01_workflow.png)

### 2.2. Hydrodynamic zoning and mode allocation

The zonal model differs from the global model only in the spatial organization of the reduced representation. Wet cells are first assigned to hydrodynamic zones, after which separate EOF bases and GP mappings are fitted within each active zone. The reconstructed zonal fields are finally combined on the HF grid.

Two zoning approaches are examined. The Rule partition uses training maximum depth, inundation frequency, and, when residual information is supplied, the mean absolute LF-HF residual. It can produce up to five classes representing deep or near-channel cells, frequently inundated cells, intermittently inundated cells, fringe cells, and an optional residual-error hotspot override. The primary settings use an 80th percentile threshold for the deep and residual-error features, with inundation-frequency thresholds of 0.7 and 0.1 for the frequent and intermittent classes. KMeans zoning uses standardized training features and \(K=4\) in the primary comparisons; \(K=6\) is used only in configuration sweeps. Representative train-only partitions for the Carlisle case are shown in Figure 11.

The zonal model is constrained by a total retained-mode budget \(B\). Mode allocation is performed only over nonempty zones. When \(B\) is at least the number of active zones, each zone receives one mode and the remaining modes are distributed according to within-zone variance. The Carlisle matched-capacity configurations use the requested total budget in the zonal model, with four realized modes at \(B=4\) and six at \(B=6\). Thus, the primary comparison changes the spatial allocation of EOF capacity without increasing the total number of retained modes.

### 2.3. Matched-capacity comparison

The principal comparison is designed to keep the representation budget the same between global and zonal LSG-Max. Event splits, the 0.03 m wet-depth threshold, evaluation fields, and total retained EOF capacity are held fixed. The strict Carlisle comparisons use \(B\in\{4,6\}\). A nominal \(B=8\) global result is retained as a capacity audit because only seven modes were realized; it is therefore shown for sensitivity but is not treated as an equal-\(B\) comparison.

Matched EOF capacity does not imply equal computational cost. The zonal approach fits several smaller EOF and GP problems, whereas the global model fits one basis and one coefficient-mapping stack. The comparison is intended to isolate representation capacity rather than wall-clock time or the number of GP objects.

All fitted quantities are derived from the training events. This includes zoning features, EOF bases, coefficient standardization, and GP models. Test events are introduced only after model fitting for prediction and evaluation. Leakage checks include verification that the official Carlisle training and test indices are disjoint, leave-one-out probes in which corruption of the held-out event leaves the train-only partition and EOF basis unchanged, and code-level checks that zoning features are constructed from training data. These controls are intended to ensure that the spatial partition does not use information from the event being evaluated.

### 2.4. Diagnostics of the zoning effect

Three complementary diagnostics are used to examine why zoning changes prediction skill.

First, an error-organization index (EOI) measures how strongly the magnitude of the LF-HF residual varies between zones for a chosen set of events \(S\). EOI uses a residual-free hydrodynamic rule with up to four active classes (maximum depth and inundation frequency; empty classes are omitted) without the residual-error hotspot override, so the partition is independent of the residual being measured and the index cannot be inflated by construction. For each cell \(i\), define the event-averaged absolute residual

\[
\bar{r}_i(S) = \frac{1}{|S|} \sum_{e \in S} |h_{\mathrm{LF},e,i} - h_{\mathrm{HF},e,i}|,
\]

and let the active mask be the cells that are wet in at least one HF event of \(S\) and exhibit non-zero across-event depth variation. For a given zone partition, EOI is defined as

\[
\mathrm{EOI} = \frac{\mathrm{Var}_k(\bar{r}_k)}{\mathrm{Var}_i(\bar{r}_i)},
\]

where \(\bar{r}_k\) is the mean of \(\bar{r}_i(S)\) over the active cells in zone \(k\), \(\mathrm{Var}_k\) is the unweighted variance across active-zone means (each zone is weighted equally regardless of its cell count), and \(\mathrm{Var}_i\) is the spatial variance of \(\bar{r}_i(S)\) over the active mask. Because the numerator is not a cell-count-weighted between-group variance, EOI is not by construction confined to the unit interval. A high value indicates that residual magnitude is more strongly separated by the chosen zones. EOI is an exploratory diagnostic and is not calibrated as a prospective decision threshold. It is evaluated in two ways: as a retrospective pooled descriptor over all available events for each case (Figure 15), and as a strictly train-only value on each leave-one-out training fold (Figure 16).

Second, a pure-EOF reconstruction experiment removes the GP mapping and reconstructs the HF fields directly using global or zonal EOFs under the same total mode budget. This provides an oracle-like test of whether the zonal basis alone gives a more efficient HF reconstruction. Oracle RMSE is calculated both with and without area weighting. Carlisle and Burnett have uniform cell areas, so the two calculations coincide. Chowilla has variable cell areas and therefore provides an explicit check on whether weighting changes the direction of the comparison. A second-order diagnostic, the zone-global explained-variance gap (ZGG), compares the variance explained by local EOF modes with the variance explained by the same number of restricted global EOF modes at the same local rank. Formally, \(\mathrm{ZGG}_k = V_k^{\mathrm{local}} - V_k^{\mathrm{global}}\), where \(V_k\) is the fraction of within-zone variance explained by the \(k\)-th mode, and the mean ZGG is reported.

Third, a Carlisle stage-swap analysis combines global and zonal representations with global and zonal coefficient-mapping structures. The four diagnostic configurations are denoted GG, ZZ, GZ, and ZG. GG and ZZ correspond to the global and fully zonal constructions. In GZ, leading global modes are restricted to each zone and QR-orthonormalized before zonal GP mapping. In ZG, zonal expansion coefficients are concatenated and passed through a shared global-style GP stack. These hybrid configurations are approximate diagnostic substitutions rather than algebraically exact decompositions of the production pipeline. They are therefore used to assess whether either stage is individually necessary for the Carlisle gain, not to assign a unique causal contribution to EOF localization or GP localization.

---

## 3. Data and Evaluation

### 3.1. Benchmark cases

The analysis uses three cases from the public Fraehr multi-fidelity inundation benchmark (Figshare 24312658). Their roles in the study are summarized in Table 1.

Carlisle, UK, is the primary statistical case and uses all nine available events. The HF model is LISFLOOD-FP and the LF model is HEC-RAS 2D. Chowilla, Australia, uses MIKE 21 fields and is treated as an applicability boundary because the LSG correction is less accurate than the LF field alone under the max-surface protocol used here. The 12-event subset follows the multi-case split used for cross-case LSG comparisons; 29 events are available in the archive.

Burnett River, Australia, uses TUFLOW as the HF model and HEC-RAS 2D as the LF model. Two evaluation protocols are retained because they answer different questions. A 12-event fixed split is used in the three-case comparison, while a separate 30-event leave-one-out analysis is used to test the equal-capacity Rule contrast. The 30-event analysis uses a fixed max-surface extract prepared for this study. Seventy-four events are available in the archive, so the 30-fold result should not be interpreted as a full-archive evaluation.

The max-surface extracts contain 581,061 HF and 5,681 LF cells for Carlisle, 109,914 HF and 1,434 LF cells for Chowilla, and 780,785 HF and 15,256 LF cells for Burnett. The Carlisle and Chowilla HF counts agree with the benchmark descriptions. The native Burnett HF grid is reported at approximately 3.7 million cells, whereas the present analysis uses the 780,785-cell evaluation extract. Geometric cell areas are taken from the Fraehr geometry archives. Carlisle and Burnett use uniform areas of 25 and 400 m², respectively, while Chowilla contains variable cell areas. Synthetic toy grids are not used for any empirical claim, and the licensed Brisbane River data are outside the scope of this study. The max-surface EOI values for Carlisle, Chowilla, and Burnett are 0.057, 0.116, and 0.957, respectively (Table 1).

**Table 1.** Benchmark cases and their roles in the analysis.

| Case | Country | HF hydrodynamic model | Events used / available | HF / LF cells | Role in this study |
|---|---|---|---:|---:|---|
| Carlisle | UK | LISFLOOD-FP | 9 / 9 | 581,061 / 5,681 | Primary matched-capacity case; 9-fold LOOCV |
| Chowilla | Australia | MIKE 21 | 12 / 29 | 109,914 / 1,434 | Applicability boundary; LSG degrades relative to LF-only |
| Burnett River | Australia | TUFLOW | 12 (fixed split); 30 (LOOCV) / 74 | 780,785 / 15,256 | Transfer case; Rule not favoured in 30-fold LOOCV |

### 3.2. Evaluation metrics

Water-depth performance is evaluated primarily using area-weighted RMSE. For cell \(i\), with area \(A_i\), predicted depth \(h_{\mathrm{pred},i}\), and reference depth \(h_{\mathrm{ref},i}\),

\[
\mathrm{RMSE}_{\mathrm{area}}
=
\sqrt{
\frac{\sum_i A_i\left(h_{\mathrm{pred},i}-h_{\mathrm{ref},i}\right)^2}
{\sum_i A_i}
}.
\]

Area-weighted MAE and bias are calculated in the corresponding manner. Inundation extent is evaluated using an area-weighted Critical Success Index (CSI) with the 0.03 m wet-depth threshold. Hits, misses, and false alarms are accumulated by cell area before CSI is calculated. Area weighting is equivalent to cell-count weighting for Carlisle and Burnett because their evaluation cells have uniform area, but it remains necessary for Chowilla.

Depth error and wet-dry skill are reported separately. This distinction is useful for the present problem because the LF field can already reproduce much of the inundation extent while retaining spatially structured errors in water depth. A reduction in RMSE therefore need not be accompanied by a comparable improvement in CSI.

### 3.3. Cross-validation and uncertainty

Carlisle is evaluated primarily by event leave-one-out cross-validation (LOOCV). Each of the nine events is held out once, and zoning, EOF fitting, and GP training are repeated using the remaining events. For each fold, the paired improvement is defined as

\[
\Delta\mathrm{RMSE}
=
\mathrm{RMSE}_{\mathrm{global}}
-
\mathrm{RMSE}_{\mathrm{zonal}},
\]

so positive values favour zoning. A percentile bootstrap confidence interval is calculated for the mean paired difference by resampling the nine event-level differences with replacement. The calculation uses 10,000 bootstrap replicates and seed 42. The same procedure is applied to the \(B=6\) Carlisle result. The official two-fold benchmark split is retained as a separate sensitivity analysis because it contains much less event-level information than the nine-fold LOOCV; for this split, the four held-out event-level differences (two per fold) are resampled with replacement. Because the two events within each fold share a single fitted model, this event-level interval is descriptive rather than an independent-sample confidence interval.

Burnett is evaluated with 30-fold event LOOCV at \(B=4\), with the same 10,000-replicate, seed-42 percentile bootstrap applied to the thirty fold-level paired differences. The 12-event Burnett result shown in the three-case comparison is a separate fixed-split calculation and is not combined with the 30-fold statistics. Representative spatial maps are drawn from held-out events and are used to illustrate error patterns rather than to estimate pooled performance.

---

## 4. Results

### 4.1. Carlisle performance under matched EOF capacity

The clearest zoning effect was observed at Carlisle under the smallest matched mode budget. At \(B=4\), the area-weighted RMSE is 0.1464 m for Global LSG-Max, 0.0964 m for Rule zoning, and 0.1015 m for KMeans zoning. Relative to the global model, Rule zoning reduces RMSE by 34.2%. The LF-only RMSE is 0.1602 m, so the Rule model is also more accurate than the uncorrected LF field under this protocol.

The difference persists at \(B=6\), although both global and zonal RMSE increase. Global RMSE rises from 0.1464 to 0.2588 m, while Rule RMSE rises from 0.0964 to 0.1256 m. At the nominal \(B=8\) setting, Global and Rule RMSE are 0.3527 and 0.1790 m, respectively. The global \(B=8\) calculation realized seven modes, so that point is shown only as a capacity-audit result and is not used as a strict matched-budget comparison (Figure 2). The non-monotonic change in global error with requested mode count is therefore reported as an observed sensitivity of this implementation rather than evidence that additional EOF modes are generally detrimental.

![Figure 2. Carlisle area-weighted depth RMSE as a function of retained-mode budget for Global, Rule, and KMeans LSG-Max. The comparisons at \(B=4\) and \(B=6\) have matched total retained-mode capacity. The nominal \(B=8\) global point realized seven modes and is shown only as a capacity audit.](../outputs/figures/fig03_mode_budget.png)

The corresponding CSI results show a different pattern. LF-only CSI is 0.9145, higher than the LSG values at \(B=4\), and no comparable zonal advantage is evident in inundation extent (Figure 3). The RMSE reduction is therefore primarily a water-depth improvement rather than an improvement in wet-dry classification. The MAE and bias results show the same general separation between the global and zonal depth predictions (Figure 4). A notable feature of the bias curves is that Global LSG-Max at \(B=4\) carries a systematic positive bias of +0.047 m, whereas Rule zonal bias is 0.001 m, effectively unbiased. At \(B=6\), the global bias reverses to \(-0.064\) m, while Rule zonal bias stays modest at +0.018 m. The zonal configuration therefore reduces the systematic depth bias in addition to RMSE.

![Figure 3. Carlisle area-weighted CSI versus retained-mode budget using a 0.03 m wet-depth threshold. As in Figure 2, the nominal \(B=8\) global point realized seven modes.](../outputs/figures/fig09_csi_budget.png)

![Figure 4. Carlisle area-weighted (a) MAE and (b) bias versus retained-mode budget. As in Figure 2, the nominal \(B=8\) global point realized seven modes.](../outputs/figures/fig13_mae_bias.png)

### 4.2. Event-to-event consistency and spatial error patterns

The event-level Carlisle comparison shows that the \(B=4\) result is not produced by a single favourable fold. Rule zoning has lower RMSE than the global model in all nine LOOCV folds. The mean paired difference is 0.0821 m, with a 95% bootstrap confidence interval of [0.0155, 0.1987] m (Figures 5–7). At \(B=6\), seven of nine folds favour Rule zoning; the mean difference is 0.0606 m with a 95% interval of [0.0032, 0.1618] m.

The official two-fold analysis gives a smaller and more uncertain difference. Its mean \(\Delta\mathrm{RMSE}\) is 0.0045 m, with a 95% descriptive event-level bootstrap interval of [-0.0073, 0.0134] m. The descriptive interval includes zero. The two analyses use different resampling structures, so they are best read together: the nine-fold LOOCV shows a fold-consistent Carlisle improvement under the matched-capacity protocol, while the official two-fold calculation indicates that the estimated magnitude is sensitive to the coarser split.

![Figure 5. Carlisle event-level Global and Rule RMSE under \(B=4\) leave-one-out cross-validation.](../outputs/figures/fig08_per_event_bootstrap.png)

![Figure 6. Carlisle held-out RMSE for Global and Rule LSG-Max at \(B=4\). Points below the 1:1 line favour Rule zoning.](../outputs/figures/fig11_loocv_scatter.png)

![Figure 7. 95% bootstrap intervals for the mean paired \(\Delta\mathrm{RMSE}\) in Carlisle and Burnett. Positive values favour zoning. The Carlisle \(B{=}4\) and \(B{=}6\) LOOCV intervals and the Burnett interval are fold-bootstrap confidence intervals (nine, nine, and thirty folds, respectively); the Carlisle official 2-fold interval is a descriptive event-level interval bootstrapped over its four held-out events (two per fold), which share each fitted fold model and therefore do not provide an independent-sample confidence interval.](../outputs/figures/fig12_stat_ci.png)

The largest global error occurs when Carlisle event index 1 (Run2) is held out. On this fold, area-weighted RMSE is 0.233 m for LF-only, 0.695 m for Global LSG-Max, and 0.167 m for Rule zoning. The maximum-depth maps show that the global reconstruction produces broad depth errors across the floodplain, whereas the Rule prediction remains closer to the HF field (Figure 8).

![Figure 8. Carlisle Run2 held-out maximum-depth fields for HF, LF, Global LSG-Max, and Rule zonal LSG-Max under \(B=4\) LOOCV. All panels use a common depth scale capped at the pooled 99th percentile of wet-cell depth for display.](../outputs/figures/figA1_inundation_maps_carlisle_ev1.png)

The wet-dry comparison for the same fold gives CSI values of 0.591 for Global and 0.816 for Rule. Most of the difference is associated with fewer false alarms in the zonal prediction (Figure 9). Residual maps show a broad positive depth error in the global prediction that is substantially reduced by Rule zoning over much of the wet floodplain (Figure 10). The train-only zone map and the cell-level observed-predicted comparison provide complementary views of the same fold (Figures 11 and 12).

![Figure 9. Carlisle Run2 hit, miss, and false-alarm maps for Global and Rule predictions using the 0.03 m wet-depth threshold.](../outputs/figures/figA2_csi_hitmiss_carlisle_ev1.png)

![Figure 10. Carlisle Run2 residual fields for Global and Rule predictions (a, b) and the change in absolute error \(|G-HF| - |R-HF|\) (c), where positive values indicate that the Rule absolute error is smaller; colour limits are symmetric and capped at the 98th percentile of wet-cell absolute residual magnitude.](../outputs/figures/figA3_residuals_carlisle_ev1.png)

![Figure 11. Train-only Rule zones for the Carlisle Run2 fold and their spatial relation to the HF depth field.](../outputs/figures/figA4_zones_overlay_carlisle_ev1.png)

![Figure 12. Wet-cell observed and predicted depths for Global and Rule LSG-Max on the held-out Carlisle Run2 event. Points are a seed-42 random subsample of the HF wet cells (depth \(\ge 0.03\) m, at most 40,000); the RMSE quoted in each panel title is the canonical LOOCV all-cell area-weighted value, not a statistic of the displayed subsample.](../outputs/figures/figA5_obs_vs_pred_carlisle_ev1.png)

A less extreme Carlisle fold, event 0 (Run1), gives RMSE values of approximately 0.074, 0.072, and 0.057 m for LF-only, Global, and Rule, respectively. The spatial differences are correspondingly smaller. The same qualitative map checks were also applied to the transfer cases: Burnett event 0 shows little separation between Global and Rule, while Chowilla event 0 shows both LSG predictions farther from HF than the LF field alone.

### 4.3. Transfer across benchmark cases

The Carlisle result does not transfer uniformly to the other cases. In Burnett 30-fold LOOCV at \(B=4\), mean RMSE is 1.7192 m for Global and 1.8164 m for Rule, giving a mean \(\Delta\mathrm{RMSE}\) of -0.0972 m. Rule improves thirteen of the 30 folds, and the paired difference is not significant (Figures 7 and 13). Thus, the Burnett leave-one-out analysis provides a direct case in which the same matched-capacity Rule approach does not improve prediction.

![Figure 13. Burnett 30-fold LOOCV RMSE for Global and Rule LSG-Max at \(B=4\).](../outputs/figures/fig10_burnett_loocv.png)

The fixed-split three-case comparison gives a related but distinct view (Table 2 and Figure 14). At Carlisle, Rule is more accurate than both Global and LF-only. At Burnett, Global and Rule are nearly identical on the 12-event fixed split. At Chowilla, LF-only RMSE is 0.3926 m, whereas Global and Rule RMSE are 2.5606 and 2.5614 m. Under this protocol, the main issue at Chowilla is therefore not the choice between global and zonal EOF representations; it is the deterioration introduced by the LSG correction relative to the LF field.

**Table 2.** Area-weighted depth RMSE (m) for the three-case \(B=4\) comparison.

| Case | LF-only | Global \(B=4\) | Rule \(B=4\) | Observed pattern |
|---|---:|---:|---:|---|
| Carlisle | 0.1602 | 0.1464 | 0.0964 | Rule < Global < LF |
| Chowilla | 0.3926 | 2.5606 | 2.5614 | LF is most accurate; both LSG variants degrade |
| Burnett (12-event fixed split) | 2.2323 | 1.6117 | 1.6122 | Global and Rule are nearly identical |

![Figure 14. Three-case area-weighted RMSE at \(B=4\) for LF-only, Global LSG-Max, and Rule zonal LSG-Max. The Burnett values use the 12-event fixed split and are separate from the 30-fold LOOCV analysis in Figure 13. The inset magnifies the Carlisle bars to resolve the smaller between-model differences.](../outputs/figures/fig04_three_case.png)

### 4.4. Residual organization and stage diagnostics

The max-surface EOI values are 0.057 for Carlisle, 0.116 for Chowilla, and 0.957 for Burnett (Figure 15). These pooled values are retrospective descriptors computed over all available events for each case (Carlisle \(n=9\), Burnett \(n=30\), Chowilla \(n=29\)); the fold-level values in Figure 16 are the strictly train-only counterparts. This cross-case comparison is descriptive rather than protocol-matched: the Chowilla pooled EOI uses all 29 available events, whereas its performance comparison (Figure 14, Table 2) uses the 12-event fixed subset. The observed EOI ordering does not match the zoning benefit. Carlisle has the lowest EOI and the clearest matched-capacity improvement, whereas Burnett has the highest EOI and no Rule advantage in the 30-fold analysis. The fold-level comparison in Figure 16 gives the same qualitative result. EOI therefore does not provide a useful first-order ranking of zoning benefit for these cases. This finding is limited to the diagnostic tested here and does not rule out other training-data indicators.

![Figure 15. Max-surface error-organization index (EOI) for Carlisle, Burnett, and Chowilla. EOI is the ratio of the unweighted variance across zone means of the event-averaged absolute-residual field \(\bar{r}_i(S)\) to its spatial variance over active cells, and is not by construction bounded by [0,1]. The pooled values are computed over all available events (Carlisle \(n=9\), Burnett \(n=30\), Chowilla \(n=29\)) on the residual-free hydrodynamic rule (up to four active classes).](../outputs/figures/fig14_eoi.png)

![Figure 16. In-fold train-only EOI (residual-free hydrodynamic rule, up to four active classes) and matched-capacity zoning \(\Delta\mathrm{RMSE}\) for Carlisle and Burnett folds. Positive \(\Delta\mathrm{RMSE}\) favours zoning.](../outputs/figures/fig15_eoi_vs_delta.png)

The pure-EOF analysis gives a more nuanced result than the ZGG values alone would suggest. ZGG is positive for all three cases (Table 3), indicating that local modes capture more within-zone variance than the same number of restricted global modes. However, the equal-budget pure-EOF oracle gives negative \(\Delta\mathrm{RMSE}\) for each case, meaning that the zonal EOF reconstruction is not more accurate than the global reconstruction before GP mapping. This apparent paradox arises because ZGG measures within-zone variance explained, whereas the oracle RMSE depends on the total reconstruction error summed over all zones. The zonal oracle loses variance that is shared across zones, which the global oracle captures in its leading modes. For Chowilla, the area-weighted oracle difference remains negative (-0.0543 m compared with -0.0657 m without weighting). Carlisle and Burnett have uniform cell areas, so weighting leaves their oracle differences unchanged.

**Table 3.** Equal-budget pure-EOF oracle reconstruction comparison. ZGG is the zone-global explained-variance gap (positive values indicate that local modes capture more within-zone variance). Oracle \(\Delta\mathrm{RMSE}\) is positive if the zonal EOF reconstruction is more accurate than the global reconstruction under the same total mode budget. Negative values indicate that the zonal EOF basis alone does not give a more efficient reconstruction of the HF field.

| Case | Mean ZGG | Oracle \(\Delta\mathrm{RMSE}\) (uniform) | Oracle \(\Delta\mathrm{RMSE}\) (area-weighted) |
|---|---:|---:|---:|
| Carlisle | 0.0479 | -0.0761 | -0.0761 |
| Burnett | 0.0287 | -0.1983 | -0.1983 |
| Chowilla | 0.1071 | -0.0657 | -0.0543 |

The Carlisle stage-swap analysis further narrows the interpretation (Table 4). Mean LOOCV RMSE is approximately 0.180 m for GG, 0.098 m for ZZ, 0.098 m for GZ, and 0.101 m for ZG. Both hybrid configurations are therefore close to the fully zonal result and substantially below GG. Because GZ and ZG are approximate substitutions, these values do not identify a unique causal stage. They do show that the Carlisle improvement is not dependent on only one of the two localized components. Taken together with the pure-EOF result, the stage-swap analysis points to the combined representation-mapping problem rather than improved HF truncation alone.

**Table 4.** Carlisle stage-swap LOOCV RMSE (m) at \(B=4\). GG: global EOF + global GP; ZZ: zonal EOF + zonal GP; GZ: restricted global EOF + zonal GP; ZG: zonal EOF + global-style GP.

| Configuration | Mean LOOCV RMSE (m) |
|---|---|
| GG (Global LSG-Max) | 0.180 |
| ZZ (Rule zonal LSG-Max) | 0.098 |
| GZ (global EOF + zonal GP) | 0.098 |
| ZG (zonal EOF + global GP) | 0.101 |

### 4.5. Secondary sensitivity analyses

Several secondary analyses were used to check whether the primary Carlisle result depends on a single formulation. Under the official nine-fold MaxWD \(R^2\) protocol, Rule LSG-Max reaches 0.988, compared with a published LSG-TS value of 0.990 and a Global Max value of approximately 0.915 (Table 5). This is a protocol comparison rather than a local head-to-head reproduction of LSG-TS.

**Table 5.** Official nine-fold MaxWD \(R^2\) protocol comparison. Published values from Fraehr et al. (2024, Table 2); this-work values computed under the same official protocol but using LSG-Max rather than LSG-TS.

| Model | MaxWD \(R^2\) |
|---|---|
| LSG-TS (published) | 0.990 |
| Kabir-1dCNN (published) | 0.984 |
| LSTM-SRR (published) | 0.690 |
| GP-EOF (published) | 0.974 |
| LSTM-EOF (published) | 0.971 |
| This work–Rule LSG-Max | 0.988 |
| This work–Global LSG-Max | 0.915 |
| This work–KMeans LSG-Max | 0.976 |

LF coarsening and channel-distance zoning were also examined as secondary robustness probes. The coarsening experiment retains the separation between Global and Rule over the tested LF grid factors (Figure 17). Adding channel-distance information changes the zonal result only modestly relative to the primary Rule partition (Table 6). These analyses support the interpretation of the Carlisle result as a spatial-representation effect under the tested settings, but they are not used to extend the main claim beyond the matched-capacity comparisons.

![Figure 17. Carlisle LF-grid coarsening sensitivity for LF-only, Global LSG, and Rule zonal LSG, evaluated on the random 7/2 train-test split (seed 42). The factor-1 point is an independently refitted uncoarsened baseline.](../outputs/figures/fig17_lf_degradation.png)

**Table 6.** Carlisle channel-distance zoning sensitivity at \(B=4\). Rule+channel dist. and KMeans+dist. include distance to the main channel as an additional zoning feature. The Rule and Global values are the primary \(B=4\) matched-capacity results.

| Configuration | Area-weighted RMSE (m) |
|---|---|
| Global LSG-Max | 0.1464 |
| Rule zoning | 0.0964 |
| Rule + channel distance | 0.0937 |
| Channel-distance only | 0.1118 |
| KMeans + distance | 0.1027 |

---

## 5. Discussion

### 5.1. Effect of zoning under matched representation capacity

The main result is that hydrodynamic zoning can materially change LSG-Max depth prediction even when the total retained EOF capacity is unchanged. At Carlisle, the difference is largest at \(B=4\), where Rule zoning reduces area-weighted RMSE from 0.1464 to 0.0964 m. The improvement occurs in every one of the nine leave-one-out folds and is also evident in the spatial error maps. Because the total number of retained modes is matched, this result cannot be attributed simply to allowing the zonal model a larger reduced space.

The Carlisle improvement is, however, concentrated in a single fold. Over half of the aggregate \(\Delta\mathrm{RMSE}\) at \(B=4\) is contributed by the held-out Run2 event, where the global model produces a large error (0.695 m) and Rule zoning corrects it to 0.167 m. Removing Run2 reduces the mean improvement from 0.082 to approximately 0.026 m, a smaller but still fold-consistent effect. Run2 is the second-largest inflow event in the Carlisle record, and its spatial pattern of inundation differs from the events used for training. A global basis with only four modes may therefore extrapolate poorly to this atypical event, whereas the zonal basis, by localising the correction, is more robust to the mismatch. This interpretation is consistent with the observation that the other eight folds, which involve events closer to the training distribution, show a smaller but consistent zonal advantage.

The water-depth and extent metrics also show that the benefit is specific to what is being predicted. LF-only CSI remains higher than the LSG values at \(B=4\), whereas Rule zoning substantially reduces depth RMSE. The LF field therefore already contains useful information on where inundation occurs, and the zonal representation mainly changes how depth structure is corrected. This distinction is important when evaluating flood surrogates because a model can reproduce the wet footprint reasonably well while still containing large spatial errors in depth.

The official two-fold sensitivity analysis is more conservative than the nine-fold LOOCV. Its descriptive event-level bootstrap interval includes zero, and the estimated mean difference is much smaller. This does not provide independent confirmation of the LOOCV effect. Rather, it shows that the estimated Carlisle advantage depends on how the small event set is partitioned. The evidence is therefore strongest for a fold-consistent improvement under the event-level LOOCV design, with the two-fold result defining an important uncertainty in its magnitude.

The behaviour across the mode-budget sweep also deserves caution. Global RMSE increases as the requested mode count is raised from four to six and then to the nominal eight-mode setting. Rule RMSE also increases, although it remains below Global. These results show that adding retained modes did not recover the global model under the present configuration. They do not establish a general inverse relationship between EOF rank and prediction accuracy, because GP estimation, event sampling, and realized mode counts also change the fitted problem. The relevant finding for this study is narrower: under the matched settings at \(B=4\) and \(B=6\), the spatial organization of a fixed mode budget affects the resulting LSG prediction.

### 5.2. Interpretation of the zonal benefit

The diagnostic analyses provide two constraints on the interpretation. First, the pure-EOF experiment indicates that the Carlisle gain is not explained by a better low-rank reconstruction of the HF field. Under equal total rank, the zonal EOF oracle is less accurate than the global oracle. Although ZGG is positive for all three cases, reflecting that local modes capture more within-zone variance than the same number of restricted global modes, the zonal oracle loses variance shared across zones that the global oracle captures in its leading modes. If the benefit were simply a consequence of representing HF inundation more efficiently within each zone, the opposite would be expected.

Second, the stage-swap results show that the two localized components cannot be cleanly separated as independent causes. Both GZ and ZG recover most of the difference between GG and ZZ. One approximation localizes the GP mapping while using restricted global coordinates, and the other retains zonal coordinates within a shared mapping structure. Their similar performance suggests that localization changes the geometry of the coefficient-prediction problem in a way that is not captured by EOF truncation error alone.

This interpretation is consistent with the structure of LSG. EOF reduction and coefficient mapping are not independent operations from the perspective of prediction error. The chosen basis determines the coefficients that the GP must learn, while the learned mapping determines which parts of that reduced representation can be reconstructed accurately for an unseen event. Dividing the domain can change the variance structure, coefficient ranges, and spatial coupling presented to the GP even when the number of retained coefficients is fixed. The current stage-swap is not sufficiently exact to assign the improvement to one of these mechanisms, but it provides evidence that a single-stage explanation is incomplete.

This finding also clarifies the relation to previous localized flood-surrogate work. Tan et al. (2025) used regionalized LSG training to address local dimensionality-reduction error, while Wang et al. (2025) used localized EOF structure within an EOF-GP flood-surrogate framework. The present analysis does not claim regionalization itself as a methodological novelty. Its contribution is the capacity-controlled comparison and the diagnostic evidence that, at Carlisle, the effect of localization persists without additional retained modes and cannot be reduced to better HF EOF reconstruction alone.

### 5.3. Transferability and applicability boundaries

The Burnett and Chowilla results show why the Carlisle finding should not be generalized into a default zoning rule. Burnett provides the most direct transfer test. Its 30-fold LOOCV does not favour Rule zoning, despite a much larger EOI than Carlisle. The fixed 12-event comparison likewise shows almost identical Global and Rule errors. In this case, partitioning the representation does not provide a measurable advantage under the tested \(B=4\) configuration.

Chowilla represents a different limitation. Both Global and Rule LSG-Max are substantially less accurate than the LF field under the max-surface protocol used here. Once the LF-to-HF correction degrades the prediction, the distinction between global and zonal representation becomes secondary. This suggests a two-stage practical assessment for similar applications. The first question is whether the LSG correction improves on the LF baseline for the quantity and protocol of interest. Only after that condition is satisfied does it become useful to ask whether the reduced representation should be global or zonal.

The EOI analysis does not resolve this selection problem. Burnett has the strongest residual organization according to the tested index but no zonal benefit, while Carlisle shows the clearest improvement at the lowest EOI. EOI therefore should not be used as a threshold for deciding whether to zone a new case. A useful selector would need to be defined from training data and then evaluated prospectively on cases that were not used to formulate the rule. That validation is outside the present study.

For current applications, the results support a comparative rather than prescriptive use of zoning. A compact global LSG model remains the natural baseline. Zonal LSG can then be evaluated under the same total EOF capacity, alongside the LF-only prediction, when depth errors suggest that a single spatial basis may be restrictive. This approach keeps the additional modelling choice visible and avoids interpreting a zonal improvement as evidence that localization will transfer to every floodplain.

### 5.4. Limitations and future work

Several limitations define the scope of the results. The reported production calculations use LSG-Max with scikit-learn Gaussian process regression. A sparse GPflow/SGPR implementation exists in the code base, but backend equivalence has not been evaluated. The conclusions therefore apply to the reported implementation and should not be assumed to transfer unchanged to a sparse-GP backend or to a zonal LSG-TS formulation.

The evidence for a positive zoning effect is also concentrated in one case. Carlisle is the only benchmark in this study with a clear improvement under matched-capacity LOOCV. The Burnett analysis covers 30 of the 74 available events and evaluates Rule zoning rather than a full KMeans LOOCV extension. The 12-event Burnett fixed split is retained only for the cross-case comparison. A full-archive analysis would provide a stronger estimate of transferability. Brisbane cannot be used because the licensed data are unavailable.

There are additional data-provenance constraints. The Chowilla archive checksum and datum provenance remain unresolved in the present workflow. These issues do not alter the reported numerical calculations, but they limit the strength of cross-study reproducibility claims and should be resolved before treating Chowilla as a definitive benchmark of LSG failure.

Finally, the diagnostics used here are retrospective. EOI was tested because it provides a simple measure of residual organization, and the result is useful in showing that this particular indicator does not explain the observed case ordering. It is not a validated decision rule. A stronger next step would be to define a selector before examining the test case, specify success and failure criteria in advance, and evaluate the selector on an unseen floodplain. The same prospective design could also be used to compare alternative zoning variables, sparse-GP backends, and larger event archives without changing the matched-capacity principle.

---

## 6. Conclusion

This study examined whether hydrodynamic zoning changes LSG-Max flood-depth prediction when the total retained EOF capacity is held fixed. The primary Carlisle result shows that it can. At \(B=4\), Rule zoning reduces area-weighted RMSE from 0.1464 to 0.0964 m and improves all nine leave-one-out folds. A similar, smaller improvement is obtained at \(B=6\). Increasing the requested global mode count does not recover the zonal performance in the Carlisle sweep; the nominal \(B=8\) global calculation realizes seven modes and is therefore retained only as a capacity-audit sensitivity. The official two-fold analysis is less conclusive than the event-level LOOCV because its descriptive event-level bootstrap interval includes zero.

The Carlisle result does not transfer uniformly across the benchmark. Burnett 30-fold LOOCV does not favour Rule zoning, and the 12-event fixed split gives almost identical Global and Rule errors. At Chowilla, both LSG variants are less accurate than the LF field under the max-surface evaluation used here. These cases distinguish two limitations: zoning may provide little benefit even when LSG itself is useful, as at Burnett, and the LF-to-HF correction may fail before the choice of spatial representation becomes relevant, as at Chowilla.

The diagnostic experiments further show that the Carlisle gain is not explained by improved EOF truncation alone. Equal-budget pure-EOF reconstruction does not favour the zonal basis, while the approximate stage-swap indicates that localising either the coefficient representation or the GP mapping recovers most of the fully zonal improvement. The tested EOI also fails to rank the cases correctly. The available evidence therefore points to an interaction between representation and mapping, but it does not identify a unique causal stage or a transferable training-data selector.

For practical applications, zonal LSG is best treated as an alternative compact representation that must be evaluated rather than assumed to be superior. A useful comparison includes the LF-only field, global LSG, and zonal LSG under the same retained-mode budget. Extending this analysis to the full Burnett archive, alternative GP backends, and prospectively defined zoning selectors would provide a stronger basis for deciding when spatial localization is warranted.

---

## Data and code availability

The hydrodynamic cases are from the public Fraehr multi-fidelity inundation benchmark (Figshare 24312658). Analysis code, evaluation artefacts, and figure sources are available at https://github.com/Coucou2016/202606-JOH-zonal-LSG. Raw hydrodynamic archives are excluded from the public repository. Hyperparameter defaults and random seeds are listed in the Supplementary Information.

---

## References

1. Fraehr, N., Wang, Q. J., Wu, W., & Nathan, R. (2022). Upskilling low-fidelity hydrodynamic models of flood inundation through spatial analysis and Gaussian Process learning. *Water Resources Research*, 58, e2022WR032248. https://doi.org/10.1029/2022WR032248
2. Fraehr, N., Wang, Q. J., Wu, W., & Nathan, R. (2023a). Development of a fast and accurate hybrid model for floodplain inundation simulations. *Water Resources Research*, 59, e2022WR033836. https://doi.org/10.1029/2022WR033836
3. Fraehr, N., Wang, Q. J., Wu, W., & Nathan, R. (2024). Assessment of surrogate models for flood inundation: The physics-guided LSG model vs. state-of-the-art machine learning models. *Water Research*, 252, 121202. https://doi.org/10.1016/j.watres.2024.121202
4. Bentivoglio, R., Isufi, E., Jonkman, S. N., & Taormina, R. (2022). Deep learning methods for flood mapping: a review of existing applications and future research directions. *Hydrology and Earth System Sciences*, 26, 4345–4378. https://doi.org/10.5194/hess-26-4345-2022
5. Teng, J., Jakeman, A. J., Vaze, J., Croke, B. F. W., Dutta, D., & Kim, S. (2017). Flood inundation modelling: A review of methods, recent advances and uncertainty analysis. *Environmental Modelling & Software*, 90, 201–216. https://doi.org/10.1016/j.envsoft.2017.01.006
6. Bates, P. D. (2022). Flood inundation prediction. *Annual Review of Fluid Mechanics*, 54, 287–315. https://doi.org/10.1146/annurev-fluid-030121-113138
7. Lu, J., Wang, Q. J., Fraehr, N., Xiang, X., & Wu, X. (2025). Choice of Gaussian Process kernels used in LSG models for flood inundation predictions. *Journal of Hydrology*, 655, 132949. https://doi.org/10.1016/j.jhydrol.2025.132949
8. Carreau, J., & Guinot, V. (2021). A PCA spatial pattern based artificial neural network downscaling model for urban flood hazard assessment. *Advances in Water Resources*, 147, 103821. https://doi.org/10.1016/j.advwatres.2020.103821
9. Zhou, Y., Wu, W., Nathan, R., & Wang, Q. J. (2021). A rapid flood inundation modelling framework using deep learning with spatial reduction and reconstruction. *Environmental Modelling & Software*, 143, 105112. https://doi.org/10.1016/j.envsoft.2021.105112
10. Zhou, Y., Wu, W., Nathan, R., & Wang, Q. J. (2022). Deep learning-based rapid flood inundation modeling for flat floodplains with complex flow paths. *Water Resources Research*, 58, e2022WR033214. https://doi.org/10.1029/2022WR033214
11. Tan, Z., Xu, D., Taraphdar, S., Ma, J., Bisht, G., & Leung, L. R. (2025). An efficient hybrid downscaling framework to estimate high-resolution river hydrodynamics. *Hydrology and Earth System Sciences*, 29, 3833–3852. https://doi.org/10.5194/hess-29-3833-2025
12. Wang, R., Lian, J., Yuan, X., Tian, F., Li, K., & Liu, Z. (2025). Rapid simulation of floods by considering the spatial and temporal characteristics of inundation. *International Journal of Disaster Risk Science*, 16, 481–495. https://doi.org/10.1007/s13753-025-00642-5
13. Fraehr, N., Wang, Q. J., Wu, W., & Nathan, R. (2023b). Supercharging hydrodynamic inundation models for instant flood insight. *Nature Water*, 1, 835–843. https://doi.org/10.1038/s44221-023-00132-2

