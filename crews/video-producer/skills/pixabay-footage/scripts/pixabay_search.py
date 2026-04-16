#!/usr/bin/env python3
"""
pixabay_search.py — Search and download copyright-free video clips from Pixabay.

Environment Variables:
  PIXABAY_API_KEY  Pixabay API key (required, register free at pixabay.com/api/docs)

Usage:
  python3 pixabay_search.py --terms "sunset,ocean waves" --aspect 9:16 --output-dir ./footage
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

import requests

PIXABAY_API = "https://pixabay.com/api/videos/"

ASPECT_MIN_WIDTH = {
    "9:16":  1080,
    "16:9":  1920,
    "1:1":   1080,
}


def log(msg: str) -> None:
    print(f"  {msg}", flush=True)


def require_env(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        print(json.dumps({"ok": False, "error": f"{name} is not set"}))
        sys.exit(1)
    return val


def md5(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()[:12]


def search_pixabay(term: str, aspect: str, min_duration: int, api_key: str) -> list[dict]:
    """Search Pixabay for video clips."""
    min_w = ASPECT_MIN_WIDTH[aspect]
    params = {"q": term, "video_type": "all", "per_page": 50, "key": api_key}
    url = f"{PIXABAY_API}?{urlencode(params)}"

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        log(f"Search failed for '{term}': {e}")
        return []

    results = []
    for v in data.get("hits", []):
        if v.get("duration", 0) < min_duration:
            continue
        for quality in ("large", "medium", "small", "tiny"):
            vf = v.get("videos", {}).get(quality, {})
            if int(vf.get("width", 0)) >= min_w:
                results.append({
                    "url": vf["url"],
                    "duration": v["duration"],
                    "term": term,
                })
                break
    return results


def download_clip(url: str, output_dir: Path, term: str) -> str | None:
    """Download a single clip. Returns local path or None on failure."""
    url_clean = url.split("?")[0]
    filename = f"pixabay-{term[:20].replace(' ', '-')}-{md5(url_clean)}.mp4"
    dest = output_dir / filename

    if dest.exists() and dest.stat().st_size > 0:
        return str(dest)

    try:
        resp = requests.get(url, timeout=(60, 240), stream=True)
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                f.write(chunk)
        if dest.stat().st_size > 0:
            return str(dest)
    except Exception as e:
        log(f"Download failed: {e}")
        if dest.exists():
            dest.unlink()
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Search and download Pixabay video clips")
    parser.add_argument("--terms", required=True)
    parser.add_argument("--aspect", default="9:16",
                        choices=["9:16", "16:9", "1:1"])
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--min-duration", type=int, default=5)
    parser.add_argument("--max-clips", type=int, default=15)
    args = parser.parse_args()

    api_key = require_env("PIXABAY_API_KEY")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    terms = [t.strip() for t in args.terms.split(",") if t.strip()]
    all_results: list[dict] = []
    seen_urls: set[str] = set()

    for term in terms:
        log(f"Searching Pixabay: '{term}' ({args.aspect})")
        clips = search_pixabay(term, args.aspect, args.min_duration, api_key)
        log(f"  Found {len(clips)} candidate clips")
        for clip in clips:
            if clip["url"] not in seen_urls:
                seen_urls.add(clip["url"])
                all_results.append(clip)
        time.sleep(0.5)

    downloaded: list[str] = []
    for clip in all_results:
        if len(downloaded) >= args.max_clips:
            break
        log(f"Downloading clip for '{clip['term']}' ({clip['duration']}s)...")
        path = download_clip(clip["url"], output_dir, clip["term"])
        if path:
            downloaded.append(path)
            log(f"  Saved: {Path(path).name}")
        time.sleep(0.3)

    print(f"\n✅ Downloaded {len(downloaded)} clips to {args.output_dir}")
    print("\n__RESULT_JSON__")
    print(json.dumps({
        "ok": True,
        "clips": downloaded,
        "total": len(downloaded),
        "output_dir": str(output_dir.resolve()),
    }, ensure_ascii=False))

    if not downloaded:
        sys.exit(1)


if __name__ == "__main__":
    main()
