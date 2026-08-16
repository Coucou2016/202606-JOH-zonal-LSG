#!/usr/bin/env python
"""Monitor Figshare downloads and report progress."""
import sys, time, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/external/fraehr2024"

files = {
    "Chowilla.zip": 31986950697,  # 29.79 GB
    "BurnettRV.zip": 31985118625,  # 29.79 GB
}

def get_size_mb(path):
    try: return os.path.getsize(path) / 1024**2
    except: return 0

print(f"Download Monitor — {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
for name, expected in files.items():
    path = DATA / name
    # Fallback to stalled copy if main file missing
    if not path.exists():
        alt = DATA / name.replace(".zip", "_stalled.zip")
        if alt.exists():
            path = alt
    size_mb = get_size_mb(path)
    expected_mb = expected / 1024**2
    pct = size_mb / expected_mb * 100 if expected_mb > 0 else 0
    bar_len = 30
    filled = int(bar_len * pct / 100)
    bar = "#" * filled + "-" * (bar_len - filled)
    status = "COMPLETE" if pct > 99.9 else f"{pct:.1f}%"
    print(f"  {name}: [{bar}] {status} ({size_mb:.0f}/{expected_mb:.0f} MB)")

total_done = sum(get_size_mb(DATA/n) for n in files)
total_expected = sum(v/1024**2 for v in files.values())
print(f"\n  Total: {total_done:.0f}/{total_expected:.0f} MB ({total_done/total_expected*100:.1f}%)")

# Check if downloads complete
all_done = all(get_size_mb(DATA/n) / (files[n]/1024**2) > 99.9 for n in files)
if all_done:
    print("\n*** ALL DOWNLOADS COMPLETE ***")
    # Verify MD5
    import hashlib
    expected_md5s = {
        "Chowilla.zip": "16e3f4d2b8514b1493a1d78af2751707",
        "BurnettRV.zip": "93df54d5bb54e9b23a09e648648146d8",
    }
    for name, expected_md5 in expected_md5s.items():
        path = DATA / name
        if path.exists():
            print(f"  Verifying {name}...")
            m = hashlib.md5()
            with open(path, "rb") as f:
                while True:
                    chunk = f.read(8*1024*1024)
                    if not chunk: break
                    m.update(chunk)
            got = m.hexdigest()
            ok = got == expected_md5
            print(f"    MD5: {got[:16]}... — {'OK' if ok else 'FAIL'}")
    sys.exit(0)
else:
    print("\n  Status: Downloading...")
    sys.exit(1)
