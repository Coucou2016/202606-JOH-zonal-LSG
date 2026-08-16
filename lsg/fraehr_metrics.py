"""Fraehr (Water Research 2024) evaluation protocol, ported for LSG-Max.

Published RMSE / FI are time-series metrics on wet cells (LSG-TS). LSG-Max
cannot reproduce those. MaxWD_R2, CSI of max extent, and peak_diff *are*
max-surface metrics and are comparable when evaluated on the official wet_idx.

References
----------
data/external/fraehr2024/Python_data/Evaluation_metrics.py
data/external/fraehr2024/Python_data/LSG_mods_and_func/LSG_support_functions.py
"""
from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import r2_score as sklearn_r2


PUBLISHED_MODELS = ("LSG", "Kabir_1dCNN", "LSTM_SRR", "GP_EOF", "LSTM_EOF")


def rmse_(true: np.ndarray, predicted: np.ndarray, axis=None) -> float | np.ndarray:
    """Fraehr RMSE_ — unweighted mean squared error, then sqrt."""
    val = np.sqrt(np.mean(np.square(predicted - true), axis=axis))
    return float(val) if np.ndim(val) == 0 else val


def fidelity_index(
    true: np.ndarray,
    pred: np.ndarray,
    wd_tol: float = 0.05,
    time_tol: float = 0.05,
    time_tol_as_timesteps: bool = False,
) -> float:
    """Time-tolerant fidelity index (LSG-TS only). ``true``/``pred`` are (T, C)."""
    true = np.asarray(true)
    pred = np.asarray(pred)
    if time_tol_as_timesteps:
        total_shifts = int(time_tol)
    else:
        total_shifts = int(round(time_tol * len(true)))
    total_shifts = max(total_shifts, 0)
    if len(true) <= 2 * total_shifts:
        return float("nan")
    core_t = true[total_shifts:-total_shifts] if total_shifts else true
    core_p = pred[total_shifts:-total_shifts] if total_shifts else pred
    n_predictions = int(core_t.size)
    if n_predictions == 0:
        return float("nan")
    diff_min = np.full_like(core_t, np.inf, dtype=np.float64)
    shifts = range(-total_shifts, total_shifts) if total_shifts else range(0, 1)
    for i in shifts:
        rolled = np.roll(true, i, axis=0)
        if total_shifts:
            rolled = rolled[total_shifts:-total_shifts]
        diff_min = np.minimum(diff_min, np.abs(core_p - rolled))
    return float(np.sum(diff_min < wd_tol) / n_predictions)


def ws2wd(data: np.ndarray, elevation: np.ndarray, dry_threshold: float = 0.03) -> np.ndarray:
    """Water-surface elevation → water depth; dry cells floored to 0."""
    wd = np.asarray(data, dtype=np.float64) - np.asarray(elevation, dtype=np.float64)
    return np.where(wd < dry_threshold, 0.0, wd)


def convert_wse_to_binary(
    data: np.ndarray,
    elevation: np.ndarray,
    threshold_flood: float = 0.03,
) -> np.ndarray:
    return (np.asarray(data) >= (np.asarray(elevation) + threshold_flood)).astype(np.int8)


def convert_depth_to_binary(depth: np.ndarray, threshold_flood: float = 0.03) -> np.ndarray:
    return (np.asarray(depth) >= threshold_flood).astype(np.int8)


def pod_rfa_csi(true_labels: np.ndarray, pred_labels: np.ndarray) -> tuple[float, float, float]:
    """POD, RFA, CSI matching ``pod_rfa_1tstep`` (standard CSI when Fraehr form is undefined)."""
    true_labels = np.asarray(true_labels)
    pred_labels = np.asarray(pred_labels)
    tp = float(np.sum((pred_labels > 0) & (true_labels > 0)))
    fp = float(np.sum((pred_labels > 0) & (true_labels == 0)))
    fn = float(np.sum((pred_labels == 0) & (true_labels > 0)))
    pod = tp / (tp + fn) if (tp + fn) else 0.0
    rfa = fp / (tp + fp) if (tp + fp) else 0.0
    csi_std = tp / (tp + fp + fn) if (tp + fp + fn) else 0.0
    if pod > 0.0 and rfa < 1.0:
        csi_f = 1.0 / ((1.0 / (1.0 - rfa)) + (1.0 / pod - 1.0))
    else:
        csi_f = csi_std
    return float(pod), float(rfa), float(csi_f)


def floor_dry(depth: np.ndarray, threshold_m: float = 0.03) -> np.ndarray:
    d = np.asarray(depth, dtype=np.float64)
    return np.where(d < threshold_m, 0.0, d)


def max_surface_protocol_metrics(
    pred_depth: np.ndarray,
    ref_depth: np.ndarray,
    wet_idx: np.ndarray | None = None,
    threshold_m: float = 0.03,
) -> dict[str, float]:
    """Max-surface metrics comparable to published MaxWD_R2 / CSI / peak_diff.

    pred/ref: (n_cells,) water depth on the HF mesh.
    If wet_idx is given, RMSE / R2 / peak_diff / CSI are computed on those cells
    (official Fraehr interpolation protocol). CSI uses binary max extent.
    """
    pred = floor_dry(np.asarray(pred_depth).reshape(-1), threshold_m)
    ref = floor_dry(np.asarray(ref_depth).reshape(-1), threshold_m)
    if wet_idx is not None:
        idx = np.asarray(wet_idx, dtype=int)
        pred_w, ref_w = pred[idx], ref[idx]
    else:
        pred_w, ref_w = pred, ref

    r2 = float(sklearn_r2(ref_w, pred_w)) if ref_w.size else float("nan")
    peak = float(np.mean(ref_w - pred_w)) if ref_w.size else float("nan")
    rmse = rmse_(ref_w, pred_w)
    true_bin = convert_depth_to_binary(ref_w, threshold_m)
    pred_bin = convert_depth_to_binary(pred_w, threshold_m)
    pod, rfa, csi = pod_rfa_csi(true_bin, pred_bin)
    return {
        "rmse_wet": float(rmse),
        "maxwd_r2": r2,
        "peak_diff": peak,
        "csi": float(csi),
        "pod": float(pod),
        "rfa": float(rfa),
        "n_wet": int(ref_w.size),
    }


def load_published_validation(npz_path, model_names=PUBLISHED_MODELS) -> dict[str, Any]:
    """Load Result_data/Validation_results.npz (or _extrap.npz)."""
    raw = np.load(npz_path, allow_pickle=True)
    out: dict[str, Any] = {"models": list(model_names), "n_events": int(raw["RMSE"].shape[0])}
    for key in ("RMSE", "CSI", "FI", "MaxWD_R2", "peak_diff", "pred_time"):
        if key not in raw.files:
            continue
        arr = np.asarray(raw[key], dtype=np.float64)
        out[key] = arr
        means = arr.mean(axis=0)
        out[f"{key}_mean"] = {
            model_names[j]: float(means[j]) for j in range(min(len(model_names), arr.shape[1]))
        }
    if "n_timesteps" in raw.files:
        out["n_timesteps"] = np.asarray(raw["n_timesteps"]).tolist()
    if "MaxWD" in raw.files:
        out["MaxWD_shape"] = list(np.asarray(raw["MaxWD"]).shape)
    return out
