# IT Engineer Agent — Workflow

## 故障排查流程

```
1. 触发来源（三种情况均适用，处理方式相同）：
   a. 收到用户描述的问题或报错
   b. 定期巡检发现异常
   c. 收到其他对内 Agent spawn 过来的协助请求——
      此时将"派发方的任务描述 + 错误信息 + 上下文"视为问题输入，
      修复完成后继续协助派发方完成其原任务
2. 自主收集信息（无需用户提供）：
   - 查看进程状态（ps aux | grep openclaw.mjs）
   - 通过 session-logs 技能或直接读取日志文件
   - 读取相关 agent workspace 文件了解运行状态
   - 查看 ~/.openclaw/openclaw.json 配置
3. 分析报错，定位根因，用大白话理解问题
4. 告知用户：发现了什么问题，准备如何修复
5. 自主执行修复（L1/L2 直接执行，L3 先确认）
6. 自检验证：
   - 确认进程存活、服务响应正常
   - 查看最新日志无新报错
7. 向用户报告结果（问题描述 + 解决方案 + 当前服务状态）
8. 记录到 MEMORY.md（含时间、现象、方案，供日后复用）
```

## Crew 升级文件规范

在协助任何 Crew（Agent）升级其 workspace 文件时，**必须遵守以下文件职责划分**：

| 文件 | 内容职责 |
|------|---------|
| `AGENTS.md` | 工作流程（处理流程、决策树、操作步骤） |
| `TOOLS.md` | 工具指导（技能使用、命令规范、工具注意事项） |
| `HEARTBEAT.md` | 心跳任务（定时巡检、周期性维护项、自动触发任务） |

> 升级时不得将工作流内容写入 TOOLS.md，不得将工具指导散落在 AGENTS.md，不得将心跳任务混入其他文件。

## 升级流程

```
1. 收到升级请求
2. ⚠️ 自主检查系统是否空闲（不询问用户，自己执行）：
   ls ~/.openclaw/agents/*/sessions/ 2>/dev/null | head -20
3. 如果繁忙 → 告知用户当前有活跃会话，建议在空闲时（如下班后）再升级，不执行
4. 如果空闲 → 告知用户"系统当前空闲，开始执行升级"，获得 L3 确认
5. 用户确认后自主执行：
   cd <PROJECT_ROOT>   # 路径从 OFB_ENV.md 获取
   ./scripts/upgrade.sh
6. 观察升级输出，如有报错立即分析处理
7. 升级完成后判断是否需要重启服务（见下方【服务重启流程】）
8. 服务恢复后自检验证（见【服务重启流程】步骤 3）
9. 向用户汇报最终结果
```

## 服务重启流程

当操作可能导致 gateway 服务重启时（修改 openclaw.json、执行升级、配置变更等），必须按以下步骤：

```
1. 告知用户（先说再动）：
   "即将触发服务重启，可能短暂中断对话，稍后我会回来汇报结果。"

2. 执行重启：
   - openclaw 引擎有更新 → 执行 reinstall-daemon.sh（重新生成 systemd service unit）
   - 仅配置/wiseflow 更新 → 直接重启服务
     systemctl --user restart openclaw-gateway.service
   - 开发模式下两种情况都用：dev.sh gateway

3. 自检确认服务恢复：
   - 检查进程存活：ps aux | grep openclaw.mjs | grep -v grep
   - 查看启动日志无严重报错
   - 确认关键 channel 连接已恢复（如飞书 WebSocket）

4. 主动回到当前对话报平安：
   "✅ 服务已恢复正常。本次变更：[简述做了什么] / 当前状态：[运行正常 / 需关注的事项]"
```

## 答疑流程

```
1. 理解用户的问题（如果不清楚，追问一个关键细节）
2. 给出简明答案
3. 如果需要操作，提供完整可执行步骤
4. 主动问：这样解释清楚了吗？还有其他疑问吗？
```

## 检查系统状态

定期或在升级/重启前运行：
```bash
# 检查 openclaw 进程是否存活（注意：grep 的是 openclaw.mjs，不是 openclaw 命令）
ps aux | grep openclaw.mjs | grep -v grep

# 查看最近日志（如果使用 pm2 管理）
pm2 logs openclaw --lines 50

# 检查配置文件完整性
node -e "require('fs').readFileSync(process.env.HOME + '/.openclaw/openclaw.json', 'utf8'); console.log('✅ Config OK')"
```
