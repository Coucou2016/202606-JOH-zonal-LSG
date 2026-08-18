"""Hydrodynamic zoning methods for floodplain partitioning.

Implements:
  Z0: Global (single zone, baseline)
  Z1: Rule-based hydrodynamic zoning
  Z2: Data-driven (KMeans / AgglomerativeClustering) zoning
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler


@dataclass
class ZoningConfig:
    method: str = "kmeans"  # "global", "rule", "kmeans", "agglomerative"
    n_zones: int = 4
    wet_threshold: float = 0.03
    random_state: int = 42
    feature_set: str = "full"  # "full", "no_residual", "no_spatial", "minimal"
    deep_percentile: float = 80
    error_percentile: float = 80
    frequent_threshold: float = 0.7
    intermittent_lower: float = 0.1
    use_channel_distance: bool = False
    near_channel_percentile: float = 20.0


# ---------------------------------------------------------------------------
# Feature construction
# ---------------------------------------------------------------------------


def build_cell_features(
    x: np.ndarray,
    y: np.ndarray,
    depth_hf_train: np.ndarray,
    depth_lf_interp_train: np.ndarray | None = None,
    terrain: np.ndarray | None = None,
    distance_to_flow: np.ndarray | None = None,
) -> np.ndarray:
    """Build feature matrix for zoning.

    depth_hf_train: (n_events, n_time, n_cells) or (n_samples, n_cells)
    depth_lf_interp_train: LF interpolated to HF cells, same shape as HF
    """
    if depth_hf_train.ndim == 3:
        flat_hf = depth_hf_train.reshape(-1, depth_hf_train.shape[-1])
    else:
        flat_hf = depth_hf_train

    max_depth = np.nanmax(flat_hf, axis=0)
    mean_depth = np.nanmean(flat_hf, axis=0)
    std_depth = np.nanstd(flat_hf, axis=0)
    inundation_frequency = np.nanmean(flat_hf >= 0.03, axis=0)
    # time-to-peak proxy: at what fraction of the time series does max occur?
    if depth_hf_train.ndim == 3:
        n_ev, n_t, n_c = depth_hf_train.shape
        argmax_per_event = np.argmax(depth_hf_train, axis=1)  # (n_ev, n_c)
        time_to_peak = np.nanmean(argmax_per_event / max(n_t - 1, 1), axis=0)
    else:
        time_to_peak = np.full(depth_hf_train.shape[1], 0.5)

    features = [
        (x - np.nanmean(x)) / (np.nanstd(x) + 1e-12),
        (y - np.nanmean(y)) / (np.nanstd(y) + 1e-12),
        np.log1p(max_depth),
        np.log1p(mean_depth),
        np.log1p(std_depth),
        inundation_frequency,
        time_to_peak,
    ]

    if terrain is not None:
        features.append(
            (terrain - np.nanmean(terrain)) / (np.nanstd(terrain) + 1e-12)
        )

    if depth_lf_interp_train is not None:
        if depth_lf_interp_train.ndim == 3:
            flat_lf = depth_lf_interp_train.reshape(-1, depth_lf_interp_train.shape[-1])
        else:
            flat_lf = depth_lf_interp_train
        residual = flat_lf - flat_hf
        mean_abs_residual = np.nanmean(np.abs(residual), axis=0)
        features.append(np.log1p(mean_abs_residual))

    if distance_to_flow is not None:
        features.append(
            np.log1p(distance_to_flow)
            / (np.nanstd(np.log1p(distance_to_flow)) + 1e-12)
        )

    return np.vstack(features).T


# ---------------------------------------------------------------------------
# Zoning methods
# ---------------------------------------------------------------------------


def global_zones(
    n_cells: int,
    active_mask: np.ndarray,
) -> np.ndarray:
    """Z0: Single global zone for all active cells."""
    labels = np.full(n_cells, fill_value=-1, dtype=int)
    labels[active_mask] = 0
    return labels


def rule_based_zones(
    max_depth: np.ndarray,
    inundation_frequency: np.ndarray,
    lf_hf_abs_residual: np.ndarray | None = None,
    distance_to_flow: np.ndarray | None = None,
    active_mask: np.ndarray | None = None,
    deep_percentile: float = 80,
    error_percentile: float = 80,
    frequent_threshold: float = 0.7,
    intermittent_lower: float = 0.1,
    near_channel_percentile: float = 20.0,
) -> np.ndarray:
    """Z1: Rule-based hydrodynamic zoning.

    Creates up to 5 zones:
      0: near-channel / deep dynamic (main conveyance)
      1: frequently inundated floodplain
      2: intermittently inundated floodplain
      3: rarely inundated fringe
      4: residual-error hotspot (override)
    """
    n = max_depth.size
    labels = np.full(n, fill_value=-1, dtype=int)
    if active_mask is None:
        active_mask = max_depth >= 0.03

    deep_thr = np.nanpercentile(max_depth[active_mask], deep_percentile)
    freq_thr = frequent_threshold
    int_lower = intermittent_lower

    err_thr = None
    if lf_hf_abs_residual is not None:
        err_thr = np.nanpercentile(lf_hf_abs_residual[active_mask], error_percentile)

    active = active_mask
    labels[active & (max_depth >= deep_thr)] = 0  # deep / near-channel
    labels[active & (max_depth < deep_thr) & (inundation_frequency >= freq_thr)] = 1
    labels[active & (inundation_frequency >= int_lower)
           & (inundation_frequency < freq_thr)] = 2
    labels[active & (inundation_frequency < int_lower)] = 3

    # Optional near-channel override (B6). Off unless distance_to_flow is passed.
    if distance_to_flow is not None:
        dist_thr = np.nanpercentile(distance_to_flow[active], near_channel_percentile)
        labels[active & (distance_to_flow <= dist_thr)] = 0

    # Error hotspot overlay (highest priority)
    if lf_hf_abs_residual is not None and err_thr is not None:
        labels[active & (lf_hf_abs_residual >= err_thr)] = 4

    # Assign unassigned active cells to nearest zone
    unassigned = active & (labels == -1)
    if unassigned.any():
        labels[unassigned] = 1  # default to frequent floodplain

    return labels


def kmeans_zones(
    features: np.ndarray,
    active_mask: np.ndarray,
    n_zones: int = 4,
    random_state: int = 42,
) -> np.ndarray:
    """Z2: KMeans clustering of cell features."""
    labels = np.full(features.shape[0], fill_value=-1, dtype=int)
    scaler = StandardScaler()
    X = scaler.fit_transform(features[active_mask])
    km = KMeans(
        n_clusters=n_zones,
        n_init=20,
        max_iter=500,
        random_state=random_state,
    )
    labels[active_mask] = km.fit_predict(X)
    return labels


def agglomerative_zones(
    features: np.ndarray,
    active_mask: np.ndarray,
    n_zones: int = 4,
) -> np.ndarray:
    """Z2b: Agglomerative clustering of cell features."""
    labels = np.full(features.shape[0], fill_value=-1, dtype=int)
    scaler = StandardScaler()
    X = scaler.fit_transform(features[active_mask])
    ac = AgglomerativeClustering(n_clusters=n_zones)
    labels[active_mask] = ac.fit_predict(X)
    return labels


def channel_distance_zones(
    distance_to_flow: np.ndarray,
    inundation_frequency: np.ndarray | None = None,
    active_mask: np.ndarray | None = None,
    n_zones: int = 4,
) -> np.ndarray:
    """Physical zoning by distance to the mapped main channel (B6).

    Active cells are split into ``n_zones`` equal-count distance bands
    (nearest = zone 0). Inundation frequency is unused in the split so the
    partition is independent of the LF–HF residual and of depth percentiles.
    """
    n = distance_to_flow.size
    labels = np.full(n, fill_value=-1, dtype=int)
    if active_mask is None:
        active_mask = np.ones(n, dtype=bool)
    d = np.asarray(distance_to_flow, dtype=np.float64)
    active = np.asarray(active_mask, dtype=bool)
    if inundation_frequency is not None:
        # keep signature for callers; frequency does not change the bins
        _ = inundation_frequency
    vals = d[active]
    if vals.size == 0:
        return labels
    qs = np.nanpercentile(vals, np.linspace(0, 100, n_zones + 1)[1:-1])
    bins = np.digitize(d, qs, right=True)
    bins = np.clip(bins, 0, n_zones - 1)
    labels[active] = bins[active]
    return labels


def merge_zones_to_budget(
    zone_labels: np.ndarray,
    active_mask: np.ndarray,
    budget: int,
) -> np.ndarray:
    """Merge the smallest zones into the largest until the number of active
    zones is at most ``budget``.

    Used to guarantee that a zonal model never consumes more EOF modes than its
    global counterpart when the zoning algorithm produces more zones than the
    retained-mode budget (e.g. rule-based zoning yielding 5 zones under B=4).
    Zone IDs are otherwise preserved.
    """
    labels = zone_labels.copy()
    active = np.asarray(active_mask, dtype=bool)
    active_labels = labels[active]
    while True:
        zids = np.unique(active_labels)
        zids = zids[zids >= 0]
        if len(zids) <= budget:
            break
        counts = {int(z): int((active_labels == z).sum()) for z in zids}
        smallest = min(counts, key=counts.get)
        largest = max(counts, key=counts.get)
        labels[active & (labels == smallest)] = largest
        active_labels = labels[active]

    # Re-map active zone IDs to a contiguous 0..K-1 range so that any IDs
    # dropped by the merge above do not leave "ghost" entries in downstream
    # visuals (e.g. a zone colorbar showing an empty, merged-away zone ID).
    unique_active = sorted(int(z) for z in np.unique(active_labels) if z >= 0)
    if unique_active != list(range(len(unique_active))):
        remap = {old_id: new_id for new_id, old_id in enumerate(unique_active)}
        for old_id, new_id in remap.items():
            labels[active & (labels == old_id)] = new_id
    return labels


# ---------------------------------------------------------------------------
# Zone labelling (for interpretable zone naming)
# ---------------------------------------------------------------------------


def label_zones_by_hydrodynamics(
    zones: np.ndarray,
    max_depth: np.ndarray,
    inundation_frequency: np.ndarray,
) -> dict[int, str]:
    """Assign human-readable names to zones based on mean statistics."""
    names = {}
    for z in sorted(set(zones) - {-1}):
        mask = zones == z
        mean_depth = np.nanmean(max_depth[mask])
        mean_freq = np.nanmean(inundation_frequency[mask])

        if mean_depth > np.nanpercentile(max_depth[max_depth > 0], 60):
            names[z] = "deep_conveyance"
        elif mean_freq > 0.6:
            names[z] = "frequent_floodplain"
        elif mean_freq > 0.2:
            names[z] = "intermittent_floodplain"
        else:
            names[z] = "fringe"
    return names


# ---------------------------------------------------------------------------
# Zone statistics
# ---------------------------------------------------------------------------


def zone_stats(
    zones: np.ndarray,
    max_depth: np.ndarray,
    inundation_frequency: np.ndarray,
    lf_hf_abs_residual: np.ndarray | None = None,
) -> dict[int, dict[str, float]]:
    """Compute per-zone summary statistics."""
    stats = {}
    for z in sorted(set(zones) - {-1}):
        mask = zones == z
        s = {
            "n_cells": int(mask.sum()),
            "fraction": float(mask.sum() / mask.size),
            "mean_max_depth": float(np.nanmean(max_depth[mask])),
            "std_max_depth": float(np.nanstd(max_depth[mask])),
            "mean_inundation_freq": float(np.nanmean(inundation_frequency[mask])),
        }
        if lf_hf_abs_residual is not None:
            s["mean_abs_residual"] = float(np.nanmean(lf_hf_abs_residual[mask]))
        stats[int(z)] = s
    return stats
