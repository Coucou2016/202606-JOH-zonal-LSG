#!/usr/bin/env python
"""Qualitative / spatial LSG-Max maps from real HF/LF packs (Fraehr-style).

Produces inundation panels, hit/miss CSI maps, residual maps, zone overlays,
and wet-cell obs-vs-pred scatter — only when real max-surface packs + geometry
are loadable. Never synthesizes flood fields.

Style: imports apply_style / save helpers from 97_scienceplots_figures.py
(SciencePlots science+ieee+no-latex, Times New Roman, English labels, 600 dpi).

Run:
  D:\\miniforge3\\envs\\hydromodel\\python.exe scripts/97b_spatial_maps.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from lsg.experiment import fit_predict_max  # noqa: E402
from lsg.fraehr import (  # noqa: E402
    cache_path,
    load_burnett_max_pack,
    load_case_geometry,
    load_or_build_carlisle_max,
    load_or_build_chowilla_max,
)
from lsg.metrics_area import area_weighted_metrics  # noqa: E402

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "sp97", ROOT / "scripts" / "97_scienceplots_figures.py"
)
_sp97 = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_sp97)
apply_style = _sp97.apply_style
save = _sp97.save
W2 = _sp97.W2
FIG = _sp97.FIG

WET = 0.03
BUDGET = 4
MANIFEST: dict[str, Any] = {"generated": [], "skipped": [], "notes": []}


def _log_skip(name: str, reason: str) -> None:
    msg = f"{name}: {reason}"
    MANIFEST["skipped"].append({"figure": name, "reason": reason})
    print(f"SKIP [{name}] {reason}")


def _log_ok(name: str, meta: dict[str, Any]) -> None:
    MANIFEST["generated"].append({"figure": name, **meta})
    print(f"OK   [{name}] {meta}")


def load_pack(case: str) -> dict[str, Any] | None:
    """Load HF/LF max surfaces already on the HF mesh + geometry."""
    try:
        if case == "carlisle":
            if not cache_path(ROOT, "carlisle").exists():
                _log_skip("pack:carlisle", "missing data/processed/carlisle_9events.npz")
                return None
            pack = load_or_build_carlisle_max(ROOT, max_events=9)
        elif case == "burnettrv":
            if not cache_path(ROOT, "burnettrv").exists():
                _log_skip("pack:burnettrv", "missing data/processed/burnettrv_30events.npz")
                return None
            pack = load_burnett_max_pack(ROOT)
        elif case == "chowilla":
            if not cache_path(ROOT, "chowilla").exists():
                _log_skip("pack:chowilla", "missing data/processed/chowilla_29events.npz")
                return None
            pack = load_or_build_chowilla_max(ROOT, max_events=None)
        else:
            return None
    except Exception as e:
        _log_skip(f"pack:{case}", f"{type(e).__name__}: {e}")
        return None

    geo = load_case_geometry(ROOT, case)
    x, y = np.asarray(geo["x_hf"]), np.asarray(geo["y_hf"])
    terrain = np.asarray(geo["terrain_hf"])
    areas = np.asarray(geo["area_hf"])
    hf = np.asarray(pack["hf_max"], dtype=np.float64)
    lf = np.asarray(pack["lf_max"], dtype=np.float64)
    if hf.shape[1] != x.size:
        _log_skip(f"pack:{case}", f"n_cells mismatch hf={hf.shape[1]} geo={x.size}")
        return None
    event_ids = pack.get("event_ids")
    if event_ids is None:
        event_ids = [f"ev{i}" for i in range(hf.shape[0])]
    else:
        event_ids = [str(e) for e in np.asarray(event_ids).tolist()]
    return {
        "case": case,
        "hf": hf,
        "lf": lf,
        "x": x,
        "y": y,
        "terrain": terrain,
        "areas": areas,
        "xy": np.column_stack([x, y]),
        "event_ids": event_ids,
        "source": str(pack.get("source", "fraehr2024")),
        "cache": str(cache_path(ROOT, case)),
    }


def grid_index(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, float, float, float, float]:
    """Map cell centres to (row, col) for a regular Cartesian mesh."""
    ux = np.unique(x)
    uy = np.unique(y)
    dx = float(np.median(np.diff(ux))) if len(ux) > 1 else 1.0
    dy = float(np.median(np.diff(uy))) if len(uy) > 1 else 1.0
    # Exact membership for Carlisle-like full rectangles
    if abs(len(ux) * len(uy) - x.size) <= 1:
        x_to_i = {v: i for i, v in enumerate(ux)}
        y_to_j = {v: j for j, v in enumerate(uy)}
        cols = np.fromiter((x_to_i[v] for v in x), dtype=np.int32, count=x.size)
        rows = np.fromiter((y_to_j[v] for v in y), dtype=np.int32, count=y.size)
        return rows, cols, float(ux.min()), float(ux.max()), float(uy.min()), float(uy.max())
    # Sparse regular (Burnett): round to nearest grid node
    cols = np.rint((x - ux.min()) / dx).astype(np.int32)
    rows = np.rint((y - uy.min()) / dy).astype(np.int32)
    return rows, cols, float(ux.min()), float(ux.max()), float(uy.min()), float(uy.max())


def to_raster(
    values: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    *,
    max_side: int = 1400,
) -> tuple[np.ndarray, tuple[float, float, float, float]]:
    """Scatter field → 2-D array (NaN dry/empty). Optionally decimate for memory."""
    rows, cols, xmin, xmax, ymin, ymax = grid_index(x, y)
    nr, nc = int(rows.max()) + 1, int(cols.max()) + 1
    # Decimate very large rasters for plotting (keep aspect)
    step = 1
    if max(nr, nc) > max_side:
        step = int(np.ceil(max(nr, nc) / max_side))
        nr_d = (nr + step - 1) // step
        nc_d = (nc + step - 1) // step
        grid = np.full((nr_d, nc_d), np.nan, dtype=np.float32)
        r2 = rows // step
        c2 = cols // step
        # last write wins; sufficient for visualisation
        grid[r2, c2] = values.astype(np.float32)
    else:
        grid = np.full((nr, nc), np.nan, dtype=np.float32)
        grid[rows, cols] = values.astype(np.float32)
    # imshow origin lower → flip row axis so north is up if y increases north
    grid = np.flipud(grid)
    extent = (xmin, xmax, ymin, ymax)
    return grid, extent


def is_regular_full(x: np.ndarray, y: np.ndarray) -> bool:
    ux, uy = np.unique(x), np.unique(y)
    return abs(len(ux) * len(uy) - x.size) <= 1


def loocv_predict(
    pack: dict[str, Any],
    event_idx: int,
    budget: int = BUDGET,
) -> dict[str, Any]:
    """Leave-one-event-out Global + Rule predictions for one held-out event."""
    hf, lf = pack["hf"], pack["lf"]
    n_ev = hf.shape[0]
    te = np.array([event_idx], dtype=int)
    tr = np.array([i for i in range(n_ev) if i != event_idx], dtype=int)
    xy = pack["xy"]
    terrain = pack["terrain"]

    t0 = time.perf_counter()
    pred_g, meta_g = fit_predict_max(
        hf[tr], lf[tr], hf[te], lf[te], terrain, xy, budget, method="global"
    )
    pred_r, meta_r = fit_predict_max(
        hf[tr], lf[tr], hf[te], lf[te], terrain, xy, budget,
        method="rule", return_labels=True,
    )
    elapsed = time.perf_counter() - t0

    hf_te = hf[te[0]]
    lf_te = lf[te[0]]
    g = pred_g[0]
    r = pred_r[0]
    areas = pack["areas"]
    met_g = area_weighted_metrics(g, hf_te, areas, WET)
    met_r = area_weighted_metrics(r, hf_te, areas, WET)
    met_lf = area_weighted_metrics(lf_te, hf_te, areas, WET)

    return {
        "hf": hf_te,
        "lf": lf_te,
        "global": g,
        "rule": r,
        "zone_labels": meta_r.get("zone_labels"),
        "active_mask": meta_r.get("active_mask"),
        "metrics": {"lf": met_lf, "global": met_g, "rule": met_r},
        "meta_g": meta_g,
        "meta_r": meta_r,
        "elapsed_s": elapsed,
        "train_idx": tr.tolist(),
        "test_idx": int(event_idx),
    }


def depth_vmax(*fields: np.ndarray, q: float = 99.0) -> float:
    wet_vals = []
    for f in fields:
        m = f >= WET
        if np.any(m):
            wet_vals.append(f[m])
    if not wet_vals:
        return 1.0
    return float(max(np.percentile(np.concatenate(wet_vals), q), WET * 2))


def plot_field(
    ax,
    values: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    *,
    cmap,
    vmin,
    vmax,
    title: str,
    regular: bool,
):
    if regular:
        grid, extent = to_raster(values, x, y)
        im = ax.imshow(
            grid,
            origin="upper",
            extent=extent,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            interpolation="nearest",
            aspect="equal",
        )
    else:
        # Unstructured / sparse: scatter (subsample if huge)
        n = values.size
        idx = np.arange(n)
        if n > 250_000:
            rng = np.random.default_rng(42)
            idx = rng.choice(n, size=250_000, replace=False)
        im = ax.scatter(
            x[idx], y[idx], c=values[idx], s=0.4, cmap=cmap,
            vmin=vmin, vmax=vmax, marker="s", linewidths=0,
        )
        ax.set_aspect("equal")
    ax.set_title(title, fontsize=9)
    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Northing (m)")
    ax.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))
    return im


def hit_miss_classes(pred: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """0=correct dry, 1=hit, 2=miss, 3=false alarm; -1 unused."""
    pw = pred >= WET
    rw = ref >= WET
    out = np.zeros(pred.shape, dtype=np.int8)
    out[rw & pw] = 1
    out[rw & ~pw] = 2
    out[~rw & pw] = 3
    return out


HM_COLORS = ["#f0f0f0", "#2ca02c", "#1f77b4", "#d62728"]  # dry, hit, miss, FA
HM_LABELS = ["Correct dry", "Hit", "Miss", "False alarm"]


def fig_inundation(pack: dict, pred: dict, event_idx: int, tag: str) -> str:
    name = f"figA1_inundation_maps_{tag}.png"
    x, y = pack["x"], pack["y"]
    regular = is_regular_full(x, y)
    hf, lf, g, r = pred["hf"], pred["lf"], pred["global"], pred["rule"]
    vmax = depth_vmax(hf, lf, g, r)
    cmap = plt.get_cmap("Blues")

    fig, axes = plt.subplots(2, 2, figsize=(W2, W2 * 0.92))
    titles = [
        f"(a) HF truth  [{pack['event_ids'][event_idx]}]",
        "(b) LF input (on HF mesh)",
        f"(c) Global LSG-Max (B={BUDGET})",
        f"(d) Rule zonal LSG-Max (B={BUDGET})",
    ]
    fields = [hf, lf, g, r]
    im = None
    for ax, field, title in zip(axes.ravel(), fields, titles):
        im = plot_field(ax, field, x, y, cmap=cmap, vmin=0.0, vmax=vmax, title=title, regular=regular)
    fig.subplots_adjust(right=0.88, hspace=0.32, wspace=0.28)
    cax = fig.add_axes([0.90, 0.18, 0.02, 0.64])
    cb = fig.colorbar(im, cax=cax)
    cb.set_label("Max. water depth (m)")
    eid = pack["event_ids"][event_idx]
    fig.suptitle(
        f"{pack['case'].title()} LOOCV held-out {eid} (event {event_idx}); "
        f"source={pack['source']}",
        fontsize=9,
        y=0.995,
    )
    save(fig, name)
    _log_ok(name, {
        "case": pack["case"],
        "event_idx": event_idx,
        "event_id": eid,
        "cache": pack["cache"],
        "rmse_global": pred["metrics"]["global"]["rmse_area"],
        "rmse_rule": pred["metrics"]["rule"]["rmse_area"],
    })
    return name


def fig_csi_spatial(pack: dict, pred: dict, event_idx: int, tag: str) -> str:
    name = f"figA2_csi_hitmiss_{tag}.png"
    x, y = pack["x"], pack["y"]
    regular = is_regular_full(x, y)
    cmap = ListedColormap(HM_COLORS)
    norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], cmap.N)

    fig, axes = plt.subplots(1, 2, figsize=(W2, W2 * 0.48))
    for ax, field, lab in (
        (axes[0], pred["global"], "Global"),
        (axes[1], pred["rule"], "Rule zonal"),
    ):
        cls = hit_miss_classes(field, pred["hf"]).astype(np.float64)
        met = pred["metrics"]["global" if lab.startswith("Global") else "rule"]
        title = f"{lab}  CSI={met['csi_area']:.3f}"
        if regular:
            grid, extent = to_raster(cls, x, y)
            ax.imshow(grid, origin="upper", extent=extent, cmap=cmap, norm=norm,
                      interpolation="nearest", aspect="equal")
        else:
            idx = np.arange(cls.size)
            if cls.size > 250_000:
                idx = np.random.default_rng(0).choice(cls.size, 250_000, replace=False)
            ax.scatter(x[idx], y[idx], c=cls[idx], s=0.4, cmap=cmap, norm=norm,
                       marker="s", linewidths=0)
            ax.set_aspect("equal")
        ax.set_title(title, fontsize=9)
        ax.set_xlabel("Easting (m)")
        ax.set_ylabel("Northing (m)")
        ax.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))
    handles = [Patch(facecolor=c, edgecolor="0.3", label=l) for c, l in zip(HM_COLORS, HM_LABELS)]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=7,
               bbox_to_anchor=(0.5, -0.02))
    eid = pack["event_ids"][event_idx]
    fig.suptitle(
        f"{pack['case'].title()} wet/dry hit–miss (thresh={WET} m); held-out {eid}",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0.06, 1, 0.95])
    save(fig, name)
    _log_ok(name, {
        "case": pack["case"],
        "event_idx": event_idx,
        "event_id": eid,
        "csi_global": pred["metrics"]["global"]["csi_area"],
        "csi_rule": pred["metrics"]["rule"]["csi_area"],
    })
    return name


def fig_residuals(pack: dict, pred: dict, event_idx: int, tag: str) -> str:
    name = f"figA3_residuals_{tag}.png"
    x, y = pack["x"], pack["y"]
    regular = is_regular_full(x, y)
    eg = pred["global"] - pred["hf"]
    er = pred["rule"] - pred["hf"]
    # show where |rule| < |global|
    improve = np.abs(eg) - np.abs(er)

    # Symmetric limit from wet-mask residuals
    wet = pred["hf"] >= WET
    lim = float(np.percentile(np.abs(np.concatenate([eg[wet], er[wet]])), 98)) if np.any(wet) else 1.0
    lim = max(lim, 0.05)
    cmap = plt.get_cmap("RdBu_r")

    fig, axes = plt.subplots(1, 3, figsize=(W2, W2 * 0.38))
    panels = [
        (eg, f"(a) Global − HF", -lim, lim, cmap),
        (er, f"(b) Rule − HF", -lim, lim, cmap),
        (improve, f"(c) |G−HF| − |R−HF|", -lim, lim, plt.get_cmap("PiYG")),
    ]
    ims = []
    for ax, (field, title, vmin, vmax, cm) in zip(axes, panels):
        im = plot_field(ax, field, x, y, cmap=cm, vmin=vmin, vmax=vmax, title=title, regular=regular)
        ims.append(im)
    for im, ax, label in zip(ims, axes, ["Residual (m)", "Residual (m)", "Improvement (m)"]):
        cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cb.set_label(label, fontsize=7)
    eid = pack["event_ids"][event_idx]
    fig.suptitle(
        f"{pack['case'].title()} residuals; LOOCV held-out {eid} (B={BUDGET})",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, name)
    _log_ok(name, {
        "case": pack["case"],
        "event_idx": event_idx,
        "event_id": eid,
        "residual_lim_m": lim,
    })
    return name


def fig_zones_overlay(pack: dict, pred: dict, event_idx: int, tag: str) -> str:
    name = f"figA4_zones_overlay_{tag}.png"
    labels = pred.get("zone_labels")
    if labels is None:
        _log_skip(name, "zone_labels missing from Rule fit")
        return name
    x, y = pack["x"], pack["y"]
    regular = is_regular_full(x, y)
    active = pred.get("active_mask")
    lab = np.asarray(labels, dtype=np.float64)
    if active is not None:
        lab = lab.copy()
        lab[~np.asarray(active, dtype=bool)] = np.nan

    fig, axes = plt.subplots(1, 2, figsize=(W2, W2 * 0.48))
    # (a) zones
    n_z = int(np.nanmax(lab)) + 1 if np.any(np.isfinite(lab)) else 4
    cmap_z = ListedColormap(plt.cm.Set2(np.linspace(0, 1, max(n_z, 4)))[:max(n_z, 4)])
    if regular:
        grid, extent = to_raster(np.nan_to_num(lab, nan=-1), x, y)
        grid = np.where(grid < 0, np.nan, grid)
        im0 = axes[0].imshow(grid, origin="upper", extent=extent, cmap=cmap_z,
                             interpolation="nearest", aspect="equal", vmin=-0.5, vmax=n_z - 0.5)
    else:
        m = np.isfinite(lab)
        im0 = axes[0].scatter(x[m], y[m], c=lab[m], s=0.4, cmap=cmap_z, marker="s", linewidths=0)
        axes[0].set_aspect("equal")
    axes[0].set_title("(a) Rule zones (train-fit)", fontsize=9)
    axes[0].set_xlabel("Easting (m)")
    axes[0].set_ylabel("Northing (m)")
    cb0 = fig.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04)
    cb0.set_label("Zone id")

    # (b) HF depth with zone edges via contour of labels (if regular)
    vmax = depth_vmax(pred["hf"])
    im1 = plot_field(
        axes[1], pred["hf"], x, y, cmap=plt.get_cmap("Blues"),
        vmin=0.0, vmax=vmax, title="(b) HF depth + zone field", regular=regular,
    )
    if regular and np.any(np.isfinite(lab)):
        grid_l, extent = to_raster(np.nan_to_num(lab, nan=-1), x, y)
        # light contours between integer zones
        try:
            yy = np.linspace(extent[3], extent[2], grid_l.shape[0])  # flipped
            xx = np.linspace(extent[0], extent[1], grid_l.shape[1])
            XX, YY = np.meshgrid(xx, yy)
            axes[1].contour(XX, YY, grid_l, levels=np.arange(-0.5, n_z, 1.0),
                            colors="k", linewidths=0.3, alpha=0.55)
        except Exception:
            pass
    fig.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04).set_label("Depth (m)")
    eid = pack["event_ids"][event_idx]
    fig.suptitle(
        f"{pack['case'].title()} hydrodynamic zones; held-out {eid}",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, name)
    _log_ok(name, {"case": pack["case"], "event_idx": event_idx, "event_id": eid, "n_zones": n_z})
    return name


def fig_obs_pred_scatter(pack: dict, pred: dict, event_idx: int, tag: str) -> str:
    name = f"figA5_obs_vs_pred_{tag}.png"
    hf = pred["hf"]
    wet = hf >= WET
    if not np.any(wet):
        _log_skip(name, "no wet HF cells")
        return name
    idx = np.where(wet)[0]
    rng = np.random.default_rng(42)
    if idx.size > 40_000:
        idx = rng.choice(idx, size=40_000, replace=False)

    fig, axes = plt.subplots(1, 2, figsize=(W2, W2 * 0.45))
    for ax, field, title in (
        (axes[0], pred["global"], "Global LSG-Max"),
        (axes[1], pred["rule"], "Rule zonal LSG-Max"),
    ):
        ax.scatter(hf[idx], field[idx], s=2, alpha=0.25, linewidths=0, rasterized=True)
        lim = float(max(hf[idx].max(), field[idx].max(), WET))
        ax.plot([0, lim], [0, lim], "k--", lw=0.8, label="1:1")
        ax.set_xlim(0, lim)
        ax.set_ylim(0, lim)
        ax.set_aspect("equal")
        ax.set_xlabel("HF observed depth (m)")
        ax.set_ylabel("Predicted depth (m)")
        met = pred["metrics"]["global" if "Global" in title else "rule"]
        ax.set_title(f"{title}\nRMSE={met['rmse_area']:.3f} m", fontsize=8)
        ax.legend(frameon=False, fontsize=7, loc="upper left")
    eid = pack["event_ids"][event_idx]
    fig.suptitle(
        f"{pack['case'].title()} wet-cell obs vs pred; LOOCV held-out {eid} (B={BUDGET})",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    save(fig, name)
    _log_ok(name, {
        "case": pack["case"],
        "event_idx": event_idx,
        "event_id": eid,
        "n_scatter_points": int(idx.size),
    })
    return name


def run_case(case: str, event_idx: int) -> None:
    pack = load_pack(case)
    if pack is None:
        return
    n_ev = pack["hf"].shape[0]
    if event_idx < 0 or event_idx >= n_ev:
        _log_skip(f"{case}:event", f"event_idx={event_idx} out of range n_ev={n_ev}")
        return
    eid = pack["event_ids"][event_idx]
    tag = f"{case}_ev{event_idx}"
    print(f"\n=== {case} LOOCV held-out event {event_idx} ({eid}) ===", flush=True)
    pred = loocv_predict(pack, event_idx, BUDGET)
    print(
        f"  fit+predict {pred['elapsed_s']:.1f}s | "
        f"RMSE LF/G/R = "
        f"{pred['metrics']['lf']['rmse_area']:.4f}/"
        f"{pred['metrics']['global']['rmse_area']:.4f}/"
        f"{pred['metrics']['rule']['rmse_area']:.4f}",
        flush=True,
    )
    # Cache prediction arrays for audit (real numbers only)
    pred_dir = ROOT / "outputs" / "predictions"
    pred_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        pred_dir / f"loocv_{tag}_B{BUDGET}.npz",
        hf=pred["hf"],
        lf=pred["lf"],
        global_pred=pred["global"],
        rule_pred=pred["rule"],
        zone_labels=pred["zone_labels"] if pred["zone_labels"] is not None else np.array([]),
        event_idx=np.array([event_idx]),
        event_id=np.array([eid]),
    )

    fig_inundation(pack, pred, event_idx, tag)
    fig_csi_spatial(pack, pred, event_idx, tag)
    fig_residuals(pack, pred, event_idx, tag)
    fig_zones_overlay(pack, pred, event_idx, tag)
    fig_obs_pred_scatter(pack, pred, event_idx, tag)


def main():
    apply_style()
    FIG.mkdir(parents=True, exist_ok=True)
    MANIFEST["notes"].append(
        "Carlisle event 1 is the LOOCV fold with largest Global RMSE spike "
        "(see loocv_results.json B=4); used as the primary qualitative map event."
    )
    # Primary positive case + one milder fold for context
    run_case("carlisle", 1)
    run_case("carlisle", 0)
    # Boundary / non-benefit cases (first event) if packs load
    run_case("burnettrv", 0)
    run_case("chowilla", 0)

    out = FIG / "spatial_maps_manifest.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(MANIFEST, f, indent=2, ensure_ascii=False)
    print(f"\nManifest → {out}")
    print(f"Generated {len(MANIFEST['generated'])}, skipped {len(MANIFEST['skipped'])}")


if __name__ == "__main__":
    main()
