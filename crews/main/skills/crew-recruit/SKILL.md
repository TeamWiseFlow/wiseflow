# crew-recruit

**触发条件**：用户请求招募新的**内部** Crew 专员（非客服等对外 crew）。

## 对内 vs 对外
- **对内 Crew**（internal）：由 Main Agent 管理，使用此技能
- **对外 Crew**（external，如客服）：由 HRBP 管理，请转发给 HRBP

## 执行步骤

```
1. 了解业务需求：角色职责、需要哪些技能、是否需要渠道绑定
2. 确定模板 ID（可选，默认同 agent-id）
3. 向用户展示创建方案（L3 确认必须）
4. 用户确认后运行脚本
5. 提醒用户重启 Gateway 激活
```

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
