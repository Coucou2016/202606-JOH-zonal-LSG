"""Pull the real numbers needed to complete the Fraehr-style manuscript revision.

The user-supplied revision cites several figures without stating values. This
script extracts exactly those values from the evaluation JSON so the prose can be
completed without inventing anything.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "outputs" / "evaluation"


def load(rel: str):
    p = EV / rel
    if not p.exists():
        print(f"!! missing {rel}")
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def show(label: str, obj, depth: int = 0, maxdepth: int = 3) -> None:
    pad = "  " * depth
    if isinstance(obj, dict):
        print(f"{pad}{label}:")
        if depth >= maxdepth:
            print(f"{pad}  keys={list(obj)[:12]}")
            return
        for k, v in list(obj.items())[:14]:
            show(str(k), v, depth + 1, maxdepth)
    elif isinstance(obj, list):
        print(f"{pad}{label}: list[{len(obj)}] head={obj[:4]}")
    else:
        print(f"{pad}{label} = {obj}")


print("########## 1. CSI / MAE / bias by budget (Carlisle true-equal) ##########")
bs = load("carlisle/budget_sweep_true_equal.json")
if bs:
    show("budget_sweep_true_equal", bs, maxdepth=4)

print("\n########## 2. LF coarsening probe ##########")
show("lf_degradation", load("carlisle/lf_degradation.json"), maxdepth=4)

print("\n########## 3. Channel-distance zoning probe ##########")
show("distance_to_channel", load("carlisle/distance_to_channel.json"), maxdepth=4)

print("\n########## 4. Official fold / MaxWD R2 ##########")
off = load("carlisle/official_fold_zonal.json")
if isinstance(off, dict):
    for k in list(off)[:14]:
        v = off[k]
        if isinstance(v, (int, float, str)):
            print(f"  {k} = {v}")
        elif isinstance(v, dict):
            print(f"  {k}: keys={list(v)[:12]}")
        elif isinstance(v, list):
            print(f"  {k}: list[{len(v)}]")

print("\n########## 5. Modal EOI / ZGG / oracle ##########")
show("modal_eoi", load("eoi/modal_eoi.json"), maxdepth=4)

print("\n########## 6. Runtime / cost (Carlisle) ##########")
cb = load("carlisle/budget_sweep.json")
if isinstance(cb, dict) and "budgets" in cb:
    for b, arms in cb["budgets"].items():
        parts = []
        for arm, m in arms.items():
            if isinstance(m, dict) and "time_s" in m:
                parts.append(f"{arm}={m['time_s']:.2f}s")
        print(f"  B={b}: " + ", ".join(parts))
