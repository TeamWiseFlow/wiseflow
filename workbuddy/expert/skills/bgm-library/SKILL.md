---
name: "bgm-library"
description: "搜索、筛选并下载 ccMixter 免版税背景音乐（仅 CC BY / CC BY-SA，商用安全），"
description_zh: "搜索、筛选并下载 ccMixter 免版税背景音乐（仅 CC BY / CC BY-SA，商用安全），"
description_en: "bgm-library: native Xiaobei workflows, tools and reusable resources."
version: "0.3.3"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。


# ccMixter 免版税背景音乐库

> **凭据**：无需 API key。ccMixter 是 Creative Commons 创建的社区 remix 站，全部音乐已带 CC 协议。

搜索、筛选并下载商用安全的免版税背景音乐，自动生成署名文件。供 `video-edit` / `video-producer` 的配乐环节使用，也可独立调用。

通过 PATH 调用 wrapper，无需拼接脚本路径：

```bash
bgm-library <command> [args]
```

## 协议过滤（默认开启）

只放行**商用安全**协议，任何含 NonCommercial (NC) 或 NoDerivs (ND) 的协议一律拦截：

- ✅ 允许：CC BY（署名）、CC BY-SA（署名-相同方式共享）
- ❌ 拦截：含 NC / ND 的任何协议

`--no-commercial-only` 可放开（不推荐，商用项目会侵权）。

---

## Commands

### `search [keywords...]` — 关键词 / 预设搜索

```bash
# 关键词搜
bgm-library search chill lofi --limit 5

# 预设搜
bgm-library search --preset travel
```

| Flag | Default | Description |
|------|---------|-------------|
| `-l, --limit <n>` | `10` | 最多返回条数 |
| `-p, --preset <name>` | — | 预设：`travel` / `tech` / `lofi` / `food` / `workout` |
| `--commercial-only` / `--no-commercial-only` | on | 协议过滤开关 |
| `--sort <field>` | `score` | `date` / `name` / `score` |

### `pick <theme>` — 按主题自动选曲并下载

按主题关键词搜、评分排序、自动下载最佳匹配。无精确匹配时回退到首关键词广搜。

```bash
bgm-library pick "chill lofi study" --output ./audio/
bgm-library pick "energetic workout motivation" --output ./audio/
```

| Flag | Default | Description |
|------|---------|-------------|
| `-o, --output <dir>` | `./public` | 输出目录 |
| `-l, --limit <n>` | `5` | 候选评估条数 |
| `--force` | off | 覆盖已存在文件 |

### `download <uploadId>` — 按 ccMixter upload ID 下载

```bash
bgm-library download 70473 --output ./audio/
```

| Flag | Default | Description |
|------|---------|-------------|
| `-o, --output <dir>` | `./public` | 输出目录 |
| `--force` | off | 覆盖已存在文件 |

### `presets` — 列出场景预设

```bash
bgm-library presets
```

| Preset | 场景 | Tags |
|--------|------|------|
| `travel` | 旅行 / Vlog | upbeat, travel, vlog, vacation, summer |
| `tech` | 科技 / 产品 | corporate, technology, digital, modern |
| `lofi` | 咖啡馆 / 学习 | lofi, chill, study, cafe, downtempo |
| `food` | 美食 / 生活 | acoustic, cooking, lifestyle, warm, light |
| `workout` | 运动 / 健身 | workout, gym, sport, energy, edm |

### `info <uploadId>` — 查看曲目详情（协议 / BPM / 时长 / 文件）

```bash
bgm-library info 70473
```

---

## Output

下载后落盘到 `--output` 目录：

- `*.mp3` — 音频文件（原文件名，非法字符替换为 `_`）
- `music_manifest.json` — 曲目元数据（供程序化读取）
- `ATTRIBUTION.txt` — TASL 格式自动署名（Title / Author / Source / License）

`music_manifest.json` 示例：

```json
{
  "tracks": [
    {
      "upload_id": 70473,
      "title": "The Fade Out",
      "artist": "coruscate",
      "source_url": "https://ccmixter.org/files/Coruscate/70473",
      "license_name": "Attribution (3.0)",
      "license_url": "http://creativecommons.org/licenses/by/3.0/",
      "file_name": "Coruscate_-_The_Fade_Out.mp3",
      "bpm": 92,
      "duration": "3:05",
      "downloaded_at": "2026-08-15T12:00:00.000Z"
    }
  ]
}
```

### ⚠️ 发布时必须附带署名

`ATTRIBUTION.txt` 是 CC 协议的法律要求。成片发布时把该文件内容写到视频描述 / 简介里，**不得省略**。

---

## 在 video-edit / video-producer 中使用

配乐环节拿到 `--bgm` 文件的来源之一（与 `aigc-video-gen music` 生成路线并列）：

```bash
# 1. 按视频主题选曲并下载到工程 audio/ 目录
bgm-library pick "科技产品展示 轻快" --output <project-dir>/audio/

# 2. 交给 video-edit 混音（循环/裁剪到视频时长，默认 0.25 音量垫底）
video-edit audio-mix input.mp4 --bgm <project-dir>/audio/Coruscate_-_The_Fade_Out.mp3 --output out.mp4
```

选曲策略：

- ✅ **优先 `bgm-library`**：免 key、免版税、自动署名、商用安全；适合绝大多数配乐场景
- ✅ **需要定制风格 / 无法在 ccMixter 找到匹配时**：用 `aigc-video-gen music`（MiniMax 生成，需 `MINIMAX_API_KEY`）
- ❌ **不要**放开 `--no-commercial-only` 下 NC/ND 协议曲目到商用成片

---

## Pitfalls

### pitfall: 403 Forbidden on download

- **症状**：下载返回 403
- **workaround**：脚本已自动带 referer 头；仍 403 说明曲目已从 ccMixter 下架，换一首

### pitfall: 搜索无结果

- **症状**：`No tracks found matching your query`
- **workaround**：ccMixter 曲库比 Pixabay 小，换更宽的关键词、减少标签、或用 `--preset`

### pitfall: ccMixter SSL 证书链不全

- **症状**：Node 报 `unable to verify the first certificate`
- **workaround**：脚本已对 ccMixter 域名放宽 TLS 校验（`rejectUnauthorized: false`），无需手动处理；仅作用于该站点

### pitfall: 依赖未装

- **症状**：`Cannot find module 'commander'` 等
- **workaround**：依赖由 `apply-addons.sh` 自动安装（skill 目录下 `package.json`）；手动补装可 `cd <skill-dir> && npm install --omit=dev`
