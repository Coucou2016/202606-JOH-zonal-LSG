"""I/O utilities for loading/saving standardized case data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


def save_geometry(
    path: Path,
    x_hf: np.ndarray,
    y_hf: np.ndarray,
    terrain_hf: np.ndarray,
    area_hf: np.ndarray,
    x_lf: np.ndarray | None = None,
    y_lf: np.ndarray | None = None,
    terrain_lf: np.ndarray | None = None,
    area_lf: np.ndarray | None = None,
    main_flow_path_x: np.ndarray | None = None,
    main_flow_path_y: np.ndarray | None = None,
    meta: dict[str, Any] | None = None,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {
        "x_hf": x_hf,
        "y_hf": y_hf,
        "terrain_hf": terrain_hf,
        "area_hf": area_hf,
    }
    if x_lf is not None:
        kwargs["x_lf"] = x_lf
        kwargs["y_lf"] = y_lf
        kwargs["terrain_lf"] = terrain_lf if terrain_lf is not None else np.array([])
        kwargs["area_lf"] = area_lf if area_lf is not None else np.array([])
    if main_flow_path_x is not None:
        kwargs["main_flow_path_x"] = main_flow_path_x
        kwargs["main_flow_path_y"] = main_flow_path_y
    kwargs["meta"] = np.array(json.dumps(meta or {}))
    np.savez_compressed(path, **kwargs)


def load_geometry(path: Path) -> dict[str, Any]:
    raw = np.load(path, allow_pickle=True)
    result = {
        "x_hf": raw["x_hf"],
        "y_hf": raw["y_hf"],
        "terrain_hf": raw["terrain_hf"],
        "area_hf": raw["area_hf"],
    }
    if "x_lf" in raw:
        result["x_lf"] = raw["x_lf"]
        result["y_lf"] = raw["y_lf"]
        result["terrain_lf"] = raw["terrain_lf"]
        result["area_lf"] = raw["area_lf"]
    if "main_flow_path_x" in raw:
        result["main_flow_path_x"] = raw["main_flow_path_x"]
        result["main_flow_path_y"] = raw["main_flow_path_y"]
    result["meta"] = json.loads(str(raw["meta"]))
    return result


def save_event(
    path: Path,
    depth: np.ndarray,
    time: np.ndarray | None = None,
    event_id: str = "",
    is_hf: bool = True,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"depth": depth, "event_id": np.array(event_id)}
    if time is not None:
        kwargs["time"] = time
    kind = "HF" if is_hf else "LF"
    kwargs["kind"] = np.array(kind)
    np.savez_compressed(path, **kwargs)


def load_event(path: Path) -> dict[str, Any]:
    raw = np.load(path, allow_pickle=True)
    result = {"depth": raw["depth"], "event_id": str(raw["event_id"])}
    if "time" in raw:
        result["time"] = raw["time"]
    result["is_hf"] = str(raw.get("kind", "HF")) == "HF"
    return result


def save_max_surface(
    path: Path,
    max_depth: np.ndarray,
    event_id: str = "",
    is_hf: bool = True,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        max_depth=max_depth,
        event_id=np.array(event_id),
        kind=np.array("HF" if is_hf else "LF"),
    )


def load_max_surface(path: Path) -> dict[str, Any]:
    raw = np.load(path, allow_pickle=True)
    return {
        "max_depth": raw["max_depth"],
        "event_id": str(raw["event_id"]),
        "is_hf": str(raw.get("kind", "HF")) == "HF",
    }


def save_split(path: Path, train_indices: np.ndarray, val_indices: np.ndarray) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, train=train_indices, val=val_indices)


def load_split(path: Path) -> dict[str, np.ndarray]:
    raw = np.load(path)
    return {"train": raw["train"], "val": raw["val"]}


def save_metrics(path: Path, metrics: dict[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


def load_metrics(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)
