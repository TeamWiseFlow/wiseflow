#!/usr/bin/env python3
"""sample_frames.py — 按固定间隔抽帧，供 agent 逐帧看图做画面分析。

用法：
  python3 sample_frames.py <input.mp4> [--interval 3] [--max-frames 100]
                           [--width 640] [--output-dir <dir>]

行为：
  - 每 --interval 秒抽一帧；若按此间隔帧数会超过 --max-frames，自动放大间隔
  - 帧缩放到 --width 宽（保持比例），JPEG 落 --output-dir
  - 帧名带时间戳：frame_0007_21.0s.jpg（第 7 帧，21.0 秒处）
  - 同目录落 index.json 并打印到 stdout：{ok, source, duration, interval, count, frames:[{file, t}]}

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


def probe_duration(input_path: str) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", input_path],
        capture_output=True,
    )
    if r.returncode != 0:
        die(f"ffprobe 失败: {input_path}")
    duration = float(json.loads(r.stdout).get("format", {}).get("duration") or 0)
    if duration <= 0:
        die(f"无法读取视频时长: {input_path}")
    return duration


def main() -> None:
    parser = argparse.ArgumentParser(description="按固定间隔抽帧，供 agent 逐帧看图做画面分析")
    parser.add_argument("input", help="输入视频")
    parser.add_argument("--interval", type=float, default=3.0,
                        help="抽帧间隔秒（默认 3）")
    parser.add_argument("--max-frames", type=int, default=100,
                        help="最大帧数（默认 100，超出自动放大间隔）")
    parser.add_argument("--width", type=int, default=640,
                        help="帧宽 px（默认 640，保持比例）")
    parser.add_argument("--output-dir", default=None,
                        help="帧输出目录（默认 <input 同目录>/frames）")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        die(f"输入文件不存在: {args.input}")
    if args.interval <= 0 or args.max_frames <= 0:
        die("--interval 与 --max-frames 必须为正")
    for b in ("ffmpeg", "ffprobe"):
        if subprocess.run(["which", b], capture_output=True).returncode != 0:
            die(f"{b} 未安装", 3)

    duration = probe_duration(args.input)
    interval = args.interval
    if duration / interval > args.max_frames:
        interval = round(duration / args.max_frames, 1)

    out_dir = args.output_dir or os.path.join(
        os.path.dirname(os.path.abspath(args.input)), "frames")
    os.makedirs(out_dir, exist_ok=True)

    tmp_pattern = os.path.join(out_dir, "tmp_%05d.jpg")
    cmd = [
        "ffmpeg", "-y",
        "-i", args.input,
        "-vf", f"fps=1/{interval},scale={args.width}:-2",
        "-q:v", "4",
        tmp_pattern,
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        die("ffmpeg 抽帧失败: " + (r.stderr or b"").decode("utf-8", "replace")[-500:])

    # tmp_%05d 从 1 起；第 n 张对应 t=(n-1)*interval（fps 滤镜首帧在 0s）
    frames = []
    n = 1
    while True:
        tmp_path = os.path.join(out_dir, f"tmp_{n:05d}.jpg")
        if not os.path.isfile(tmp_path):
            break
        t = round((n - 1) * interval, 1)
        name = f"frame_{n - 1:04d}_{t}s.jpg"
        os.replace(tmp_path, os.path.join(out_dir, name))
        frames.append({"file": os.path.join(out_dir, name), "t": t})
        n += 1

    if not frames:
        die("未抽出任何帧")

    report = {
        "ok": True,
        "source": args.input,
        "duration": round(duration, 2),
        "interval": interval,
        "count": len(frames),
        "frames": frames,
    }
    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
