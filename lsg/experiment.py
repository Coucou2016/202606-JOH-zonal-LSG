"""Shared LSG-Max fit/predict used by the innovation-track scripts."""
from __future__ import annotations

import time
from typing import Any

import numpy as np

from lsg.baseline_lsg import GlobalLSG
from lsg.metrics_area import area_weighted_metrics
from lsg.zonal_lsg import ZonalLSG
from lsg.zoning import ZoningConfig


def fit_predict_max(
    hf_tr: np.ndarray,
    lf_tr: np.ndarray,
    hf_te: np.ndarray,
    lf_te: np.ndarray,
    terrain: np.ndarray,
    xy: np.ndarray,
    budget: int,
    method: str = "global",
    distance_to_flow: np.ndarray | None = None,
    n_zones: int = 4,
    use_channel_distance: bool = False,
    return_labels: bool = False,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Train LSG-Max on ``*_tr`` and predict ``*_te``. LF already on the HF mesh."""
    n_hf = int(hf_tr.shape[1])
    sd = (1, n_hf)
    t0 = time.perf_counter()
    extra: dict[str, Any] = {}

    if method == "global":
        m = GlobalLSG(variant="max", max_eof_modes=30, eof_variance=0.99, wet_threshold=0.03)
        m.force_n_modes = budget
        m.fit(hf_tr, lf_tr, terrain, sd, sd, lf_already_interpolated=True)
        pred = m.predict(lf_te, terrain, sd, sd, lf_already_interpolated=True)
        n_modes = int(m.state.n_modes) if m.state else 0
    else:
        zc = ZoningConfig(
            method=method,
            n_zones=n_zones,
            wet_threshold=0.03,
            use_channel_distance=use_channel_distance,
        )
        m = ZonalLSG(
            zoning_config=zc,
            variant="max",
            mode_budget=budget,
            max_modes_per_zone=10,
            eof_variance=0.99,
            wet_threshold=0.03,
        )
        m.fit(
            hf_tr, lf_tr, terrain, sd, sd,
            x_hf=xy[:, 0], y_hf=xy[:, 1],
            distance_to_flow=distance_to_flow,
        )
        pred = m.predict(lf_te, terrain, sd, sd)
        zs = m.get_zone_statistics() if m.state else {}
        n_modes = int(sum(v["n_modes"] for v in zs.values())) if zs else 0
        extra["zone_stats"] = {str(k): v for k, v in zs.items()}
        if return_labels and m.state is not None:
            extra["zone_labels"] = m.state.zone_labels
            extra["active_mask"] = m.state.active_mask

    meta = {
        "n_modes": n_modes,
        "time_s": float(time.perf_counter() - t0),
        "method": method,
        "budget": int(budget),
        **extra,
    }
    return pred, meta


def per_event_area(pred: np.ndarray, ref: np.ndarray, areas: np.ndarray) -> list[dict[str, float]]:
    return [area_weighted_metrics(pred[i], ref[i], areas, 0.03) for i in range(pred.shape[0])]


def mean_area(rows: list[dict[str, float]]) -> dict[str, float]:
    keys = rows[0].keys()
    return {k: float(np.mean([r[k] for r in rows])) for k in keys}


def jsonable(obj):
    """JSON-safe conversion for numpy scalars / arrays."""
    if isinstance(obj, dict):
        return {str(k): jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, float)):
        v = float(obj)
        if np.isnan(v) or np.isinf(v):
            return None
        return v
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    return obj
