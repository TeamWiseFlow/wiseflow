# wiseflow backend 开发文档

## 目标

wiseflow backend 设计目标为对外功能接口，可以供 网页UI、APP UI、ChatBot以及各类下游任务（以下统称前端）调用。

同时提供一个 ws 连接和 个 http 接口。

## 整体框架

整体框架使用 fastapi 开发。通过 代码仓根目录的 [run.sh](../run.sh) 启动

端口通过环境变量  WISEFLOW_BACKEND_PORT 设定，如无设定，默认值为 8077

## http 接口

http 接口，统一响应格式为：

{"success": bool, "msg": str, "data": any}；失败时 msg 填详细原因。

### 重要说明：统一返回模式

**成功判断标准：** 根据 `success` 字段判断操作是否成功
- `success: true` - 操作成功，`data` 字段包含有效结果
- `success: false` - 操作失败，`msg` 字段包含失败原因，`data` 可能为 `null` 或默认值

http 涉及如下27个接口。

### 2、list_task 

此接口用 GET 方法即可，读取全部 task 的数据

backend 接收后，调用 AsyncDatabaseManager 的 对应方法读取 本地数据库中 task 表的数据。成功时返回任务列表（可能为空列表），失败时 msg 会有失败详情。

AsyncDatabaseManager 和 数据库schema 参考  [core/async_database.py](../core/async_database.py)

### 3、del_task

仅接收一个 task_id 的参数，字符串格式。

backend 接收后，调用 AsyncDatabaseManager 的 对应方法删除本地数据库中 task 表对应项目。成功时返回被删除的 task_id，失败时 msg 会有失败详情。

AsyncDatabaseManager 和 数据库schema 参考  [core/async_database.py](../core/async_database.py)

### 4、read_task

此接口用 GET 方法即可，仅接收一个 task_id 的参数，字符串格式。

backend 接收后，调用 AsyncDatabaseManager 的 对应方法读取本地数据库中 task 表中对应条目。成功时返回任务详情，任务不存在时返回空结果，查询失败时 msg 会有失败详情。

AsyncDatabaseManager 和 数据库schema 参考  [core/async_database.py](../core/async_database.py)

### 5、add_task

接收一个请求体，代表了新增 task 的数据。新增支持可选字段 `title`（任务标题，字符串）。

请求体主要字段：

- `focuses: (int|object)[]`（可选）
- `search: string[]`（可选）
- `title: string[]`（可选）
- `sources: {type, detail}[]`（可选）
- `activated: boolean`（可选，默认 true）
- `time_slots: ("1st"|"2nd"|"3rd"|"4th")[]`（可选）
- `title: string`（可选，默认空字符串）

backend 接收后，调用 AsyncDatabaseManager 的 对应方法在本地数据库的 tasks 表中新增一个项目。成功时返回新增的 task_id，失败时 msg 会有失败详情。

AsyncDatabaseManager 和 数据库schema 参考  [core/async_database.py](../core/async_database.py)

### 6、update_task

接收一个请求体， 必须包含 task_id 和 需要更改的内容。支持更新 `title` 字段。

可更新字段：`focuses`、`search`、`sources`、`activated`、`time_slots`、`title`、`status`、`errors`。

backend 接收后，调用 AsyncDatabaseManager 的 对应方法更新本地数据库的 tasks 中的项目。成功时返回被更新的 task_id，失败时 msg 会有失败详情。

特别注意：

search time_slot 这些也是这样，

本质上，backend 接受后，会按提供的内容进行覆盖写

**如果更新涉及 focuses 一定要特别注意**

- 如果focused 完全不更新，则提交的 focuses 为None （这一项不提交）；
- 如果有新增 focus 或者某个 focus 更新，则提交 focuses 为 【 dict， int， dict 。。。】 （dict对应新增或者更新的 focus，int 对应不变的 focus 的 id）
- 如果传入删除某个 focus，则提交focuses 为  【int, int,....] (int 为保留的那些 focus 的 id）
- 2、3也可以一起用，就是不在列表里面的 id 都会解除与 task 的关联

AsyncDatabaseManager 和 数据库schema 参考  [core/async_database.py](../core/async_database.py)

### 7、read_focus

此接口用 GET 方法即可，没有参数

backend 接收后，调用 AsyncDatabaseManager 的 对应方法读取本地数据库中 focuses 表中所有条目返回。成功时返回 focus 详情，focus 不存在时返回空结果，查询失败时 msg 会有失败详情。

AsyncDatabaseManager 和 数据库schema 参考  [core/async_database.py](../core/async_database.py)

注意：仅允许前端读取 focus，focus 的更新（实际是新增一条，更新与 task 的关联）或删除（其实是与 task 解除关系）只能通过 update_task 接口。

### 8、 list_info 

此接口用 GET 方法，接收两个可选参数：

- `start_time`：查询此时间之后新增的消息，使用 ISO 8601 UTC 格式（如 2025-01-01T00:00:00Z），不填表示不限时间（默认值为 null）
- `max_items_per_focus`：每个 focus 最多返回的信息数量，0 或负数表示使用默认值 12，最大不超过 12（默认值为 0）

**重要特性：**
- backend 使用单次批量查询优化，避免多次数据库访问
- 按**所有**数据库中的 focus_id 分组返回对应 focus_id 下符合条件的 infos
- 即使某个 focus_id 没有符合条件的 infos，也会在返回结果中体现为空数组
- 每个 focus 最多返回 12 条信息（硬限制，保证性能）

**返回数据格式：**

```json
{
  "success": true,
  "msg": "",
  "data": {
    "1": [info1, info2, ...],
    "2": [info3, info4, ...],
    "3": []
  }
}
```

**注意事项：**

- 每个 focus_id 对应的 info 数组按 created 时间降序排列（新 -> 旧）
- focus_id 之间无特定排序，如需按更新时间排序，可取每个数组第一个 info 的 created 时间
- focus 对外展示建议使用 focus_statement 而非 id（同一 focus_id 下所有 info 的 focus_statement 相同）
- 时间格式统一使用 ISO 8601 UTC（如 2025-01-01T00:00:00Z），前端可用 `new Date().toISOString()` 生成

**示例调用：**

```bash
# 获取所有 focus 的最新信息（每个最多12条）
GET /list_info

# 获取 2025年1月1日之后的信息（每个 focus 最多12条）
GET /list_info?start_time=2025-01-01T00:00:00Z

# 获取最近信息，每个 focus 最多5条
GET /list_info?max_items_per_focus=5

# 获取指定时间后的信息，每个 focus 最多10条
GET /list_info?start_time=2025-01-01T00:00:00Z&max_items_per_focus=10
```

AsyncDatabaseManager 和 数据库schema 参考  [core/async_database.py](../core/async_database.py)

### 9、 del_info

仅接收一个 info_id 的参数，字符串格式。

backend 接收后，调用 AsyncDatabaseManager 的 对应方法删除本地数据库中 infos 表对应项目。成功时返回被删除的 info_id，失败时 msg 会有失败详情。

AsyncDatabaseManager 和 数据库schema 参考  [core/async_database.py](../core/async_database.py)

### 10、 read_info

此接口用 POST 方法，支持复杂的条件查询和分页，接收 JSON 请求体。

**请求参数：**

- `focuses`：要查询的 focus ID 列表，数组类型，可选（不填表示查询所有 focus）
- `per_focus_limit`：每个 focus 最多返回的信息数量，整数，可选（默认 50，最大 50）
- `limit`：总体返回数量限制，整数，可选（默认 20，最大 1000）
- `offset`：分页偏移量，整数，可选（默认 0）
- `start_time`：时间范围开始，ISO 8601 UTC 格式，可选
- `end_time`：时间范围结束，ISO 8601 UTC 格式，可选
- `source_url`：按来源 URL 精确查询，可选（与其他条件可组合）
- `info_id`：按 info 唯一 ID 精确查询，可选

**重要限制：**
- `per_focus_limit` 和 `limit` 不能同时为 0
- 使用单次批量查询优化，支持窗口函数或应用层分组
  
> 说明：当提供 `info_id` 或 `source_url` 进行精确查询时，即使 `per_focus_limit = 0` 且 `limit = 0`，也允许查询；否则会返回错误。

**请求示例：**

```json
{
  "focuses": [1, 2, 3],
  "per_focus_limit": 30,
  "limit": 100,
  "offset": 0,
  "start_time": "2025-01-01T00:00:00Z",
  "end_time": "2025-12-31T23:59:59Z"
}
```

```json
{
  "limit": 50,
  "offset": 20,
  "start_time": "2025-01-01T00:00:00Z"
}
```

```json
{
  "info_id": "abc123def456"
}
```

```json
{
  "source_url": "https://example.com/article/42",
  "start_time": "2025-01-01T00:00:00Z"
}
```

**返回格式：**

```json
{
  "success": true,
  "msg": "",
  "data": [
    {
      "id": "abc123",
      "type": "article",
      "content": "信息内容...",
      "focus_statement": "焦点描述",
      "focus_id": 1,
      "source_url": "https://example.com",
      "source_title": "来源标题",
      "refers": "引用信息",
      "created": "2025-01-01T12:00:00Z"
    }
  ]
}
```

**注意事项：**

- 返回结果按 `created` 时间降序排列（新 -> 旧）
- 时间格式统一使用 ISO 8601 UTC（如 2025-01-01T00:00:00Z）
- 支持灵活的时间范围查询和分页
- 当同时指定 `per_focus_limit` 和 `limit` 时，两个限制都会生效
- 前端生成时间：JavaScript 用 `new Date().toISOString()`，Python 用 `datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')`

AsyncDatabaseManager 和 数据库schema 参考  [core/async_database.py](../core/async_database.py)


### 12、13、14、15 local_proxies 的增删改查接口：

分别对应 local_proxies表单的 list、del、update 和 add 

- **list**: 成功时返回代理列表，失败时 msg 会有失败详情
- **add**: 成功时返回新增代理的 id，失败时 msg 会有失败详情  
- **update**: 成功时返回更新后代理的id，失败时 msg 会有失败详情
- **del**: 成功时返回被删除的代理 id，失败时 msg 会有失败详情 

AsyncDatabaseManager 和 数据库schema 参考  [core/async_database.py](../core/async_database.py)

### 16、17、18、19 kdl_proxies 的增删改查接口：

分别对应 kdl_proxies 表单的 list、del、update 和 add 

- **list**: 成功时返回 KDL 代理列表，失败时 msg 会有失败详情
- **add**: 成功时返回新增 KDL 的 id，失败时 msg 会有失败详情
- **update**: 成功时返回更新后 KDL 代理的id，失败时 msg 会有失败详情  
- **del**: 成功时返回被删除的 KDL 代理 id，失败时 msg 会有失败详情 

AsyncDatabaseManager 和 数据库schema 参考  [core/async_database.py](../core/async_database.py)

### 20、21、22、23 mc_backup_accounts 的增删改查接口：

分别对应 mc_backup_accounts 表单的 list、del、update 和 add 

- **list**: 成功时返回备份账户列表，失败时 msg 会有失败详情
- **add**: 成功时返回新增备份账户的 id，失败时 msg 会有失败详情
- **update**: 成功时返回更新后备份账户的id，失败时 msg 会有失败详情
- **del**: 成功时返回被删除的备份账户 id，失败时 msg 会有失败详情 

AsyncDatabaseManager 和 数据库schema 参考  [core/async_database.py](../core/async_database.py)

# 24、list_config 接口

本接口使用 GET 方法即可，backend 接收后，返回的主体数据是一个字典，包含了目前运行中的 config 字典

# 25、reset_config 接口

本接口使用 GET 方法即可，backend 接收后 会把运行中的 config 重置为默认值，只返回成功与否

**注意：这里仅仅是删除本地保存的用户配置文件，需要提醒用户，设置更改要重新启动 wiseflow 本地程序**

# 26、update_config 接口

本接口使用 POST 方法，payload 是需要更新的项目

backend 接收后会对应更新相关的项目，并把更新后的项目，保存在 work_dir/user_configs.json 中

然后返回 success。

**注意：这里仅仅是更新本地保存的用户配置文件，需要提醒用户，设置更改要重新启动 wiseflow 本地程序**

# 27、clear_task_errors 接口

本接口使用 GET 方法，仅接收一个 task_id 的参数，int格式。

backend 接收后，调用 AsyncDatabaseManager 的 clear_task_error 方法清除指定任务的错误信息并将状态重置为正常。成功时返回被清除错误的 task_id，失败时 msg 会有失败详情。

AsyncDatabaseManager 和 数据库schema 参考 [core/async_database.py](../core/async_database.py)

# 28、ws_history 接口

本接口使用 GET 方法，接收 `limit` 和 `offset` 两个参数。

- 功能：返回最近的 websocket 历史消息记录。
- 存储字段：`type: string`，`prompt_id: string|null`，`code: int|null`，`params: string[]`，`actions: object[]`，`action_id: string|null`，`timeout: int|null`，`ts: number`（Unix 秒）。
- 排序与分页：按 `ts` 倒序排列，支持 `limit` 与 `offset`。
- 自动清理：每次读取前会自动清理 `ts` 超过 24 小时的历史记录。

返回内容示例：

```
{
  "success": true,
  "msg": "",
  "data": [
    { "type": "notify", "code": 1, "params": ["用户名", "5分钟前"], "timeout": 180, "ts": 1700000000.123 },
    { "type": "prompt_resolved", "prompt_id": "abc123", "action_id": "done", "ts": 1700000001.234 }
  ]
}
```
