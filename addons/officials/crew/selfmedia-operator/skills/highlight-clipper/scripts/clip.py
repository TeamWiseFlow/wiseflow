#!/usr/bin/env python3
"""highlight-clipper — Extract highlight clips from a local video.

Flow:
  1. Extract audio via ffmpeg (16kHz mono WAV)
  2. Transcribe via SiliconFlow ASR (SenseVoiceSmall with timestamps)
  3. Score transcript segments for highlight potential
  4. Select top-N diverse highlights
  5. Clip each highlight with ffmpeg

Usage:
  python3 ./skills/highlight-clipper/scripts/clip.py <video_path> --out-dir <dir> [options]
"""

import argparse
import gc
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ASR_URL = "https://api.siliconflow.cn/v1/audio/transcriptions"
DEFAULT_ASR_MODEL = "FunAudioLLM/SenseVoiceSmall"
CHUNK_DURATION = 300  # 5 min per ASR chunk
DEFAULT_COUNT = 3
DEFAULT_BUFFER = 3.0
DEFAULT_CLIP_MIN = 15
DEFAULT_CLIP_MAX = 60
MIN_HIGHLIGHT_GAP = 30  # min seconds between highlight starts

SAFE_OUTPUT_DIRS = (Path("output_videos"), Path("tmp"))

# ── Highlight scoring keywords ──────────────────────────────────────────

EMPHASIS_WORDS = frozenset({
    "最", "极", "超", "非常", "特别", "真的", "绝对", "必须", "一定", "千万",
    "竟然", "居然", "简直", "太", "极其", "无比", "惊人", "震撼", "炸裂",
    "逆天", "离谱", "夸张", "恐怖", "神奇", "绝了", "史上", "顶级", "终极",
})
CONTRAST_WORDS = frozenset({
    "但是", "然而", "可是", "不过", "其实", "没想到", "殊不知", "结果", "原来",
})
CTA_WORDS = frozenset({
    "赶紧", "快", "别", "不要", "一定要", "记得", "收藏", "关注", "点赞",
    "转发", "下单", "链接",
})
QUESTION_MARKS = frozenset({"？", "?", "吗", "呢", "嘛", "吧", "如何", "怎么", "为什么", "为啥"})


# ── Utilities ───────────────────────────────────────────────────────────

def die(msg: str) -> None:
    print(f"[error] {msg}", file=sys.stderr)
    sys.exit(1)


def _tail_file(path: str, max_chars: int) -> str:
    """Read the last N characters of a file without loading the whole thing."""
    try:
        size = os.path.getsize(path)
        if size <= max_chars:
            with open(path, "r", errors="replace") as f:
                return f.read()
        with open(path, "rb") as f:
            f.seek(size - max_chars)
            f.readline()
            return f.read().decode(errors="replace")
    except OSError:
        return ""


def ensure_safe_output_dir(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        die("output path must be relative to the workspace")
    if ".." in path.parts:
        die("output path must not contain '..'")
    resolved = (Path.cwd() / path).resolve()
    for base in SAFE_OUTPUT_DIRS:
        base_resolved = (Path.cwd() / base).resolve()
        if resolved == base_resolved or resolved.is_relative_to(base_resolved):
            return resolved
    allowed = ", ".join(str(d) for d in SAFE_OUTPUT_DIRS)
    die(f"output path must be under one of: {allowed}")


# ── Media probing ───────────────────────────────────────────────────────

def probe_duration(filepath: str) -> float:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", filepath],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return float(data.get("format", {}).get("duration", 0))
    except (subprocess.TimeoutExpired, json.JSONDecodeError, ValueError):
        pass
    return 0.0


# ── Audio extraction ────────────────────────────────────────────────────

def extract_audio_chunk(video_path: str, output_path: str,
                        start: float = 0, duration: float | None = None) -> str:
    cmd = ["ffmpeg", "-y"]
    if start > 0:
        cmd.extend(["-ss", str(start)])
    cmd.extend(["-i", video_path, "-vn", "-ar", "16000", "-ac", "1", "-f", "wav"])
    if duration is not None:
        cmd.extend(["-t", str(duration)])
    cmd.append(output_path)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as stderr_f:
        stderr_path = stderr_f.name
    try:
        with open(stderr_path, "w") as stderr_fh:
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=stderr_fh, text=True, timeout=120)
        if result.returncode != 0:
            tail = _tail_file(stderr_path, 500)
            die(f"Audio extraction failed: {tail}")
    finally:
        try:
            os.unlink(stderr_path)
        except OSError:
            pass
    if not os.path.exists(output_path):
        die(f"Audio file not created: {output_path}")
    return output_path


# ── ASR ─────────────────────────────────────────────────────────────────

def build_multipart_formdata(file_path: str, fields: dict[str, str]) -> tuple[bytes, str]:
    boundary = f"----HLClipper{uuid.uuid4().hex}"
    filename = os.path.basename(file_path)
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    parts: list[bytes] = []
    parts.append(
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode("utf-8")
    )
    with open(file_path, "rb") as f:
        parts.append(f.read())
    parts.append(b"\r\n")
    for name, value in fields.items():
        parts.append(
            (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
                f"{value}\r\n"
            ).encode("utf-8")
        )
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def call_asr(audio_path: str) -> dict:
    api_key = os.environ.get("SILICONFLOW_API_KEY", "").strip()
    if not api_key:
        die("SILICONFLOW_API_KEY not set")
    model = os.environ.get("ASR_MODEL", DEFAULT_ASR_MODEL).strip() or DEFAULT_ASR_MODEL
    body, content_type = build_multipart_formdata(audio_path, {"model": model})
    req = urllib.request.Request(ASR_URL, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode(errors="replace")
        die(f"ASR API failed (HTTP {e.code}): {err_body}")
    except urllib.error.URLError as e:
        die(f"ASR request failed: {e.reason}")


def estimate_segments(text: str, duration: float, offset: float = 0) -> list[dict]:
    """Estimate segment timestamps when ASR doesn't return them."""
    sentences = re.split(r"[。！？!?；;\n]", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return []
    total_chars = sum(len(s) for s in sentences)
    if total_chars == 0:
        return []
    segments = []
    current_time = offset
    for s in sentences:
        seg_duration = (len(s) / total_chars) * duration
        segments.append({
            "start": round(current_time, 2),
            "end": round(current_time + seg_duration, 2),
            "text": s,
        })
        current_time += seg_duration
    return segments


def transcribe_video(video_path: str, tmp_dir: str, video_duration: float) -> tuple[str, list[dict]]:
    """Transcribe video audio, chunking long videos automatically."""
    all_segments: list[dict] = []
    all_text_parts: list[str] = []

    if video_duration <= CHUNK_DURATION:
        audio_path = os.path.join(tmp_dir, "audio.wav")
        extract_audio_chunk(video_path, audio_path)
        result = call_asr(audio_path)
        segments = result.get("segments", [])
        text = result.get("text", "")
        if segments:
            all_segments.extend(segments)
        elif text:
            all_segments.extend(estimate_segments(text, video_duration))
        all_text_parts.append(text)
    else:
        offset = 0.0
        chunk_idx = 0
        while offset < video_duration:
            chunk_idx += 1
            audio_path = os.path.join(tmp_dir, f"audio_{chunk_idx}.wav")
            chunk_dur = min(CHUNK_DURATION, video_duration - offset)
            extract_audio_chunk(video_path, audio_path, start=offset, duration=chunk_dur)
            result = call_asr(audio_path)
            segments = result.get("segments", [])
            text = result.get("text", "")
            if segments:
                for seg in segments:
                    all_segments.append({
                        "start": seg.get("start", 0) + offset,
                        "end": seg.get("end", 0) + offset,
                        "text": seg.get("text", ""),
                    })
            elif text:
                all_segments.extend(estimate_segments(text, chunk_dur, offset))
            all_text_parts.append(text)
            offset += CHUNK_DURATION

    return " ".join(all_text_parts), all_segments


# ── Highlight scoring ───────────────────────────────────────────────────

def score_segment(text: str) -> float:
    if not text or not text.strip():
        return 0.0
    score = 0.0
    for w in EMPHASIS_WORDS:
        if w in text:
            score += 2.0
    for w in CONTRAST_WORDS:
        if w in text:
            score += 3.0
    for w in CTA_WORDS:
        if w in text:
            score += 2.5
    for m in QUESTION_MARKS:
        if m in text:
            score += 1.5
    score += min(len(re.findall(r"\d+\.?\d*%?", text)), 3) * 1.0
    score += (text.count("!") + text.count("！")) * 1.5
    score += min(len(text.strip()) / 20, 3.0)
    return score


def select_highlights(segments: list[dict], count: int) -> list[dict]:
    if not segments:
        return []
    valid = [s for s in segments if s.get("end", 0) - s.get("start", 0) >= 1.0]
    if not valid:
        valid = segments
    scored = [{**s, "highlight_score": score_segment(s.get("text", ""))} for s in valid]
    scored.sort(key=lambda s: s["highlight_score"], reverse=True)
    selected = []
    for seg in scored:
        if len(selected) >= count:
            break
        start = seg.get("start", 0)
        if not any(abs(start - s.get("start", 0)) < MIN_HIGHLIGHT_GAP for s in selected):
            selected.append(seg)
    if len(selected) < count:
        remaining = [s for s in scored if s not in selected]
        for seg in remaining:
            if len(selected) >= count:
                break
            selected.append(seg)
    selected.sort(key=lambda s: s.get("start", 0))
    return selected


# ── Video clipping ──────────────────────────────────────────────────────

def determine_clip_bounds(seg: dict, video_duration: float,
                          buffer: float, clip_min: float, clip_max: float) -> tuple[float, float]:
    seg_start = seg.get("start", 0)
    seg_end = seg.get("end", 0)
    seg_duration = seg_end - seg_start
    target = max(seg_duration + buffer * 2, clip_min)
    target = min(target, clip_max)
    clip_start = max(seg_start - buffer, 0)
    clip_end = min(clip_start + target, video_duration)
    if clip_end - clip_start < clip_min:
        clip_start = max(clip_end - target, 0)
    return round(clip_start, 2), round(clip_end, 2)


def clip_video(video_path: str, start: float, end: float, output_path: str) -> None:
    duration = end - start
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start), "-i", video_path, "-t", str(duration),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        output_path,
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as stderr_f:
        stderr_path = stderr_f.name
    try:
        with open(stderr_path, "w") as stderr_fh:
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=stderr_fh, text=True, timeout=120)
        if result.returncode != 0:
            tail = _tail_file(stderr_path, 500)
            die(f"ffmpeg clip failed: {tail}")
    finally:
        try:
            os.unlink(stderr_path)
        except OSError:
            pass
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        die(f"Clip output missing or empty: {output_path}")
    gc.collect()


# ── Main ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Extract highlight clips from a local video")
    parser.add_argument("video_path", help="Path to the source video file")
    parser.add_argument("--out-dir", required=True, dest="out_dir",
                        help="Output directory under output_videos/ or tmp/")
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT,
                        help=f"Number of highlights (default: {DEFAULT_COUNT})")
    parser.add_argument("--min-duration", type=float, default=DEFAULT_CLIP_MIN, dest="min_duration",
                        help=f"Minimum clip duration seconds (default: {DEFAULT_CLIP_MIN})")
    parser.add_argument("--max-duration", type=float, default=DEFAULT_CLIP_MAX, dest="max_duration",
                        help=f"Maximum clip duration seconds (default: {DEFAULT_CLIP_MAX})")
    parser.add_argument("--buffer", type=float, default=DEFAULT_BUFFER,
                        help=f"Buffer seconds before/after segment (default: {DEFAULT_BUFFER})")
    args = parser.parse_args()

    if not os.path.isfile(args.video_path):
        die(f"Video file not found: {args.video_path}")

    out_dir = ensure_safe_output_dir(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    video_duration = probe_duration(args.video_path)
    if video_duration <= 0:
        die(f"Cannot determine video duration: {args.video_path}")
    print(f"[info] Video duration: {video_duration:.2f}s")

    tmp_dir = str(out_dir / "_tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    try:
        print("[info] Extracting audio & transcribing...")
        full_text, segments = transcribe_video(args.video_path, tmp_dir, video_duration)

        if not segments:
            die("ASR returned no segments — cannot identify highlights")

        print(f"[info] Transcribed {len(segments)} segments")

        print("[info] Selecting highlights...")
        highlights = select_highlights(segments, args.count)

        if not highlights:
            die("No suitable highlights found")

        print(f"[info] Selected {len(highlights)} highlights")

        highlights_info = []
        for i, hl in enumerate(highlights, 1):
            clip_start, clip_end = determine_clip_bounds(
                hl, video_duration, args.buffer, args.min_duration, args.max_duration,
            )
            clip_filename = f"highlight_{i:02d}.mp4"
            clip_path = str(out_dir / clip_filename)

            print(f"[info] Clipping highlight {i}/{len(highlights)}: {clip_start:.1f}s – {clip_end:.1f}s")
            clip_video(args.video_path, clip_start, clip_end, clip_path)

            clip_duration = probe_duration(clip_path)
            clip_size = os.path.getsize(clip_path) / (1024 * 1024)

            highlights_info.append({
                "index": i,
                "file": clip_filename,
                "start": clip_start,
                "end": clip_end,
                "duration": round(clip_duration, 2),
                "size_mb": round(clip_size, 2),
                "text": hl.get("text", ""),
                "score": round(hl.get("highlight_score", 0), 2),
            })

        report = {
            "source_video": os.path.basename(args.video_path),
            "video_duration": round(video_duration, 2),
            "highlight_count": len(highlights_info),
            "full_transcript": full_text,
            "highlights": highlights_info,
        }
        report_path = str(out_dir / "highlights.json")
        Path(report_path).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8",
        )

        print(f"[done] {len(highlights_info)} highlights saved to: {out_dir}")
        for hl in highlights_info:
            text_preview = hl["text"][:50] + "..." if len(hl["text"]) > 50 else hl["text"]
            print(f"  #{hl['index']}: {hl['start']:.1f}s–{hl['end']:.1f}s ({hl['duration']:.1f}s) — {text_preview}")

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
