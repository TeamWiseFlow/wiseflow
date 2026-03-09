# Wiseflow Addon for OpenClaw

浏览器反检测 + Tab Recovery + Smart Search + RSS Reader。

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
- **信源可自定义**：用户可以自由指定搜索源，精准匹配自己的信息需求

### 4. Browser Guide 技能

教会 agent 处理登录墙、验证码、懒加载、付费墙等场景的最佳实践。

### 5. RSS Reader 技能

支持读取 RSS/Atom Feed，可订阅任意支持标准 feed 格式的内容源。

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
├── addon.json                    # 元数据
├── overrides.sh                  # pnpm overrides: playwright-core → patchright-core + 禁用内置 web_search
├── patches/
│   ├── 001-browser-tab-recovery.patch        # 标签页恢复补丁
│   └── 002-disable-web-search-env-var.patch  # 禁用内置 web_search（env var）
├── skills/
│   ├── browser-guide/SKILL.md    # 浏览器使用最佳实践
│   ├── smart-search/SKILL.md     # 多平台搜索 URL 构造（替代内置 web_search）
│   └── rss-reader/               # RSS/Atom Feed 读取器
│       ├── SKILL.md
│       ├── package.json
│       └── scripts/fetch-rss.mjs
```

## 三层加载机制

addon 被 `apply-addons.sh` 加载时按以下顺序执行：

1. **overrides.sh** — 运行 pnpm overrides 替换 playwright-core 为 patchright-core，并禁用内置 web_search（最稳健，不依赖行号）
2. **patches/*.patch** — 应用 git patch（精确代码改动，上游更新时可能需调整）
3. **skills/*/SKILL.md** — 安装自定义技能到 openclaw

## 要求

- OpenClaw >= 2026.2
- pnpm（由 openclaw_for_business 提供）

## 测试

参见项目根目录的 [tests/README.md](../tests/README.md) 了解浏览器反检测测试用例。
