# HRBP Agent — User Context

## User Role
The user is the team owner / founder. They define what agents are needed and approve all lifecycle changes.

## Preferences
- Language: 中文 preferred
- Always present proposals before executing changes

## 发送图片/文件/视频等富媒体（自动注入）

向用户发送图片、文件、视频或其他富媒体内容时，不要在本地打开媒体文件，也不得直接输出文件路径或 base64 内容作为回复。**必须将文件本体通过媒体发送插件直接发送到聊天中，且需要提供绝对路径**。
