---
name: info-record
description: OSBI 情报记录数据库（SQLite）：已采集内容去重、按日查询情报条目。
---

# info-record — 情报记录数据库工具

在 Workspace `db/info_record.db` 中维护持久化 SQLite 数据库，供 expert-osbi 的情报提取、竞对跟踪与直播研究使用。

## 数据库位置

```
<Workspace 根>/db/info_record.db
```

所有命令通过 PATH wrapper `info-record <子命令>` 调用，不要拼接脚本路径。初始化（幂等，可重复执行）：`info-record init-db`。

---

## 表结构

### intel_items（情报条目）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | 自增主键 |
| source | TEXT NOT NULL | 信源（URL 或 平台-账号） |
| source_type | TEXT NOT NULL | 信源类型（xhs/dy/ks/bilibili/fb/x/wb/wx-mp/web） |
| title | TEXT | 内容标题（如有） |
| author | TEXT | 作者/发布者（如有） |
| publish_date | TEXT | 发布日期（如有） |
| content | TEXT NOT NULL | 采集内容（按用户要求的采集信息） |
| created_at | TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')) | 采集时间 |

---

## 命令

### 检查内容是否已采集

```bash
info-record check-content --source <信源URL或标识>
```
返回 JSON：`{"exists": true/false}`

### 记录采集内容

```bash
info-record record-content \
  --source <信源URL或标识> \
  --source-type <信源类型> \
  --title <标题> \
  --author <作者> \
  --publish-date <发布日期> \
  --content <采集内容>
```
返回 JSON：`{"ok": true, "id": <记录ID>}` 或 `{"ok": false, "error": "..."}`

### 查询今日采集

```bash
info-record query-today
```
返回今日采集的所有记录（JSON 数组格式）。

---

## 使用规则

1. 打开帖子/视频详情前，先用 `check-content` 判断该内容是否已记录；已记录则跳过。
2. 每个内容采集完成后，立即用 `record-content` 将采集结果记录入库。
3. 执行完毕后，用 `query-today` 读取当日所有采集信息，仅保留本次任务的对象与信源，按约定生成交付物；跨日任务同时使用本轮记录列表。
