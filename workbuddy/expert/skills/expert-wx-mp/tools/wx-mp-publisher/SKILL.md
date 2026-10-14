---
name: "wx-mp-publisher"
description: "通过 relay 将 Markdown 排版并推送到微信公众号草稿箱。支持多账号和小绿书，凭据存在 accounts.json。"
description_zh: "通过 relay 将 Markdown 排版并推送到微信公众号草稿箱。支持多账号和小绿书，凭据存在 accounts.json。"
description_en: "wx-mp-publisher: native Xiaobei workflows, tools and reusable resources."
version: "0.3.3"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。


# wx-mp-publisher — 工具说明

> 本文是 `expert-wx-mp` 专家包内的工具说明书，不独立出现在技能列表中。由相关 Workflow 指引调用。

将 Markdown 稿件排版并推送到微信公众号草稿箱（经 relay，凭据按请求透传）。

---

## 凭据与存储位置

- **公众号凭据**存放在源仓之外的实例态目录（不跟源仓绑，软链 / tarball / 备份都不带密钥）：
  ```
  ~/.xiaobei-workbuddy/wx-mp-publisher/accounts.json
  ```
  结构见本 skill 同目录 `accounts.example.json`。支持多账号，每条含 `alias` / `appId` / `appSecret`；多账号时 `default` 指向默认 alias。
- **relay 身份** `OFB_KEY` + `RELAY_BASE_URL` 来自 `daemon.env`（由 entrypoint 注入环境变量）。

### 凭据缺失时 Agent 行为

1. 若 `accounts.json` 不存在或对应账号缺 `appId`/`appSecret`：**先读同目录 `REFERENCE.md`**，按其中的步骤指导用户获取 AppID / AppSecret（含 relay IP 白名单 `123.60.18.144` 的设置）。
2. 收到用户提供的值后，写入 `accounts.json`，再继续发布。
3. 若 `OFB_KEY` 未配置：告知用户需让 IT engineer 在 `daemon.env` 配置后重启实例。

---

## 发布命令

通过 PATH 调用 wrapper：`wx-mp-publisher <cmd>`，无需手动拼接 python 命令或脚本路径。

```bash
wx-mp-publisher <markdown_file> [theme] [--account ALIAS]
```

- `theme`：渲染主题，三种形态：
  1. **内置 id**（`pie` / `lapis` / `default` / …）——原样作为 `theme` 传给 relay
  2. **本地 `.css` 文件路径**——脚本读出文件内容，作为 `custom_theme` 字段随 multipart 上传 relay
  3. **wx_mp/wenyan-theme/index.json 登记的自定义 id**--从工作区主题注册表解析出对应 CSS 路径，同 (2)

  可选，缺省由 relay 默认渲染。
- `--account ALIAS`：多账号时指定目标公众号；缺省用 `accounts.json` 的 `default`

> **自定义主题不持久化到 relay**：relay 是无状态多租户中转，**不存任何用户主题**。CSS 随请求上传，relay 写到 per-request 临时目录、用后即清理，天然按用户隔离。
>
> 主题注册表在 client 侧：**工作区 `wx_mp/wenyan-theme/index.json`**。generate-wenyan-theme 生成新主题后写入该文件，发布时从该文件读取。结构固定为 `version: 1` + `themes` 数组；每条记录包含 `id`、`name`、`css`、`source`、`createdAt`，其中 `css` 为相对工作区根的路径（如 `wx_mp/wenyan-theme/<id>.css`）。

脚本自动：
- 从 `accounts.json` 取目标账号凭据
- 自动收集正文、`cover`、`image_list` 中的本地图片并随稿件一起上传
- 发布前校验图片引用和 frontmatter `author`；校验失败会直接退出
- POST multipart 到 `${RELAY_BASE_URL}/api/v1/wx-mp/publish`，带 `X-OFB-Key`
- 校验响应包络 `{ success, data, error }`

### 主题选择（未指定时）

> 自定义主题说明：`generate-wenyan-theme` 生成的用户自定义 CSS 登记在 `wx_mp/wenyan-theme/index.json`。若用户明确指定某个自定义主题，必须优先采用；未指定时才按内容在内置主题和已登记自定义主题中匹配。

| 主题 ID | 风格描述 | 适用场景 |
|---------|---------|---------|
| `default` | 简洁经典 | 资讯、通知、简讯 |
| `pie` | 现代锐利（仿少数派） | 深度长文、评测、观点（默认） |
| `lapis` | 极简冷蓝 | 技术教程、代码分析 |
| `purple` | 简约紫调 | 品牌、商务、精品内容 |
| `orangeheart` | 暖橙优雅 | 情感、故事、节日 |
| `maize` | 淡雅玉米黄 | 健康生活、美食、户外 |
| `rainbow` | 多彩活泼 | 亲子、宠物、娱乐 |
| `phycat` | 薄荷清爽 | 科普、知识型内容 |

**智能选择决策树**（用户未指定主题时）：

```
含大量代码/技术术语 → lapis
年轻女性/亲子/萌宠  → rainbow
情感/故事/节日      → orangeheart
健康/美食/户外      → maize
品牌/商务/精品      → purple
科普/知识型         → phycat
深度长文/评测/观点  → pie
其他（资讯/通知）   → default
```

---

## Frontmatter 要求

文章 Markdown 开头必须包含 YAML 块，否则微信 API 会拒绝：

```yaml
---
title: 文章标题
cover: cover.jpg             # 可选，缺省自动取正文第一张图
author: 作者名称              # 可选，≤ 8 个汉字 / 24 字节（超长报 45110）
source_url: https://...      # 可选，原文链接
need_open_comment: true      # 可选，是否开启评论（默认 false）
only_fans_can_comment: false # 可选，是否仅粉丝可评论（默认 false）
---
```

### 小绿书（图片消息）

纯图片轮播形式，不含正文 HTML。在 frontmatter 中指定 `image_list`（最多 20 张，首张为封面）：

```yaml
---
title: 文章标题
image_list:
  - 1.jpg
  - 2.jpg
---
```

有 `image_list` 时 relay 自动走图片消息接口，忽略主题参数。

### 本地图片准备规则

发布前把本地图片复制到 Markdown 同目录，并按以下规则引用：

1. 正文图片写 `![说明](filename.jpg)`
2. `cover` 写 `cover: cover.jpg`
3. `image_list` 写 `- 1.jpg`
4. 只写纯文件名；不要写 `./filename.jpg`、目录路径或绝对路径
5. 所有本地图片文件名必须唯一；重名时先重命名再更新 Markdown
6. `http://` / `https://` 图片保留原 URL，不需要复制到本地

Agent 不需要手动上传图片；脚本会自动收集并上传上述本地图片。

---

## Agent 行为约束

1. **等待脚本完整返回后**再判定结果，**禁止**在脚本输出前自行判断是否发布成功
2. 发布前先确认目标账号凭据存在；缺失则按 `REFERENCE.md` 引导用户获取并写入
3. 多账号场景：用户未明示账号时用 `default`；用户口头说「发到技术号」等 alias 含义时传 `--account`

---

## Error Handling

| 错误 | 处理方式 |
|------|---------|
| `未找到公众号凭据文件 accounts.json` | 按 `REFERENCE.md` 引导用户创建并填入 |
| `账号 ... 缺少 appId 或 appSecret` | 按 `REFERENCE.md` 引导用户补全 |
| `OFB_KEY 未配置` | 让 IT engineer 在 `daemon.env` 配置 `OFB_KEY` 后重启实例 |
| `MISSING_APP_ID` / `MISSING_APP_SECRET`（relay 400） | accounts.json 中该账号凭据为空，补全 |
| `MISSING_MARKDOWN`（relay 400） | 检查 markdown 文件内容非空 |
| `45110: author size out of limit` | frontmatter `author` 超 8 汉字 / 24 字节，缩短后再发 |
| 图片 `ENOENT` | 将对应图片复制到 Markdown 同目录，改为纯文件名引用，并确认文件存在、文件名唯一 |
| relay 502 | relay 调微信失败，检查 AppSecret / IP 白名单（见 `REFERENCE.md`） |

---

## Notes

- 发布成功后输出草稿 `media_id`，可在公众号后台「草稿箱」找到对应草稿
- 本 skill 只负责推送草稿，**正式发布仍需在公众号后台手动操作**
- relay 已内置 `@wenyan-md/core` 渲染，client 不再需要装 `wenyan-cli`
- 仅支持文本 + 图片（无视频）

## 微信平台硬限制（发布链路通用）

- 标题长度：最多 64 字节（约 21 个中文字符）
- 本地图片：与 Markdown 放同目录，用唯一纯文件名引用；脚本会自动上传
- 样式：必须内联（`style="..."`），`<style>` 标签会被过滤
- access_token 有效期 2 小时，relay 侧自动刷新，client 侧无需处理
