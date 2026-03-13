# Wiseflow Addon for OpenClaw

浏览器反检测 + Tab Recovery + Smart Search + RSS Reader + 新媒体小编 Crew。

本目录是 [wiseflow](https://github.com/TeamWiseFlow/wiseflow) 提供给 [openclaw-for-business](https://github.com/TeamWiseFlow/openclaw_for_business) 的标准 addon 包。

## 功能

### 1. Patchright 反检测浏览器

通过 pnpm overrides 将 `playwright-core` 替换为 `patchright-core`，无需修改上游源码。显著降低自动化浏览器被目标网站识别和拦截的概率，从而不需要安装 chrome relay extension，只用托管浏览器也能达到与 relay 同样、甚至更优的网络获取与操作能力。

### 2. Tab Recovery 补丁

当 Agent 操作过程中目标标签页意外关闭或消失时，自动进行快照级别的标签页恢复，确保任务不会因标签页丢失而中断。

### 3. Smart Search（智能搜索）

替代 openclaw 内置的 `web_search`，提供更强大的搜索能力。相比原版内置的 web search tool，具备三大核心优势：

- **完全免费，无需 API Key**：不依赖任何第三方搜索 API，零成本使用
- **即时搜索，时效性最佳**：直接驱动浏览器前往目标页面或各大社交媒体平台（微博、Twitter/X、facebook 等）进行搜索，第一时间获取最新发布的内容
- **信源可自定��**：用户可以自由指定搜索源，精准匹配自己的信息需求

### 4. Browser Guide 技能

教会 agent 处��登录墙、验证码、懒加载、付费墙等场景的最佳实践。

### 5. RSS Reader 技能

支持读取 RSS/Atom Feed，可订阅任意支持标准 feed 格式的内容源。

### 6. 新媒体小编 Crew

开箱即用的中文自媒体内容创作 AI Agent，配置于 `crew/new-media-editor/`。

**核心工作流：**

- **Mode A**：选题调研 → 热点分析 → 图文草稿
  深入采集微博实时热搜、小红书、知乎、B 站、抖音等平台的最新内容，分析热点角度与��异化切入点，生成完整图文草稿。

- **Mode B**：草稿扩写 → 完整文章
  接收用户的草稿片段或关键词，搜寻网络佐证（数据、权威来源、真实案例），扩展为结构完整的文章。

- **文章排版（Output Strategy）**：定稿后自动调用 [文颜（Wenyan）](https://github.com/caol64/wenyan) 将 Markdown 渲染为公众号风格 HTML，内置 7 套主题并根据文章内容智能匹配，同时生成 Markdown 原文备份。

- **Mode C**：推送微信公众号草稿箱（需配置 `WECHAT_APP_ID`/`WECHAT_APP_SECRET`）

**Crew 专属技能：**

| 技能 | 说明 |
|------|------|
| `siliconflow-img-gen` | 文生图，调用 SiliconFlow API 生成配图（需 `SILICONFLOW_API_KEY`） |
| `siliconflow-video-gen` | 文生视频 / 图生视频（需 `SILICONFLOW_API_KEY`） |
| `wenyan-formatter` | Markdown → 公众号风格 HTML 渲染，或直接推送草稿箱 |



## 安装

将本目录复制到 openclaw_for_business 的 `addons/` 目录：

```bash
# 方式一：从 wiseflow 仓库复制
git clone https://github.com/TeamWiseFlow/wiseflow.git /tmp/wiseflow
cp -r /tmp/wiseflow/wiseflow <openclaw_for_business>/addons/wiseflow

# 方式二：如果已有 wiseflow 仓库
cp -r /path/to/wiseflow/wiseflow <openclaw_for_business>/addons/wiseflow
```

安装后重启 openclaw 即可生效（`dev.sh` 会自动扫描并应用）。

## 目录结构

```
wiseflow/
├── addon.json                    # 元数据（名称、版本、描述）
├── overrides.sh                  # pnpm overrides: playwright-core → patchright-core + 禁用内置 web_search
├── patches/
│   ├── 001-browser-tab-recovery.patch        # 标签页恢复补丁
│   ├── 002-disable-web-search-env-var.patch  # 禁用内置 web_search（env var）
│   ├── 003-act-field-validation.patch        # ACT 字段校验补丁
│   └── 004-web-fetch-allow-rfc2544.patch     # 允许 RFC 2544 假 IP（代理 fake-IP DNS 兼容）
├── skills/                       # 全局技能（所有 Agent 可用）
│   ├── browser-guide/SKILL.md    # 浏览器使用最佳实践
│   ├── smart-search/SKILL.md     # 多平台搜索 URL 构造（替代内置 web_search）
│   └── rss-reader/               # RSS/Atom Feed 读取器
│       ├── SKILL.md
│       ├── package.json
│       └── scripts/fetch-rss.mjs
└── crew/                         # Crew 模板（由 HRBP 管理）
    └── new-media-editor/         # 新媒体小编（command-tier: T1）
        ├── SOUL.md               # 角色定义 + 权限级别声明
        ├── IDENTITY.md           # Agent 身份设定
        ├── AGENTS.md             # 工作流程（Mode A/B/C + Image/Video Strategy）
        ├── TOOLS.md              # 工具清单与使用规则
        ├── BOOTSTRAP.md          # 首次启动引导
        ├── BUILTIN_SKILLS        # 内置全局技能列表
        ├── DENIED_SKILLS         # 禁用技能列表
        ├── ALLOWED_COMMANDS      # 命令权限微调（T1 + bash/python3/node/npx）
        ├── MEMORY.md / TASKS.md / HEARTBEAT.md / USER.md
        └── skills/               # Crew 专属技能
            ├── siliconflow-img-gen/   # 文生图（SiliconFlow Images API）
            │   ├── SKILL.md
            │   └── scripts/gen.py
            ├── siliconflow-video-gen/ # 文生视频（SiliconFlow Video API）
            │   ├── SKILL.md
            │   └── scripts/gen.py
            └── wenyan-formatter/      # Markdown 排版 & 公众号发布
                ├── SKILL.md
                └── scripts/format.sh
```

## 四层加载机制

addon 被 `apply-addons.sh` 加载时按以下顺序执行：

1. **overrides.sh** — pnpm overrides 替换 playwright-core 为 patchright-core，并禁用内置 web_search（最稳健，不依赖行号）
2. **patches/*.patch** — git patch 精确代码改动（上游更新时可能需调整）
3. **skills/*/SKILL.md** — 全局技能安装（所有 Agent 可见）
4. **crew/*/** — Crew 模板安装到 `crews/`，由 HRBP 管理实例化

## 要求

- OpenClaw >= 2026.2
- pnpm（由 openclaw_for_business 提供）
- Node.js >= 18（wenyan-formatter 使用 `npx`，需要 Node.js 环境）

## 测试

参见���目根目录的 [tests/README.md](../tests/README.md) 了解浏览器反检测测试用例。

## 开源致谢

本 addon 集成或依赖以下开源项目：

- [Patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright) — Playwright 的反检测 fork，Apache-2.0
- [文颜（Wenyan）](https://github.com/caol64/wenyan) — 多平台 Markdown 排版工具，Apache-2.0
  `wenyan-formatter` 技能通过调用 `@wenyan-md/cli`（[wenyan-cli](https://github.com/caol64/wenyan-cli)）实现 Markdown 渲染与公众号发布能力。
