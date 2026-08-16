"""Shared data loading utilities for scripts."""
from pathlib import Path

import numpy as np


def load_case_data(processed_dir: Path) -> dict:
    events_dir = processed_dir / "events"
    hf_ts_list, lf_ts_list, ids = [], [], []

    for f in sorted(events_dir.glob("*_event_*_HF_ts.npz")):
        data = np.load(f, allow_pickle=True)
        hf_ts_list.append(data["depth"])
        ids.append(str(data["event_id"]))
    for f in sorted(events_dir.glob("*_event_*_LF_ts.npz")):
        lf_ts_list.append(np.load(f, allow_pickle=True)["depth"])

    hf_ts = np.stack(hf_ts_list)
    lf_ts = np.stack(lf_ts_list)
    geo = np.load(processed_dir / "geometry.npz", allow_pickle=True)
    shape_hf = tuple(geo.get("shape_hf", np.array([30, 40])).tolist())
    shape_lf = tuple(geo.get("shape_lf", np.array([7, 10])).tolist())

    result = {
        "hf_ts": hf_ts, "lf_ts": lf_ts,
        "terrain_hf": geo["terrain_hf"],
        "shape_hf": shape_hf, "shape_lf": shape_lf,
        "event_ids": ids,
    }
    if "x_hf" in geo:
        result["x_hf"] = geo["x_hf"]
        result["y_hf"] = geo["y_hf"]
    return result


def make_split(event_ids: list, processed_dir: Path):
    splits_dir = processed_dir / "splits"
    if (splits_dir / "fold_00.json").exists():
        split_data = np.load(splits_dir / "fold_00.json", allow_pickle=True)
        return split_data["train"].astype(int), split_data["val"].astype(int)

    rng = np.random.default_rng(42)
    idx = rng.permutation(len(event_ids))
    n_train = int(0.8 * len(event_ids))
    return idx[:n_train], idx[n_train:]
