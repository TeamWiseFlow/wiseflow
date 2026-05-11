# BusinessDeveloper — Tools

## 核心原则

1. **浏览器优先**：自媒体平台内容浏览、搜索、互动均通过 browser 工具完成
2. **数据库通过脚本**：bd-record 和 info-record 的所有操作均通过对应脚本，不直接写 SQL
3. **遇风控立即停止**：不尝试绕过验证码或 IP 封锁，报告给用户
4. **串行操作**：浏览器操作不可并行，避免竞态

## 所需环境变量

| 变量 | 用途 | 必填 |
|------|------|------|
| `SILICONFLOW_API_KEY` | LLM 生成话术和分析内容 | 是 |
| `SMTP_SERVER` | SMTP 邮件服务器 | Email 功能必填 |
| `SMTP_PORT` | SMTP 端口（默认 587） | 否 |
| `SMTP_USER` | 发件人邮箱账号 | Email 功能必填 |
| `SMTP_PASSWORD` | 邮箱密码或应用专用密码 | Email 功能必填 |
| `SMTP_FROM` | 发件人显示名称和地址 | 否 |

## 技能工具映射

| 工具/技能 | 用途 |
|-----------|------|
| browser | 所有自媒体平台操作（搜索、浏览、互动） |
| smart-search | 构造平台搜索 URL |
| browser-guide | 浏览器操作最佳实践（登录、CAPTCHA等） |
| bd-record | 创作者/帖子去重记录（SQLite 脚本） |
| info-record | 情报采集去重记录（SQLite 脚本） |
| xhs-interact | 小红书专用互动（评论/回复/点赞） |
| email-ops | 一对一邮件联络 |
