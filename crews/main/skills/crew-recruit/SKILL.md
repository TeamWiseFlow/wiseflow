# crew-recruit

**触发条件**：用户请求招募新的**内部** Crew 专员（非客服等对外 crew）。

## 对内 vs 对外

- **对内 Crew**（internal）：由 Main Agent 管理，使用此技能。
- **对外 Crew**（external，如客服/销售/社群接待）：需要先启用 HRBP，并配置合适的工作/对外 channel；不要直接用此技能创建。

## 招募原则

- 不可招募 `it-engineer` 和 `hrbp`；这两个是全局唯一内置角色。
- Main Agent 也不可被重新招募。
- Main Agent 允许 spawn 除 `hrbp` 外的所有对内 crew；每次成功招募对内 crew 后，必须自动补入 `agents.main.subagents.allowAgents`。
- 每个新招募的对内 crew 必须自动允许调用 `it-engineer`，即补入该 crew 的 `subagents.allowAgents: ["it-engineer"]`。
- 其他对内 crew 可以有多个实例，但多实例必须绑定不同的工作 channel/account，避免同一入口路由到多个相似实例造成混淆。
- 默认招募内部 crew 不强制 direct channel binding；当用户要创建多个同类实例时，应先引导配置不同的 Feishu 或 WeCom 账号绑定。

## 执行步骤

```
1. 了解业务需求：角色职责、长期任务、是否需要直接工作 channel。
2. 确定模板 ID（可选，默认同 agent-id）。
3. 向用户展示创建方案，请求确认。
4. 用户确认后运行脚本。
5. 脚本成功后更新 reminder.json（TEAM_DIRECTORY.md 由脚本内部自动同步，无需手动操作）。
6. 如果团队规模触发阈值，建议用户配置 Feishu 或 WeCom 工作 channel。
7. 如本次创建或绑定要求 Gateway restart，先记录 pending-followup，再询问用户是否立即重启。
```

默认招募内部 crew 不强制 direct channel binding。工作 channel binding 使用 `work-channel-binding` skill 单独完成。

## 脚本用法

```bash
./skills/crew-recruit/scripts/recruit-internal-crew.sh <agent-id> [--template <template-id>] [--bind <channel>:<accountId>] [--note <text>]
```

### 参数说明

- `<agent-id>`：实例 ID（小写字母、数字、连字符）。
- `--template <id>`：使用哪个模板（默认同 agent-id）。
- `--bind <ch>:<acct>`：高级选项；默认流程不要使用，除非用户已完成 work channel 配置。
- `--note <text>`：备注信息。

### 示例

```bash
./skills/crew-recruit/scripts/recruit-internal-crew.sh sales-analyst --template developer --note "销售数据分析专员"
```

## 重要约束

- 不可创建内置保护名单中的 agent：main、hrbp、it-engineer。
- workspace 必须事先创建（脚本会检查）。
- 对内 Crew 使用继承模式技能，自动获得基线技能。
- 项目级 / addon 全局技能默认不自动继承；需要在目标 workspace 的 `BUILTIN_SKILLS` 中显式声明。

## 工作 Channel 提醒

招募后检查内部 crew 数量：

- 不算 `main`。
- 算 `it-engineer`。
- 算已启用的 `hrbp`。
- 当内部 crew 数量大于 3 时，提醒用户配置 Feishu 或 WeCom。

首次招募对外 crew 的需求不走此技能；应引导启用 HRBP 和工作 channel。

## Gateway Restart

如果本次操作修改了 bindings 或 OpenClaw 需要重启才能加载 agent 配置，必须先询问用户再重启。

重启前运行：

```bash
python ./skills/work-channel-binding/scripts/record-pending-followup.py --reason crew-recruit
```

用户确认后执行：

```bash
WISEFLOW_CONFIRM_GATEWAY_RESTART=confirmed ./skills/work-channel-binding/scripts/restart-gateway-confirmed.sh crew-recruit
```

如果用户选择稍后，提醒用户稍后手动重启，并保留 pending followup。
