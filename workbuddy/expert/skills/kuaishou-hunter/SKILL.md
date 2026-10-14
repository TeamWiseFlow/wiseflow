---
name: "kuaishou-hunter"
description: "快手内容搜索与采集：作品、账号、评论、媒体下载；支持范围以 methods 为准，互动写操作走 expert-bd。"
description_zh: "快手内容搜索与采集：作品、账号、评论、媒体下载；支持范围以 methods 为准，互动写操作走 expert-bd。"
description_en: "kuaishou-hunter: native Xiaobei workflows, tools and reusable resources."
version: "0.3.3"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。



# 快手内容采集

首次登录：`kuaishou-hunter login`。
扫码登录返回二维码与下一步提示，交用户扫码后运行 `kuaishou-hunter login-confirm`。短信登录由 `login --method sms --phone <手机号>` 请求，用户给验证码后 `login-confirm --method sms --code <验证码>` 完成；手机与中间票据由脚本保存，不手工拼接。不要在非交互 Agent 环境等待终端输入。快手主站、创作者中心和直播站票据由运行库内同一登录流程管理。


```bash
kuaishou-hunter check
kuaishou-hunter search '关键词' --limit 20
kuaishou-hunter user '<用户ID或主页链接>'
kuaishou-hunter user-posts '<用户ID或主页链接>' --limit 20
kuaishou-hunter comments '<作品链接>' --limit 20
kuaishou-hunter fetch '<作品链接>' --output-dir /绝对路径/样本 --download-media
kuaishou-hunter fetch '<视频链接>' --output-dir /绝对路径/样本 --download-media --video-only
kuaishou-hunter methods
kuaishou-hunter call <resource> <action> [平台选项]
```

普通查询返回 JSON 信封，`data` 是数组或对象，`page` 保留游标；fetch 返回 `note`、`media_paths`，保存 `note.json` 和有序媒体文件。保留真实来源、完整字符串 ID 与原始计数，缺项为 null，不补零。终端缩略 ID 不能用于下一步。核对账号作品的作者身份；数字 uid、用户名与 secUid 不能互换。

列表默认 20 条，`--limit` 范围 1–100；按实际 `page` 游标有界续读，不使用 --all。`call` 只允许 methods 列出的读取接口，不能借此发评论、私信、点赞或关注。会话缺失/明确过期返回 2，风控和网络故障保留独立错误，不触发盲重登。

作品搜索不支持 --sort/--type/--time。关注流只有首屏，user likes/followers/following 只支持 me。二级评论参数覆盖有限；notice count 只有总数。400002、验证码或风控应停止并报告，不能当空数据或登录失效。

视频先下载再交 `viral-chaser` 本地 analyzer，采用返回的实际视频路径；`--video-only` 在下载前拒绝图文。图文和文字采样在 `expert-kuaishou` 或调用方 workflow 回读原文与图片分析。创作/发布/本人数据走 `expert-kuaishou`；互动写接口目前未实现，公开直播读取走本 hunter，调研分析走 当前实际可用的公开资料检索能力。下载依赖平台返回的实际可访问媒体 URL，失败不回报下载成功。

## 公开直播读取

房间、列表、分类、礼物、回放与有界监听使用 `kuaishou-hunter live`；[读取说明](tools/kuaishou-live/SKILL.md)。原 kuaishou-live wrapper 保留在 hunter 内，调用同一只读入口。竞对调研交 当前实际可用的公开资料检索能力，快手互动写接口保持未实现。
