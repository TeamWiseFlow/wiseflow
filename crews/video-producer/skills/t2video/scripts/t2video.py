#!/usr/bin/env python3
"""
t2video — Text-to-Video pipeline (MoneyPrinterTurbo style)

Pipeline:
  topic/script → LLM script → SiliconFlow TTS → video materials → MoviePy → MP4

Material modes:
  default        : AI-generated images via SiliconFlow Images API
  --footage-dir  : local video clips (.mp4/.mov/.avi)
  --images-dir   : local image files (.jpg/.png)
  --auto-gen-video: AI video clips via SiliconFlow Video API (slow, 1-5 min each)

Environment Variables:
  SILICONFLOW_API_KEY   Required for LLM + TTS + image/video generation
  LLM_API_KEY           Override LLM key (defaults to SILICONFLOW_API_KEY)
  LLM_API_BASE          LLM base URL (default: https://api.siliconflow.cn/v1)
  LLM_MODEL             LLM model name (default: Qwen/Qwen2.5-7B-Instruct)
"""

import argparse
import glob
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

# ── Constants ──────────────────────────────────────────────────────────────────

SF_BASE_URL = "https://api.siliconflow.cn/v1"
SF_TTS_ENDPOINT = "/audio/speech"
SF_IMG_ENDPOINT = "/images/generations"
SF_VIDEO_SUBMIT_ENDPOINT = "/video/submit"
SF_VIDEO_STATUS_ENDPOINT = "/video/status"

DEFAULT_TTS_VOICE = "FishAudio/speech-01-hd"
DEFAULT_TTS_MODEL = "FunAudioLLM/CosyVoice2-0.5B"
DEFAULT_IMG_MODEL = "black-forest-labs/FLUX.1-schnell"
DEFAULT_VIDEO_MODEL = "Wan-AI/Wan2.2-T2V-A14B"
DEFAULT_LLM_MODEL = "Qwen/Qwen2.5-7B-Instruct"

ASPECT_RESOLUTIONS = {
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
    "1:1": (1080, 1080),
}

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".webm", ".mkv"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

PLACEHOLDER_COLOR = (30, 30, 50)


# ── Utilities ──────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def err(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr, flush=True)


def die(msg: str) -> None:
    err(msg)
    sys.exit(1)


def require_env(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        die(f"Environment variable {name} is not set.")
    return val


def ensure_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def slugify(text: str, max_len: int = 20) -> str:
    text = re.sub(r"[^\w\u4e00-\u9fff]+", "-", text).strip("-")
    return text[:max_len]


def get_audio_duration(audio_path: str) -> float:
    """Get audio duration using moviepy."""
    from moviepy.editor import AudioFileClip
    with AudioFileClip(audio_path) as clip:
        return clip.duration


# ── LLM ───────────────────────────────────────────────────────────────────────

def llm_generate_script(topic: str, language: str) -> str:
    """Generate a narration script from a topic via LLM."""
    api_key = os.environ.get("LLM_API_KEY", "").strip() or require_env("SILICONFLOW_API_KEY")
    api_base = os.environ.get("LLM_API_BASE", SF_BASE_URL).rstrip("/")
    model = os.environ.get("LLM_MODEL", DEFAULT_LLM_MODEL)

    lang_hint = "Chinese (Mandarin)" if language == "zh" else "English"
    prompt = (
        f"You are a professional short-video scriptwriter. "
        f"Write a narration script for a 30-60 second video about: {topic}\n"
        f"Requirements:\n"
        f"- Language: {lang_hint}\n"
        f"- Tone: engaging, conversational, suitable for voiceover\n"
        f"- Length: 100-200 words\n"
        f"- No stage directions, just the spoken narration text\n"
        f"Output only the script text, nothing else."
    )

    log(f"LLM: generating script for topic='{topic}'")
    resp = requests.post(
        f"{api_base}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 512},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def llm_generate_scene_prompts(script: str, n_scenes: int) -> list[str]:
    """Generate image/video prompts for each scene from the script."""
    api_key = os.environ.get("LLM_API_KEY", "").strip() or require_env("SILICONFLOW_API_KEY")
    api_base = os.environ.get("LLM_API_BASE", SF_BASE_URL).rstrip("/")
    model = os.environ.get("LLM_MODEL", DEFAULT_LLM_MODEL)

    prompt = (
        f"Given this video narration script:\n\n{script}\n\n"
        f"Generate exactly {n_scenes} visual scene descriptions in English, "
        f"suitable as image/video generation prompts. "
        f"Each prompt should be vivid, cinematic, 1-2 sentences. "
        f"Output as a JSON array of strings, nothing else."
    )

    log(f"LLM: generating {n_scenes} scene prompts")
    resp = requests.post(
        f"{api_base}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 512},
        timeout=60,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"].strip()
    # Extract JSON array
    match = re.search(r"\[.*\]", content, re.DOTALL)
    if match:
        return json.loads(match.group())
    # Fallback: split by newlines
    return [line.strip() for line in content.split("\n") if line.strip()][:n_scenes]


# ── TTS (SiliconFlow) ──────────────────────────────────────────────────────────

def tts_generate(text: str, voice: str, output_path: str) -> str:
    """Generate audio from text via SiliconFlow TTS API. Returns output_path."""
    api_key = require_env("SILICONFLOW_API_KEY")
    api_base = os.environ.get("LLM_API_BASE", SF_BASE_URL).rstrip("/")

    log(f"TTS: generating audio, voice='{voice}', length={len(text)} chars")
    payload = {
        "model": DEFAULT_TTS_MODEL,
        "input": text,
        "voice": voice,
        "response_format": "mp3",
    }

    resp = requests.post(
        f"{api_base}{SF_TTS_ENDPOINT}",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(resp.content)
    log(f"TTS: saved → {output_path}")
    return output_path


# ── Image Generation (SiliconFlow) ────────────────────────────────────────────

def generate_image(prompt: str, output_path: str, image_size: str = "1024x1024") -> str | None:
    """Generate one image via SiliconFlow API. Returns output_path or None on failure."""
    api_key = require_env("SILICONFLOW_API_KEY")
    api_base = os.environ.get("LLM_API_BASE", SF_BASE_URL).rstrip("/")

    try:
        resp = requests.post(
            f"{api_base}{SF_IMG_ENDPOINT}",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": DEFAULT_IMG_MODEL, "prompt": prompt, "image_size": image_size, "batch_size": 1},
            timeout=120,
        )
        resp.raise_for_status()
        url = resp.json()["images"][0]["url"]
        img_data = requests.get(url, timeout=60).content
        with open(output_path, "wb") as f:
            f.write(img_data)
        return output_path
    except Exception as e:
        err(f"Image generation failed for '{prompt[:40]}...': {e}")
        return None


# ── Video Generation (SiliconFlow Wan2.2) ─────────────────────────────────────

def generate_video_clip(prompt: str, output_path: str, image_size: str = "720x1280",
                         poll_interval: int = 15, timeout: int = 600) -> str | None:
    """Generate a video clip via SiliconFlow Video API (async). Returns output_path or None."""
    api_key = require_env("SILICONFLOW_API_KEY")
    api_base = os.environ.get("LLM_API_BASE", SF_BASE_URL).rstrip("/")

    log(f"Video gen: submitting job for '{prompt[:50]}...'")
    try:
        resp = requests.post(
            f"{api_base}{SF_VIDEO_SUBMIT_ENDPOINT}",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": DEFAULT_VIDEO_MODEL, "prompt": prompt, "image_size": image_size},
            timeout=30,
        )
        resp.raise_for_status()
        request_id = resp.json().get("requestId")
        if not request_id:
            err("No requestId in video gen response")
            return None
    except Exception as e:
        err(f"Video gen submit failed: {e}")
        return None

    log(f"Video gen: polling requestId={request_id} (timeout={timeout}s)")
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(poll_interval)
        try:
            status_resp = requests.get(
                f"{api_base}{SF_VIDEO_STATUS_ENDPOINT}/{request_id}",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30,
            )
            status_resp.raise_for_status()
            data = status_resp.json()
            status = data.get("status", "")
            if status == "Succeed":
                video_url = data.get("results", {}).get("videos", [{}])[0].get("url", "")
                if not video_url:
                    err("Video gen succeeded but no URL in response")
                    return None
                video_data = requests.get(video_url, timeout=120).content
                with open(output_path, "wb") as f:
                    f.write(video_data)
                log(f"Video gen: saved → {output_path}")
                return output_path
            elif status in ("Failed", "Error"):
                err(f"Video gen failed: {data}")
                return None
            else:
                log(f"Video gen: status={status}, waiting...")
        except Exception as e:
            err(f"Video gen poll error: {e}")

    err(f"Video gen timed out after {timeout}s")
    return None


# ── Video Composition (MoviePy) ────────────────────────────────────────────────

def make_placeholder_clip(duration: float, resolution: tuple, color: tuple):
    """Create a solid-color placeholder clip."""
    from moviepy.editor import ColorClip
    return ColorClip(size=resolution, color=color, duration=duration)


def image_to_clip(image_path: str, duration: float, resolution: tuple):
    """Convert an image to a video clip with zoom effect."""
    from moviepy.editor import ImageClip
    clip = ImageClip(image_path, duration=duration)
    # Resize to fill resolution
    clip = clip.resize(resolution)
    # Center crop if needed
    if clip.size[0] != resolution[0] or clip.size[1] != resolution[1]:
        x_center = clip.size[0] / 2
        y_center = clip.size[1] / 2
        clip = clip.crop(
            x_center=x_center, y_center=y_center,
            width=resolution[0], height=resolution[1],
        )
    return clip


def video_to_clip(video_path: str, max_duration: float, resolution: tuple):
    """Trim and resize a video clip to fit target resolution."""
    from moviepy.editor import VideoFileClip
    clip = VideoFileClip(video_path).without_audio()
    if clip.duration > max_duration:
        clip = clip.subclip(0, max_duration)
    # Resize to fill
    clip = clip.resize(resolution)
    # Center crop
    if clip.size[0] != resolution[0] or clip.size[1] != resolution[1]:
        x_center = clip.size[0] / 2
        y_center = clip.size[1] / 2
        clip = clip.crop(
            x_center=x_center, y_center=y_center,
            width=resolution[0], height=resolution[1],
        )
    return clip


def compose_video(
    material_paths: list[str],
    material_type: str,  # "image" | "video"
    audio_path: str,
    output_path: str,
    aspect: str,
    clip_duration: float,
    transition: str,
) -> str:
    """Compose final video from materials + audio. Returns output_path."""
    from moviepy.editor import AudioFileClip, CompositeVideoClip, concatenate_videoclips

    resolution = ASPECT_RESOLUTIONS.get(aspect, (1080, 1920))
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration

    log(f"Compose: {len(material_paths)} {material_type}s, duration={total_duration:.1f}s, aspect={aspect}")

    if not material_paths:
        log("Compose: no materials — using placeholder")
        placeholder = make_placeholder_clip(total_duration, resolution, PLACEHOLDER_COLOR)
        final = placeholder.set_audio(audio)
        final.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac",
                              verbose=False, logger=None)
        return output_path

    # Build clips list covering total_duration
    clips = []
    elapsed = 0.0
    idx = 0
    while elapsed < total_duration:
        path = material_paths[idx % len(material_paths)]
        remaining = total_duration - elapsed
        dur = min(clip_duration, remaining)
        try:
            if material_type == "image":
                clip = image_to_clip(path, dur, resolution)
            else:
                clip = video_to_clip(path, dur, resolution)
        except Exception as e:
            err(f"Failed to load '{path}': {e} — using placeholder")
            clip = make_placeholder_clip(dur, resolution, PLACEHOLDER_COLOR)
        clips.append(clip)
        elapsed += dur
        idx += 1

    if transition == "fade" and len(clips) > 1:
        from moviepy.editor import VideoFileClip as VFC  # noqa
        faded = []
        for i, c in enumerate(clips):
            if i > 0:
                c = c.crossfadein(0.3)
            faded.append(c)
        clips = faded

    video = concatenate_videoclips(clips, method="compose")
    video = video.set_audio(audio).set_duration(total_duration).set_fps(30)
    video.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac",
                          verbose=False, logger=None)
    log(f"Compose: written → {output_path}")
    return output_path


# ── Material Collection ────────────────────────────────────────────────────────

def collect_footage(footage_dir: str) -> list[str]:
    paths = []
    for ext in VIDEO_EXTS:
        paths.extend(glob.glob(os.path.join(footage_dir, f"*{ext}")))
        paths.extend(glob.glob(os.path.join(footage_dir, f"*{ext.upper()}")))
    return sorted(paths)


def collect_images(images_dir: str) -> list[str]:
    paths = []
    for ext in IMAGE_EXTS:
        paths.extend(glob.glob(os.path.join(images_dir, f"*{ext}")))
        paths.extend(glob.glob(os.path.join(images_dir, f"*{ext.upper()}")))
    return sorted(paths)


def ai_generate_images(scene_prompts: list[str], assets_dir: str,
                        image_size: str) -> list[str]:
    """Generate AI images for each scene prompt. Returns list of saved paths."""
    paths = []
    for i, prompt in enumerate(scene_prompts):
        out = os.path.join(assets_dir, f"scene_{i+1:02d}.png")
        if os.path.exists(out):
            log(f"Image {i+1}: using cached {out}")
            paths.append(out)
            continue
        log(f"Image {i+1}/{len(scene_prompts)}: generating...")
        result = generate_image(prompt, out, image_size)
        if result:
            paths.append(result)
        else:
            err(f"Image {i+1} generation failed, skipping")
    return paths


def ai_generate_video_clips(scene_prompts: list[str], assets_dir: str,
                              image_size: str) -> list[str]:
    """Generate AI video clips for each scene. Returns list of saved paths."""
    paths = []
    for i, prompt in enumerate(scene_prompts):
        out = os.path.join(assets_dir, f"clip_{i+1:02d}.mp4")
        if os.path.exists(out):
            log(f"Clip {i+1}: using cached {out}")
            paths.append(out)
            continue
        log(f"Clip {i+1}/{len(scene_prompts)}: generating (may take 1-5 min)...")
        result = generate_video_clip(prompt, out, image_size)
        if result:
            paths.append(result)
        else:
            err(f"Clip {i+1} generation failed, skipping")
    return paths


# ── Main Pipeline ──────────────────────────────────────────────────────────────

def run_once(
    topic: str,
    script: str,
    language: str,
    aspect: str,
    footage_dir: str | None,
    images_dir: str | None,
    auto_gen_video: bool,
    voice: str,
    clip_duration: float,
    transition: str,
    n_images: int,
    output_dir: str,
    run_idx: int = 1,
) -> dict:
    """Run the full pipeline once. Returns result dict."""
    resolution = ASPECT_RESOLUTIONS.get(aspect, (1080, 1920))
    w, h = resolution
    image_size = f"{w}x{h}" if w <= h else f"{h}x{w}"  # always WxH

    # Date slug for filenames
    date_slug = datetime.now().strftime("%Y-%m-%d")
    topic_slug = slugify(topic or script, 20)
    base_name = f"{date_slug}-{topic_slug}"
    if run_idx > 1:
        base_name += f"-{run_idx}"

    assets_dir = ensure_dir(os.path.join(output_dir, "assets", base_name))

    # Step 1: Script
    if script:
        final_script = script
        log("Script: using provided script")
    else:
        log(f"Script: generating from topic='{topic}'")
        final_script = llm_generate_script(topic, language)
        log(f"Script: {final_script[:120]}...")

    # Step 2: TTS narration
    audio_path = str(assets_dir / "audio.mp3")
    if not os.path.exists(audio_path):
        tts_generate(final_script, voice, audio_path)
    else:
        log(f"TTS: using cached {audio_path}")
    audio_duration = get_audio_duration(audio_path)
    log(f"Audio: duration={audio_duration:.1f}s")

    # Step 3: Collect / generate materials
    material_type = "image"
    material_paths = []

    if footage_dir:
        material_paths = collect_footage(footage_dir)
        material_type = "video"
        if not material_paths:
            err(f"No video files found in '{footage_dir}'")
        else:
            log(f"Materials: {len(material_paths)} local video clips from {footage_dir}")

    elif images_dir:
        material_paths = collect_images(images_dir)
        material_type = "image"
        if not material_paths:
            err(f"No image files found in '{images_dir}'")
        else:
            log(f"Materials: {len(material_paths)} local images from {images_dir}")

    elif auto_gen_video:
        material_type = "video"
        # Generate scene count based on audio duration
        n_scenes = max(2, int(audio_duration / 8))
        scene_prompts = llm_generate_scene_prompts(final_script, n_scenes)
        log(f"Materials: generating {n_scenes} AI video clips (this may take {n_scenes * 3}-{n_scenes * 5} min)")
        material_paths = ai_generate_video_clips(scene_prompts, str(assets_dir), image_size)
        if not material_paths:
            log("AI video gen failed entirely — falling back to AI images")
            material_type = "image"
            material_paths = ai_generate_images(scene_prompts, str(assets_dir), "1024x1024")

    else:
        # Default: AI-generated images
        material_type = "image"
        scene_prompts = llm_generate_scene_prompts(final_script, n_images)
        log(f"Materials: generating {n_images} AI images")
        material_paths = ai_generate_images(scene_prompts, str(assets_dir), "1024x1024")

    # Step 4: Compose
    output_video = os.path.join(output_dir, f"{base_name}.mp4")
    compose_video(
        material_paths=material_paths,
        material_type=material_type,
        audio_path=audio_path,
        output_path=output_video,
        aspect=aspect,
        clip_duration=clip_duration,
        transition=transition,
    )

    # Step 5: Save metadata
    meta = {
        "topic": topic,
        "script": final_script,
        "audio_duration": round(audio_duration, 1),
        "aspect": aspect,
        "voice": voice,
        "material_mode": "footage" if footage_dir else ("images" if images_dir else ("ai-video" if auto_gen_video else "ai-images")),
        "material_count": len(material_paths),
        "output": output_video,
        "generated_at": datetime.now().isoformat(),
    }
    meta_path = os.path.join(output_dir, f"{base_name}.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    log(f"✅ Done: {output_video}")
    return meta


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="t2video — Text-to-Video pipeline")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--topic", help="Video topic (LLM generates script)")
    src.add_argument("--script", help="Direct script text (skips LLM)")

    mat = parser.add_mutually_exclusive_group()
    mat.add_argument("--footage-dir", help="Directory of local video clips")
    mat.add_argument("--images-dir", help="Directory of local image files")
    mat.add_argument("--auto-gen-video", action="store_true", help="Generate video clips via SiliconFlow")

    parser.add_argument("--language", default="zh", choices=["zh", "en"])
    parser.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "1:1"])
    parser.add_argument("--voice", default=DEFAULT_TTS_VOICE,
                        help=f"SiliconFlow TTS voice (default: {DEFAULT_TTS_VOICE})")
    parser.add_argument("--clip-duration", type=float, default=5.0,
                        help="Max seconds per footage/image clip (default: 5)")
    parser.add_argument("--transition", default="none", choices=["none", "fade"])
    parser.add_argument("--n-images", type=int, default=5,
                        help="Number of AI images in default mode (default: 5)")
    parser.add_argument("--batch", type=int, default=1, help="Generate N versions")
    parser.add_argument("--output-dir", required=True, help="Output directory")

    args = parser.parse_args()

    ensure_dir(args.output_dir)

    # Verify SILICONFLOW_API_KEY early
    require_env("SILICONFLOW_API_KEY")

    results = []
    errors = []
    for i in range(1, args.batch + 1):
        if args.batch > 1:
            log(f"── Batch {i}/{args.batch} ──")
        try:
            meta = run_once(
                topic=args.topic or "",
                script=args.script or "",
                language=args.language,
                aspect=args.aspect,
                footage_dir=args.footage_dir,
                images_dir=args.images_dir,
                auto_gen_video=args.auto_gen_video,
                voice=args.voice,
                clip_duration=args.clip_duration,
                transition=args.transition,
                n_images=args.n_images,
                output_dir=args.output_dir,
                run_idx=i,
            )
            results.append(meta)
        except Exception as e:
            err(f"Batch {i} failed: {e}")
            errors.append(str(e))

    if args.batch > 1:
        log(f"Batch complete: {len(results)} succeeded, {len(errors)} failed")
        if results:
            log("Output files:")
            for r in results:
                log(f"  {r['output']}")

    if errors and not results:
        sys.exit(1)


if __name__ == "__main__":
    main()
