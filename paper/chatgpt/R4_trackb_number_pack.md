# Track B number pack for R4 data authenticity audit (desensitized)

Source of truth: local `outputs/evaluation/**` JSON (not manuscript prose).

## Carlisle budget_sweep_true_equal.json
- LF-only RMSE 0.1602; CSI 0.9145
- B=4: Global 0.1464; Rule 0.0964; KMeans 0.1015; modes 4/4/4
- B=6: Global 0.2588; Rule 0.1256; KMeans 0.1367
- B=8: Global 0.3527 (actual_modes=7 MISMATCH); Rule 0.1790 (actual_modes=8)

## Carlisle loocv_results.json + loocv_bootstrap_ci.json (rng=42, n=10000)
- B=4: 9/9; mean Δ 0.0821; CI [0.0155, 0.1987]
- B=6: 7/9; mean Δ 0.0606; CI [0.0032, 0.1618]

## Carlisle multifold_bootstrap.json (official 2-fold)
- mean Δ 0.0045; CI [-0.0073, 0.0134]; significant=false

## Carlisle stage_swap.json loocv.summary
- GG 0.1802; ZZ 0.0979; GZ 0.0980; ZG 0.1010

## Carlisle official_fold_zonal.json summary
- Rule mean MaxWD R² 0.988; published LSG-TS MaxWD R² 0.990; Global Max ≈ 0.915

## EOI eoi_all.json (max-surface pooled)
- Carlisle 0.057; Chowilla 0.116; Burnett 0.957

## modal_eoi.json pooled
- All three: ZGG_POSITIVE_ORACLE_LOSS (oracle_delta_rmse < 0)

## Burnett loocv_results.json summary.rule
- mean Global 1.7479; Rule 1.8260; Δ -0.0781; 6/30; significant=false

## Chowilla budget_sweep_full.json B=4
- LF 0.3926; Global 2.5606; Rule 2.5614; KMeans 2.5619

## Burnett validation_std.json (12-event three-case split)
- LF 2.2323; Global 1.6120; Rule_B4 1.6122
