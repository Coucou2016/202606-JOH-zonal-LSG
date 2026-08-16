"""EOF (PCA) analysis for LSG — extended with zonal support."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from sklearn.decomposition import PCA


@dataclass
class EOFResult:
    components_: np.ndarray
    explained_variance_: np.ndarray
    explained_variance_ratio_: np.ndarray
    n_components_: int
    singular_values_: np.ndarray


def temporal_mean(data: np.ndarray) -> np.ndarray:
    return np.mean(data, axis=0)


def center_data(data: np.ndarray, mean: np.ndarray | None = None) -> np.ndarray:
    mean = temporal_mean(data) if mean is None else mean
    return data - mean


def apply_weights(data: np.ndarray, weights: np.ndarray) -> np.ndarray:
    w = np.asarray(weights, dtype=np.float64).reshape(1, -1)
    return data * w


def fit_eof(
    data: np.ndarray,
    weights: np.ndarray | None = None,
    n_components: int = 100,
    hf_mean: np.ndarray | None = None,
    variance_threshold: float | None = None,
) -> tuple[EOFResult, np.ndarray]:
    """Fit EOF spatial modes via SVD on centred data.

    Parameters
    ----------
    data : (n_samples, n_cells)
    weights : optional (n_cells,) cell-area sqrt weights
    n_components : max modes to compute
    hf_mean : precomputed temporal mean
    variance_threshold : if set, returns the minimum number of modes
                          needed to explain this fraction of variance

    Returns
    -------
    (EOFResult, mean)
    """
    mean = temporal_mean(data) if hf_mean is None else hf_mean
    centred = center_data(data, mean).astype(np.float64)
    if weights is not None:
        centred = apply_weights(centred, weights)

    n_samples, n_cells = centred.shape
    k = min(n_components, n_samples, n_cells)
    u, s, vt = np.linalg.svd(centred, full_matrices=False)
    k = min(k, len(s))
    components = vt[:k]
    var = (s[:k] ** 2) / max(n_samples - 1, 1)
    total = var.sum() if var.sum() > 0 else 1.0
    result = EOFResult(
        components_=components,
        explained_variance_=var,
        explained_variance_ratio_=var / total,
        n_components_=k,
        singular_values_=s[:k],
    )
    return result, mean


def fit_eof_sklearn(
    data: np.ndarray,
    weights: np.ndarray | None = None,
    n_components: int = 100,
    hf_mean: np.ndarray | None = None,
) -> tuple[EOFResult, np.ndarray]:
    """Fit EOF using sklearn PCA (matches Fraehr et al. reference code)."""
    mean = temporal_mean(data) if hf_mean is None else hf_mean
    centred = center_data(data, mean).astype(np.float64)
    if weights is not None:
        centred = apply_weights(centred, weights)

    n_components = min(n_components, centred.shape[0], centred.shape[1])
    pca = PCA(n_components=n_components, svd_solver="auto")
    pca.fit(centred)

    result = EOFResult(
        components_=pca.components_,
        explained_variance_=pca.explained_variance_,
        explained_variance_ratio_=pca.explained_variance_ratio_,
        n_components_=pca.n_components_,
        singular_values_=pca.singular_values_,
    )
    return result, mean


def project_pseudo_ecs(
    data: np.ndarray,
    eof_modes: np.ndarray,
    weights: np.ndarray | None = None,
    hf_mean: np.ndarray | None = None,
) -> np.ndarray:
    """Project data onto EOF modes to get pseudo-expansion coefficients."""
    mean = temporal_mean(data) if hf_mean is None else hf_mean
    centred = center_data(data, mean)
    if weights is not None:
        centred = apply_weights(centred, weights)
    return centred @ eof_modes.T


def reconstruct_from_ecs(
    ecs: np.ndarray,
    eof_modes: np.ndarray,
    mean: np.ndarray,
    weights: np.ndarray | None = None,
) -> np.ndarray:
    """Reconstruct data from expansion coefficients and EOF modes."""
    recon = ecs @ eof_modes
    if weights is not None:
        w = np.asarray(weights, dtype=np.float64).reshape(1, -1)
        recon = recon / (w + 1e-12)
    return recon + mean


def norths_rule(pca: EOFResult, n_samples: int) -> int:
    """North's rule of thumb for significant EOF modes."""
    eigenvalues = pca.explained_variance_
    if len(eigenvalues) < 2:
        return len(eigenvalues)
    d_eigen = np.abs(np.diff(eigenvalues))
    d_error = np.sqrt(2.0 / n_samples) * eigenvalues[:-1]
    boundary = np.where(d_eigen <= d_error)[0]
    if len(boundary) == 0:
        return len(eigenvalues)
    return int(boundary[0])


def kaiser_significant(pca: EOFResult) -> int:
    """Kaiser criterion: eigenvalues > 1.0."""
    return int(np.sum(pca.explained_variance_ > 1.0))


def select_n_modes(pca: EOFResult, n_samples: int) -> int:
    """Select number of EOF modes by North's rule and Kaiser criterion."""
    n_north = norths_rule(pca, n_samples)
    n_kaiser = kaiser_significant(pca)
    return max(1, min(n_north, n_kaiser, pca.n_components_))


def modes_for_variance(
    pca: EOFResult, variance_threshold: float = 0.99
) -> int:
    """Number of modes needed to explain `variance_threshold` fraction."""
    cumsum = np.cumsum(pca.explained_variance_ratio_)
    n = int(np.searchsorted(cumsum, variance_threshold) + 1)
    return min(n, pca.n_components_)


def explained_variance_curve(pca: EOFResult) -> dict[str, np.ndarray]:
    """Return cumulative explained variance curve for plotting."""
    n = pca.n_components_
    return {
        "cumulative": np.cumsum(pca.explained_variance_ratio_),
        "individual": pca.explained_variance_ratio_,
        "n_modes": np.arange(1, n + 1),
    }
