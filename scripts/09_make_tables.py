#!/usr/bin/env python
"""Generate paper tables from Track B artefacts (registry + evaluation JSON + geometry).

Do not hardcode toy RMSE. Synthetic 30x40 processed trees are not cited here.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.fraehr import EXPECTED_HF_CELLS, EXPECTED_LF_CELLS, load_case_geometry, raw_dir_exists


def _read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _write_csv(path: Path, headers: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Saved {path}")


def _cell_counts(root: Path, case: str) -> tuple[int, int | None]:
    if raw_dir_exists(root, case):
        try:
            geo = load_case_geometry(root, case)
            return geo["n_hf"], geo.get("n_lf")
        except Exception as e:
            print(f"  [warn] geometry load failed for {case}: {e}")
    return EXPECTED_HF_CELLS[case], EXPECTED_LF_CELLS[case]


def _manifest_row(rows: list[dict], case: str, model: str, b: str | None = None) -> dict | None:
    matches = [
        r for r in rows
        if r["case"] == case and r["model"] == model
        and (b is None or str(r["B_requested"]) == str(b))
    ]
    return matches[0] if matches else None


def table01_case_summary(output_dir: Path, root: Path, manifest: list[dict]) -> None:
    """Table 1: Dataset information from real geometry + registry event counts."""
    c_hf, c_lf = _cell_counts(root, "carlisle")
    h_hf, h_lf = _cell_counts(root, "chowilla")
    b_hf, b_lf = _cell_counts(root, "burnettrv")

    def n_events(case: str) -> tuple[str, str]:
        row = next((r for r in manifest if r["case"] == case and r["model"] != "LF-only"), None)
        if not row:
            return "?", "?"
        return str(row["events_used"]), str(row["events_available"])

    c_u, c_a = n_events("Carlisle")
    h_u, h_a = n_events("Chowilla")
    b_u, b_a = n_events("BurnettRV")

    rows = [
        ["Carlisle", "UK", "LISFLOOD-FP", c_u, c_a, c_hf, c_lf or "", "Moderate",
         "Full 9-fold LOOCV (Track B)"],
        ["Chowilla", "Australia", "MIKE 21", h_u, h_a, h_hf, h_lf or "", "High",
         "Boundary case: LSG degrades vs LF-only"],
        ["BurnettRV", "Australia", "TUFLOW", b_u, b_a, b_hf, b_lf or "", "Moderate",
         "Global ~ zonal; both improve over LF"],
    ]
    headers = ["Case", "Country", "Hydro model", "n_events_used", "n_events_available",
               "n_hf_cells", "n_lf_cells", "Complexity", "Paper role"]
    _write_csv(output_dir / "tables" / "table01_case_summary.csv", headers, rows)


def table02_experiment_matrix(output_dir: Path) -> None:
    rows = [
        ["E0", "LF-only", "N/A", "N/A", "LF baseline"],
        ["E1", "Global LSG-Max", "Global (1)", "B=4/6/8 forced", "Equal-budget baseline"],
        ["E2", "Rule zLSG-Max", "Rule (depth+freq)", "B=4/6/8", "Physical zones"],
        ["E3", "KMeans zLSG-Max", "KMeans (K=4)", "B=4/6/8", "Data-driven zones"],
        ["E4", "Carlisle 9-fold LOOCV", "Rule vs Global", "B=4 and B=6", "Event-level significance"],
        ["E5", "Official 2-fold bootstrap", "Rule vs Global", "official splits",
         "Not significant (cite honestly)"],
        ["E6", "Chowilla boundary", "Global/Rule/KMeans", "B=4/8/12", "LSG degrades"],
        ["E7", "BurnettRV validation", "Global/Rule/KMeans", "B=4/8", "Diffuse residuals"],
    ]
    headers = ["ID", "Model", "Zoning", "EOF budget", "Purpose"]
    _write_csv(output_dir / "tables" / "table02_experiment_matrix.csv", headers, rows)


def table03_main_results(output_dir: Path, manifest: list[dict]) -> None:
    """Table 3: Main results from result_manifest_v4.csv (no toy RMSE)."""
    headers = ["Case", "Model", "B", "RMSE_area (m)", "CSI_area", "Status", "Notes"]
    rows = []
    for case in ["Carlisle", "Chowilla", "BurnettRV"]:
        case_rows = [r for r in manifest if r["case"] == case]
        for r in case_rows:
            rows.append([
                r["case"], r["model"], r["B_requested"],
                r["rmse_area"], r["csi_area"], r["status"],
                r.get("notes", "")[:80],
            ])
        rows.append(["", "", "", "", "", "", ""])
    if rows and not rows[-1][0]:
        rows.pop()
    _write_csv(output_dir / "tables" / "table03_main_results.csv", headers, rows)


def table04_carlisle_budget(output_dir: Path, eval_dir: Path, manifest: list[dict]) -> None:
    """Table 4: Carlisle true equal-budget + LOOCV / official 2-fold honesty."""
    sweep_path = eval_dir / "carlisle" / "budget_sweep_true_equal.json"
    boot_path = eval_dir / "carlisle" / "multifold_bootstrap.json"
    loocv_path = eval_dir / "carlisle" / "loocv_results.json"

    headers = ["Source", "Setting", "Global RMSE", "Rule RMSE", "KMeans RMSE",
               "Delta Rule vs Global", "Significant"]
    rows = []
    if sweep_path.exists():
        cb = json.loads(sweep_path.read_text(encoding="utf-8"))
        for B in ["4", "6", "8"]:
            g = cb["budgets"][B]["global"]["rmse_area"]
            r = cb["budgets"][B]["rule"]["rmse_area"]
            k = cb["budgets"][B]["kmeans"]["rmse_area"]
            d = (g - r) / g * 100
            rows.append([
                "true_equal_budget", f"B={B}",
                f"{g:.4f}", f"{r:.4f}", f"{k:.4f}",
                f"{d:+.1f}%", "n/a (single split)",
            ])
    if loocv_path.exists():
        loocv = json.loads(loocv_path.read_text(encoding="utf-8"))
        for B in [4, 6]:
            items = [e for e in loocv["per_event"] if e["B"] == B]
            improved = sum(1 for e in items if e["delta_rmse"] > 0)
            rows.append([
                "loocv_9fold", f"B={B}",
                "", "", "",
                f"{improved}/{len(items)} folds improved",
                "see report (B=4 CI excludes 0)",
            ])
    if boot_path.exists():
        mb = json.loads(boot_path.read_text(encoding="utf-8"))
        sig = mb.get("significant", False)
        rows.append([
            "official_2fold",
            f"n_folds={mb.get('n_folds')}",
            "", "", "",
            f"mean_delta={mb.get('mean_delta_rmse'):.4f}; "
            f"CI=[{mb.get('ci_95_lower'):.4f},{mb.get('ci_95_upper'):.4f}]",
            "NO" if not sig else "YES",
        ])

    bloo_path = eval_dir / "burnettrv" / "loocv_results.json"
    if bloo_path.exists():
        bloo = json.loads(bloo_path.read_text(encoding="utf-8"))
        sm = bloo.get("summary", {}).get("rule")
        if sm:
            rows.append([
                "burnett_loocv",
                f"n={sm.get('n_folds')} B={bloo.get('config', {}).get('B', 4)}",
                f"{sm['mean_global_rmse']:.4f}",
                f"{sm['mean_zonal_rmse']:.4f}",
                "",
                f"mean_dRMSE={sm['mean_delta_rmse']:+.4f}; "
                f"{sm['n_improved']}/{sm['n_folds']} improved",
                "YES" if sm.get("significant") else "NO",
            ])

    ch = _manifest_row(manifest, "Chowilla", "global", "4")
    if ch:
        lf = _manifest_row(manifest, "Chowilla", "LF-only")
        rows.append([
            "chowilla_boundary", "B=4",
            ch["rmse_area"],
            _manifest_row(manifest, "Chowilla", "rule", "4")["rmse_area"],
            _manifest_row(manifest, "Chowilla", "kmeans", "4")["rmse_area"],
            f"LSG degrades vs LF-only {lf['rmse_area'] if lf else '?'}",
            "n/a (boundary case)",
        ])

    _write_csv(output_dir / "tables" / "table04_ablation.csv", headers, rows)


def main():
    parser = argparse.ArgumentParser(description="Generate paper tables from Track B artefacts")
    parser.add_argument("--case", default="all",
                        choices=["carlisle", "chowilla", "burnettrv", "all"])
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    output_dir = Path(args.output_dir) if args.output_dir else (root / "outputs")
    eval_dir = output_dir / "evaluation"
    manifest_path = output_dir / "registry" / "result_manifest_v4.csv"
    if not manifest_path.exists():
        raise SystemExit(f"Missing {manifest_path}; run scripts/45_build_registry.py --skip-eoi")
    manifest = _read_csv(manifest_path)

    table01_case_summary(output_dir, root, manifest)
    table02_experiment_matrix(output_dir)
    table03_main_results(output_dir, manifest)
    table04_carlisle_budget(output_dir, eval_dir, manifest)
    print(f"\nAll tables generated in {output_dir / 'tables'}")


if __name__ == "__main__":
    main()
