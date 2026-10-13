---
name: "twitter-im"
description: "X/Twitter私信会话，支持范围以工具能力表为准。"
description_zh: "X/Twitter私信会话，支持范围以工具能力表为准。"
description_en: "twitter-im: native Xiaobei workflows, tools and reusable resources."
version: "0.3.2"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。



# X/Twitter im

只读最近20个会话首页。history 是端到端加密的占位消息，不当作可读正文；不能发送、标已读、撤回、删除会话或实时监听。

```bash
twitter-im list --limit 20
twitter-im history "<会话ID>" --limit 20
twitter-im call <resource> <action> [平台选项]
twitter-im --help
```

查询通过 --account 指定真实账号，完整ID作为字符串传递。list/history 只返回可得首页，--limit 不扩展上游范围，不把结果当完整历史。

登录使用 `x-hunter login/export`。只执行真实接口已支持的动作，仍须本地实号验证响应、送达与权限。超时/断连先核对结果，不换通道重发；风控不当作登出。

内容搜索、作品、用户和评论采集使用 `x-hunter`。记录真实查询目标、时间、覆盖范围与加密状态。
