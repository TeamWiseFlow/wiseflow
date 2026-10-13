---
name: "kuaishou-live"
description: "快手公开直播资料、回放与有界事件监听；不支持发言或点赞。"
description_zh: "快手公开直播资料、回放与有界事件监听；不支持发言或点赞。"
description_en: "kuaishou-live: native Xiaobei workflows, tools and reusable resources."
version: "0.3.1"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。



# 快手 live

只读公开房间、列表、分类、礼物、回放与有界事件监听。get 的直播主播ID与用户主页ID是两套；replays 传主页ID，不混用。没有直播评论、点赞、私信或主播后台接口。快手普通评论、点赞、收藏与关注写操作也未实现。

```bash
kuaishou-live get "<直播间>"
kuaishou-live listen "<直播间>" --duration 1m
kuaishou-live call <resource> <action> [平台选项]
kuaishou-live --help
```

查询通过 --account 指定同一个真实账号，完整ID作为字符串传递。列表默认20条、最多100条；监听 --duration 为1s–10m，默认1m，输出JSONL。不无限监听，不把样本当完整历史。

登录使用 kuaishou-hunter login。只执行真实接口已支持的动作，仍须本地实号验证响应、送达与权限。超时/断连先核对结果，不换通道重发；风控不当作登出。

内容搜索、作品、用户和评论采集使用 `kuaishou-hunter`。本工具归 kuaishou-hunter，`kuaishou-live` 是保留的只读 wrapper；也可使用 `kuaishou-hunter live`。竞对调研由 当前实际可用的公开资料检索能力 编排，记录目标、观察窗口、证据和缺项；互动写接口未实现，不执行主播后台管理。
