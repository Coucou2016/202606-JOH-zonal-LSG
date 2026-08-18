"""Zonal LSG — hydrodynamically zoned EOF-GP learning.

Core class that integrates zoning, zonal EOF, and zonal GP mapping
into a unified multi-fidelity emulator.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from lsg import eof, gp, spatial, zoning, zonal_eof


@dataclass
class ZonalLSGState:
    zone_labels: np.ndarray
    active_mask: np.ndarray
    eof_state: zonal_eof.ZonalEOFState
    gp_modes_by_zone: dict[int, list]
    shape_hf: tuple[int, int]
    shape_lf: tuple[int, int]
    training_time_s: float = 0.0
    variant: str = "ts"
    wet_threshold: float = 0.03


class ZonalLSG:
    """Hydrodynamically zoned LSG emulator."""

    def __init__(
        self,
        zoning_config: zoning.ZoningConfig | None = None,
        variant: str = "ts",
        weight_by_cell_area: bool = True,
        max_modes_per_zone: int = 50,
        eof_variance: float = 0.99,
        mode_budget: int | None = None,  # "free" -> None, "global_equal" -> int
        inducing_point_fraction: float = 0.02,
        gp_kernel: str = "exponential",
        wet_threshold: float = 0.03,
        random_state: int = 42,
    ):
        if variant not in ("ts", "max"):
            raise ValueError(f"variant must be 'ts' or 'max', got {variant}")
        self.zoning_config = zoning_config or zoning.ZoningConfig()
        self.variant = variant
        self.weight_by_cell_area = weight_by_cell_area
        self.max_modes_per_zone = max_modes_per_zone
        self.eof_variance = eof_variance
        self.mode_budget = mode_budget
        self.inducing_point_fraction = inducing_point_fraction
        self.gp_kernel = gp_kernel
        self.wet_threshold = wet_threshold
        self.random_state = random_state
        self.state: ZonalLSGState | None = None

    def fit(
        self,
        hf_depth: np.ndarray,
        lf_depth: np.ndarray,
        terrain_hf: np.ndarray,
        shape_hf: tuple[int, int],
        shape_lf: tuple[int, int],
        x_hf: np.ndarray | None = None,
        y_hf: np.ndarray | None = None,
        distance_to_flow: np.ndarray | None = None,
    ) -> ZonalLSGState:
        """Fit zonal LSG model.

        Parameters
        ----------
        hf_depth : (n_events, n_timesteps, n_cells) or (n_events, n_cells)
        lf_depth : same shape as hf_depth but on LF grid
        terrain_hf : (n_cells,) terrain on HF grid
        shape_hf, shape_lf : 2D grid shapes
        x_hf, y_hf : optional cell coordinates for feature building
        distance_to_flow : optional distance-to-main-flow-path
        """
        t0 = time.perf_counter()
        zc = self.zoning_config

        # Build training matrices
        if self.variant == "ts":
            n_ev, n_t, _ = hf_depth.shape
            hf_mat = hf_depth.reshape(n_ev * n_t, -1)
            lf_mat = lf_depth.reshape(n_ev * n_t, -1)
        else:
            hf_mat = hf_depth.max(axis=1) if hf_depth.ndim == 3 else hf_depth
            lf_mat = lf_depth.max(axis=1) if lf_depth.ndim == 3 else lf_depth

        # Wet mask
        active = spatial.wet_cell_mask(hf_mat, self.wet_threshold)
        n_total = active.size

        # Interpolate LF to HF
        lf_already_interp = lf_mat.shape[1] == shape_hf[0] * shape_hf[1]
        if lf_already_interp:
            lf_interp = lf_mat
        else:
            lf_interp = spatial.interpolate_lf_to_hf_grid(
                lf_mat, shape_lf, shape_hf, terrain_hf
            )

        # Build cell features for zoning
        if x_hf is None:
            x_hf = np.arange(n_total)
        if y_hf is None:
            y_hf = np.arange(n_total)

        features = zoning.build_cell_features(
            x_hf, y_hf,
            hf_depth if self.variant == "ts" else hf_mat,
            lf_interp if self.variant == "ts" else None,
            terrain=terrain_hf,
            distance_to_flow=distance_to_flow,
        )

        # --- Zoning ---
        if zc.method == "global":
            zone_labels = zoning.global_zones(n_total, active)
        elif zc.method == "rule":
            max_depth = np.nanmax(hf_mat, axis=0)
            inundation_freq = np.nanmean(hf_mat >= self.wet_threshold, axis=0)
            lf_hf_residual = np.nanmean(np.abs(lf_interp - hf_mat), axis=0)
            zone_labels = zoning.rule_based_zones(
                max_depth, inundation_freq,
                lf_hf_abs_residual=lf_hf_residual,
                distance_to_flow=distance_to_flow if zc.use_channel_distance else None,
                active_mask=active,
                deep_percentile=zc.deep_percentile,
                error_percentile=zc.error_percentile,
                frequent_threshold=zc.frequent_threshold,
                intermittent_lower=zc.intermittent_lower,
                near_channel_percentile=zc.near_channel_percentile,
            )
        elif zc.method == "channel":
            if distance_to_flow is None:
                raise ValueError("zoning method 'channel' requires distance_to_flow")
            inundation_freq = np.nanmean(hf_mat >= self.wet_threshold, axis=0)
            zone_labels = zoning.channel_distance_zones(
                distance_to_flow,
                inundation_frequency=inundation_freq,
                active_mask=active,
                n_zones=zc.n_zones,
            )
        elif zc.method == "kmeans":
            zone_labels = zoning.kmeans_zones(
                features, active, n_zones=zc.n_zones,
                random_state=zc.random_state,
            )
        elif zc.method == "agglomerative":
            zone_labels = zoning.agglomerative_zones(
                features, active, n_zones=zc.n_zones,
            )
        else:
            raise ValueError(f"Unknown zoning method: {zc.method}")

        # --- Cell weights ---
        n_hf_cells = shape_hf[0] * shape_hf[1]
        areas_hf = spatial.cell_areas_uniform(shape_hf, 1.0)
        w_full = spatial.sqrt_area_weights(areas_hf) if self.weight_by_cell_area else None
        w = w_full[active] if w_full is not None else None

        # --- Zonal EOF ---
        hf_wet = hf_mat[:, active]
        lf_wet = lf_interp[:, active]

        # Compute global n_modes for budget
        global_pca, _ = eof.fit_eof(
            hf_wet, weights=w, n_components=self.max_modes_per_zone
        )
        global_n = eof.modes_for_variance(global_pca, self.eof_variance)
        global_n = min(global_n, eof.select_n_modes(global_pca, hf_wet.shape[0]))

        # Determine mode budget
        if self.mode_budget is not None and isinstance(self.mode_budget, int):
            budget = self.mode_budget
        elif self.mode_budget == "global_equal" or (
            isinstance(self.mode_budget, str) and self.mode_budget == "global_equal"
        ):
            budget = global_n
        else:
            budget = None

        # Enforce the total-mode budget at the zoning level: if the zoning
        # produced more active zones than the budget, merge the smallest zones
        # so the zonal model never exceeds its global counterpart's capacity.
        if budget is not None:
            zone_labels = zoning.merge_zones_to_budget(zone_labels, active, budget)

        eof_state = zonal_eof.fit_zonal_eof(
            hf_wet, lf_wet,
            zone_labels=zone_labels,
            active_mask=active,
            weights=w,
            max_modes_per_zone=self.max_modes_per_zone,
            variance_threshold=self.eof_variance,
            mode_budget=budget,
        )
        eof_state.global_n_modes = global_n

        # --- Zonal GP training ---
        gp_by_zone = {}
        for zr in eof_state.zones:
            zone_mask_global = zone_labels[active] == zr.zone_id

            # Get zone data
            hf_z = hf_wet[:, zone_mask_global]
            lf_z = lf_wet[:, zone_mask_global]
            w_z = w[zone_mask_global] if w is not None else None

            modes_z = zr.eof_result.components_[:zr.n_modes]
            hf_ecs = eof.project_pseudo_ecs(hf_z, modes_z, w_z, zr.hf_mean)
            lf_ecs = eof.project_pseudo_ecs(lf_z, modes_z, w_z, zr.hf_mean)

            gp_modes = gp.train_ec_emulator(
                lf_ecs, hf_ecs,
                inducing_fraction=self.inducing_point_fraction,
                kernel_type=self.gp_kernel,
            )
            gp_by_zone[zr.zone_id] = gp_modes

        training_time = time.perf_counter() - t0
        self.state = ZonalLSGState(
            zone_labels=zone_labels,
            active_mask=active,
            eof_state=eof_state,
            gp_modes_by_zone=gp_by_zone,
            shape_hf=shape_hf,
            shape_lf=shape_lf,
            training_time_s=training_time,
            variant=self.variant,
            wet_threshold=self.wet_threshold,
        )
        return self.state

    def predict(
        self,
        lf_depth: np.ndarray,
        terrain_hf: np.ndarray,
        shape_hf: tuple[int, int],
        shape_lf: tuple[int, int],
    ) -> np.ndarray:
        """Predict HF depth using zonal LSG."""
        if self.state is None:
            raise RuntimeError("Model not fitted.")
        st = self.state

        if self.variant == "ts":
            n_ev, n_t, _ = lf_depth.shape
            lf_flat = lf_depth.reshape(n_ev * n_t, -1)
        else:
            lf_flat = lf_depth.max(axis=1) if lf_depth.ndim == 3 else lf_depth

        # Interpolate LF
        lf_already = lf_flat.shape[1] == shape_hf[0] * shape_hf[1]
        if lf_already:
            lf_interp = lf_flat
        else:
            lf_interp = spatial.interpolate_lf_to_hf_grid(
                lf_flat, shape_lf, shape_hf, terrain_hf
            )
        lf_wet = lf_interp[:, st.active_mask]
        n_samples = lf_flat.shape[0]
        n_active = int(st.active_mask.sum())

        recon_active = np.zeros((n_samples, n_active), dtype=np.float64)

        # Predict per zone
        for zr in st.eof_state.zones:
            zid = zr.zone_id
            zone_mask = st.zone_labels[st.active_mask] == zid
            n_zone_cells = int(zone_mask.sum())

            if n_zone_cells == 0:
                continue

            lf_z = lf_wet[:, zone_mask]
            w_z = st.eof_state.zones[
                [i for i, z in enumerate(st.eof_state.zones) if z.zone_id == zid][0]
            ].weights

            modes_z = zr.eof_result.components_[:zr.n_modes]
            lf_ecs = eof.project_pseudo_ecs(lf_z, modes_z, w_z, zr.hf_mean)

            gp_modes = st.gp_modes_by_zone[zid]
            hf_ecs = gp.predict_ec_emulator(gp_modes, lf_ecs)

            recon_z = eof.reconstruct_from_ecs(
                hf_ecs, modes_z, zr.hf_mean, w_z
            )
            recon_z = np.where(recon_z < self.wet_threshold, 0.0, recon_z)
            recon_active[:, zone_mask] = recon_z

        # Full domain reconstruction
        n_total = shape_hf[0] * shape_hf[1]
        full = np.zeros((n_samples, n_total), dtype=np.float64)
        full[:, st.active_mask] = recon_active

        if self.variant == "ts":
            return full.reshape(n_ev, n_t, -1)
        return full

    def get_zone_statistics(self) -> dict[int, dict[str, float]]:
        """Return per-zone EOF and cell statistics."""
        if self.state is None:
            raise RuntimeError("Model not fitted.")
        st = self.state
        active_labels = st.zone_labels[st.active_mask]

        stats = {}
        for zr in st.eof_state.zones:
            mask = active_labels == zr.zone_id
            stats[zr.zone_id] = {
                "n_cells": int(mask.sum()),
                "n_modes": zr.n_modes,
                "explained_variance": zr.explained_variance,
            }
        return stats

    def save(self, path: Path) -> None:
        if self.state is None:
            raise RuntimeError("Nothing to save.")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            path,
            zone_labels=self.state.zone_labels,
            active_mask=self.state.active_mask,
            shape_hf=np.array(self.state.shape_hf),
            shape_lf=np.array(self.state.shape_lf),
            training_time_s=self.state.training_time_s,
            variant=self.state.variant,
            wet_threshold=self.state.wet_threshold,
        )
        # Save EOF state and GP modes separately
        eof_path = path.with_suffix(".eof.npz")
        np.savez_compressed(
            eof_path,
            **{
                f"zone_{zr.zone_id}_cells": zr.cell_indices
                for zr in self.state.eof_state.zones
            },
            **{
                f"zone_{zr.zone_id}_modes": zr.eof_result.components_[:zr.n_modes]
                for zr in self.state.eof_state.zones
            },
            **{
                f"zone_{zr.zone_id}_mean": zr.hf_mean
                for zr in self.state.eof_state.zones
            },
            total_modes=self.state.eof_state.total_eof_modes,
            global_n_modes=self.state.eof_state.global_n_modes,
        )

    def load(self, path: Path) -> ZonalLSGState:
        raw = np.load(path, allow_pickle=True)
        self.state = ZonalLSGState(
            zone_labels=raw["zone_labels"],
            active_mask=raw["active_mask"].astype(bool),
            eof_state=None,  # would need full reconstruction
            gp_modes_by_zone={},
            shape_hf=tuple(raw["shape_hf"].tolist()),
            shape_lf=tuple(raw["shape_lf"].tolist()),
            training_time_s=float(raw.get("training_time_s", 0)),
            variant=str(raw.get("variant", "ts")),
            wet_threshold=float(raw.get("wet_threshold", 0.03)),
        )
        return self.state
