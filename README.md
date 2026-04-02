# Wiseflow

🚀 **STEP INTO 5.x**

> 📌 **寻找 4.x 版本？** 原版 v4.32 及之前版本的代码在 [`4.x` 分支](https://github.com/TeamWiseFlow/wiseflow/tree/4.x)中。

```
“吾生也有涯，而知也无涯。以有涯随无涯，殆已！“ —— 《庄子·内篇·养生主第三》
```

## what's wiseflow

wiseflow 是基于 [openclaw](https://github.com/openclaw/openclaw) 的一套旨在面向真实营业场景的Multi-Agent（多智能体）系统（MAS），支持部署后对外提供 7*24 营业业务，内置自动化网络推广与销售型客服 Agent.

*wiseflow 又名 openclaw_for_business，简称 ofb*

> openclaw很强，能够帮你收发邮件、写报告、控制智能家居……但是讲真，这是你最需要的吗？
>
> 让 AI 帮我们 “搞钱”才是王道！
>
> **本项目的目的不是为你增加一个“个人助理”，而是为你打造一直“云上牛马”团队，可以 7*24 小时给你在线搞钱的那种！**

## 🌟 快速开始

1. 至本代码仓的 [Releases](https://github.com/TeamWiseFlow/wiseflow/releases) 下载最新版代码压缩包，解压缩到任意位置

或

```bash
git clone https://github.com/TeamWiseFlow/wiseflow.git
cd wiseflow
git clone https://github.com/openclaw/openclaw.git
cd ..
```

2. 进入解压缩后的代码目录，根据需求选择启动方式：

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
> - **不建议**直接在 Windows（原生）下运行

3. 打开 `~\.openclaw\openclaw.json` 输入你的大模型服务端点地址和 api key 

🎉 大功告成！

注意：

- dev.sh 或者 reinstall-daemon.sh 脚本会自动初始化一个最佳配置的openclaw.json，基础使用几乎不用改；
- wiseflow 不改 openclaw 的原始代码，release 包中内置的 openclaw 由 CI/CD 程序自动从官方 github 代码仓抓取，请放心使用。

4. 安装后如何用可以参考 [quick start](docs/quick_start.md)

> **💡 模型费用说明**
>
> wiseflow5.x 底层基于 openclaw，Agent 工作流对 token 消耗有一定要求，建议先准备好大模型 API：
>
> - **国内用户（推荐）**：[硅基流动（SiliconFlow）](https://cloud.siliconflow.cn/i/WNLYbBpi) — 注册并实名认证可领取免费全平台模型代金券，覆盖上手阶段所需费用（配置模板中已预置 siliconflow.cn 的最佳实践，可直接使用）。😄 欢迎使用我的[推荐链接](https://cloud.siliconflow.cn/i/WNLYbBpi)注册，你我都会获赠 ¥16 平台奖励
> - **OpenAI / 海外闭源模型**：推荐 [AiHubMix](https://aihubmix.com?aff=Gp54) — 国内直连无障碍。😄 欢迎使用我的[邀请链接](https://aihubmix.com?aff=Gp54)注册
> - **海外用户**：可直接使用 SiliconFlow 国际版：https://www.siliconflow.com/
安装后重启 openclaw_for_business 即可生效。

🎉 wiseflow 目前提供付费知识库，包含《手把手从零开始安装教程》、《Openclaw自定义配置全案教程》、《Windows 下安装 WSL2 无脑教程》以及各种高阶独门秘籍等，年费仅需¥168，还能加入 **vip微信交流群**

欢迎添加”掌柜的“企业微信（这背后接的就是 wiseflow）咨询了解：

<img width="360" height="360" alt="wiseflow掌柜" src="https://github.com/user-attachments/assets/b013b3fd-546e-4176-b418-57bee419e761" />

🌹 开源不易，感谢支持！

## ✨ 创新点

原版 openclaw，包括国内各大厂推出的基于 openclaw 的“虾”，它们的定位都是“个人助理”（personal AI assistant），也即适合服务你自己，但并不适合替你服务别人，因此也就没办法替你搞钱。

wiseflow 专为打造可在线 7*24 小时搞钱的目的而生，我们在原版的基础上以补丁、配置模板、专属技能等方式（但不改原版一行代码，以保证完全的兼容性）做了如下改进：

#### “Crew”的概念

- Crew 是绑定了专属工作指导和技能组合的Agent

> 原版openclaw是把所有技能（包括内置和用户自定义安装的）绑定到同一个 Agent 上，Agent Spawn 出的 subagent 也默认继承所有技能。但这会造成两个问题：1、臃肿，代表着每一轮对话都更加耗费 token、模型思考时间也会更长并且更容易出错；2、如果 Agent 是提供对外服务的，那么会很危险，想象外部客户可以通过 Agent 操控你家的的智能家居或者连通你的打印机……当然你可以通过原版的配置禁用这些技能，然而为什么要让一个，比如说客服 Agent 拥有连接智能家居和打印机的技能？

wiseflow 的做法是提供 `Crew Template`，针对每个 crew 的应用目的（客服、新媒体运营、财务报税）提供专属的 skill（很多是我们定制开发的）和基础的工作指导、人设，并留给用户充分的“调教”空间。

wiseflow 的 Crew 分为两大类：`对内`和`对外`.

- `对内crew` 负责服务你和其他 crew，相当于公司的中后台。这里面有三个是内置且全局唯一的，负责提供最基础的支撑，相当于公司的管理层：
  - Main Agent，负责管理所有对内 crew 的生命周期，你也可以把它当成唯一对话入口，通过它喊其他 Crew 干活；
  - IT Engineer，负责帮你搞定 openclaw 繁琐的配置，日常运维（升级、定时心跳检查状态）等，**对，你没看错，只要你完成第一次部署，后面它就可以帮你去做系统配置和运维**
  - HRBP，负责帮你招募、管理对外服务 crew，还能帮你周期性质的扫描对外服务 crew 的 feedback，不断升级他们……

  以上三个内置 crew 我们都已经提供了现成的最佳配置（角色定义文件、SKills、权限等）

- `对外crew` 负责服务外部客户，是帮你“搞钱”的。
  - 你可以通过 HRBP 创建并招募符合你自己业务要求的对外 crew；
  - 目前我们已经随代码仓提供了两个对外 crew 模板：`sales customer service` （销售导向客服） `selfmedia operator` (新媒体运营)
    - `sales customer service` 不是一个单纯回答客户咨询的客服，它以促进成交为目的，会在咨询答疑过程中以用户无感的巧妙话术促进销售、调研用户来源、记录客户信息，并具有发起收款和确认收款的能力；
    - `selfmedia operator` 不仅仅能够帮你写稿、生图（那些你用豆包、千问、DeepSeek 也能做），它能够随时记录你的灵感，你无意中看到的素材也可以随手转发给它，它都会记住并应用在后续产出中，并且它还能**自动完成在各个自媒体平台发布**的工作
  - 更多能够帮你在线搞钱的 crew template 陆续发布中……

> 说实话，市面上有很多基于 openclaw 的二开项目都支持多 crew（Agent），甚至还支持让这些 crew（Agent） 自主协同，或者带个办公室界面，你能看到他们在一起“过家家”……我认为这些都太华而不实了! 如果不能搞钱，一个 Agent Team 跟一个 chatbot 一样，只是玩具而已！

有关“多 crew 机制”设计，详见[CREW TYPE DESIGN](docs/crew-system.md)

#### Crew 之间的自主协作
  
我们巧妙的利用了 OpenClaw 的 Spawn Subagent 机制实现了 crew 之间的自主互助能力，这意味着：

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

- **安全**

我们采用三重命令执行机制，**权限由 `exec-approvals.json` + `tools.exec` 自动强制执行**，不单单是角色定义中告知。

**层级概览**

| Tier | 名称 | 执行策略 | 适用 Crew |
|------|------|----------|-----------|
| T0 | read-only | `security: deny` — 默认禁止所有 shell 命令 | external crews（默认） |
| T1 | basic-shell | `security: allowlist` — 仅允许只读命令 | low-risk internal crews |
| T2 | dev-tools | `security: allowlist` — 开发工具链 + 只读命令 | main |
| T3 | admin | `security: full` — 完整系统操作 | it-engineer, hrbp |

**易用性脚本**

- **配置模板** — 预设国内可用的模型、渠道、技能等配置
- **工具脚本** — 一键启动、一键部署、一键更新…… 

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

#### Addon 机制与生态（marketplace）

wiseflow 不改上游（openclaw）代码，一切改造和增强都通过 `addon` 机制完成，这最大化的保障了兼容性，也即是说：wiseflow 无缝支持**从 clawhub.ai安装技能**。

wiseflow 代码仓会不会更新、添加 [official addons](addons/officials), 我们也欢迎社区贡献更多 addon，第三方也可以通过 add-on 向 wiseflow 用户发放 crew template，参见 [Addon 开发](docs/addon_development.md)。

同时，我们也已规划了 Add-on Marketplace, 预计将于 2026.4 月上线，不同于 openclaw clawhub，这是一个专门提供搞钱技能和能搞钱的 crew template的市场，敬请期待！

## 目录结构

```
wiseflow/
├── openclaw/              # 上游仓库（git clone，禁止直接修改）
├── crews/                 # Crew 模板库 + 内置 Crew（Template → Instance 模型）
│   ├── shared/            # 共享协议（RULES.md、TEMPLATES.md）
│   ├── _template/         # 空白脚手架（创建新模板的起点）
│   ├── index.md           # 模板注册表（HRBP 维护）
│   ├── main/              # [built-in] Main Agent（路由调度器）
│   ├── hrbp/              # [built-in] HRBP（Crew 生命周期管理）
│   │   └── skills/        # HRBP 专属技能（recruit/modify/remove/list/usage）
│   ├── it-engineer/       # [built-in] IT Engineer（系统运维）
│   ├── sales-cs/          # [official] 销售型客服crew模板
│   ├── selfmedia-operator/# [official] 自媒体运营crew模板
│   ├── ...                # [official] 不断增加的crew模板
│   └── _template/         # 空白脚手架（创建新 Crew 模板的起点）
├── skills/                # 全局共享技能（所有 Agent 可见）
├── addons/                # addon 安装目录
│   ├── officials/         # [official] wiseflow 官方 addon
│   ├── ...                # 用户可以自行安装的第三方 addon
├── config-templates/      # 配置模板（开箱即用的最佳实践）
│   └── openclaw.json      # 默认配置模板
├── scripts/               # 工具脚本
│   ├── libs/              # 脚本共享工具
│   ├── dev.sh             # 开发模式启动（自动安装 crew 系统 + addon）
│   ├── setup-crew.sh      # 多 crew 系统安装（幂等）
│   ├── apply-addons.sh    # 全局 skills + addon 加载器
│   ├── upgrade.sh         # 一键升级脚本（推荐入口）
│   ├── reinstall-daemon.sh # 生产模式安装后台服务
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

## Citation

如果您在相关工作中参考或引用了本项目的部分或全部，请注明如下信息：

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## 友情链接

[<img src="https://github.com/TeamWiseFlow/wiseflow/raw/4.x/docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://cloud.siliconflow.cn/i/WNLYbBpi)
