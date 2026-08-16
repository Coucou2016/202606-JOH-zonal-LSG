"""Uncertainty quantification for zonal LSG predictions.

Uses GP predictive variance where available (gpflow) or ensemble spread
for sklearn/numpy fallback.
"""

from __future__ import annotations

import numpy as np


def gp_predictive_variance(
    gp_mode,
    x: np.ndarray,
) -> np.ndarray:
    """Extract GP predictive variance at test points.

    For gpflow SGPR models, returns predictive variance.
    For sklearn GPR, returns predictive std.
    For numpy fallback, returns constant placeholder.
    """
    model = gp_mode.model
    x_sc = gp_mode.scaler_x.transform(x)

    if hasattr(model, "predict_f"):
        # gpflow
        mean, var = model.predict_f(x_sc)
        var_scaled = gp_mode.scaler_y.inverse_transform(
            np.sqrt(var)
        ) ** 2
        return var_scaled.ravel()
    elif hasattr(model, "predict"):
        # sklearn
        mean, std = model.predict(x_sc, return_std=True)
        return (gp_mode.scaler_y.inverse_transform(
            std.reshape(-1, 1)
        ).ravel()) ** 2
    else:
        # numpy fallback
        return np.full(len(x), 0.01)


def ensemble_spread(
    predictions: list[np.ndarray],
) -> np.ndarray:
    """Compute ensemble standard deviation across multiple predictors."""
    stack = np.stack(predictions, axis=0)
    return np.std(stack, axis=0)


def uncertainty_zone_map(
    pred_variance: np.ndarray,
    zone_labels: np.ndarray,
    active_mask: np.ndarray,
) -> dict[int, float]:
    """Compute mean predictive variance per zone."""
    result = {}
    for z in sorted(set(zone_labels) - {-1}):
        mask = zone_labels[active_mask] == z
        if mask.any():
            result[int(z)] = float(np.mean(pred_variance[mask]))
    return result
