#!/usr/bin/env python
"""List all files in a Figshare article for selective download."""
import argparse
import csv
import json
from pathlib import Path

import requests


BASE_URL = "https://api.figshare.com/v2"


def main():
    parser = argparse.ArgumentParser(description="List Figshare article files")
    parser.add_argument("--article", required=True, help="Figshare article ID, e.g. 24312658")
    parser.add_argument("--out", required=True, help="CSV manifest output path")
    args = parser.parse_args()

    url = f"{BASE_URL}/articles/{args.article}/files"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    files = r.json()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "name", "size_GB", "download_url", "supplied_md5"],
        )
        writer.writeheader()
        for item in files:
            writer.writerow({
                "id": item.get("id"),
                "name": item.get("name"),
                "size_GB": round(item.get("size", 0) / 1024**3, 3),
                "download_url": item.get("download_url"),
                "supplied_md5": item.get("supplied_md5"),
            })

    print(json.dumps(files, indent=2)[:4000])
    print(f"\nSaved manifest to {out}")


if __name__ == "__main__":
    main()
