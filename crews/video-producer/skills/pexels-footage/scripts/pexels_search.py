#!/usr/bin/env python3
"""
pexels_search.py — Search and download copyright-free video clips from Pexels.

Environment Variables:
  PEXELS_API_KEY   Pexels API key (required, register free at pexels.com/api)

Usage:
  python3 pexels_search.py --terms "sunset,ocean waves" --aspect 9:16 --output-dir ./footage
  python3 pexels_search.py --terms "city traffic,business meeting" --aspect 16:9 --output-dir ./footage --max-clips 20
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

PEXELS_API = "https://api.pexels.com/videos/search"

ASPECT_RESOLUTIONS = {
    "9:16":  (1080, 1920),
    "16:9":  (1920, 1080),
    "1:1":   (1080, 1080),
}

ORIENTATION_MAP = {
    "9:16":  "portrait",
    "16:9":  "landscape",
    "1:1":   "square",
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


def search_pexels(term: str, aspect: str, min_duration: int, api_key: str) -> list[dict]:
    """Search Pexels for video clips matching term and aspect ratio."""
    w, h = ASPECT_RESOLUTIONS[aspect]
    orientation = ORIENTATION_MAP[aspect]

    params = {"query": term, "per_page": 20, "orientation": orientation}
    url = f"{PEXELS_API}?{urlencode(params)}"

    try:
        resp = requests.get(
            url,
            headers={"Authorization": api_key,
                     "User-Agent": "Mozilla/5.0"},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        log(f"Search failed for '{term}': {e}")
        return []

    results = []
    for v in data.get("videos", []):
        if v.get("duration", 0) < min_duration:
            continue
        for vf in v.get("video_files", []):
            if int(vf.get("width", 0)) == w and int(vf.get("height", 0)) == h:
                results.append({
                    "url": vf["link"],
                    "duration": v["duration"],
                    "term": term,
                })
                break
    return results


def download_clip(url: str, output_dir: Path, term: str) -> str | None:
    """Download a single video clip. Returns local path or None on failure."""
    url_clean = url.split("?")[0]
    filename = f"pexels-{term[:20].replace(' ', '-')}-{md5(url_clean)}.mp4"
    dest = output_dir / filename

    if dest.exists() and dest.stat().st_size > 0:
        return str(dest)

    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=(60, 240),
            stream=True,
        )
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
    parser = argparse.ArgumentParser(description="Search and download Pexels video clips")
    parser.add_argument("--terms", required=True,
                        help="Comma-separated search terms (one per scene)")
    parser.add_argument("--aspect", default="9:16",
                        choices=list(ASPECT_RESOLUTIONS.keys()),
                        help="Aspect ratio (default: 9:16)")
    parser.add_argument("--output-dir", required=True,
                        help="Directory to save downloaded clips")
    parser.add_argument("--min-duration", type=int, default=5,
                        help="Minimum clip duration in seconds (default: 5)")
    parser.add_argument("--max-clips", type=int, default=15,
                        help="Maximum total clips to download (default: 15)")
    args = parser.parse_args()

    api_key = require_env("PEXELS_API_KEY")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    terms = [t.strip() for t in args.terms.split(",") if t.strip()]
    all_results: list[dict] = []
    seen_urls: set[str] = set()

    # Collect candidate clips (deduplicated)
    for term in terms:
        log(f"Searching Pexels: '{term}' ({args.aspect})")
        clips = search_pexels(term, args.aspect, args.min_duration, api_key)
        log(f"  Found {len(clips)} candidate clips")
        for clip in clips:
            if clip["url"] not in seen_urls:
                seen_urls.add(clip["url"])
                all_results.append(clip)
        time.sleep(0.3)  # be polite with the API

    # Download up to max-clips
    downloaded: list[str] = []
    for clip in all_results:
        if len(downloaded) >= args.max_clips:
            break
        log(f"Downloading clip for '{clip['term']}' ({clip['duration']}s)...")
        path = download_clip(clip["url"], output_dir, clip["term"])
        if path:
            downloaded.append(path)
            log(f"  Saved: {Path(path).name}")
        time.sleep(0.2)

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
