#!/usr/bin/env python3
"""MiniMax Hailuo 视频生成 + 背景音乐生成。

直连 MiniMax V2 异步任务端点：
  - 视频：POST /v2/video_generation → GET /v2/query/video_generation/{task_id}
  - 音乐：POST /v1/music_generation（同步，返回音频字节）

模型：MiniMax-H3（视频）、music-3.0（音乐）。
鉴权：HTTP header `Authorization: Bearer ${MINIMAX_API_KEY}`。

H3 多模态参考（content[] + role）支持的输入组合：
  - 文生视频：仅一个 text
  - 图生视频-首帧：text + 1 image_url（role=first_frame 或不填）
  - 图生视频-尾帧：text + 1 image_url（role=last_frame）
  - 图生视频-首尾帧：text + 2 image_url（role 分别 first_frame/last_frame）
  - 多模态参考生视频：text + reference_image/reference_video/reference_audio 组合
    （不可仅输入音频，须至少 1 个参考视频或图片）

图生视频与多模态参考互斥：content 中出现 reference_* 任一 role，就不能再出现
first_frame/last_frame（反之亦然）。
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# aigc_common.py 与本脚本同目录（skills/aigc-video-gen/scripts/）
sys.path.insert(0, str(Path(__file__).resolve().parent))
from aigc_common import (  # noqa: E402
    HttpError,
    TaskFailed,
    append_decision,
    die,
    download,
    ensure_safe_output,
    generate,
    get_json,
    log,
    post_json,
    resolve_image,
    resolve_media_url,
    resolve_prev_segment,
)

# ---- MiniMax 端点与常量 -------------------------------------------------------

MM_BASE = "https://api.minimaxi.com"
MM_VIDEO_CREATE = f"{MM_BASE}/v2/video_generation"
MM_VIDEO_QUERY = f"{MM_BASE}/v2/query/video_generation/{{task_id}}"
MM_MUSIC_CREATE = f"{MM_BASE}/v1/music_generation"

MM_VIDEO_MODELS = {
    "hailuo-h3": "MiniMax-H3",
}
MM_MUSIC_MODEL = "music-3.0"

MM_POLL_INTERVAL = 10  # 官方推荐轮询间隔 10 秒
MM_TIMEOUT = 900


# ---- 鉴权 --------------------------------------------------------------------

def mm_headers(api_key: str) -> dict:
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


# ---- MiniMax 视频生成 --------------------------------------------------------

def mm_video_build_content(model: str, args: argparse.Namespace) -> list[dict]:
    """构造 MiniMax V2 视频 content[] 数组。

    content[] 每个元素：type(text/image_url/video_url/audio_url) + role(可选)
    role 取值：first_frame / last_frame / reference_image / reference_video / reference_audio

    H3 多模态参考约束（官方文档）：
      - 图生视频与多模态参考互斥：reference_* 任一出现，就不能有 first_frame/last_frame
      - 多模态参考不可仅输入音频：须至少 1 个参考视频或图片
      - 每次请求必须包含一个非空 text 项（prompt 必填）
    """
    items: list[dict] = [{"type": "text", "text": args.prompt}]

    # 图生视频路径：--image / --last-frame
    if args.image:
        items.append(
            {"type": "image_url", "image_url": {"url": resolve_image(args.image)}, "role": "first_frame"}
        )
    if args.last_frame:
        items.append(
            {"type": "image_url", "image_url": {"url": resolve_image(args.last_frame)}, "role": "last_frame"}
        )

    # 多模态参考路径：--ref-image / --ref-video / --ref-audio
    if args.ref_image:
        items.append(
            {"type": "image_url", "image_url": {"url": resolve_image(args.ref_image)}, "role": "reference_image"}
        )
    if args.ref_video:
        items.append(
            {"type": "video_url", "video_url": {"url": resolve_media_url(args.ref_video, "ref-video")}, "role": "reference_video"}
        )
    if args.ref_audio:
        items.append(
            {"type": "audio_url", "audio_url": {"url": resolve_media_url(args.ref_audio, "ref-audio")}, "role": "reference_audio"}
        )

    return items


def mm_video_build_payload(model: str, args: argparse.Namespace) -> dict:
    """构造 MiniMax V2 视频生成请求体。

    通用字段：model / content[] / duration / resolution / ratio
    i2v 场景宽高比由输入图片决定，ratio 恒为 adaptive（官方文档）；此处仅在用户显式
    传 --ratio 时带上，否则省略让服务端自判。
    """
    payload: dict = {
        "model": model,
        "content": mm_video_build_content(model, args),
        "duration": args.duration,
        "resolution": args.resolution,
    }
    # t2v 场景 ratio 必填且不能为 adaptive；i2v 由图片决定 ratio 应省略。
    # 此处简化：仅在无 --image 时带 ratio（对齐官方示例的 t2va 必填 ratio 约束）。
    if args.ratio and not args.image:
        payload["ratio"] = args.ratio
    return payload


def mm_video_submit(model: str, args: argparse.Namespace, api_key: str) -> str:
    payload = mm_video_build_payload(model, args)
    resp = post_json(MM_VIDEO_CREATE, payload, mm_headers(api_key), timeout=60)
    # V2 响应：顶层 task_id（V2 不再用 base_resp 信封，错误走 HTTP 状态码）
    task_id = resp.get("task_id") or resp.get("id")
    if not task_id:
        die(
            f"minimax video submit: no task id in response: "
            f"raw={json.dumps(resp, ensure_ascii=False)}"
        )
    return task_id


def mm_video_poll(task_id: str, api_key: str) -> str:
    """轮询 MiniMax V2 视频任务，成功时返回 task.content.url（成片下载地址）。"""
    url = MM_VIDEO_QUERY.format(task_id=task_id)
    deadline = time.time() + MM_TIMEOUT
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        resp = get_json(url, mm_headers(api_key), timeout=30)
        task = resp.get("task") or resp  # V2 响应在 task 字段下，兜底兼容顶层
        status = (task.get("status") or "").lower()
        log(f"minimax video poll #{attempt}: status={status}")
        if status == "succeeded":
            content = task.get("content") or {}
            video_url = content.get("url") or content.get("video_url")
            if not video_url:
                die(f"minimax video succeeded but no content.url: {json.dumps(resp, ensure_ascii=False)}")
            return video_url
        if status in {"failed", "cancelled"}:
            err = task.get("error") or {}
            raise TaskFailed(
                f"minimax video task {status}: code={err.get('code', '')} msg={err.get('message', '')}"
            )
        time.sleep(MM_POLL_INTERVAL)
    die(f"minimax video timed out after {MM_TIMEOUT}s (task {task_id})")


def mm_video_candidates(args: argparse.Namespace) -> list[str]:
    """MiniMax 视频候选链：目前仅 MiniMax-H3。--model 显式指定时只用该模型。"""
    return [MM_VIDEO_MODELS["hailuo-h3"]]


# ---- MiniMax 音乐生成 --------------------------------------------------------

def mm_music_build_payload(args: argparse.Namespace) -> dict:
    """构造 MiniMax 音乐生成请求体。

    官方字段：model(music-3.0) / prompt(风格描述) / lyrics(歌词,可含 [verse]/[chorus] 标签)
    / audio_setting(sample_rate/bitrate/format)。
    """
    payload: dict = {
        "model": MM_MUSIC_MODEL,
        "prompt": args.prompt,
    }
    lyrics = getattr(args, "lyrics", None)
    if lyrics:
        payload["lyrics"] = lyrics
    audio_setting: dict = {"format": "mp3", "sample_rate": 44100, "bitrate": 256000}
    payload["audio_setting"] = audio_setting
    return payload


def mm_music_generate(args: argparse.Namespace, api_key: str) -> bytes:
    """MiniMax 音乐生成：POST /v1/music_generation，返回音频二进制。

    官方示例为同步 POST，响应体即音频字节流（或 JSON 含 base64 audio 字段）。
    """
    payload = mm_music_build_payload(args)
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        MM_MUSIC_CREATE, data=data, headers=mm_headers(api_key), method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            content_type = resp.headers.get("Content-Type", "")
            body = resp.read()
            if "audio" in content_type or content_type == "application/octet-stream":
                return body
            json_resp = json.loads(body.decode("utf-8"))
            audio_field = json_resp.get("audio") or (json_resp.get("data") or {}).get("audio")
            if audio_field:
                return base64.b64decode(audio_field)
            die(f"minimax music: no audio in response: {json.dumps(json_resp, ensure_ascii=False)}")
    except urllib.error.HTTPError as exc:
        die(f"minimax music HTTP {exc.code}: {exc.read().decode(errors='replace')}")
    except urllib.error.URLError as exc:
        die(f"minimax music URLError: {exc.reason}")


# ---- 调度 --------------------------------------------------------------------

def run_one(platform: str, model: str, args: argparse.Namespace, api_key: str) -> str:
    """Submit + poll for a single MiniMax model. Returns video URL or raises."""
    task_id = mm_video_submit(model, args, api_key)
    log(f"minimax video task submitted: {task_id} (model={model})")
    return mm_video_poll(task_id, api_key)


def cmd_music(args: argparse.Namespace) -> None:
    """MiniMax 背景音乐生成子命令。

    流程：mm_music_generate（同步 POST /v1/music_generation）→ 写文件。
    仅 minimax 平台支持，需 MINIMAX_API_KEY。
    """
    api_key = (os.environ.get("MINIMAX_API_KEY") or "").strip()
    if not api_key:
        die("MINIMAX_API_KEY 未设置 —— 请实时提醒用户提供 key,然后交 IT engineer 配置")
    output_path = ensure_safe_output(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    log(f"minimax music generation: prompt={args.prompt!r}")
    audio_bytes = mm_music_generate(args, api_key)
    output_path.write_bytes(audio_bytes)
    meta = output_path.with_suffix(".json")
    meta.write_text(
        json.dumps(
            {
                "platform": "minimax",
                "capability": "music",
                "model": MM_MUSIC_MODEL,
                "prompt": args.prompt,
                "lyrics": getattr(args, "lyrics", None),
                "file": str(output_path),
                "bytes": len(audio_bytes),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"[done] music saved: {output_path}")
    print(f"[done] metadata:    {meta}")


def cmd_video(args: argparse.Namespace) -> None:
    if args.duration < 4 or args.duration > 15:
        die("--duration 必须在 4–15 秒之间（MiniMax H3 约束）")

    # --prev-segment: 抽取上一段末帧作为本段首帧（人物故事首尾帧对齐）
    resolve_prev_segment(args)

    # H3 多模态参考约束校验（官方文档）
    has_i2v = bool(args.image or args.last_frame)
    has_ref = bool(args.ref_image or args.ref_video or args.ref_audio)
    if has_i2v and has_ref:
        die(
            "图生视频（--image/--last-frame）与多模态参考（--ref-image/--ref-video/--ref-audio）"
            "互斥：content 中出现 reference_* 任一 role，就不能有 first_frame/last_frame"
        )
    # 多模态参考不可仅输入音频：须至少 1 个参考视频或图片
    if args.ref_audio and not (args.ref_image or args.ref_video):
        die(
            "多模态参考不可仅输入音频：须至少 1 个参考视频（--ref-video）或图片（--ref-image）"
        )

    api_key = (os.environ.get("MINIMAX_API_KEY") or "").strip()
    if not api_key:
        die("MINIMAX_API_KEY 未设置 —— 请实时提醒用户提供 key,然后交 IT engineer 配置")

    candidates = [args.model] if args.model else mm_video_candidates(args)

    output_path = ensure_safe_output(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    mode = "r2v" if has_ref else ("i2v" if has_i2v else "t2v")
    log(
        f"platform=minimax mode={mode} candidates={candidates} "
        f"duration={args.duration}s ratio={args.ratio} resolution={args.resolution}"
    )
    video_url = generate("minimax", candidates, args, api_key, run_one)
    download(video_url, output_path)

    meta = output_path.with_suffix(".json")
    meta.write_text(
        json.dumps(
            {
                "platform": "minimax",
                "mode": mode,
                "model_candidates": candidates,
                "duration": args.duration,
                "ratio": args.ratio,
                "resolution": args.resolution,
                "video_url": video_url,
                "file": str(output_path),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"[done] video saved: {output_path}")
    print(f"[done] metadata:    {meta}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="MiniMax Hailuo video generation + music generation."
    )
    sub = parser.add_subparsers(dest="command")

    # ── 默认子命令：video（向后兼容，无子命令时走 video）──
    p_video = sub.add_parser("video", help="视频生成(默认,可省略 video 子命令)")
    p_video.add_argument("--prompt", required=True, help="画面+音频描述（声画同出）")
    p_video.add_argument("--image", default=None, help="首帧图片：URL 或本地路径（→ i2v）")
    p_video.add_argument("--last-frame", default=None, dest="last_frame", help="尾帧图片：URL 或本地路径（i2v 首尾帧）")
    p_video.add_argument("--ref-image", default=None, dest="ref_image", help="参考图片：URL 或本地路径（→ 多模态参考，角色/主体一致性）")
    p_video.add_argument("--ref-video", default=None, dest="ref_video", help="参考视频 URL（→ 多模态参考，需公网 URL）")
    p_video.add_argument("--ref-audio", default=None, dest="ref_audio", help="参考音频 URL（→ 多模态参考，须同时有 --ref-image 或 --ref-video）")
    p_video.add_argument("--duration", type=int, default=8, help="时长（秒），默认 8，H3 范围 4–15")
    p_video.add_argument("--ratio", default="9:16", help="宽高比，默认 9:16")
    p_video.add_argument("--resolution", default="720P", choices=["720P", "1080P"], help="分辨率，默认 720P")
    p_video.add_argument("--model", default=None, help="指定模型 id（关闭候选链 fallback）")
    p_video.add_argument("--output", required=True, help="输出 MP4 路径（相对工作区，须在 output_videos/tmp/fragments/artifacts 或 <platform>/outputs/ 下）")

    # ── music 子命令：minimax 背景音乐生成 ──
    p_music = sub.add_parser("music", help="MiniMax 背景音乐生成(需 MINIMAX_API_KEY)")
    p_music.add_argument("--prompt", required=True, help="音乐描述(风格/情绪/乐器)")
    p_music.add_argument("--duration", type=int, default=None, dest="music_duration", help="音乐时长(秒),不传走模型默认")
    p_music.add_argument("--output", required=True, help="输出音频路径(相对工作区,须在 output_videos/tmp/fragments/artifacts 或 <platform>/outputs/ 下)")

    return parser


def main() -> None:
    parser = build_parser()

    # 向后兼容：无子命令时，把全部 argv 当成 video 子命令的参数
    argv = sys.argv[1:]
    if not argv or argv[0].startswith("-"):
        argv = ["video"] + argv

    # video 子命令可省略：如果第一个 token 不是已知子命令，默认走 video
    known_subcommands = {"video", "music"}
    if argv and argv[0] not in known_subcommands:
        argv = ["video"] + argv

    args = parser.parse_args(argv)

    if args.command == "music":
        cmd_music(args)
    else:
        cmd_video(args)


if __name__ == "__main__":
    main()
