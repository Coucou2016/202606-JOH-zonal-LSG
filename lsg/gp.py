"""Gaussian Process emulators for EC mapping.

Supports gpflow (preferred) and sklearn/numpy fallback.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

try:
    import gpflow
    from sklearn.preprocessing import StandardScaler as _SklearnScaler

    _HAS_GPFLOW = True
except ImportError:
    gpflow = None
    _SklearnScaler = None
    _HAS_GPFLOW = False


@dataclass
class SparseGPMode:
    model: object
    scaler_x: object
    scaler_y: object


class _NumpyStandardScaler:
    def __init__(self) -> None:
        self.mean_: np.ndarray | None = None
        self.scale_: np.ndarray | None = None

    def fit_transform(self, x: np.ndarray) -> np.ndarray:
        self.mean_ = x.mean(axis=0)
        self.scale_ = x.std(axis=0)
        self.scale_[self.scale_ < 1e-12] = 1.0
        return (x - self.mean_) / self.scale_

    def transform(self, x: np.ndarray) -> np.ndarray:
        assert self.mean_ is not None and self.scale_ is not None
        return (x - self.mean_) / self.scale_

    def inverse_transform(self, y: np.ndarray) -> np.ndarray:
        assert self.scale_ is not None
        if y.ndim == 1:
            return y * self.scale_[0] + self.mean_[0]
        return y * self.scale_ + self.mean_


def make_scaler():
    if _HAS_GPFLOW and _SklearnScaler is not None:
        return _SklearnScaler()
    return _NumpyStandardScaler()


def inducing_points_grid(x_sc: np.ndarray, n_inducing: int) -> np.ndarray:
    """Create inducing points along a grid in the input space."""
    dim = x_sc.shape[1]
    z = np.linspace(x_sc[:, 0].min(), x_sc[:, 0].max(), n_inducing).reshape(-1, 1)
    for j in range(1, dim):
        col = np.linspace(x_sc[:, j].min(), x_sc[:, j].max(), n_inducing)
        z = np.hstack([z, col.reshape(-1, 1)])
    return z


def train_sparse_gp_gpflow(
    x_train: np.ndarray,
    y_train: np.ndarray,
    inducing_fraction: float = 0.02,
    kernel_type: str = "exponential",
) -> SparseGPMode:
    """Train a Sparse GP (SGPR) with gpflow."""
    n_inducing = max(2, round(len(x_train) * inducing_fraction))
    scaler_x = make_scaler()
    scaler_y = make_scaler()
    x_sc = scaler_x.fit_transform(x_train)
    y_sc = scaler_y.fit_transform(y_train.reshape(-1, 1))

    z = inducing_points_grid(x_sc, n_inducing)
    ini_length = float(np.mean(np.abs(x_sc)))

    if kernel_type == "exponential":
        kernel = gpflow.kernels.Exponential(variance=1.0, lengthscales=ini_length)
    elif kernel_type == "matern32":
        kernel = gpflow.kernels.Matern32(variance=1.0, lengthscales=ini_length)
    else:
        kernel = gpflow.kernels.SquaredExponential(variance=1.0, lengthscales=ini_length)

    model = gpflow.models.SGPR(
        data=(x_sc, y_sc),
        kernel=kernel,
        inducing_variable=z,
    )

    opt = gpflow.optimizers.Scipy()
    # Phase 1: fix kernel params, optimize inducing points
    for trainable in (
        model.kernel.variance,
        model.kernel.lengthscales,
        model.likelihood.variance,
    ):
        gpflow.set_trainable(trainable, False)
    opt.minimize(
        model.training_loss,
        model.trainable_variables,
        method="L-BFGS-B",
        options=dict(maxiter=100),
    )
    # Phase 2: unfreeze all
    for trainable in (
        model.kernel.variance,
        model.kernel.lengthscales,
        model.likelihood.variance,
    ):
        gpflow.set_trainable(trainable, True)
    gpflow.set_trainable(model.inducing_variable.Z, False)
    opt.minimize(
        model.training_loss,
        model.trainable_variables,
        method="L-BFGS-B",
        options=dict(maxiter=100),
    )
    return SparseGPMode(model=model, scaler_x=scaler_x, scaler_y=scaler_y)


class _RBFKernelGP:
    """Lightweight RBF GP fallback (no dependencies)."""

    def __init__(self, length_scale: float = 1.0, noise: float = 0.05) -> None:
        self.length_scale = length_scale
        self.noise = noise
        self.x_train: np.ndarray | None = None
        self.y_train: np.ndarray | None = None
        self._alpha: np.ndarray | None = None

    def _kernel(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        dist = np.sum((a[:, None, :] - b[None, :, :]) ** 2, axis=2)
        return np.exp(-0.5 * dist / (self.length_scale**2))

    def fit(self, x: np.ndarray, y: np.ndarray) -> None:
        self.x_train = x
        self.y_train = y.ravel()
        k = self._kernel(x, x) + self.noise * np.eye(len(x))
        try:
            self._alpha = np.linalg.solve(k, self.y_train)
        except np.linalg.LinAlgError:
            self._alpha = np.linalg.lstsq(k, self.y_train, rcond=None)[0]

    def predict(self, x: np.ndarray) -> np.ndarray:
        assert self.x_train is not None and self._alpha is not None
        k_star = self._kernel(x, self.x_train)
        return k_star @ self._alpha


def train_sparse_gp_numpy(x_train: np.ndarray, y_train: np.ndarray) -> _RBFKernelGP:
    model = _RBFKernelGP()
    model.fit(x_train, y_train.ravel())
    return model


def train_sparse_gp_sklearn(
    x_train: np.ndarray, y_train: np.ndarray
) -> SparseGPMode:
    """Train using sklearn GaussianProcessRegressor."""
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, WhiteKernel

    scaler_x = make_scaler()
    scaler_y = make_scaler()
    x_sc = scaler_x.fit_transform(x_train)
    y_sc = scaler_y.fit_transform(y_train.reshape(-1, 1))

    kernel = RBF(length_scale=1.0) + WhiteKernel(noise_level=0.05)
    gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=3, alpha=1e-6)
    gpr.fit(x_sc, y_sc.ravel())
    return SparseGPMode(model=gpr, scaler_x=scaler_x, scaler_y=scaler_y)


def predict_sparse_gp(mode: SparseGPMode, x: np.ndarray) -> np.ndarray:
    x_sc = mode.scaler_x.transform(x)
    model = mode.model

    if isinstance(model, _RBFKernelGP):
        return model.predict(x_sc)
    elif hasattr(model, "predict_f"):
        # gpflow
        mean, _ = model.predict_f(x_sc)
        return mode.scaler_y.inverse_transform(mean).ravel()
    else:
        # sklearn GPR with NaN safety
        try:
            mean = model.predict(x_sc)
            mean = np.nan_to_num(mean, nan=0.0, posinf=0.0, neginf=0.0)
            result = mode.scaler_y.inverse_transform(mean.reshape(-1, 1)).ravel()
            return np.nan_to_num(result, nan=0.0, posinf=0.0, neginf=0.0)
        except Exception:
            return np.zeros(len(x_sc))


def train_ec_emulator(
    lf_ecs: np.ndarray,
    hf_ecs: np.ndarray,
    inducing_fraction: float = 0.02,
    kernel_type: str = "exponential",
) -> list[SparseGPMode]:
    """Train one GP per EOF mode: LF ECs -> HF ECs."""
    modes = []
    x = lf_ecs
    n_modes = hf_ecs.shape[1]

    for i in range(n_modes):
        y = hf_ecs[:, i]
        if _HAS_GPFLOW:
            try:
                sm = train_sparse_gp_gpflow(
                    x, y,
                    inducing_fraction=inducing_fraction,
                    kernel_type=kernel_type,
                )
            except Exception:
                sm = train_sparse_gp_sklearn(x, y)
        else:
            try:
                sm = train_sparse_gp_sklearn(x, y)
            except Exception:
                scaler_x = make_scaler()
                scaler_y = make_scaler()
                x_sc = scaler_x.fit_transform(x)
                gpr = train_sparse_gp_numpy(x_sc, scaler_y.fit_transform(y.reshape(-1, 1)))
                sm = SparseGPMode(model=gpr, scaler_x=scaler_x, scaler_y=scaler_y)
        modes.append(sm)
    return modes


def predict_ec_emulator(
    modes: Sequence[SparseGPMode], lf_ecs: np.ndarray
) -> np.ndarray:
    """Predict HF expansion coefficients from LF ECs."""
    preds = [predict_sparse_gp(m, lf_ecs) for m in modes]
    return np.column_stack(preds)
