# AI首席情报官（Wiseflow）

**[English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/TeamWiseFlow/wiseflow)

🚀 **使用大模型从各类信源中每日追踪你最关注的信息！**

wiseflow 能够智能监控、追踪包括主流社交媒体、网站、RSS、搜索引擎在内的各类网络信源，并从中智能提取你最关注的信息

## 🎉  WiseFlow Pro 版本现已发布！

更强的抓取能力、更全面的社交媒体支持、含 UI 界面和免部署一键安装包！

https://github.com/user-attachments/assets/49b464fe-e9ea-472a-ba05-665230758a9c

🔥🔥 **Pro 版本现已面向全网发售**：https://shouxiqingbaoguan.com/ 

🔥 即日起为 wiseflow 开源版本贡献 PR（代码、文档、成功案例分享均欢迎），一经采纳，贡献者将获赠 wiseflow pro版本一年使用权（含相关 LLM 使用费用）！

## Wiseflow 4.2 开源版本

4.2版本在4.0、4.1版本基础上重点强化了网页抓取能力，现在程序可以直接调用您本地“真正”的 Chrome 浏览器进行获取。这不仅最大化降低了被目标站点“风控”的概率，而且还带来了可以持久化用户数据、支持页面操作脚本等新特性！（比如部分网站需要用户登录后才能展示完整内容，您现在可以预先登录，然后再使用 wiseflow 获取完整内容）。

因为4.2版本直接使用您本地的 Chrome 浏览器进行抓取，所以现在部署时无需执行 `python -m playwright install --with-deps chromium` 了，但需要**按默认安装路径安装 google chrome 浏览器**

除此之外，我们还重构了搜索引擎方案，以及提供了完备的 proxy 方案。具体见 **[CHANGELOG](CHANGELOG.md)**

### 🔍 自定义搜索源

4.1版本支持为关注点精准配置搜索源，目前支持 bing、github 和 arxiv三个搜索源，且均使用平台原生接口，无需额外申请第三方服务。

<img src="docs/select_search_source.gif" alt="search_source" width="360">

### 🧠 让 AI 站在你的立场上思考！

4.1版本支持为 focuspoint 设定角色和目的，从而指导 LLM 以特定视角或目的进行分析和提取。但使用时请注意：

    - 如果关注点本身指向性很具体，那么角色和目的的设定对结果影响不大；
    - 影响最终结果质量的第一要素永远是信源，一定要提供与关注点高度相关的信源。

有关角色和目的设定对提取结果影响的测评案例，请参考 [task1](test/reports/report_v4x_llm/task1)

### ⚙️ 自定义提取模式

现在你可以在 pb 界面下创建自己的表单，并配置给特定的关注点，LLM 将按照表单字段进行精准提取。

### 👥 社交平台信源支持创作者查找模式

现在可以指定程序按关注点在社交平台上查找相关内容，并进一步查找内容的创作者主页信息。结合"自定义提取模式"，wiseflow可以帮助你在全网搜索潜在客户、合作伙伴或者投资人的联系方式。

<img src="docs/find_person_by_wiseflow.png" alt="find_person_by_wiseflow" width="720">

## 🌹 最佳 LLM 搭配指南

“在 LLM 时代，优秀的开发者应该把至少60%的时间花在选择合适的 LLM 模型上” ☺️

我们精选了7套来自真实项目的测试样本，并广泛选择了主流的且输出价格不超过 ￥4/M tokens 的模型，进行了详细的wiseflow info extracting任务测试, 得出了如下使用推荐：

    - 性能优先场景下，推荐使用：ByteDance-Seed/Seed-OSS-36B-Instruct

    - 成本优先场景下，依然推荐使用：Qwen/Qwen3-14B

视觉辅助分析模型，依然可以使用：/Qwen/Qwen2.5-VL-7B-Instruct （wiseflow 任务目前对此的依赖不高）

详细的测试报告，可见 [LLM USE TEST](./test/reports/README.md)

需要说明的是，以上测试结果仅代表模型在 wiseflow 信息提取任务上的表现，不能代表模型的综合能力和全面能力。wiseflow 信息提取任务与其他类型任务（如规划、写作等）可能存在明显不同，另外成本是我们重点考虑的因素之一，因为 wiseflow 任务对模型的使用量消耗会比较大，尤其是在多信源、多关注点情况下。

wiseflow 不限定模型服务提供商，只要兼容 openaiSDK 请求接口格式即可。您可以选择已有的 Maas 服务或者 Ollama 等本地部署模型服务。

对于中国大陆区域用户，我们推荐使用 Siliconflow 的模型服务

🌹 欢迎使用我的 [推荐链接](https://cloud.siliconflow.cn/i/WNLYbBpi) 申请，你我都会获赠￥14平台奖励

另外，如果您对 openai 系列模型更加青睐的话，'o3-mini' 和 'openai/gpt-oss-20b' 也是不错的选择，视觉辅助分析可以搭配 gpt-4o-mini。

💰 目前在 wiseflow 应用内可以官方价格的九折使用由 AiHubMix 转发的 openai 系列模型官方接口。

**注意：** 享受优惠需要切换至 aihubmix 分支，详见 [README](https://github.com/TeamWiseFlow/wiseflow/blob/aihubmix/README.md)

## 🧐  与 “ChatGPTs” /“Deepseeks”/ “豆包” 等的区别

首先，wiseflow 与这些产品一样，背后都是 llm，也就是“大模型”，但是因为被设计的用途不一样，所以在如下两类场景中，使用“ChatGPTs” /“Deepseeks”/ “豆包” 这些可能并不能满足需求（大概率，现阶段为满足这类需求，你也找不到比 wiseflow 更适合的产品 ☺️）

你需要获取指定信源最新（数小时内发布）的内容，且你不想遗漏任何你可能感兴趣的部分

举例而言，比如对权威机构政策发布的跟踪、行业情报或者科技情报的跟踪、竞争对手的动态跟踪或者你只想从有限的高质量信源获取信息（摆脱推荐算法的控制🤣）等……“ChatGPTs” /“Deepseeks”/ “豆包” 等通用问答智能体并不会对指定信源做监控，他们的作用类似搜索引擎，面向的是全网信息，且通常只能获取2-3天或更长时延的“二手信息”。

你需要重复性的从网络（尤其是社交媒体）中发现并提取指定信息

举例而言，从社交媒体中找寻特定领域的潜在客户、供应商或者投资人，采集他们的联系方式等……同样“ChatGPTs” /“Deepseeks”/ “豆包” 等通用问答智能体更擅长的是总结并提炼答案，而不是搜集并整理信息。

## ✋ 与“爬虫”或 RPA 的区别

首先，wiseflow 并不是爬虫，也不是传统意义上的 RPA！

wiseflow 使用您使用的浏览器代替您以真实人类行为进行操作（当然，这依靠 LLM，甚至视觉 LLM）。在这个过程中不存在任何不合规行为，对于所有登录和验证操作 wiseflow 只会提醒用户，而不会越俎代庖，当然，这些操作在有效期内您只需执行一次，wiseflow会保留登录态（但不是保留用户名和密码，事实上，wiseflow 完全无法读取您输入的任何用户名和密码，您的任何操作都是在真实的官方页面上进行的）。

正因为 wiseflow 使用真实浏览器（而不是无头浏览器、虚拟浏览器等），并完全模拟用户真实浏览行为，因此它具有比“爬虫”和 RPA 更强的反侦测能力，除此之外，它还具有如下特性：

- 全平台采集能力：支持网站、RSS、微博、快手、Bing、GitHub、arXiv、eBay 等，Pro 版额外支持微信公众号、小红书、知乎、B站、抖音。
- 创新的 HTML 智能解析机制：可自动识别关键信息与可延伸探索的链接。
- “爬查一体”策略：在爬取过程中实时由 LLM 判断与提取，仅抓取相关信息，大幅降低风控风险。
- 真正开箱即用：无需 Xpath、脚本或人工配置，普通用户也能轻松使用。
- 完全无需担心 LLM 使用费用：所有 LLM 调用费用已包含在订阅中，无需另行配置服务或密钥。

## 🌟 快速开始

**只需三步即可开始使用！**

**4.2版本起，必须先安装 google chrome 浏览器（使用默认安装路径）**

**windows 用户请提前下载 git bash 工具，并在 bash 中执行如下命令 [bash下载链接](https://git-scm.com/downloads/win)**

### 📋 下载项目源代码并安装 uv 和 pocketbase

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

上述操作会完成 uv 的安装。

接下来去 [pocketbase docs](https://pocketbase.io/docs/) 下载对应自己系统的 pocketbase 程序放置于 [.pb](./pb/) 文件夹下

也可以尝试使用 install_pocketbase.sh (for MacOS/Linux) 或 install_pocketbase.ps1 (for Windows) 来安装。

### 📥 参考 env_sample 配置 .env 文件

在 wiseflow 文件夹（项目根目录）参考 env_sample 创建 .env 文件，并填入相关设定信息。

4.x 版本无需用户在.env 中提供 pocketbase 的账密，也不限定 pocketbase 的版本, 同时我们也暂时取消了 Secondary Model 的设定, 因此你其实最少仅需四个参数即可完成配置：

- LLM_API_KEY="" # LLM 服务的 key （任何提供 OpenAI 格式 API 的模型服务商均可，本地使用 ollama 部署则无需设置）
- LLM_API_BASE="https://api.siliconflow.cn/v1" # LLM 服务接口地址（推荐使用siliconflow服务, 欢迎使用我的 [推荐链接](https://cloud.siliconflow.cn/i/WNLYbBpi) 申请，你我都会获赠￥14平台奖励）
- PRIMARY_MODEL=ByteDance-Seed/Seed-OSS-36B-Instruct # 价格敏感且提取不复杂的场景可以使用 Qwen3-14B
- VL_MODEL=Pro/Qwen/Qwen2.5-VL-7B-Instruct

### 🚀  起飞！

```bash
cd wiseflow
uv venv # 仅第一次执行需要
source .venv/bin/activate  # Linux/macOS
# 或者在 Windows 上：
# .venv\Scripts\activate
uv sync # 仅第一次执行需要
chmod +x run.sh # 仅第一次执行需要
./run.sh  # Linux/macOS
.\run.bat  # Windows
```

详细使用教程请参考 [docs/manual/manual.md](./docs/manual/manual.md)

## 📚 如何在您自己的程序中使用 wiseflow 抓取出的数据

wiseflow 所有抓取数据都会即时存入 pocketbase，因此您可以直接操作 pocketbase 数据库来获取数据。

PocketBase作为流行的轻量级数据库，目前已有 Go/Javascript/Python 等语言的SDK。

另外 Pro 版本自带api，更加便于二次开发和集成至已有系统。

不管是基于 wiseflow 还是基于 wiseflow-pro，我们都欢迎在如下 repo 中分享并推广您的应用案例！

- https://github.com/TeamWiseFlow/wiseflow-plus

(在此 repo 中贡献 PR， 采纳后也一样会获赠 wiseflow-pro 一年使用权)

## 🛡️ 许可协议

自4.2版本起，我们更新了开源许可协议，敬请查阅： [LICENSE](LICENSE) 

商用合作，请联系 **Email：zm.zhao@foxmail.com**

## 📬 联系方式

有任何问题或建议，欢迎通过 [issue](https://github.com/TeamWiseFlow/wiseflow/issues) 留言。

## 🤝 本项目基于如下优秀的开源项目：

- Crawl4ai（Open-source LLM Friendly Web Crawler & Scraper） https://github.com/unclecode/crawl4ai
- Patchright(Undetected Python version of the Playwright testing and automation library) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- MediaCrawler（xhs/dy/wb/ks/bilibili/zhihu crawler） https://github.com/NanmiCoder/MediaCrawler
- NoDriver（Providing a blazing fast framework for web automation, webscraping, bots and any other creative ideas...） https://github.com/ultrafunkamsterdam/nodriver
- Pocketbase（Open Source realtime backend in 1 file） https://github.com/pocketbase/pocketbase
- Feedparser（Parse feeds in Python） https://github.com/kurtmckee/feedparser
- SearXNG（a free internet metasearch engine which aggregates results from various search services and databases） https://github.com/searxng/searxng

## Citation

如果您在相关工作中参考或引用了本项目的部分或全部，请注明如下信息：

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## 友情链接

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)