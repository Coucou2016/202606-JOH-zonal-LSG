#!/usr/bin/env python
"""Inspect raw case data: list all NPZ files, their keys, shapes, and dtypes."""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def describe_npz(path: Path):
    try:
        data = np.load(path, allow_pickle=True)
    except Exception as e:
        print(f"[fail] {path}: {e}")
        return []

    rows = []
    for key in data.files:
        arr = data[key]
        shape = getattr(arr, "shape", None)
        dtype = getattr(arr, "dtype", None)
        rows.append({
            "file": str(path),
            "key": key,
            "shape": str(shape),
            "dtype": str(dtype),
        })
    return rows


def main():
    parser = argparse.ArgumentParser(description="Inspect NPZ files in a case directory")
    parser.add_argument("--case-dir", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    case_dir = Path(args.case_dir)
    rows = []

    for path in case_dir.rglob("*.npz"):
        rows.extend(describe_npz(path))

    df = pd.DataFrame(rows)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)

    print(df.head(50).to_string(index=False))
    print(f"\nSaved inspection table to {out}")
    print(f"Found {df['file'].nunique() if len(df) else 0} npz files")


if __name__ == "__main__":
    main()
