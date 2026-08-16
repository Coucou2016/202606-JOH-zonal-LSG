"""Test evaluation metrics."""
import numpy as np

from lsg.metrics import (
    rmse, mae, bias,
    contingency_table, pod, rfa, csi, far, hss,
    extent_metrics, zone_metrics, error_hotspot_metrics,
    paired_improvement,
)


def test_rmse():
    pred = np.array([1.0, 2.0, 3.0])
    ref = np.array([1.0, 2.0, 3.0])
    assert rmse(pred, ref) == 0.0


def test_mae():
    pred = np.array([0.0, 0.0])
    ref = np.array([1.0, 1.0])
    assert mae(pred, ref) == 1.0


def test_bias():
    pred = np.array([2.0, 2.0])
    ref = np.array([1.0, 1.0])
    assert bias(pred, ref) == 1.0


def test_perfect_contingency():
    pred = np.array([1.0, 0.0, 1.0, 0.0])
    ref = np.array([1.0, 0.0, 1.0, 0.0])
    ct = contingency_table(pred, ref, threshold_m=0.03)
    assert ct["hits"] == 2
    assert ct["misses"] == 0
    assert ct["false_alarms"] == 0
    assert pod(ct) == 1.0
    assert rfa(ct) == 0.0
    assert csi(ct) == 1.0


def test_extent_metrics():
    rng = np.random.default_rng(42)
    pred = rng.normal(0.1, 0.05, 100)
    ref = rng.normal(0.1, 0.05, 100)
    met = extent_metrics(pred, ref, 0.03)
    for key in ["rmse", "mae", "bias", "csi", "pod", "far", "hss"]:
        assert key in met
        assert isinstance(met[key], float)


def test_zone_metrics():
    rng = np.random.default_rng(42)
    pred = rng.normal(0.1, 0.05, (5, 100))
    ref = rng.normal(0.1, 0.05, (5, 100))
    zones = np.array([0] * 50 + [1] * 50)
    met = zone_metrics(pred, ref, zones, threshold_m=0.03)
    assert len(met) == 2
    assert 0 in met and 1 in met


def test_error_hotspot_metrics():
    pred = np.array([0.0, 0.2, 0.0, 0.5])
    ref = np.array([0.0, 0.1, 0.0, 0.1])
    err_baseline = np.abs(pred - ref)
    met = error_hotspot_metrics(
        pred, ref, error_baseline=err_baseline, hotspot_percentile=50
    )
    assert met["hotspot_n_cells"] > 0


def test_paired_improvement():
    global_met = [{"rmse": 0.10}, {"rmse": 0.12}, {"rmse": 0.11}]
    zonal_met = [{"rmse": 0.08}, {"rmse": 0.09}, {"rmse": 0.09}]
    result = paired_improvement(global_met, zonal_met, key="rmse", n_bootstrap=500)
    assert result["mean_delta"] < 0  # improvement
    assert "ci_lower" in result
    assert "ci_upper" in result
