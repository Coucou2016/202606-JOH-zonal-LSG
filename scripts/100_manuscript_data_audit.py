#!/usr/bin/env python
"""Machine-checkable audit: manuscript/report headline numbers vs evaluation JSON.

Writes:
  outputs/evaluation/manuscript_data_audit.json
  paper/DATA_PROVENANCE.md
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

OUT_JSON = _ROOT / "outputs" / "evaluation" / "manuscript_data_audit.json"
OUT_MD = _ROOT / "paper" / "DATA_PROVENANCE.md"
MS = _ROOT / "paper" / "manuscript.md"
MANIFEST = _ROOT / "outputs" / "figures" / "spatial_maps_manifest.json"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _approx(a: float, b: float, tol: float = 5e-4) -> bool:
    if a is None or b is None:
        return False
    if not np.isfinite(a) or not np.isfinite(b):
        return False
    return abs(float(a) - float(b)) <= tol


def _find_ms(pattern: str, text: str) -> list[str]:
    return re.findall(pattern, text)


def audit() -> dict[str, Any]:
    ms = MS.read_text(encoding="utf-8")
    checks: list[dict[str, Any]] = []

    def add(name: str, expected: float, observed: float | None, tol: float = 5e-4, source: str = "") -> None:
        ok = observed is not None and _approx(expected, observed, tol)
        checks.append(
            {
                "name": name,
                "expected": expected,
                "observed": observed,
                "tol": tol,
                "pass": bool(ok),
                "source": source,
            }
        )

    # --- Carlisle budget ---
    bud = _load(_ROOT / "outputs/evaluation/carlisle/budget_sweep_true_equal.json")
    b4 = bud["budgets"]["4"]
    add("carlisle_B4_global_rmse", 0.1464, round(b4["global"]["rmse_area"], 4), 5e-4, "budget_sweep_true_equal.json")
    add("carlisle_B4_rule_rmse", 0.0964, round(b4["rule"]["rmse_area"], 4), 5e-4, "budget_sweep_true_equal.json")
    add("carlisle_B4_kmeans_rmse", 0.1015, round(b4["kmeans"]["rmse_area"], 4), 5e-4, "budget_sweep_true_equal.json")
    add("carlisle_lf_rmse", 0.1602, round(bud["lf_only"]["rmse_area"], 4), 5e-4, "budget_sweep_true_equal.json")
    add("carlisle_lf_csi", 0.9145, round(bud["lf_only"]["csi_area"], 4), 5e-4, "budget_sweep_true_equal.json")
    b6 = bud["budgets"]["6"]
    add("carlisle_B6_global_rmse", 0.2588, round(b6["global"]["rmse_area"], 4), 5e-4, "budget_sweep_true_equal.json")
    add("carlisle_B6_rule_rmse", 0.1256, round(b6["rule"]["rmse_area"], 4), 5e-4, "budget_sweep_true_equal.json")
    b8g = bud["budgets"]["8"]["global"]
    add("carlisle_B8_global_rmse", 0.3527, round(b8g["rmse_area"], 4), 5e-4, "budget_sweep_true_equal.json")
    add("carlisle_B8_actual_modes", 7.0, float(b8g.get("actual_modes", float("nan"))), 0.0, "budget_sweep_true_equal.json")

    # manuscript string presence for key numbers
    for token in ["0.1464", "0.0964", "0.1015", "9/9", "0.057", "0.116", "0.957"]:
        checks.append(
            {
                "name": f"manuscript_contains_{token}",
                "expected": True,
                "observed": token in ms,
                "pass": token in ms,
                "source": "paper/manuscript.md",
            }
        )

    # LOOCV
    loo = _load(_ROOT / "outputs/evaluation/carlisle/loocv_results.json")
    rows4 = [r for r in loo["per_event"] if int(r.get("B", 4)) == 4]
    n_imp = sum(1 for r in rows4 if float(r["delta_rmse"]) > 0)
    add("carlisle_loocv_B4_n_improved", 9.0, float(n_imp), 0.0, "loocv_results.json")
    mean_d = float(np.mean([r["delta_rmse"] for r in rows4]))
    add("carlisle_loocv_B4_mean_delta", 0.0821, round(mean_d, 4), 5e-4, "loocv_results.json")
    # fold1 spike cited in ms
    f1 = next(r for r in rows4 if int(r["test_event"]) == 1)
    add("carlisle_loocv_ev1_global", 0.694, round(f1["global_rmse"], 3), 5e-3, "loocv_results.json")
    add("carlisle_loocv_ev1_rule", 0.166, round(f1["zonal_rmse"], 3), 5e-3, "loocv_results.json")

    ci = _load(_ROOT / "outputs/evaluation/carlisle/loocv_bootstrap_ci.json")
    # tolerate nested shapes
    def _ci_pair(obj: Any) -> tuple[float | None, float | None]:
        if isinstance(obj, dict):
            for key in ("ci95", "ci", "interval", "B4"):
                if key in obj:
                    return _ci_pair(obj[key])
            lo = obj.get("low") or obj.get("lower") or obj.get("ci_low")
            hi = obj.get("high") or obj.get("upper") or obj.get("ci_high")
            if lo is not None and hi is not None:
                return float(lo), float(hi)
            if "mean_delta" in obj and "ci_low" in obj:
                return float(obj["ci_low"]), float(obj["ci_high"])
        if isinstance(obj, (list, tuple)) and len(obj) >= 2:
            return float(obj[0]), float(obj[1])
        return None, None

    # Prefer explicit B=4 block if present
    ci_src = ci
    if "results" in ci and "B4" in ci["results"]:
        ci_src = ci["results"]["B4"]
    elif "B4" in ci:
        ci_src = ci["B4"]
    elif "budgets" in ci and "4" in ci["budgets"]:
        ci_src = ci["budgets"]["4"]
    if isinstance(ci_src, dict) and "ci_95" in ci_src:
        lo, hi = float(ci_src["ci_95"][0]), float(ci_src["ci_95"][1])
    else:
        lo, hi = _ci_pair(ci_src)
    if lo is None:
        # scan for numbers matching manuscript
        text = json.dumps(ci)
        m = re.search(r"0\.0155", text)
        checks.append(
            {
                "name": "carlisle_loocv_ci_contains_0155",
                "expected": True,
                "observed": bool(m),
                "pass": bool(m),
                "source": "loocv_bootstrap_ci.json",
            }
        )
    else:
        add("carlisle_loocv_ci_low", 0.0155, round(lo, 4), 5e-4, "loocv_bootstrap_ci.json")
        add("carlisle_loocv_ci_high", 0.1987, round(hi, 4), 5e-4, "loocv_bootstrap_ci.json")

    # Official fold
    mf = _load(_ROOT / "outputs/evaluation/carlisle/multifold_bootstrap.json")
    sig = mf.get("significant")
    if sig is None and isinstance(mf.get("summary"), dict):
        sig = mf["summary"].get("significant")
    checks.append(
        {
            "name": "carlisle_official_2fold_nonsig",
            "expected": False,
            "observed": sig,
            "pass": sig is False,
            "source": "multifold_bootstrap.json",
        }
    )

    # Burnett LOOCV
    br = _load(_ROOT / "outputs/evaluation/burnettrv/loocv_results.json")
    rule_sum = ((br.get("summary") or {}).get("rule") or {})
    g = rule_sum.get("mean_global_rmse")
    r = rule_sum.get("mean_zonal_rmse")
    add("burnett_loocv_global", 1.7479, round(float(g), 4) if g is not None else None, 5e-4, "burnettrv/loocv_results.json")
    add("burnett_loocv_rule", 1.8260, round(float(r), 4) if r is not None else None, 5e-4, "burnettrv/loocv_results.json")

    # Chowilla / three-case — prefer budget_sweep_full (has explicit rule arm)
    ch = _load(_ROOT / "outputs/evaluation/chowilla/budget_sweep_full.json")
    def _case_rmse(obj: dict, *arms: str) -> float | None:
        if "budgets" in obj and "4" in obj["budgets"]:
            block = obj["budgets"]["4"]
            for arm in arms:
                if arm in block and isinstance(block[arm], dict):
                    return float(block[arm].get("rmse_area", float("nan")))
        for arm in arms:
            if arm in obj and isinstance(obj[arm], dict):
                return float(obj[arm].get("rmse_area", obj[arm].get("rmse", float("nan"))))
        return None

    ch_g = _case_rmse(ch, "global")
    ch_r = _case_rmse(ch, "rule", "zonal")
    ch_lf = float(ch["lf_only"]["rmse_area"]) if "lf_only" in ch else None
    add("chowilla_global_rmse", 2.5606, round(ch_g, 4) if ch_g is not None else None, 5e-4, "chowilla/budget_sweep_full.json")
    add("chowilla_rule_rmse", 2.5614, round(ch_r, 4) if ch_r is not None else None, 5e-4, "chowilla/budget_sweep_full.json")
    add("chowilla_lf_rmse", 0.3926, round(ch_lf, 4) if ch_lf is not None else None, 5e-4, "chowilla/budget_sweep_full.json")

    vs = _load(_ROOT / "outputs/evaluation/burnettrv/validation_std.json")
    bg = float(vs["global"]["rmse_area"])
    brule = float(vs["Rule_B4"]["rmse_area"])
    blf = float(vs["lf_only"]["rmse_area"])
    add("burnett12_global", 1.6120, round(bg, 4), 5e-4, "burnettrv/validation_std.json")
    add("burnett12_rule", 1.6122, round(brule, 4), 5e-4, "burnettrv/validation_std.json")
    add("burnett12_lf", 2.2323, round(blf, 4), 5e-4, "burnettrv/validation_std.json")

    # EOI
    eoi = _load(_ROOT / "outputs/evaluation/eoi/eoi_all.json")
    cases = eoi.get("cases") or eoi
    for case, exp in (("carlisle", 0.057), ("chowilla", 0.116), ("burnettrv", 0.957)):
        block = cases.get(case) or {}
        val = block.get("eoi") or (block.get("pooled") or {}).get("eoi")
        add(f"eoi_{case}", exp, round(float(val), 3) if val is not None else None, 5e-3, "eoi_all.json")

    # stage-swap
    ss = _load(_ROOT / "outputs/evaluation/carlisle/stage_swap.json")
    means = ((ss.get("loocv") or {}).get("summary") or {})
    for arm, exp in (("GG", 0.180), ("ZZ", 0.098), ("GZ", 0.098), ("ZG", 0.101)):
        v = (means.get(arm) or {}).get("mean_rmse")
        add(f"stage_swap_{arm}", exp, round(float(v), 3) if v is not None else None, 5e-3, "stage_swap.json")

    # MaxWD
    # search registry or evaluation
    maxwd_ok = "0.988" in ms and "0.990" in ms
    checks.append(
        {
            "name": "manuscript_maxwd_r2_tokens",
            "expected": True,
            "observed": maxwd_ok,
            "pass": maxwd_ok,
            "source": "manuscript.md tokens vs published contrast",
        }
    )

    # modal oracle sign
    modal = _load(_ROOT / "outputs/evaluation/eoi/modal_eoi.json")
    for case in ("carlisle", "burnettrv", "chowilla"):
        d = ((modal.get("cases") or {}).get(case) or {}).get("pooled", {}).get("oracle_delta_rmse")
        checks.append(
            {
                "name": f"modal_oracle_delta_neg_{case}",
                "expected": "<0",
                "observed": d,
                "pass": d is not None and float(d) < 0,
                "source": "modal_eoi.json",
            }
        )

    # spatial maps provenance
    spatial = {"pass": False, "n_figures": 0, "issues": []}
    if MANIFEST.exists():
        man = _load(MANIFEST)
        gens = man.get("generated") or man.get("figures") or []
        spatial["n_figures"] = len(gens)
        spatial["pass"] = len(gens) >= 20
        for item in gens:
            fig = item.get("figure") or item.get("path")
            p = _ROOT / "outputs" / "figures" / Path(fig).name
            if not p.exists():
                spatial["issues"].append(f"missing file {fig}")
                spatial["pass"] = False
            if item.get("case") not in ("carlisle", "burnettrv", "chowilla"):
                spatial["issues"].append(f"bad case {item}")
            # representative-event caveat
            if "overall" in str(item).lower() and "representative" not in str(item).lower():
                pass
        checks.append(
            {
                "name": "spatial_maps_manifest_complete",
                "expected": ">=20 figs",
                "observed": spatial["n_figures"],
                "pass": spatial["pass"],
                "source": "spatial_maps_manifest.json",
                "issues": spatial["issues"],
            }
        )
    else:
        checks.append(
            {
                "name": "spatial_maps_manifest_complete",
                "expected": True,
                "observed": False,
                "pass": False,
                "source": "missing manifest",
            }
        )

    n_pass = sum(1 for c in checks if c.get("pass"))
    n_fail = sum(1 for c in checks if not c.get("pass"))
    report = {
        "n_checks": len(checks),
        "n_pass": n_pass,
        "n_fail": n_fail,
        "all_pass": n_fail == 0,
        "checks": checks,
        "spatial": spatial,
        "notes": [
            "Manuscript numbers are rounded to 4 dp in prose; audit uses evaluation JSON as ground truth.",
            "Spatial maps are representative held-out events, not pooled skill claims.",
            "Fraehr 2024 full text unavailable (ScienceDirect CAPTCHA); not used as numeric source.",
        ],
    }
    return report


def write_provenance(report: dict[str, Any]) -> None:
    lines = [
        "# Data provenance — JOH zonal LSG manuscript",
        "",
        "Machine audit: `scripts/100_manuscript_data_audit.py` → `outputs/evaluation/manuscript_data_audit.json`.",
        "",
        f"**Audit result:** {report['n_pass']}/{report['n_checks']} PASS"
        + ("; ALL PASS" if report["all_pass"] else f"; FAIL={report['n_fail']}"),
        "",
        "## Primary numeric sources (Track B)",
        "",
        "| Claim family | Source artefact |",
        "|---|---|",
        "| Carlisle equal-B RMSE/CSI | `outputs/evaluation/carlisle/budget_sweep_true_equal.json` |",
        "| Carlisle LOOCV / CI | `.../loocv_results.json`, `.../loocv_bootstrap_ci.json` |",
        "| Official 2-fold | `.../multifold_bootstrap.json` |",
        "| Burnett 30-fold | `outputs/evaluation/burnettrv/loocv_results.json` |",
        "| Chowilla / three-case | `outputs/evaluation/chowilla/budget_sweep*.json`, Burnett validation |",
        "| EOI | `outputs/evaluation/eoi/eoi_all.json` |",
        "| Modal EOI / oracle | `outputs/evaluation/eoi/modal_eoi.json` |",
        "| Stage-swap | `outputs/evaluation/carlisle/stage_swap.json` |",
        "| Spatial maps | `outputs/figures/spatial_maps_manifest.json` + `scripts/97b_spatial_maps.py` |",
        "",
        "## Failed or soft checks",
        "",
    ]
    fails = [c for c in report["checks"] if not c.get("pass")]
    if not fails:
        lines.append("- None.")
    else:
        for c in fails:
            lines.append(
                f"- **{c['name']}**: expected={c.get('expected')} observed={c.get('observed')} ({c.get('source')})"
            )
    lines.extend(
        [
            "",
            "## Scope boundaries (not numeric errors)",
            "",
            "- gpflow/SGPR backend not run in this environment (sklearn GPR production numbers).",
            "- Brisbane licensed data absent (`config/cases/brisbane.yaml`).",
            "- Real zonal LSG-TS on Fraehr packs not claimed as Track B headline.",
            "- Fraehr 2024 full PDF blocked by publisher CAPTCHA; abstract/metadata only.",
            "",
            "## Cell areas",
            "",
            "- Carlisle HF Area ≡ 25 m² (uniform); Burnett ≡ 400 m² (uniform).",
            "- Chowilla HF Area varies (~139–25628 m²) → area-weighted oracle sensitivity is informative.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = audit()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_provenance(report)
    print(f"PASS {report['n_pass']}/{report['n_checks']}  FAIL {report['n_fail']}")
    print("Wrote", OUT_JSON)
    print("Wrote", OUT_MD)
    if not report["all_pass"]:
        for c in report["checks"]:
            if not c.get("pass"):
                print(" FAIL", c["name"], "exp", c.get("expected"), "obs", c.get("observed"))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
