---
name: "kuaishou-engagement"
description: "快手本人已发布作品数据获取和指标回填，不负责发布或其他账号数据分析。"
description_zh: "快手本人已发布作品数据获取和指标回填，不负责发布或其他账号数据分析。"
description_en: "kuaishou-engagement: native Xiaobei workflows, tools and reusable resources."
version: "0.3.1"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。



# 快手本人作品指标

```bash
kuaishou-engagement check --account default
kuaishou-engagement list --account default --limit 20
kuaishou-engagement fetch --record-id 12 --account default --limit 100
kuaishou-engagement daily --account default --limit 30
```

fetch 的 --record-id 是 published-track 表行 ID，不是平台作品 ID。脚本在线核验当前用户，获取本人作品列表，按完整发布 URL 或自动入库 notes.platform_runtime 中的创作者作品 ID 匹配同 alias 的记录，再调用 published-track update-metrics。快手使用当前已验证创作者会话的本人列表，存在作者字段时再核对。私密/审核中的数字 ID 可能没有公开链接；不拿上传 fileId 匹配作品，不用公开 hunter 空列表判失败。

默认只取 20 条，最大 100 条；只更新真实匹配的记录，没取到的记录返回 skipped，不用标题猜匹配。只写接口提供的非负整数，真实 0 保留，null 不写、不覆盖历史值。结果保留 source、captured_at 与分页信息。不提供受众画像、收益或后台深指标；接口与字段仍需本地实号验收。
