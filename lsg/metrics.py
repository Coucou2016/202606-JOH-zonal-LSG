"""Evaluation metrics for flood inundation prediction.

RMSE, MAE, Bias, CSI, POD, RFA/FAR, plus zone-level and hotspot metrics.
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Continuous metrics
# ---------------------------------------------------------------------------


def rmse(pred: np.ndarray, ref: np.ndarray) -> float:
    return float(np.sqrt(np.mean((pred - ref) ** 2)))


def mae(pred: np.ndarray, ref: np.ndarray) -> float:
    return float(np.mean(np.abs(pred - ref)))


def bias(pred: np.ndarray, ref: np.ndarray) -> float:
    return float(np.mean(pred - ref))


def r2_score(pred: np.ndarray, ref: np.ndarray) -> float:
    ss_res = np.sum((ref - pred) ** 2)
    ss_tot = np.sum((ref - np.mean(ref)) ** 2)
    return float(1 - ss_res / (ss_tot + 1e-12))


# ---------------------------------------------------------------------------
# Binary / contingency metrics
# ---------------------------------------------------------------------------


def contingency_table(
    pred_depth: np.ndarray,
    ref_depth: np.ndarray,
    threshold_m: float = 0.03,
) -> dict[str, int]:
    pred_wet = pred_depth >= threshold_m
    ref_wet = ref_depth >= threshold_m
    hits = int(np.sum(pred_wet & ref_wet))
    misses = int(np.sum(~pred_wet & ref_wet))
    false_alarms = int(np.sum(pred_wet & ~ref_wet))
    correct_neg = int(np.sum(~pred_wet & ~ref_wet))
    return {
        "hits": hits,
        "misses": misses,
        "false_alarms": false_alarms,
        "correct_negatives": correct_neg,
    }


def pod(ct: dict[str, int]) -> float:
    """Probability of Detection = hits / (hits + misses)."""
    denom = ct["hits"] + ct["misses"]
    return ct["hits"] / denom if denom else 0.0


def far(ct: dict[str, int]) -> float:
    """False Alarm Ratio = false_alarms / (hits + false_alarms)."""
    denom = ct["hits"] + ct["false_alarms"]
    return ct["false_alarms"] / denom if denom else 0.0


def rfa(ct: dict[str, int]) -> float:
    """Ratio of False Alarms (same as FAR)."""
    return far(ct)


def csi(ct: dict[str, int]) -> float:
    """Critical Success Index = hits / (hits + misses + false_alarms)."""
    denom = ct["hits"] + ct["misses"] + ct["false_alarms"]
    return ct["hits"] / denom if denom else 0.0


def hss(ct: dict[str, int]) -> float:
    """Heidke Skill Score."""
    n = ct["hits"] + ct["misses"] + ct["false_alarms"] + ct["correct_negatives"]
    expected = (
        (ct["hits"] + ct["misses"]) * (ct["hits"] + ct["false_alarms"])
        + (ct["correct_negatives"] + ct["misses"])
        * (ct["correct_negatives"] + ct["false_alarms"])
    ) / n
    return (ct["hits"] + ct["correct_negatives"] - expected) / (
        n - expected + 1e-12
    )


# ---------------------------------------------------------------------------
# Combined metrics
# ---------------------------------------------------------------------------


def extent_metrics(
    pred_depth: np.ndarray,
    ref_depth: np.ndarray,
    threshold_m: float = 0.03,
) -> dict[str, float]:
    ct = contingency_table(pred_depth, ref_depth, threshold_m)
    return {
        "rmse": rmse(pred_depth, ref_depth),
        "mae": mae(pred_depth, ref_depth),
        "bias": bias(pred_depth, ref_depth),
        "r2": r2_score(pred_depth, ref_depth),
        "pod": pod(ct),
        "far": far(ct),
        "csi": csi(ct),
        "hss": hss(ct),
        "ct_hits": ct["hits"],
        "ct_misses": ct["misses"],
        "ct_false_alarms": ct["false_alarms"],
        "ct_correct_negatives": ct["correct_negatives"],
    }


def max_surface_metrics(
    pred_ts: np.ndarray,
    ref_ts: np.ndarray,
    threshold_m: float = 0.03,
    time_axis: int = 0,
) -> dict[str, float]:
    """Compute metrics on maximum flood surfaces derived from time series."""
    pred_max = pred_ts.max(axis=time_axis)
    ref_max = ref_ts.max(axis=time_axis)
    return extent_metrics(pred_max, ref_max, threshold_m)


# ---------------------------------------------------------------------------
# Zone-level metrics
# ---------------------------------------------------------------------------


def zone_metrics(
    pred: np.ndarray,
    ref: np.ndarray,
    zone_labels: np.ndarray,
    threshold_m: float = 0.03,
    active_mask: np.ndarray | None = None,
) -> dict[int, dict[str, float]]:
    """Compute per-zone evaluation metrics.

    pred/ref: (n_samples, n_cells) or (n_cells,)
    zone_labels: (n_cells,) integer zone IDs (-1 = inactive)
    """
    if pred.ndim == 1:
        pred = pred.reshape(1, -1)
        ref = ref.reshape(1, -1)

    if active_mask is not None:
        pred = pred[:, active_mask]
        ref = ref[:, active_mask]
        zone_labels = zone_labels[active_mask]

    unique_zones = sorted(set(zone_labels) - {-1})
    results = {}
    for z in unique_zones:
        mask_z = zone_labels == z
        pred_z = pred[:, mask_z].ravel()
        ref_z = ref[:, mask_z].ravel()
        results[int(z)] = extent_metrics(pred_z, ref_z, threshold_m)
    return results


# ---------------------------------------------------------------------------
# Error hotspot metrics
# ---------------------------------------------------------------------------


def error_hotspot_metrics(
    pred: np.ndarray,
    ref: np.ndarray,
    error_baseline: np.ndarray | None = None,
    hotspot_percentile: float = 90,
    threshold_m: float = 0.03,
) -> dict[str, float]:
    """Compute metrics in error hotspots.

    If error_baseline is given, hotspots are defined by that error map
    (e.g., global LSG error). Otherwise defined by |pred - ref|.
    """
    if error_baseline is None:
        error = np.abs(pred - ref)
    else:
        error = np.abs(error_baseline)

    wet = ref >= threshold_m
    if not wet.any():
        return {"hotspot_rmse": 0.0, "hotspot_n_cells": 0}

    threshold = np.percentile(error[wet], hotspot_percentile)
    hotspot = wet & (error >= threshold)
    n_hotspot = int(hotspot.sum())

    if n_hotspot == 0:
        return {"hotspot_rmse": 0.0, "hotspot_n_cells": 0}

    return {
        "hotspot_rmse": float(
            np.sqrt(np.mean((pred[hotspot] - ref[hotspot]) ** 2))
        ),
        "hotspot_mae": float(np.mean(np.abs(pred[hotspot] - ref[hotspot]))),
        "hotspot_bias": float(np.mean(pred[hotspot] - ref[hotspot])),
        "hotspot_n_cells": n_hotspot,
        "hotspot_fraction": float(n_hotspot / wet.sum()),
    }


# ---------------------------------------------------------------------------
# Paired improvement statistics
# ---------------------------------------------------------------------------


def paired_improvement(
    metrics_global: list[dict[str, float]],
    metrics_zonal: list[dict[str, float]],
    key: str = "rmse",
    n_bootstrap: int = 1000,
    ci: float = 0.95,
    rng: np.random.Generator | None = None,
) -> dict[str, Any]:
    """Bootstrap confidence interval for zonal - global improvement.

    metrics_global / metrics_zonal: list of per-fold or per-event metric dicts.
    Lower RMSE (or MAE, bias magnitude) is better -> negative delta = improvement.
    Higher CSI, POD, R2 is better -> positive delta = improvement.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    g = np.array([m[key] for m in metrics_global])
    z = np.array([m[key] for m in metrics_zonal])
    delta = z - g  # negative = improvement for error metrics

    n = len(delta)
    boot_deltas = []
    for _ in range(n_bootstrap):
        idx = rng.choice(n, size=n, replace=True)
        boot_deltas.append(np.mean(delta[idx]))

    boot_deltas = np.array(boot_deltas)
    lower = np.percentile(boot_deltas, (1 - ci) / 2 * 100)
    upper = np.percentile(boot_deltas, (1 + ci) / 2 * 100)
    mean_delta = np.mean(delta)
    is_significant = lower * upper > 0  # same sign

    return {
        "mean_delta": float(mean_delta),
        "ci_lower": float(lower),
        "ci_upper": float(upper),
        "ci_level": ci,
        "significant": bool(is_significant),
        "direction": "improvement" if (
            (key in ("rmse", "mae", "far", "rfa") and mean_delta < 0)
            or (key in ("csi", "pod", "r2", "hss") and mean_delta > 0)
        ) else "degradation",
    }


# ---------------------------------------------------------------------------
# Speed metrics
# ---------------------------------------------------------------------------


def speedup_ratio(
    runtime_lf: float,
    runtime_surrogate: float,
    runtime_hf: float,
) -> float:
    """Compute speed-up ratio: (LF + surrogate) vs HF."""
    return runtime_hf / (runtime_lf + runtime_surrogate + 1e-12)
