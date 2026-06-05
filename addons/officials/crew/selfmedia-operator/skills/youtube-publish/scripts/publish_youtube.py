#!/usr/bin/env python3
"""Upload videos to YouTube via YouTube Data API v3 with OAuth2."""

import argparse
import json
import os
import sys
from pathlib import Path

import requests

CREDS_DIR = Path.home() / ".openclaw" / "credentials"
CLIENT_SECRET_FILE = CREDS_DIR / "youtube_client_secret.json"
TOKEN_FILE = CREDS_DIR / "youtube_token.json"
YOUTUBE_UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/videos"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def output(data: dict) -> None:
    sys.stdout.write(json.dumps(data, ensure_ascii=False) + "\n")


def err_exit(msg: str, code: int = 1) -> None:
    sys.stderr.write(f"[youtube-publish] ERROR: {msg}\n")
    output({"ok": False, "error": msg})
    sys.exit(code)


def load_token() -> dict:
    if not TOKEN_FILE.exists():
        err_exit("AUTH_REQUIRED", 2)
    try:
        return json.loads(TOKEN_FILE.read_text())
    except json.JSONDecodeError:
        err_exit("AUTH_REQUIRED", 2)


def refresh_access_token(token_data: dict) -> str:
    if not CLIENT_SECRET_FILE.exists():
        err_exit("AUTH_REQUIRED: no client_secret.json", 2)

    cs = json.loads(CLIENT_SECRET_FILE.read_text())
    installed = cs.get("installed", cs.get("web", {}))
    client_id = installed.get("client_id", "")
    client_secret = installed.get("client_secret", "")
    refresh_token = token_data.get("refresh_token", "")

    if not all([client_id, client_secret, refresh_token]):
        err_exit("AUTH_REQUIRED: incomplete credentials", 2)

    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    if resp.status_code != 200:
        err_exit(f"AUTH_REQUIRED: refresh failed: {resp.text}", 2)

    new_token = resp.json()
    new_token["refresh_token"] = refresh_token
    CREDS_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(new_token, indent=2))
    return new_token.get("access_token", "")


def init_resumable_upload(
    access_token: str, title: str, description: str,
    tags: list[str], visibility: str, category_id: str,
) -> str:
    metadata = {
        "snippet": {
            "title": title[:100],
            "description": description or "",
            "tags": tags if tags else [],
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": visibility,
            "selfDeclaredMadeForKids": False,
        },
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    params = {"uploadType": "resumable", "part": "snippet,status"}
    resp = requests.post(
        YOUTUBE_UPLOAD_URL, headers=headers, params=params,
        json=metadata, timeout=30,
    )
    if resp.status_code in (401, 403):
        err_exit("AUTH_REQUIRED", 2)
    if resp.status_code not in (200, 201):
        err_exit(f"UPLOAD_FAILED: init HTTP {resp.status_code}: {resp.text}")

    upload_url = resp.headers.get("Location", "")
    if not upload_url:
        err_exit("UPLOAD_FAILED: no upload URL in response")
    return upload_url


def upload_video(upload_url: str, video_path: str) -> dict:
    file_size = os.path.getsize(video_path)
    headers = {"Content-Length": str(file_size)}
    with open(video_path, "rb") as f:
        resp = requests.put(upload_url, headers=headers, data=f, timeout=600)

    if resp.status_code in (401, 403):
        err_exit("AUTH_REQUIRED", 2)
    if resp.status_code not in (200, 201):
        err_exit(f"UPLOAD_FAILED: upload HTTP {resp.status_code}: {resp.text}")

    data = resp.json()
    video_id = data.get("id", "")
    return {"ok": True, "video_id": video_id, "url": f"https://youtu.be/{video_id}"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload video to YouTube")
    parser.add_argument("--title", required=True, help="Video title (max 100 chars)")
    parser.add_argument("--video", required=True, help="Video file path")
    parser.add_argument("--description", default="", help="Video description")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--visibility", default="private", choices=["public", "unlisted", "private"])
    parser.add_argument("--category-id", default="28", help="YouTube category ID (default: 28=Sci/Tech)")
    parser.add_argument("--made-for-kids", action="store_true", help="Mark as made for kids")
    args = parser.parse_args()

    if len(args.title) > 100:
        err_exit("TITLE_TOO_LONG")

    if not os.path.exists(args.video):
        err_exit(f"UPLOAD_FAILED: video not found: {args.video}")

    token_data = load_token()
    access_token = token_data.get("access_token", "")
    if not access_token:
        err_exit("AUTH_REQUIRED", 2)

    try:
        sys.stderr.write("[youtube-publish] refreshing access token...\n")
        access_token = refresh_access_token(token_data)
    except SystemExit:
        raise
    except Exception as e:
        err_exit(f"AUTH_REQUIRED: {e}", 2)

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []

    sys.stderr.write("[youtube-publish] initializing resumable upload...\n")
    upload_url = init_resumable_upload(
        access_token, args.title, args.description,
        tags, args.visibility, args.category_id,
    )

    sys.stderr.write("[youtube-publish] uploading video...\n")
    result = upload_video(upload_url, args.video)
    output(result)


if __name__ == "__main__":
    main()
