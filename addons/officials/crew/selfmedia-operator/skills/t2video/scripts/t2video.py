#!/usr/bin/env python3
"""
t2video — One-stop Short Video Production

Three modes:
  tts      — Edge TTS (default, free) or SiliconFlow TTS → audio
  gen      — SiliconFlow Video Gen: prompt/image → video clip (mp4)
  compose  — MoviePy/FFmpeg: materials + audio → final MP4 (with optional plan for positioned inserts)

Usage:
  python3 t2video.py tts   --text "Hello" [--provider edge|siliconflow] [--voice ...]
  python3 t2video.py gen   --prompt "..." [--model ...] [--out-dir ...]
  python3 t2video.py compose --audio <path> --materials-dir <dir> --output <path> [--plan <json>]
"""

import argparse
import asyncio
import contextlib
import glob
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


# ════════════════════════════════════════════════════════════════════════════════
# Shared Utilities
# ════════════════════════════════════════════════════════════════════════════════


def log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def err(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr, flush=True)


def die(msg: str) -> None:
    err(msg)
    sys.exit(1)


def ensure_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def slugify(text: str, max_len: int = 20) -> str:
    text = re.sub(r"[^\w一-鿿]+", "-", text).strip("-")
    return text[:max_len]


def _suppress_stdout():
    """Context manager to suppress MoviePy v2 FFMPEG_VideoReader stdout noise."""
    return contextlib.redirect_stdout(io.StringIO())


def _ffmpeg_available() -> bool:
    """Check if ffmpeg is available on the system."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# ════════════════════════════════════════════════════════════════════════════════
# Plan Utilities — Positioned Material Insertion
# ════════════════════════════════════════════════════════════════════════════════


def parse_plan(plan_path: str) -> dict | None:
    """Parse a compose plan JSON file.

    Returns dict with keys: audio (str), aspect (str), tracks (list[dict]).
    Each track has: position (str), material (str), duration (float|None).
    Returns None if plan_path is empty/None.
    """
    if not plan_path:
        return None
    path = Path(plan_path)
    if not path.is_file():
        die(f"Plan file not found: {plan_path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        die(f"Failed to read plan file: {exc}")

    tracks = data.get("tracks", [])
    if not isinstance(tracks, list):
        die("Plan 'tracks' must be a list")

    for i, track in enumerate(tracks):
        if "position" not in track:
            die(f"Track #{i} missing 'position'")
        if "material" not in track:
            die(f"Track #{i} missing 'material'")
        if not os.path.isfile(track["material"]):
            die(f"Track #{i} material not found: {track['material']}")

    return data


def resolve_position(position: str, total_duration: float) -> float:
    """Convert a position specification to seconds.

    Supports:
      - Percentage: "0%", "50%", "100%"
      - Seconds: "5.0", "12.5"
    """
    if isinstance(position, (int, float)):
        return float(position)

    position = str(position).strip()

    if position.endswith("%"):
        try:
            pct = float(position[:-1])
        except ValueError:
            die(f"Invalid position percentage: {position}")
        return total_duration * (pct / 100.0)

    try:
        return float(position)
    except ValueError:
        die(f"Invalid position: {position}. Use percentage ('50%') or seconds ('5.0')")


# ════════════════════════════════════════════════════════════════════════════════
# TTS Mode — Edge TTS (default) / SiliconFlow TTS (fallback)
# ════════════════════════════════════════════════════════════════════════════════

# ── Edge TTS ─────────────────────────────────────────────────────────────────

EDGE_TTS_DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
EDGE_TTS_VALID_VOICES = {
    "zh-CN-XiaoxiaoNeural",
    "zh-CN-XiaoyiNeural",
    "zh-CN-YunjianNeural",
    "zh-CN-YunxiNeural",
    "zh-CN-YunxiaNeural",
    "zh-CN-YunyangNeural",
    "zh-CN-liaoning-XiaobeiNeural",
    "zh-CN-shaanxi-XiaoniNeural",
    "en-US-JennyNeural",
    "en-US-GuyNeural",
    "en-US-AriaNeural",
    "en-US-DavisNeural",
    "ja-JP-NanamiNeural",
    "ja-JP-KeitaNeural",
    "ko-KR-SunHiNeural",
    "ko-KR-InJoonNeural",
}

# ── SiliconFlow TTS ─────────────────────────────────────────────────────────

SF_TTS_DEFAULT_API_BASE = "https://api.siliconflow.cn/v1"
SF_TTS_DEFAULT_MODEL = "FunAudioLLM/CosyVoice2-0.5B"
SF_TTS_DEFAULT_VOICE = "FunAudioLLM/CosyVoice2-0.5B:alex"
SF_TTS_VALID_FORMATS = {"mp3", "opus", "wav", "pcm"}
SF_TTS_VALID_VOICES = {
    "FunAudioLLM/CosyVoice2-0.5B:alex",
    "FunAudioLLM/CosyVoice2-0.5B:anna",
    "FunAudioLLM/CosyVoice2-0.5B:bella",
    "FunAudioLLM/CosyVoice2-0.5B:benjamin",
    "FunAudioLLM/CosyVoice2-0.5B:charles",
    "FunAudioLLM/CosyVoice2-0.5B:claire",
    "FunAudioLLM/CosyVoice2-0.5B:david",
    "FunAudioLLM/CosyVoice2-0.5B:diana",
}

# ── Common TTS ───────────────────────────────────────────────────────────────

TTS_SAFE_INPUT_DIRS = (
    Path("scripts"),
    Path("assets"),
    Path("tmp"),
    Path("output_videos"),
    Path("output_video"),
)
TTS_SAFE_OUTPUT_DIRS = (
    Path("assets/audio"),
    Path("tmp"),
    Path("output_videos"),
    Path("output_video"),
)
TTS_TEXT_EXTENSIONS = {".txt", ".md"}
TTS_MAX_TEXT_FILE_BYTES = 512 * 1024


def _tts_ensure_safe_path(
    raw_path: str, allowed_dirs: tuple[Path, ...], purpose: str
) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        die(f"{purpose} path must be relative to the workspace")
    if ".." in path.parts:
        die(f"{purpose} path must not contain '..'")
    root = Path.cwd().resolve()
    resolved = (root / path).resolve()
    if not any(
        resolved == (root / base).resolve()
        or resolved.is_relative_to((root / base).resolve())
        for base in allowed_dirs
    ):
        allowed = ", ".join(str(base) for base in allowed_dirs)
        die(f"{purpose} path must be under one of: {allowed}")
    return resolved


def _tts_read_text_file(raw_path: str) -> str:
    path = _tts_ensure_safe_path(raw_path, TTS_SAFE_INPUT_DIRS, "--text-file")
    if path.suffix.lower() not in TTS_TEXT_EXTENSIONS:
        die(
            f"--text-file must use one of these extensions: "
            f"{', '.join(sorted(TTS_TEXT_EXTENSIONS))}"
        )
    if not path.is_file():
        die(f"--text-file does not exist or is not a file: {raw_path}")
    if path.stat().st_size > TTS_MAX_TEXT_FILE_BYTES:
        die(f"--text-file exceeds {TTS_MAX_TEXT_FILE_BYTES} bytes")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        die("--text-file must be UTF-8 encoded")
    except OSError as exc:
        die(f"failed to read --text-file: {exc}")
    raise AssertionError("unreachable")


def _tts_read_text(args: argparse.Namespace) -> str:
    if args.text and args.text_file:
        die("Use either --text or --text-file, not both")
    if args.text_file:
        text = _tts_read_text_file(args.text_file)
    elif args.text:
        text = args.text
    else:
        die("Either --text or --text-file is required")
    text = text.strip()
    if not text:
        die("Input text is empty")
    return text


def _tts_resolve_output_path(args: argparse.Namespace, ext: str) -> Path:
    raw_path = args.output or str(
        (
            Path(args.out_dir)
            if args.out_dir
            else Path(f"tmp/tts-{int(time.time())}")
        )
        / f"speech.{ext}"
    )
    output_path = _tts_ensure_safe_path(raw_path, TTS_SAFE_OUTPUT_DIRS, "output")
    return output_path


# ── Edge TTS Implementation ──────────────────────────────────────────────────


def _edge_tts_available() -> bool:
    try:
        import edge_tts  # noqa: F401

        return True
    except ImportError:
        return False


def _edge_tts_validate_args(args: argparse.Namespace) -> None:
    voice = args.voice or EDGE_TTS_DEFAULT_VOICE
    if voice not in EDGE_TTS_VALID_VOICES:
        die(
            f"Unsupported edge-tts voice: {voice}. "
            f"Valid voices: {', '.join(sorted(EDGE_TTS_VALID_VOICES))}"
        )
    if args.speed is not None and not -50 <= args.speed <= 50:
        die("--speed for edge-tts must be between -50 and 50 (percentage)")


def _edge_tts_run(
    text: str,
    voice: str,
    rate: int | None,
    output_path: Path,
) -> Path:
    """Run edge-tts. Returns audio output path."""
    import edge_tts

    rate_str = f"{rate:+d}%" if rate is not None else "+0%"

    async def _do() -> bytearray:
        communicate = edge_tts.Communicate(text, voice, rate=rate_str)
        audio_data = bytearray()

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])

        if not audio_data:
            die("edge-tts produced no audio output")
        return audio_data

    loop = asyncio.new_event_loop()
    try:
        audio_data = loop.run_until_complete(_do())
    finally:
        loop.close()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(bytes(audio_data))

    return output_path


# ── SiliconFlow TTS Implementation ───────────────────────────────────────────


def _sf_tts_validate_args(args: argparse.Namespace) -> None:
    if args.sf_model != SF_TTS_DEFAULT_MODEL:
        die(f"Unsupported SiliconFlow model: {args.sf_model}. Use {SF_TTS_DEFAULT_MODEL}")
    voice = args.voice or SF_TTS_DEFAULT_VOICE
    if voice and voice not in SF_TTS_VALID_VOICES:
        die(
            f"Unsupported SiliconFlow voice: {voice}. "
            f"Valid voices: {', '.join(sorted(SF_TTS_VALID_VOICES))}"
        )
    if len(args.text) > 128000:
        die("Input text exceeds 128000 characters")


def _sf_tts_build_payload(args: argparse.Namespace, text: str) -> dict:
    voice = args.voice or SF_TTS_DEFAULT_VOICE
    payload: dict = {
        "model": args.sf_model,
        "input": text,
        "voice": voice,
        "response_format": args.format,
    }
    if args.sample_rate is not None:
        payload["sample_rate"] = args.sample_rate
    if args.speed is not None:
        payload["speed"] = args.speed
    return payload


def _sf_tts_create_speech(api_base: str, api_key: str, payload: dict) -> bytes:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{api_base.rstrip('/')}/audio/speech",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        die(f"HTTP {exc.code}: {body}")
    except urllib.error.URLError as exc:
        die(f"request failed: {exc.reason}")
    raise AssertionError("unreachable")


def _sf_tts_run(
    text: str,
    args: argparse.Namespace,
    output_path: Path,
) -> Path:
    """Run SiliconFlow TTS. Returns audio output path."""
    payload = _sf_tts_build_payload(args, text)

    api_key = os.environ.get("SILICONFLOW_API_KEY", "").strip()
    if not api_key:
        die("SILICONFLOW_API_KEY not set")
    api_base = (
        os.environ.get("SILICONFLOW_API_BASE", SF_TTS_DEFAULT_API_BASE).strip()
        or SF_TTS_DEFAULT_API_BASE
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    audio = _sf_tts_create_speech(api_base, api_key, payload)
    if not audio:
        die("empty audio response")
    output_path.write_bytes(audio)

    return output_path


# ── TTS Main ─────────────────────────────────────────────────────────────────


def tts_main(args: argparse.Namespace) -> None:
    text = _tts_read_text(args)
    provider = args.provider

    if provider == "edge":
        if not _edge_tts_available():
            die("edge-tts is not installed. Run: pip install edge-tts>=7.0")
        _edge_tts_validate_args(args)
        fmt = "mp3"
        output_path = _tts_resolve_output_path(args, fmt)
        voice = args.voice or EDGE_TTS_DEFAULT_VOICE
        log(f"TTS [edge]: voice={voice} chars={len(text)}")
        audio_path = _edge_tts_run(text, voice, args.speed, output_path)
        log(f"TTS done: {audio_path}")

    elif provider == "siliconflow":
        _sf_tts_validate_args(args)
        output_path = _tts_resolve_output_path(args, args.format)
        voice = args.voice or SF_TTS_DEFAULT_VOICE
        log(f"TTS [siliconflow]: voice={voice} format={args.format} chars={len(text)}")
        audio_path = _sf_tts_run(text, args, output_path)
        log(f"TTS done: {audio_path}")

    else:
        die(f"Unknown TTS provider: {provider}. Use 'edge' or 'siliconflow'.")

    # Save metadata
    meta = {
        "mode": "tts",
        "provider": provider,
        "voice": args.voice or (
            EDGE_TTS_DEFAULT_VOICE if provider == "edge" else SF_TTS_DEFAULT_VOICE
        ),
        "text_chars": len(text),
        "audio_file": str(audio_path),
    }
    meta_path = audio_path.with_suffix(".json")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


# ════════════════════════════════════════════════════════════════════════════════
# Gen Mode — SiliconFlow Video Generation
# ════════════════════════════════════════════════════════════════════════════════

GEN_SUBMIT_URL = "https://api.siliconflow.cn/v1/video/submit"
GEN_STATUS_URL = "https://api.siliconflow.cn/v1/video/status"

GEN_T2V_MODEL = "Wan-AI/Wan2.2-T2V-A14B"
GEN_I2V_MODEL = "Wan-AI/Wan2.2-I2V-A14B"
GEN_VALID_SIZES = {"1280x720", "720x1280", "960x960"}


def _gen_post_json(url: str, payload: dict, api_key: str, timeout: int = 60) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        die(f"HTTP {e.code}: {body}")
    except urllib.error.URLError as exc:
        die(f"request failed: {exc.reason}")
    raise AssertionError("unreachable")


def _gen_submit_job(payload: dict, api_key: str) -> str:
    result = _gen_post_json(GEN_SUBMIT_URL, payload, api_key, timeout=60)
    rid = result.get("requestId")
    if not rid:
        die(f"No requestId in response: {result}")
    return rid


def _gen_poll_until_done(
    request_id: str, api_key: str, poll_interval: int, timeout: int
) -> dict:
    deadline = time.time() + timeout
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        result = _gen_post_json(
            GEN_STATUS_URL, {"requestId": request_id}, api_key, timeout=30
        )
        status = result.get("status", "")
        log(f"Gen poll #{attempt}: status={status}")
        if status == "Succeed":
            return result
        if status == "Failed":
            reason = result.get("reason", "unknown")
            die(f"Generation failed: {reason}")
        time.sleep(poll_interval)
    die(f"Timed out after {timeout}s")


def _gen_download_video(url: str, dest_path: Path) -> None:
    log(f"Downloading video -> {dest_path}")
    req = urllib.request.Request(url, headers={"User-Agent": "wiseflow-t2video/1.0"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        dest_path.write_bytes(resp.read())


def gen_main(args: argparse.Namespace) -> None:
    if args.model == GEN_I2V_MODEL and not args.image:
        die(f"--image is required when using model '{GEN_I2V_MODEL}'")

    api_key = os.environ.get("SILICONFLOW_API_KEY", "").strip()
    if not api_key:
        die("SILICONFLOW_API_KEY not set")

    ts = int(time.time())
    out_dir = Path(args.out_dir) if args.out_dir else Path(f"./tmp/sf-video-{ts}")
    out_dir.mkdir(parents=True, exist_ok=True)

    payload: dict = {
        "model": args.model,
        "prompt": args.prompt,
        "image_size": args.image_size,
    }
    if args.image:
        payload["image"] = args.image
    if args.negative_prompt:
        payload["negative_prompt"] = args.negative_prompt
    if args.seed is not None:
        payload["seed"] = args.seed

    log(f"Gen: submitting job model={args.model} size={args.image_size}")
    request_id = _gen_submit_job(payload, api_key)
    log(f"Gen: jobId={request_id}")
    log(f"Gen: polling every {args.poll_interval}s (timeout={args.timeout}s)")

    result = _gen_poll_until_done(
        request_id, api_key, args.poll_interval, args.timeout
    )

    videos = result.get("results", {}).get("videos", [])
    if not videos:
        die(f"No videos in result: {result}")

    video_url = videos[0].get("url", "")
    if not video_url:
        die("Empty video URL in result")

    video_path = out_dir / f"video_{request_id[:8]}.mp4"
    _gen_download_video(video_url, video_path)

    result_path = out_dir / "result.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))

    log(f"Gen done: {video_path}")
    log(f"Metadata: {result_path}")


# ════════════════════════════════════════════════════════════════════════════════
# Compose Mode — Video Assembly
# ════════════════════════════════════════════════════════════════════════════════

# ── MoviePy Version Detection ────────────────────────────────────────────────


def _get_moviepy_major() -> int:
    try:
        import moviepy

        return int(moviepy.__version__.split(".")[0])
    except Exception:
        return 2


_MOVIEPY_MAJOR = _get_moviepy_major()

# ── Constants ────────────────────────────────────────────────────────────────

ASPECT_RESOLUTIONS = {
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
    "1:1": (1080, 1080),
}

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".webm", ".mkv"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

PLACEHOLDER_COLOR = (30, 30, 50)
SEGMENT_CODEC = "libx264"
SEGMENT_FPS = 30
SEGMENT_PIX_FMT = "yuv420p"

# ── Audio Helpers ────────────────────────────────────────────────────────────


def get_audio_duration(audio_path: str) -> float:
    from moviepy import AudioFileClip

    clip = None
    try:
        with _suppress_stdout():
            clip = AudioFileClip(audio_path)
            duration = clip.duration
        return duration
    finally:
        if clip is not None:
            clip.close()


# ── Material Collection ──────────────────────────────────────────────────────


def collect_materials(materials_dir: str) -> list[dict]:
    items: list[dict] = []
    for ext in VIDEO_EXTS:
        for p in glob.glob(os.path.join(materials_dir, f"*{ext}")):
            items.append({"path": p, "type": "video"})
        for p in glob.glob(os.path.join(materials_dir, f"*{ext.upper()}")):
            items.append({"path": p, "type": "video"})
    for ext in IMAGE_EXTS:
        for p in glob.glob(os.path.join(materials_dir, f"*{ext}")):
            items.append({"path": p, "type": "image"})
        for p in glob.glob(os.path.join(materials_dir, f"*{ext.upper()}")):
            items.append({"path": p, "type": "image"})
    return sorted(items, key=lambda x: x["path"])


# ── FFmpeg Concat ────────────────────────────────────────────────────────────


def concat_video_clips_with_ffmpeg(
    segment_paths: list[str],
    output_path: str,
    audio_path: str,
) -> str:
    if not segment_paths:
        raise ValueError("No segment paths provided for ffmpeg concat")

    fd, concat_list_path = tempfile.mkstemp(suffix=".txt", prefix="t2v_concat_")
    os.close(fd)
    concat_output = output_path + ".concat_tmp.mp4"

    try:
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for seg_path in segment_paths:
                escaped = seg_path.replace("'", "'\\''")
                f.write(f"file '{escaped}'\n")

        log(f"FFmpeg concat: joining {len(segment_paths)} segments (stream copy)")
        cmd_concat = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_list_path, "-c", "copy", concat_output,
        ]
        result = subprocess.run(cmd_concat, capture_output=True, text=True)
        if result.returncode != 0:
            log("FFmpeg concat: stream copy failed, falling back to re-encode")
            cmd_reencode = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", concat_list_path,
                "-c:v", SEGMENT_CODEC, "-pix_fmt", SEGMENT_PIX_FMT,
                "-r", str(SEGMENT_FPS), concat_output,
            ]
            result = subprocess.run(cmd_reencode, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(
                    f"FFmpeg concat failed (re-encode): {result.stderr[-500:]}"
                )

        log("FFmpeg mux: adding audio track")
        cmd_mux = [
            "ffmpeg", "-y",
            "-i", concat_output, "-i", audio_path,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest", output_path,
        ]
        result = subprocess.run(cmd_mux, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg audio mux failed: {result.stderr[-500:]}")

    finally:
        for path in (concat_list_path, concat_output):
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

    return output_path


# ── Video Composition (MoviePy) ──────────────────────────────────────────────


def make_placeholder_clip(duration: float, resolution: tuple, color: tuple):
    from moviepy import ColorClip

    return ColorClip(size=resolution, color=color, duration=duration)


def image_to_clip(image_path: str, duration: float, resolution: tuple):
    from moviepy import ImageClip

    with _suppress_stdout():
        clip = ImageClip(image_path, duration=duration)
    clip = clip.resized(resolution)
    if clip.size[0] != resolution[0] or clip.size[1] != resolution[1]:
        x_center = clip.size[0] / 2
        y_center = clip.size[1] / 2
        clip = clip.cropped(
            x_center=x_center,
            y_center=y_center,
            width=resolution[0],
            height=resolution[1],
        )
    return clip


def video_to_clip(video_path: str, max_duration: float, resolution: tuple):
    from moviepy import VideoFileClip

    with _suppress_stdout():
        clip = VideoFileClip(video_path).without_audio()
    if clip.duration > max_duration:
        clip = clip.subclipped(0, max_duration)
    clip = clip.resized(resolution)
    if clip.size[0] != resolution[0] or clip.size[1] != resolution[1]:
        x_center = clip.size[0] / 2
        y_center = clip.size[1] / 2
        clip = clip.cropped(
            x_center=x_center,
            y_center=y_center,
            width=resolution[0],
            height=resolution[1],
        )
    return clip


def _apply_crossfade(clip, duration: float = 0.3):
    if _MOVIEPY_MAJOR >= 2:
        from moviepy.video.fx.CrossFadeIn import CrossFadeIn

        return clip.with_effects([CrossFadeIn(duration)])
    else:
        return clip.crossfadein(duration)


def _concat_clips(clips: list):
    from moviepy import concatenate_videoclips

    if _MOVIEPY_MAJOR >= 2:
        return concatenate_videoclips(clips)
    else:
        return concatenate_videoclips(clips, method="compose")


def _write_clip(clip, output_path: str, *, audio: bool = True, **kwargs) -> None:
    write_kwargs: dict = {
        "fps": SEGMENT_FPS,
        "codec": SEGMENT_CODEC,
        "logger": None,
    }
    if audio:
        write_kwargs["audio_codec"] = "aac"
        write_kwargs["audio_fps"] = 44100
        write_kwargs["audio_bitrate"] = "192k"
    else:
        write_kwargs["audio"] = False

    if _MOVIEPY_MAJOR >= 2:
        write_kwargs["pixel_format"] = SEGMENT_PIX_FMT
    else:
        write_kwargs["verbose"] = False

    write_kwargs.update(kwargs)
    clip.write_videofile(output_path, **write_kwargs)


# ── Timeline Builder ─────────────────────────────────────────────────────────


def _build_timeline(
    plan: dict | None,
    audio_duration: float,
) -> list[dict]:
    """Build a timeline of segments from plan tracks.

    Each segment: {"start": float, "end": float, "material": str, "type": str}
    - type is "video" or "image" for plan tracks, "auto" for gap-fill from materials-dir
    """
    if not plan or not plan.get("tracks"):
        return [{"start": 0.0, "end": audio_duration, "material": "", "type": "auto"}]

    tracks = sorted(
        plan["tracks"],
        key=lambda t: resolve_position(t["position"], audio_duration),
    )

    segments: list[dict] = []
    prev_end = 0.0

    for track in tracks:
        start = resolve_position(track["position"], audio_duration)
        if start < prev_end:
            err(
                f"Warning: track at {track['position']} overlaps previous segment, "
                f"clamping start to {prev_end:.1f}s"
            )
            start = prev_end

        # Gap before this track
        if start > prev_end + 0.01:
            segments.append(
                {"start": prev_end, "end": start, "material": "", "type": "auto"}
            )

        # Determine material type and duration
        mat_path = track["material"]
        mat_ext = Path(mat_path).suffix.lower()
        remaining = audio_duration - start

        if mat_ext in VIDEO_EXTS:
            mat_type = "video"
            from moviepy import VideoFileClip

            with _suppress_stdout():
                vc = VideoFileClip(mat_path)
                mat_dur = vc.duration
                vc.close()
            mat_dur = min(mat_dur, remaining)
        elif mat_ext in IMAGE_EXTS:
            mat_type = "image"
            mat_dur = track.get("duration")
            if not mat_dur:
                die(f"Image material '{mat_path}' must specify 'duration' in plan")
            mat_dur = min(float(mat_dur), remaining)
        else:
            die(f"Unsupported material type: {mat_path}")

        end = start + mat_dur
        segments.append(
            {"start": start, "end": end, "material": mat_path, "type": mat_type}
        )
        prev_end = end

    # Gap after last track
    if prev_end < audio_duration - 0.01:
        segments.append(
            {"start": prev_end, "end": audio_duration, "material": "", "type": "auto"}
        )

    return segments


# ── Main Composition ─────────────────────────────────────────────────────────


def compose_video(
    materials: list[dict],
    audio_path: str,
    output_path: str,
    aspect: str,
    clip_duration: float,
    transition: str,
    plan: dict | None = None,
) -> str:
    from moviepy import AudioFileClip

    resolution = ASPECT_RESOLUTIONS.get(aspect, (1080, 1920))
    audio_duration = get_audio_duration(audio_path)
    log(f"Audio duration: {audio_duration:.1f}s")

    video_items = [m for m in materials if m["type"] == "video"]
    image_items = [m for m in materials if m["type"] == "image"]

    if video_items:
        primary = video_items
        primary_type = "video"
    elif image_items:
        primary = image_items
        primary_type = "image"
    else:
        primary = []
        primary_type = "none"

    plan_tracks = plan.get("tracks", []) if plan else []
    log(
        f"Compose: {len(primary)} {primary_type} materials, "
        f"{len(plan_tracks)} plan tracks, "
        f"duration={audio_duration:.1f}s, aspect={aspect}"
    )

    # ── Build timeline ──────────────────────────────────────────────────
    timeline = _build_timeline(plan, audio_duration)

    # ── Build segment clips from timeline ───────────────────────────────
    clips = []
    auto_idx = 0

    for segment in timeline:
        seg_dur = segment["end"] - segment["start"]
        if seg_dur <= 0.01:
            continue

        if segment["type"] == "auto":
            if not primary:
                clips.append(
                    make_placeholder_clip(seg_dur, resolution, PLACEHOLDER_COLOR)
                )
                continue
            remaining = seg_dur
            while remaining > 0.01:
                item = primary[auto_idx % len(primary)]
                dur = min(clip_duration, remaining)
                try:
                    if item["type"] == "image" or primary_type == "image":
                        clip = image_to_clip(item["path"], dur, resolution)
                    else:
                        clip = video_to_clip(item["path"], dur, resolution)
                except Exception as e:
                    err(f"Failed to load '{item['path']}': {e} — using placeholder")
                    clip = make_placeholder_clip(dur, resolution, PLACEHOLDER_COLOR)
                clips.append(clip)
                remaining -= dur
                auto_idx += 1
        elif segment["type"] == "video":
            try:
                clip = video_to_clip(segment["material"], seg_dur, resolution)
            except Exception as e:
                err(f"Failed to load '{segment['material']}': {e} — using placeholder")
                clip = make_placeholder_clip(seg_dur, resolution, PLACEHOLDER_COLOR)
            clips.append(clip)
        elif segment["type"] == "image":
            try:
                clip = image_to_clip(segment["material"], seg_dur, resolution)
            except Exception as e:
                err(f"Failed to load '{segment['material']}': {e} — using placeholder")
                clip = make_placeholder_clip(seg_dur, resolution, PLACEHOLDER_COLOR)
            clips.append(clip)

    if not clips:
        log("Compose: no clips generated — using placeholder")
        with _suppress_stdout():
            audio = AudioFileClip(audio_path)
        try:
            placeholder = make_placeholder_clip(
                audio_duration, resolution, PLACEHOLDER_COLOR
            )
            final = placeholder.with_audio(audio)
            _write_clip(final, output_path)
        finally:
            audio.close()
        return output_path

    # ── Concatenate video clips ──────────────────────────────────────────
    use_ffmpeg = transition == "none" and _ffmpeg_available()

    if use_ffmpeg:
        log(f"Compose: using ffmpeg concat path ({len(clips)} segments)")
        tmpdir = tempfile.mkdtemp(prefix="t2v_segments_")
        segment_paths: list[str] = []
        try:
            for i, clip in enumerate(clips):
                seg_path = os.path.join(tmpdir, f"seg_{i:04d}.mp4")
                _write_clip(clip, seg_path, audio=False)
                segment_paths.append(seg_path)
                clip.close()

            concat_video_clips_with_ffmpeg(segment_paths, output_path, audio_path)
        finally:
            for seg_path in segment_paths:
                if os.path.exists(seg_path):
                    try:
                        os.remove(seg_path)
                    except OSError:
                        pass
            try:
                os.rmdir(tmpdir)
            except OSError:
                pass
    else:
        log(f"Compose: using MoviePy path (transition={transition})")

        if transition == "fade" and len(clips) > 1:
            faded = []
            for i, c in enumerate(clips):
                if i > 0:
                    c = _apply_crossfade(c, 0.3)
                faded.append(c)
            clips = faded

        video = _concat_clips(clips)

        with _suppress_stdout():
            audio = AudioFileClip(audio_path)
        try:
            video = (
                video.with_audio(audio)
                .with_duration(audio_duration)
                .with_fps(SEGMENT_FPS)
            )
            _write_clip(video, output_path)
        finally:
            audio.close()

    log(f"Compose: written -> {output_path}")
    return output_path


def compose_main(args: argparse.Namespace) -> None:
    if not os.path.exists(args.audio):
        die(f"Audio file not found: {args.audio}")
    if not os.path.isdir(args.materials_dir):
        die(f"Materials directory not found: {args.materials_dir}")

    # Parse plan if provided
    plan = parse_plan(getattr(args, "plan", None))

    materials = collect_materials(args.materials_dir)
    if not materials and not (plan and plan.get("tracks")):
        err(
            f"Warning: no video/image files found in {args.materials_dir} "
            "— will use placeholder"
        )

    ensure_dir(os.path.dirname(args.output) or ".")

    compose_video(
        materials=materials,
        audio_path=args.audio,
        output_path=args.output,
        aspect=args.aspect,
        clip_duration=args.clip_duration,
        transition=args.transition,
        plan=plan,
    )

    # Save metadata
    audio_duration = get_audio_duration(args.audio)
    meta = {
        "mode": "compose",
        "audio": args.audio,
        "materials_dir": args.materials_dir,
        "material_count": len(materials),
        "audio_duration": round(audio_duration, 1),
        "aspect": args.aspect,
        "transition": args.transition,
        "plan": getattr(args, "plan", None),
        "output": args.output,
        "generated_at": datetime.now().isoformat(),
    }
    meta_path = os.path.splitext(args.output)[0] + ".json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    log(f"Done: {args.output}")


# ════════════════════════════════════════════════════════════════════════════════
# Entry Point — Subcommand Router
# ════════════════════════════════════════════════════════════════════════════════


def main() -> None:
    parser = argparse.ArgumentParser(
        description="t2video — One-stop Short Video Production",
    )
    subparsers = parser.add_subparsers(dest="mode", help="Operation mode")

    # ── tts subcommand ────────────────────────────────────────────────────
    tts_parser = subparsers.add_parser("tts", help="Text-to-speech")
    tts_parser.add_argument("--text", default=None, help="Text to synthesize")
    tts_parser.add_argument(
        "--text-file", default=None, dest="text_file", help="UTF-8 text file"
    )
    tts_parser.add_argument(
        "--provider",
        default="edge",
        choices=["edge", "siliconflow"],
        help="TTS provider: edge (default, free) or siliconflow",
    )
    tts_parser.add_argument(
        "--voice",
        default=None,
        help="Voice ID (provider-specific, see docs)",
    )
    tts_parser.add_argument(
        "--format",
        default="mp3",
        choices=sorted(SF_TTS_VALID_FORMATS),
        help="Audio response format (siliconflow only)",
    )
    tts_parser.add_argument(
        "--speed",
        type=int,
        default=None,
        help="Speech speed. Edge: -50 to 50 (percentage). SiliconFlow: 0.25 to 4.0",
    )
    tts_parser.add_argument(
        "--sample-rate",
        type=int,
        default=None,
        dest="sample_rate",
        help="Output sample rate (siliconflow only)",
    )
    tts_parser.add_argument(
        "--sf-model",
        default=SF_TTS_DEFAULT_MODEL,
        dest="sf_model",
        help="SiliconFlow TTS model ID",
    )
    tts_parser.add_argument(
        "--output", default=None, help="Exact output file path"
    )
    tts_parser.add_argument(
        "--out-dir", default=None, dest="out_dir", help="Output directory"
    )

    # ── gen subcommand ────────────────────────────────────────────────────
    gen_parser = subparsers.add_parser(
        "gen", help="AI video generation via SiliconFlow"
    )
    gen_parser.add_argument("--prompt", required=True, help="Video description")
    gen_parser.add_argument(
        "--model",
        default=GEN_T2V_MODEL,
        choices=[GEN_T2V_MODEL, GEN_I2V_MODEL],
        help="Model ID",
    )
    gen_parser.add_argument(
        "--image",
        default=None,
        help="Image URL or base64 data URI (required for I2V model)",
    )
    gen_parser.add_argument(
        "--image-size",
        default="1280x720",
        choices=sorted(GEN_VALID_SIZES),
        dest="image_size",
        help="Video resolution",
    )
    gen_parser.add_argument(
        "--negative-prompt", default=None, dest="negative_prompt"
    )
    gen_parser.add_argument("--seed", type=int, default=None)
    gen_parser.add_argument(
        "--poll-interval", type=int, default=10, dest="poll_interval"
    )
    gen_parser.add_argument("--timeout", type=int, default=600)
    gen_parser.add_argument(
        "--out-dir", default=None, dest="out_dir", help="Output directory"
    )

    # ── compose subcommand ────────────────────────────────────────────────
    compose_parser = subparsers.add_parser(
        "compose", help="Compose video from materials + audio"
    )
    compose_parser.add_argument(
        "--audio", required=True, help="Path to narration audio file (mp3/wav)"
    )
    compose_parser.add_argument(
        "--materials-dir",
        required=True,
        help="Directory containing video clips and/or images",
    )
    compose_parser.add_argument(
        "--plan",
        default=None,
        help="Path to plan JSON file for positioned material insertion",
    )
    compose_parser.add_argument(
        "--aspect",
        default="9:16",
        choices=["9:16", "16:9", "1:1"],
        help="Output aspect ratio (default: 9:16)",
    )
    compose_parser.add_argument(
        "--clip-duration",
        type=float,
        default=5.0,
        help="Max seconds per material clip (default: 5)",
    )
    compose_parser.add_argument(
        "--transition",
        default="none",
        choices=["none", "fade"],
        help="Clip transitions (default: none)",
    )
    compose_parser.add_argument(
        "--output", required=True, help="Output MP4 file path"
    )

    args = parser.parse_args()

    if args.mode == "tts":
        tts_main(args)
    elif args.mode == "gen":
        gen_main(args)
    elif args.mode == "compose":
        compose_main(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
