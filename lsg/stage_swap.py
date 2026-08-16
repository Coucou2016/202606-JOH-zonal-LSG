"""Stage-swap ablations: cross EOF scope × GP scope under equal mode budget.

Four LSG-Max configurations (rule zoning when zonal):

  GG — global EOF + global GP   (baseline GlobalLSG)
  ZZ — zonal  EOF + zonal  GP   (baseline ZonalLSG)
  GZ — global EOF + zonal  GP   (global modes, zone-local EC mapping)
  ZG — zonal  EOF + global GP   (zonal modes, rank-pooled shared GPs)

GZ / ZG are intentional approximations; see ``LIMITATIONS``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np

from lsg import eof, gp, spatial, zoning, zonal_eof
from lsg.baseline_lsg import GlobalLSG
from lsg.zonal_lsg import ZonalLSG
from lsg.zoning import ZoningConfig

StageId = Literal["GG", "ZZ", "GZ", "ZG"]

LIMITATIONS = (
    "GZ: each zone uses the leading n_z global EOF modes restricted to the zone "
    "and QR-orthonormalized (not native zone EOFs); n_z follows variance-share "
    "budget like ZZ. This is a strong approximation — sliced global modes can be "
    "near-null on fringe zones. ZG: zonal EOF ECs are concatenated in zone order "
    "into one length-B vector; a single Global-style GP stack maps that vector."
)


@dataclass
class _ZonePack:
    zone_id: int
    cell_mask_active: np.ndarray  # bool over wet/active cells
    modes: np.ndarray  # (n_modes, n_zone_cells)
    mean: np.ndarray
    weights: np.ndarray | None
    n_modes: int
    gp_modes: list = field(default_factory=list)


@dataclass
class StageSwapState:
    stage: StageId
    active_mask: np.ndarray
    zone_labels: np.ndarray
    packs: list[_ZonePack]
    n_modes_total: int
    wet_threshold: float = 0.03


def _rule_labels(
    hf_mat: np.ndarray,
    lf_mat: np.ndarray,
    active: np.ndarray,
    wet_threshold: float = 0.03,
) -> np.ndarray:
    max_depth = np.nanmax(hf_mat, axis=0)
    inundation_freq = np.nanmean(hf_mat >= wet_threshold, axis=0)
    lf_hf_residual = np.nanmean(np.abs(lf_mat - hf_mat), axis=0)
    return zoning.rule_based_zones(
        max_depth,
        inundation_freq,
        lf_hf_abs_residual=lf_hf_residual,
        active_mask=active,
    )


def _allocate_budget(
    zone_variances: list[float], mode_budget: int
) -> list[int]:
    """Match zonal_eof true-equal allocation (1 base + variance share)."""
    K = len(zone_variances)
    if K == 0:
        return []
    if mode_budget < K:
        return [1] * K
    total_var = sum(zone_variances) + 1e-12
    base = [1] * K
    remaining = mode_budget - K
    var_shares = [v / total_var for v in zone_variances]
    extra = [max(0, round(remaining * s)) for s in var_shares]
    diff = remaining - sum(extra)
    sorted_idx = sorted(
        range(K),
        key=lambda i: extra[i] - round(remaining * var_shares[i]),
        reverse=True,
    )
    i = 0
    while diff != 0 and i < len(sorted_idx) * 10:
        idx = sorted_idx[i % K]
        if diff > 0:
            extra[idx] += 1
            diff -= 1
        elif extra[idx] > 0:
            extra[idx] -= 1
            diff += 1
        i += 1
    return [b + e for b, e in zip(base, extra)]


def _qr_modes(modes: np.ndarray) -> np.ndarray:
    """Orthonormalize mode rows over zone cells via thin QR on transpose."""
    # modes: (k, n_cells) — want orthonormal rows in cell space
    if modes.size == 0:
        return modes
    k, n = modes.shape
    if k == 0 or n == 0:
        return modes
    # QR on (n, k) so columns are orthonormal → rows of Q.T are modes
    q, _ = np.linalg.qr(modes.T, mode="reduced")
    return q.T[:k]


def fit_stage_swap(
    hf_tr: np.ndarray,
    lf_tr: np.ndarray,
    budget: int,
    stage: StageId,
    wet_threshold: float = 0.03,
    weight_by_cell_area: bool = True,
    shape_hf: tuple[int, int] | None = None,
) -> StageSwapState:
    """Fit one stage-swap configuration on max-surface matrices (n_ev, n_cells)."""
    if stage in ("GG", "ZZ"):
        raise ValueError("Use fit_predict_stage for GG/ZZ (delegates to Global/Zonal LSG)")

    n_cells = hf_tr.shape[1]
    if shape_hf is None:
        shape_hf = (1, n_cells)

    active = spatial.wet_cell_mask(hf_tr, wet_threshold)
    hf_wet = hf_tr[:, active]
    lf_wet = lf_tr[:, active]
    areas = spatial.cell_areas_uniform(shape_hf, 1.0)
    w_full = spatial.sqrt_area_weights(areas) if weight_by_cell_area else None
    w = w_full[active] if w_full is not None else None

    labels = _rule_labels(hf_tr, lf_tr, active, wet_threshold)
    active_labels = labels[active]
    unique = sorted(int(z) for z in np.unique(active_labels))

    if stage == "GZ":
        return _fit_gz(
            hf_wet, lf_wet, labels, active, active_labels, unique, w, budget, wet_threshold
        )
    if stage == "ZG":
        return _fit_zg(
            hf_wet, lf_wet, labels, active, active_labels, unique, w, budget, wet_threshold
        )
    raise ValueError(f"unknown stage {stage}")


def _fit_gz(
    hf_wet, lf_wet, labels, active, active_labels, unique, w, budget, wet_threshold
) -> StageSwapState:
    pca, g_mean = eof.fit_eof(hf_wet, weights=w, n_components=min(30, hf_wet.shape[0]))
    n_g = min(budget, pca.n_components_)
    g_modes = pca.components_[:n_g]  # (B, n_active)

    # Per-zone variance of global reconstruction residual as allocation proxy
    zone_vars = []
    masks = []
    for zid in unique:
        m = active_labels == zid
        masks.append(m)
        if not np.any(m):
            zone_vars.append(0.0)
            continue
        # variance of HF on zone (proxy for how much structure lives there)
        zone_vars.append(float(np.var(hf_wet[:, m])))

    alloc = _allocate_budget(zone_vars, budget)
    packs: list[_ZonePack] = []
    # Each zone gets the leading n_z global modes (shared top modes), restricted
    # and QR-orthonormalized on the zone support — not a cyclic slice of weaker modes.
    for zid, m, n_z in zip(unique, masks, alloc):
        if not np.any(m) or n_z <= 0:
            continue
        n_use = min(n_z, n_g)
        raw = g_modes[:n_use][:, m]
        modes_z = _qr_modes(raw)
        mean_z = np.mean(hf_wet[:, m], axis=0)
        w_z = w[m] if w is not None else None
        hf_ecs = eof.project_pseudo_ecs(hf_wet[:, m], modes_z, w_z, mean_z)
        lf_ecs = eof.project_pseudo_ecs(lf_wet[:, m], modes_z, w_z, mean_z)
        gp_modes = gp.train_ec_emulator(lf_ecs, hf_ecs)
        packs.append(
            _ZonePack(
                zone_id=zid,
                cell_mask_active=m,
                modes=modes_z,
                mean=mean_z,
                weights=w_z,
                n_modes=int(modes_z.shape[0]),
                gp_modes=gp_modes,
            )
        )
    return StageSwapState(
        stage="GZ",
        active_mask=active,
        zone_labels=labels,
        packs=packs,
        n_modes_total=sum(p.n_modes for p in packs),
        wet_threshold=wet_threshold,
    )


def _fit_zg(
    hf_wet, lf_wet, labels, active, active_labels, unique, w, budget, wet_threshold
) -> StageSwapState:
    """Zonal EOF bases; one global GP stack on concatenated zone ECs (length B)."""
    z_state = zonal_eof.fit_zonal_eof(
        hf_wet,
        lf_wet,
        zone_labels=labels,
        active_mask=active,
        weights=w,
        max_modes_per_zone=10,
        variance_threshold=0.99,
        mode_budget=budget,
    )

    packs: list[_ZonePack] = []
    lf_blocks: list[np.ndarray] = []
    hf_blocks: list[np.ndarray] = []
    for zr in z_state.zones:
        m = active_labels == zr.zone_id
        modes_z = zr.eof_result.components_[: zr.n_modes]
        hf_ecs = eof.project_pseudo_ecs(hf_wet[:, m], modes_z, zr.weights, zr.hf_mean)
        lf_ecs = eof.project_pseudo_ecs(lf_wet[:, m], modes_z, zr.weights, zr.hf_mean)
        packs.append(
            _ZonePack(
                zone_id=zr.zone_id,
                cell_mask_active=m,
                modes=modes_z,
                mean=zr.hf_mean,
                weights=zr.weights,
                n_modes=zr.n_modes,
                gp_modes=[],  # filled after shared training
            )
        )
        lf_blocks.append(lf_ecs)
        hf_blocks.append(hf_ecs)

    lf_cat = np.hstack(lf_blocks) if lf_blocks else np.zeros((hf_wet.shape[0], 0))
    hf_cat = np.hstack(hf_blocks) if hf_blocks else np.zeros((hf_wet.shape[0], 0))
    shared = gp.train_ec_emulator(lf_cat, hf_cat)

    # Slice shared GPs back onto packs (column order = zone order above)
    col = 0
    for pack in packs:
        pack.gp_modes = shared[col : col + pack.n_modes]
        col += pack.n_modes

    return StageSwapState(
        stage="ZG",
        active_mask=active,
        zone_labels=labels,
        packs=packs,
        n_modes_total=sum(p.n_modes for p in packs),
        wet_threshold=wet_threshold,
    )


def predict_stage_swap(
    state: StageSwapState,
    lf_te: np.ndarray,
) -> np.ndarray:
    """Predict HF max surfaces for GZ/ZG."""
    lf_wet = lf_te[:, state.active_mask]
    n_s = lf_te.shape[0]
    n_act = int(state.active_mask.sum())
    recon = np.zeros((n_s, n_act), dtype=np.float64)

    if state.stage == "ZG":
        # Concatenate LF ECs → shared GP stack → split HF ECs by zone
        lf_blocks = []
        for pack in state.packs:
            lf_z = lf_wet[:, pack.cell_mask_active]
            lf_blocks.append(
                eof.project_pseudo_ecs(lf_z, pack.modes, pack.weights, pack.mean)
            )
        lf_cat = np.hstack(lf_blocks) if lf_blocks else np.zeros((n_s, 0))
        # All packs share the same GP list pieces; rebuild full shared list
        shared = []
        for pack in state.packs:
            shared.extend(pack.gp_modes)
        hf_cat = gp.predict_ec_emulator(shared, lf_cat) if shared else lf_cat
        col = 0
        for pack in state.packs:
            m = pack.cell_mask_active
            hf_ecs = hf_cat[:, col : col + pack.n_modes]
            col += pack.n_modes
            recon_z = eof.reconstruct_from_ecs(
                hf_ecs, pack.modes, pack.mean, pack.weights
            )
            recon_z = np.where(recon_z < state.wet_threshold, 0.0, recon_z)
            recon[:, m] = recon_z
    else:
        for pack in state.packs:
            m = pack.cell_mask_active
            lf_z = lf_wet[:, m]
            lf_ecs = eof.project_pseudo_ecs(lf_z, pack.modes, pack.weights, pack.mean)
            hf_ecs = gp.predict_ec_emulator(pack.gp_modes, lf_ecs)
            recon_z = eof.reconstruct_from_ecs(
                hf_ecs, pack.modes, pack.mean, pack.weights
            )
            recon_z = np.where(recon_z < state.wet_threshold, 0.0, recon_z)
            recon[:, m] = recon_z

    full = np.zeros_like(lf_te, dtype=np.float64)
    full[:, state.active_mask] = recon
    return full


def fit_predict_stage(
    hf_tr: np.ndarray,
    lf_tr: np.ndarray,
    hf_te: np.ndarray,
    lf_te: np.ndarray,
    terrain: np.ndarray,
    xy: np.ndarray,
    budget: int,
    stage: StageId,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Unified entry: GG/ZZ via existing classes; GZ/ZG via stage_swap."""
    import time

    n_hf = int(hf_tr.shape[1])
    sd = (1, n_hf)
    t0 = time.perf_counter()

    if stage == "GG":
        m = GlobalLSG(variant="max", max_eof_modes=30, eof_variance=0.99, wet_threshold=0.03)
        m.force_n_modes = budget
        m.fit(hf_tr, lf_tr, terrain, sd, sd, lf_already_interpolated=True)
        pred = m.predict(lf_te, terrain, sd, sd, lf_already_interpolated=True)
        n_modes = int(m.state.n_modes) if m.state else 0
        meta = {"stage": stage, "n_modes": n_modes, "time_s": time.perf_counter() - t0}
        return pred, meta

    if stage == "ZZ":
        zc = ZoningConfig(method="rule", n_zones=4, wet_threshold=0.03)
        m = ZonalLSG(
            zoning_config=zc,
            variant="max",
            mode_budget=budget,
            max_modes_per_zone=10,
            eof_variance=0.99,
            wet_threshold=0.03,
        )
        m.fit(hf_tr, lf_tr, terrain, sd, sd, x_hf=xy[:, 0], y_hf=xy[:, 1])
        pred = m.predict(lf_te, terrain, sd, sd)
        zs = m.get_zone_statistics() if m.state else {}
        n_modes = int(sum(v["n_modes"] for v in zs.values())) if zs else 0
        meta = {
            "stage": stage,
            "n_modes": n_modes,
            "time_s": time.perf_counter() - t0,
            "zone_stats": {str(k): v for k, v in zs.items()},
        }
        return pred, meta

    state = fit_stage_swap(hf_tr, lf_tr, budget, stage)
    pred = predict_stage_swap(state, lf_te)
    meta = {
        "stage": stage,
        "n_modes": state.n_modes_total,
        "time_s": time.perf_counter() - t0,
        "limitations": LIMITATIONS,
        "n_zones": len(state.packs),
    }
    return pred, meta
