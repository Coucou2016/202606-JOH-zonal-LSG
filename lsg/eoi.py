"""Error Organisation Index (EOI) — training-data residual-organisation diagnostic.

EOI = Var(zone-mean |LF−HF|) / Var(cell |LF−HF|) on the training wet mask.
The numerator is the **unweighted** variance across active-zone means (each zone
weighted equally regardless of cell count), so EOI is not by construction
confined to [0, 1].
High EOI indicates stronger between-zone organisation of LF–HF residual magnitude
relative to total cell-scale variance. It does **not** imply that zoning will
improve downstream LSG skill (Track B falsifies EOI-as-switch).
"""
from __future__ import annotations

from typing import Any

import numpy as np

from lsg.spatial import wet_cell_mask
from lsg.zoning import rule_based_zones


# Descriptive bins only — not validated decision thresholds for zoning.
EOI_HIGH = 0.30
EOI_MODERATE = 0.15


def interpret_eoi(eoi: float) -> str:
    if eoi > EOI_HIGH:
        return "HIGH_structured_residual"
    if eoi > EOI_MODERATE:
        return "MODERATE_partially_structured"
    return "LOW_diffuse_residual"


def compute_eoi(
    mean_abs_residual: np.ndarray,
    zone_labels: np.ndarray,
    active_mask: np.ndarray | None = None,
) -> dict[str, Any]:
    """EOI from a cell residual map and integer zone labels (−1 inactive)."""
    resid = np.asarray(mean_abs_residual, dtype=np.float64).reshape(-1)
    labels = np.asarray(zone_labels).reshape(-1)
    if active_mask is None:
        active = labels >= 0
    else:
        active = np.asarray(active_mask, dtype=bool).reshape(-1) & (labels >= 0)

    out: dict[str, Any] = {
        "eoi": float("nan"),
        "between_zone_var": float("nan"),
        "total_var": float("nan"),
        "n_active": int(active.sum()),
        "n_zones": 0,
        "zone_mean_abs_residual": {},
        "zone_n_cells": {},
        "interpretation": "undefined",
    }
    if int(active.sum()) < 8:
        return out

    r = resid[active]
    z = labels[active]
    zone_ids = sorted(int(i) for i in np.unique(z))
    zone_means = []
    for zid in zone_ids:
        m = z == zid
        n = int(m.sum())
        mu = float(np.mean(r[m])) if n else float("nan")
        out["zone_mean_abs_residual"][str(zid)] = mu
        out["zone_n_cells"][str(zid)] = n
        if n:
            zone_means.append(mu)

    total_var = float(np.var(r))
    between = float(np.var(zone_means)) if len(zone_means) >= 2 else 0.0
    eoi = between / (total_var + 1e-12)
    out.update(
        eoi=float(eoi),
        between_zone_var=between,
        total_var=total_var,
        n_zones=len(zone_ids),
        interpretation=interpret_eoi(eoi),
    )
    return out


def eoi_from_max_surfaces(
    hf_max: np.ndarray,
    lf_max: np.ndarray,
    wet_threshold: float = 0.03,
    event_index: np.ndarray | slice | None = None,
) -> dict[str, Any]:
    """Train-only EOI on LSG-Max surfaces using rule-based zones.

    hf_max, lf_max: (n_events, n_cells), LF already on the HF mesh.
    event_index: which events count as training (default: all).
    """
    if event_index is None:
        hf = np.asarray(hf_max, dtype=np.float64)
        lf = np.asarray(lf_max, dtype=np.float64)
    else:
        hf = np.asarray(hf_max[event_index], dtype=np.float64)
        lf = np.asarray(lf_max[event_index], dtype=np.float64)

    mean_resid = np.mean(np.abs(lf - hf), axis=0)
    max_depth = np.nanmax(hf, axis=0)
    inund_freq = np.nanmean(hf >= wet_threshold, axis=0)
    active = wet_cell_mask(hf, wet_threshold)
    labels = rule_based_zones(max_depth, inund_freq, active_mask=active)
    result = compute_eoi(mean_resid, labels, active)
    result["n_train_events"] = int(hf.shape[0])
    result["n_cells"] = int(hf.shape[1])
    result["mean_abs_residual_domain"] = float(np.mean(mean_resid[active])) if active.any() else float("nan")
    return result


def eoi_loocv_folds(
    hf_max: np.ndarray,
    lf_max: np.ndarray,
    wet_threshold: float = 0.03,
) -> list[dict[str, Any]]:
    """Per-fold train-only EOI for event-level leave-one-out."""
    n = hf_max.shape[0]
    rows = []
    for i in range(n):
        train = [j for j in range(n) if j != i]
        rec = eoi_from_max_surfaces(hf_max, lf_max, wet_threshold, event_index=train)
        rec["fold"] = i
        rec["test_event"] = i
        rows.append(rec)
    return rows


# ---------------------------------------------------------------------------
# Second-order (modal) diagnostics — replace first-order EOI as a switch
# ---------------------------------------------------------------------------


def principal_angles_deg(U: np.ndarray, V: np.ndarray) -> np.ndarray:
    """Principal angles (degrees) between column subspaces of U and V.

    U, V: (n_ambient, k) with orthonormal columns (or QR-orthonormalised).
    """
    U = np.asarray(U, dtype=np.float64)
    V = np.asarray(V, dtype=np.float64)
    if U.ndim == 1:
        U = U.reshape(-1, 1)
    if V.ndim == 1:
        V = V.reshape(-1, 1)
    Qu, _ = np.linalg.qr(U, mode="reduced")
    Qv, _ = np.linalg.qr(V, mode="reduced")
    # Singular values of Qu.T @ Qv are cos(theta)
    s = np.linalg.svd(Qu.T @ Qv, compute_uv=False)
    s = np.clip(s, 0.0, 1.0)
    return np.degrees(np.arccos(s))


def _rule_labels_from_hf(
    hf: np.ndarray,
    wet_threshold: float = 0.03,
) -> tuple[np.ndarray, np.ndarray]:
    max_depth = np.nanmax(hf, axis=0)
    inund_freq = np.nanmean(hf >= wet_threshold, axis=0)
    active = wet_cell_mask(hf, wet_threshold)
    labels = rule_based_zones(max_depth, inund_freq, active_mask=active)
    return labels, active


def _allocate_modes(n_zones: int, budget: int) -> list[int]:
    """Equal-ish allocation: each zone ≥1 if budget ≥ n_zones, else 1 each."""
    if n_zones <= 0:
        return []
    if budget < n_zones:
        return [1] * n_zones
    base = [1] * n_zones
    rem = budget - n_zones
    i = 0
    while rem > 0:
        base[i % n_zones] += 1
        rem -= 1
        i += 1
    return base


def _oracle_rmse(a: np.ndarray, b: np.ndarray, weights: np.ndarray | None = None) -> float:
    err2 = (np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)) ** 2
    if weights is None:
        return float(np.sqrt(np.mean(err2)))
    w = np.asarray(weights, dtype=np.float64).reshape(-1)
    den = float(np.sum(w)) + 1e-12
    if err2.ndim == 2:
        return float(np.sqrt(np.mean(np.sum(err2 * w[None, :], axis=1) / den)))
    return float(np.sqrt(np.sum(err2 * w) / den))


def modal_subspace_diagnostic(
    hf_max: np.ndarray,
    budget: int = 4,
    modes_per_zone_cap: int = 4,
    wet_threshold: float = 0.03,
    event_index: np.ndarray | slice | None = None,
    cell_areas: np.ndarray | None = None,
) -> dict[str, Any]:
    """Second-order zonal-EOF diagnostic on LSG-Max surfaces.

    Zone supports are disjoint, so zero-padded principal angles are always 90°
    and are **not** used. Instead:

    1. **Zone–global variance gap (ZGG):** on each zone, variance explained by
       ``k_z`` local modes minus variance explained by the same number of
       *global* modes restricted to that zone. Positive ZGG means local modes
       explain more within-zone variance than the same number of restricted
       global modes; this is **not** sufficient evidence that zonal EOF
       reconstruction or downstream LSG prediction will improve.
    2. **Equal-budget oracle EOF reconstruction:** HF→EOF→HF with total B modes
       (global vs rule). ``oracle_delta_rmse = RMSE_G − RMSE_Z`` (positive ⇒
       zoning already helps *before* any GP). When ``cell_areas`` is provided,
       also report area-weighted oracle RMSE / ΔRMSE.

    No LF or GP is used — this isolates the EOF organisation hypothesis.
    """
    from lsg import eof

    if event_index is None:
        hf = np.asarray(hf_max, dtype=np.float64)
    else:
        hf = np.asarray(hf_max[event_index], dtype=np.float64)

    labels, active = _rule_labels_from_hf(hf, wet_threshold)
    hf_wet = hf[:, active]
    labels_wet = labels[active]
    areas_wet = None
    if cell_areas is not None:
        areas_wet = np.asarray(cell_areas, dtype=np.float64).reshape(-1)[active]
    zone_ids = sorted(int(z) for z in np.unique(labels_wet) if z >= 0)
    n_active = int(active.sum())
    n_ev = int(hf.shape[0])
    out: dict[str, Any] = {
        "n_train_events": n_ev,
        "n_active": n_active,
        "n_zones": len(zone_ids),
        "budget": int(budget),
        "mean_zgg": float("nan"),
        "zone_zgg": {},
        "mean_principal_angle_deg": float("nan"),  # deprecated / unused
        "oracle_rmse_global": float("nan"),
        "oracle_rmse_zonal": float("nan"),
        "oracle_delta_rmse": float("nan"),
        "oracle_rmse_global_area": float("nan"),
        "oracle_rmse_zonal_area": float("nan"),
        "oracle_delta_rmse_area": float("nan"),
        "area_weights_used": bool(areas_wet is not None),
        "interpretation": "undefined",
    }
    if len(zone_ids) < 2 or n_ev < 2 or n_active < 8:
        return out

    B = int(budget)
    k_g = min(B, n_ev, n_active)
    pca_g, mean_g = eof.fit_eof(hf_wet, n_components=k_g)
    modes_g = pca_g.components_[:k_g]  # (k_g, n_active)

    # --- equal-budget oracle reconstruction ---
    ecs_g = eof.project_pseudo_ecs(hf_wet, modes_g, None, mean_g)
    recon_g = eof.reconstruct_from_ecs(ecs_g, modes_g, mean_g, None)
    rmse_g = _oracle_rmse(recon_g, hf_wet, None)
    rmse_g_area = (
        _oracle_rmse(recon_g, hf_wet, areas_wet) if areas_wet is not None else float("nan")
    )

    alloc = _allocate_modes(len(zone_ids), B)
    recon_z = np.zeros_like(hf_wet)
    zgg_list = []
    zone_zgg: dict[str, float] = {}
    zone_masks: dict[int, np.ndarray] = {}

    for zid, n_m in zip(zone_ids, alloc):
        m = labels_wet == zid
        zone_masks[zid] = m
        n_z = int(m.sum())
        if n_z < 2:
            recon_z[:, m] = hf_wet[:, m]
            continue
        k = min(int(n_m), n_ev, n_z, modes_per_zone_cap)
        hf_z = hf_wet[:, m]
        # local EOF
        pca_z, mean_z = eof.fit_eof(hf_z, n_components=max(k, 1))
        k = min(k, pca_z.n_components_)
        modes_z = pca_z.components_[:k]
        ecs_z = eof.project_pseudo_ecs(hf_z, modes_z, None, mean_z)
        recon_z[:, m] = eof.reconstruct_from_ecs(ecs_z, modes_z, mean_z, None)

        # variance explained: local vs global modes restricted to zone
        centred = hf_z - mean_z
        tot = float(np.sum(centred ** 2)) + 1e-12
        ve_local = float(np.sum(pca_z.explained_variance_ratio_[:k]))
        # global modes on this zone: (k_use, n_z); orthonormalise via QR
        k_use = min(k, modes_g.shape[0])
        Gz = modes_g[:k_use, :][:, m].T  # (n_z, k_use)
        Qg, _ = np.linalg.qr(Gz, mode="reduced")
        proj = centred @ Qg  # (n_ev, k_use)
        recon_g_z = proj @ Qg.T
        ve_grest = float(np.sum(recon_g_z ** 2) / tot)
        gap = ve_local - ve_grest
        zgg_list.append(gap)
        zone_zgg[str(zid)] = float(gap)

    rmse_z = _oracle_rmse(recon_z, hf_wet, None)
    rmse_z_area = (
        _oracle_rmse(recon_z, hf_wet, areas_wet) if areas_wet is not None else float("nan")
    )
    delta = rmse_g - rmse_z
    delta_area = (
        float(rmse_g_area - rmse_z_area) if areas_wet is not None else float("nan")
    )
    mean_zgg = float(np.mean(zgg_list)) if zgg_list else float("nan")

    out.update(
        mean_zgg=mean_zgg,
        zone_zgg=zone_zgg,
        oracle_rmse_global=rmse_g,
        oracle_rmse_zonal=rmse_z,
        oracle_delta_rmse=float(delta),
        oracle_rmse_global_area=float(rmse_g_area) if areas_wet is not None else float("nan"),
        oracle_rmse_zonal_area=float(rmse_z_area) if areas_wet is not None else float("nan"),
        oracle_delta_rmse_area=delta_area,
        mode_allocation={str(z): int(a) for z, a in zip(zone_ids, alloc)},
    )
    if delta > 0 and mean_zgg > 0.02:
        out["interpretation"] = "ZGG_AND_ORACLE_GAIN"
    elif delta > 0:
        out["interpretation"] = "ORACLE_GAIN_WEAK_ZGG"
    elif mean_zgg > 0.02:
        out["interpretation"] = "ZGG_POSITIVE_ORACLE_LOSS"
    else:
        out["interpretation"] = "LOW_MODAL_SEPARATION"
    return out


def modal_diagnostic_loocv(
    hf_max: np.ndarray,
    budget: int = 4,
    wet_threshold: float = 0.03,
    cell_areas: np.ndarray | None = None,
) -> list[dict[str, Any]]:
    """Per-fold train-only modal diagnostic (leave-one-event-out training set)."""
    n = hf_max.shape[0]
    rows = []
    for i in range(n):
        train = [j for j in range(n) if j != i]
        rec = modal_subspace_diagnostic(
            hf_max,
            budget=budget,
            wet_threshold=wet_threshold,
            event_index=train,
            cell_areas=cell_areas,
        )
        rec["fold"] = i
        rec["test_event"] = i
        rows.append(rec)
    return rows
