#!/usr/bin/env python
"""Build pre-registered wet-mask comparison table from A4 extrap_zonal.json.

Does not re-run models. Writes:
  outputs/evaluation/carlisle/extrap_wetmask_preregistered.json
  outputs/tables/table_extrap_wetmask.csv
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "outputs" / "evaluation" / "carlisle" / "extrap_zonal.json"
OUT_JSON = ROOT / "outputs" / "evaluation" / "carlisle" / "extrap_wetmask_preregistered.json"
OUT_CSV = ROOT / "outputs" / "tables" / "table_extrap_wetmask.csv"

MASKS = (
    ("mask_train", "train_wet"),
    ("mask_official_interp", "official_interp_wet"),
    ("mask_official_extrap", "official_extrap_wet"),
    ("mask_all", "all_cells"),
)


def main() -> None:
    raw = json.loads(SRC.read_text(encoding="utf-8"))
    n_wet = (raw.get("config") or {}).get("n_wet") or {}
    rows = []
    for ev in raw.get("per_event") or []:
        eid = ev.get("event")
        for model in ("lf_only", "global", "rule"):
            block = ev.get(model) or {}
            for mask_key, mask_lab in MASKS:
                m = block.get(mask_key)
                if not isinstance(m, dict):
                    continue
                rows.append({
                    "event": eid,
                    "model": model,
                    "mask": mask_lab,
                    "n_wet": m.get("n_wet"),
                    "rmse_wet": m.get("rmse_wet"),
                    "maxwd_r2": m.get("maxwd_r2"),
                    "csi": m.get("csi"),
                    "peak_diff": m.get("peak_diff"),
                    "rmse_area_full": block.get("rmse_area"),
                })

    payload = {
        "protocol": "pre_registered_wet_masks",
        "source": str(SRC.as_posix()),
        "n_wet_counts": n_wet,
        "note": (
            "Masks are pre-registered: train_wet / official_interp / official_extrap / all_cells. "
            "Do not post-select the mask that maximises R2. LF-only remains the fair extrap baseline."
        ),
        "rows": rows,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "event", "model", "mask", "n_wet", "rmse_wet",
                "maxwd_r2", "csi", "peak_diff", "rmse_area_full",
            ],
        )
        w.writeheader()
        for r in rows:
            w.writerow({
                k: ("" if r.get(k) is None else (f"{r[k]:.6f}" if isinstance(r[k], float) else r[k]))
                for k in w.fieldnames
            })
    print(f"Wrote {OUT_JSON} ({len(rows)} rows)")
    print(f"Wrote {OUT_CSV}")


if __name__ == "__main__":
    main()
