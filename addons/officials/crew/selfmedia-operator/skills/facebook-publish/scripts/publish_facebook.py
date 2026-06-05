#!/usr/bin/env python3
"""Publish posts, videos, and reels to Facebook via Meta Graph API v23.0."""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

CREDS_DIR = Path.home() / ".openclaw" / "credentials"
CONFIG_FILE = CREDS_DIR / "facebook_config.json"
GRAPH_API = "https://graph.facebook.com/v23.0"


def output(data: dict) -> None:
    sys.stdout.write(json.dumps(data, ensure_ascii=False) + "\n")


def err_exit(msg: str, code: int = 1) -> None:
    sys.stderr.write(f"[facebook-publish] ERROR: {msg}\n")
    output({"ok": False, "error": msg})
    sys.exit(code)


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        err_exit("AUTH_REQUIRED: no facebook_config.json", 2)
    return json.loads(CONFIG_FILE.read_text())


def api_get(path: str, token: str, params: dict | None = None) -> dict:
    p = {"access_token": token, **(params or {})}
    resp = requests.get(f"{GRAPH_API}{path}", params=p, timeout=30)
    if resp.status_code in (401, 403):
        err_exit("AUTH_REQUIRED", 2)
    data = resp.json()
    if "error" in data:
        err_exit(f"API_ERROR: {data['error'].get('message', data)}")
    return data


def api_post(path: str, token: str, data: dict | None = None, files: dict | None = None) -> dict:
    params = {"access_token": token}
    if data and not files:
        resp = requests.post(f"{GRAPH_API}{path}", params=params, json=data, timeout=120)
    elif files:
        resp = requests.post(f"{GRAPH_API}{path}", params=params, files=files, data=data, timeout=300)
    else:
        resp = requests.post(f"{GRAPH_API}{path}", params=params, timeout=30)
    if resp.status_code in (401, 403):
        err_exit("AUTH_REQUIRED", 2)
    result = resp.json()
    if "error" in result:
        err_exit(f"API_ERROR: {result['error'].get('message', result)}")
    return result


def publish_feed_post(page_id: str, token: str, message: str, image_paths: list[str] | None = None) -> dict:
    if image_paths:
        path = f"/{page_id}/photos"
        if len(image_paths) == 1:
            with open(image_paths[0], "rb") as f:
                result = api_post(path, token, data={"message": message}, files={"source": f})
            post_id = result.get("post_id", result.get("id", ""))
        else:
            uploaded_ids = []
            for img_path in image_paths:
                with open(img_path, "rb") as f:
                    r = api_post(path, token, data={"published": "false"}, files={"source": f})
                uploaded_ids.append(r["id"])
            result = api_post(f"/{page_id}/feed", token, data={
                "message": message,
                "attached_media": json.dumps([{"media_fbid": mid} for mid in uploaded_ids]),
            })
            post_id = result.get("id", "")
    else:
        result = api_post(f"/{page_id}/feed", token, data={"message": message})
        post_id = result.get("id", "")

    return {"ok": True, "post_id": post_id, "url": f"https://facebook.com/{post_id}"}


def publish_video(page_id: str, token: str, video_path: str, title: str, description: str) -> dict:
    file_size = os.path.getsize(video_path)
    start = api_post(f"/{page_id}/videos", token, data={
        "upload_phase": "start",
        "file_size": file_size,
    })
    upload_session_id = start.get("upload_session_id", "")
    video_id = start.get("video_id", "")

    chunk_size = 4 * 1024 * 1024
    with open(video_path, "rb") as f:
        offset = 0
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            api_post(f"/{page_id}/videos", token, files={"video_file_chunk": chunk}, data={
                "upload_phase": "transfer",
                "upload_session_id": upload_session_id,
                "start_offset": str(offset),
            })
            offset += len(chunk)

    api_post(f"/{page_id}/videos", token, data={
        "upload_phase": "finish",
        "upload_session_id": upload_session_id,
        "title": title,
        "description": description,
    })

    return {"ok": True, "post_id": video_id, "url": f"https://facebook.com/{video_id}"}


def publish_reel(page_id: str, token: str, video_path: str, description: str) -> dict:
    init = api_post(f"/{page_id}/video_reels", token, data={"upload_phase": "start"})
    upload_url = init.get("upload_url", "")
    video_id = init.get("video_id", "")

    with open(video_path, "rb") as f:
        requests.put(upload_url, data=f, timeout=300)

    api_post(f"/{page_id}/video_reels", token, data={
        "upload_phase": "finish",
        "video_id": video_id,
        "title": description[:255] if description else "",
    })

    return {"ok": True, "post_id": video_id, "url": f"https://facebook.com/reel/{video_id}"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish to Facebook")
    parser.add_argument("--message", required=True, help="Post message/caption")
    parser.add_argument("--mode", required=True, choices=["feed", "video", "reel", "story"])
    parser.add_argument("--video", help="Video file path")
    parser.add_argument("--images", nargs="+", help="Image file paths")
    parser.add_argument("--title", default="", help="Video title")
    args = parser.parse_args()

    config = load_config()
    token = config.get("page_access_token", "")
    page_id = config.get("page_id", "")
    if not token or not page_id:
        err_exit("AUTH_REQUIRED: missing token or page_id", 2)

    if args.mode == "feed":
        result = publish_feed_post(page_id, token, args.message, args.images)
    elif args.mode == "video":
        if not args.video:
            err_exit("--video required for video mode")
        result = publish_video(page_id, token, args.video, args.title, args.message)
    elif args.mode == "reel":
        if not args.video:
            err_exit("--video required for reel mode")
        result = publish_reel(page_id, token, args.video, args.message)
    else:
        err_exit(f"story mode not yet implemented")

    output(result)


if __name__ == "__main__":
    main()
