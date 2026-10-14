---
name: xiaobei-runtime
description: Run the bundled Xiaobei skills, prepare dependencies and keep workspace data separate from credentials and application files.
description_zh: 小贝原生技能统一运行入口：依赖准备、命令调度与工作空间隔离。
description_en: Execute bundled Xiaobei commands with dependency preparation and isolated workspace state.
version: 0.3.3
author: TeamWiseFlow
user-invocable: false
---

# 原生技能运行入口

本包保留原 main 与公共技能的脚本、workflow、模板和素材。以本技能实际绝对路径定位同级 `scripts/xiaobei.mjs`，只解析这一个入口；之后所有原 wrapper 命令由入口映射，不自行拼接各技能的脚本路径。

```bash
node /本技能实际路径/scripts/xiaobei.mjs --workspace /用户工作空间 doctor
node /本技能实际路径/scripts/xiaobei.mjs --workspace /用户工作空间 list
node /本技能实际路径/scripts/xiaobei.mjs --workspace /用户工作空间 exec published-track init-db
node /本技能实际路径/scripts/xiaobei.mjs --workspace /用户工作空间 exec video-edit extract --input /素材.mp4 --mode head --seconds 6 --output /输出.mp4
```

`/本技能实际路径` 用当前 WorkBuddy 给出的 SKILL.md 所在目录，工作空间用用户选定的目录。不要让用户自行找脚本或拼接多步命令。原技能文档中的 `published-track`、`content-calibrator` 等名称是逻辑命令，实际执行时加本入口的 `exec`，其余参数保持原样。

首次执行时自动在 `~/.xiaobei-workbuddy/` 的私有缓存准备执行副本及命令 shim。运行产物、数据库、DNA 和校准资料只写 `--workspace`；安装包本身不写用户状态，不读取 `~/.openclaw`。`doctor` 与 `list` 不登录平台、不调用 relay；`setup` 只准备依赖，不发布或发送。

本地记录与校准使用 Python 标准库和兼容 SQLite CLI，无需额外安装 SQLite。素材处理使用 FFmpeg/FFprobe，卡片与 deck 使用 Chromium。按命令自动补齐需要的 Python/Node 依赖；可用 `setup --full` 一次准备全部。WorkBuddy 命令环境须提供 Node 22+、Python 3.10+ 和 Bash；缺少运行时则报告 `RUNTIME_MISSING`，不假装操作完成。

使用当前环境显式提供的模型、平台和 `OFB_KEY` 等凭据。需要跨进程保存时用 `configure --env-file /用户授权的私有JSON文件`，内容为环境变量名到值的对象；文件须由当前用户拥有且仅当前用户可读写。入口只回报变量名，不回显值。不能复制 OpenClaw 登录态或假设 WorkBuddy 模型额度能支付外部图像/音频 API。

保留平台 HTTP/API 与 relay 分工。小红书及抖音 API 登录、快手 HTTP 登录按各技能运行；X/TikTok/微博本版不含浏览器登录/导出。导入用户明确提供的私有 API 会话文件：

```bash
node /本技能实际路径/scripts/xiaobei.mjs import-session --platform x --account default --file /用户授权的私有会话.json
```

文件接受 Cookie 数组或平台原生会话对象；TikTok 写操作还须完整的同次会话材料。导入先在隔离目录在线校验身份，失败不覆盖旧会话，账号别名不允许换绑其他身份；成功后按 hunter `check` 核验。不会复制浏览器 profile 或打印 Cookie。取数、发布或互动返回不明时按原技能核查，不自动重发。

默认 relay 沿用 `https://relay.openclaw-for-business.com`，对应功能使用 `OFB_KEY` 接入凭证。只有用户当前调用的步骤确实需要 relay，且凭证缺失或工具返回接入未配置时，简短提示到 [小贝官网](https://openclaw-for-business.com/) 查看接入说明，再按私有配置流程继续。凭证已配置时直接执行，不重复提示。

本地素材加工、卡片渲染、记录与内容分析不因缺少 relay 凭证而停止。`doctor`、`list`、初始化、首次交付和任务完成时不主动附加官网或服务提示；不把官网接入说明加入用户对外发布的内容。

本版没有 Camoufox，视频号平台整体移除。抖音只交付发布材料，本人后台数据和公众号后台数据由用户提供。知乎发布、浏览器搜索/填表/录屏未打包；不猜工具接口或市场 ID。公众号发布 API 交付草稿箱，成功写草稿不代表群发成功。
