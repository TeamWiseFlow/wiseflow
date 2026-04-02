# crew-dismiss

**触发条件**：用户请求下线/解除某个**内部** Crew 专员。

## 对内 vs 对外
- **对内 Crew**（internal）：由 Main Agent 管理，使用此技能
- **对外 Crew**（external，如客服）：由 HRBP 管理，请转发给 HRBP

## 执行步骤

```
1. 确认 agent-id
2. 检查非保护名单（main/hrbp/it-engineer 不可删除）
3. 展示当前配置和绑定（让用户确认）
4. 说明：workspace 将归档，可恢复
5. 用户明确确认（L3 — 必须）
6. 运行脚本
7. 更新 MEMORY.md 花名册
8. 提醒重启 Gateway
```

## 脚本用法

```bash
./skills/crew-dismiss/scripts/dismiss-internal-crew.sh <agent-id>
```

## 保护名单
以下为内置全局 Crew，不可删除、不可多实例：
- `main` — 本 agent（自身）
- `hrbp` — 对外 crew 管理员
- `it-engineer` — OFB 系统运维

## 重要约束
- 删除是不可逆操作（归档后可恢复，但需手动操作）
- 必须获得用户明确确认（L3）
