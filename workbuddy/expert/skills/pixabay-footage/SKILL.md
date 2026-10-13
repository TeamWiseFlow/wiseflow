---
name: "pixabay-footage"
description: "Search and download copyright-free images and video clips from Pixabay"
description_zh: "Search and download copyright-free images and video clips from Pixabay"
description_en: "pixabay-footage: native Xiaobei workflows, tools and reusable resources."
version: "0.3.2"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。


# Pixabay Footage — Pexels 之外的备选图片/视频素材

Use this skill when:
- Pexels results are not suitable or quota is exhausted
- You need alternative copyright-free images or video clips
- Preparing visual assets for content creation

**Prerequisites**: `PIXABAY_API_KEY` must be set. Register free at https://pixabay.com/api/docs/

---

## Usage

通过 PATH 调用 wrapper，无需拼接脚本路径。

### 下载图片

```bash
pixabay-footage \
  --type image \
  --terms "sunset,ocean,forest" \
  --aspect 16:9 \
  --output-dir ./assets/images \
  [--max-clips 15]
```

### 下载视频

```bash
pixabay-footage \
  --type video \
  --terms "sunset,ocean" \
  --aspect 9:16 \
  --output-dir ./video_assets/footage \
  --min-duration 5 \
  --max-duration 30
```

**重要**：视频下载**一次只允许下载一个**（脚本已强制 `--max-clips=1`），不允许批量下载。下载时应根据 content-check 报告的时长缺口，通过 `--min-duration` 和 `--max-duration` 精确匹配所需时长，不要下载远超需求的素材。

Same interface as `pexels-footage`. Output format identical.

---

## When to Choose Pixabay vs Pexels

| | Pixabay | Pexels |
|-|---------|--------|
| Photo quality | Good | High |
| Photo count | 4M+ | 3M+ |
| Video quality | Good (HD) | Higher (HD/4K) |
| Video count | 2M+ | 1M+ |
| Rate limits | 100 req/min (free) | 200 req/hour (free) |
| Best for | Objects, abstract, concepts | People, nature, lifestyle |

Pexels is the **primary** footage source (higher quality). Fall back to Pixabay if Pexels results are insufficient or rate-limited.

---

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--terms` | required | Comma-separated search keywords (one per scene) |
| `--type` | `video` | `image` or `video` |
| `--aspect` | `9:16` | `9:16` (portrait) \| `16:9` (landscape) \| `1:1` (square) |
| `--output-dir` | required | Directory to save downloaded files |
| `--min-duration` | `5` | Minimum clip duration in seconds (video only) |
| `--max-duration` | none | Maximum clip duration in seconds (video only). **强烈建议设置**，避免下载过长的素材 |
| `--max-clips` | `1` (video) / `15` (image) | Maximum total files to download. **视频类型强制为 1** |

---

## Output

Same JSON structure as pexels-footage:
- `--type image` → `{"ok": true, "images": [...], "total": N, "output_dir": "..."}`
- `--type video` → `{"ok": true, "clips": [...], "total": N, "output_dir": "..."}`

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PIXABAY_API_KEY` | Pixabay API key (required) |
