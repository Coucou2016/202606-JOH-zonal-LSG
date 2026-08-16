#!/usr/bin/env python
"""Download Figshare files — fresh download, NO resume (server breaks on Range)."""
import argparse, hashlib, time, os
from pathlib import Path
import requests
from tqdm import tqdm

BASE_URL = "https://api.figshare.com/v2"

def md5_file(path: Path) -> str:
    m = hashlib.md5()
    with path.open("rb") as f:
        while chunk := f.read(8*1024*1024):
            m.update(chunk)
    return m.hexdigest()

def refresh_url(article_id: str, filename: str) -> str | None:
    try:
        r = requests.get(f"{BASE_URL}/articles/{article_id}/files", timeout=60)
        r.raise_for_status()
        for item in r.json():
            if item["name"] == filename:
                return item["download_url"]
    except: pass
    return None

def download_file(url: str, out_path: Path, expected_md5: str | None,
                  max_retries: int, article_id: str):
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if complete
    if out_path.exists() and expected_md5:
        try:
            if out_path.stat().st_size > 1e9 and md5_file(out_path) == expected_md5:
                print(f"[skip] {out_path.name}: complete, MD5 verified")
                return
        except: pass
        # Remove any existing partial
        print(f"[clean] Removing old {out_path.name}")
        try: out_path.unlink()
        except:
            alt = out_path.with_suffix(f".old_{int(time.time())}")
            try: out_path.rename(alt)
            except: pass

    current_url = url
    attempt = 0
    while attempt < max_retries:
        attempt += 1
        try:
            print(f"[attempt {attempt}/{max_retries}] Downloading {out_path.name}...")
            resp = requests.get(current_url, stream=True, timeout=(30, 300))

            if resp.status_code == 403 and article_id:
                new = refresh_url(article_id, out_path.name)
                if new and new != current_url:
                    current_url = new
                    attempt -= 1
                    time.sleep(5)
                    continue

            resp.raise_for_status()
            total = int(resp.headers.get("content-length", 0))

            with out_path.open("wb") as f, tqdm(
                total=total, unit="B", unit_scale=True, desc=out_path.name
            ) as pbar:
                for chunk in resp.iter_content(chunk_size=4*1024*1024):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

            # Verify
            if expected_md5:
                print(f"Verifying {out_path.name}...")
                got = md5_file(out_path)
                if got == expected_md5:
                    print(f"[ok] {out_path.name}: MD5 verified ({out_path.stat().st_size/1024**3:.1f} GB)")
                    return
                print(f"[fail] MD5 mismatch, retrying...")
                out_path.unlink()
                time.sleep(5)
                continue
            return

        except (requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            print(f"[retry {attempt}/{max_retries}] {type(e).__name__}")
            if out_path.exists():
                try: out_path.unlink()
                except: pass
            time.sleep(10 * min(attempt, 6))
        except requests.exceptions.HTTPError as e:
            print(f"[retry {attempt}/{max_retries}] HTTP {e.response.status_code}")
            time.sleep(10 * min(attempt, 6))

    raise RuntimeError(f"Failed: {out_path.name} after {max_retries} attempts")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--article", required=True)
    parser.add_argument("--contains", nargs="+", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--max-retries", type=int, default=100)
    args = parser.parse_args()

    r = requests.get(f"{BASE_URL}/articles/{args.article}/files", timeout=60)
    r.raise_for_status()
    selected = [f for f in r.json()
                if any(k.lower() in f["name"].lower() for k in args.contains)]
    if not selected:
        print("No matching files.")
        return

    outdir = Path(args.outdir)
    for item in selected:
        print(f"Downloading {item['name']} ({item['size']/1024**3:.2f} GB)...")
        download_file(item["download_url"], outdir / item["name"],
                      item.get("supplied_md5"), args.max_retries, args.article)

if __name__ == "__main__":
    main()
