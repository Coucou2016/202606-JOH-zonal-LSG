"""Global LSG (baseline) — unified class for LSG-TS and LSG-Max."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from lsg import eof, gp, spatial


@dataclass
class LSGState:
    wet_idx: np.ndarray
    hf_mean: np.ndarray
    eof_modes: np.ndarray
    weights: np.ndarray | None
    n_modes: int
    gp_modes: list = field(default_factory=list)
    shape_hf: tuple[int, int] = (0, 0)
    shape_lf: tuple[int, int] = (0, 0)
    use_sklearn_fallback: bool = False
    training_time_s: float = 0.0


class GlobalLSG:
    """Global LSG model (standard LSG-TS and LSG-Max)."""

    def __init__(
        self,
        variant: str = "ts",
        weight_by_cell_area: bool = True,
        max_eof_modes: int = 100,
        eof_variance: float = 0.99,
        inducing_point_fraction: float = 0.02,
        gp_kernel: str = "exponential",
        wet_threshold: float = 0.03,
    ):
        if variant not in ("ts", "max"):
            raise ValueError(f"variant must be 'ts' or 'max', got {variant}")
        self.variant = variant
        self.weight_by_cell_area = weight_by_cell_area
        self.max_eof_modes = max_eof_modes
        self.eof_variance = eof_variance
        self.inducing_point_fraction = inducing_point_fraction
        self.gp_kernel = gp_kernel
        self.wet_threshold = wet_threshold
        self.state: LSGState | None = None

    def fit(
        self,
        hf_depth: np.ndarray,
        lf_depth: np.ndarray,
        terrain_hf: np.ndarray,
        shape_hf: tuple[int, int],
        shape_lf: tuple[int, int],
        lf_already_interpolated: bool = False,
    ) -> LSGState:
        """Fit global LSG model.

        hf_depth: (n_events, n_timesteps, n_hf_cells) for TS
                  (n_events, n_hf_cells) for max
        lf_already_interpolated: if True, lf_depth is already on HF grid
        """
        t0 = time.perf_counter()

        # Build training matrices
        if self.variant == "ts":
            n_ev, n_t, _ = hf_depth.shape
            hf_mat = hf_depth.reshape(n_ev * n_t, -1)
            lf_mat = lf_depth.reshape(n_ev * n_t, -1)
        else:
            hf_mat = hf_depth.max(axis=1) if hf_depth.ndim == 3 else hf_depth
            lf_mat = lf_depth.max(axis=1) if lf_depth.ndim == 3 else lf_depth

        # Wet mask
        wet = spatial.wet_cell_mask(hf_mat, self.wet_threshold)
        hf_wet = hf_mat[:, wet]

        # Interpolate LF to HF grid
        if lf_already_interpolated or lf_mat.shape[1] == hf_mat.shape[1]:
            lf_interp = lf_mat  # Already on HF grid
        else:
            lf_interp = spatial.interpolate_lf_to_hf_grid(
                lf_mat, shape_lf, shape_hf, terrain_hf
            )
        lf_wet = lf_interp[:, wet]

        # Cell-area weights
        areas = spatial.cell_areas_uniform(shape_hf, 1.0)  # default to uniform
        w = spatial.sqrt_area_weights(areas[wet]) if self.weight_by_cell_area else None

        # EOF
        pca, hf_mean = eof.fit_eof(
            hf_wet, weights=w, n_components=self.max_eof_modes
        )
        n_modes = eof.modes_for_variance(pca, self.eof_variance)
        # If force_n_modes is set (true equal-budget experiment), use it
        if hasattr(self, 'force_n_modes') and self.force_n_modes is not None:
            n_modes = min(self.force_n_modes, pca.n_components_)
        else:
            n_modes = min(n_modes, eof.select_n_modes(pca, hf_wet.shape[0]))
        modes = pca.components_[:n_modes]

        # Project to ECs
        hf_ecs = eof.project_pseudo_ecs(hf_wet, modes, w, hf_mean)
        lf_ecs = eof.project_pseudo_ecs(lf_wet, modes, w, hf_mean)

        # Train GP per mode
        gp_modes = gp.train_ec_emulator(
            lf_ecs, hf_ecs,
            inducing_fraction=self.inducing_point_fraction,
            kernel_type=self.gp_kernel,
        )

        training_time = time.perf_counter() - t0
        self.state = LSGState(
            wet_idx=np.where(wet)[0],
            hf_mean=hf_mean,
            eof_modes=modes,
            weights=w,
            n_modes=n_modes,
            gp_modes=gp_modes,
            shape_hf=shape_hf,
            shape_lf=shape_lf,
            training_time_s=training_time,
        )
        return self.state

    def predict(
        self,
        lf_depth: np.ndarray,
        terrain_hf: np.ndarray,
        shape_hf: tuple[int, int],
        shape_lf: tuple[int, int],
        lf_already_interpolated: bool = False,
    ) -> np.ndarray:
        """Predict HF depth."""
        if self.state is None:
            raise RuntimeError("Model not fitted.")

        if self.variant == "ts":
            n_ev, n_t, _ = lf_depth.shape
            lf_flat = lf_depth.reshape(n_ev * n_t, -1)
        else:
            lf_flat = lf_depth.max(axis=1) if lf_depth.ndim == 3 else lf_depth

        # Interpolate LF
        if lf_already_interpolated or lf_flat.shape[1] == shape_hf[0] * shape_hf[1]:
            lf_interp = lf_flat
        else:
            lf_interp = spatial.interpolate_lf_to_hf_grid(
                lf_flat, shape_lf, shape_hf, terrain_hf
            )
        lf_wet = lf_interp[:, self.state.wet_idx]

        # Project to ECs
        lf_ecs = eof.project_pseudo_ecs(
            lf_wet, self.state.eof_modes, self.state.weights, self.state.hf_mean
        )

        # GP predict
        hf_ecs = gp.predict_ec_emulator(self.state.gp_modes, lf_ecs)

        # Reconstruct
        recon_wet = eof.reconstruct_from_ecs(
            hf_ecs, self.state.eof_modes, self.state.hf_mean, self.state.weights
        )

        # Threshold
        recon_wet = np.where(recon_wet < self.wet_threshold, 0.0, recon_wet)

        # Full domain
        full = np.zeros((lf_flat.shape[0], shape_hf[0] * shape_hf[1]), dtype=np.float64)
        full[:, self.state.wet_idx] = recon_wet

        if self.variant == "ts":
            return full.reshape(n_ev, n_t, -1)
        return full

    def save(self, path: Path) -> None:
        if self.state is None:
            raise RuntimeError("Nothing to save.")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            path,
            wet_idx=self.state.wet_idx,
            hf_mean=self.state.hf_mean,
            eof_modes=self.state.eof_modes,
            weights=self.state.weights if self.state.weights is not None else np.array([]),
            n_modes=self.state.n_modes,
            shape_hf=np.array(self.state.shape_hf),
            shape_lf=np.array(self.state.shape_lf),
            variant=self.variant,
            training_time_s=self.state.training_time_s,
        )

    def load(self, path: Path) -> LSGState:
        raw = np.load(path, allow_pickle=True)
        w = raw["weights"]
        weights = w if w.size else None
        self.state = LSGState(
            wet_idx=raw["wet_idx"],
            hf_mean=raw["hf_mean"],
            eof_modes=raw["eof_modes"],
            weights=weights,
            n_modes=int(raw["n_modes"]),
            shape_hf=tuple(raw["shape_hf"].tolist()),
            shape_lf=tuple(raw["shape_lf"].tolist()),
            training_time_s=float(raw.get("training_time_s", 0)),
        )
        return self.state
