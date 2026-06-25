#!/usr/bin/env python3
"""Publish content to Douyin via H5 Schema (open platform).

Generates a schema URL that opens the Douyin app's publish page.
The user must open this URL on a device with the Douyin app installed
to confirm and complete the publishing.

Flow:
  client_key + client_secret → client_token → ticket + share_id → schema URL
"""

import argparse
import hashlib
import json
import random
import string
import sys
import time
from pathlib import Path
from urllib.parse import quote, urlencode

import requests

CREDS_DIR = Path.home() / ".openclaw" / "credentials"
CONFIG_FILE = CREDS_DIR / "douyin_config.json"
DOUYIN_API = "https://open.douyin.com"


def output(data: dict) -> None:
    sys.stdout.write(json.dumps(data, ensure_ascii=False) + "\n")


def err_exit(msg: str, code: int = 1) -> None:
    sys.stderr.write(f"[douyin-publish] ERROR: {msg}\n")
    output({"ok": False, "error": msg})
    sys.exit(code)


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        err_exit(
            "CONFIG_MISSING: no douyin_config.json. "
            "Create ~/.openclaw/credentials/douyin_config.json with client_key and client_secret.",
            2,
        )
    cfg = json.loads(CONFIG_FILE.read_text())
    if not cfg.get("client_key") or not cfg.get("client_secret"):
        err_exit("CONFIG_INVALID: douyin_config.json must contain client_key and client_secret", 2)
    return cfg


def generate_nonce_str(length: int = 32) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def get_client_token(config: dict) -> str:
    """Get client_token via client_credential grant (no user auth needed).

    client_token is valid for 2 hours. Repeated calls invalidate the previous
    one (with a 5-minute buffer). Rate limit: 500 calls per 5 minutes.
    """
    resp = requests.post(
        f"{DOUYIN_API}/oauth/client_token/",
        json={
            "client_key": config["client_key"],
            "client_secret": config["client_secret"],
            "grant_type": "client_credential",
        },
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    if resp.status_code != 200:
        err_exit(f"CLIENT_TOKEN_FAILED: HTTP {resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    if data.get("message") != "success":
        desc = data.get("data", {}).get("description", str(data))
        err_exit(f"CLIENT_TOKEN_FAILED: {desc}")

    token = data.get("data", {}).get("access_token", "")
    if not token:
        err_exit("CLIENT_TOKEN_FAILED: no access_token in response")
    return token


def get_open_ticket(client_token: str) -> str:
    """Get open ticket for schema signature generation."""
    resp = requests.get(
        f"{DOUYIN_API}/open/getticket/",
        headers={
            "Content-Type": "application/json",
            "access-token": client_token,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        err_exit(f"TICKET_FAILED: HTTP {resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    ticket = data.get("data", {}).get("ticket", "")
    if not ticket:
        err_exit("TICKET_FAILED: no ticket in response")
    return ticket


def get_share_id(client_token: str) -> str:
    """Get share_id for tracking publish result via webhook/query."""
    resp = requests.get(
        f"{DOUYIN_API}/share-id/",
        params={"need_callback": "true"},
        headers={
            "Content-Type": "application/json",
            "access-token": client_token,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        err_exit(f"SHARE_ID_FAILED: HTTP {resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    error_code = data.get("extra", {}).get("error_code", -1)
    if error_code != 0:
        desc = data.get("extra", {}).get("description", str(data))
        err_exit(f"SHARE_ID_FAILED: {desc}")

    share_id = data.get("data", {}).get("share_id", "")
    if not share_id:
        err_exit("SHARE_ID_FAILED: no share_id in response")
    return share_id


def generate_signature(ticket: str, nonce_str: str, timestamp: str) -> str:
    """Generate MD5 signature for H5 schema.

    Sign string: nonce_str={nonce_str}&ticket={ticket}&timestamp={timestamp}
    Result: MD5 hex digest of the sign string.
    """
    sign_str = f"nonce_str={nonce_str}&ticket={ticket}&timestamp={timestamp}"
    return hashlib.md5(sign_str.encode()).hexdigest()


def build_schema_url(
    client_key: str,
    ticket: str,
    share_id: str,
    title: str,
    video_path: str | None,
    image_path: str | None,
    image_list_path: list[str] | None,
    hashtag_list: list[str] | None,
    title_hashtag_list: list[dict] | None,
    short_title: str | None,
    private_status: int | None,
    download_type: int | None,
    share_to_type: int | None,
    poi_id: str | None,
    feature: str | None,
) -> str:
    """Build the H5 share schema URL.

    Schema format: snssdk1128://openplatform/share?share_type=h5&client_key=xx&...
    All parameters should be URL-encoded. Spaces encoded as %20 (not +).
    """
    nonce_str = generate_nonce_str(32)
    timestamp = str(int(time.time()))
    signature = generate_signature(ticket, nonce_str, timestamp)

    params = {
        "client_key": client_key,
        "nonce_str": nonce_str,
        "timestamp": timestamp,
        "signature": signature,
        "share_type": "h5",
    }

    if share_id:
        params["state"] = share_id

    # Media content
    if video_path:
        params["video_path"] = video_path
        params["share_to_publish"] = "1"
    if image_path:
        params["image_path"] = image_path
    if image_list_path:
        params["image_list_path"] = json.dumps(image_list_path, ensure_ascii=False)

    # Title
    if title:
        params["title"] = title
    if short_title:
        params["short_title"] = short_title

    # Hashtags
    if hashtag_list:
        params["hashtag_list"] = json.dumps(hashtag_list, ensure_ascii=False)
    if title_hashtag_list:
        params["title_hashtag_list"] = json.dumps(title_hashtag_list, ensure_ascii=False)

    # Privacy & download
    if private_status is not None:
        params["private_status"] = str(private_status)
    if download_type is not None:
        params["download_type"] = str(download_type)
    if share_to_type is not None:
        params["share_to_type"] = str(share_to_type)

    # Location
    if poi_id:
        params["poi_id"] = poi_id

    # Note mode
    if feature:
        params["feature"] = feature

    # Use quote_via=quote so spaces become %20 instead of +
    return "snssdk1128://openplatform/share?" + urlencode(params, quote_via=quote)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Publish content to Douyin via H5 Schema (open platform)"
    )
    parser.add_argument("--title", required=True, help="Content title")
    parser.add_argument(
        "--video",
        help="Video URL (publicly accessible, mp4/mov, max 128M)",
    )
    parser.add_argument(
        "--image",
        help="Single image URL (png/jpg/gif, max 20M)",
    )
    parser.add_argument(
        "--images",
        help="Comma-separated image URLs for album mode (png/jpg, Douyin 22.2.0+)",
    )
    parser.add_argument("--tags", default="", help="Comma-separated hashtags")
    parser.add_argument(
        "--short-title", dest="short_title",
        help="Short title (Douyin 30.0.0+)",
    )
    parser.add_argument(
        "--private-status", dest="private_status", type=int, choices=[0, 1, 2],
        help="Visibility: 0=public, 1=self-only, 2=friends-only (Douyin 30.0.0+)",
    )
    parser.add_argument(
        "--download-type", dest="download_type", type=int, choices=[1, 2],
        help="Download: 1=allow, 2=disallow (Douyin 30.0.0+)",
    )
    parser.add_argument(
        "--share-to-type", dest="share_to_type", type=int, choices=[0, 1],
        help="Publish type: 0=post, 1=forward to daily (Douyin 25.4.0+)",
    )
    parser.add_argument(
        "--poi-id", dest="poi_id",
        help="Location POI ID (Douyin 22.2.0+)",
    )
    parser.add_argument(
        "--feature", choices=["note"],
        help="Set to 'note' for note mode with multi-image (Douyin 30.3.0+)",
    )
    args = parser.parse_args()

    # Validate: at least one media required
    if not args.video and not args.image and not args.images:
        err_exit("MISSING_MEDIA: at least one of --video, --image, --images is required")

    config = load_config()

    # Step 1: Get client_token (no user auth needed)
    sys.stderr.write("[douyin-publish] step 1/4: getting client_token...\n")
    client_token = get_client_token(config)

    # Step 2: Get open ticket for signature
    sys.stderr.write("[douyin-publish] step 2/4: getting open ticket...\n")
    ticket = get_open_ticket(client_token)

    # Step 3: Get share_id for result tracking
    sys.stderr.write("[douyin-publish] step 3/4: getting share_id...\n")
    share_id = get_share_id(client_token)

    # Build hashtag lists
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    hashtag_list = tags if tags else None
    title_hashtag_list = None
    if tags:
        # Place hashtags at end of title (AiToEarn convention)
        title_hashtag_list = [{"name": tag, "start": len(args.title)} for tag in tags]

    # Build image list
    image_list_path = None
    if args.images:
        image_list_path = [url.strip() for url in args.images.split(",") if url.strip()]

    # Step 4: Generate schema URL
    sys.stderr.write("[douyin-publish] step 4/4: generating share schema...\n")
    schema_url = build_schema_url(
        client_key=config["client_key"],
        ticket=ticket,
        share_id=share_id,
        title=args.title,
        video_path=args.video,
        image_path=args.image,
        image_list_path=image_list_path,
        hashtag_list=hashtag_list,
        title_hashtag_list=title_hashtag_list,
        short_title=args.short_title,
        private_status=args.private_status,
        download_type=args.download_type,
        share_to_type=args.share_to_type,
        poi_id=args.poi_id,
        feature=args.feature,
    )

    sys.stderr.write(f"[douyin-publish] schema generated (share_id={share_id})\n")
    output({
        "ok": True,
        "schema_url": schema_url,
        "share_id": share_id,
        "hint": "Open schema_url on a device with Douyin app to complete publishing. Use share_id to query result later.",
    })


if __name__ == "__main__":
    main()
