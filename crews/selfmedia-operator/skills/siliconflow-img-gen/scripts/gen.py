#!/usr/bin/env python3
"""SiliconFlow image generation — stdlib only (no httpx/requests)."""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

API_URL = "https://api.siliconflow.cn/v1/images/generations"

# Models that accept guidance_scale and batch_size
KOLORS_MODELS = {"kwai-kolors/kolors"}

def build_payload(args):
    model = args.model
    payload = {
        "model": model,
        "prompt": args.prompt,
        "image_size": args.image_size,
        "num_inference_steps": args.steps,
        "batch_size": args.batch_size,
    }
    # guidance_scale only supported by Kolors
    if args.guidance is not None:
        if model.lower() in KOLORS_MODELS:
            payload["guidance_scale"] = args.guidance
        else:
            print(f"[warn] --guidance ignored for model {model}", file=sys.stderr)
    if args.negative_prompt:
        payload["negative_prompt"] = args.negative_prompt
    if args.seed is not None:
        payload["seed"] = args.seed
    # Qwen does not accept image_size or batch_size in some variants — keep them
    # but note the model may ignore them silently
    return payload


def api_request(payload, api_key):
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


def download_image(url, dest_path):
    req = urllib.request.Request(url, headers={"User-Agent": "wiseflow-img-gen/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        dest_path.write_bytes(resp.read())


def main():
    parser = argparse.ArgumentParser(description="SiliconFlow image generation")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--model", default="Qwen/Qwen-Image-Edit-2509")
    parser.add_argument("--image-size", default="1024x1024", dest="image_size")
    parser.add_argument("--batch-size", type=int, default=1, dest="batch_size")
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--guidance", type=float, default=None)
    parser.add_argument("--negative-prompt", default=None, dest="negative_prompt")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--out-dir", default=None, dest="out_dir")
    args = parser.parse_args()

    api_key = os.environ.get("SILICONFLOW_API_KEY")
    if not api_key:
        print("[error] SILICONFLOW_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    ts = int(time.time())
    out_dir = Path(args.out_dir) if args.out_dir else Path(f"./tmp/sf-img-{ts}")
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(args)
    print(f"[info] Generating image with model={args.model} size={args.image_size} …")
    result = api_request(payload, api_key)

    images = result.get("images", [])
    if not images:
        print(f"[error] No images in response: {result}", file=sys.stderr)
        sys.exit(1)

    prompts_map = {}
    for i, img in enumerate(images):
        url = img.get("url", "")
        dest = out_dir / f"{i:02d}.png"
        print(f"[info] Downloading image {i} → {dest}")
        download_image(url, dest)
        prompts_map[str(i)] = {"prompt": args.prompt, "url": url, "file": str(dest)}

    (out_dir / "prompts.json").write_text(json.dumps(prompts_map, ensure_ascii=False, indent=2))

    # Simple HTML gallery
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
