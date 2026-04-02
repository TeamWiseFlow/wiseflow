# Crew 模板注册表

> 本文件是**开发者参考**，综合列出项目中所有 Crew 模板。
> 运行时由各自的管理者维护独立索引：
> - `~/.openclaw/crew_templates/index.md` — 对内模板目录，由 **Main Agent** 维护
> - `~/.openclaw/hrbp_templates/index.md` — 对外模板目录，由 **HRBP** 维护
> Crew 类型说明详见 `CREW_TYPES.md`。

## 对内 Crew 模板（Internal — 内置，由 Main Agent 管理）

| 模板 ID | 名称 | 简介 | 类型 | 版本 |
|---------|------|------|------|------|
| main | Main Agent | 路由调度器，消息入口，对内 crew 生命周期管理 | internal | OFB built-in |
| hrbp | HRBP | 对外 Crew 生命周期管理（招聘/调岗/解雇/升级） | internal | OFB built-in |
| it-engineer | IT Engineer | OFB 系统部署、维护、升级、排障 | internal | OFB built-in |

## 对外 Crew 模板（External — 由 HRBP 管理）

| 模板 ID | 名称 | 简介 | 类型 | 版本 |
|---------|------|------|------|------|
| sales-cs | 销售型客服 | 客户咨询、问题解答、成交导向、客户调研，bind-only | external | OFB official |

## 用户自建模板（User-created）

| 模板 ID | 名称 | 类型 | 简介 | 创建日期 |
|---------|------|------|------|----------|
| _(暂无)_ | | | | |

## 市场引入模板（Marketplace）

| 模板 ID | 名称 | 类型 | 来源 | 引入日期 |
|---------|------|------|------|----------|
| _(暂无)_ | | | | |
