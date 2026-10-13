---
name: "douyin-interact"
description: "对抖音作品点赞、收藏、评论或回复评论；先预览目标与文字，再执行已确认的操作。"
description_zh: "对抖音作品点赞、收藏、评论或回复评论；先预览目标与文字，再执行已确认的操作。"
description_en: "douyin-interact: native Xiaobei workflows, tools and reusable resources."
version: "0.3.1"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。


# 抖音作品互动

先用 `douyin-hunter fetch` 与 `douyin-hunter comments` 核实作品及目标评论。接口写入使用独立 API 会话 `~/.xiaobei-workbuddy/douyin-api/session.json`，该会话缺失时等待独立登录流程完成。文字和目标必须由用户确认或来自用户已经批准的运营策略。

```bash
douyin-interact like --url "https://www.douyin.com/video/<id>"
douyin-interact comment --url "https://www.douyin.com/video/<id>" --text "已确认的评论"
douyin-interact reply --url "https://www.douyin.com/video/<id>" --comment-id <id> --text "已确认的回复"
```

默认只输出预览。核对目标、文字和账号后，在同一命令末尾加 `--confirm` 才发送。`unlike`、`favorite`、`unfavorite` 同样需要 `--confirm`。写操作依赖 Relay v2 `web.request` 完成端点联调；服务未就绪时 `SIGN_UNAVAILABLE` 或 `UNSUPPORTED_OPERATION` 不视作成功。一次调用只提交一次；超时或结果不明时先到平台核实，不自动重试。平台风控、Relay 故障与登录失效分别处理，不把接口空响应当作成功。
