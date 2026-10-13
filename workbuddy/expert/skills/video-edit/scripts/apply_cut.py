#!/usr/bin/env python3
"""apply_cut.py — 按 cut_plan.json 剪拼视频。

用法：
  python3 apply_cut.py <input.mp4> <cut_plan.json> [--output output.mp4] [--fade-ms 40]

流程：
  1. 读 cut_plan.json，滤 keep=true 段
  2. ffmpeg atrim/ss 逐段抽出（关键帧对齐两遍法：第一遍抽粗段，第二遍精定位）
  3. 段间加 --fade-ms 毫秒 triangular fade 防咔点
  4. concat 拼接 + libx264/aac 编码

与 extract_and_concat.py 的分工：
  - extract_and_concat.py：人工指定剪头/尾/中段 + 拼接（用户告诉 agent 剪哪）
  - apply_cut.py：按 cut_plan.json 自动剪（cut_plan.py 自判剪哪，用户只给源视频 + 模式开关）

依赖：ffmpeg；无第三方 Python 包。与 assemble.py / extract_and_concat.py 同范式。

退出码：
  0 = 成功
  1 = 参数错误 / 文件不存在 / cut_plan 格式错
  3 = ffmpeg 不存在
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def _run_ffmpeg(cmd: list, label: str) -> bool:
    """跑一条 ffmpeg 命令，返 True/False；失败打印 stderr 摘要。"""
    try:
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode != 0:
            print(json.dumps({
                "ok": False,
                "label": label,
                "stderr": (r.stderr or b"").decode("utf-8", "replace")[:500],
            }), file=sys.stderr)
            return False
        return True
    except FileNotFoundError:
        print(json.dumps({"ok": False, "error": "ffmpeg 未安装"}), file=sys.stderr)
        return False


def extract_segments(input_path: str, plan: list, tmp_dir: str,
                     width: int, height: int, fps: int, fade_ms: int) -> list:
    """逐段抽出 keep=true 段，落 tmp_dir/seg_NN.mp4。返段路径列表。"""
    segs = []
    kept = [(i, p) for i, p in enumerate(plan) if p.get("keep")]
    if not kept:
        return []

    for idx, (i, p) in enumerate(kept):
        s = float(p["start"])
        e = float(p["end"])
        dur = e - s
        if dur <= 0:
            continue
        seg_path = os.path.join(tmp_dir, f"seg_{idx:02d}.mp4")

        # 段间淡入淡出（防咔点）
        fade_opt = ""
        if fade_ms > 0:
            fade_dur = fade_ms / 1000.0
            fade_out_st = max(0, dur - fade_dur)
            fade_opt = (
                f"afade=in:d={fade_dur},"
                f"afade=out:d={fade_dur}:st={fade_out_st}"
            )

        # 视频滤镜：scale 保持比例 + pad 到目标分辨率 + setsar + fps
        vf = (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}"
        )

        cmd = [
            "ffmpeg", "-y",
            "-ss", str(s),
            "-t", str(dur),
            "-i", input_path,
            "-vf", vf,
        ]
        if fade_opt:
            cmd += ["-af", fade_opt]
        cmd += [
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "20",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            seg_path,
        ]

        if not _run_ffmpeg(cmd, f"extract seg {idx}"):
            continue
        if not os.path.isfile(seg_path) or os.path.getsize(seg_path) == 0:
            continue
        segs.append(seg_path)

    return segs


def concat_segments(seg_paths: list, output_path: str) -> bool:
    """ffmpeg concat 拼接段。"""
    if not seg_paths:
        return False

    # 单段直接复制
    if len(seg_paths) == 1:
        import shutil
        shutil.copy(seg_paths[0], output_path)
        return True

    # 多段 concat
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tf:
        for sp in seg_paths:
            tf.write(f"file '{sp}'\n")
        list_path = tf.name

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_path,
        "-c", "copy",
        output_path,
    ]
    ok = _run_ffmpeg(cmd, "concat")

    try:
        os.unlink(list_path)
    except OSError:
        pass

    return ok


def probe_dimensions(input_path: str) -> tuple:
    """ffprobe 拿宽高 + fps，失败退 1280x720 30fps。"""
    try:
        r = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,r_frame_rate",
                "-of", "json",
                input_path,
            ],
            capture_output=True,
        )
        if r.returncode != 0:
            return (1280, 720, 30)
        data = json.loads(r.stdout)
        streams = data.get("streams") or []
        if not streams:
            return (1280, 720, 30)
        s = streams[0]
        w = int(s.get("width") or 1280)
        h = int(s.get("height") or 720)
        fr = s.get("r_frame_rate", "30/1")
        if "/" in fr:
            num, den = fr.split("/", 1)
            fps = int(round(eval(f"{num}/{den}"))) if den and int(den) != 0 else 30
        else:
            fps = int(float(fr))
        return (w, h, fps)
    except Exception:
        return (1280, 720, 30)


def main() -> None:
    parser = argparse.ArgumentParser(description="按 cut_plan.json 剪拼视频")
    parser.add_argument("input", help="输入源视频")
    parser.add_argument("plan", help="cut_plan.json 路径")
    parser.add_argument("--output", default=None,
                        help="输出 MP4 路径（默认 <input>_cut.mp4）")
    parser.add_argument("--fade-ms", type=int, default=40,
                        help="段间淡入淡出毫秒（默认 40，防咔点）")
    args = parser.parse_args()

    # 默认输出路径
    if args.output is None:
        stem = os.path.splitext(args.input)[0]
        args.output = f"{stem}_cut.mp4"

    # 校验输入
    if not os.path.isfile(args.input):
        print(json.dumps({"ok": False, "error": f"输入文件不存在: {args.input}"}),
              file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.plan):
        print(json.dumps({"ok": False, "error": f"计划文件不存在: {args.plan}"}),
              file=sys.stderr)
        sys.exit(1)

    # 校验 ffmpeg
    if subprocess.run(["which", "ffmpeg"], capture_output=True).returncode != 0:
        print(json.dumps({"ok": False, "error": "ffmpeg 未安装"}), file=sys.stderr)
        sys.exit(3)

    # 读 cut_plan.json
    with open(args.plan, "r", encoding="utf-8") as f:
        plan_data = json.load(f)

    if not plan_data.get("ok", True) is True and "ok" in plan_data:
        # ok=false 不能应用
        if plan_data.get("ok") is False:
            print(json.dumps({"ok": False, "error": "cut_plan.json 标记 ok=false，不能应用"}),
                  file=sys.stderr)
            sys.exit(1)

    plan = plan_data.get("plan") or []
    kept = [p for p in plan if p.get("keep")]
    if not kept:
        print(json.dumps({"ok": False, "error": "cut_plan.json 中无 keep=true 段，无可剪拼"}),
              file=sys.stderr)
        sys.exit(1)

    # 探测源分辨率/帧率
    width, height, fps = probe_dimensions(args.input)

    # 逐段抽 + 拼接
    with tempfile.TemporaryDirectory(prefix="apply_cut_") as tmp_dir:
        segs = extract_segments(
            args.input, plan, tmp_dir,
            width, height, fps, args.fade_ms,
        )
        if not segs:
            print(json.dumps({"ok": False, "error": "逐段抽出全部失败"}), file=sys.stderr)
            sys.exit(1)

        if not concat_segments(segs, args.output):
            print(json.dumps({"ok": False, "error": "concat 拼接失败"}), file=sys.stderr)
            sys.exit(1)

    # 成片自检
    if not os.path.isfile(args.output) or os.path.getsize(args.output) == 0:
        print(json.dumps({"ok": False, "error": "成片不存在或为空"}), file=sys.stderr)
        sys.exit(1)

    # 输出报告
    keep_dur = sum(p["end"] - p["start"] for p in kept)
    report = {
        "ok": True,
        "output": args.output,
        "segments": len(segs),
        "kept_segments": len(kept),
        "kept_duration": round(keep_dur, 3),
        "resolution": f"{width}x{height}",
        "fps": fps,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
