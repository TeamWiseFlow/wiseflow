#!/usr/bin/env python3
"""publish_wx_mp.py — 推送 Markdown 稿件到微信公众号草稿箱（经 relay 透传凭据）

Usage:
  python3 publish_wx_mp.py <markdown_file> [theme] [--account ALIAS]

凭据：从同级 ../accounts.json 读取（多账号，由 Agent 帮用户维护）。
relay：RELAY_BASE_URL + OFB_KEY 来自 daemon.env（entrypoint 注入）。

relay 端点：POST {RELAY_BASE_URL}/api/v1/wx-mp/publish
  multipart：markdown + wechat_app_id + wechat_app_secret + theme? + images?*
  响应包络：{ success, data: { media_id?, article_url? }, error }
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
# 凭据放在源仓之外（实例态目录），避免软链模式下密钥落进源仓工作树
ACCOUNTS_FILE = (Path(os.environ.get("XIAOBEI_WORKBUDDY_HOME", Path.home() / ".xiaobei-workbuddy"))) / "wx-mp-publisher" / "accounts.json"
PUBLISHER_DIR = SCRIPT_DIR.parent
TOOLS_DIR = PUBLISHER_DIR.parent
EXPERT_PACK_DIR = TOOLS_DIR.parent
SKILLS_DIR = EXPERT_PACK_DIR.parent


def _detect_crew_workspace() -> Path:
    return Path(os.environ["XIAOBEI_WORKSPACE"])


CREW_WORKSPACE = _detect_crew_workspace()
THEME_ROOT = CREW_WORKSPACE / "wx_mp" / "wenyan-theme"
THEME_INDEX = THEME_ROOT / "index.json"
DEFAULT_RELAY_BASE_URL = "https://relay.openclaw-for-business.com"
ENDPOINT = "/api/v1/wx-mp/publish"
TIMEOUT_S = 180


def die(msg: str) -> None:
    print(f"✗ {msg}", file=sys.stderr)
    sys.exit(1)


def log(msg: str) -> None:
    print(f">>> {msg}", flush=True)


# ── 凭据 ─────────────────────────────────────────────────────────────────────

def load_account(alias_arg: str | None) -> tuple[str, str, str]:
    """返回 (alias, appId, appSecret)。alias_arg 为 None 时用 default。"""
    if not ACCOUNTS_FILE.exists():
        die(
            "未找到公众号凭据文件 accounts.json。\n"
            f"  位置：{ACCOUNTS_FILE}\n"
            "  → 请让 Agent 帮你创建并填入公众号 AppID/AppSecret（获取方式见 wx-mp-publisher SKILL 同目录 REFERENCE.md）"
        )
    try:
        cfg = json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"accounts.json 解析失败: {e}")

    accounts = cfg.get("accounts") or []
    if not accounts:
        die("accounts.json 中没有账号。请让 Agent 帮你填入公众号 AppID/AppSecret（见 REFERENCE.md）。")

    if alias_arg:
        target = next((a for a in accounts if a.get("alias") == alias_arg), None)
        if not target:
            names = ", ".join(a.get("alias", "?") for a in accounts)
            die(f"未找到账号 alias={alias_arg}。现有账号: {names}")
    else:
        default_alias = cfg.get("default", "")
        if not default_alias:
            if len(accounts) == 1:
                target = accounts[0]
            else:
                names = ", ".join(a.get("alias", "?") for a in accounts)
                die(f"存在多账号但未指定 default，且未传 --account。现有账号: {names}")
        else:
            target = next((a for a in accounts if a.get("alias") == default_alias), None)
            if not target:
                die(f"accounts.json default={default_alias!r} 在 accounts 中不存在。")

    app_id = (target.get("appId") or "").strip()
    app_secret = (target.get("appSecret") or "").strip()
    alias = target.get("alias", "?")
    if not app_id or not app_secret:
        die(f"账号 {alias!r} 缺少 appId 或 appSecret。请让 Agent 补全（见 REFERENCE.md）。")
    return alias, app_id, app_secret


# ── relay env ────────────────────────────────────────────────────────────────

def relay_env() -> tuple[str, str]:
    relay = os.environ.get("RELAY_BASE_URL", "").rstrip("/") or DEFAULT_RELAY_BASE_URL
    ofb_key = os.environ.get("OFB_KEY", "").strip()
    if not ofb_key:
        die("当前功能需要 relay 服务，OFB_KEY 尚未配置。请到 https://openclaw-for-business.com/ 查看接入说明，再通过 xiaobei-runtime 的私有配置流程继续。")
    return relay, ofb_key


# ── 主题解析 ──────────────────────────────────────────────────────────────────

def _resolve_registered_theme_path(theme_id: str) -> Path | None:
    """从 <workspace>/wx_mp/wenyan-theme/index.json 查登记的主题 id，返回受控 CSS 路径或 None。

    注册表结构：
      {"version": 1, "themes": [{"id": "...", "css": "wx_mp/wenyan-theme/....css", ...}]}
    css 为相对工作区根的路径；兼容旧的 "wenyan-theme/<id>.css" 写法（落到主题目录下同名文件）。
    """
    if not THEME_INDEX.exists():
        return None

    try:
        registry = json.loads(THEME_INDEX.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        die(f"主题注册表解析失败: {THEME_INDEX}: {e}")

    themes = registry.get("themes") if isinstance(registry, dict) else None
    if not isinstance(registry, dict) or registry.get("version") != 1 or not isinstance(themes, list):
        die(f"主题注册表格式错误: {THEME_INDEX}，需要 version=1 和 themes 数组")

    for theme in themes:
        if not isinstance(theme, dict) or theme.get("id") != theme_id:
            continue
        css = theme.get("css")
        if not isinstance(css, str) or not css:
            die(f"主题 {theme_id!r} 缺少 css 路径: {THEME_INDEX}")
        css_path = Path(css)
        if css_path.is_absolute() or css_path.suffix != ".css":
            die(
                f"主题 {theme_id!r} 的 css 必须是相对工作区的 .css 路径"
                f"（如 wx_mp/wenyan-theme/{theme_id}.css）: {THEME_INDEX}"
            )
        root = THEME_ROOT.resolve()
        # 候选解析（每个候选都先做 THEME_ROOT 包含校验，防止越界）：
        #   新约定：相对工作区根，如 "wx_mp/wenyan-theme/<id>.css"
        #   旧约定："wenyan-theme/<id>.css" 或裸 "<id>.css" → 落到主题目录下同名文件
        for cand in (CREW_WORKSPACE / css_path, THEME_ROOT / css_path.name):
            resolved = cand.resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                continue
            if resolved.is_file():
                return resolved
        die(
            f"主题 {theme_id!r} 的 CSS 文件不存在或路径越界: {css}"
            f"（注册表: {THEME_INDEX}，主题目录: {THEME_ROOT}）"
        )
    return None


def resolve_theme(theme_arg: str | None) -> tuple[str, str] | None:
    """返回 ('theme', id) / ('custom_theme', css_text) / None。

    解析顺序：
      1. theme_arg 为空 → None
      2. 以 .css 结尾且是本地文件 → custom_theme（CSS 文本）
      3. wx_mp/wenyan-theme/index.json 登记的自定义 id → 解析 CSS 路径 → custom_theme
      4. 其它 → 内置主题 id，原样作为 theme
    """
    if not theme_arg:
        return None
    p = Path(theme_arg)
    if theme_arg.endswith(".css") and p.is_file():
        return ("custom_theme", p.read_text(encoding="utf-8"))
    css_path = _resolve_registered_theme_path(theme_arg)
    if css_path is not None:
        return ("custom_theme", css_path.read_text(encoding="utf-8"))
    return ("theme", theme_arg)


# ── multipart 构建 ───────────────────────────────────────────────────────────

def build_multipart(fields: dict[str, str], files: list[tuple[str, Path]]) -> tuple[bytes, str]:
    """手动构造 multipart/form-data，返回 (body, content_type)。文本字段按 utf-8 原样写入（不 base64）。"""
    import mimetypes
    import uuid

    boundary = uuid.uuid4().hex
    parts: list[bytes] = []
    for name, value in fields.items():
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n".encode("utf-8")
            + value.encode("utf-8") + b"\r\n"
        )
    for name, path in files:
        ctype, _ = mimetypes.guess_type(str(path))
        if ctype is None:
            ctype = "application/octet-stream"
        with open(path, "rb") as f:
            file_data = f.read()
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"; filename=\"{path.name}\"\r\n"
            f"Content-Type: {ctype}\r\n\r\n".encode("utf-8")
            + file_data + b"\r\n"
        )
    body = b"".join(parts) + f"--{boundary}--\r\n".encode("ascii")
    content_type = f"multipart/form-data; boundary={boundary}"
    return body, content_type


def _frontmatter_local_refs(md_text: str) -> list[str]:
    """从 YAML frontmatter 提取 cover / image_list 里的本地图片引用（原始字符串）。"""
    if not md_text.startswith("---"):
        return []
    end = md_text.find("\n---", 3)
    if end < 0:
        return []
    refs: list[str] = []
    in_image_list = False
    for line in md_text[3:end].splitlines():
        m = re.match(r"^\s*cover:\s*(\S+)", line)
        if m:
            refs.append(m.group(1))
            in_image_list = False
            continue
        if re.match(r"^\s*image_list:\s*$", line):
            in_image_list = True
            continue
        if re.match(r"^\s*image_list:\s*\S", line):
            in_image_list = False
            continue
        if in_image_list:
            m = re.match(r"^\s*-\s+(\S+)", line)
            if m:
                refs.append(m.group(1))
            elif re.match(r"^\S", line):
                in_image_list = False
    return refs


def extract_local_images(md_text: str, md_dir: Path) -> list[Path]:
    """从 markdown 提取本地图片路径：正文 ![]() + frontmatter cover / image_list。

    http/https/data: 跳过（由 relay 自行抓取）。
    """
    out: list[Path] = []
    seen: set[Path] = set()

    def add(src: str) -> None:
        if src.startswith(("http://", "https://", "data:")):
            return
        p = Path(src) if Path(src).is_absolute() else (md_dir / src).resolve()
        if p.is_file() and p not in seen:
            seen.add(p)
            out.append(p)

    for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", md_text):
        add(m.group(1).split()[0])  # 去掉可选 title
    for ref in _frontmatter_local_refs(md_text):
        add(ref)
    return out


def rewrite_image_refs(md_text: str, local_images: list[Path], md_dir: Path) -> str:
    """把本地图片引用重写为 basename，与 images multipart 文件名对齐。

    relay 端 @wenyan-md/core 渲染时按文件名匹配上传的 images，带目录前缀或绝对路径
    会让 relay 去自己磁盘 stat 报 ENOENT。覆盖 markdown / frontmatter 里可能出现的
    所有形式：绝对路径、`./name`、`name`、以及相对 md_dir 的子目录路径（如 `images/x.jpg`）。
    """
    if not local_images:
        return md_text
    for img in local_images:
        name = img.name
        candidates = {str(img), f"./{name}", name}
        try:
            candidates.add(str(img.relative_to(md_dir)))
        except ValueError:
            pass
        for original in candidates:
            if original != name:
                md_text = md_text.replace(original, name)
    return md_text


# ── 发布前校验 ─────────────────────────────────────────────────────────────

# 微信草稿 author 字段上限：8 个汉字 / 24 字节（errcode 45110: author size out of limit）
WX_AUTHOR_MAX_BYTES = 24


def _parse_frontmatter_author(md_text: str) -> str | None:
    """从 YAML frontmatter 提取 author 字段值（去首尾引号）；无则返回 None。"""
    if not md_text.startswith("---"):
        return None
    end = md_text.find("\n---", 3)
    if end < 0:
        return None
    for line in md_text[3:end].splitlines():
        m = re.match(r"^\s*author:\s*(.+?)\s*$", line)
        if m:
            val = m.group(1).strip()
            if (val.startswith('"') and val.endswith('"')) or (
                val.startswith("'") and val.endswith("'")
            ):
                val = val[1:-1]
            return val
    return None


def validate_for_publish(md_text: str) -> None:
    """发布前校验，命中违规即 die() 拦截，避免 relay/微信侧报错。

    1. 本地图片引用必须用纯文件名（basename），不得含目录前缀或绝对路径。
    2. frontmatter author 字段 ≤ 24 字节（8 个汉字）。
    """
    # 1. 图片引用：正文 ![]() + frontmatter cover/image_list
    local_refs = [
        m.group(1).split()[0] for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", md_text)
    ]
    local_refs += _frontmatter_local_refs(md_text)
    bad_imgs = [
        ref
        for ref in local_refs
        if not ref.startswith(("http://", "https://", "data:"))
        and ("/" in ref or "\\" in ref or Path(ref).is_absolute())
    ]
    if bad_imgs:
        die(
            "图片引用必须用纯文件名（与上传时的 originalname 一致），不得带目录前缀或绝对路径。\n"
            "  relay 把图片按 originalname 存到 per-request 临时目录，带前缀的路径在 relay 侧\n"
            "  stat 不到会 ENOENT。请改为 basename：\n    "
            + "\n    ".join(bad_imgs)
        )

    # 2. author 长度
    author = _parse_frontmatter_author(md_text)
    if author is not None:
        n = len(author.encode("utf-8"))
        if n > WX_AUTHOR_MAX_BYTES:
            die(
                f"frontmatter author 超过微信草稿上限（{WX_AUTHOR_MAX_BYTES} 字节 / 8 个汉字），"
                f"当前 {n} 字节：{author!r}。请缩短 author 字段。"
            )


# ── 主流程 ───────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="推送 Markdown 到微信公众号草稿箱（经 relay）")
    parser.add_argument("markdown_file", help="Markdown 文件路径")
    parser.add_argument(
        "theme", nargs="?", default=None,
        help="主题：内置 id（pie/lapis/default/…）/ 本地 .css 路径 / wx_mp/wenyan-theme/index.json 登记的自定义 id",
    )
    parser.add_argument("--account", default=None, help="指定公众号 alias（缺省用 accounts.json 的 default）")
    args = parser.parse_args()

    md_path = Path(args.markdown_file)
    if not md_path.is_file():
        die(f"文件不存在: {md_path}")

    alias, app_id, app_secret = load_account(args.account)
    relay, ofb_key = relay_env()

    md_text = md_path.read_text(encoding="utf-8")
    images = extract_local_images(md_text, md_path.parent)
    md_text = rewrite_image_refs(md_text, images, md_path.parent)
    validate_for_publish(md_text)

    fields = {
        "markdown": md_text,
        "wechat_app_id": app_id,
        "wechat_app_secret": app_secret,
    }
    theme_field = resolve_theme(args.theme)
    if theme_field is not None:
        fields[theme_field[0]] = theme_field[1]
    files = [("images", p) for p in images]

    log(f"账号: {alias}")
    if theme_field is None:
        log("主题: (relay 默认)")
    elif theme_field[0] == "custom_theme":
        nbytes = len(theme_field[1].encode("utf-8"))
        log(f"主题: 自定义 CSS（{nbytes} 字节，随请求上传 relay 不持久化）")
    else:
        log(f"主题: {theme_field[1]}")
    log(f"图片: {len(images)} 张")
    log("正在推送草稿到 relay...")

    body, content_type = build_multipart(fields, files)
    url = f"{relay}{ENDPOINT}"
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": content_type, "X-OFB-Key": ofb_key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            payload = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        text = e.read().decode(errors="replace")
        die(f"relay HTTP {e.code}: {text}")
    except urllib.error.URLError as e:
        die(f"relay 不可达: {e.reason}")

    if not payload.get("success"):
        err = payload.get("error") or payload
        die(f"发布失败: {err}")

    data = payload.get("data") or {}
    print("✓ 草稿已推送")
    if data.get("media_id"):
        print(f"  media_id: {data['media_id']}")
    if data.get("article_url"):
        print(f"  article_url: {data['article_url']}")
    print("  下一步：在公众号后台「草稿箱」中预览并正式发布。")


if __name__ == "__main__":
    main()
