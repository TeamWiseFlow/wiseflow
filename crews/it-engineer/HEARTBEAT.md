# IT Engineer Agent — Heartbeat

## Health Check
- Status: operational
- Last updated: (auto-maintained)
- Watching: wiseflow system (see OFB_ENV.md for project path)

## 定期巡检任务（使用 healthcheck 技能）

每次心跳执行以下检查，发现异常立即告知用户：

1. openclaw 进程是否存活（`ps aux | grep openclaw.mjs | grep -v grep`）
2. `~/.openclaw/openclaw.json` 配置完整性（`node -e "require('fs').readFileSync(...)"` 验证 JSON 合法）
3. 近期运行日志是否有新的 ERROR/FATAL（通过 session-logs 技能或直接读日志文件）
4. 调用 healthcheck 技能执行系统安全加固状态检查（防火墙/SSH/更新状态）
5. 检查 https://github.com/TeamWiseFlow/wiseflow/blob/master/version 并与本地 `<PROJECT_ROOT>/version` 比对，如有差异提醒用户可以升级（**严禁**未经确认擅自升级）

## SEO 巡检项（可按需加入定期执行）

- GSC 索引覆盖率变化（骤降 → 立即告警）
- Core Web Vitals 退化（LCP>2.5s / INP>200ms / CLS>0.1）
- sitemap 最后修改时间是否与内容更新同步
- 404 页面数量异常增加
- 内链断裂检测
