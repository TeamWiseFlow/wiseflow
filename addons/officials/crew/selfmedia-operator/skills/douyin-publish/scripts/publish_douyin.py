#!/usr/bin/env python3
"""Publish videos to Douyin via open platform API with OAuth2."""

import argparse
import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path

import requests

CREDS_DIR = Path.home() / ".openclaw" / "credentials"
CONFIG_FILE = CREDS_DIR / "douyin_config.json"
TOKEN_FILE = CREDS_DIR / "douyin_token.json"
DOUYIN_API = "https://open.douyin.com"


def output(data: dict) -> None:
    sys.stdout.write(json.dumps(data, ensure_ascii=False) + "\n")


def err_exit(msg: str, code: int = 1) -> None:
    sys.stderr.write(f"[douyin-publish] ERROR: {msg}\n")
    output({"ok": False, "error": msg})
    sys.exit(code)


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        err_exit("AUTH_REQUIRED: no douyin_config.json", 2)
    return json.loads(CONFIG_FILE.read_text())


def load_token() -> dict:
    if not TOKEN_FILE.exists():
        err_exit("AUTH_REQUIRED", 2)
    return json.loads(TOKEN_FILE.read_text())


def refresh_access_token(config: dict, token_data: dict) -> str:
    refresh_token = token_data.get("refresh_token", "")
    if not refresh_token:
        err_exit("AUTH_REQUIRED: no refresh token", 2)

    resp = requests.post(
        f"{DOUYIN_API}/oauth/refresh_token/",
        data={
            "client_key": config["client_key"],
            "client_secret": config["client_secret"],
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    if resp.status_code != 200:
        err_exit(f"AUTH_REQUIRED: refresh failed: {resp.text}", 2)

    data = resp.json()
    token_info = data.get("data", {})
    if token_info.get("error_code") != 0:
        err_exit(f"AUTH_REQUIRED: {token_info.get('description', data)}", 2)

    new_token = {
        "access_token": token_info.get("access_token", ""),
        "refresh_token": token_info.get("refresh_token", refresh_token),
        "expires_in": token_info.get("expires_in", 0),
        "open_id": token_info.get("open_id", token_data.get("open_id", "")),
    }
    CREDS_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(new_token, indent=2))
    return new_token["access_token"]


def upload_video(access_token: str, open_id: str, video_path: str) -> str:
    url = f"{DOUYIN_API}/api/douyin/v1/video/upload_video/"
    file_size = os.path.getsize(video_path)
    filename = os.path.basename(video_path)

    with open(video_path, "rb") as f:
        resp = requests.post(
            url,
            headers={"access-token": access_token},
            params={"open_id": open_id},
            files={"video": (filename, f, "video/mp4")},
            timeout=300,
        )

    if resp.status_code in (401, 403):
        err_exit("AUTH_REQUIRED", 2)
    data = resp.json()
    if data.get("data", {}).get("error_code") != 0:
        err_exit(f"UPLOAD_FAILED: {data.get('data', {}).get('description', data)}")

    video_id = data.get("data", {}).get("video", {}).get("video_id", "")
    if not video_id:
        err_exit(f"UPLOAD_FAILED: no video_id: {data}")
    return video_id


def upload_cover(access_token: str, open_id: str, cover_path: str) -> str:
    url = f"{DOUYIN_API}/api/douyin/v1/video/upload_cover/"
    with open(cover_path, "rb") as f:
        resp = requests.post(
            url,
            headers={"access-token": access_token},
            params={"open_id": open_id},
            files={"image": ("cover.jpg", f, "image/jpeg")},
            timeout=60,
        )
    data = resp.json()
    return data.get("data", {}).get("image", {}).get("image_url", "")


def create_video(
    access_token: str, open_id: str,
    video_id: str, title: str, cover_url: str,
    tags: list[str], is_private: bool,
) -> dict:
    url = f"{DOUYIN_API}/api/douyin/v1/video/create_video/"
    text = title
    if tags:
        text += " " + " ".join(f"#{t}" for t in tags)

    payload = {
        "video_id": video_id,
        "text": text[:55],
    }
    if cover_url:
        payload["cover_url"] = cover_url
    if is_private:
        payload["private"] = True

    resp = requests.post(
        url,
        headers={
            "access-token": access_token,
            "Content-Type": "application/json",
        },
        params={"open_id": open_id},
        json=payload,
        timeout=30,
    )

    if resp.status_code in (401, 403):
        err_exit("AUTH_REQUIRED", 2)
    data = resp.json()
    if data.get("data", {}).get("error_code") != 0:
        msg = data.get("data", {}).get("description", str(data))
        if "login" in msg.lower() or "登录" in msg:
            err_exit("AUTH_REQUIRED", 2)
        err_exit(f"PUBLISH_FAILED: {msg}")

    item_id = data.get("data", {}).get("item_id", "")
    return {"ok": True, "item_id": item_id, "url": f"https://www.douyin.com/video/{item_id}"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish video to Douyin")
    parser.add_argument("--title", required=True, help="Video title (max 55 chars)")
    parser.add_argument("--video", required=True, help="Video file path")
    parser.add_argument("--cover", help="Cover image path")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--private", action="store_true", help="Set to private")
    args = parser.parse_args()

    if not os.path.exists(args.video):
        err_exit(f"UPLOAD_FAILED: video not found: {args.video}")

    config = load_config()
    token_data = load_token()

    try:
        access_token = refresh_access_token(config, token_data)
    except SystemExit:
        raise
    except Exception as e:
        err_exit(f"AUTH_REQUIRED: {e}", 2)

    open_id = token_data.get("open_id", "")
    if not open_id:
        err_exit("AUTH_REQUIRED: no open_id in token", 2)

    sys.stderr.write("[douyin-publish] uploading video...\n")
    video_id = upload_video(access_token, open_id, args.video)

    cover_url = ""
    if args.cover and os.path.exists(args.cover):
        sys.stderr.write("[douyin-publish] uploading cover...\n")
        cover_url = upload_cover(access_token, open_id, args.cover)

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []

    sys.stderr.write("[douyin-publish] creating video post...\n")
    result = create_video(
        access_token, open_id, video_id, args.title, cover_url,
        tags, args.private,
    )
    output(result)


if __name__ == "__main__":
    main()
