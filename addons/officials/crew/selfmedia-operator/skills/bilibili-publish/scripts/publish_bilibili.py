#!/usr/bin/env python3
"""Publish videos to Bilibili via Open Platform API (OAuth2 + HMAC-SHA256).

Based on AiToEarn's bilibili-api.service.ts, adapted for wiseflow skill architecture.

Authentication: OAuth2 with app_key/app_secret (Bilibili Open Platform).
  - BILIBILI_APP_ID and BILIBILI_APP_SECRET must be set in environment.
  - Access token stored in ~/.openclaw/logins/bilibili-oauth.json

Usage:
  python3 publish_bilibili.py --title "标题" --video video.mp4 --tags AI,科技
"""

import argparse
import hashlib
import hmac
import json
import os
import sys
import time
import uuid
from pathlib import Path

import requests

LOGINS_DIR = Path.home() / ".openclaw" / "logins"
OAUTH_FILE = LOGINS_DIR / "bilibili-oauth.json"
CHUNK_SIZE = 5 * 1024 * 1024  # 5MB chunks

# Open Platform API endpoints
AUTH_BASE = "https://api.bilibili.com/x/account-oauth2/v1"
MEMBER_BASE = "https://member.bilibili.com/arcopen/fn"
UPLOAD_BASE = "https://openupos.bilivideo.com/video/v2"


def output(data: dict) -> None:
    sys.stdout.write(json.dumps(data, ensure_ascii=False) + "\n")


def err_exit(msg: str, code: int = 1) -> None:
    sys.stderr.write(f"[bilibili-publish] ERROR: {msg}\n")
    output({"ok": False, "error": msg})
    sys.exit(code)


# ── OAuth2 ────────────────────────────────────────────────────────────────

def get_app_credentials() -> tuple[str, str]:
    app_id = os.environ.get("BILIBILI_APP_ID", "")
    app_secret = os.environ.get("BILIBILI_APP_SECRET", "")
    if not app_id or not app_secret:
        err_exit(
            "CREDENTIALS_MISSING: BILIBILI_APP_ID and BILIBILI_APP_SECRET "
            "environment variables are required. Apply at https://open.bilibili.com/",
            2,
        )
    return app_id, app_secret


def load_token() -> dict | None:
    if not OAUTH_FILE.exists():
        return None
    try:
        return json.loads(OAUTH_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def save_token(data: dict) -> None:
    LOGINS_DIR.mkdir(parents=True, exist_ok=True)
    OAUTH_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def get_access_token() -> str:
    """Get a valid access token, refreshing if needed."""
    app_id, app_secret = get_app_credentials()
    token_data = load_token()

    if not token_data:
        err_exit(
            "AUTH_REQUIRED: No OAuth token found. Complete OAuth2 flow first:\n"
            "1. Open auth page: login-manager or browser to get authorization code\n"
            "2. Run: python3 publish_bilibili.py --exchange-token <code>",
            2,
        )

    access_token = token_data.get("access_token", "")
    expires_at = token_data.get("expires_at", 0)
    refresh_token = token_data.get("refresh_token", "")

    # Token still valid (with 10min buffer)
    if access_token and expires_at > time.time() + 600:
        return access_token

    # Try refresh
    if refresh_token:
        sys.stderr.write("[bilibili-publish] refreshing access token...\n")
        resp = requests.post(
            f"{AUTH_BASE}/refresh_token",
            params={
                "client_id": app_id,
                "client_secret": app_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            timeout=30,
        )
        data = resp.json()
        if data.get("code") == 0 and data.get("data"):
            token_info = data["data"]
            save_token({
                "access_token": token_info["access_token"],
                "refresh_token": token_info["refresh_token"],
                "expires_at": int(time.time()) + token_info.get("expires_in", 2592000),
                "mid": token_info.get("mid", ""),
            })
            return token_info["access_token"]
        sys.stderr.write(f"[bilibili-publish] token refresh failed: {data}\n")

    err_exit(
        "AUTH_EXPIRED: Token expired and refresh failed. Re-authorization required.",
        2,
    )


def exchange_token(code: str) -> None:
    """Exchange authorization code for access token."""
    app_id, app_secret = get_app_credentials()
    resp = requests.post(
        f"{AUTH_BASE}/token",
        params={
            "client_id": app_id,
            "client_secret": app_secret,
            "grant_type": "authorization_code",
            "code": code,
        },
        timeout=30,
    )
    data = resp.json()
    if data.get("code") != 0:
        err_exit(f"TOKEN_EXCHANGE_FAILED: {data}")

    token_info = data["data"]
    save_token({
        "access_token": token_info["access_token"],
        "refresh_token": token_info["refresh_token"],
        "expires_at": int(time.time()) + token_info.get("expires_in", 2592000),
        "mid": token_info.get("mid", ""),
    })
    output({"ok": True, "mid": token_info.get("mid", ""), "path": str(OAUTH_FILE)})


# ── HMAC-SHA256 Request Signing ──────────────────────────────────────────

def generate_headers(
    app_id: str, app_secret: str,
    access_token: str, body: dict | None = None,
    is_form: bool = False,
) -> dict:
    """Generate signed request headers per Bilibili Open Platform spec."""
    md5_str = json.dumps(body) if body else ""
    x_bili_content_md5 = hashlib.md5(md5_str.encode()).hexdigest()

    headers = {
        "Accept": "application/json",
        "Content-Type": "multipart/form-data" if is_form else "application/json",
        "x-bili-content-md5": x_bili_content_md5,
        "x-bili-timestamp": str(int(time.time())),
        "x-bili-signature-method": "HMAC-SHA256",
        "x-bili-signature-nonce": str(uuid.uuid4()),
        "x-bili-accesskeyid": app_id,
        "x-bili-signature-version": "2.0",
        "access-token": access_token,
        "Authorization": "",
    }

    # Sort x-bili-* headers, join with \n, HMAC-SHA256 sign
    header_str = "\n".join(
        f"{k}:{headers[k]}"
        for k in sorted(k for k in headers if k.startswith("x-bili-"))
    )
    signature = hmac.new(
        app_secret.encode(), header_str.encode(), hashlib.sha256,
    ).hexdigest()
    headers["Authorization"] = signature

    return headers


# ── API Operations ───────────────────────────────────────────────────────

def video_init(access_token: str, filename: str) -> str:
    """Initialize video upload, return upload_token."""
    app_id, app_secret = get_app_credentials()
    body = {"name": filename, "utype": "0"}
    headers = generate_headers(app_id, app_secret, access_token, body=body)
    resp = requests.post(
        f"{MEMBER_BASE}/archive/video/init",
        headers=headers, json=body, timeout=30,
    )
    data = resp.json()
    if data.get("code") != 0:
        err_exit(f"UPLOAD_FAILED: video init: {data.get('message', data)}")
    return data["data"]["upload_token"]


def upload_chunks(access_token: str, video_path: str, upload_token: str) -> list[dict]:
    """Upload video in chunks, return list of {part_number, etag}."""
    app_id, app_secret = get_app_credentials()
    headers = generate_headers(app_id, app_secret, access_token)
    # Remove Content-Type for binary upload
    upload_headers = {k: v for k, v in headers.items() if k != "Content-Type"}

    parts = []
    with open(video_path, "rb") as f:
        part_num = 0
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            part_num += 1
            resp = requests.post(
                f"{UPLOAD_BASE}/part/upload",
                headers=upload_headers,
                params={"upload_token": upload_token, "part_number": part_num},
                data=chunk,
                timeout=120,
            )
            data = resp.json()
            if data.get("code") != 0:
                err_exit(f"UPLOAD_FAILED: chunk {part_num}: {data.get('message', data)}")
            etag = data["data"]["etag"]
            parts.append({"part_number": part_num, "etag": etag})
            sys.stderr.write(f"[bilibili-publish] uploaded chunk {part_num}\n")
    return parts


def video_complete(access_token: str, upload_token: str) -> None:
    """Complete chunked upload (server-side merge)."""
    app_id, app_secret = get_app_credentials()
    headers = generate_headers(app_id, app_secret, access_token)
    resp = requests.post(
        f"{MEMBER_BASE}/archive/video/complete",
        headers=headers,
        params={"upload_token": upload_token},
        timeout=30,
    )
    data = resp.json()
    if data.get("code") != 0:
        err_exit(f"UPLOAD_FAILED: video complete: {data.get('message', data)}")


def cover_upload(access_token: str, cover_path: str) -> str:
    """Upload cover image, return cover URL."""
    app_id, app_secret = get_app_credentials()
    headers = generate_headers(app_id, app_secret, access_token, is_form=True)
    with open(cover_path, "rb") as f:
        files = {"file": (os.path.basename(cover_path), f, "image/jpeg")}
        resp = requests.post(
            f"{MEMBER_BASE}/archive/cover/upload",
            headers=headers, files=files, timeout=30,
        )
    data = resp.json()
    if data.get("code") != 0:
        err_exit(f"UPLOAD_FAILED: cover: {data.get('message', data)}")
    return data["data"]["url"]


def archive_add(
    access_token: str, upload_token: str,
    title: str, desc: str, cover_url: str,
    tid: int, tags: str, copyright_type: int,
) -> dict:
    """Submit video archive."""
    app_id, app_secret = get_app_credentials()
    body = {
        "title": title,
        "desc": desc or "",
        "cover": cover_url,
        "tid": tid,
        "tag": tags,
        "copyright": copyright_type,
    }
    headers = generate_headers(app_id, app_secret, access_token, body=body)
    resp = requests.post(
        f"{MEMBER_BASE}/archive/add-by-utoken",
        headers=headers,
        params={"upload_token": upload_token},
        json=body,
        timeout=30,
    )
    data = resp.json()
    if data.get("code") != 0:
        err_exit(f"SUBMIT_FAILED: {data.get('message', data)}")

    resource_id = data["data"].get("resource_id", "")
    # resource_id format: "avid:bvid" or just "avid"
    bvid = ""
    if ":" in str(resource_id):
        _, bvid = str(resource_id).split(":", 1)
    return {"ok": True, "resource_id": resource_id, "bvid": bvid, "url": f"https://www.bilibili.com/video/{bvid}" if bvid else ""}


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Publish video to Bilibili via Open Platform API")
    parser.add_argument("--title", required=True, help="Video title (max 80 chars)")
    parser.add_argument("--video", required=True, help="Video file path")
    parser.add_argument("--cover", help="Cover image path")
    parser.add_argument("--desc", default="", help="Video description")
    parser.add_argument("--tid", type=int, default=122, help="Partition ID (default: 122=野生技术协会)")
    parser.add_argument("--tags", required=True, help="Comma-separated tags")
    parser.add_argument("--copyright", type=int, default=1, choices=[1, 2], help="1=self-made, 2=repost")
    parser.add_argument("--exchange-token", help="Exchange OAuth authorization code for access token")
    args = parser.parse_args()

    # OAuth code exchange mode
    if args.exchange_token:
        exchange_token(args.exchange_token)
        return

    # Validate video file
    video_path = os.path.abspath(args.video)
    if not os.path.isfile(video_path):
        err_exit(f"UPLOAD_FAILED: video not found: {video_path}")

    if len(args.title) > 80:
        err_exit("TITLE_TOO_LONG: title exceeds 80 characters")

    # Get access token (auto-refresh if needed)
    access_token = get_access_token()

    # Step 1: Initialize upload
    filename = os.path.basename(video_path)
    sys.stderr.write("[bilibili-publish] initializing upload...\n")
    upload_token = video_init(access_token, filename)

    # Step 2: Upload chunks
    sys.stderr.write("[bilibili-publish] uploading chunks...\n")
    upload_chunks(access_token, video_path, upload_token)

    # Step 3: Complete upload
    sys.stderr.write("[bilibili-publish] completing upload...\n")
    video_complete(access_token, upload_token)

    # Step 4: Upload cover (optional)
    cover_url = ""
    if args.cover and os.path.isfile(args.cover):
        sys.stderr.write("[bilibili-publish] uploading cover...\n")
        cover_url = cover_upload(access_token, args.cover)

    # Step 5: Submit archive
    sys.stderr.write("[bilibili-publish] submitting archive...\n")
    result = archive_add(
        access_token, upload_token,
        args.title, args.desc, cover_url,
        args.tid, args.tags, args.copyright,
    )

    output(result)


if __name__ == "__main__":
    main()
