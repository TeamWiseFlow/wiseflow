#!/usr/bin/env python3
"""Publish posts to Threads via Meta Graph API (content container pattern)."""

import argparse
import json
import sys
import time
from pathlib import Path

import requests

CREDS_DIR = Path.home() / ".openclaw" / "credentials"
CONFIG_FILE = CREDS_DIR / "threads_config.json"
GRAPH_API = "https://graph.facebook.com/v23.0"
POLL_INTERVAL = 5
POLL_MAX = 60


def output(data: dict) -> None:
    sys.stdout.write(json.dumps(data, ensure_ascii=False) + "\n")


def err_exit(msg: str, code: int = 1) -> None:
    sys.stderr.write(f"[threads-publish] ERROR: {msg}\n")
    output({"ok": False, "error": msg})
    sys.exit(code)


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        err_exit("AUTH_REQUIRED: no threads_config.json", 2)
    return json.loads(CONFIG_FILE.read_text())


def api_post(path: str, token: str, data: dict | None = None, files: dict | None = None) -> dict:
    params = {"access_token": token}
    if files:
        resp = requests.post(f"{GRAPH_API}{path}", params=params, data=data, files=files, timeout=30)
    else:
        resp = requests.post(f"{GRAPH_API}{path}", params=params, json=data, timeout=30)
    if resp.status_code in (401, 403):
        err_exit("AUTH_REQUIRED", 2)
    result = resp.json()
    if "error" in result:
        err_exit(f"API_ERROR: {result['error'].get('message', result)}")
    return result


def create_item_container(user_id: str, token: str, text: str, media_url: str | None = None, media_type: str | None = None) -> str:
    data: dict = {"media_type": media_type or "TEXT"}
    if text:
        data["text"] = text
    if media_url and media_type == "IMAGE":
        data["image_url"] = media_url
    elif media_url and media_type in ("VIDEO", "REEL"):
        data["video_url"] = media_url

    result = api_post(f"/{user_id}/threads", token, data)
    container_id = result.get("id", "")
    if not container_id:
        err_exit(f"UPLOAD_FAILED: no container id: {result}")
    return container_id


def poll_status(token: str, container_id: str) -> str:
    for _ in range(POLL_MAX):
        params = {"access_token": token, "fields": "status_code"}
        resp = requests.get(f"https://graph.facebook.com/v23.0/{container_id}", params=params, timeout=30)
        data = resp.json()
        status = data.get("status_code", "")
        if status == "FINISHED":
            return "ready"
        elif status == "ERROR":
            err_exit(f"UPLOAD_FAILED: container error: {data}")
        time.sleep(POLL_INTERVAL)
    err_exit("MEDIA_PROCESSING: timed out")


def publish_post(user_id: str, token: str, creation_id: str) -> dict:
    result = api_post(f"/{user_id}/threads_publish", token, data={"creation_id": creation_id})
    post_id = result.get("id", "")
    return {"ok": True, "post_id": post_id, "url": f"https://www.threads.net/post/{post_id}"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish to Threads")
    parser.add_argument("--text", required=True, help="Post text")
    parser.add_argument("--images", help="Image URLs (comma-separated)")
    parser.add_argument("--video", help="Video URL")
    args = parser.parse_args()

    config = load_config()
    token = config.get("access_token", "")
    user_id = config.get("threads_user_id", "")
    if not token or not user_id:
        err_exit("AUTH_REQUIRED: missing token or user_id", 2)

    media_type = None
    media_url = None
    if args.video:
        media_type = "VIDEO"
        media_url = args.video
    elif args.images:
        urls = [u.strip() for u in args.images.split(",") if u.strip()]
        if len(urls) == 1:
            media_type = "IMAGE"
            media_url = urls[0]
        else:
            container_ids = []
            for url in urls:
                cid = create_item_container(user_id, token, "", url, "IMAGE")
                poll_status(token, cid)
                container_ids.append(cid)
            carousel_data = {
                "media_type": "CAROUSEL",
                "children": ",".join(container_ids),
            }
            if args.text:
                carousel_data["text"] = args.text
            result = api_post(f"/{user_id}/threads", token, carousel_data)
            carousel_id = result.get("id", "")
            poll_status(token, carousel_id)
            result = publish_post(user_id, token, carousel_id)
            output(result)
            return

    sys.stderr.write("[threads-publish] creating container...\n")
    container_id = create_item_container(user_id, token, args.text, media_url, media_type)

    if media_type:
        sys.stderr.write("[threads-publish] waiting for media processing...\n")
        poll_status(token, container_id)

    result = publish_post(user_id, token, container_id)
    output(result)


if __name__ == "__main__":
    main()
