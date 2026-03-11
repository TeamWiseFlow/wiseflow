#!/usr/bin/env python3
"""SiliconFlow video generation script (text-to-video and image-to-video)."""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import httpx

API_BASE = "https://api.siliconflow.cn/v1"
T2V_MODEL = "Wan-AI/Wan2.2-T2V-A14B"
I2V_MODEL = "Wan-AI/Wan2.2-I2V-A14B"
VALID_SIZES = {"1280x720", "720x1280", "960x960"}


def get_api_key() -> str:
    key = os.environ.get("SILICONFLOW_API_KEY", "")
    if not key:
        print("Error: SILICONFLOW_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
    return key


def submit_job(api_key: str, payload: dict) -> str:
    """Submit the video generation job and return requestId."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    url = f"{API_BASE}/video/submit"
    with httpx.Client(timeout=60) as client:
        resp = client.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        print(f"Submit error {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)
    data = resp.json()
    request_id = data.get("requestId")
    if not request_id:
        print(f"No requestId in response: {data}", file=sys.stderr)
        sys.exit(1)
    return request_id


def poll_status(api_key: str, request_id: str, poll_interval: int, timeout: int) -> dict:
    """Poll the video status endpoint until done or timeout."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    url = f"{API_BASE}/video/status"
    deadline = time.time() + timeout
    while time.time() < deadline:
        with httpx.Client(timeout=30) as client:
            resp = client.post(url, headers=headers, json={"requestId": request_id})
        if resp.status_code != 200:
            print(f"Status error {resp.status_code}: {resp.text}", file=sys.stderr)
            sys.exit(1)
        data = resp.json()
        status = data.get("status", "")
        print(f"  Status: {status}")
        if status == "Succeed":
            return data
        if status == "Failed":
            reason = data.get("reason", "unknown")
            print(f"Generation failed: {reason}", file=sys.stderr)
            sys.exit(1)
        # InQueue or InProgress — keep polling
        time.sleep(poll_interval)
    print(f"Timed out after {timeout}s waiting for video generation.", file=sys.stderr)
    sys.exit(1)


def download_video(video_url: str, dest: Path) -> None:
    print(f"Downloading video to {dest} ...")
    with httpx.Client(timeout=300) as client:
        with client.stream("GET", video_url) as r:
            r.raise_for_status()
            with dest.open("wb") as f:
                for chunk in r.iter_bytes(chunk_size=8192):
                    f.write(chunk)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate videos via SiliconFlow API")
    parser.add_argument("--prompt", required=True, help="Video description")
    parser.add_argument(
        "--model",
        default=T2V_MODEL,
        choices=[T2V_MODEL, I2V_MODEL],
        help="Model ID",
    )
    parser.add_argument(
        "--image",
        default=None,
        help="Image URL or base64 data URI (required for I2V model)",
    )
    parser.add_argument(
        "--image-size",
        default="1280x720",
        choices=sorted(VALID_SIZES),
        help="Video resolution",
    )
    parser.add_argument("--negative-prompt", default=None, help="Negative prompt")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--poll-interval", type=int, default=10, help="Seconds between polls")
    parser.add_argument("--timeout", type=int, default=600, help="Max seconds to wait")
    parser.add_argument("--out-dir", default=None, help="Output directory")
    args = parser.parse_args()

    # Validate I2V requires image
    if args.model == I2V_MODEL and not args.image:
        print(f"Error: --image is required when using model '{I2V_MODEL}'.", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.out_dir) if args.out_dir else Path(f"./tmp/sf-video-{int(time.time())}")
    out_dir.mkdir(parents=True, exist_ok=True)

    api_key = get_api_key()

    payload: dict = {
        "model": args.model,
        "prompt": args.prompt,
        "image_size": args.image_size,
    }
    if args.image:
        payload["image"] = args.image
    if args.negative_prompt:
        payload["negative_prompt"] = args.negative_prompt
    if args.seed is not None:
        payload["seed"] = args.seed

    print(f"Submitting video generation job (model: {args.model})...")
    request_id = submit_job(api_key, payload)
    print(f"Job submitted. requestId: {request_id}")
    print("Polling for completion (this typically takes 1–5 minutes)...")

    result = poll_status(api_key, request_id, args.poll_interval, args.timeout)

    videos = result.get("results", {}).get("videos", [])
    if not videos:
        print("No videos in result.", file=sys.stderr)
        sys.exit(1)

    video_url = videos[0].get("url", "")
    if not video_url:
        print("Empty video URL in result.", file=sys.stderr)
        sys.exit(1)

    video_path = out_dir / f"video_{request_id[:8]}.mp4"
    download_video(video_url, video_path)

    # Save full result metadata
    result_path = out_dir / "result.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))

    print(f"\nDone. Video saved to: {video_path}")
    print(f"Metadata: {result_path}")


if __name__ == "__main__":
    main()
