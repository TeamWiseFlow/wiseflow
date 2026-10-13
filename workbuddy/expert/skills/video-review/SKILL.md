---
name: "video-review"
description: "成片自检闸门——ffprobe 校验 + 5 位抽帧黑帧扫 + 音频电平 + 时长/分辨率一致性，verdict pass/fail/warn。各视频生产技能合成后、交付前必跑。"
description_zh: "成片自检闸门——ffprobe 校验 + 5 位抽帧黑帧扫 + 音频电平 + 时长/分辨率一致性，verdict pass/fail/warn。各视频生产技能合成后、交付前必跑。"
description_en: "video-review: native Xiaobei workflows, tools and reusable resources."
version: "0.3.1"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。


# video-review（成片自检公共技能）

## 用途

视频合成后的**强制自检闸门**——在向用户交付前跑一次，拦成片硬伤：

- ffprobe 全字段校验（codec / 分辨率 / fps / pix_fmt / 音频配置）
- 5 位抽帧黑帧扫（0% / 25% / 50% / 75% / 100%）—— ≥2 黑帧判 critical
- 音频电平分析（volumedetect）—— 静音 / 削波 / 无音轨
- 时长 vs 目标（`--target-duration`，默认 ±5% 容差）
- 分辨率 floor（9:16 竖屏最低 720x1280）+ 目标比对 + 段一致性

## 调用

```bash
video-review <final.mp4>                    # 直接审单个成片文件
video-review <project-dir>                  # 审 <dir>/video.mp4，并对 artifacts/ 做段一致性检查
video-review <project-dir> --target-duration 30 --target-resolution 720x1280
video-review <final.mp4> --output review.json
```

参数：

| 参数 | 默认 | 说明 |
|------|------|------|
| `target` | — | 成片文件路径；或项目目录（目录时审 `<dir>/video.mp4`，且若存在 `artifacts/` 一并做段一致性检查） |
| `--target-duration` | 无 | 目标时长（秒），从脚本片段规划累加得出 |
| `--target-resolution` | 无 | 目标分辨率，形如 `720x1280` |
| `--output` | `<project-dir>/review/verdict.json` | verdict JSON 落盘路径 |

## verdict 语义

| verdict | 退出码 | 含义 | 处置 |
|---------|--------|------|------|
| `pass` | 0 | 无 critical 无 warning | 可交付 |
| `fail` | 1 | 有 critical issue | **不准交**——按 `critical[]` 修复后重审，最多重修 2 轮，仍 fail 则向用户复述 critical 项请求决策 |
| `warn` | 2 | 有 non-critical issue | 向用户复述让其决定是否重修 |
| — | 3 | 脚本本身故障（ffprobe missing / path invalid） | 不算评审结论，修脚本 |

## verdict JSON schema

```json
{
  "verdict": "pass" | "fail" | "warn",
  "file": "<video.mp4 absolute path>",
  "ffprobe": { "codec", "width", "height", "fps", "pix_fmt", "duration", "size_bytes", "audio": {...} },
  "frames": [ { "position_pct", "path", "mean_luma", "is_black" } ],
  "audio_level": { "mean_db", "max_db", "silent", "clipping", "absent" },
  "checks": [
    { "name": "duration_match",   "status": "pass",    "detail": "actual 30.2s vs target 30s, gap 0.2s" },
    { "name": "resolution_floor", "status": "pass",    "detail": "720x1280" },
    { "name": "resolution_uniform", "status": "fail",  "detail": "成片 720x1280 vs 段01 1080x1920" }
  ],
  "critical": [ "resolution_uniform: ..." ],
  "warnings": [ "audio_level mean_db=-42.1 close to silent threshold" ]
}
```

## 抽帧产物

5 帧静图落 `<project-dir>/review/frames/frame_NNN.jpg`，verdict JSON 落 `<project-dir>/review/verdict.json`。**不进 `artifacts/`、不进 `previews/`**，与 keyframes/ 子目录同级，互不混淆。

## 段一致性检查

`probe_segments` 扫 `<project-dir>/artifacts/` 下各段 ffprobe，逐段比对分辨率与成片是否一致——拼了不同分辨率段是硬伤。`artifacts/_deprecated/` 子目录不参与（非递归 listdir）。

## 强制约定

- **禁止跳过本脚本交付**：各视频生产技能的合成环节产出 `video.mp4` 后，必须先跑本脚本，verdict=pass 才能进交付/封面环节
- **禁止肉眼看交代替本脚本**：本脚本是替代"裸拼完就交"脆弱闸门的强制自检
- **warn 处置**：声画同出模式下 `audio_absent` warning 要对照看——AI 生成模式该出声没出声是 critical（退回重生成或补 TTS）；Stock Footage + `--no-audio` 模式下 `audio_absent` 是预期，warn 可放行
