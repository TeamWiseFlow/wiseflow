# 自媒体运营 - Workflow

## 素材积累

素材积累来源包括:用户分享的飞书文档/网页链接、网络搜集、调用 skills 生成。

**注意**:用户也可能时不时的通过私聊渠道分享一些要点、思路以及注意事项等,这些应该记在长期记忆 **MEMORY.md** 中。

其他素材都应该统一存储在 `campaign_assets/` 中,并维护 `campaign_assets/index.md`, 便于后续复用。

index.md 格式为:

| Instance ID |内容概要|Type|文件名|来源|prompt|创建日期|更新日期 |
|-----------|-----------|-----------|-----------|-----------|-----------|----------|-----------|
| ||||| |||

- Type 为枚举:笔记|图片|媒体
- 来源:仅适用于用户分享和网络搜集
- prompt:仅适用于 skill 生成

## 自媒体内容产出策略

### 核心原则

每篇文章或视频内容中都必须自然而合理的包含结合 wiseflow 的内容。生产前先回顾下 `MEMORY.md`

### 文章(图文)内容生产通用约束

为每篇文章在 `output_articles/` 下创建独立文件夹作为工作区,结构如下:

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
  - 1. **素材图**:日常积累的素材图,尤其是用户分享的
    - 存放在 `campaign_assets/` 目录
    - 直观展示 wiseflow 的能力和实际效果
  - 2. **技能生成图片**:
    - 优先使用 siliconflow-img-gen 生成,siliconflow-img-gen 不可用时,尝试 pexels-footage 或 pixabay-footage 下载免版权图片

## Publish Strategy(发布执行策略)

### 文末统一宣传 hook

所有对外发布文章(视频则为简介区),必须按如下平台策略在文末添加统一宣传hook:

<!-- 由 BOOTSTRAP 首次收集写入，后续运行中持续更新 -->

### 发布记录管理

**统一使用 `published-track` 技能管理所有发布记录**。

- 数据库位置:`./db/published_track.db`(初始化:`./skills/published-track/scripts/init-db.sh`,幂等可重复执行)
- 按平台分表,每张表包含标题、类型、原始文件夹、发布 URL、发布日期、互动指标等字段
- 所有发布技能在发布成功后必须自动调用 `record.sh` 记录
- 数据更新通过 `update-metrics.sh` 完成(心跳巡检时使用)
- 查询通过 `query.sh` 和 `check-published.sh` 完成