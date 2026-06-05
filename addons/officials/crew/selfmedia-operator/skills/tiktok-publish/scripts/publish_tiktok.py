#!/usr/bin/env python3
"""Upload videos to TikTok via Content Posting API with OAuth2."""

import argparse
import json
import os
import sys
from pathlib import Path

import requests

CREDS_DIR = Path.home() / ".openclaw" / "credentials"
CONFIG_FILE = CREDS_DIR / "tiktok_config.json"
TOKEN_FILE = CREDS_DIR / "tiktok_token.json"
TIKTOK_API = "https://open.tiktokapis.com/v2"
TIKTOK_AUTH = "https://www.tiktok.com/v2/auth/authorize"
TIKTOK_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"


def output(data: dict) -> None:
    sys.stdout.write(json.dumps(data, ensure_ascii=False) + "\n")


def err_exit(msg: str, code: int = 1) -> None:
    sys.stderr.write(f"[tiktok-publish] ERROR: {msg}\n")
    output({"ok": False, "error": msg})
    sys.exit(code)


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        err_exit("AUTH_REQUIRED: no tiktok_config.json", 2)
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
        TIKTOK_TOKEN_URL,
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

    new_token = resp.json()
    CREDS_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(new_token, indent=2))
    return new_token.get("access_token", "")


def init_publish(access_token: str) -> dict:
    url = f"{TIKTOK_API}/post/publish/video/init/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "post_info": {
            "title": "",
            "privacy_level": "PUBLIC_TO_EVERYONE",
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
        },
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code in (401, 403):
        err_exit("AUTH_REQUIRED", 2)

    data = resp.json()
    if data.get("error", {}).get("code") != "ok":
        err_exit(f"UPLOAD_FAILED: init: {data}")

    return data.get("data", {})


def upload_video_chunked(upload_url: str, video_path: str, access_token: str) -> None:
    file_size = os.path.getsize(video_path)
    chunk_size = 5 * 1024 * 1024

    with open(video_path, "rb") as f:
        offset = 0
        while offset < file_size:
            chunk = f.read(min(chunk_size, file_size - offset))
            end = offset + len(chunk) - 1
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "video/mp4",
                "Content-Range": f"bytes {offset}-{end}/{file_size}",
                "Content-Length": str(len(chunk)),
            }
            resp = requests.put(upload_url, headers=headers, data=chunk, timeout=120)
            if resp.status_code not in (200, 201, 308):
                err_exit(f"UPLOAD_FAILED: chunk at {offset} HTTP {resp.status_code}")
            offset = end + 1
            sys.stderr.write(f"[tiktok-publish] uploaded {offset}/{file_size} bytes\n")


def check_publish_status(access_token: str, publish_id: str) -> dict:
    url = f"{TIKTOK_API}/post/publish/status/fetch/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {"publish_id": publish_id}
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    data = resp.json()
    if data.get("error", {}).get("code") != "ok":
        err_exit(f"PUBLISH_FAILED: status check: {data}")
    return data.get("data", {})


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload video to TikTok")
    parser.add_argument("--title", required=True, help="Video title (max 150 chars)")
    parser.add_argument("--video", required=True, help="Video file path")
    parser.add_argument("--description", default="", help="Video description")
    parser.add_argument("--privacy", default="public",
                        choices=["public", "mutual_follow", "follower", "private"])
    parser.add_argument("--disable-comment", action="store_true")
    parser.add_argument("--disable-duet", action="store_true")
    parser.add_argument("--disable-stitch", action="store_true")
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

    sys.stderr.write("[tiktok-publish] initializing publish...\n")
    init_data = init_publish(access_token)
    publish_id = init_data.get("publish_id", "")
    upload_url = init_data.get("upload_url", "")

    if not publish_id or not upload_url:
        err_exit(f"UPLOAD_FAILED: invalid init response: {init_data}")

    sys.stderr.write(f"[tiktok-publish] uploading video (publish_id={publish_id})...\n")
    upload_video_chunked(upload_url, args.video, access_token)

    output({"ok": True, "publish_id": publish_id, "status": "UPLOAD_COMPLETE"})


if __name__ == "__main__":
    main()
