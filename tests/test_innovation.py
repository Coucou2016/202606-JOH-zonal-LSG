"""EOI, Fraehr protocol metrics, unstructured coarsening, channel zoning."""
import numpy as np
import pytest

from lsg.adaptive_resolution import coarsen_unstructured_mesh
from lsg.eoi import compute_eoi, eoi_from_max_surfaces
from lsg.fraehr_metrics import (
    convert_depth_to_binary,
    fidelity_index,
    max_surface_protocol_metrics,
    pod_rfa_csi,
    rmse_,
    ws2wd,
)
from lsg.spatial import densify_polyline, distance_to_path
from lsg.zoning import channel_distance_zones, rule_based_zones


def test_eoi_high_when_zones_separated():
    n = 200
    resid = np.concatenate([np.full(100, 0.01), np.full(100, 0.40)])
    labels = np.concatenate([np.zeros(100, dtype=int), np.ones(100, dtype=int)])
    out = compute_eoi(resid, labels)
    assert out["eoi"] > 0.9
    assert out["interpretation"] == "exploratory_diagnostic_no_threshold"


def test_eoi_low_when_residual_is_noise():
    rng = np.random.default_rng(0)
    resid = rng.normal(0.2, 0.02, 400)
    labels = np.repeat(np.arange(4), 100)
    out = compute_eoi(resid, labels)
    assert out["eoi"] < 0.15


def test_eoi_from_max_surfaces_shape():
    rng = np.random.default_rng(1)
    hf = np.clip(rng.normal(0.5, 0.3, (6, 80)), 0, None)
    lf = hf + rng.normal(0, 0.05, hf.shape)
    lf[:, :20] += 0.4
    rec = eoi_from_max_surfaces(hf, lf)
    assert rec["n_train_events"] == 6
    assert 0.0 <= rec["eoi"] <= 1.0 + 1e-6


def test_rmse_and_ws2wd():
    assert rmse_(np.array([1.0, 2.0]), np.array([1.0, 2.0])) == 0.0
    wd = ws2wd(np.array([10.0, 10.05]), np.array([10.0, 10.0]))
    assert wd[0] == 0.0
    assert wd[1] == pytest.approx(0.05)


def test_pod_rfa_csi_perfect():
    a = np.array([1, 1, 0, 0])
    pod, rfa, csi = pod_rfa_csi(a, a)
    assert pod == 1.0
    assert rfa == 0.0
    assert csi == pytest.approx(1.0)


def test_max_surface_protocol_metrics():
    ref = np.array([0.0, 1.0, 2.0, 0.0])
    pred = np.array([0.0, 1.0, 2.0, 0.0])
    m = max_surface_protocol_metrics(pred, ref, wet_idx=np.array([1, 2]))
    assert m["maxwd_r2"] == pytest.approx(1.0)
    assert m["rmse_wet"] == pytest.approx(0.0)
    assert m["csi"] == pytest.approx(1.0)
    assert m["n_wet"] == 2


def test_fidelity_index_perfect_series():
    t = np.linspace(0, 1, 20)[:, None] + np.zeros((20, 3))
    fi = fidelity_index(t, t, wd_tol=0.05, time_tol=0.05)
    assert fi == pytest.approx(1.0)


def test_convert_depth_binary():
    b = convert_depth_to_binary(np.array([0.0, 0.02, 0.04]), 0.03)
    assert list(b) == [0, 0, 1]


def test_channel_distance_zones_four_bands():
    d = np.linspace(0, 100, 200)
    active = np.ones(200, dtype=bool)
    labels = channel_distance_zones(d, active_mask=active, n_zones=4)
    assert set(labels) == {0, 1, 2, 3}
    assert labels[0] == 0
    assert labels[-1] == 3


def test_rule_based_near_channel_override():
    n = 100
    max_depth = np.full(n, 0.2)
    freq = np.full(n, 0.5)
    dist = np.linspace(0, 50, n)
    active = np.ones(n, dtype=bool)
    base = rule_based_zones(max_depth, freq, active_mask=active)
    over = rule_based_zones(max_depth, freq, distance_to_flow=dist, active_mask=active)
    assert (over == 0).sum() > (base == 0).sum()


def test_coarsen_unstructured_reduces_cells():
    rng = np.random.default_rng(2)
    x = rng.uniform(0, 100, 400)
    y = rng.uniform(0, 100, 400)
    v = rng.normal(1.0, 0.1, (3, 400))
    out, xc, yc = coarsen_unstructured_mesh(v, x, y, factor=4)
    assert out.shape[0] == 3
    assert out.shape[1] < 400
    assert xc.size == out.shape[1]


def test_densify_polyline_spacing():
    px = np.array([0.0, 10.0])
    py = np.array([0.0, 0.0])
    xs, ys = densify_polyline(px, py, spacing=2.0)
    step = np.diff(xs)
    assert step.max() <= 2.0 + 1e-9
    xs2, ys2 = densify_polyline(px, py, spacing=0.25)
    d = distance_to_path(np.array([0.0, 5.0]), np.array([1.0, 1.0]), xs2, ys2)
    assert d[0] == pytest.approx(1.0, abs=0.05)
    assert d[1] == pytest.approx(1.0, abs=0.05)


def test_principal_angles_identical():
    from lsg.eoi import principal_angles_deg

    rng = np.random.default_rng(0)
    U = rng.normal(size=(50, 3))
    Qu, _ = np.linalg.qr(U)
    ang = principal_angles_deg(Qu, Qu)
    assert np.all(ang < 1e-6)


def test_principal_angles_orthogonal():
    from lsg.eoi import principal_angles_deg

    U = np.eye(10, 2)
    V = np.zeros((10, 2))
    V[2, 0] = 1.0
    V[3, 1] = 1.0
    ang = principal_angles_deg(U, V)
    assert np.all(ang > 89.0)


def test_modal_subspace_on_synthetic():
    from lsg.eoi import modal_subspace_diagnostic

    rng = np.random.default_rng(3)
    n_ev, n = 8, 120
    left = np.sin(np.linspace(0, 2 * np.pi, 60))
    right = np.cos(np.linspace(0, 4 * np.pi, 60))
    hf = np.zeros((n_ev, n))
    for e in range(n_ev):
        a, b = 1.5 + rng.random(), 0.2 + 0.3 * rng.random()
        hf[e, :60] = np.clip(a * (0.8 + 0.2 * left) + 0.02 * rng.normal(size=60), 0.1, None)
        if e % 2 == 0:
            hf[e, 60:] = np.clip(b * (0.5 + 0.5 * right) + 0.01 * rng.normal(size=60), 0.04, None)
        else:
            hf[e, 60:] = 0.0
    rec = modal_subspace_diagnostic(hf, budget=4)
    assert rec["n_zones"] >= 2
    assert np.isfinite(rec["mean_zgg"])
    assert np.isfinite(rec["oracle_delta_rmse"])
    assert "zone_zgg" in rec


def test_stage_swap_four_arms_synthetic():
    """GZ/ZG run and return finite RMSE under equal budget on a tiny field."""
    from lsg.stage_swap import fit_predict_stage

    rng = np.random.default_rng(5)
    n_ev, n = 6, 80
    xy = np.column_stack([np.arange(n), np.zeros(n)])
    terrain = np.zeros(n)
    hf = np.zeros((n_ev, n))
    for e in range(n_ev):
        hf[e, :40] = 0.5 + 0.3 * rng.random() + 0.05 * rng.normal(size=40)
        hf[e, 40:] = 0.08 + 0.04 * rng.random(size=40)
    lf = hf + rng.normal(0, 0.03, hf.shape)
    lf[:, :40] += 0.1
    lf = np.clip(lf, 0, None)
    tr, te = [0, 1, 2, 3], [4, 5]
    for stage in ("GG", "ZZ", "GZ", "ZG"):
        pred, meta = fit_predict_stage(
            hf[tr], lf[tr], hf[te], lf[te], terrain, xy, budget=4, stage=stage
        )
        assert pred.shape == (2, n)
        assert np.isfinite(pred).all()
        assert meta["n_modes"] >= 1
