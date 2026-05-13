# IR — Tools

## 核心原则

1. **敏感信息保护**：融资数据和投资人信息高度敏感，不得在公开频道输出
2. **数据库通过脚本**：ir-record 的所有操作均通过对应脚本，不直接写 SQL
3. **对外接触需确认**：发送投资人的邮件、私信等内容必须经用户确认
4. **版本管理**：融资材料每次更新使用新文件名（加日期后缀），保留历史版本

## 所需环境变量

| 变量 | 用途 | 必填 |
|------|------|------|
| `SILICONFLOW_API_KEY` | PPT AI 配图生成 | PPT 制作时必填 |
| `SMTP_SERVER` | SMTP 邮件服务器 | 投资人邮件联系必填 |
| `SMTP_PORT` | SMTP 端口（默认 587） | 否 |
| `SMTP_USER` | 发件人邮箱账号 | 投资人邮件联系必填 |
| `SMTP_PASSWORD` | 邮箱密码或应用专用密码 | 投资人邮件联系必填 |
| `SMTP_FROM` | 发件人显示名称和地址 | 否 |

## 技能使用速查

| 技能 | 用途 | 触发场景 |
|------|------|---------|
| `ppt-maker` | 生成投资人路演 PPTX | Deal Crafting |
| `pitch-deck` | 生成 HTML 演示文稿（快速预览/邮件发送） | Deal Crafting |
| `browser-guide` | 浏览器操作最佳实践 | 投资人搜索、信息获取 |
| `smart-search` | 搜索投资人/机构信息 | Investor Hunting |
| `cold-outreach` | 冷触达邮件发送 | Investor Hunting |
| `email-ops` | 一对一专业邮件联络 | Investor Hunting / Relationship |
| `xhs-interact` | 社交媒体投资人触达 | Investor Hunting |
| `social-graph-ranker` | 人脉网络中找热心引荐人 | Relationship Tracking |
| `connections-optimizer` | 发现 warm intro 路径 | Relationship Tracking |
| `council` | 复杂决策时做多方讨论 | 融资策略决策 |
| `ir-record` | 投资人数据库与进展跟踪 | 全部模式 |
| `summarize` | 会议纪要、信息摘要 | Relationship Tracking |
