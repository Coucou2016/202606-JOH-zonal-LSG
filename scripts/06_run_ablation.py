#!/usr/bin/env python
"""Run ablation experiments: vary K, remove features, compare zoning methods."""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.zonal_lsg import ZonalLSG
from lsg.zoning import ZoningConfig
from lsg.metrics import extent_metrics
from scripts._loader import load_case_data, make_split


def run_single_ablation(
    case_name: str,
    variant: str,
    zoning_method: str,
    n_zones: int,
    mode_budget: str,
    processed_dir: Path,
    output_dir: Path,
) -> dict:
    data = load_case_data(processed_dir)
    train_idx, val_idx = make_split(data["event_ids"], processed_dir)

    model = ZonalLSG(
        zoning_config=ZoningConfig(method=zoning_method, n_zones=n_zones),
        variant=variant,
        mode_budget=None if mode_budget == "free" else "global_equal",
        wet_threshold=0.03,
    )
    model.fit(
        data["hf_ts"][train_idx], data["lf_ts"][train_idx],
        data["terrain_hf"], data["shape_hf"], data["shape_lf"],
        x_hf=data.get("x_hf"), y_hf=data.get("y_hf"),
    )

    pred = model.predict(
        data["lf_ts"][val_idx], data["terrain_hf"],
        data["shape_hf"], data["shape_lf"],
    )
    hf_flat = data["hf_ts"][val_idx].reshape(-1, data["shape_hf"][0] * data["shape_hf"][1])
    pred_flat = pred.reshape(-1, data["shape_hf"][0] * data["shape_hf"][1])

    metrics = extent_metrics(pred_flat, hf_flat, 0.03)
    metrics["n_zones"] = n_zones
    metrics["n_modes"] = sum(model.state.eof_state.zones[0].n_modes
                             if hasattr(model.state.eof_state, 'zones')
                             else 0 for _ in [0])
    if model.state:
        zone_stats = model.get_zone_statistics()
        metrics["total_eof_modes"] = sum(v["n_modes"] for v in zone_stats.values())
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Run ablation experiments")
    parser.add_argument("--case", required=True,
                        choices=["carlisle", "chowilla", "burnettrv", "all"])
    parser.add_argument("--variant", default="ts", choices=["ts", "max"])
    parser.add_argument("--n-zones", nargs="+", type=int, default=[2, 4, 6, 8, 12])
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    cases = ["carlisle", "chowilla", "burnettrv"] if args.case == "all" else [args.case]
    root = Path(__file__).resolve().parents[1]
    output_dir = args.output_dir or (root / "outputs")

    all_results = {}
    for case in cases:
        processed_dir = root / "data" / "processed" / case
        case_results = []

        for k in args.n_zones:
            for method in ["kmeans", "rule"]:
                for budget in ["free", "global_equal"]:
                    print(f"Ablation: {case} | {method} | K={k} | budget={budget}")
                    try:
                        met = run_single_ablation(
                            case, args.variant, method, k, budget,
                            processed_dir, output_dir,
                        )
                        met["method"] = method
                        met["budget"] = budget
                        case_results.append(met)
                    except Exception as e:
                        print(f"  FAILED: {e}")

        all_results[case] = case_results

    out_path = output_dir / "evaluation" / f"ablation_{args.case}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nAblation results saved to {out_path}")


if __name__ == "__main__":
    main()
