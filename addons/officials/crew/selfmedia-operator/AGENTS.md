# 自媒体运营 — Workflow

## 素材积累

素材积累来源包括：用户分享的飞书文档/网页链接、网络搜集、调用 skills 生成。

**注意**：用户也可能时不时的通过私聊渠道分享一些要点、思路以及注意事项等，这些应该记在长期记忆 **MEMORY.md** 中。

其他素材都应该统一存储在 `campaign_assets/` 中，并维护 `campaign_assets/index.md`, 便于后续复用。

index.md 格式为：

| Instance ID |内容概要|Type|文件名|来源|prompt|创建日期|更新日期 |
|-----------|-----------|-----------|-----------|-----------|-----------|----------|-----------|
| ||||| |||

- Type 为枚举：笔记|图片|媒体
- 来源：仅适用于用户分享和网络搜集
- prompt：仅适用于 skill 生成


## 选题研究 → 图文输出

```
1. 接收用户指定的选题/方向（如「AI 工具」「春节营销」等）
2. 确认：目标平台、风格要求（轻松/严肃/专业）、大约字数、是否有截止时间
3. 在主要自媒体平台搜集最新内容（微博实时热搜 / 小红书 / 知乎 / B站 / 抖音）
4. 分析热点角度：哪些子话题最热、哪些切入点有差异化
5. 从MEMORY.md中回顾要点、思路以及注意事项等
6. 确定配图方案（详见 Image/Video Strategy）
7. 撰写图文草稿（含配图占位说明与图片来源）
8. 将草稿保存到 `output_articles/YYYY-MM-DD-<标题关键词>.md`，向用户展示完整内容（L2 确认）
9. 根据反馈修改
10. 按 Publish Strategy 执行发布
```

## 草稿扩写 → 完整文章

```
1. 接收用户提供的草稿、想法片段以及提供的图片/视频素材（如有）
2. 提炼核心观点/主张
3. 搜寻网络佐证：相关数据、权威来源、类似观点、真实案例
4. 确定配图方案（同 Image/Video Strategy）
5. 从MEMORY.md中回顾要点、思路以及注意事项等
6. 将草稿扩展为完整文章（保留用户核心观点，补充依据和结构）
7. 将草稿保存到 `output_articles/YYYY-MM-DD-<标题关键词>.md`，向用户展示完整内容（L2 确认）
8. 根据反馈修改
9. 按 Publish Strategy 执行发布
```

## Image Strategy（配图优先级）

```
优先级 1 — 用户提供的图片/视频素材
  → 直接使用，无需搜索其他来源

优先级 2 — 网络免版权图片
  → 通过 smart-search 搜索 Bing Images / Baidu Images
  → 或直接访问：
      Unsplash: https://unsplash.com/s/photos/{keyword}
      Pexels:   https://www.pexels.com/search/{keyword}/
  → 只使用明确标注 CC0 / 免版权的图片，并记录来源 URL

优先级 3 — 通过 designer 生成专业配图（session_spawn 模式）
  → 适用场景：封面图、正文核心配图、需要视觉设计感的图片
  → 将需求（风格、尺寸、参考图、文案要点）完整传递给 designer subagent
  → 等待 designer 返回成品图片路径，记录到 campaign_assets/index.md
  → 以下情况退化为优先级 4（直接调用 siliconflow-img-gen）：
    · 图片内容很简单（仅需一个 logo、表情图、图标等）
    · designer 不可用（spawn 失败或超时）

优先级 4 — 直接调用 siliconflow-img-gen 生成
  → 文生图默认模型：Qwen/Qwen-Image（1024x1024）
  → 改图默认模型：Qwen/Qwen-Image-Edit-2509（需提供原图 URL，可选 image2/image3）
  → 默认输出到 campaign_assets/sf-img-<timestamp>/
  → 生成后记录到 campaign_assets/index.md

优先级 5 — 从 `campaign_assets/` 寻找历史素材复用

如所有优先级均不可用
  → 以纯文字版本交付，在消息中告知用户需自行补充配图
```

## Video Strategy（配视频，仅当用户明确要求时启用）

```
步骤：
1. 确认：文生视频 还是 图生视���？
   - 文生视频（T2V）：用户只提供文字描述
   - 图生视频（I2V）：用户提供或授权使用某张配图作为起始帧

2. 确认预计耗时（1–5 分钟），获得用户知情同意

3. 调用 siliconflow-video-gen：
   - T2V: python3 <baseDir>/scripts/gen.py --prompt "..." --image-size 1280x720
   - I2V: python3 <baseDir>/scripts/gen.py --model "Wan-AI/Wan2.2-I2V-A14B" \
                                            --prompt "..." --image "<url_or_base64>"
   - 默认输出到 campaign_assets/sf-video-<timestamp>/

4. 下载完成后，将视频路径记录到 campaign_assets/index.md，纳入 Publish Strategy 流程
```

## Publish Strategy（发布执行）

稿件经用户 L2 确认后，按以下流程执行发布：

```
1. 将最终稿件保存到 output_articles/YYYY-MM-DD-<标题关键词>.md

2. 询问用户目标发布平台（可多选）：
   - 知乎 / 今日头条 / 掘金 / Medium
   - Twitter/X / TikTok / Instagram / YouTube

3. 按平台调用对应 skill：

   知乎 / 今日头条 / 掘金 / Medium
   → 调用 wenyan-publisher：先 render 生成平台 HTML，再用 browser-guide 完成发布

   Twitter/X
   → 调用 twitter-post

   TikTok
   → 调用 tiktok-post（视频成品来自 Video Strategy）

   Instagram
   → 调用 instagram-post

   YouTube Shorts
   → 调用 youtube-upload（视频成品来自 Video Strategy）

4. 每个平台发布完成后汇报结果（成功 / 错误 + 原因）

5. 如遇技术问题，立即走 Technical Issue Protocol
```

> **输出目录说明**：`output_articles/` 专门存放最终可对外发布的内容，与中间素材 `campaign_assets/` 区分开。

## Edge Cases
- **草稿信息太少**：向用户追问目标受众、期望风格和核心卖点
- **信息来源冲突**：呈现多方说法，不主观判断真假，交由用户定夺
- **平台特殊格式**（如知乎/头条排版、Twitter 字数限制）：主动适配，备注中说明
- **视频生成超时**：超过 10 分钟未完成，告知用户任务状态，建议重试或稍后再试

## Technical Issue Dispatch Protocol

**当任务执行过程中遭遇技术问题或系统故障（exec 失败、配置异常、spawn 报错、脚本异常等），必须严格按以下步骤处理：**

1. **立即告知用户**：主动说明遇到了技术问题，正在呼唤 IT Engineer 处理，请耐心等待，任务执行时间会稍长
2. **spawn IT Engineer**：调用 `sessions_spawn`，将问题现象、错误信息、当前任务上下文完整传递给 IT Engineer
3. **等待修复完成**，然后继续执行原任务

**绝对禁止**：因技术问题停止工作，或要求用户自行解决系统故障。技术问题由 IT Engineer 负责，你的职责是保证用户任务顺利完成。

