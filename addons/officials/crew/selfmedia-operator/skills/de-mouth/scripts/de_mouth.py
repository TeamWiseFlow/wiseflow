#!/usr/bin/env python3
"""de-mouth — Remove filler words, silences, and speech errors from talking-head videos.

Pipeline:
  1. Extract audio via ffmpeg
  2. Transcribe via ASR (Volcengine with word-level timestamps, or SiliconFlow fallback)
  3. Detect speech errors (script-based: silences, fillers, stutters)
  4. Output analysis files for AI semantic analysis (repetitions, corrections, incomplete sentences)
  5. Apply delete list and cut video via ffmpeg filter_complex
  6. Optionally: 2-pass HD re-encode, SRT subtitles, JianYing draft directory

Usage:
  python3 ./skills/de-mouth/scripts/de_mouth.py <video_path> --out-dir <dir> [options]
"""

import argparse
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

# ── Constants ────────────────────────────────────────────────────────────────

ASR_VOLCENGINE_URL_SUBMIT = "https://openspeech.bytedance.com/api/v1/vc/submit"
ASR_VOLCENGINE_URL_QUERY = "https://openspeech.bytedance.com/api/v1/vc/query"
ASR_SILICONFLOW_URL = "https://api.siliconflow.cn/v1/audio/transcriptions"
UPLOAD_URL = "https://uguu.se/upload"

DEFAULT_SILENCE_THRESHOLD = 0.3  # seconds
DEFAULT_KEEP_FILLERS = ""  # comma-separated filler words to preserve
FILLER_WORDS = frozenset("嗯啊哎诶呃额唉哦噢呀欸")
STUTTER_PATTERNS = ["那个那个", "就是就是", "然后然后", "这个这个", "所以所以"]
CONTINUOUS_FILLER_PAIRS = True  # detect consecutive filler pairs (嗯啊, 啊呃)

SAFE_OUTPUT_DIRS = (Path("output_videos"), Path("tmp"))

# ── Utilities ────────────────────────────────────────────────────────────────

def die(msg: str) -> None:
    print(f"[error] {msg}", file=sys.stderr)
    sys.exit(1)


def log(tag: str, msg: str) -> None:
    print(f"[{tag}] {msg}")


def run_cmd(cmd: list[str], timeout: int = 120, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command, capturing output. Returns CompletedProcess."""
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        if check:
            die(f"Command timed out: {' '.join(cmd[:3])}...")
        raise


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


# ── Step 1: Audio extraction ────────────────────────────────────────────────

def extract_audio(video_path: str, output_path: str) -> str:
    """Extract audio as MP3 from video."""
    cmd = ["ffmpeg", "-y", "-i", video_path, "-vn", "-acodec", "libmp3lame", output_path]
    result = run_cmd(cmd, timeout=180)
    if result.returncode != 0:
        die(f"Audio extraction failed: {result.stderr[-500:]}")
    if not os.path.exists(output_path):
        die(f"Audio file not created: {output_path}")
    log("audio", f"Extracted {os.path.getsize(output_path) / 1024 / 1024:.1f}MB MP3")
    return output_path


# ── Step 2a: Upload audio to get public URL ─────────────────────────────────

def upload_audio(audio_path: str) -> str:
    """Upload audio to uguu.se and return public URL."""
    cmd = ["curl", "-s", "-F", f"files[]=@{audio_path}", UPLOAD_URL]
    result = run_cmd(cmd, timeout=120)
    if result.returncode != 0:
        die(f"Upload failed: {result.stderr}")
    try:
        resp = json.loads(result.stdout)
        url = resp["files"][0]["url"]
        log("upload", f"Audio uploaded: {url}")
        return url
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        die(f"Upload response parse failed: {result.stdout[:200]}")


# ── Step 2b: ASR — Volcengine (word-level timestamps) ───────────────────────

def transcribe_volcengine(audio_url: str, api_key: str, hot_words: list[str] | None = None) -> dict:
    """Transcribe via Volcengine OpenSpeech API (async submit + poll)."""
    # Build request body
    body = {"url": audio_url}
    if hot_words:
        body["hot_words"] = hot_words

    # Submit task
    submit_body = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{ASR_VOLCENGINE_URL_SUBMIT}?language=zh-CN&use_itn=True&use_capitalize=True&max_lines=1&words_per_line=15",
        data=submit_body,
        method="POST",
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("x-api-key", api_key)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            submit_result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        die(f"Volcengine submit failed (HTTP {e.code}): {e.read().decode(errors='replace')[:300]}")

    task_id = submit_result.get("id")
    if not task_id:
        die(f"Volcengine submit returned no task ID: {json.dumps(submit_result)[:200]}")

    log("asr", f"Volcengine task submitted: {task_id}")

    # Poll for result
    max_attempts = 120  # 10 min at 5s intervals
    for attempt in range(max_attempts):
        time.sleep(5)
        query_req = urllib.request.Request(
            f"{ASR_VOLCENGINE_URL_QUERY}?id={task_id}",
            method="GET",
        )
        query_req.add_header("x-api-key", api_key)

        try:
            with urllib.request.urlopen(query_req, timeout=30) as resp:
                query_result = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            die(f"Volcengine query failed (HTTP {e.code})")

        code = query_result.get("code", -1)
        if code == 0:
            utterances = query_result.get("utterances", [])
            log("asr", f"Volcengine transcription complete: {len(utterances)} utterances")
            return query_result
        elif code == 1000:
            if attempt % 6 == 5:  # log every 30s
                log("asr", f"Still processing... ({attempt * 5}s)")
        else:
            die(f"Volcengine transcription failed (code={code})")

    die("Volcengine transcription timed out (10 min)")


# ── Step 2c: ASR — SiliconFlow (text only, no timestamps) ──────────────────

def build_multipart_formdata(file_path: str, fields: dict[str, str]) -> tuple[bytes, str]:
    boundary = f"----DeMouth{uuid.uuid4().hex}"
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


def transcribe_siliconflow(audio_path: str, api_key: str) -> dict:
    """Transcribe via SiliconFlow API (OpenAI-compatible, text only)."""
    model = os.environ.get("ASR_MODEL", "FunAudioLLM/SenseVoiceSmall")
    body, content_type = build_multipart_formdata(audio_path, {"model": model})
    req = urllib.request.Request(ASR_SILICONFLOW_URL, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", content_type)

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode(errors="replace")
        die(f"SiliconFlow ASR failed (HTTP {e.code}): {err_body[:300]}")

    text = result.get("text", "")
    log("asr", f"SiliconFlow transcription complete: {len(text)} chars")
    return result


# ── Step 2d: Unified ASR dispatch ───────────────────────────────────────────

def detect_asr_mode() -> str:
    """Detect which ASR to use based on available API keys."""
    if os.environ.get("VOLCENGINE_API_KEY", "").strip():
        return "volcengine"
    if os.environ.get("SILICONFLOW_API_KEY", "").strip():
        return "siliconflow"
    die("No ASR API key found. Set VOLCENGINE_API_KEY (recommended) or SILICONFLOW_API_KEY")


def run_asr(audio_path: str, hot_words: list[str] | None = None) -> tuple[str, dict]:
    """Run ASR and return (mode, raw_result)."""
    mode = detect_asr_mode()
    if mode == "volcengine":
        api_key = os.environ["VOLCENGINE_API_KEY"].strip()
        audio_url = upload_audio(audio_path)
        result = transcribe_volcengine(audio_url, api_key, hot_words)
        return "volcengine", result
    else:
        api_key = os.environ["SILICONFLOW_API_KEY"].strip()
        result = transcribe_siliconflow(audio_path, api_key)
        return "siliconflow", result


# ── Step 3: Generate subtitles_words.json from ASR result ───────────────────

def volcengine_to_words(result: dict) -> list[dict]:
    """Convert Volcengine result to subtitles_words.json format."""
    all_words = []
    for utterance in result.get("utterances", []):
        for word in utterance.get("words", []):
            all_words.append({
                "text": word["text"],
                "start": word["start_time"] / 1000,
                "end": word["end_time"] / 1000,
                "isGap": False,
            })
    return insert_gaps(all_words)


def siliconflow_to_words(result: dict, audio_path: str) -> list[dict]:
    """Convert SiliconFlow text result to estimated subtitles_words.json format.

    Since SiliconFlow doesn't provide timestamps, we estimate based on
    character distribution across audio duration.
    """
    text = result.get("text", "")
    if not text:
        die("SiliconFlow returned empty text")

    # Get audio duration
    probe = run_cmd(["ffprobe", "-v", "quiet", "-print_format", "json",
                     "-show_format", audio_path], timeout=15)
    try:
        duration = float(json.loads(probe.stdout)["format"]["duration"])
    except (json.JSONDecodeError, KeyError, ValueError):
        die("Cannot determine audio duration for timestamp estimation")

    # Split into sentences and distribute across duration
    sentences = re.split(r"([。！？；\n])", text)
    chunks = []
    current = ""
    for part in sentences:
        current += part
        if part in "。！？；\n" and current.strip():
            chunks.append(current.strip())
            current = ""
    if current.strip():
        chunks.append(current.strip())

    if not chunks:
        chunks = [text]

    total_chars = sum(len(c) for c in chunks)
    all_words = []
    cursor = 0.0

    for chunk in chunks:
        chunk_chars = len(chunk)
        chunk_duration = (chunk_chars / total_chars) * duration if total_chars > 0 else 0
        char_duration = chunk_duration / chunk_chars if chunk_chars > 0 else 0

        for char in chunk:
            if char.strip():  # skip whitespace
                all_words.append({
                    "text": char,
                    "start": round(cursor, 3),
                    "end": round(cursor + char_duration, 3),
                    "isGap": False,
                })
            cursor += char_duration

    return insert_gaps(all_words)


def insert_gaps(words: list[dict]) -> list[dict]:
    """Insert isGap entries between words where silence exists."""
    result = []
    last_end = 0.0

    for word in words:
        gap_duration = word["start"] - last_end
        if gap_duration > 0.1:
            if gap_duration > 0.5:
                # Split long gaps into 1s chunks
                gap_start = last_end
                while gap_start < word["start"]:
                    gap_end = min(gap_start + 1.0, word["start"])
                    result.append({
                        "text": "",
                        "start": round(gap_start, 3),
                        "end": round(gap_end, 3),
                        "isGap": True,
                    })
                    gap_start = gap_end
            else:
                result.append({
                    "text": "",
                    "start": round(last_end, 3),
                    "end": round(word["start"], 3),
                    "isGap": True,
                })
        result.append(word)
        last_end = word["end"]

    return result


# ── Step 4: Script-based deterministic detection ────────────────────────────

def detect_silences(words: list[dict], threshold: float) -> list[int]:
    """Detect silences >= threshold. Returns indices to delete."""
    indices = []
    for i, w in enumerate(words):
        if w.get("isGap") and (w["end"] - w["start"]) >= threshold:
            indices.append(i)
    return indices


def detect_filler_words(words: list[dict], keep: set[str]) -> list[int]:
    """Detect standalone filler words. Returns indices to delete."""
    indices = []
    for i, w in enumerate(words):
        if not w.get("isGap") and w["text"] in FILLER_WORDS and w["text"] not in keep:
            indices.append(i)
    return indices


def detect_stutters(words: list[dict]) -> list[int]:
    """Detect stutter patterns (那个那个, 就是就是, etc.). Returns indices to delete.

    Strategy: delete the first occurrence, keep the last.
    """
    indices = []
    # Build full text with indices
    indexed_text = []
    for i, w in enumerate(words):
        if not w.get("isGap"):
            indexed_text.append((i, w["text"]))

    # Join text for pattern matching
    full_text = "".join(t for _, t in indexed_text)
    idx_map = [i for i, _ in indexed_text]

    for pattern in STUTTER_PATTERNS:
        half = pattern[:len(pattern)//2]
        pos = 0
        while True:
            idx = full_text.find(pattern, pos)
            if idx == -1:
                break
            # Delete the first half of the stutter
            half_len = len(half)
            for j in range(half_len):
                if idx + j < len(idx_map):
                    indices.append(idx_map[idx + j])
            pos = idx + len(pattern)

    return indices


def detect_continuous_fillers(words: list[dict], keep: set[str]) -> list[int]:
    """Detect consecutive filler word pairs (嗯啊, 啊呃). Delete both."""
    indices = []
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i + 1]
        if (not w1.get("isGap") and not w2.get("isGap")
                and w1["text"] in FILLER_WORDS and w2["text"] in FILLER_WORDS
                and w1["text"] not in keep and w2["text"] not in keep):
            indices.append(i)
            indices.append(i + 1)
    return indices


# ── Step 5: Generate analysis files for AI semantic analysis ────────────────

def generate_readable(words: list[dict], output_path: str) -> None:
    """Generate readable.txt for AI analysis."""
    lines = []
    for i, w in enumerate(words):
        if w.get("isGap"):
            dur = (w["end"] - w["start"])
            if dur >= 0.2:
                lines.append(f"{i}|[静{dur:.2f}s]|{w['start']:.2f}-{w['end']:.2f}")
        else:
            lines.append(f"{i}|{w['text']}|{w['start']:.2f}-{w['end']:.2f}")
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")


def generate_sentences(words: list[dict], output_path: str) -> None:
    """Generate sentences.txt — split by silences >= 0.5s."""
    sentences = []
    curr = {"text": "", "startIdx": -1, "endIdx": -1}

    for i, w in enumerate(words):
        is_long_gap = w.get("isGap") and (w["end"] - w["start"]) >= 0.5
        if is_long_gap:
            if curr["text"]:
                sentences.append(curr)
            curr = {"text": "", "startIdx": -1, "endIdx": -1}
        elif not w.get("isGap"):
            if curr["startIdx"] == -1:
                curr["startIdx"] = i
            curr["text"] += w["text"]
            curr["endIdx"] = i

    if curr["text"]:
        sentences.append(curr)

    lines = []
    for i, s in enumerate(sentences):
        lines.append(f"{i}|{s['startIdx']}-{s['endIdx']}|{s['text']}")
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")
    return sentences


# ── Step 6: FFmpeg precise cutting ──────────────────────────────────────────

def probe_video(filepath: str) -> dict:
    """Probe video parameters."""
    result = run_cmd(["ffprobe", "-v", "quiet", "-print_format", "json",
                      "-show_format", "-show_streams", filepath], timeout=15)
    if result.returncode != 0:
        die(f"ffprobe failed: {result.stderr}")

    data = json.loads(result.stdout)
    video_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    if not video_stream:
        die("No video stream found")

    format_info = data.get("format", {})
    duration = float(format_info.get("duration", 0))

    bitrate = int(video_stream.get("bit_rate", 0))
    if bitrate == 0:
        bitrate = int(format_info.get("bit_rate", 0))

    profile = video_stream.get("profile", "high")
    pix_fmt = video_stream.get("pix_fmt", "yuv420p")

    return {
        "duration": duration,
        "bitrate": bitrate,
        "profile": profile,
        "pix_fmt": pix_fmt,
    }


def delete_indices_to_segments(words: list[dict], delete_indices: list[int]) -> list[dict]:
    """Convert delete indices to time segments.

    For each deleted word, expand to include adjacent gaps.
    Then merge overlapping/adjacent segments.
    """
    if not delete_indices:
        return []

    # Mark all indices to delete, expanding to include adjacent gaps
    delete_set = set(delete_indices)

    # Expand: if a word is deleted, also delete any gap between it and adjacent deleted words
    sorted_indices = sorted(delete_set)
    expanded = set(sorted_indices)

    # Merge contiguous ranges and convert to time segments
    segments = []
    idx_list = sorted(expanded)

    i = 0
    while i < len(idx_list):
        start_idx = idx_list[i]
        end_idx = idx_list[i]

        # Extend range while contiguous or with gaps in between
        j = i + 1
        while j < len(idx_list):
            # Check if there are only gaps between end_idx and idx_list[j]
            gap_only = True
            for k in range(end_idx + 1, idx_list[j]):
                if k < len(words) and not words[k].get("isGap"):
                    gap_only = False
                    break
            if gap_only and idx_list[j] - end_idx <= 3:  # allow up to 2 gaps between
                end_idx = idx_list[j]
                j += 1
            else:
                break

        start_time = words[start_idx]["start"]
        end_time = words[end_idx]["end"]
        segments.append({"start": round(start_time, 3), "end": round(end_time, 3)})
        i = j

    # Merge overlapping segments
    segments.sort(key=lambda s: s["start"])
    merged = []
    for seg in segments:
        if merged and seg["start"] <= merged[-1]["end"] + 0.2:  # 200ms merge gap
            merged[-1]["end"] = max(merged[-1]["end"], seg["end"])
        else:
            merged.append({"start": seg["start"], "end": seg["end"]})

    return merged


def cut_video(input_path: str, delete_segments: list[dict], output_path: str) -> None:
    """Cut video using ffmpeg -ss/-to per segment + concat demuxer.

    This avoids trim filter grey frame issues and provides frame-accurate cutting.
    """
    if not delete_segments:
        # No deletions, just copy
        shutil.copy2(input_path, output_path)
        log("cut", "No segments to delete, copied original")
        return

    info = probe_video(input_path)
    duration = info["duration"]
    bitrate_k = info["bitrate"] // 1000
    profile = info["profile"].lower()
    pix_fmt = info["pix_fmt"]

    # Map profile
    x264_profile = "high"
    if profile == "main":
        x264_profile = "main"
    elif profile == "baseline":
        x264_profile = "baseline"

    maxrate_k = bitrate_k * 13 // 10
    bufsize_k = bitrate_k * 2

    # Calculate keep segments
    keep_segs = []
    cursor = 0.0
    for seg in delete_segments:
        if seg["start"] > cursor:
            keep_segs.append({"start": cursor, "end": seg["start"]})
        cursor = seg["end"]
    if cursor < duration:
        keep_segs.append({"start": cursor, "end": duration})

    if not keep_segs:
        die("All segments would be deleted")

    log("cut", f"Keeping {len(keep_segs)} segments, deleting {len(delete_segments)} segments")

    # Calculate deleted time
    deleted_time = sum(s["end"] - s["start"] for s in delete_segments)
    log("cut", f"Deleting {deleted_time:.2f}s of {duration:.2f}s ({deleted_time/duration*100:.1f}%)")

    # Use filter_complex for precise cutting
    filters = []
    vconcat = ""

    for i, seg in enumerate(keep_segs):
        filters.append(
            f"[0:v]trim=start={seg['start']:.3f}:end={seg['end']:.3f},setpts=PTS-STARTPTS[v{i}]"
        )
        filters.append(
            f"[0:a]atrim=start={seg['start']:.3f}:end={seg['end']:.3f},asetpts=PTS-STARTPTS[a{i}]"
        )
        vconcat += f"[v{i}]"

    filters.append(f"{vconcat}concat=n={len(keep_segs)}:v=1:a=0[outv]")

    # Audio: simple concat (no crossfade for speed)
    aconcat = "".join(f"[a{i}]" for i in range(len(keep_segs)))
    filters.append(f"{aconcat}concat=n={len(keep_segs)}:v=0:a=1[outa]")

    filter_complex = ";".join(filters)

    cmd = [
        "ffmpeg", "-y", "-v", "error", "-stats",
        "-i", input_path,
        "-filter_complex", filter_complex,
        "-map", "[outv]", "-map", "[outa]",
        "-c:v", "libx264", f"-profile:v", x264_profile,
        f"-b:v", f"{bitrate_k}k", f"-maxrate", f"{maxrate_k}k", f"-bufsize", f"{bufsize_k}k",
        "-pix_fmt", pix_fmt,
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        output_path,
    ]

    result = run_cmd(cmd, timeout=600)
    if result.returncode != 0:
        # Fallback: segment-by-segment cutting
        log("cut", "filter_complex failed, falling back to segment extraction...")
        _cut_video_fallback(input_path, keep_segs, output_path, x264_profile, bitrate_k, maxrate_k, bufsize_k, pix_fmt)
    else:
        log("cut", f"Output: {output_path}")


def _cut_video_fallback(input_path: str, keep_segs: list[dict], output_path: str,
                        profile: str, bitrate_k: int, maxrate_k: int, bufsize_k: int,
                        pix_fmt: str) -> None:
    """Fallback: extract each segment with -ss/-to, then concat."""
    tmp_dir = tempfile.mkdtemp(prefix="de_mouth_")
    try:
        part_files = []
        for i, seg in enumerate(keep_segs):
            part_file = os.path.join(tmp_dir, f"part{i:04d}.mp4")
            seg_duration = seg["end"] - seg["start"]
            cmd = [
                "ffmpeg", "-y",
                "-ss", f"{seg['start']:.3f}", "-i", input_path,
                "-t", f"{seg_duration:.3f}",
                "-c:v", "libx264", f"-profile:v", profile,
                f"-b:v", f"{bitrate_k}k", f"-maxrate", f"{maxrate_k}k", f"-bufsize", f"{bufsize_k}k",
                "-pix_fmt", pix_fmt,
                "-c:a", "aac", "-b:a", "192k",
                "-avoid_negative_ts", "make_zero",
                part_file,
            ]
            result = run_cmd(cmd, timeout=120)
            if result.returncode != 0:
                die(f"Segment {i} extraction failed: {result.stderr[-300:]}")
            part_files.append(part_file)

        # Concat
        list_file = os.path.join(tmp_dir, "concat.txt")
        list_content = "\n".join(f"file '{os.path.abspath(f)}'" for f in part_files)
        Path(list_file).write_text(list_content)

        cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-f", "concat", "-safe", "0", "-i", list_file,
            "-c", "copy", "-movflags", "+faststart",
            output_path,
        ]
        result = run_cmd(cmd, timeout=120)
        if result.returncode != 0:
            die(f"Concat failed: {result.stderr[-300:]}")

        log("cut", f"Output (fallback): {output_path}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ── Step 7: HD re-encode (2-pass) ───────────────────────────────────────────

def hd_reencode(input_path: str, output_path: str, multiplier: float = 1.2) -> None:
    """2-pass encode with sharpening, matching or exceeding original quality."""
    info = probe_video(input_path)
    bitrate_k = info["bitrate"] // 1000
    target_k = int(bitrate_k * multiplier)
    maxrate_k = target_k * 13 // 10
    bufsize_k = target_k * 2
    profile = info["profile"].lower()
    pix_fmt = info["pix_fmt"]

    x264_profile = "high"
    if profile == "main":
        x264_profile = "main"
    elif profile == "baseline":
        x264_profile = "baseline"

    passlog = tempfile.mktemp(prefix="ffmpeg2pass_")
    try:
        # Pass 1
        cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-i", input_path,
            "-vf", "unsharp=5:5:0.3:5:5:0.3",
            "-c:v", "libx264", f"-profile:v", x264_profile,
            f"-b:v", f"{target_k}k", "-preset", "slow",
            "-pix_fmt", pix_fmt,
            "-pass", "1", "-passlogfile", passlog,
            "-an", "-f", "null", "/dev/null",
        ]
        result = run_cmd(cmd, timeout=600)
        if result.returncode != 0:
            die(f"HD Pass 1 failed: {result.stderr[-300:]}")

        # Pass 2
        cmd = [
            "ffmpeg", "-y", "-v", "error", "-stats",
            "-i", input_path,
            "-vf", "unsharp=5:5:0.3:5:5:0.3",
            "-c:v", "libx264", f"-profile:v", x264_profile,
            f"-b:v", f"{target_k}k", f"-maxrate", f"{maxrate_k}k", f"-bufsize", f"{bufsize_k}k",
            "-preset", "slow",
            "-pix_fmt", pix_fmt,
            "-pass", "2", "-passlogfile", passlog,
            "-c:a", "copy",
            "-movflags", "+faststart",
            output_path,
        ]
        result = run_cmd(cmd, timeout=600)
        if result.returncode != 0:
            die(f"HD Pass 2 failed: {result.stderr[-300:]}")

        log("hd", f"HD output: {output_path} ({bitrate_k}kbps → {target_k}kbps)")
    finally:
        for ext in ("", ".log", ".log.mbtree"):
            try:
                os.unlink(f"{passlog}{ext}")
            except OSError:
                pass


# ── Step 8: SRT subtitle generation ─────────────────────────────────────────

def generate_srt(words: list[dict], delete_indices: set[int], output_path: str) -> None:
    """Generate SRT subtitle file from words, excluding deleted indices."""
    def to_srt_time(sec: float) -> str:
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        ms = int(round((sec % 1) * 1000))
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    # Group words into subtitle lines (by sentence boundaries)
    lines = []
    current_words = []
    sentence_end_re = re.compile(r"[。！？!?；]")

    for i, w in enumerate(words):
        if i in delete_indices:
            continue
        if w.get("isGap"):
            if current_words:
                gap_dur = w["end"] - w["start"]
                if gap_dur >= 0.3:  # sentence break at 0.3s+ silence
                    lines.append(current_words)
                    current_words = []
            continue

        current_words.append(w)
        if sentence_end_re.search(w["text"]):
            lines.append(current_words)
            current_words = []

    if current_words:
        lines.append(current_words)

    # Write SRT
    srt_content = []
    for idx, line_words in enumerate(lines, 1):
        text = "".join(w["text"] for w in line_words).strip()
        if not text:
            continue
        # Remove trailing punctuation for cleaner subtitles
        text = re.sub(r"[。！？!?；]+$", "", text)
        start = to_srt_time(line_words[0]["start"])
        end = to_srt_time(line_words[-1]["end"])
        srt_content.append(f"{idx}\n{start} --> {end}\n{text}\n")

    Path(output_path).write_text("\n".join(srt_content), encoding="utf-8")
    log("srt", f"Generated {len(srt_content)} subtitle lines")


# ── Step 9: JianYing draft generation ───────────────────────────────────────

def generate_jianying_draft(srt_path: str, output_dir: str, name: str = "字幕草稿",
                           width: int = 1440, height: int = 1080,
                           font_size: int = 7, text_color: str = "#FFDE00",
                           border_color: str = "#000000") -> None:
    """Generate JianYing draft directory (draft_content.json + draft_info.json).

    Users can copy this directory to ~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft/
    and restart JianYing to import.

    This is a simplified implementation based on capcut-mate's reverse-engineered schema.
    Only covers basic subtitles without effects/animations.
    """
    draft_id = uuid.uuid4().hex[:16]
    draft_dir = os.path.join(output_dir, f"{name}-{draft_id[-8:]}")
    os.makedirs(draft_dir, exist_ok=True)

    # Parse SRT
    srt_text = Path(srt_path).read_text(encoding="utf-8")
    blocks = re.split(r"\n\n+", srt_text.strip())
    captions = []
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        m = re.match(
            r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)",
            lines[1]
        )
        if not m:
            continue

        def to_us(h, mi, s, ms):
            return (int(h) * 3600 + int(mi) * 60 + int(s)) * 1_000_000 + int(ms) * 1000

        start_us = to_us(*m.groups()[:4])
        end_us = to_us(*m.groups()[4:])
        text = "\n".join(lines[2:])
        captions.append({"start": start_us, "end": end_us, "text": text})

    if not captions:
        log("draft", "No captions to generate draft")
        return

    # Generate minimal draft_content.json
    # This is a simplified version — enough for JianYing to load subtitles
    total_duration_us = captions[-1]["end"] if captions else 10_000_000

    # Build tracks
    text_materials = {}
    text_tracks = []

    for i, cap in enumerate(captions):
        mat_id = uuid.uuid4().hex
        text_materials[mat_id] = {
            "type": "text",
            "content": cap["text"],
            "font_size": font_size,
            "font_color": text_color,
            "border_color": border_color,
            "border_width": 40,
            "bold": True,
            "has_shadow": True,
        }

        text_tracks.append({
            "id": uuid.uuid4().hex,
            "material_id": mat_id,
            "target_timerange": {
                "start": cap["start"],
                "duration": cap["end"] - cap["start"],
            },
            "source_timerange": {
                "start": 0,
                "duration": cap["end"] - cap["start"],
            },
            "transform": {"y": -850},
        })

    draft_content = {
        "id": draft_id,
        "platform": "win",
        "type": "video",
        "duration": total_duration_us,
        "materials": {
            "texts": text_materials,
        },
        "tracks": [
            {
                "type": "text",
                "attribute": 0,
                "segments": text_tracks,
            }
        ],
        "config": {
            "width": width,
            "height": height,
            "fps": 30.0,
        },
    }

    draft_info = {
        "draft_id": draft_id,
        "draft_name": f"{name}-{draft_id[-8:]}",
        "duration": total_duration_us,
        "create_time": int(time.time() * 1000000),
        "update_time": int(time.time() * 1000000),
        "platform": "win",
    }

    content_path = os.path.join(draft_dir, "draft_content.json")
    info_path = os.path.join(draft_dir, "draft_info.json")

    Path(content_path).write_text(
        json.dumps(draft_content, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    Path(info_path).write_text(
        json.dumps(draft_info, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    log("draft", f"JianYing draft: {draft_dir} ({len(captions)} captions)")
    log("draft", "Copy to ~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft/ and restart JianYing to import")


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove filler words and speech errors from talking-head videos"
    )
    parser.add_argument("video_path", help="Path to the source video file")
    parser.add_argument("--out-dir", required=True, dest="out_dir",
                        help="Output directory under output_videos/ or tmp/")
    parser.add_argument("--silence-threshold", type=float, default=DEFAULT_SILENCE_THRESHOLD,
                        dest="silence_threshold",
                        help=f"Silence threshold in seconds (default: {DEFAULT_SILENCE_THRESHOLD})")
    parser.add_argument("--keep-fillers", type=str, default=DEFAULT_KEEP_FILLERS,
                        dest="keep_fillers",
                        help="Comma-separated filler words to preserve (e.g. 嗯,啊)")
    parser.add_argument("--no-ai", action="store_true",
                        help="Skip AI semantic analysis (only script-based detection)")
    parser.add_argument("--hd", action="store_true",
                        help="2-pass HD re-encode output")
    parser.add_argument("--hd-multiplier", type=float, default=1.2,
                        dest="hd_multiplier",
                        help="HD bitrate multiplier (default: 1.2)")
    parser.add_argument("--srt", action="store_true",
                        help="Generate SRT subtitle file")
    parser.add_argument("--draft", action="store_true",
                        help="Generate JianYing draft directory")
    parser.add_argument("--dict", type=str, default=None,
                        help="Path to hot words dictionary file (one word per line)")
    args = parser.parse_args()

    if not os.path.isfile(args.video_path):
        die(f"Video file not found: {args.video_path}")

    out_dir = ensure_safe_output_dir(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Parse keep-fillers
    keep_fillers = set()
    if args.keep_fillers:
        keep_fillers = {w.strip() for w in args.keep_fillers.split(",") if w.strip()}

    # Load hot words dictionary
    hot_words = None
    if args.dict and os.path.isfile(args.dict):
        hot_words = [line.strip() for line in Path(args.dict).read_text(encoding="utf-8").splitlines() if line.strip()]
        log("dict", f"Loaded {len(hot_words)} hot words")

    # ── Step 1: Extract audio ──
    log("step", "1/8: Extracting audio...")
    tmp_dir = str(out_dir / "_tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    try:
        audio_path = os.path.join(tmp_dir, "audio.mp3")
        extract_audio(args.video_path, audio_path)

        # ── Step 2: ASR transcription ──
        log("step", "2/8: Transcribing via ASR...")
        asr_mode, asr_result = run_asr(audio_path, hot_words)

        # ── Step 3: Generate subtitles_words.json ──
        log("step", "3/8: Generating word-level subtitles...")
        if asr_mode == "volcengine":
            words = volcengine_to_words(asr_result)
        else:
            words = siliconflow_to_words(asr_result, audio_path)

        words_path = str(out_dir / "subtitles_words.json")
        Path(words_path).write_text(json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8")
        log("words", f"{len(words)} elements ({sum(1 for w in words if w.get('isGap'))} gaps)")

        # ── Step 4: Script-based deterministic detection ──
        log("step", "4/8: Detecting speech errors (script-based)...")

        # Silences
        silence_indices = detect_silences(words, args.silence_threshold)
        log("detect", f"Silences >= {args.silence_threshold}s: {len(silence_indices)}")

        # Filler words
        filler_indices = detect_filler_words(words, keep_fillers)
        log("detect", f"Filler words: {len(filler_indices)}")

        # Stutters
        stutter_indices = detect_stutters(words)
        log("detect", f"Stutters: {len(stutter_indices)}")

        # Continuous fillers
        continuous_indices = detect_continuous_fillers(words, keep_fillers)
        log("detect", f"Continuous fillers: {len(continuous_indices)}")

        # Merge all script-based deletions
        script_deletes = sorted(set(silence_indices + filler_indices + stutter_indices + continuous_indices))
        log("detect", f"Total script-based deletions: {len(script_deletes)}")

        # ── Step 5: Generate analysis files for AI ──
        log("step", "5/8: Generating analysis files...")

        readable_path = str(out_dir / "readable.txt")
        sentences_path = str(out_dir / "sentences.txt")
        auto_selected_path = str(out_dir / "auto_selected.json")

        generate_readable(words, readable_path)
        generate_sentences(words, sentences_path)

        # Save script-based auto_selected for AI to extend
        Path(auto_selected_path).write_text(
            json.dumps(script_deletes, indent=2), encoding="utf-8"
        )

        # Generate analysis report
        analysis = {
            "mode": asr_mode,
            "total_words": len(words),
            "gaps": sum(1 for w in words if w.get("isGap")),
            "script_detections": {
                "silences": len(silence_indices),
                "fillers": len(filler_indices),
                "stutters": len(stutter_indices),
                "continuous_fillers": len(continuous_indices),
            },
            "script_delete_count": len(script_deletes),
            "ai_analysis_needed": not args.no_ai,
        }
        analysis_path = str(out_dir / "analysis.json")
        Path(analysis_path).write_text(
            json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        # ── Step 6: Apply deletions and cut video ──
        log("step", "6/8: Cutting video...")

        # Use script_deletes as the final delete list
        # (AI analysis results will be merged by the agent and re-run if needed)
        delete_segments = delete_indices_to_segments(words, script_deletes)

        video_name = Path(args.video_path).stem
        cut_output = str(out_dir / f"{video_name}_clean.mp4")
        cut_video(args.video_path, delete_segments, cut_output)

        # ── Step 7: HD re-encode (optional) ──
        final_output = cut_output
        if args.hd:
            log("step", "7/8: HD re-encoding...")
            hd_output = str(out_dir / f"{video_name}_clean_hd.mp4")
            hd_reencode(cut_output, hd_output, args.hd_multiplier)
            final_output = hd_output
        else:
            log("step", "7/8: HD re-encode skipped")

        # ── Step 8: SRT + JianYing draft (optional) ──
        if args.srt or args.draft:
            log("step", "8/8: Generating subtitles...")
            srt_output = str(out_dir / f"{video_name}.srt")
            delete_set = set(script_deletes)
            generate_srt(words, delete_set, srt_output)

            if args.draft:
                draft_dir = str(out_dir / "jianying_draft")
                os.makedirs(draft_dir, exist_ok=True)
                generate_jianying_draft(srt_output, draft_dir, name=video_name)
        else:
            log("step", "8/8: Subtitles skipped")

        # ── Summary ──
        info = probe_video(args.video_path)
        new_info = probe_video(final_output)

        print("\n" + "=" * 60)
        print(f"✅ de-mouth complete!")
        print(f"   Input:  {args.video_path} ({info['duration']:.1f}s)")
        print(f"   Output: {final_output} ({new_info['duration']:.1f}s)")
        deleted_dur = info["duration"] - new_info["duration"]
        print(f"   Deleted: {deleted_dur:.1f}s ({deleted_dur / info['duration'] * 100:.1f}%)")
        print(f"   ASR: {asr_mode}")
        print(f"   Script detections: {len(script_deletes)} items")
        if not args.no_ai:
            print(f"   ⚠️  AI semantic analysis pending — agent should read readable.txt + sentences.txt")
            print(f"   Then update auto_selected.json and re-run with --apply-ai")
        if args.srt:
            print(f"   SRT: {out_dir / f'{video_name}.srt'}")
        if args.draft:
            print(f"   JianYing draft: {out_dir / 'jianying_draft'}")
        print("=" * 60)

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
