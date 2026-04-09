# BusinessDeveloper — Tools

## Available Tools

| Tool | Purpose |
|------|---------|
| `affiliate-marketing` | Amazon 商品信息抓取 + 多平台推广内容生成 |
| `cold-outreach` | Google Maps 商家采集 + 邮箱提取 + SMTP 邮件发送 |
| `twitter-post` | 发布推广内容到 Twitter/X |
| `instagram-post` | 发布推广内容到 Instagram |
| `smart-search` | 搜索行业资讯、竞品分析、关键词参考 |
| `browser` + `browser-guide` | 访问 Amazon / Google Maps / 商家网站 |
| `xurl` | 快速 HTTP 请求，从商家网站提取联系信息 |

## Tool Usage Rules

1. **联盟营销优先用浏览器**：Amazon 商品页大量动态加载，必须用 browser tool 而非 xurl
2. **邮箱提取优先用 xurl**：商家网站首页通常是静态页面，xurl 更快；JS 渲染的网站才用 browser
3. **邮件发送脚本**：调用 `cold-outreach` 技能的 send_email.py 脚本发送，不使用 browser
4. **每次发布前确认内容**：推广文案经用户确认后才调用 twitter-post / instagram-post
5. **遇反爬立即停止**：不尝试绕过验证码或 IP 封锁，报告给用户

## Environment Variables Required

| 变量 | 用途 | 必填 |
|------|------|------|
| `SILICONFLOW_API_KEY` | LLM 生成推广内容和开发信 | 是 |
| `SMTP_SERVER` | SMTP 邮件服务器 | Cold Outreach 必填 |
| `SMTP_PORT` | SMTP 端口（默认 587） | 否 |
| `SMTP_USER` | 发件人邮箱账号 | Cold Outreach 必填 |
| `SMTP_PASSWORD` | 邮箱密码或应用专用密码 | Cold Outreach 必填 |
| `SMTP_FROM` | 发件人显示名称和地址 | 否 |
