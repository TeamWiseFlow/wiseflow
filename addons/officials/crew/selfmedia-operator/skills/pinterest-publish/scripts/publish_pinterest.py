#!/usr/bin/env python3
"""Create pins on Pinterest via Pinterest API v5 with OAuth2."""

import argparse
import json
import sys
from pathlib import Path

import requests

CREDS_DIR = Path.home() / ".openclaw" / "credentials"
CONFIG_FILE = CREDS_DIR / "pinterest_config.json"
PINTEREST_API = "https://api.pinterest.com/v5"


def output(data: dict) -> None:
    sys.stdout.write(json.dumps(data, ensure_ascii=False) + "\n")


def err_exit(msg: str, code: int = 1) -> None:
    sys.stderr.write(f"[pinterest-publish] ERROR: {msg}\n")
    output({"ok": False, "error": msg})
    sys.exit(code)


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        err_exit("AUTH_REQUIRED: no pinterest_config.json", 2)
    return json.loads(CONFIG_FILE.read_text())


def api_post(token: str, path: str, data: dict) -> dict:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(f"{PINTEREST_API}{path}", headers=headers, json=data, timeout=30)
    if resp.status_code in (401, 403):
        err_exit("AUTH_REQUIRED", 2)
    result = resp.json()
    if "error" in result and isinstance(result["error"], dict):
        err_exit(f"API_ERROR: {result['error'].get('message', result)}")
    return result


def create_image_pin(token: str, board_id: str, title: str, description: str, image_url: str, link: str = "") -> dict:
    data = {
        "board_id": board_id,
        "title": title,
        "description": description,
        "media_source": {
            "source_type": "image_url",
            "url": image_url,
        },
    }
    if link:
        data["link"] = link

    result = api_post(token, "/pins", data)
    pin_id = result.get("id", "")
    return {"ok": True, "pin_id": pin_id, "url": f"https://www.pinterest.com/pin/{pin_id}/"}


def create_video_pin(token: str, board_id: str, title: str, description: str, video_url: str, link: str = "") -> dict:
    register = api_post(token, "/media", data={"media_type": "video"})
    media_id = register.get("media_id", "")
    if not media_id:
        err_exit(f"UPLOAD_FAILED: no media_id: {register}")

    data = {
        "board_id": board_id,
        "title": title,
        "description": description,
        "media_source": {
            "source_type": "video_id",
            "video_id": media_id,
            "cover_image_url": video_url,
        },
    }
    if link:
        data["link"] = link

    result = api_post(token, "/pins", data)
    pin_id = result.get("id", "")
    return {"ok": True, "pin_id": pin_id, "url": f"https://www.pinterest.com/pin/{pin_id}/"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Create pin on Pinterest")
    parser.add_argument("--title", required=True, help="Pin title")
    parser.add_argument("--description", default="", help="Pin description")
    parser.add_argument("--image", help="Image URL")
    parser.add_argument("--video", help="Video URL")
    parser.add_argument("--board-id", required=True, help="Board ID")
    parser.add_argument("--link", default="", help="Destination link URL")
    args = parser.parse_args()

    config = load_config()
    token = config.get("access_token", "")
    if not token:
        err_exit("AUTH_REQUIRED: missing access_token", 2)

    board_id = args.board_id or config.get("board_id", "")
    if not board_id:
        err_exit("INVALID_BOARD: no board_id provided", 2)

    if args.image:
        result = create_image_pin(token, board_id, args.title, args.description, args.image, args.link)
    elif args.video:
        result = create_video_pin(token, board_id, args.title, args.description, args.video, args.link)
    else:
        err_exit("Either --image or --video URL is required")

    output(result)


if __name__ == "__main__":
    main()
