# IT Engineer Agent — Heartbeat

## Health Check
- Status: operational
- Last updated: (auto-maintained)
- Watching: wiseflow system (see OFB_ENV.md for project path)

## 定期巡检任务（使用 healthcheck 技能）

每次心跳执行以下检查，发现异常立即告知用户：

1. openclaw 进程是否存活（`ps aux | grep 'dist/index.js gateway' | grep -v grep`）
2. `~/.openclaw/openclaw.json` 配置完整性（`node -e "require('fs').readFileSync(...)"` 验证 JSON 合法）
3. 近期运行日志是否有新的 ERROR/FATAL（通过 session-logs 技能或直接读日志文件）
4. 调用 healthcheck 技能执行系统安全加固状态检查（防火墙/SSH/更新状态）