# Figure ↔ Code Correspondence Audit Pack (for ChatGPT visual + code review)

**Repo:** https://github.com/Coucou2016/202606-JOH-zonal-LSG
**Commit under review:** `dd010a0`
**Manuscript:** https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/paper/manuscript.md

This pack pairs every manuscript figure with (a) the figure image, (b) the exact
generating code, and (c) the underlying data values, so you can do a **visual
review** and a **code review** simultaneously. Please check each figure for:

1. **Internal consistency** — does the figure match the caption and the numbers
   quoted in the manuscript text?
2. **Visual quality** — axis labels, legends, font sizes, color maps, panel
   layout, overlapping text, misleading axes, truncated labels.
3. **Correctness of the code** — does the code actually plot what the caption
   claims? Any indexing, unit, or sign errors?
4. **Statistical presentation** — confidence intervals, error bars, 1:1 lines,
   baseline lines drawn correctly?

Figures are embedded below as raw GitHub image URLs (ChatGPT can render these
inline). The generating code lives in `scripts/97_scienceplots_figures.py`
(statistical figures) and `scripts/97b_spatial_maps.py` (spatial maps).

---

## Figure 1 — Workflow schematic

**Caption:** Global and zonal LSG-Max workflows. Both models use the same
LF-to-HF sequence, but the zonal model partitions the wet domain before EOF
reduction and GP mapping. The total retained-mode budget is matched in the
primary comparisons.

![Figure 1](https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/fig01_workflow.png)

**Generating code** (`fig01_workflow` in `97_scienceplots_figures.py`):

```python
def fig01_workflow():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(W2, 3.15))
    steps_g = ["LF interpolate to HF grid", "Global EOF",
               "GP: LF coeffs → HF coeffs", "Reconstruct max. inundation"]
    steps_z = ["Hydrodynamic zoning (train only)", "Zonal EOF",
               "Zonal GP mapping", "Stitch zonal max. surfaces"]
    yg = [0.82, 0.58, 0.34, 0.10]
    for ax, title, steps, fc, ec in (
        (ax1, "Global LSG-Max (baseline)", steps_g, "#d9e8f5", "#2c5d8c"),
        (ax2, "Zonal LSG-Max (this work)", steps_z, "#dcefe4", "#1e7a4a"),
    ):
        ...
```

**Data:** none (schematic).

---

## Figure 2 — Carlisle RMSE vs mode budget

**Caption:** Carlisle area-weighted depth RMSE as a function of retained-mode
budget for Global, Rule, and KMeans LSG-Max. The comparisons at \(B=4\) and
\(B=6\) have matched total retained-mode capacity. The nominal \(B=8\) global
point realized seven modes and is shown only as a capacity audit.

![Figure 2](https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/fig03_mode_budget.png)

**Generating code** (`fig03_mode_budget`):

```python
def fig03_mode_budget(cb: dict):
    Bs = [4, 6, 8]
    g = [cb["budgets"][str(b)]["global"]["rmse_area"] for b in Bs]
    r = [cb["budgets"][str(b)]["rule"]["rmse_area"] for b in Bs]
    k = [cb["budgets"][str(b)]["kmeans"]["rmse_area"] for b in Bs]
    lf = cb["lf_only"]["rmse_area"]
    fig, ax = plt.subplots(figsize=(W1, 2.55))
    ax.plot(Bs, g, "o-", label="Global", markersize=4)
    ax.plot(Bs, r, "s--", label="Rule zonal", markersize=4)
    ax.plot(Bs, k, "^:", label="KMeans zonal", markersize=4)
    ax.axhline(lf, color="0.45", ls="-.", lw=0.8, label="LF only")
    ax.set_xlabel("Mode budget $B$")
    ax.set_ylabel("Area-weighted RMSE (m)")
    ax.set_xticks(Bs)
    ax.legend(frameon=False, fontsize=7)
```

**Data** (`budget_sweep_true_equal.json`):
| B | Global | Rule | KMeans | LF-only |
|---|---|---|---|---|
| 4 | 0.1464 | 0.0964 | 0.1015 | 0.1602 |
| 6 | 0.2588 | 0.1256 | 0.1367 | — |
| 8 | 0.3527 (7 modes) | 0.1790 | 0.2980 | — |

---

## Figure 3 — Carlisle CSI vs mode budget

**Caption:** Carlisle area-weighted CSI versus retained-mode budget using a
0.03 m wet-depth threshold.

![Figure 3](https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/fig09_csi_budget.png)

**Code:** second half of `fig03_mode_budget` (same as Fig 2 but `csi_area`).

**Data:** LF-only CSI = 0.9145; at B=4 Global 0.884, Rule 0.884, KMeans 0.881.

---

## Figure 4 — Carlisle MAE and bias vs mode budget

**Caption:** Carlisle area-weighted MAE and bias versus retained-mode budget.

![Figure 4](https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/fig13_mae_bias.png)

**Generating code** (`fig_mae_bias`):

```python
def fig_mae_bias(cb: dict):
    Bs = [4, 6, 8]
    fig, axes = plt.subplots(1, 2, figsize=(W2, 2.55))
    for ax, key, ylab in (
        (axes[0], "mae_area", "Area-weighted MAE (m)"),
        (axes[1], "bias_area", "Area-weighted bias (m)"),
    ):
        ax.plot(Bs, [cb["budgets"][str(b)]["global"][key] for b in Bs], "o-", label="Global")
        ax.plot(Bs, [cb["budgets"][str(b)]["rule"][key] for b in Bs], "s--", label="Rule zonal")
        ax.plot(Bs, [cb["budgets"][str(b)]["kmeans"][key] for b in Bs], "^:", label="KMeans")
        ax.axhline(cb["lf_only"][key], color="0.45", ls="-.", lw=0.8, label="LF only")
        ax.set_xlabel("Mode budget $B$"); ax.set_ylabel(ylab); ax.set_xticks(Bs)
        if key == "bias_area":
            ax.axhline(0.0, color="0.6", lw=0.5)
    axes[0].legend(frameon=False, fontsize=6)
```

**Data (bias, m):** B=4 Global +0.047, Rule +0.001; B=6 Global −0.064, Rule +0.018.

---

## Figure 5 — Carlisle per-event RMSE (B=4 LOOCV)

**Caption:** Carlisle event-level Global and Rule RMSE under \(B=4\) leave-one-out
cross-validation.

![Figure 5](https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/fig08_per_event_bootstrap.png)

**Code** (`fig_carlisle_loocv`, first figure): plots `global_rmse` vs `zonal_rmse`
against held-out event index for `B=4`.

---

## Figure 6 — Carlisle LOOCV scatter (Global vs Rule)

**Caption:** Carlisle held-out RMSE for Global and Rule LSG-Max at \(B=4\). Points
below the 1:1 line favour Rule zoning.

![Figure 6](https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/fig11_loocv_scatter.png)

**Code** (`fig_carlisle_loocv`, second figure):

```python
fig, ax = plt.subplots(figsize=(W1, 2.7))
ax.plot([0, max(g)], [0, max(g)], color="0.5", lw=0.7, ls="--", label="1:1")
ax.scatter(g, z, s=22, zorder=3)
ax.set_xlabel("Global RMSE (m)"); ax.set_ylabel("Rule zonal RMSE (m)")
ax.set_aspect("equal", adjustable="box")
```

---

## Figure 7 — Bootstrap CI for mean ΔRMSE

**Caption:** Bootstrap confidence intervals for the mean paired \(\Delta\mathrm{RMSE}\)
in Carlisle and Burnett. Positive values favour zoning.

![Figure 7](https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/fig12_stat_ci.png)

**Data:** Carlisle B=4 mean 0.0821 CI [0.0155, 0.1987]; B=6 mean 0.0606 CI
[0.0032, 0.1618]; official 2-fold mean 0.0045 CI [−0.0073, 0.0134]; Burnett
30-fold mean −0.0781 CI [−0.2116, 0.0405].

---

## Figure 8 — Carlisle Run2 maximum-depth maps

**Caption:** Carlisle Run2 held-out maximum-depth fields for HF, LF, Global
LSG-Max, and Rule zonal LSG-Max under \(B=4\) LOOCV. All panels use a common
depth scale.

![Figure 8](https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/figA1_inundation_maps_carlisle_ev1.png)

**Code** (`fig_inundation` in `97b_spatial_maps.py`): 2×2 panels — (a) HF truth,
(b) LF input, (c) Global LSG-Max, (d) Rule zonal; shared `Blues` colormap,
shared `vmax = 99th percentile of wet depth`.

---

## Figure 9 — Carlisle Run2 hit/miss/FA maps

**Caption:** Carlisle Run2 hit, miss, and false-alarm maps for Global and Rule
predictions using the 0.03 m wet-depth threshold.

![Figure 9](https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/figA2_csi_hitmiss_carlisle_ev1.png)

**Code** (`fig_csi_spatial`): classes 0=correct dry (grey), 1=hit (green),
2=miss (blue), 3=false alarm (red). CSI Global=0.591, Rule=0.816.

---

## Figure 10 — Carlisle Run2 residual fields

**Caption:** Carlisle Run2 residual fields for Global and Rule predictions and the
corresponding change in absolute error.

![Figure 10](https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/figA3_residuals_carlisle_ev1.png)

**Code** (`fig_residuals`): (a) Global−HF, (b) Rule−HF, (c) |G−HF|−|R−HF|;
symmetric limits from 98th percentile of wet residuals (lim = 1.54 m).

---

## Figure 11 — Carlisle Run2 train-only zones

**Caption:** Train-only Rule zones for the Carlisle Run2 fold and their spatial
relation to the HF depth field.

![Figure 11](https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/figA4_zones_overlay_carlisle_ev1.png)

**Code** (`fig_zones_overlay`): (a) zone-id map, (b) HF depth + zone contours.

---

## Figure 12 — Carlisle Run2 obs-vs-pred scatter

**Caption:** Wet-cell observed and predicted depths for Global and Rule LSG-Max on
the held-out Carlisle Run2 event.

![Figure 12](https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/figA5_obs_vs_pred_carlisle_ev1.png)

**Code** (`fig_obs_pred_scatter`): subsample ≤40k wet cells; color-coded Global
(#2c7bb6) vs Rule (#d7191c); 1:1 reference line; RMSE annotated in title.

---

## Figure 13 — Burnett 30-fold LOOCV RMSE

**Caption:** Burnett 30-fold LOOCV RMSE for Global and Rule LSG-Max at \(B=4\).

![Figure 13](https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/fig10_burnett_loocv.png)

**Data:** mean Global 1.7479, mean Rule 1.8260, Δ = −0.0781, 6/30 folds improved.

---

## Figure 14 — Three-case area-weighted RMSE

**Caption:** Three-case area-weighted RMSE at \(B=4\) for LF-only, Global LSG-Max,
and Rule zonal LSG-Max. The Burnett values use the 12-event fixed split and are
separate from the 30-fold LOOCV analysis in Figure 13.

![Figure 14](https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/fig04_three_case.png)

**Data:** Carlisle LF 0.1602/Global 0.1464/Rule 0.0964; Chowilla 0.3926/2.5606/2.5614;
Burnett 2.2323/1.6120/1.6122.

---

## Figure 15 — Max-surface EOI

**Caption:** Max-surface error-organization index for Carlisle, Burnett, and Chowilla.

![Figure 15](https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/fig14_eoi.png)

**Data:** Carlisle 0.057, Chowilla 0.116, Burnett 0.957. Color thresholds: >0.30
green "High", 0.15–0.30 amber, <0.15 red.

---

## Figure 16 — EOI vs ΔRMSE (per fold)

**Caption:** In-fold training EOI and matched-capacity zoning \(\Delta\mathrm{RMSE}\)
for Carlisle and Burnett folds. Positive \(\Delta\mathrm{RMSE}\) favours zoning.

![Figure 16](https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/fig15_eoi_vs_delta.png)

**Data:** Carlisle corr(EOI, ΔRMSE) = −0.578; Burnett corr = −0.425.

---

## Figure 17 — Carlisle LF-grid coarsening

**Caption:** Carlisle LF-grid coarsening sensitivity for LF-only, Global LSG, and
Rule zonal LSG.

![Figure 17](https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/master/outputs/figures/fig17_lf_degradation.png)

**Code** (`fig_degradation`): RMSE vs coarsening factor for LF-only/Global/Rule.

---

## Uncited figures (exist but intentionally not in manuscript)

These are generated but their data are presented as tables in the manuscript
instead of figures (per your earlier request to convert bar charts to tables):

| File | Content | Manuscript location |
|---|---|---|
| `fig16_official_maxwd_r2.png` | Official MaxWD R² protocol comparison | Table 5 |
| `fig18_channel_distance.png` | Channel-distance zoning sensitivity | Table 6 |
| `fig19_modal_eoi.png` | ZGG + oracle ΔRMSE | Table 3 |
| `fig08_runtime.png` | Train+predict wall time vs RMSE | (not cited) |
