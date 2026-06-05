#!/usr/bin/env python3
"""Publish posts and reels to Instagram via Meta Graph API (content container pattern)."""

import argparse
import json
import sys
import time
from pathlib import Path

import requests

CREDS_DIR = Path.home() / ".openclaw" / "credentials"
CONFIG_FILE = CREDS_DIR / "instagram_config.json"
GRAPH_API = "https://graph.facebook.com/v23.0"
POLL_INTERVAL = 5
POLL_MAX = 60


def output(data: dict) -> None:
    sys.stdout.write(json.dumps(data, ensure_ascii=False) + "\n")


def err_exit(msg: str, code: int = 1) -> None:
    sys.stderr.write(f"[instagram-publish] ERROR: {msg}\n")
    output({"ok": False, "error": msg})
    sys.exit(code)


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        err_exit("AUTH_REQUIRED: no instagram_config.json", 2)
    return json.loads(CONFIG_FILE.read_text())


def api_post(path: str, token: str, data: dict | None = None) -> dict:
    params = {"access_token": token}
    resp = requests.post(f"{GRAPH_API}{path}", params=params, json=data, timeout=30)
    if resp.status_code in (401, 403):
        err_exit("AUTH_REQUIRED", 2)
    result = resp.json()
    if "error" in result:
        err_exit(f"API_ERROR: {result['error'].get('message', result)}")
    return result


def create_media_container(ig_id: str, token: str, media_type: str, media_url: str, caption: str = "") -> str:
    data = {"media_type": media_type, "image_url" if media_type == "IMAGE" else "video_url": media_url}
    if caption:
        data["caption"] = caption
    if media_type == "REEL":
        data["media_type"] = "REELS"
        data["video_url"] = media_url

    result = api_post(f"/{ig_id}/media", token, data)
    container_id = result.get("id", "")
    if not container_id:
        err_exit(f"UPLOAD_FAILED: no container id: {result}")
    return container_id


def poll_container_status(ig_id: str, token: str, container_id: str) -> str:
    for _ in range(POLL_MAX):
        params = {"access_token": token, "fields": "status_code"}
        resp = requests.get(f"{GRAPH_API}/{container_id}", params=params, timeout=30)
        data = resp.json()
        status = data.get("status_code", "")
        if status == "FINISHED":
            return "ready"
        elif status == "ERROR":
            err_exit(f"UPLOAD_FAILED: container error: {data}")
        time.sleep(POLL_INTERVAL)
    err_exit("MEDIA_PROCESSING: timed out waiting for container")


def publish_container(ig_id: str, token: str, creation_id: str) -> dict:
    result = api_post(f"/{ig_id}/media_publish", token, data={"creation_id": creation_id})
    post_id = result.get("id", "")
    return {"ok": True, "post_id": post_id, "url": f"https://www.instagram.com/p/{post_id}"}


def publish_carousel(ig_id: str, token: str, image_urls: list[str], caption: str) -> dict:
    children_ids = []
    for url in image_urls[:10]:
        cid = create_media_container(ig_id, token, "IMAGE", url)
        poll_container_status(ig_id, token, cid)
        children_ids.append(cid)

    data = {
        "media_type": "CAROUSEL",
        "children": ",".join(children_ids),
        "caption": caption,
    }
    result = api_post(f"/{ig_id}/media", token, data)
    carousel_id = result.get("id", "")
    poll_container_status(ig_id, token, carousel_id)
    return publish_container(ig_id, token, carousel_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish to Instagram")
    parser.add_argument("--caption", required=True, help="Caption (max 2200 chars, max 30 hashtags)")
    parser.add_argument("--mode", required=True, choices=["feed", "carousel", "reel"])
    parser.add_argument("--images", nargs="+", help="Image URLs")
    parser.add_argument("--video", help="Video URL (for reels)")
    args = parser.parse_args()

    config = load_config()
    token = config.get("page_access_token", "")
    ig_id = config.get("ig_user_id", "")
    if not token or not ig_id:
        err_exit("AUTH_REQUIRED: missing token or ig_user_id", 2)

    if args.mode == "feed":
        if not args.images or len(args.images) != 1:
            err_exit("--images requires exactly 1 URL for feed mode")
        cid = create_media_container(ig_id, token, "IMAGE", args.images[0], args.caption)
        sys.stderr.write("[instagram-publish] waiting for media processing...\n")
        poll_container_status(ig_id, token, cid)
        result = publish_container(ig_id, token, cid)
    elif args.mode == "carousel":
        if not args.images or len(args.images) < 2:
            err_exit("--images requires 2-10 URLs for carousel mode")
        result = publish_carousel(ig_id, token, args.images, args.caption)
    elif args.mode == "reel":
        if not args.video:
            err_exit("--video URL required for reel mode")
        cid = create_media_container(ig_id, token, "REEL", args.video, args.caption)
        sys.stderr.write("[instagram-publish] waiting for video processing...\n")
        poll_container_status(ig_id, token, cid)
        result = publish_container(ig_id, token, cid)

    output(result)


if __name__ == "__main__":
    main()
