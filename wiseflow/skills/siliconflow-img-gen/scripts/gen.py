#!/usr/bin/env python3
"""SiliconFlow image generation script."""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

import httpx

API_BASE = "https://api.siliconflow.cn/v1"
DEFAULT_MODEL = "Kwai-Kolors/Kolors"
VALID_SIZES = {"1024x1024", "960x1280", "768x1024", "720x1440", "720x1280"}


def get_api_key() -> str:
    key = os.environ.get("SILICONFLOW_API_KEY", "")
    if not key:
        print("Error: SILICONFLOW_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
    return key


def build_payload(args: argparse.Namespace) -> dict:
    payload: dict = {
        "model": args.model,
        "prompt": args.prompt,
        "image_size": args.image_size,
        "num_inference_steps": args.steps,
        "num_images": args.batch_size,
    }
    if args.negative_prompt:
        payload["negative_prompt"] = args.negative_prompt
    if args.guidance is not None:
        payload["guidance_scale"] = args.guidance
    if args.seed is not None:
        payload["seed"] = args.seed
    return payload


def generate_images(api_key: str, payload: dict) -> list[dict]:
    """Call the SiliconFlow images API and return list of {url, seed} dicts."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    url = f"{API_BASE}/images/generations"
    with httpx.Client(timeout=120) as client:
        resp = client.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        print(f"API error {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)
    data = resp.json()
    return data.get("images", [])


def download_image(image_url: str, dest: Path) -> None:
    with httpx.Client(timeout=60) as client:
        r = client.get(image_url)
    r.raise_for_status()
    # If the response is base64 (data URI)
    content = r.content
    if image_url.startswith("data:image"):
        _, b64 = image_url.split(",", 1)
        content = base64.b64decode(b64)
    dest.write_bytes(content)


def save_images(images: list[dict], out_dir: Path, prompt: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, img in enumerate(images):
        url = img.get("url", "")
        dest = out_dir / f"image_{i:02d}.png"
        if url.startswith("data:image"):
            _, b64 = url.split(",", 1)
            dest.write_bytes(base64.b64decode(b64))
        else:
            download_image(url, dest)
        paths.append(dest)
        print(f"Saved: {dest}")
    return paths


def write_metadata(images: list[dict], paths: list[Path], out_dir: Path, prompt: str) -> None:
    meta = {
        "prompt": prompt,
        "images": [
            {"file": str(p.name), "url": img.get("url", ""), "seed": img.get("seed")}
            for p, img in zip(paths, images)
        ],
    }
    (out_dir / "prompts.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))


def write_gallery(paths: list[Path], out_dir: Path, prompt: str) -> None:
    items = "\n".join(
        f'<li><img src="{p.name}" alt="{p.name}" style="max-width:400px"><p>{p.name}</p></li>'
        for p in paths
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Generated Images</title></head>
<body>
<h1>Generated Images</h1>
<p><strong>Prompt:</strong> {prompt}</p>
<ul style="list-style:none;padding:0">{items}</ul>
</body>
</html>"""
    (out_dir / "index.html").write_text(html)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate images via SiliconFlow API")
    parser.add_argument("--prompt", required=True, help="Image description")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model ID")
    parser.add_argument(
        "--image-size",
        default="1024x1024",
        choices=sorted(VALID_SIZES),
        help="Output resolution",
    )
    parser.add_argument("--batch-size", type=int, default=1, choices=range(1, 5), help="Number of images")
    parser.add_argument("--steps", type=int, default=20, help="Inference steps (1-100)")
    parser.add_argument("--guidance", type=float, default=None, help="Guidance scale (0-20)")
    parser.add_argument("--negative-prompt", default=None, help="Negative prompt")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory (default: ./tmp/sf-img-<timestamp>)",
    )
    args = parser.parse_args()

    if args.image_size not in VALID_SIZES:
        print(f"Invalid --image-size. Choose from: {', '.join(sorted(VALID_SIZES))}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.out_dir) if args.out_dir else Path(f"./tmp/sf-img-{int(time.time())}")
    api_key = get_api_key()
    payload = build_payload(args)

    print(f"Generating {args.batch_size} image(s) with model '{args.model}'...")
    images = generate_images(api_key, payload)
    if not images:
        print("No images returned from API.", file=sys.stderr)
        sys.exit(1)

    paths = save_images(images, out_dir, args.prompt)
    write_metadata(images, paths, out_dir, args.prompt)
    write_gallery(paths, out_dir, args.prompt)
    print(f"\nDone. {len(paths)} image(s) saved to: {out_dir}/")
    print(f"Gallery: {out_dir}/index.html")


if __name__ == "__main__":
    main()
