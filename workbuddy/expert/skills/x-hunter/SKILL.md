---
name: "x-hunter"
description: "X/Twitter 登录、内容搜索与采集：作品、账号、评论、媒体下载；互动写操作走 expert-bd，创作/发布/本人数据走 expert-twitter。"
description_zh: "X/Twitter 登录、内容搜索与采集：作品、账号、评论、媒体下载；互动写操作走 expert-bd，创作/发布/本人数据走 expert-twitter。"
description_en: "x-hunter: native Xiaobei workflows, tools and reusable resources."
version: "0.3.1"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。

本版保留 API 业务，不包含浏览器 login/export/prepare-write。通过 `xiaobei-runtime import-session` 导入用户明确授权的 API 会话文件，再执行 hunter check；快手仍可用 HTTP 扫码/短信登录。TikTok 写操作仍需完整会话材料，不绕过原门槛。



# X/Twitter内容采集

会话导入与检查见 [运行库登录说明](../platform-runtime/references/login.md)。发布与 BD 复用对应账号的 API 会话，多账号显式传 `--account`。

```bash
x-hunter check
x-hunter search '关键词' --limit 20
x-hunter user '<用户ID或主页链接>'
x-hunter user-posts '<用户ID或主页链接>' --limit 20
x-hunter comments '<作品链接>' --limit 20
x-hunter fetch '<作品链接>' --output-dir /绝对路径/样本 --download-media
x-hunter fetch '<视频链接>' --output-dir /绝对路径/样本 --download-media --video-only
x-hunter methods
x-hunter call <resource> <action> [平台选项]
```

普通查询返回 JSON 信封，`data` 是数组或对象，`page` 保留游标；fetch 返回 `note`、`media_paths`，保存 `note.json` 和有序媒体文件。保留真实来源、完整字符串 ID 与原始计数，缺项为 null，不补零。终端缩略 ID 不能用于下一步。核对账号作品的作者身份；数字 uid、用户名与 secUid 不能互换。

列表默认 20 条，`--limit` 范围 1–100；按实际 `page` 游标有界续读，不使用 --all。`call` 只允许 methods 列出的读取接口，不能借此发评论、私信、点赞或关注。会话缺失/明确过期返回 2，风控和网络故障保留独立错误，不触发盲重登。

只读与写接口仍需真实账号验收。媒体搜索 --type video/image 不支持 --sort latest；推荐流可读，关注流未实现。通知、粉丝/关注列表和收藏列表尚不支持。

视频先下载再交 `viral-chaser` 本地 analyzer，采用返回的实际视频路径；`--video-only` 在下载前拒绝图文。图文和文字采样在 `expert-twitter` 或调用方 workflow 回读原文与图片分析。创作/发布/本人数据走 `expert-twitter`；互动走 expert-bd，公开商业信息分析走 当前实际可用的公开资料检索能力；X 直播尚无已实现接口。下载依赖平台返回的实际可访问媒体 URL，失败不回报下载成功。
