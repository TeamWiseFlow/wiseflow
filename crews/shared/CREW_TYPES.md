# Crew 类型系统

> 本文件是 OFB Crew 类型系统的权威定义。所有模板和脚本均依据此文件判断 Crew 行为。

---

## 两种 Crew 类型

### 对内 Crew（internal）

服务对象是企业内部管理者，代表企业利益运行。

| 属性 | 规范 |
|------|------|
| 声明方式 | SOUL.md 中 `crew-type: internal` |
| 技能继承 | 自动继承基线技能；项目/addon 全局技能需在 `BUILTIN_SKILLS` 显式声明 |
| 命令权限 | 按 SOUL.md 中的 command-tier 声明（T1/T2/T3） |
| 路由模式 | spawn + bind 双模式均可 |
| 生命周期管理 | 由 Main Agent 管理（通过专属技能脚本） |
| 升级方式 | 由管理者（人类用户或 Main Agent）发起 |
| TEAM_DIRECTORY | 记录在 `~/.openclaw/crew_templates/TEAM_DIRECTORY.md`，所有对内 Crew 可读 |
| 模板目录 | `~/.openclaw/crew_templates/`，仅 Main Agent 可访问 |

**内置对内 Crew（全局唯一，不可删除）**：
- `main` — 路由调度器、对内 crew 生命周期管理（不含 hrbp 和 it-engineer）（T2）
- `hrbp` — 对外 Crew 生命周期管理（T3）
- `it-engineer` — OFB 系统运维（T3）

---

### 对外 Crew（external）

服务对象是外部客户或业务合作方，代表企业对外。

| 属性 | 规范 |
|------|------|
| 声明方式 | SOUL.md 中 `crew-type: external` |
| 技能继承 | **声明式**——仅使用 `DECLARED_SKILLS` 文件中列出的技能（declare 模式） |
| 命令权限 | 默认 T0（禁止所有 shell 命令），可通过白名单声明额外权限 |
| 路由模式 | **仅支持 bind 模式**，禁止 Main Agent 通过 spawn 路由 |
| 生命周期管理 | 由 HRBP 管理，注册信息记录在 `EXTERNAL_CREW_REGISTRY.md` |
| 升级方式 | 只能由 HRBP 主导升级 |
| 会话隔离 | `dmScope: per-channel-peer`（全局设置，每个外部用户独立 session） |
| 反馈收集 | 用户不满意时必须记录到 workspace 的 `feedback/` 目录 |
| 模板目录 | `~/.openclaw/hrbp_templates/`，仅 HRBP 可访问 |

**内置对外 Crew（官方模板）**：
- `customer-service` — 客户服务（T0）

---

## DECLARED_SKILLS 文件格式

对外 Crew 模板必须包含 `DECLARED_SKILLS` 文件，每行一个技能名称：

```
# 声明式技能列表（external crew 专用）
# 每行一个技能名称；以 # 开头的为注释；支持空行
# 允许声明任何内置技能（包括 addon 安装的全局技能）

nano-pdf
xurl
```

**注意**：对外 Crew 技能列表由 HRBP 管理，技能变更需经 HRBP 审核。

---

## feedback 目录格式

对外 Crew 实例的 workspace 中必须存在 `feedback/` 目录，每天使用一个文件记录反馈。

文件命名：`feedback/YYYY-MM-DD.md`

每条反馈条目格式（追加写入，每次会话结束时记录一条）：

```markdown
## Feedback: {时间戳 HH:MM}

**渠道**：{channel-id 或 feishu/wechat 等}
**用户摘要**：{用户身份的简短描述，不含 PII}
**问题分类**：{咨询|投诉|请求|升级}
**问题描述**：{一句话概括问题}
**处理方式**：{做了什么}
**结果**：{已解决|未解决|已升级}
**用户情绪**：{满意|中性|不满}
**备注**：{可选补充}
```

HRBP 可通过 `hrbp-feedback-review` 技能读取所有对外 Crew 实例的反馈并制定升级方案。

---

## Addon 声明规范

Addon 提供 Crew 模板时，SOUL.md 中**必须**包含 `crew-type` 声明：

```markdown
## 权限级别
crew-type: external
command-tier: T0
```

若 addon.json 同时声明了 `crew-type`（全局）或 `crew-types.<template-id>`（逐模板），其值必须与 SOUL.md 一致；不一致会被 `apply-addons.sh` 直接拒绝。
