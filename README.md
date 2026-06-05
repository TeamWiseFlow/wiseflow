# Wiseflow

🚀 **v5.5.0 更新**

- **从安装到出活，全程微信对话完成**：首次部署时自动安装官方微信插件，扫码绑定后，Wiseflow Main Agent 直接在微信上引导你完成业务背景采集、团队组建、渠道配置——不再需要编辑任何配置文件。
- 如果只是想要一个个人助理、或者使用场景比较简单（crew 数量不超过 3 个），可以一直使用微信渠道，无需额外申请飞书开放平台或企业微信（后续如需扩展，Main Agent 也会给出申请和开通的详细指导）
- **Designer 升级**：从"出图工具"重新定位为**系统性视觉设计体系构建者**，内置 `design-system-picker` 技能，预置 15 套品牌设计系统（覆盖 fintech / devtools / productivity / consumer / luxury / enterprise 等全品类），一键匹配风格后从零构建完整网页、APP 界面、品牌视觉体系
- **IT Engineer 升级**：新增SEO、ICP备案辅助、云服务资源管理能力，现在 Designer + IT Engineer 的技能组合可覆盖官网 / Landing Page 的完整流程——**设计 → 开发 → 部署（云计算）→ 备案（ICP）→ SEO**
- **Selfmedia Operator 增强**：新增微信公众号文章自动排版并推送至草稿箱、简单短视频制作（t2video）、高光时刻视频剪辑（highlight-clipper），现已支持 15 个国内外主流自媒体平台的发布能力（部分为pro版本提供）
- **商务拓展 + 投资人关系正式发布**：business-developer 继承 4.x 全部核心能力（指定信源监控、行业情报采集、社交媒体潜客挖掘），并新增业务介绍 PPT 制作能力；investor-relationship 预发布

详见 [CHANGELOG.md](CHANGELOG.md)

---

## what's wiseflow

Wiseflow 是基于 [openclaw](https://github.com/openclaw/openclaw) 的 Multi-Agent 系统，为 **所有被/或即将为 AI 时代冲击、需要独立拓展收入来源的个体** 打造——被裁员/降薪的职场人、副业探索者、自媒体个体户、小生意人、刚毕业的年轻人……

> **对于 99% 的人来说，人工智能技术带来的其实是灾难**
>
> 这不是危言耸听。历史上每一次技术变革——蒸汽机、电力、互联网——无一例外都让会用它的人赚得更多，不会用的人被甩得更远。因为技术本质上是杠杆：有资本、有资源的人能第一时间装备自己，效率翻倍；而普通人连反应的时间都没有，就已经被替代了。AI 时代只会把这个规律放大到极致——99% 的输家，1% 的赢家。这非常不公平、也不合理。然而遗憾的是，这场变革已经无法被停止，那么，我们能做点什么？
>
> 本项目的立意是**为普通人提供一支AI搞钱团队**，以对抗AI技术发展带来的日益严峻的贫富差距。我们号召整个开源社区与我们一起为普通人而战，用技术对抗权贵！

我们不贩卖焦虑，也不承诺捷径。挣钱的本质从来是提供价值——你干了那么多年的事、攒下的经验、对某个领域的判断，那才是真有价值的。问题是：一个人有经验、有方法，但时间和精力终究有限。

wiseflow 目前能为你提供的是：
- AI自动化获客：**商务拓展** 挖客户 → **自媒体运营** 铺声量 → **销售客服** 促转化 → **HRBP** 调策略 → **IT Engineer** 保运行
- 业务支撑与保障：**设计师** 搭官网/落地页 → **IT Engineer** 搞 ICP 备案、服务器管理、SEO 优化

<img width="960" src="assets/crews.png" />

> 📌 **寻找 4.x 版本？** 原版 v4.32 及之前版本的代码在 [`4.x` 分支](https://github.com/TeamWiseFlow/wiseflow/tree/4.x)中。

---

## 🌟 快速开始

### 0. 准备 API Key

1. 注册 [DeepSeek 官方 API](https://platform.deepseek.com/) 并充值（前期试水，充个 10 块钱够了），获得 `DEEPSEEK_API_KEY`
2. 注册 [SiliconFlow](https://cloud.siliconflow.cn/i/WNLYbBpi)（🎁 欢迎使用我的邀请链接，你我均会获得 16 元代金券），获得 `SILICONFLOW_API_KEY`

> 如果习惯使用 ChatGPT / Gemini / Claude 等海外模型见下方[模型费用说明](#-模型费用说明)中的 AiHubMix 备选方案。

### 1. 获取代码

至 [Releases](https://github.com/TeamWiseFlow/wiseflow/releases) 下载最新版压缩包并解压；

### 2. 一键安装

```bash
cd wiseflow
./scripts/install.sh
```

`install.sh` 会自动完成：
- 拉取最新代码
- 初始化 `openclaw.json`（内置最佳模型配置，无需手动编辑）
- 安装系统 daemon（开机自启 + 崩溃重启）
- **交互式引导你输入** `DEEPSEEK_API_KEY` 和 `SILICONFLOW_API_KEY`（仅在首次或缺失时询问）
- 安装腾讯官方 `openclaw-weixin` extension，并引导扫码绑定

> **调试模式**（单次启动，适合测试）：`./scripts/dev.sh gateway`

> **系统要求**：推荐 Ubuntu 22.04；支持 WSL2 / macOS；不建议 Windows 原生

### 3. 微信对话完成 Onboard

安装完成后，打开微信搜索上一步绑定的机器人，直接发消息即可——它会主动引导你完成首次 onboard**：

1. 告诉它你的公司/品牌、产品和目标用户
2. 它会把这些业务背景存入 `business-context/`，后续招募的 crew 自动继承
3. 按需招募第一个 crew（如商务拓展、自媒体运营）
4. 团队扩大后，一条对话即可配置飞书或企业微信工作 channel

**不需要编辑配置文件、不需要手动同步信息——从安装到出活，全程对话完成。**

注：微信官方 openclaw 插件限定一个微信账号只能对应一个机器人，如果您之前已经绑定了其他 Agent（openclaw 或者 hermes 等），这会挤掉已经绑定的 agent。但是在完成 wiseflow 团队配置后，您可以将此 bot 替换回其他 agent，这不影响已经绑定工作渠道的 wiseflow crew team。

> 💡 更详细的操作指引见 [quick start](docs/quick_start.md)

### 系统与环境要求

| 项目 | 最低要求 | 推荐配置 |
|------|---------|---------|
| CPU | 2 核 | 4 核 |
| 内存 | 8 GB | 16 GB |
| 可用硬盘 | 40 GB | 120 GB |
| 带宽 | 10 Mbps | — |

- **网络**：需可访问外网；建议使用正常住宅 IP，数据中心 IP 部分平台可能识别限制
- **部署环境**：支持无头云服务器（ECS）部署，但推荐在有桌面环境的电脑上部署（日常使用中可不插显示器），浏览器自动化类技能在桌面环境下更稳定
- **操作系统**：推荐 Ubuntu 24.04；支持 Windows WSL2、macOS 15 / 26

> **💡 模型费用说明**
>
> wiseflow5.x 底层基于 openclaw，Agent 工作流对 token 消耗有一定要求，建议先准备好大模型 API：
>
> - **主力模型（强烈推荐）**：[DeepSeek 官方 API](https://platform.deepseek.com/) — 综合性能、速度、性价比最优。高缓存命中机制，实际应用成本可控。需要注册并充值获得 `DEEPSEEK_API_KEY`。
> - **替补 & 视觉模型**：[SiliconFlow](https://cloud.siliconflow.cn/i/WNLYbBpi) — 模型丰富，可作为 DeepSeek 的 fallback，同时提供视觉理解模型（`Qwen/Qwen3.6-27B`）和生图/生视频 API。需要注册获得 `SILICONFLOW_API_KEY`。
>   > 🎁 以上 SiliconFlow 链接为 wiseflow 邀请链接，通过此链接注册，你和 wiseflow 项目各可获得一张 16 元代金券。
>
> - **海外模型用户**：如果想使用 ChatGPT / Gemini / Claude 等海外模型，可通过 [AiHubMix](https://aihubmix.com/?aff=Gp54) 统一接入（全兼容 OpenAI 接口，国内直连）。欢迎通过此[邀请链接](https://aihubmix.com/?aff=Gp54)注册。备选配置模板见 `config-templates/openclaw-aihubmix.json`。
>
> 配置模板已预置以上最佳实践，`install.sh` 会自动检测所需环境变量并引导你输入。安装后重启 openclaw gateway 即可生效。

🎉 wiseflow 目前提供付费知识库，包含《手把手从零开始安装教程》、《安装之后三分钟上手指南》、《Openclaw自定义配置全案教程》、《Windows 下安装 WSL2 无脑教程》、《秘籍：云服务器（ECS）部署》以及各种最佳实践分享，年费仅需¥168，还能加入 **vip微信交流群** ，共同探讨交流各种玩法，还有每月一次的闭门分享（腾讯会议），陪伴你从“小白“到“大神“！

欢迎添加”掌柜的“企业微信（这背后接的就是 wiseflow sales-cs）咨询了解：

<img width="360" height="360" alt="wiseflow掌柜" src="https://github.com/user-attachments/assets/b013b3fd-546e-4176-b418-57bee419e761" />

🌹 开源不易，感谢支持！

## ✨ 创新点

Wiseflow 在 openclaw 基础上以addon、配置模板、专属技能等方式（不改上游一行代码，保证完全兼容性）做了如下改进：

#### “Crew”的概念

原版 OpenClaw 定位是 **personal AI assistant**——个人助理。但个人助理和工作场景是很不一样的：工作场景的技能不要求丰富，但要求稳定、专业；不同的工作要对应不同的定义约束和技能组合，即不同岗位需要使用不同的 harness。

Wiseflow 的做法是提供 `Crew Template`，针对每个岗位提供专属 skill 和工作指导，并留给用户充分的调教空间。

目前 wiseflow 内置如下 crew，可以按需启用：

| Crew | 职责 | 关键技能 |
|------|------|---------|
| Main Agent（微信上的那个，默认启用，全局唯一） | 管理所有 crew 生命周期，唯一对话入口 | crew 招募/管理、渠道配置 |
| IT Engineer（默认启用，全局唯一，可协助其他 crew 排障） | 系统运维、配置、故障排查 | seo、icp-filing、icp-exemption、tccli、alicloud-find-skills、session-logs |
| HRBP | 招募管理对外 crew，周期扫描 feedback 升级 | crew-recruit、crew-modify、crew-remove、crew-list、crew-usage |
| 商务拓展 | 客户挖掘端 | 社交媒体潜客挖掘、竞品监控、行业情报、生成业务介绍 PPT |
| 自媒体运营 | 内容生产端 | 写稿、生图、15 个平台自动发布、t2video（短视频）、highlight-clipper（高光剪辑） |
| 设计师 | 视觉设计端 | 15 套品牌设计系统、完整网页/APP/品牌视觉体系构建 |
| 销售型客服 | 获客转化端 | 自动回复促进成交、调研用户来源、记录客户信息、发起/确认收款 |
| 投资人关系 | 融资端 | 寻找投资人、冷接触、填报申请表、生成 BP |
| Video Producer* | 专业视频端 | 专业短视频制作 |

> *\* 标记的 crew 由 Pro 版本提供*

  <details>
  <summary><strong>自媒体运营 — 支持的社交媒体平台（15 个）</strong></summary>

  | 平台 | 发布方式 |
  |------|---------|
  | 微信公众号 | API + wenyan-cli 渲染 |
  | 企业微信朋友圈* | API |
  | 小红书* | API |
  | 抖音 | API（OAuth2） |
  | B站* | Web API |
  | 快手* | Web API |
  | 今日头条 | 浏览器 + CDP |
  | 掘金 | 浏览器 |
  | Twitter/X | 浏览器 |
  | YouTube | YouTube Data API v3 |
  | TikTok | Content Posting API |
  | Instagram | Meta Graph API |
  | Facebook | Meta Graph API |
  | Threads | Meta Graph API |
  | Pinterest | Pinterest API v5 |

  > *\* 标记的平台发布技能由 Pro 版本提供，开源版不包含*

  </details>

有关”多 crew 机制”设计，详见[CREW TYPE DESIGN](docs/crew-system.md)

#### Crew 之间的自主协作
  
我们巧妙的利用了 OpenClaw 的 Spawn Subagent 机制实现了 crew 之间的自主协作能力，这意味着：

Crew 遇到自己不能解决的问题：
  ```text
  1. ❌ 不会停止工作
  2. ❌ 不会喊用户帮忙 （这很傻，不是吗？）
  3. ✅ 自主调用合适的 subagent 协助
  4. ✅ 问题解决后继续原任务
  ```

工作流程：

  假设新媒体运营 crew 正在处理内容发布任务，突然遇到 API 调用失败：
  ```text
  [media-operator] 正在发布文章到微信公众号...
  [media-operator] 发现错误：access_token expired
  [media-operator] 判断：这是技术问题，调用 IT Engineer
    └── [it-engineer] 收到协助请求：access_token 过期
    └── [it-engineer] 分析原因：token 刷新机制异常
    └── [it-engineer] 执行修复：重新配置 token 刷新
    └── [it-engineer] 返回结果：问题已解决
  [media-operator] 收到解决方案，继续发布文章
  [media-operator] 任务完成
  ```
  用户视角：整个过程用户无感知，Agent 自主完成了问题排查和修复。
  
示例：
  
1. 目前 wiseflow 已经默认配置 `it-engineer` 为所有对内 crew 可 spawn，这令我们可以不必为一个任务分别找不同的 crew以及在任务执行过程中遇到问题，crew 也会自动唤起 it-engineer 进行协查：
  
<img width="960" src="assets/crews_co_work.png" />

#### 可用性增强

原版openclaw的使用和维护并不简单，尤其对于非技术用户而言，充满暗坑，最受诟病的是**安全性**和**安装部署**，为此我们也做了不少改进：

##### 安全

我们采用三重命令执行机制，**权限由 `exec-approvals.json` + `tools.exec` 自动强制执行**，不单单是角色定义中告知。

**层级概览**

| Tier | 名称 | 执行策略 | 适用 Crew |
|------|------|----------|-----------|
| T0 | read-only | `security: deny` — 默认禁止所有 shell 命令 | external crews（默认） |
| T1 | basic-shell | `security: allowlist` — 仅允许只读命令 | low-risk internal crews |
| T2 | dev-tools | `security: allowlist` — 开发工具链 + 只读命令 | main, hrbp，selfmedia-operator... |
| T3 | admin | `security: full` — 完整系统操作 | it-engineer |

##### 易用性脚本

- **配置模板** — 预设国内可用的模型、渠道、技能等配置
- **工具脚本** — 一键启动、一键部署、一键更新…… 

##### wiseflow 内置补丁与可配置环境变量

wiseflow 通过 `patches/` 目录对 openclaw 源码打补丁，每次运行 `apply-addons.sh` 时自动应用。以下是当前生效的补丁及其可配置项：

| 补丁 | 说明 | 相关环境变量 |
|------|------|-------------|
| `001-relax-exec-allowlist-shell-syntax` | 放宽 exec-approvals 的 shell 语法限制，允许 `$()`、反引号、重定向等常用写法 | 无 |
| `002-disable-web-search-env-var` | 支持通过环境变量禁用 openclaw 内置 web search | `OPENCLAW_DISABLE_WEB_SEARCH=1` |
| `003-act-field-validation` | 修复浏览器 act 动作的字段验证逻辑 | 无 |
| `004-chrome-port-grace-retry` | Chrome CDP 端口占用时优雅重试，避免因端口冲突导致浏览器启动失败 | 无 |
| `005-browser-timeout-env-var` | 支持通过环境变量自定义浏览器操作默认超时（原默认仅 20 秒，网络慢时容易中断） | `OPENCLAW_BROWSER_TIMEOUT_MS=60000` （执行 install.sh 脚本会自动配置）|

#### 浏览器增强

**🌍 反检测浏览器，且无需安装浏览器插件**

wiseflow 将 openclaw 内置的 Playwright 替换为 [Patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright)（Playwright 的反检测 fork），显著降低自动化浏览器被目标网站识别和拦截的概率。

> 我们综合考察了目前市面上流行的各浏览器自动化框架，包括 nodriver、browser-use、vercel 的 agent-browser等，目前可以确认的是虽然基本原理都是通过走 cdp 并提供持久化 openclaw 专用的 profile，但是只有 patchright 提供了完全的针对 CDP 探针的移除，换言之，即便是用最纯粹的 cdp 直连方案，也是带有特征的，即也是可以被检测到的。其他框架的定位是自动化测试目的，而非获取目的，而 patchright 本身就定位于获取，并且它本质上是 playwright 的 patch，继承了几乎全部的 playwright 上层 api，这就天然与 openclaw 兼容，不必额外安装任何插件或者mcp

我们认为反侦测能力是为了实现“在线搞钱“目的的一个基础能力，比如 `selfmedia-operator` 能够实现自动去各个平台发帖、回帖就完全基于此项改进。

**🔍 Smart Search（智能搜索） Skill**

替代 openclaw 内置的 `web_search`，提供更强大的搜索能力。相比原版内置的 web search tool，Smart Search 具备三大核心优势：

- **完全免费，无需 API Key**：不依赖任何第三方搜索 API，零成本使用
- **即时搜索，时效性最佳**：直接驱动浏览器前往目标页面或各大社交媒体平台（微博、Twitter/X、facebook 等）进行搜索，第一时间获取最新发布的内容
- **信源可自定义**：用户可以自由指定搜索源，精准匹配自己的信息需求

https://github.com/user-attachments/assets/8d097b3b-f9ab-42eb-98bb-88af5d28b089

#### 可私有化部署的私密信道 —— awada

通过 awada，你可以完全私有化部署自己的 channel，或者是对接第三方消息中转站，实现接入企微 bot 等能力。

详见 [awada readme](awada/README.md)

## 目录结构

```
wiseflow/
├── openclaw/              # 上游仓库（git clone，禁止直接修改）
├── crews/                 # 内置 Crew 模板（全局唯一，不可删除）
│   ├── shared/            # 共享协议（RULES.md、TEMPLATES.md）
│   ├── _template/         # 空白脚手架（创建新模板的起点）
│   ├── index.md           # 模板注册表（HRBP 维护）
│   ├── main/              # [built-in] Main Agent（路由调度器）
│   ├── hrbp/              # [built-in] HRBP（Crew 生命周期管理）
│   │   └── skills/        # HRBP 专属技能（recruit/modify/remove/list/usage）
│   └── it-engineer/       # [built-in] IT Engineer（系统运维 + SEO 技术优化）
│       └── skills/        # IT Engineer 专属技能（seo、session-logs 等）
├── skills/                # wiseflow 默认全局技能（smart-search / browser-guide / complex-task 等）
├── patches/               # wiseflow 基础补丁（对所有 addon 生效）
│   ├── *.patch            # git 补丁（按序号顺序应用到 openclaw/）
│   └── overrides.sh       # pnpm 依赖覆盖（如替换 playwright → patchright）
├── addons/                # addon 安装目录
│   ├── officials/         # [official] wiseflow 官方 addon
│   │   ├── skills/        # 官方 addon 提供的额外全局技能（rss-reader / siliconflow-* 等）
│   │   └── crew/          # 官方 Crew 模板
│   │       ├── sales-cs/          # 销售型客服
│   │       ├── selfmedia-operator/# 自媒体运营
│   │       ├── designer/          # 设计师
│   │       └── business-developer/# 商务拓展
│   └── ...                # 用户可以自行安装的第三方 addon
├── config-templates/      # 配置模板（开箱即用的最佳实践）
│   └── openclaw.json      # 默认配置模板
├── scripts/               # 工具脚本（详见 scripts/README.md）
│   ├── lib/               # 脚本共享工具
│   ├── install.sh         # 一键安装 / 升级（推荐入口）
│   ├── apply-addons.sh    # 应用补丁 + 全局技能 + addon + build + restart
│   ├── dev.sh             # 开发模式启动（前台运行 gateway）
│   ├── setup-crew.sh      # 多 crew 系统安装（仅同步 markdown，幂等）
│   └── setup-wsl2.sh      # WSL2 环境配置
└── docs/                  # 项目文档
```

运行时数据使用上游默认位置 `~/.openclaw/`。

🌹 即日起为 wiseflow 开源版本贡献 PR（代码、文档、成功案例分享均欢迎），一经采纳，贡献者将获赠 wiseflow pro版本一年使用权！

## 🛡️ 许可协议

自4.2版本起，我们更新了开源许可协议，敬请查阅： [LICENSE](LICENSE) 

## 📬 联系方式

有任何问题或建议，欢迎通过 [issue](https://github.com/TeamWiseFlow/wiseflow/issues) 留言。

商务合作专属邮箱：`zm.zhao # foxmail.com` (发送时将 # 替换为 @)

## 🤝 wiseflow5.x 基于如下优秀的开源项目：

- openclaw(Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞) https://github.com/openclaw/openclaw
- Patchright(Undetected Python version of the Playwright testing and automation library) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- Feedparser（Parse feeds in Python） https://github.com/kurtmckee/feedparser
- SearXNG（a free internet metasearch engine which aggregates results from various search services and databases） https://github.com/searxng/searxng
- opencli（A CLI for social media & web platforms — smart-search skill 借鉴了其搜索 URL 模式与平台适配方案） https://github.com/jackwener/opencli
- 文颜(Markdown文章排版美化工具，支持微信公众号、今日头条、知乎等平台。) https://github.com/caol64/wenyan
- Everything Claude Code（Claude Code 全局 skill / rule / agent 集合，wiseflow 的 complex-task 等编排 skill 借鉴了其 blueprint 和 gan-style-harness 的设计思路） https://github.com/affaan-m/everything-claude-code
- awesome-design-md（A curated collection of design systems in markdown format — Designer 内置设计系统库参考了此项目的设计系统结构） https://github.com/VoltAgent/awesome-design-md

## Citation

如果您在相关工作中参考或引用了本项目的部分或全部，请注明如下信息：

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

![star](https://atomgit.com/wiseflow/wiseflow/star/badge.svg) 国内托管地址：[https://atomgit.com/wiseflow/wiseflow](https://atomgit.com/wiseflow/wiseflow)

## 友情链接

[<img src="https://github.com/TeamWiseFlow/wiseflow/raw/4.x/docs/logos/tianqibao.png" alt="tianqibao" height="60">](https://baotianqi.cn/)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[<img src="https://resource.aihubmix.com/logo.png" alt="aihubmix" height="60">](https://aihubmix.com/?aff=Gp54)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[<img src="https://github.com/TeamWiseFlow/wiseflow/raw/4.x/docs/logos/SiliconFlow.png" alt="siliconflow" height="40">](https://cloud.siliconflow.cn/i/WNLYbBpi)
