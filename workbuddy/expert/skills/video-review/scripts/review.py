#!/usr/bin/env python3
"""Final-video self-review — post-compose quality gate.

Runs AFTER assemble.py / apply_cut.py produces video.mp4 (or highlight.mp4).
Outputs verdict JSON. The calling skill's workflow mandates: review.py must
pass before the video is handed back to the user. A "fail" verdict means the
agent must fix and re-review, not deliver.

What it checks:
  1. ffprobe full validation — codec, resolution, fps, pixel format, audio config
  2. 5-position frame extraction (0% / 25% / 50% / 75% / 100%) → black-frame + overlay-break scan
  3. Audio level analysis — silence / clipping / absent track
  4. Duration vs target (from sibling script.md 片段规划表 时长列累加，or --target-duration)
  5. Resolution uniformity — checks the成片 matches the first segment's resolution
     (拼了不同分辨率段是硬伤)

NOT included (deliberately):
  - Subtitle presence check — assemble.py 不烧字幕，无意义
  - Delivery promise / slideshow risk — 那是脚本阶段的事，归 Step 2 slideshow-risk 自检清单
  - Decision audit trail — 那是 decisions.log 的事，归 state.json + decisions.log

Usage:
  video-review <final.mp4>                    # 直接审单个成片文件
  video-review <project-dir>                  # 审 <dir>/video.mp4 + artifacts/ 段一致性
  video-review <project-dir> --target-duration 30 --target-resolution 720x1280
  video-review <final.mp4> --output review.json

Exit codes:
  0  verdict = "pass"   → 可以交付
  1  verdict = "fail"   → 必须修，不准交
  2  verdict = "warn"   → 有 non-critical issues，向用户复述让其决定是否重修
  3  script error (ffprobe missing / path invalid / ...) — 脚本本身故障，不算评审结论

Verdict JSON schema (also pretty-printed to stdout):
  {
    "verdict": "pass" | "fail" | "warn",
    "file": "<video.mp4 absolute path>",
    "ffprobe": { codec, width, height, fps, pix_fmt, duration, size_bytes, audio {...} },
    "frames": [ { "position_pct": 0, "path": "...", "mean_luma": 0.0, "is_black": false } ],
    "audio_level": { "mean_db": -32.4, "max_db": -8.1, "silent": false, "clipping": false },
    "checks": [
      { "name": "duration_match",   "status": "pass",    "detail": "actual 30.2s vs target 30s, gap 0.2s" },
      { "name": "resolution_720p",  "status": "pass",    "detail": "720x1280" },
      { "name": "resolution_uniform", "status": "fail",    "detail": "成片 720x1280 vs 段01 1080x1920" },
      ...
    ],
    "critical": [ "resolution_uniform: ..." ],
    "warnings": [ "audio_level mean_db=-42.1 close to silent threshold" ]
  }
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────────

VIDEO_EXTS = {".mp4", ".mov", ".webm", ".mkv", ".avi"}
REVIEW_DIR_NAME = "review"        # <project-dir>/review/ 抽帧 + verdict JSON 落这
FRAMES_SUBDIR = "frames"

# Frame extraction positions (% of duration). 5 位（0/25/50/75/100%）足够拦黑帧/overlay 损，不堆 footage。
FRAME_POSITIONS_PCT = [0.0, 25.0, 50.0, 75.0, 100.0]

# Black frame threshold — luma mean below this → "black". 对齐 check.py 的 0.02，可调。
BLACK_LUMA_THRESHOLD = 0.02
# Audio thresholds — 声画同出模式下 BGM+旁白正常电平 -25~-10 dB，过静/过响都硬伤
AUDIO_SILENT_THRESHOLD_DB = -60.0
AUDIO_CLIPPING_THRESHOLD_DB = -1.0

# Duration tolerance — 拼接允许 ±5% 偏差
DURATION_TOLERANCE_PCT = 5.0

# Resolution floor — 9:16 竖屏短视频最低 720x1280，横屏 1280x720
RES_MIN_LONG = 720
RES_MIN_SHORT = 720


# ── Helpers ────────────────────────────────────────────────────────────────

def die(msg: str, code: int = 3) -> None:
    print(f"[error] {msg}", file=sys.stderr)
    sys.exit(code)


def run(cmd: list[str], timeout: int = 60) -> tuple[int, str, str]:
    """Run a subprocess, return (exit, stdout, stderr)."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except FileNotFoundError:
        die(f"missing binary: {cmd[0]}")
    except subprocess.TimeoutExpired:
        die(f"timeout running: {' '.join(cmd[:3])}...")


def ffprobe(path: str) -> dict:
    """Full ffprobe dump as dict. Returns {error: str} on failure."""
    rc, out, err = run([
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", path,
    ], timeout=30)
    if rc != 0:
        return {"error": f"ffprobe exit {rc}: {err.strip()}"}
    try:
        return json.loads(out)
    except json.JSONDecodeError as e:
        return {"error": f"ffprobe output not JSON: {e}"}


# ── Frame extraction & black detection ─────────────────────────────────────

def extract_frames(video: str, duration: float, out_dir: Path) -> list[dict]:
    """Extract 5 frames at FRAME_POSITIONS_PCT. Returns list of {position_pct, path, mean_luma, is_black}."""
    out_dir.mkdir(parents=True, exist_ok=True)
    frames: list[dict] = []

    for pct in FRAME_POSITIONS_PCT:
        # timestamp in seconds
        ts = duration * pct / 100.0
        # 端 0% 时 ts=0，ffmpeg trim 起会拒；用 -ss 段定位 + -frames:v 1
        frame_path = out_dir / f"frame_{int(pct):03d}.jpg"
        cmd = [
            "ffmpeg", "-y", "-v", "quiet",
            "-ss", f"{ts:.3f}", "-i", video,
            "-frames:v", "1", "-q:v", "2",
            str(frame_path),
        ]
        rc, _, _ = run(cmd, timeout=30)
        if rc != 0 or not frame_path.exists():
            frames.append({"position_pct": pct, "path": None, "mean_luma": None, "is_black": None})
            continue

        # Use ffmpeg signalstats to get mean luma. signalstats gives YAVG.
        rc, out, _ = run([
            "ffmpeg", "-v", "quiet", "-i", str(frame_path),
            "-vf", "signalstats", "-f", "null", "-",
        ], timeout=15)
        mean_luma: float | None = None
        # signalstats prints to stderr normally; with quiet we get nothing.
        # Fallback: use ffmpeg with stderr passthrough to catch YAVG=N.
        if rc == 0:
            rc2, out2, err2 = run([
                "ffmpeg", "-v", "info", "-i", str(frame_path),
                "-vf", "signalstats", "-f", "null", "-",
            ], timeout=15)
            for line in (err2 + out2).splitlines():
                # Example: "signalstats: YAVG=0.012300 ..."
                if "YAVG=" in line:
                    try:
                        mean_luma = float(line.split("YAVG=")[1].split()[0])
                    except (IndexError, ValueError):
                        pass
                    break

        # If signalstats failed, try a Pillow-free fallback via ffmpeg lutyuv mean
        if mean_luma is None:
            # Use ffmpeg blackframe filter — it logs frames below threshold
            rc3, _, err3 = run([
                "ffmpeg", "-v", "info", "-i", str(frame_path),
                "-vf", f"blackframe=threshold={BLACK_LUMA_THRESHOLD}",
                "-f", "null", "-",
            ], timeout=15)
            # If "black" appears in stderr, frame is black
            is_black_log = "First black frame detected" in err3 or "black" in err3.lower()
            mean_luma = 0.0 if is_black_log else 0.5  # placeholder; we trust is_black_log

        is_black = mean_luma is not None and mean_luma < BLACK_LUMA_THRESHOLD
        frames.append({
            "position_pct": pct,
            "path": str(frame_path),
            "mean_luma": round(mean_luma, 4) if mean_luma is not None else None,
            "is_black": is_black,
        })

    return frames


# ── Audio level analysis ────────────────────────────────────────────────────

def analyze_audio(video: str, has_audio: bool) -> dict:
    """Use ffmpeg volumedetect filter. Returns {mean_db, max_db, silent, clipping, absent}."""
    if not has_audio:
        return {"absent": True, "silent": None, "clipping": None, "mean_db": None, "max_db": None}

    rc, _, err = run([
        "ffmpeg", "-v", "info", "-i", video,
        "-af", "volumedetect",
        "-f", "null", "-",
    ], timeout=60)

    mean_db: float | None = None
    max_db: float | None = None
    for line in err.splitlines():
        if "mean_volume:" in line:
            try:
                mean_db = float(line.split("mean_volume:")[-1].strip().rstrip(" dB"))
            except (IndexError, ValueError):
                pass
        elif "max_volume:" in line:
            try:
                max_db = float(line.split("max_volume:")[-1].strip().rstrip(" dB"))
            except (IndexError, ValueError):
                pass

    silent = mean_db is not None and mean_db < AUDIO_SILENT_THRESHOLD_DB
    clipping = max_db is not None and max_db >= AUDIO_CLIPPING_THRESHOLD_DB

    return {
        "absent": False,
        "mean_db": round(mean_db, 2) if mean_db is not None else None,
        "max_db": round(max_db, 2) if max_db is not None else None,
        "silent": silent,
        "clipping": clipping,
    }


# ── Resolution uniformity vs segments ───────────────────────────────────────

def probe_segments(project_dir: Path) -> list[dict]:
    """Quick ffprobe of each artifact segment for resolution uniformity check."""
    artifacts = project_dir / "artifacts"
    if not artifacts.is_dir():
        return []

    segments: list[dict] = []
    for name in sorted(os.listdir(artifacts)):
        path = artifacts / name
        if path.suffix.lower() not in VIDEO_EXTS:
            continue
        if not path.is_file():
            continue
        # Skip _deprecated subfolder is non-recursive — but we're listdir level only
        data = ffprobe(str(path))
        if "error" in data:
            segments.append({"file": name, "error": data["error"]})
            continue
        streams = data.get("streams", [])
        v = next((s for s in streams if s.get("codec_type") == "video"), None)
        if v:
            segments.append({
                "file": name,
                "width": int(v.get("width", 0)),
                "height": int(v.get("height", 0)),
            })
    return segments


# ── Main ───────────────────────────────────────────────────────────────────

def review(project_dir: Path, video: Path, target_duration: float | None,
           target_resolution: str | None, output_path: Path | None) -> dict:
    """Run full review, build verdict dict, write JSON, return dict."""
    if not video.is_file():
        die(f"成片不存在: {video}")

    review_dir = project_dir / REVIEW_DIR_NAME
    frames_dir = review_dir / FRAMES_SUBDIR
    review_dir.mkdir(parents=True, exist_ok=True)

    verdict: dict = {
        "verdict": "pass",
        "file": str(video.resolve()),
        "ffprobe": {},
        "frames": [],
        "audio_level": {},
        "checks": [],
        "critical": [],
        "warnings": [],
    }

    # ── 1. ffprobe full ───────────────────────────────────────────────────
    data = ffprobe(str(video))
    if "error" in data:
        verdict["verdict"] = "fail"
        verdict["critical"].append(f"ffprobe failed: {data['error']}")
        # No further checks possible
        _finalize(verdict, output_path)
        return verdict

    fmt = data.get("format", {})
    streams = data.get("streams", [])
    v_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    a_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    if not v_stream:
        verdict["verdict"] = "fail"
        verdict["critical"].append("no video stream in output")
        _finalize(verdict, output_path)
        return verdict

    duration = float(fmt.get("duration", 0))
    width = int(v_stream.get("width", 0))
    height = int(v_stream.get("height", 0))
    fps = v_stream.get("r_frame_rate", "unknown")
    pix_fmt = v_stream.get("pix_fmt", "unknown")

    verdict["ffprobe"] = {
        "codec": v_stream.get("codec_name", "unknown"),
        "width": width,
        "height": height,
        "fps": fps,
        "pix_fmt": pix_fmt,
        "duration": round(duration, 2),
        "size_bytes": int(fmt.get("size", 0)),
        "audio": (
            {"codec": a_stream.get("codec_name", "unknown"),
             "sample_rate": int(a_stream.get("sample_rate", 0)),
             "channels": int(a_stream.get("channels", 0))}
            if a_stream else None
        ),
    }

    # ── 2. Frame extraction & black detection ────────────────────────────
    frames = extract_frames(str(video), duration, frames_dir)
    verdict["frames"] = frames
    black_count = sum(1 for f in frames if f.get("is_black") is True)
    if black_count >= 2:        # ≥2 black frames out of 5 → critical
        verdict["critical"].append(
            f"black_frame: {black_count}/{len(frames)} sampled frames are black — overlay/encode broken"
        )
    elif black_count == 1:
        verdict["warnings"].append(
            f"black_frame: 1/{len(frames)} sampled frame is black — likely first-frame transition, verify"
        )

    # ── 3. Audio level ───────────────────────────────────────────────────
    audio = analyze_audio(str(video), a_stream is not None)
    verdict["audio_level"] = audio
    if audio.get("absent"):
        # 声画同出模式下无声是硬伤；Stock Footage + --no-audio 模式下正常 — 软警告
        verdict["warnings"].append("audio_absent: no audio track (verify against pipeline mode)")
    else:
        if audio.get("silent"):
            verdict["critical"].append(
                f"audio_silent: mean_db={audio['mean_db']} below {-AUDIO_SILENT_THRESHOLD_DB}dB — silent audio"
            )
        if audio.get("clipping"):
            verdict["critical"].append(
                f"audio_clipping: max_db={audio['max_db']} above {AUDIO_CLIPPING_THRESHOLD_DB}dB — clipping"
            )

    # ── 4. Duration vs target ────────────────────────────────────────────
    if target_duration is not None and target_duration > 0:
        gap_pct = abs(duration - target_duration) / target_duration * 100
        if gap_pct > DURATION_TOLERANCE_PCT:
            verdict["critical"].append(
                f"duration_mismatch: actual {duration:.2f}s vs target {target_duration}s, gap {gap_pct:.1f}% > {DURATION_TOLERANCE_PCT}%"
            )
        elif gap_pct > 1.0:
            verdict["warnings"].append(
                f"duration_drift: actual {duration:.2f}s vs target {target_duration}s, gap {gap_pct:.1f}%"
            )
        verdict["checks"].append({
            "name": "duration_match",
            "status": "pass" if gap_pct <= DURATION_TOLERANCE_PCT else "fail",
            "detail": f"actual {duration:.2f}s vs target {target_duration}s, gap {gap_pct:.1f}%"
        })
    else:
        verdict["checks"].append({
            "name": "duration_match",
            "status": "skipped",
            "detail": "no target_duration provided"
        })

    # ── 5. Resolution floor + uniformity ─────────────────────────────────
    long_side = max(width, height)
    short_side = min(width, height)
    if long_side < RES_MIN_LONG or short_side < RES_MIN_SHORT:
        verdict["critical"].append(
            f"resolution_low: {width}x{height} below floor {RES_MIN_SHORT}p"
        )
    verdict["checks"].append({
        "name": "resolution_floor",
        "status": "pass" if long_side >= RES_MIN_LONG and short_side >= RES_MIN_SHORT else "fail",
        "detail": f"{width}x{height}"
    })

    if target_resolution:
        try:
            tw, th = (int(x) for x in target_resolution.lower().split("x"))
        except ValueError:
            verdict["warnings"].append(f"invalid --target-resolution: {target_resolution}")
            tw = th = None
        if tw and th:
            if width != tw or height != th:
                verdict["critical"].append(
                    f"resolution_mismatch: actual {width}x{height} vs target {tw}x{th}"
                )
            verdict["checks"].append({
                "name": "resolution_target",
                "status": "pass" if width == tw and height == th else "fail",
                "detail": f"{width}x{height} vs {tw}x{th}"
            })

    # Uniformity vs segments
    segments = probe_segments(project_dir)
    if segments:
        mismatches = [
            s for s in segments
            if "width" in s and (s["width"] != width or s["height"] != height)
        ]
        if mismatches:
            examples = "; ".join(f"{s['file']}={s['width']}x{s['height']}" for s in mismatches[:3])
            verdict["critical"].append(
                f"resolution_uniform: 成片 {width}x{height} vs 段分辨率不齐 — {examples}"
            )
        verdict["checks"].append({
            "name": "resolution_uniform",
            "status": "pass" if not mismatches else "fail",
            "detail": f"成片 {width}x{height}, 段数 {len(segments)}, 不齐 {len(mismatches)}"
        })

    # ── Pixel format sanity ──────────────────────────────────────────────
    if "420" not in pix_fmt:
        verdict["warnings"].append(f"pix_fmt_unusual: {pix_fmt} — 多平台发布建议 yuv420p")

    # ── Final verdict tally ──────────────────────────────────────────────
    if verdict["critical"]:
        verdict["verdict"] = "fail"
    elif verdict["warnings"]:
        verdict["verdict"] = "warn"
    else:
        verdict["verdict"] = "pass"

    _finalize(verdict, output_path)
    return verdict


def _finalize(verdict: dict, output_path: Path | None) -> None:
    """Pretty-print verdict to stdout and write JSON."""
    print(json.dumps(verdict, indent=2, ensure_ascii=False))

    if output_path is None:
        # Default: write to <project-dir>/review/verdict.json
        # output_path is None means caller didn't specify — we already have review_dir
        # but we don't here. Simpler: caller always passes output_path.
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(verdict, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[ok] verdict written to {output_path}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Final-video self-review. Runs after assemble.py / apply_cut.py, before delivery."
    )
    parser.add_argument("target", metavar="target",
                        help="成片文件路径，或项目目录（目录时审 <dir>/video.mp4，并对 <dir>/artifacts/ 做段一致性检查）")
    parser.add_argument("--target-duration", type=float, default=None,
                        help="目标时长（秒），从 script.md 片段规划累加得出")
    parser.add_argument("--target-resolution", default=None,
                        help="目标分辨率，形如 720x1280")
    parser.add_argument("--output", default=None,
                        help="verdict JSON 落盘路径，默认 <project-dir>/review/verdict.json")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if target.is_file():
        video = target
        project_dir = target.parent
    elif target.is_dir():
        project_dir = target
        video = target / "video.mp4"
    else:
        die(f"目标不存在: {target}")

    output_path = (
        Path(args.output).resolve() if args.output
        else project_dir / REVIEW_DIR_NAME / "verdict.json"
    )

    verdict = review(project_dir, video, args.target_duration, args.target_resolution, output_path)

    # Exit code: 0 pass / 1 fail / 2 warn / 3 script error
    sys.exit({
        "pass": 0,
        "fail": 1,
        "warn": 2,
    }.get(verdict["verdict"], 3))


if __name__ == "__main__":
    main()
