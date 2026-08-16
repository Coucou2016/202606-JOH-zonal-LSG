"""Extract Track B locked numbers for ChatGPT data audit (no secrets)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "outputs" / "evaluation"


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> None:
    out: dict = {}

    bud = load("carlisle/budget_sweep_true_equal.json")
    out["budget"] = {
        "lf_rmse": round(bud["lf_only"]["rmse_area"], 4),
        "lf_csi": round(bud["lf_only"]["csi_area"], 4),
        "rows": {
            b: {
                "global": round(v["global"]["rmse_area"], 4),
                "rule": round(v["rule"]["rmse_area"], 4),
                "kmeans": round(v["kmeans"]["rmse_area"], 4),
                "global_modes": v["global"].get("actual_modes"),
                "rule_modes": v["rule"].get("actual_modes"),
            }
            for b, v in bud["budgets"].items()
        },
    }

    loo = load("carlisle/loocv_results.json")
    for B in (4, 6):
        rows = [r for r in loo["per_event"] if r["B"] == B]
        deltas = [r["delta_rmse"] for r in rows]
        out[f"loocv_B{B}"] = {
            "n": len(rows),
            "improved": sum(x > 0 for x in deltas),
            "mean_delta": round(sum(deltas) / len(deltas), 4),
            "mean_global": round(sum(r["global_rmse"] for r in rows) / len(rows), 4),
            "mean_zonal": round(sum(r["zonal_rmse"] for r in rows) / len(rows), 4),
        }
        if "summary" in loo:
            out[f"loocv_B{B}"]["file_summary"] = loo.get("summary")

    # bootstrap / official if present
    for name in (
        "carlisle/multifold_bootstrap.json",
        "carlisle/official_fold_zonal.json",
        "carlisle/stage_swap.json",
        "eoi/eoi_all.json",
        "eoi/modal_eoi.json",
        "burnettrv/loocv_results.json",
    ):
        d = load(name)
        out[name] = {"top_keys": list(d.keys())[:30]}
        if "summary" in d:
            out[name]["summary"] = d["summary"]
        if name.endswith("stage_swap.json"):
            # LOOCV means if nested
            if "loocv_means" in d:
                out[name]["loocv_means"] = d["loocv_means"]
            if "loocv" in d:
                loc = d["loocv"]
                if isinstance(loc, dict) and "means" in loc:
                    out[name]["loocv_means"] = loc["means"]
                elif isinstance(loc, dict):
                    means = {}
                    for arm in ("GG", "ZZ", "GZ", "ZG"):
                        if arm in loc and isinstance(loc[arm], dict) and "rmse_area" in loc[arm]:
                            means[arm] = round(loc[arm]["rmse_area"], 4)
                        elif arm in loc and isinstance(loc[arm], list):
                            vals = [
                                x["rmse_area"] if isinstance(x, dict) else x
                                for x in loc[arm]
                            ]
                            means[arm] = round(sum(vals) / len(vals), 4)
                    if means:
                        out[name]["loocv_means"] = means
            # search recursively for mean dict
            blob = json.dumps(d)
            for key in ("mean_rmse", "loocv_mean", "fold_means"):
                if key in blob:
                    out[name][f"has_{key}"] = True
            # explicit walk
            def walk(obj, path=""):
                if isinstance(obj, dict):
                    if set(obj.keys()) >= {"GG", "ZZ"} and all(
                        isinstance(obj.get(a), (int, float)) for a in ("GG", "ZZ") if a in obj
                    ):
                        return {path: obj}
                    found = {}
                    for k, v in obj.items():
                        found.update(walk(v, f"{path}/{k}"))
                    return found
                if isinstance(obj, list):
                    found = {}
                    for i, v in enumerate(obj[:3]):
                        found.update(walk(v, f"{path}[{i}]"))
                    return found
                return {}

            candidates = walk(d)
            if candidates:
                out[name]["numeric_arm_dicts"] = {
                    k: v for k, v in list(candidates.items())[:10]
                }

        if name.endswith("eoi_all.json"):
            cases = d.get("cases") or d
            eoi_map = {}
            for c, v in cases.items() if isinstance(cases, dict) else []:
                if not isinstance(v, dict):
                    continue
                if "eoi" in v:
                    eoi_map[c] = round(v["eoi"], 3)
                elif "pooled" in v and isinstance(v["pooled"], dict) and "eoi" in v["pooled"]:
                    eoi_map[c] = round(v["pooled"]["eoi"], 3)
                else:
                    for kk, vv in v.items():
                        if isinstance(vv, dict) and "eoi" in vv:
                            eoi_map[c] = round(vv["eoi"], 3)
                            break
            out[name]["eoi"] = eoi_map

        if name.endswith("modal_eoi.json"):
            cases = d.get("cases", {})
            modal = {}
            for c, v in cases.items():
                pooled = v.get("pooled", v)
                modal[c] = {
                    "mean_zgg": round(pooled.get("mean_zgg", 0), 4),
                    "oracle_delta_rmse": round(pooled.get("oracle_delta_rmse", 0), 4),
                    "interpretation": pooled.get("interpretation"),
                }
            out[name]["modal"] = modal

        if name.endswith("burnettrv/loocv_results.json"):
            rows = d["per_event"]
            g = [r["global"]["rmse_area"] for r in rows]
            z = [r["rule"]["rmse_area"] for r in rows]
            dlt = [gg - zz for gg, zz in zip(g, z)]
            out[name]["computed"] = {
                "n": len(rows),
                "mean_global": round(sum(g) / len(g), 4),
                "mean_rule": round(sum(z) / len(z), 4),
                "mean_delta": round(sum(dlt) / len(dlt), 4),
                "improved": sum(x > 0 for x in dlt),
            }

        if name.endswith("multifold_bootstrap.json"):
            # keep useful summaries
            for k in ("B4", "B6", "official", "summary", "results", "bootstrap"):
                if k in d:
                    out[name][k] = d[k]

        if name.endswith("official_fold_zonal.json"):
            pub = d.get("published_mean", {}).get("MaxWD_R2", {})
            out[name]["published_MaxWD_R2_LSG"] = pub.get("LSG")
            # mean rule maxwd if available
            folds = d.get("per_fold", [])
            if folds and "rule" in folds[0]:
                r2 = [f["rule"].get("maxwd_r2") for f in folds if "rule" in f]
                g2 = [f["global"].get("maxwd_r2") for f in folds if "global" in f]
                out[name]["mean_rule_maxwd_r2"] = round(sum(r2) / len(r2), 3)
                out[name]["mean_global_maxwd_r2"] = round(sum(g2) / len(g2), 3)

    # three-case foldall
    three = {}
    for case in ("carlisle", "chowilla", "burnettrv"):
        three[case] = {}
        for label, fname in (
            ("lf", None),
            ("global", "global_lsg_ts_foldall_metrics.json"),
            ("rule", "zonal_lsg_ts_rule_k4_global_equal_foldall_metrics.json"),
        ):
            if label == "lf":
                continue
            p = ROOT / case / fname
            if not p.exists():
                continue
            dd = json.loads(p.read_text(encoding="utf-8"))
            rmse = dd.get("rmse_area")
            if rmse is None and isinstance(dd.get("metrics"), dict):
                rmse = dd["metrics"].get("rmse_area")
            if rmse is None and isinstance(dd.get("summary"), dict):
                rmse = dd["summary"].get("rmse_area")
            three[case][label] = {
                "rmse_area": round(rmse, 4) if isinstance(rmse, (int, float)) else rmse,
                "keys": list(dd.keys())[:15],
            }
            if "lf_only" in dd and isinstance(dd["lf_only"], dict):
                lf = dd["lf_only"]
                lf_rmse = lf.get("rmse_area")
                if lf_rmse is None and isinstance(lf.get("metrics"), dict):
                    lf_rmse = lf["metrics"].get("rmse_area")
                three[case]["lf"] = {
                    "rmse_area": round(lf_rmse, 4)
                    if isinstance(lf_rmse, (int, float))
                    else lf_rmse,
                    "keys": list(lf.keys())[:12],
                }
    out["three_case_foldall"] = three

    dest = Path(__file__).resolve().parent / "_trackb_numbers_extract.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(dest)
    print(json.dumps(out, indent=2, ensure_ascii=False)[:8000])


if __name__ == "__main__":
    main()
