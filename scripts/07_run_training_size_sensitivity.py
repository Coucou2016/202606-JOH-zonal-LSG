#!/usr/bin/env python
"""Training size sensitivity: how does zonal vs global LSG perform with fewer samples?"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.baseline_lsg import GlobalLSG
from lsg.zonal_lsg import ZonalLSG
from lsg.zoning import ZoningConfig
from lsg.metrics import extent_metrics
from scripts._loader import load_case_data


def run_training_size(
    case_name: str,
    fractions: list[float],
    n_repeats: int,
    seeds: list[int],
    processed_dir: Path,
    output_dir: Path,
) -> dict:
    data = load_case_data(processed_dir)
    hf_ts, lf_ts = data["hf_ts"], data["lf_ts"]
    terrain = data["terrain_hf"]
    shape_hf, shape_lf = data["shape_hf"], data["shape_lf"]
    n_events = len(data["event_ids"])

    results = {"global": {}, "zonal": {}}

    for frac in fractions:
        global_metrics = []
        zonal_metrics = []

        for rep in range(min(n_repeats, len(seeds))):
            rng = np.random.default_rng(seeds[rep])
            idx = rng.permutation(n_events)
            n_train = max(2, int(n_events * frac))
            train_idx = idx[:n_train]
            val_idx = idx[n_train:]

            if len(val_idx) == 0:
                val_idx = train_idx[-1:]

            # Global LSG
            g_model = GlobalLSG(variant="ts", wet_threshold=0.03)
            g_model.fit(
                hf_ts[train_idx], lf_ts[train_idx],
                terrain, shape_hf, shape_lf,
            )
            g_pred = g_model.predict(
                lf_ts[val_idx], terrain, shape_hf, shape_lf,
            )
            g_flat = g_pred.reshape(-1, shape_hf[0] * shape_hf[1])
            h_flat = hf_ts[val_idx].reshape(-1, shape_hf[0] * shape_hf[1])
            global_metrics.append(extent_metrics(g_flat, h_flat, 0.03))

            # Zonal LSG (K=4, global_equal budget)
            z_model = ZonalLSG(
                zoning_config=ZoningConfig(method="kmeans", n_zones=4),
                variant="ts",
                mode_budget="global_equal",
                wet_threshold=0.03,
            )
            z_model.fit(
                hf_ts[train_idx], lf_ts[train_idx],
                terrain, shape_hf, shape_lf,
            )
            z_pred = z_model.predict(
                lf_ts[val_idx], terrain, shape_hf, shape_lf,
            )
            z_flat = z_pred.reshape(-1, shape_hf[0] * shape_hf[1])
            zonal_metrics.append(extent_metrics(z_flat, h_flat, 0.03))

        # Aggregate over repeats
        for key in ["rmse", "csi", "pod", "far"]:
            g_vals = [m[key] for m in global_metrics]
            z_vals = [m[key] for m in zonal_metrics]
            results["global"].setdefault(key, {})[str(frac)] = {
                "mean": float(np.mean(g_vals)),
                "std": float(np.std(g_vals)),
            }
            results["zonal"].setdefault(key, {})[str(frac)] = {
                "mean": float(np.mean(z_vals)),
                "std": float(np.std(z_vals)),
            }

        print(f"  frac={frac:.1f}: Global RMSE={np.mean([m['rmse'] for m in global_metrics]):.4f}, "
              f"Zonal RMSE={np.mean([m['rmse'] for m in zonal_metrics]):.4f}")

    out_path = output_dir / "evaluation" / f"training_size_{case_name}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved to {out_path}")
    return results


def main():
    parser = argparse.ArgumentParser(description="Training size sensitivity")
    parser.add_argument("--case", required=True,
                        choices=["carlisle", "chowilla", "burnettrv", "all"])
    parser.add_argument("--variant", default="ts")
    parser.add_argument("--fractions", nargs="+", type=float,
                        default=[0.2, 0.4, 0.6, 0.8, 1.0])
    parser.add_argument("--n-repeats", type=int, default=3)
    parser.add_argument("--seeds", nargs="+", type=int,
                        default=[42, 123, 456])
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    cases = ["carlisle", "chowilla", "burnettrv"] if args.case == "all" else [args.case]

    for case in cases:
        processed_dir = root / "data" / "processed" / case
        run_training_size(
            case, args.fractions, args.n_repeats, args.seeds,
            processed_dir, root / "outputs",
        )


if __name__ == "__main__":
    main()
