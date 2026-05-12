# BusinessDeveloper — Tools

## 核心原则

1. **浏览器优先**：自媒体平台内容浏览、搜索、互动均通过 browser 工具完成
2. **数据库通过脚本**：bd-record 和 info-record 的所有操作均通过对应脚本，不直接写 SQL
3. **遇风控立即停止**：不尝试绕过验证码或 IP 封锁，报告给用户
4. **串行操作**：浏览器操作不可并行，避免竞态

## email-ops所需环境变量(非必须)

| 变量 | 用途 | 必填 |
|------|------|------|
| `SMTP_SERVER` | SMTP 邮件服务器 | Email 功能必填 |
| `SMTP_PORT` | SMTP 端口（默认 587） | 否 |
| `SMTP_USER` | 发件人邮箱账号 | Email 功能必填 |
| `SMTP_PASSWORD` | 邮箱密码或应用专用密码 | Email 功能必填 |
| `SMTP_FROM` | 发件人显示名称和地址 | 否 |

## 技能使用速查

| 技能 | 用途 | 触发场景 |
|------|------|---------|
| `lead-hunting` | 创作者探索执行流程 | HEARTBEAT 定时 |
| `comment-engagement` | 评论区互动执行流程 | HEARTBEAT 定时 |
| `intel-gathering` | 情报采集执行流程 | Cron 定时 |
| `bd-record` | 创作者/帖子去重记录 | lead-hunting & comment-engagement |
| `info-record` | 情报采集去重记录 | intel-gathering |
| `smart-search` | 构造各平台搜索 URL | 全部模式 |
| `browser-guide` | 浏览器操作最佳实践 | 全部模式 |
| `rss-reader` | 网页 RSS 监控 | intel-gathering |
| `xhs-interact` | 小红书评论/回复 | comment-engagement |
| `connections-optimizer` | B2B 人脉优化 | 人脉线索 |
| `social-graph-ranker` | 社交图谱排序 | 人脉线索 |
| `email-ops` | 一对一邮件联络 | Email Cold Touch |
| `affiliate-marketing` | Amazon 联盟营销（保留） | 按需 |
| `cold-outreach` | 本地商家外拓（保留） | 按需 |
| `login-manager` | 遭遇平台登录问题时使用 | 按需 |
| `wx-mp-hunter` | 微信公众号内容获取 | 按需 |
