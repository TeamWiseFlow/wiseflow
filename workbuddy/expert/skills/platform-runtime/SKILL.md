---
name: "platform-runtime"
description: "TikTok、快手、X 和微博平台工具的内部运行库，统一管理登录和会话，由各 hunter、发布、engagement 与 BD wrapper 调用。"
description_zh: "TikTok、快手、X 和微博平台工具的内部运行库，统一管理登录和会话，由各 hunter、发布、engagement 与 BD wrapper 调用。"
description_en: "platform-runtime: native Xiaobei workflows, tools and reusable resources."
version: "0.3.1"
author: "TeamWiseFlow"
user-invocable: false
disable-model-invocation: true
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。

本版保留 API 业务，不包含浏览器 login/export/prepare-write。通过 `xiaobei-runtime import-session` 导入用户明确授权的 API 会话文件，再执行 hunter check；快手仍可用 HTTP 扫码/短信登录。TikTok 写操作仍需完整会话材料，不绕过原门槛。

平台任务使用对应技能 wrapper，由 xiaobei-runtime 调度。本目录提供四平台共享 API 传输、能力检查、发布回执与会话管理，不作为业务入口。会话导入及快手 HTTP 登录见 [登录说明](references/login.md)。

状态由运行层设置 PLATFORM_API_HOME，默认使用独立 ~/.xiaobei-workbuddy/logins/platform-api。依赖按 package.json 和固定四平台 profile 由运行层安装；保留原上游版本、校验值、裁剪和探测逻辑。不要绕过固定版本安装器手工安装 catbus-cli。

平台代理按 PLATFORM_API_<平台大写ID>_PROXY、PLATFORM_API_PROXY、HTTPS_PROXY/HTTP_PROXY 选择，空的显式平台代理值表示直连。不读取浏览器配置，代理和凭据不输出日志。
