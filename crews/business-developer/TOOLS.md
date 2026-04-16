# BusinessDeveloper — Tools

## Tool Usage Rules

1. **联盟营销优先用浏览器**：Amazon 商品页大量动态加载，必须用 browser tool
2. **邮件发送脚本**：调用 `cold-outreach` 技能的 send_email.py 脚本发送，不使用 browser
3. **每次发布前确认内容**：推广文案经用户确认后才调用 twitter-post / instagram-post
4. **遇反爬立即停止**：不尝试绕过验证码或 IP 封锁，报告给用户

## Environment Variables Required

| 变量 | 用途 | 必填 |
|------|------|------|
| `SILICONFLOW_API_KEY` | LLM 生成推广内容和开发信 | 是 |
| `SMTP_SERVER` | SMTP 邮件服务器 | Cold Outreach 必填 |
| `SMTP_PORT` | SMTP 端口（默认 587） | 否 |
| `SMTP_USER` | 发件人邮箱账号 | Cold Outreach 必填 |
| `SMTP_PASSWORD` | 邮箱密码或应用专用密码 | Cold Outreach 必填 |
| `SMTP_FROM` | 发件人显示名称和地址 | 否 |
