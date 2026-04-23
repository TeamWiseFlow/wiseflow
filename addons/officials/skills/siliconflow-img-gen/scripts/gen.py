#!/usr/bin/env python3
"""SiliconFlow image generation — stdlib only (no httpx/requests).

Two modes:
  text-to-image : default model Qwen/Qwen-Image
  image-edit    : default model Qwen/Qwen-Image-Edit-2509 (requires --image)
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

API_URL = "https://api.siliconflow.cn/v1/images/generations"

# Valid image_size values for Qwen/Qwen-Image
QWEN_SIZES = {
    "1328x1328",  # 1:1
    "1664x928",   # 16:9
    "928x1664",   # 9:16
    "1472x1140",  # 4:3
    "1140x1472",  # 3:4
    "1584x1056",  # 3:2
    "1056x1584",  # 2:3
}

DEFAULT_GEN_MODEL = "Qwen/Qwen-Image"
DEFAULT_EDIT_MODEL = "Qwen/Qwen-Image-Edit-2509"


def build_payload(args: argparse.Namespace) -> dict:
    is_edit_mode = bool(args.image)
    model = args.model or (DEFAULT_EDIT_MODEL if is_edit_mode else DEFAULT_GEN_MODEL)

    payload: dict = {
        "model": model,
        "prompt": args.prompt,
        "num_inference_steps": args.steps,
    }

    if is_edit_mode:
        payload["image"] = args.image
        if args.image2:
            payload["image2"] = args.image2
        if args.image3:
            payload["image3"] = args.image3
    else:
        size = args.image_size or "1328x1328"
        if size not in QWEN_SIZES:
            print(
                f"[warn] --image-size {size!r} is not in the Qwen valid size list. "
                f"Valid options: {sorted(QWEN_SIZES)}",
                file=sys.stderr,
            )
        payload["image_size"] = size

    if args.cfg is not None:
        payload["cfg"] = args.cfg

    if args.seed is not None:
        payload["seed"] = args.seed

    return payload


def api_request(payload: dict, api_key: str) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"[error] HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def download_image(url: str, dest_path: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "wiseflow-img-gen/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        dest_path.write_bytes(resp.read())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SiliconFlow image generation (text-to-image or image-edit)"
    )
    parser.add_argument("--prompt", required=True, help="Text description for the image")
    parser.add_argument("--model", default=None, help="Model ID (auto-selected by mode if omitted)")
    parser.add_argument(
        "--image-size",
        default=None,
        dest="image_size",
        help=(
            "Output resolution for text-to-image mode. "
            "Qwen valid values: 1328x1328 / 1664x928 / 928x1664 / 1472x1140 / "
            "1140x1472 / 1584x1056 / 1056x1584"
        ),
    )
    parser.add_argument("--steps", type=int, default=20, help="Inference steps (1–100)")
    parser.add_argument(
        "--cfg",
        type=float,
        default=None,
        help="CFG scale (Qwen: 0.1–20, recommended 4.0 for text-in-image)",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed (0–9999999999)")
    # image-edit inputs
    parser.add_argument("--image", default=None, help="Source image URL (enables image-edit mode)")
    parser.add_argument("--image2", default=None, help="Second source image URL (edit mode only)")
    parser.add_argument("--image3", default=None, help="Third source image URL (edit mode only)")
    parser.add_argument("--out-dir", default=None, dest="out_dir", help="Output directory")
    args = parser.parse_args()

    api_key = os.environ.get("SILICONFLOW_API_KEY")
    if not api_key:
        print("[error] SILICONFLOW_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    ts = int(time.time())
    out_dir = Path(args.out_dir) if args.out_dir else Path(f"./tmp/sf-img-{ts}")
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(args)
    mode = "image-edit" if args.image else "text-to-image"
    print(f"[info] Mode={mode} model={payload['model']} …")

    result = api_request(payload, api_key)

    images = result.get("images", [])
    if not images:
        print(f"[error] No images in response: {result}", file=sys.stderr)
        sys.exit(1)

    prompts_map: dict = {}
    for i, img in enumerate(images):
        url = img.get("url", "")
        dest = out_dir / f"{i:02d}.png"
        print(f"[info] Downloading image {i} → {dest}")
        download_image(url, dest)
        prompts_map[str(i)] = {"prompt": args.prompt, "url": url, "file": str(dest)}

    (out_dir / "prompts.json").write_text(json.dumps(prompts_map, ensure_ascii=False, indent=2))

    gallery_html = ["<!DOCTYPE html><html><body>"]
    for i in range(len(images)):
        gallery_html.append(f'<img src="{i:02d}.png" style="max-width:512px;margin:4px">')
    gallery_html.append("</body></html>")
    (out_dir / "index.html").write_text("\n".join(gallery_html))

    print(f"[done] {len(images)} image(s) saved to {out_dir}/")
    for k, v in prompts_map.items():
        print(f"  [{k}] {v['file']}")


if __name__ == "__main__":
    main()
