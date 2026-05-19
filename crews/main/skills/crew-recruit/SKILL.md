# crew-recruit

**触发条件**：用户请求招募新的**内部** Crew 专员（非客服等对外 crew）。

## 对内 vs 对外
- **对内 Crew**（internal）：由 Main Agent 管理，使用此技能
- **对外 Crew**（external，如客服）：由 HRBP 管理，请转发给 HRBP

## 执行步骤

```
1. 了解业务需求：角色职责、需要哪些技能、是否需要渠道绑定
2. 确定模板 ID（可选，默认同 agent-id）
3. 向用户展示创建方案，等待用户确认
4. 用户确认后运行脚本
5. 脚本执行成功后，告知用户必须重启 Gateway 才能生效，并询问是否立即重启
6. 用户确认重启 → 执行 systemctl --user restart openclaw-gateway
```

> ⚠️ 步骤 5-6 是**必需**的，不可跳过。原因：openclaw 热加载对 `bindings` 变更标记为 `none`（不触发 channel 重启），而 feishu channel 在启动时将配置捕获为快照，不会自动刷新。招募新 crew 后若不重启 gateway，新 crew 的 feishu bot 收到的消息会被错误路由到 `agent:main`。只有重启 gateway 才能让所有 channel 重新加载包含新 bindings 的完整配置。

## 脚本用法

```bash
./skills/crew-recruit/scripts/recruit-internal-crew.sh <agent-id> [--template <template-id>] [--bind <channel>:<accountId>] [--note <text>]
```

### 参数说明
- `<agent-id>`：实例 ID（小写字母、数字、连字符）
- `--template <id>`：使用哪个模板（默认同 agent-id）
- `--bind <ch>:<acct>`：渠道绑定（可选，事后可手动添加）
- `--note <text>`：备注信息

### 示例
```bash
./skills/crew-recruit/scripts/recruit-internal-crew.sh sales-analyst --template developer --note "销售数据分析专员"
```

## 重要约束
- 不可创建内置保护名单中的 agent：main、hrbp、it-engineer
- workspace 必须事先创建（脚本会检查）
- 对内 Crew 使用**继承模式**技能，自动获得基线技能
- 项目级 / addon 全局技能默认不自动继承；需要在目标 workspace 的 `BUILTIN_SKILLS` 中显式声明

## 重启 Gateway

招募完成后**必须重启** gateway，否则新 crew 的渠道路由不会生效。重启前需征得用户确认：

```
招募已完成！新 crew 的配置已写入 openclaw.json。
⚠️ 需要重启 Gateway 才能激活新 crew 的渠道路由（热加载无法刷新 binding 快照）。
重启期间所有 agent 将短暂中断（约 10-15 秒）。
是否现在重启？(确认/稍后)
```

用户确认后执行：
```bash
systemctl --user restart openclaw-gateway
```

用户选择"稍后"时，提醒用户稍后手动执行上述命令。
