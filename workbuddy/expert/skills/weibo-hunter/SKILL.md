---
name: "weibo-hunter"
description: "微博登录、内容搜索与采集：作品、账号、评论、媒体下载。内容发布走 weibo-publish，互动能力以 expert-bd 能力表为准。"
description_zh: "微博登录、内容搜索与采集：作品、账号、评论、媒体下载。内容发布走 weibo-publish，互动能力以 expert-bd 能力表为准。"
description_en: "weibo-hunter: native Xiaobei workflows, tools and reusable resources."
version: "0.3.2"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。

本版保留 API 业务，不包含浏览器 login/export/prepare-write。通过 `xiaobei-runtime import-session` 导入用户明确授权的 API 会话文件，再执行 hunter check；快手仍可用 HTTP 扫码/短信登录。TikTok 写操作仍需完整会话材料，不绕过原门槛。



# 微博内容采集

会话导入与检查见 [运行库登录说明](../platform-runtime/references/login.md)。发布与 BD 复用对应账号的 API 会话，多账号显式传 `--account`。

```bash
weibo-hunter check
weibo-hunter search '关键词' --limit 20
weibo-hunter user '<用户ID或主页链接>'
weibo-hunter user-posts '<用户ID或主页链接>' --limit 20
weibo-hunter comments '<作品链接>' --limit 20
weibo-hunter fetch '<作品链接>' --output-dir /绝对路径/样本 --download-media
weibo-hunter fetch '<视频链接>' --output-dir /绝对路径/样本 --download-media --video-only
weibo-hunter methods
weibo-hunter call <resource> <action> [平台选项]
```

普通查询返回 JSON 信封，`data` 是数组或对象，`page` 保留游标；fetch 返回 `note`、`media_paths`，保存 `note.json` 和有序媒体文件。保留真实来源、完整字符串 ID 与原始计数，缺项为 null，不补零。终端缩略 ID 不能用于下一步。核对账号作品的作者身份；数字 uid、用户名与 secUid 不能互换。

列表默认 20 条，`--limit` 范围 1–100；按实际 `page` 游标有界续读，不使用 --all。`call` 只允许 methods 列出的读取接口，不能借此发评论、私信、点赞或关注。会话缺失/明确过期返回 2，风控和网络故障保留独立错误，不触发盲重登。

搜索仅第一页，--limit 不会突破该限制；评论只有一级。用户搜索、推荐流与通知未实现。详情资料的媒体地址由本技能下载，不调用尚未实现的平台 item download。

视频先下载再交 `viral-chaser` 本地 analyzer，采用返回的实际视频路径；`--video-only` 在下载前拒绝图文。图文和文字由调用方回读原文与图片分析，发布使用 `weibo-publish`。微博没有专家包或本人指标回填工具；互动写操作、私信和直播尚不支持。下载依赖平台返回的实际可访问媒体 URL，失败不回报下载成功。
