#!/usr/bin/env python
"""Smart Chowilla downloader with proper resume support detection.

Do not start a 30 GB Chowilla re-download unless explicitly requested.
"""
import hashlib, os, sys, time, requests
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
URL = "https://ndownloader.figshare.com/files/44120567"
DEST = str(_ROOT / "data" / "external" / "fraehr2024" / "Chowilla.zip")
EXPECTED_MD5 = "16e3f4d2b8514b1493a1d78af2751707"
EXPECTED_SIZE = 31986950697

def md5_file(path):
    m = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(8*1024*1024):
            m.update(chunk)
    return m.hexdigest()

def get_direct_url():
    """Follow redirect to get the actual storage URL"""
    r = requests.head(URL, allow_redirects=False, timeout=30)
    if r.status_code == 302:
        return r.headers["Location"]
    return URL

def test_resume_support(direct_url):
    """Test if the storage server supports Range requests"""
    try:
        r = requests.get(direct_url, headers={"Range": "bytes=0-0"}, timeout=30)
        return r.status_code == 206
    except:
        return False

def download():
    dest_dir = os.path.dirname(DEST)
    os.makedirs(dest_dir, exist_ok=True)

    # Check if already complete
    if os.path.exists(DEST):
        size = os.path.getsize(DEST)
        if size == EXPECTED_SIZE:
            print(f"Existing file: {size/1024**3:.1f} GB, verifying MD5...")
            if md5_file(DEST) == EXPECTED_MD5:
                print("ALREADY COMPLETE — MD5 verified!")
                return True
            else:
                print("MD5 mismatch, restarting...")
                os.remove(DEST)
        else:
            print(f"Partial file ({size/1024**3:.1f} GB), checking resume support...")
            direct_url = get_direct_url()
            if test_resume_support(direct_url):
                print(f"Resume SUPPORTED! Continuing from {size/1024**3:.1f} GB")
                # Use Range to resume
                resume_pos = size
            else:
                print("Resume NOT supported, restarting from scratch")
                os.remove(DEST)
                resume_pos = 0
    else:
        resume_pos = 0

    attempt = 0
    while attempt < 200:
        attempt += 1
        try:
            # Get fresh URL each attempt
            direct_url = get_direct_url()
            headers = {}
            if resume_pos > 0:
                headers["Range"] = f"bytes={resume_pos}-"
                print(f"[{attempt}/200] Resuming from {resume_pos/1024**3:.2f} GB...")
            else:
                print(f"[{attempt}/200] Starting fresh download...")

            resp = requests.get(direct_url, headers=headers, stream=True,
                               timeout=(30, 300))

            if resp.status_code == 206:
                print("  Server returned 206 (Partial Content) — resume OK")
            elif resp.status_code == 200 and resume_pos > 0:
                print("  Server returned 200 (Full Content) — resume NOT supported, restarting")
                resume_pos = 0
                os.remove(DEST) if os.path.exists(DEST) else None
                continue

            if resp.status_code in (403, 410):
                print("  URL expired, getting fresh URL next attempt...")
                time.sleep(5)
                continue

            resp.raise_for_status()

            mode = "ab" if resume_pos > 0 else "wb"
            total = int(resp.headers.get("content-length", 0)) + resume_pos
            downloaded = resume_pos

            with open(DEST, mode) as f:
                for chunk in resp.iter_content(chunk_size=4*1024*1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        pct = downloaded / EXPECTED_SIZE * 100
                        print(f"\r  {downloaded/1024**3:.1f}/{EXPECTED_SIZE/1024**3:.1f} GB ({pct:.1f}%)  "
                              f"speed: {len(chunk)/1024/1024:.1f} MB/s   ", end="", flush=True)

            print()  # newline after progress

            # Verify
            actual_size = os.path.getsize(DEST)
            if actual_size == EXPECTED_SIZE:
                print("  Size OK! Verifying MD5...")
                if md5_file(DEST) == EXPECTED_MD5:
                    print("  *** MD5 VERIFIED — DOWNLOAD COMPLETE! ***")
                    return True
                else:
                    print("  MD5 FAILED, removing and retrying...")
                    os.remove(DEST)
                    resume_pos = 0
                    time.sleep(10)
                    continue
            else:
                print(f"  Size mismatch: {actual_size} != {EXPECTED_SIZE}")
                resume_pos = actual_size  # try to resume from here

        except (requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            print(f"\n  {type(e).__name__}, retrying in {min(attempt*5, 120)}s...")
            # Keep the partial file for resume
            if os.path.exists(DEST):
                resume_pos = os.path.getsize(DEST)
            time.sleep(min(attempt * 5, 120))
        except Exception as e:
            print(f"\n  Error: {e}")
            time.sleep(10)

    print("Exhausted all retries.")
    return False

if __name__ == "__main__":
    print(f"Downloading Chowilla.zip ({EXPECTED_SIZE/1024**3:.1f} GB)")
    print(f"Destination: {DEST}")
    success = download()
    sys.exit(0 if success else 1)
