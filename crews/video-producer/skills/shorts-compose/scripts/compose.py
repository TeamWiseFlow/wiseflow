#!/usr/bin/env python3
"""
shorts-compose — Generate a short-form video from a topic or script.

Pipeline (Image Mode):
  topic/script → LLM script → edge-tts audio → SiliconFlow images → MoviePy video

Pipeline (Footage Mode, when --footage-dir is provided):
  topic/script → LLM script → edge-tts audio → local video clips → MoviePy video

Usage:
  # Image mode (AI-generated images)
  python3 compose.py --topic "AI工具推荐" --language zh --output-dir ./output_videos

  # Footage mode (real video clips from pexels-footage / pixabay-footage)
  python3 compose.py --topic "大自然之美" --footage-dir ./video_assets/footage \
                     --aspect 16:9 --output-dir ./output_videos

  # Script provided directly
  python3 compose.py --script "直接提供脚本文本" --language zh --output-dir ./output_videos

  # Batch generation
  python3 compose.py --topic "AI工具" --batch 3 --output-dir ./output_videos

Environment Variables:
  SILICONFLOW_API_KEY  SiliconFlow API key (required for image mode LLM; always required for script gen)
  LLM_API_KEY          Override LLM API key (defaults to SILICONFLOW_API_KEY)
  LLM_API_BASE         LLM API base URL (default: https://api.siliconflow.cn/v1)
  LLM_MODEL            Model name (default: Qwen/Qwen2.5-7B-Instruct)
  EDGE_TTS_VOICE       TTS voice name (auto-selected by language if not set)
"""

import argparse
import asyncio
import glob
import json
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import requests

# ── Constants ────────────────────────────────────────────────────────────────

SILICONFLOW_API_URL = "https://api.siliconflow.cn/v1/images/generations"
SILICONFLOW_IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"

DEFAULT_TTS_VOICES = {
    "zh": "zh-CN-YunxiNeural",
    "en": "en-US-GuyNeural",
}

PLACEHOLDER_COLOR = (30, 30, 50)

ASPECT_RESOLUTIONS = {
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
    "1:1":  (1080, 1080),
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def err(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr, flush=True)


def require_env(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        err(f"Environment variable {name} is not set.")
        sys.exit(1)
    return val


def slugify(text: str, max_len: int = 20) -> str:
    import re
    text = re.sub(r"[^\w\u4e00-\u9fff]+", "-", text).strip("-")
    return text[:max_len]


def ensure_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


# ── LLM ──────────────────────────────────────────────────────────────────────

def llm_call(prompt: str) -> str:
    api_key = os.environ.get("LLM_API_KEY", "").strip() or require_env("SILICONFLOW_API_KEY")
    api_base = os.environ.get("LLM_API_BASE", "https://api.siliconflow.cn/v1").rstrip("/")
    model = os.environ.get("LLM_MODEL", "Qwen/Qwen2.5-7B-Instruct")

    resp = requests.post(
        f"{api_base}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def generate_script(topic: str, language: str, duration_hint: int) -> str:
    lang_name = "Chinese" if language == "zh" else "English"
    n_sentences = max(3, duration_hint // 8)
    return llm_call(
        f"Write a short video script for a {duration_hint}-second vertical short video.\n"
        f"Topic: {topic}\nLanguage: {lang_name}\nSentences: exactly {n_sentences} short sentences\n"
        f"Rules: Plain text only, NO markdown, NO titles, direct engaging tone, no intro.\n"
        f"Return ONLY the script text."
    )


def generate_metadata(script: str, topic: str, language: str) -> dict:
    lang_name = "Chinese" if language == "zh" else "English"
    raw = llm_call(
        f"Based on this short video script, generate metadata in {lang_name}.\n"
        f"Script:\n{script}\n\n"
        f'Return ONLY valid JSON:\n{{"title": "...", "description": "...", "tags": ["tag1","tag2","tag3","tag4","tag5"]}}'
    )
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except Exception:
        return {"title": topic[:80], "description": script[:200], "tags": []}


def generate_image_prompts(script: str, n: int) -> list[str]:
    raw = llm_call(
        f"Generate {n} image prompts for AI image generation.\nScript:\n{script}\n"
        f"Rules: English, vivid descriptive language, cinematic 9:16 vertical.\n"
        f"Return ONLY a JSON array of {n} strings."
    )
    import re
    raw = raw.replace("```json", "").replace("```", "").strip()
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    return json.loads(raw)


# ── TTS ───────────────────────────────────────────────────────────────────────

async def _synthesize_async(text: str, voice: str, output_path: str) -> None:
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def synthesize_tts(script: str, language: str, output_path: str) -> str:
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        err("edge-tts not installed. Run: pip install edge-tts")
        sys.exit(1)
    voice = os.environ.get("EDGE_TTS_VOICE") or DEFAULT_TTS_VOICES.get(language, "en-US-GuyNeural")
    log(f"TTS: voice={voice}")
    asyncio.run(_synthesize_async(script, voice, output_path))
    return output_path


# ── Image Generation (Image Mode) ────────────────────────────────────────────

def generate_image(prompt: str, output_path: str, api_key: str, size: str = "1080x1920") -> bool:
    try:
        resp = requests.post(
            SILICONFLOW_API_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": SILICONFLOW_IMAGE_MODEL, "prompt": prompt,
                  "image_size": size, "num_inference_steps": 4},
            timeout=120,
        )
        resp.raise_for_status()
        image_url = resp.json()["images"][0]["url"]
        img_resp = requests.get(image_url, timeout=60)
        img_resp.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(img_resp.content)
        return True
    except Exception as e:
        log(f"  ⚠ Image generation failed: {e}")
        return False


def create_placeholder_image(output_path: str, width: int = 1080, height: int = 1920) -> str:
    try:
        from PIL import Image
        img = Image.new("RGB", (width, height), color=PLACEHOLDER_COLOR)
        img.save(output_path)
    except ImportError:
        import struct, zlib
        def _png(w, h, color):
            raw = bytes([0] + list(color) * w) * h
            def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
            ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
            return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
        with open(output_path, "wb") as f:
            f.write(_png(width, height, PLACEHOLDER_COLOR))
    return output_path


# ── Video Composition ─────────────────────────────────────────────────────────

def _crop_to_aspect(clip, target_w: int, target_h: int):
    """Crop a clip to target aspect ratio, then resize."""
    from moviepy.video.fx.all import crop
    target_ratio = target_w / target_h
    actual_ratio = clip.w / clip.h
    if abs(actual_ratio - target_ratio) > 0.01:
        if actual_ratio > target_ratio:
            new_w = int(clip.h * target_ratio)
            clip = crop(clip, width=new_w, height=clip.h,
                        x_center=clip.w / 2, y_center=clip.h / 2)
        else:
            new_h = int(clip.w / target_ratio)
            clip = crop(clip, width=clip.w, height=new_h,
                        x_center=clip.w / 2, y_center=clip.h / 2)
    return clip.resize((target_w, target_h))


def compose_from_images(image_paths: list[str], audio_path: str, output_path: str,
                        aspect: str = "9:16", transition: str = "none") -> float:
    """Compose video from static images + audio."""
    try:
        from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
        from moviepy.video.fx.all import fadein, fadeout
    except ImportError:
        err("moviepy not installed. Run: pip install moviepy")
        sys.exit(1)

    target_w, target_h = ASPECT_RESOLUTIONS[aspect]
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    frame_duration = total_duration / len(image_paths)

    clips = []
    for img_path in image_paths:
        clip = ImageClip(img_path).set_duration(frame_duration).set_fps(30)
        clip = _crop_to_aspect(clip, target_w, target_h)
        if transition == "fade" and frame_duration > 1:
            clip = clip.fx(fadein, 0.5).fx(fadeout, 0.5)
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose")
    final = final.set_audio(audio).set_duration(total_duration).set_fps(30)
    final.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac",
                          threads=2, logger=None)
    return total_duration


def compose_from_footage(footage_dir: str, audio_path: str, output_path: str,
                         aspect: str = "9:16", transition: str = "none",
                         max_clip_duration: int = 5) -> float:
    """Compose video from real video clips + audio."""
    try:
        from moviepy.editor import (AudioFileClip, VideoFileClip,
                                     concatenate_videoclips)
        from moviepy.video.fx.all import fadein, fadeout
    except ImportError:
        err("moviepy not installed. Run: pip install moviepy")
        sys.exit(1)

    target_w, target_h = ASPECT_RESOLUTIONS[aspect]
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration

    # Collect all video files from footage_dir
    video_files = []
    for ext in ("*.mp4", "*.mov", "*.webm", "*.avi"):
        video_files.extend(glob.glob(os.path.join(footage_dir, ext)))

    if not video_files:
        log(f"  ⚠ No video files found in {footage_dir}, falling back to placeholder images")
        # Create placeholder and fall back to image mode
        placeholder = str(Path(footage_dir) / "placeholder.png")
        create_placeholder_image(placeholder, target_w, target_h)
        return compose_from_images([placeholder], audio_path, output_path, aspect, transition)

    random.shuffle(video_files)
    log(f"  Found {len(video_files)} video clips in footage dir")

    clips = []
    total_built = 0.0

    while total_built < total_duration + 1:
        for vf_path in video_files:
            if total_built >= total_duration + 1:
                break
            try:
                vc = VideoFileClip(vf_path)
                seg_dur = min(max_clip_duration, vc.duration)
                vc = vc.subclip(0, seg_dur).set_fps(30)
                vc = _crop_to_aspect(vc, target_w, target_h)
                if transition == "fade" and seg_dur > 1:
                    vc = vc.fx(fadein, 0.5).fx(fadeout, 0.5)
                clips.append(vc)
                total_built += seg_dur
            except Exception as e:
                log(f"  ⚠ Skipping {Path(vf_path).name}: {e}")
        if not clips:
            break

    if not clips:
        log("  ⚠ No valid clips loaded, using placeholder")
        placeholder = str(Path(footage_dir) / "placeholder.png")
        create_placeholder_image(placeholder, target_w, target_h)
        return compose_from_images([placeholder], audio_path, output_path, aspect, transition)

    final = concatenate_videoclips(clips, method="compose")
    final = final.set_audio(audio).set_duration(total_duration).set_fps(30)
    final.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac",
                          threads=2, logger=None)

    for clip in clips:
        try:
            clip.close()
        except Exception:
            pass
    return total_duration


# ── Single Video Run ──────────────────────────────────────────────────────────

def run_once(args, output_dir: Path, assets_dir: Path, run_index: int = 0) -> dict:
    """Execute the full pipeline once. Returns metadata dict."""
    topic_for_meta = args.topic or (args.script or "")[:30]
    sf_api_key = os.environ.get("SILICONFLOW_API_KEY", "")

    # Step 1: Script
    if args.topic:
        log(f"Step 1/5: Generating script for: {args.topic}")
        script = generate_script(args.topic, args.language, args.duration_hint)
    else:
        log("Step 1/5: Using provided script")
        script = args.script

    # Step 2: Metadata
    log("Step 2/5: Generating metadata")
    try:
        metadata = generate_metadata(script, topic_for_meta, args.language)
    except Exception as e:
        log(f"  ⚠ Metadata failed ({e}), using defaults")
        metadata = {"title": topic_for_meta[:80], "description": script[:200], "tags": []}

    # Step 3: TTS
    log("Step 3/5: Synthesizing TTS")
    suffix = f"_{run_index}" if run_index else ""
    audio_path = str(assets_dir / f"audio{suffix}_{uuid4().hex[:6]}.mp3")
    synthesize_tts(script, args.language, audio_path)

    # Step 4: Media preparation
    target_w, target_h = ASPECT_RESOLUTIONS[args.aspect]
    image_size = f"{target_w}x{target_h}"

    if args.footage_dir:
        log(f"Step 4/5: Using footage from {args.footage_dir}")
        media_ready = True
    else:
        log(f"Step 4/5: Generating {args.n_images} images ({args.aspect})")
        if not sf_api_key:
            require_env("SILICONFLOW_API_KEY")
        try:
            prompts = generate_image_prompts(script, args.n_images)
        except Exception as e:
            log(f"  ⚠ Prompt generation failed ({e}), using fallback")
            prompts = [f"cinematic {topic_for_meta} scene, {args.aspect} vertical"] * args.n_images

        image_paths = []
        for i, prompt in enumerate(prompts):
            path = str(assets_dir / f"frame{suffix}_{i:02d}_{uuid4().hex[:6]}.png")
            log(f"  Generating image {i+1}/{len(prompts)}: {prompt[:50]}...")
            if not generate_image(prompt, path, sf_api_key, image_size):
                create_placeholder_image(path, target_w, target_h)
            image_paths.append(path)
            if i < len(prompts) - 1:
                time.sleep(0.5)
        media_ready = image_paths

    # Step 5: Compose
    log("Step 5/5: Composing video")
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(topic_for_meta)
    idx_str = f"-{run_index+1}" if args.batch > 1 else ""
    video_filename = f"{date_str}-{slug}{idx_str}.mp4"
    meta_filename = f"{date_str}-{slug}{idx_str}.json"
    video_path = str(output_dir / video_filename)
    meta_path = str(output_dir / meta_filename)

    if args.footage_dir:
        duration = compose_from_footage(
            args.footage_dir, audio_path, video_path,
            aspect=args.aspect, transition=args.transition,
            max_clip_duration=args.clip_duration,
        )
    else:
        duration = compose_from_images(
            media_ready, audio_path, video_path,
            aspect=args.aspect, transition=args.transition,
        )

    full_metadata = {
        **metadata,
        "duration": round(duration, 1),
        "language": args.language,
        "aspect": args.aspect,
        "script": script,
        "footage_mode": bool(args.footage_dir),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "video_path": str(Path(video_path).resolve()),
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(full_metadata, f, ensure_ascii=False, indent=2)

    return {
        "ok": True,
        "video_path": str(Path(video_path).resolve()),
        "meta_path": str(Path(meta_path).resolve()),
        "title": full_metadata["title"],
        "description": full_metadata["description"],
        "tags": full_metadata["tags"],
        "duration": round(duration, 1),
        "aspect": args.aspect,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a short-form video")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--topic", help="Video topic (triggers LLM script generation)")
    group.add_argument("--script", help="Direct script text")
    parser.add_argument("--language", default="zh", choices=["zh", "en"])
    parser.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "1:1"],
                        help="Video aspect ratio (default: 9:16)")
    parser.add_argument("--footage-dir", default="",
                        help="Directory of pre-downloaded video clips (enables footage mode)")
    parser.add_argument("--clip-duration", type=int, default=5,
                        help="Max seconds per video clip in footage mode (default: 5)")
    parser.add_argument("--transition", default="none", choices=["none", "fade"],
                        help="Transition between clips/images (default: none)")
    parser.add_argument("--n-images", type=int, default=5,
                        help="Number of AI images in image mode (default: 5)")
    parser.add_argument("--duration-hint", type=int, default=45,
                        help="Target duration hint in seconds (default: 45)")
    parser.add_argument("--batch", type=int, default=1,
                        help="Number of videos to generate (default: 1)")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--assets-dir", default="")
    args = parser.parse_args()

    output_dir = ensure_dir(args.output_dir)
    assets_dir = ensure_dir(args.assets_dir or str(output_dir / "assets"))

    # Early validation
    if not args.footage_dir or not args.script:
        require_env("SILICONFLOW_API_KEY")

    results = []
    for i in range(args.batch):
        if args.batch > 1:
            log(f"\n{'='*50}\nGenerating video {i+1}/{args.batch}\n{'='*50}")
        try:
            result = run_once(args, output_dir, assets_dir, i)
            results.append(result)
            print(f"\n✅ Video {i+1} ready: {result['video_path']}")
        except Exception as e:
            log(f"  ❌ Video {i+1} failed: {e}")
            results.append({"ok": False, "error": str(e)})

    # Final summary
    successful = [r for r in results if r.get("ok")]
    print(f"\n{'='*60}")
    print(f"✅ Generated {len(successful)}/{args.batch} videos in {args.output_dir}")
    for r in successful:
        print(f"   {Path(r['video_path']).name}  ({r['duration']}s, {r['aspect']})")
    print(f"{'='*60}")

    print("\n__RESULT_JSON__")
    if args.batch == 1:
        print(json.dumps(results[0] if results else {"ok": False, "error": "no results"}, ensure_ascii=False))
    else:
        print(json.dumps({"ok": bool(successful), "videos": results, "total": len(successful)}, ensure_ascii=False))

    if not successful:
        sys.exit(1)


if __name__ == "__main__":
    main()
