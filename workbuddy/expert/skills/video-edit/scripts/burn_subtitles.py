#!/usr/bin/env python3
"""burn_subtitles.py — 把 SRT/ASS 字幕烧录进视频。

用法：
  python3 burn_subtitles.py <input.mp4> <subs.srt> [--output out.mp4]
                            [--font-size 20] [--margin-v 40] [--position bottom|top]

行为：
  - SRT 走统一样式（白字黑描边居中，--font-size/--margin-v/--position 可调）
  - ASS 自带样式，样式参数被忽略
  - 视频重编码（libx264 crf 20），音频不动（-c:a copy）

退出码：
  0 = 成功
  1 = 参数错误 / 文件不存在 / ffmpeg 失败
  3 = ffmpeg 不存在
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys


def die(msg: str, code: int = 1) -> None:
    print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False), file=sys.stderr)
    sys.exit(code)


def filter_escape(s: str) -> str:
    """转义 ffmpeg filtergraph 参数里的特殊字符。"""
    out = s
    for c in ("\\", "'", ":", ",", ";", "[", "]"):
        out = out.replace(c, "\\" + c)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="把 SRT/ASS 字幕烧录进视频")
    parser.add_argument("input", help="输入视频")
    parser.add_argument("subs", help="字幕文件（.srt 或 .ass）")
    parser.add_argument("--output", default=None,
                        help="输出 MP4 路径（默认 <input>_sub.mp4）")
    parser.add_argument("--font-size", type=int, default=20,
                        help="字号（默认 20，仅 SRT 生效）")
    parser.add_argument("--margin-v", type=int, default=40,
                        help="垂直边距 px（默认 40，仅 SRT 生效）")
    parser.add_argument("--position", choices=["bottom", "top"], default="bottom",
                        help="字幕位置（默认 bottom，仅 SRT 生效）")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        die(f"输入文件不存在: {args.input}")
    if not os.path.isfile(args.subs):
        die(f"字幕文件不存在: {args.subs}")
    if subprocess.run(["which", "ffmpeg"], capture_output=True).returncode != 0:
        die("ffmpeg 未安装", 3)

    if args.output is None:
        stem = os.path.splitext(args.input)[0]
        args.output = f"{stem}_sub.mp4"

    subs_path = filter_escape(os.path.abspath(args.subs))
    if args.subs.lower().endswith(".ass"):
        vf = f"subtitles={subs_path}"
    else:
        alignment = 2 if args.position == "bottom" else 8  # ASS：2=底部居中，8=顶部居中
        style = (
            "FontName=Noto Sans CJK SC,"
            f"FontSize={args.font_size},"
            "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
            "Outline=2,Shadow=0,"
            f"Alignment={alignment},MarginV={args.margin_v}"
        )
        vf = f"subtitles={subs_path}:force_style={filter_escape(style)}"

    cmd = [
        "ffmpeg", "-y",
        "-i", args.input,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-movflags", "+faststart",
        args.output,
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        die("ffmpeg 烧录失败: " + (r.stderr or b"").decode("utf-8", "replace")[-500:])
    if not os.path.isfile(args.output) or os.path.getsize(args.output) == 0:
        die("输出不存在或为空")

    print(json.dumps({
        "ok": True,
        "output": args.output,
        "subs": args.subs,
    }, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
