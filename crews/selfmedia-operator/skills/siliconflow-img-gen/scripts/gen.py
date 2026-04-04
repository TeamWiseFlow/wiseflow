#!/usr/bin/env python3
"""SiliconFlow image generation/editing — stdlib only (no httpx/requests)."""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://api.siliconflow.cn/v1/images/generations"

DEFAULT_GEN_MODEL = "Qwen/Qwen-Image"
DEFAULT_EDIT_MODEL = "Qwen/Qwen-Image-Edit-2509"


def default_out_dir() -> Path:
    """Return a migration-friendly default output directory.

    Resolve from this script location:
    <workspace>/skills/siliconflow-img-gen/scripts/gen.py
      -> <workspace>/campaign_assets
    """
    workspace_root = Path(__file__).resolve().parents[3]
    return workspace_root / "campaign_assets"


def build_payload(args, model: str):
    payload = {
        "model": model,
        "prompt": args.prompt,
        "num_inference_steps": args.steps,
        "cfg": args.cfg,
    }

    # image_size is used for text-to-image. Edit models may ignore it silently.
    payload["image_size"] = args.image_size

    # Output format (png/jpg)
    output_format = args.format.lower()
    if output_format == "jpeg":
        output_format = "jpg"
    if output_format in ["jpg", "jpeg"]:
        payload["output_format"] = "jpeg"

    if args.negative_prompt:
        payload["negative_prompt"] = args.negative_prompt
    if args.seed is not None:
        payload["seed"] = args.seed

    # Edit mode accepts image/image2/image3
    if args.image:
        payload["image"] = args.image
    if args.image2:
        payload["image2"] = args.image2
    if args.image3:
        payload["image3"] = args.image3

    # batch_size is useful for text generation variants.
    if args.batch_size is not None:
        payload["batch_size"] = args.batch_size

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


def is_edit_mode(args) -> bool:
    return bool(args.image)


def resolve_model(args) -> str:
    if args.model:
        return args.model
    return DEFAULT_EDIT_MODEL if is_edit_mode(args) else DEFAULT_GEN_MODEL


def main():
    parser = argparse.ArgumentParser(description="SiliconFlow image generation/editing")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--model", default=None, help="Model ID (auto by mode if omitted)")
    parser.add_argument("--image-size", default="1024x1024", dest="image_size")
    parser.add_argument("--batch-size", type=int, default=1, dest="batch_size")
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--cfg", type=float, default=4)
    parser.add_argument("--negative-prompt", default=None, dest="negative_prompt")
    parser.add_argument("--seed", type=int, default=None)

    # Image-edit inputs. --image enables edit mode.
    parser.add_argument("--image", default=None, help="Original image URL (required for edit mode)")
    parser.add_argument("--image2", default=None, help="Optional second image URL")
    parser.add_argument("--image3", default=None, help="Optional third image URL")

    parser.add_argument("--out-dir", default=None, dest="out_dir")
    parser.add_argument("--format", default="jpg", choices=["png", "jpg", "jpeg"], help="Output image format (default: jpg)")
    args = parser.parse_args()

    api_key = os.environ.get("SILICONFLOW_API_KEY")
    if not api_key:
        print("[error] SILICONFLOW_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    if (args.image2 or args.image3) and not args.image:
        print("[error] --image2/--image3 require --image", file=sys.stderr)
        sys.exit(1)

    model = resolve_model(args)

    ts = int(time.time())
    out_root = Path(args.out_dir) if args.out_dir else default_out_dir()
    out_dir = out_root / f"sf-img-{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(args, model)
    print(f"[info] Requesting image(s): model={model} edit_mode={is_edit_mode(args)}")
    result = api_request(payload, api_key)

    images = result.get("images", [])
    if not images:
        print(f"[error] No images in response: {result}", file=sys.stderr)
        sys.exit(1)

    # Determine output extension
    output_format = args.format.lower()
    if output_format == "jpeg":
        output_format = "jpg"
    ext = output_format

    prompts_map = {}
    for i, img in enumerate(images):
        url = img.get("url", "")
        dest = out_dir / f"{i:02d}.{ext}"
        print(f"[info] Downloading image {i} -> {dest}")
        download_image(url, dest)
        prompts_map[str(i)] = {
            "prompt": args.prompt,
            "url": url,
            "file": str(dest),
            "model": model,
            "edit_mode": is_edit_mode(args),
            "source_image": args.image or "",
            "source_image2": args.image2 or "",
            "source_image3": args.image3 or "",
        }

    (out_dir / "prompts.json").write_text(
        json.dumps(prompts_map, ensure_ascii=False, indent=2)
    )

    gallery_html = ["<!DOCTYPE html><html><body>"]
    for i in range(len(images)):
        gallery_html.append(
            f'<img src="{i:02d}.{ext}" style="max-width:512px;margin:4px">'
        )
    gallery_html.append("</body></html>")
    (out_dir / "index.html").write_text("\n".join(gallery_html))

    print(f"[done] {len(images)} image(s) saved to {out_dir}/")
    for k, v in prompts_map.items():
        print(f"  [{k}] {v['file']}")


if __name__ == "__main__":
    main()
