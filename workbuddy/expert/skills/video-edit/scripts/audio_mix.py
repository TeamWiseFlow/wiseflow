#!/usr/bin/env python3
"""audio_mix.py — 给已有视频加旁白/背景音乐（混音后处理）。

用法：
  python3 audio_mix.py <input.mp4> --bgm music.mp3 [--bgm-volume 0.25] [--output out.mp4]
  python3 audio_mix.py <input.mp4> --narration speech.mp3 [--original-volume 0] [--output out.mp4]
  python3 audio_mix.py <input.mp4> --narration speech.mp3 --bgm music.mp3 [--output out.mp4]

行为：
  - 只给 --bgm：BGM 循环/裁剪到视频时长，按 --bgm-volume 压低后混入原音轨，结尾 2s 淡出
  - 只给 --narration：旁白替换原音轨；--original-volume > 0 时改为原音轨按该音量垫底混入
  - 两个都给：旁白为主 + BGM 垫底；原音轨默认丢弃，--original-volume > 0 时混入
  - 视频流不重编码（-c:v copy），只重编音频（aac 192k）

退出码：
  0 = 成功
  1 = 参数错误 / 文件不存在 / ffmpeg 失败
  3 = ffmpeg/ffprobe 不存在
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


def check_bins() -> None:
    for b in ("ffmpeg", "ffprobe"):
        if subprocess.run(["which", b], capture_output=True).returncode != 0:
            die(f"{b} 未安装", 3)


def probe(input_path: str) -> tuple:
    """返 (duration, has_audio)。"""
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-show_entries", "stream=codec_type", "-of", "json", input_path],
        capture_output=True,
    )
    if r.returncode != 0:
        die(f"ffprobe 失败: {input_path}")
    data = json.loads(r.stdout)
    duration = float(data.get("format", {}).get("duration") or 0)
    has_audio = any(s.get("codec_type") == "audio" for s in data.get("streams", []))
    if duration <= 0:
        die(f"无法读取视频时长: {input_path}")
    return duration, has_audio


def main() -> None:
    parser = argparse.ArgumentParser(description="给已有视频加旁白/背景音乐（混音后处理）")
    parser.add_argument("input", help="输入视频")
    parser.add_argument("--narration", default=None, help="旁白音频文件")
    parser.add_argument("--bgm", default=None, help="背景音乐文件（自动循环/裁剪到视频时长）")
    parser.add_argument("--bgm-volume", type=float, default=0.25,
                        help="BGM 音量系数（默认 0.25）")
    parser.add_argument("--narration-volume", type=float, default=1.0,
                        help="旁白音量系数（默认 1.0）")
    parser.add_argument("--original-volume", type=float, default=None,
                        help="原音轨音量系数（默认：无旁白时 1.0，有旁白时 0 即替换）")
    parser.add_argument("--output", default=None,
                        help="输出 MP4 路径（默认 <input>_mixed.mp4）")
    args = parser.parse_args()

    if not args.narration and not args.bgm:
        die("--narration 与 --bgm 至少给一个")
    if not os.path.isfile(args.input):
        die(f"输入文件不存在: {args.input}")
    for p in (args.narration, args.bgm):
        if p and not os.path.isfile(p):
            die(f"音频文件不存在: {p}")

    check_bins()
    duration, has_audio = probe(args.input)

    if args.output is None:
        stem = os.path.splitext(args.input)[0]
        args.output = f"{stem}_mixed.mp4"

    orig_vol = args.original_volume
    if orig_vol is None:
        orig_vol = 0.0 if args.narration else 1.0

    # 组输入：0 = 视频；旁白/BGM 依次追加
    cmd = ["ffmpeg", "-y", "-i", args.input]
    idx = 1
    narration_idx = bgm_idx = None
    if args.narration:
        cmd += ["-i", args.narration]
        narration_idx = idx
        idx += 1
    if args.bgm:
        cmd += ["-stream_loop", "-1", "-i", args.bgm]
        bgm_idx = idx
        idx += 1

    # 音频链：主音（旁白 > 原音轨）在前，垫底音在后
    chains = []
    labels = []
    if narration_idx is not None:
        chains.append(f"[{narration_idx}:a]volume={args.narration_volume}[an]")
        labels.append("[an]")
    if has_audio and orig_vol > 0:
        chains.append(f"[0:a]volume={orig_vol}[ao]")
        labels.append("[ao]")
    if bgm_idx is not None:
        fade_st = max(0.0, duration - 2.0)
        chains.append(
            f"[{bgm_idx}:a]atrim=0:{duration},asetpts=PTS-STARTPTS,"
            f"volume={args.bgm_volume},afade=out:st={fade_st}:d=2[ab]"
        )
        labels.append("[ab]")

    if not labels:
        die("无可用音频源（视频无音轨且未给 --narration/--bgm 有效输入）")

    if len(labels) == 1:
        chains.append(f"{labels[0]}anull[aout]")
    else:
        chains.append(
            f"{''.join(labels)}amix=inputs={len(labels)}:duration=first:"
            f"dropout_transition=0:normalize=0[aout]"
        )

    cmd += [
        "-filter_complex", ";".join(chains),
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(duration),
        "-movflags", "+faststart",
        args.output,
    ]

    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        die("ffmpeg 混音失败: " + (r.stderr or b"").decode("utf-8", "replace")[-500:])
    if not os.path.isfile(args.output) or os.path.getsize(args.output) == 0:
        die("输出不存在或为空")

    print(json.dumps({
        "ok": True,
        "output": args.output,
        "duration": round(duration, 2),
        "narration": args.narration,
        "bgm": args.bgm,
        "original_volume": orig_vol,
    }, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
