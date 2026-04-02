# HRBP Agent — Memory

## External Crew Registry
- 本 workspace 中的 `EXTERNAL_CREW_REGISTRY.md` 是对外 Crew 实例的权威记录，仅 HRBP 可访问
- 每次招募/修改/解除对外 Crew 后必须同步更新

## Internal Crew Directory（只读参考）
- `~/.openclaw/crew_templates/TEAM_DIRECTORY.md`（由 Main Agent 维护，HRBP 只读）
- 对内 Crew 的生命周期不由 HRBP 管理

## External Template Library
- 外部 Crew 模板目录：`~/.openclaw/hrbp_templates/`
- 模板索引：`~/.openclaw/hrbp_templates/index.md`
- OFB 项目路径参考：见 workspace 中的 `OFB_ENV.md`

## OFB 系统知识

### 项目信息
- **OFB 仓库**：https://github.com/TeamWiseFlow/openclaw_for_business
- **上游 OpenClaw 仓库**：https://github.com/openclaw/openclaw
- **OpenClaw 官方教程**：https://docs.openclaw.ai/

### Crews 机制要点
- 两种 Crew 类型：internal（对内，spawn+bind，继承技能）和 external（对外，bind-only，声明式技能）
- HRBP 只管理 external crew，不管理 internal crew
- External crew 实例化时必须创建 `DECLARED_SKILLS`（声明式技能）和 `feedback/`（用户反馈目录）
- External crew 不能自主升级，只能由 HRBP 发起升级
- `dmScope: per-channel-peer` 是全局配置，对所有 channel 生效（包括内部 crew）

### 关键路径
> 实际 OFB 项目路径记录在 `OFB_ENV.md`（同目录），每次运行 setup-crew.sh 自动更新。

### 运行时数据位置
- openclaw.json：`~/.openclaw/openclaw.json`
- 对外 crew workspace：`~/.openclaw/workspace-<instance-id>/`
- 对外 crew 反馈：`~/.openclaw/workspace-<instance-id>/feedback/`
- 对外 crew 模板：`~/.openclaw/hrbp_templates/`
- 归档目录：`~/.openclaw/archived/`

## 保护名单（内部 Crew，不受 HRBP 管理）
以下为内置对内 Crew，不可删除、不可多实例：
- `main` — 路由调度器
- `hrbp` — 本 agent（自身）
- `it-engineer` — OFB 系统运维

## 对外 Crew 实例注册表
> 权威数据在本 workspace 的 `EXTERNAL_CREW_REGISTRY.md`（更结构化）
> 此处仅保留操作历史摘要

## Operation History
（每次招募/修改/解除操作后追加记录）
