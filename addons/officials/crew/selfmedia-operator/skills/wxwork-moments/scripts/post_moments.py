#!/usr/bin/env python3
"""post_moments.py — 企业微信朋友圈一键发布

用法：
  python3 post_moments.py "正文" [file1 file2 ...]
  python3 post_moments.py "正文" --link URL TITLE [cover_image]

环境变量（优先本地直连，次选 relay）：
  本地直连：WXWORK_CORP_ID  +  WXWORK_CORP_SECRET
  relay   ：WXWORK_PROXY_URL  +  WENYAN_API_KEY
"""

import argparse
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_API_BASE = "https://qyapi.weixin.qq.com"
IMAGE_MAX_DIM = 1248
RESIZE_TARGET = 1200


def die(msg: str) -> None:
    print(f"[error] {msg}", file=sys.stderr)
    sys.exit(1)


def log(msg: str) -> None:
    print(f">>> {msg}", flush=True)


def http_get_json(url: str, timeout: int = 30) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "wiseflow-wxwork/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def http_post_multipart(url: str, fields: dict, files: dict, headers: dict | None = None, timeout: int = 120) -> dict:
    """Post multipart/form-data. files: {field_name: (filename, filepath)}."""
    import uuid
    boundary = uuid.uuid4().hex
    parts = []

    for key, val in fields.items():
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{val}\r\n".encode())

    for field_name, (filename, filepath) in files.items():
        with open(filepath, "rb") as f:
            file_data = f.read()
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{field_name}\"; filename=\"{filename}\"\r\n\r\n".encode()
            + file_data + b"\r\n"
        )

    body = b"".join(parts) + f"--{boundary}--\r\n".encode()
    hdrs = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    if headers:
        hdrs.update(headers)

    req = urllib.request.Request(url, data=body, headers=hdrs, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def http_post_json(url: str, payload: dict, headers: dict | None = None, timeout: int = 30) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    hdrs = {"Content-Type": "application/json"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=data, headers=hdrs, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def get_access_token(corp_id: str, corp_secret: str) -> str:
    url = f"{DEFAULT_API_BASE}/cgi-bin/gettoken?corpid={corp_id}&corpsecret={corp_secret}"
    d = http_get_json(url)
    if d.get("errcode", 0) != 0:
        die(f"获取 token 失败: {d.get('errmsg', str(d))}")
    return d["access_token"]


def fetch_og_image(url: str) -> str | None:
    """Fetch a URL and extract og:image, return the image URL or None."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="ignore")
        m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
        if not m:
            m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', html, re.I)
        return m.group(1) if m else None
    except Exception:
        return None


def download_file(url: str, dest: str) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=10).read()
        Path(dest).write_bytes(data)
        return True
    except Exception:
        return False


def auto_resize_image(filepath: str) -> str:
    """Resize image if both dimensions >= IMAGE_MAX_DIM. Returns original or temp path."""
    try:
        from PIL import Image
    except ImportError:
        return filepath

    img = Image.open(filepath)
    w, h = img.size
    if w < IMAGE_MAX_DIM or h < IMAGE_MAX_DIM:
        return filepath

    ratio = RESIZE_TARGET / max(w, h)
    nw, nh = int(w * ratio), int(h * ratio)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - RESIZE_TARGET) // 2
    top = (nh - RESIZE_TARGET) // 2
    img = img.crop((left, top, left + RESIZE_TARGET, top + RESIZE_TARGET))

    tmp = tempfile.NamedTemporaryFile(prefix="_wx_auto_resize_", suffix=".jpg", delete=False)
    tmp.close()
    img.save(tmp.name, "JPEG", quality=92, optimize=True)
    return tmp.name


def upload_media(filepath: str, media_type: str, token: str | None, proxy_url: str | None, api_key: str | None) -> str:
    """Upload media file, return media_id."""
    ext = Path(filepath).suffix.lower()
    filename = Path(filepath).name
    file_field = "media"

    if token:
        url = f"{DEFAULT_API_BASE}/cgi-bin/media/upload?access_token={token}&type={media_type}"
        headers = None
    elif proxy_url and api_key:
        url = f"{proxy_url}/wxwork/media/upload"
        headers = {"x-api-key": api_key}
    else:
        die("无可用上传通道")

    try:
        result = http_post_multipart(url, {"type": media_type}, {file_field: (filename, filepath)}, headers=headers)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        die(f"上传失败 HTTP {e.code}: {body}")

    if "media_id" not in result:
        die(f"上传失败: {result}")
    return result["media_id"]


def main() -> None:
    parser = argparse.ArgumentParser(description="企业微信朋友圈发布")
    parser.add_argument("text", help="朋友圈正文")
    parser.add_argument("files", nargs="*", help="图片/视频文件路径")
    parser.add_argument("--link", nargs=3, metavar=("URL", "TITLE", "COVER"), help="图文链接模式：URL 标题 [封面图]")
    args = parser.parse_args()

    # Normalize text: WeChat API expects \n as literal two chars (backslash+n), not real newlines
    text = args.text.replace("\n", "\\n").replace("\r", "")

    media_files = list(args.files) if args.files else []
    link_mode = args.link is not None
    link_url = args.link[0] if args.link else ""
    link_title = args.link[1] if args.link else ""
    link_cover = args.link[2] if args.link and len(args.link) > 2 and args.link[2] else None

    if link_cover:
        media_files = [link_cover]

    # Validate file count
    has_video = any(Path(f).suffix.lower() in {".mp4", ".mov", ".avi", ".wmv"} for f in media_files)
    if not link_mode and has_video and len(media_files) > 1:
        die("视频只能上传 1 个")
    if not link_mode and not has_video and len(media_files) > 9:
        die(f"图片最多 9 张，当前 {len(media_files)} 张")

    # Mode detection
    corp_id = os.environ.get("WXWORK_CORP_ID", "").strip()
    corp_secret = os.environ.get("WXWORK_CORP_SECRET", "").strip()
    proxy_url = os.environ.get("WXWORK_PROXY_URL", "").strip()
    api_key = os.environ.get("WENYAN_API_KEY", "").strip()

    if corp_id and corp_secret:
        mode = "local"
    elif proxy_url and api_key:
        mode = "relay"
    else:
        die("请配置环境变量：\n  本地直连：WXWORK_CORP_ID + WXWORK_CORP_SECRET\n  relay  ：WXWORK_PROXY_URL + WENYAN_API_KEY")

    log(f"模式: {mode}")

    token = None
    if mode == "local":
        log("获取 access_token...")
        token = get_access_token(corp_id, corp_secret)

    # Link mode: auto-fetch og:image if no cover
    if link_mode and not media_files:
        log("未提供封面图，尝试从链接抓取 og:image...")
        og_url = fetch_og_image(link_url)
        if og_url:
            log(f"  og:image: {og_url}")
            og_tmp = tempfile.mktemp(suffix=".jpg")
            if download_file(og_url, og_tmp):
                media_files = [og_tmp]
                log("  封面图已下载")
            else:
                die("封面图下载失败。企业微信 link 类附件必须提供封面图")
        else:
            die("链接未包含 og:image，无法自动获取封面图。请手动指定：--link URL TITLE /path/to/cover.jpg")

    # Upload media
    media_ids: list[str] = []
    media_type = ""

    for filepath in media_files:
        if not Path(filepath).is_file():
            die(f"文件不存在: {filepath}")

        ext = Path(filepath).suffix.lower()
        if ext in {".jpg", ".jpeg", ".png", ".gif"}:
            ftype = "image"
        elif ext in {".mp4", ".mov", ".avi", ".wmv"}:
            ftype = "video"
        else:
            die(f"不支持的文件类型: {filepath}")

        media_type = ftype
        log(f"上传 {ftype}: {filepath}")

        # Auto-resize large images
        upload_path = filepath
        if ftype == "image":
            upload_path = auto_resize_image(filepath)
            if upload_path != filepath:
                log("  ⚠ 原始分辨率超标，已自动缩放到 1200x1200")

        mid = upload_media(upload_path, ftype, token, proxy_url if mode == "relay" else None, api_key if mode == "relay" else None)
        log(f"  media_id: {mid}")
        media_ids.append(mid)

    # Build payload
    payload: dict = {"text": {"content": text}}

    if link_mode:
        link_obj: dict = {"title": link_title, "url": link_url}
        if media_ids:
            link_obj["media_id"] = media_ids[0]
        payload["attachments"] = [{"msgtype": "link", "link": link_obj}]
    elif media_ids:
        if media_type == "video":
            payload["attachments"] = [{"msgtype": "video", "video": {"media_id": media_ids[0]}}]
        else:
            payload["attachments"] = [
                {"msgtype": "image", "image": {"media_id": mid}} for mid in media_ids
            ]

    # Publish
    log("发布朋友圈...")
    try:
        if mode == "relay":
            result = http_post_json(
                f"{proxy_url}/wxwork/moments/add",
                payload,
                headers={"x-api-key": api_key},
            )
        else:
            result = http_post_json(
                f"{DEFAULT_API_BASE}/cgi-bin/externalcontact/add_moment_task?access_token={token}",
                payload,
            )
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        die(f"发布失败 HTTP {e.code}: {body}")

    errcode = result.get("errcode")
    ok = result.get("ok")
    if errcode == 0 or ok is True:
        print("✓ 发布成功")
        mid = result.get("moment_id") or result.get("jobid")
        if mid:
            print(f"  moment_id: {mid}")
    elif errcode is not None:
        die(f"✗ 发布失败 (errcode={errcode}): {result.get('errmsg', '')}")
    else:
        die(f"✗ 发布失败: {result}")


if __name__ == "__main__":
    main()
