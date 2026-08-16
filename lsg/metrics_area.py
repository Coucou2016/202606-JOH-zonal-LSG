"""Area-weighted evaluation metrics for unstructured floodplain meshes."""
import numpy as np


def area_weighted_rmse(pred, ref, areas):
    """RMSE weighted by cell area."""
    w = np.asarray(areas, dtype=np.float64)
    se = w * (pred - ref) ** 2
    return float(np.sqrt(np.sum(se) / (np.sum(w) + 1e-12)))


def area_weighted_mae(pred, ref, areas):
    """MAE weighted by cell area."""
    w = np.asarray(areas, dtype=np.float64)
    return float(np.sum(w * np.abs(pred - ref)) / (np.sum(w) + 1e-12))


def area_weighted_bias(pred, ref, areas):
    """Bias weighted by cell area."""
    w = np.asarray(areas, dtype=np.float64)
    return float(np.sum(w * (pred - ref)) / (np.sum(w) + 1e-12))


def area_weighted_contingency(pred_depth, ref_depth, areas, threshold_m=0.03):
    """Contingency table with area-weighted counts."""
    w = np.asarray(areas, dtype=np.float64)
    pred_wet = pred_depth >= threshold_m
    ref_wet = ref_depth >= threshold_m

    hit_area = float(np.sum(w[pred_wet & ref_wet]))
    miss_area = float(np.sum(w[~pred_wet & ref_wet]))
    fa_area = float(np.sum(w[pred_wet & ~ref_wet]))
    cn_area = float(np.sum(w[~pred_wet & ~ref_wet]))

    return {
        "hits_area": hit_area,
        "misses_area": miss_area,
        "false_alarms_area": fa_area,
        "correct_negatives_area": cn_area,
    }


def area_weighted_csi(pred_depth, ref_depth, areas, threshold_m=0.03):
    """Area-weighted Critical Success Index."""
    ct = area_weighted_contingency(pred_depth, ref_depth, areas, threshold_m)
    denom = ct["hits_area"] + ct["misses_area"] + ct["false_alarms_area"]
    return ct["hits_area"] / denom if denom > 0 else 0.0


def area_weighted_pod(pred_depth, ref_depth, areas, threshold_m=0.03):
    """Area-weighted Probability of Detection."""
    ct = area_weighted_contingency(pred_depth, ref_depth, areas, threshold_m)
    denom = ct["hits_area"] + ct["misses_area"]
    return ct["hits_area"] / denom if denom > 0 else 0.0


def area_weighted_far(pred_depth, ref_depth, areas, threshold_m=0.03):
    """Area-weighted False Alarm Ratio."""
    ct = area_weighted_contingency(pred_depth, ref_depth, areas, threshold_m)
    denom = ct["hits_area"] + ct["false_alarms_area"]
    return ct["false_alarms_area"] / denom if denom > 0 else 0.0


def area_weighted_metrics(pred, ref, areas, threshold_m=0.03):
    """All area-weighted metrics."""
    return {
        "rmse_area": area_weighted_rmse(pred, ref, areas),
        "mae_area": area_weighted_mae(pred, ref, areas),
        "bias_area": area_weighted_bias(pred, ref, areas),
        "csi_area": area_weighted_csi(pred, ref, areas, threshold_m),
        "pod_area": area_weighted_pod(pred, ref, areas, threshold_m),
        "far_area": area_weighted_far(pred, ref, areas, threshold_m),
    }


def per_event_metrics(pred_events, ref_events, areas, threshold_m=0.03):
    """Compute metrics separately for each event."""
    n_ev = pred_events.shape[0]
    results = []
    for i in range(n_ev):
        m = area_weighted_metrics(pred_events[i], ref_events[i], areas, threshold_m)
        m["event"] = i
        results.append(m)
    return results


def bootstrap_delta(global_metrics, zonal_metrics, key="rmse_area",
                    n_bootstrap=10000, ci=0.95, seed=42):
    """Bootstrap confidence interval for zonal - global improvement."""
    rng = np.random.default_rng(seed)
    g = np.array([m[key] for m in global_metrics])
    z = np.array([m[key] for m in zonal_metrics])
    delta = z - g  # negative = improvement for error metrics
    n = len(delta)

    boot_means = np.array([
        np.mean(rng.choice(delta, size=n, replace=True))
        for _ in range(n_bootstrap)
    ])

    lower = np.percentile(boot_means, (1 - ci) / 2 * 100)
    upper = np.percentile(boot_means, (1 + ci) / 2 * 100)
    mean_delta = float(np.mean(delta))
    improved = float(np.mean(delta < 0))  # fraction improved

    # For CSI/POD/R2: positive delta = improvement
    is_error_metric = key.startswith("rmse") or key.startswith("mae") or \
                      key.startswith("bias") or key.startswith("far")

    return {
        "mean_delta": mean_delta,
        "median_delta": float(np.median(delta)),
        "ci_lower": float(lower),
        "ci_upper": float(upper),
        "ci_level": ci,
        "n_bootstrap": n_bootstrap,
        "significant": bool(lower * upper > 0),
        "improved_fraction": improved,
        "direction": "improvement" if (
            (is_error_metric and mean_delta < 0) or
            (not is_error_metric and mean_delta > 0)
        ) else "degradation",
    }
