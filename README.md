# Wiseflow

**[English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

🚀 **STEP INTO 5.x**

> 📌 **寻找 4.x 版本？** 原版 v4.30 及之前版本的代码在 [`4.x` 分支](https://github.com/TeamWiseFlow/wiseflow/tree/4.x)中。

```
“吾生也有涯，而知也无涯。以有涯随无涯，殆已！“ —— 《庄子·内篇·养生主第三》
```

wiseflow 4.x(包括之前的版本) 通过一系列精密的 workflow 实现了在特定场景下的强大的获取能力，但依然存在诸多局限性：

- 1. 无法获取交互式内容（需要经过点选才能出现的内容，尤其是动态加载的情况）
- 2. 只能进行信息过滤与提取，几乎没有任何下游任务能力
- ……

虽然我们一直致力于完善它的功能、扩增它的边界，但真实世界是复杂的，真实的互联网也一样，规则永无可能穷尽，因此固定的 workflow 永远做不到适配所有场景，这不是 wiseflow 的问题，这是传统软件的问题！

然而过去一年 Agent 的突飞猛进，让我们看到了由大模型驱动完全模拟人类互联网行为在技术上的可能，[openclaw](https://github.com/openclaw/openclaw) 的出现更让我们坚定了此信念。

更奇妙的是，通过前期的实验和探索，我们发现将 wiseflow 的获取能力以”插件“形式融入 openclaw，即可以完美解决上面提到的两个局限性。我们接下来会陆续放出激动人心的真实 demo 视频，同时开源发布这些”插件“。

不过需要说明的是，openclaw 的 plugin 系统与传统上我们理解的“插件”（类似 claude code 的 plugin）并不相同，因此我们不得不额外提出了“add-on"的概念，所以确切的说，wiseflow5.x 将以 openclaw add-on 的形态出现。原版的 openclaw 并不具有”add-on“架构，不过实际上，你只需要几条简单的 shell 命令即可完成这个”改造“。我们也准备了开箱即用、同时包含一系列针对真实商用场景预设配置的 openclaw 强化版本，即 [openclaw_for_business](https://github.com/TeamWiseFlow/openclaw_for_business), 你可以直接 clone ，并将 wiseflow release 解压缩放置于 openclaw_for_business 的 add-on 文件夹内即可。

## ✨ 主要功能

wiseflow add-on 目前为 openclaw 提供以下四项核心增益：

### 1. 反检测浏览器

将 openclaw 内置的 Playwright 替换为 [Patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright)（Playwright 的反检测 fork），显著降低自动化浏览器被目标网站识别和拦截的概率。从而实现不需要安装 chrome relay extension，只用托管浏览器也能达到与 relay 同样、甚至更优的网络获取与操作能力。

### 2. 标签页自动恢复

当 Agent 操作过程中目标标签页意外关闭或消失时，自动进行快照级别的标签页恢复，确保任务不会因标签页丢失而中断。

### 3. Smart Search（智能搜索）

替代 openclaw 内置的 `web_search`，提供更强大的搜索能力。相比原版内置的 web search tool，Smart Search 具备三大核心优势：

- **完全免费，无需 API Key**：不依赖任何第三方搜索 API，零成本使用
- **即时搜索，时效性最佳**：直接驱动浏览器前往目标页面或各大社交媒体平台（微博、Twitter/X、facebook 等）进行搜索，第一时间获取最新发布的内容
- **信源可自定义**：用户可以自由指定搜索源，精准匹配自己的信息需求

### 4. 新媒体小编 Crew（预设 AI Agent）

开箱即用的中文自媒体内容创作 AI Agent，深耕微博、小红书、知乎、B 站、抖音等国内主流平台。

**主要能力：**

- 选题研究 + 热点分析（Mode A）
- 草稿扩写 + 网络佐证（Mode B）
- 文章定稿后自动调用 [文颜（Wenyan）](https://github.com/caol64/wenyan) 渲染为公众号风格 HTML，支持 7 套内置主题智能匹配
- 可直接推送微信公众号草稿箱（Mode C，需配置 `WECHAT_APP_ID`/`WECHAT_APP_SECRET`）
- 支持 AI 文生图（[SiliconFlow](https://siliconflow.com/) 图片/视频生成，需配置 `SILICONFLOW_API_KEY`）

## 🌟 快速开始

直接从本代码仓的 [Releases](https://github.com/TeamWiseFlow/wiseflow/releases) 下载包含了 openclaw_for_business 和 wiseflow addon 的整合压缩包。

1. 下载压缩包并解压缩
2. 进入解压缩后的文件夹
3. 根据需求选择启动方式：

   **调试模式**（单次启动，适合测试和开发）：
   ```bash
   ./scripts/dev.sh gateway
   ```

   **生产模式**（安装为系统服务，适合长期运行）：
   ```bash
   ./scripts/reinstall-daemon.sh
   ```

> **系统要求**
> - 推荐使用 **Ubuntu 22.04** 系统
> - 支持 **Windows WSL2** 环境
> - 支持 **macOS**
> - **不支持**直接在 Windows（原生）下运行

### 【备用】手动方案

注意：你需要先下载部署 openclaw_for_business，下载地址为：https://github.com/TeamWiseFlow/openclaw_for_business/releases

复制代码仓内的 wiseflow 文件夹（注意不是代码仓本身）到 openclaw_for_business 的 `addons/` 目录：

```bash
# 方式一：从 wiseflow 仓库复制
git clone https://github.com/TeamWiseFlow/wiseflow.git /tmp/wiseflow
cp -r /tmp/wiseflow/wiseflow <openclaw_for_business>/addons/wiseflow
```

安装后重启 openclaw_for_business 即可生效。

## 目录结构

```
wiseflow/                         # addon 包（复制到 addons/ 目录使用）
├── addon.json                    # 元数据
├── overrides.sh                  # pnpm overrides + 禁用内置 web_search
├── patches/
│   ├���─ 001-browser-tab-recovery.patch        # 标签页恢复补丁
│   ├── 002-disable-web-search-env-var.patch  # 禁用内置 web_search（env var）
│   └── 003-act-field-validation.patch        # ACT 字段校验补丁
├── skills/                       # 全局技能（所有 Agent 可用）
│   ├── browser-guide/SKILL.md    # 浏览器最佳实践（登录/验证码/懒加载等）
│   ├── smart-search/SKILL.md     # 多平台搜索 URL 构造（替代内置 web_search）
│   └── rss-reader/               # RSS/Atom Feed 读取器
│       ├── SKILL.md
│       ├── package.json
│       └── scripts/fetch-rss.mjs
└── crew/                         # 预设 AI Agent（Crew 模板）
    └── new-media-editor/         # 新媒体小编（中文自媒体内容创作）
        ├── IDENTITY.md / SOUL.md / AGENTS.md / TOOLS.md / ...
        └── skills/               # Crew 专属技能
            ├── siliconflow-img-gen/   # 文生图（SiliconFlow API）
            ├── siliconflow-video-gen/ # 文生视频（SiliconFlow API）
            └── wenyan-formatter/      # Markdown → 公众号 HTML / 推送草稿

docs/                             # 技术文档（代码仓根目录）
├── anti-detection-research.md
└── more_powerful_search_skill/

scripts/                          # 工具脚本（代码仓根目录）
└── generate-patch.sh

tests/                            # 测试用例和脚本（代码仓根目录）
├── README.md
└── run-managed-tests.mjs
```

##  WiseFlow Pro 版本现已发布！

更强的抓取能力、更全面的社交媒体支持、含 UI 界面和免部署一键安装包！

https://github.com/user-attachments/assets/57f8569c-e20a-4564-a669-1200d56c5725

🔥 **Pro 版本现已面向全网发售**：https://shouxiqingbaoguan.com/ 

🌹 即日起为 wiseflow 开源版本贡献 PR（代码、文档、成功案例分享均欢迎），一经采纳，贡献者将获赠 wiseflow pro版本一年使用权！

📥  📚 🎉 


## 🛡️ 许可协议

自4.2版本起，我们更新了开源许可协议，敬请查阅： [LICENSE](LICENSE) 

商用合作，请联系 **Email：zm.zhao@foxmail.com**

## 📬 联系方式

有任何问题或建议，欢迎通过 [issue](https://github.com/TeamWiseFlow/wiseflow/issues) 留言。

有关 pro 版本的需求或合作反馈，欢迎联系 AI首席情报官“掌柜”企业微信：

<img src="docs/wechat.jpg" alt="wechat" width="360">

## 🤝 wiseflow5.x 基于如下优秀的开源项目：

- Patchright(Undetected Python version of the Playwright testing and automation library) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- Feedparser（Parse feeds in Python） https://github.com/kurtmckee/feedparser
- SearXNG（a free internet metasearch engine which aggregates results from various search services and databases） https://github.com/searxng/searxng
- 文颜（Wenyan）多平台 Markdown 排版与发布工具（新媒体小编 Crew 通过 wenyan-formatter 技能调用） https://github.com/caol64/wenyan

## Citation

如果您在相关工作中参考或引用了本项目的部分或全部，请注明如下信息：

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## 友情链接

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)
