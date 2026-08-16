"""Zonal EOF decomposition — per-zone EOF, projection, and reconstruction."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from lsg import eof


@dataclass
class ZoneEOFResult:
    zone_id: int
    cell_indices: np.ndarray  # indices into full HF grid
    n_cells: int
    eof_result: eof.EOFResult | None = None
    hf_mean: np.ndarray | None = None
    weights: np.ndarray | None = None
    n_modes: int = 0
    explained_variance: float = 0.0


@dataclass
class ZonalEOFState:
    zones: list[ZoneEOFResult]
    inactive_idx: np.ndarray  # cells not in any zone
    total_active_cells: int
    total_eof_modes: int
    global_n_modes: int = 0  # for budget comparison


def fit_zonal_eof(
    hf_wet: np.ndarray,
    lf_wet: np.ndarray,
    zone_labels: np.ndarray,
    active_mask: np.ndarray,
    weights: np.ndarray | None = None,
    max_modes_per_zone: int = 50,
    variance_threshold: float = 0.99,
    mode_budget: int | None = None,
) -> ZonalEOFState:
    """Fit EOF separately for each hydrodynamic zone.

    Parameters
    ----------
    hf_wet : (n_samples, n_cells) HF data on all wet cells
    lf_wet : (n_samples, n_cells) LF data interpolated to all wet cells
    zone_labels : (n_total_cells,) zone ID for each cell (-1 = inactive)
    active_mask : (n_total_cells,) boolean mask of active cells
    weights : optional cell weights for EOF
    max_modes_per_zone : cap on EOF modes per zone
    variance_threshold : variance fraction to retain
    mode_budget : if set, total modes across all zones <= mode_budget

    Returns
    -------
    ZonalEOFState with fitted EOF per zone
    """
    unique_zones = sorted(set(zone_labels[active_mask]))
    n_zones = len(unique_zones)

    # First pass: fit all zones freely
    zone_results = []
    zone_variances = []
    for zid in unique_zones:
        zone_mask = zone_labels == zid
        cells_z = np.where(zone_mask)[0]

        if len(cells_z) == 0:
            continue

        hf_z = hf_wet[:, zone_mask[active_mask]]
        w_z = weights[zone_mask[active_mask]] if weights is not None else None

        pca, mean_z = eof.fit_eof(
            hf_z, weights=w_z, n_components=min(max_modes_per_zone, hf_z.shape[0], hf_z.shape[1])
        )
        n_modes = eof.modes_for_variance(pca, variance_threshold)
        n_modes = min(n_modes, max_modes_per_zone)

        zr = ZoneEOFResult(
            zone_id=zid,
            cell_indices=cells_z,
            n_cells=len(cells_z),
            eof_result=pca,
            hf_mean=mean_z,
            weights=w_z,
            n_modes=n_modes,
            explained_variance=float(
                np.sum(pca.explained_variance_ratio_[:n_modes])
            ),
        )
        zone_results.append(zr)
        zone_variances.append(float(np.sum(pca.explained_variance_[:n_modes])))

    # If mode budget is set, redistribute modes
    # TRUE equal budget: total zonal modes <= mode_budget
    # Each zone gets at least 1 mode; remaining allocated by variance share
    if mode_budget is not None and len(zone_results) > 1:
        K = len(zone_results)
        if mode_budget < K:
            # Cannot allocate: merge smallest zones or cap at 1 per zone
            # For fairness: allocate exactly 1 per zone (total = K)
            allocations = [1] * K
        else:
            total_var = sum(zone_variances) + 1e-12
            # Each zone gets 1 base mode
            base = [1] * K
            remaining = mode_budget - K
            # Allocate remaining modes by variance share
            var_shares = [v / total_var for v in zone_variances]
            extra = [max(0, round(remaining * s)) for s in var_shares]
            # Adjust to match budget exactly
            diff = remaining - sum(extra)
            sorted_idx = sorted(range(K), key=lambda i: extra[i] - round(remaining * var_shares[i]),
                               reverse=True)
            i = 0
            while diff != 0 and i < len(sorted_idx) * 10:
                idx = sorted_idx[i % K]
                if diff > 0:
                    extra[idx] += 1; diff -= 1
                elif extra[idx] > 0:
                    extra[idx] -= 1; diff += 1
                i += 1
            allocations = [b + e for b, e in zip(base, extra)]

        for zr, alloc in zip(zone_results, allocations):
            alloc = min(alloc, zr.eof_result.n_components_)
            zr.n_modes = alloc
            zr.explained_variance = float(
                np.sum(zr.eof_result.explained_variance_ratio_[:alloc])
            )

    total_modes = sum(zr.n_modes for zr in zone_results)
    return ZonalEOFState(
        zones=zone_results,
        inactive_idx=np.where(~active_mask)[0],
        total_active_cells=int(active_mask.sum()),
        total_eof_modes=total_modes,
    )


def project_zonal_ecs(
    data_wet: np.ndarray,
    zone_state: ZonalEOFState,
    active_mask: np.ndarray,
) -> dict[int, np.ndarray]:
    """Project data onto per-zone EOF bases.

    Returns dict mapping zone_id -> expansion coefficients.
    """
    ecs_dict = {}
    for zr in zone_state.zones:
        zone_mask_global = np.zeros(len(active_mask), dtype=bool)
        # Map zone cell indices to data columns
        cells_in_data = np.isin(
            np.arange(data_wet.shape[1]),
            zr.cell_indices,
        )
        data_z = data_wet[:, cells_in_data]

        w_z = zr.weights
        modes = zr.eof_result.components_[:zr.n_modes]
        ecs = eof.project_pseudo_ecs(data_z, modes, w_z, zr.hf_mean)
        ecs_dict[zr.zone_id] = ecs
    return ecs_dict


def reconstruct_zonal(
    ecs_dict: dict[int, np.ndarray],
    zone_state: ZonalEOFState,
    active_mask: np.ndarray,
    n_samples: int,
    wet_threshold: float = 0.03,
) -> np.ndarray:
    """Reconstruct full HF prediction from per-zone ECs.

    Returns (n_samples, n_active_cells) array.
    """
    recon = np.zeros((n_samples, zone_state.total_active_cells), dtype=np.float64)

    for zr in zone_state.zones:
        if zr.zone_id not in ecs_dict:
            continue
        ecs = ecs_dict[zr.zone_id]
        modes = zr.eof_result.components_[:zr.n_modes]
        recon_z = eof.reconstruct_from_ecs(ecs, modes, zr.hf_mean, zr.weights)
        recon_z = np.where(recon_z < wet_threshold, 0.0, recon_z)

        # Map back to global active-cell indices
        # Find where this zone's cells are in the active_mask
        cells_z = zr.cell_indices
        mask_in_active = np.isin(
            np.arange(len(active_mask))[active_mask],
            cells_z,
        )
        recon[:, mask_in_active] = recon_z

    return recon
