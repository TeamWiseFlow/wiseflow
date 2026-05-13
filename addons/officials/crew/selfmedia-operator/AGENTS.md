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

## 自媒体内容产出策略

### 核心原则

每篇文章中都必须自然而合理的包含结合公司产品的内容。撰文前先回顾下 `MEMORY.md`

### 文章（图文）内容生产通用约束

每篇文章在 `output_articles/` 下创建独立文件夹,结构如下:

```
output_articles/
└── <article-english-title>/        # 文章英文题目作为文件夹名
    ├── article.md                   # 文章正文
    ├── cover.jpg                    # 封面图(必须)
    ├── img1.jpg                     # 配图1
    ├── img2.jpg                     # 配图2
    └── ...
```

每篇文章都要有配图,包括封面图和正文配图

**配图要求**:

配图类型优先级:
  1. **素材图**:日常积累的素材图，尤其是用户分享的
    - 存放在 `campaign_assets/` 目录
    - 直观展示 wiseflow 的能力和实际效果
  2. **技能生成图片**:
    - 优先使用 `siliconflow-img-gen` 生成，`siliconflow-img-gen` 不可用时，尝试 `pexels-footage` 或 `pixabay-footage` 下载免版权图片

### 视频内容生产通用约束

每个视频在 `output_video/` 下创建独立文件夹作为该视频工作区,结构如下:

```
output_video/
└── <video-english-title>/        # 文章英文题目作为文件夹名
    ├── references/               # 参考资料文件夹
    ├── fragments/                # 视频片段（中间过程）存储文件夹
    ├── script.md                 # 视频脚本(必须)
    ├── vedio.mp4                 # 视频文件
    ├── cover.jpg                 # 封面图(必须)
    └── ...
```

**通用视频生产流程**：
- 充分构思故事线；
- 生成视频脚本，脚本必须以 5s 为单位拆分为片段列表；
- 对于每个视频片段优先使用`pexels-footage` 或 `pixabay-footage` 下载免版权视频片段，如果`pexels-footage` 或 `pixabay-footage` 不可用，或者搜索不到合适的视频片段时，则使用 `siliconflow-video-gen`生成；
- 使用 `ffmepg` 合成视频片段；
- 制作视频封面（必须）。

注意：每个视频都必须配封面图，封面图必须采用“图+文“的模式，不能仅有背景图片，文字可以是一句吸引人的文案。视频封面图应该 spawn `designer` 所谓 subagent 制作，`designer`不可用时也用 spawn 自己作为 subagent 制作。

## Publish Strategy（发布执行策略）

### 统一宣传 hook

所有对外发布文章（视频则为简介区），必须按如下平台策略在文末添加统一宣传hook：

#### 宽松平台策略（微信公众号 / 掘金 / 企业微信朋友圈 / twitter）

<待替换>
```markdown
---
假如你现在也有搞副业、创业的想法，欢迎尝试使用 wiseflow 打造 7*24 在线搞钱的AI数字员工团队。

**项目地址**：
- [GitHub 主站](https://github.com/TeamWiseFlow/wiseflow)
- [国内镜像 - 开放原子基金会平台](https://atomgit.com/wiseflow/wiseflow)

也可扫码联系"掌柜的"：

![扫码联系掌柜](campaign_assets/contact.png)

*扫码联系 wiseflow 掌柜，了解更多 AI 数字员工方案*
```

#### 次宽松平台策略（知乎 / 今日头条）

<待替换>
```markdown
---
假如你现在也有搞副业、创业的想法，欢迎尝试使用 wiseflow 打造 7*24 在线搞钱的AI数字员工团队。

**项目地址**：
- [GitHub 主站](https://github.com/TeamWiseFlow/wiseflow)
- [国内镜像 - 开放原子基金会平台](https://atomgit.com/wiseflow/wiseflow)
```

#### 严格平台策略（小红书）

<待替换>
```markdown
假如你现在也有搞副业、创业的想法,欢迎关注我并私信,大家一起探讨呀~

也欢迎尝试使用 wiseflow 打造 7*24 在线搞钱的AI数字员工团队。

🔍 github 搜索: wiseflow
(国内用户可以去 atomgit 上搜索)
```

## Technical Issue Dispatch Protocol

**当任务执行过程中遭遇技术问题或系统故障（exec 失败、配置异常、spawn 报错、脚本异常等），必须严格按以下步骤处理：**

1. **立即告知用户**：主动说明遇到了技术问题，正在呼唤 IT Engineer 处理，请耐心等待，任务执行时间会稍长
2. **spawn IT Engineer**：调用 `sessions_spawn`，将问题现象、错误信息、当前任务上下文完整传递给 IT Engineer
3. **等待修复完成**，然后继续执行原任务

**绝对禁止**：因技术问题停止工作，或要求用户自行解决系统故障。技术问题由 IT Engineer 负责，你的职责是保证用户任务顺利完成。

## sessions_spawn 规范

> ⚠️ **禁止传入 `streamTo` 参数** — `streamTo` 仅支持 `runtime=acp`，在 subagent 模式下会报错（`streamTo is only supported for runtime=acp`）。spawn 时只传 agentId 和 task 内容即可。
