# AI首席情报官（Wiseflow）

**[English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/TeamWiseFlow/wiseflow)

🚀 **从指定信源中持续提取你需要的信息**

支持主流自媒体平台、支持需要预登录的站点、使用真实浏览器，定时监控、持续追踪、大模型自动提取

## 🎉  WiseFlow Pro 版本现已发布！

更强的抓取能力、更全面的社交媒体支持、含 UI 界面和免部署一键安装包！

https://github.com/user-attachments/assets/57f8569c-e20a-4564-a669-1200d56c5725

🔥🔥 **Pro 版本现已面向全网发售**：https://shouxiqingbaoguan.com/ 

🌹 即日起为 wiseflow 开源版本贡献 PR（代码、文档、成功案例分享均欢迎），一经采纳，贡献者将获赠 wiseflow pro版本一年使用权！

另外如果你想“零折腾、零成本”快速看下 wiseflow pro 的信息获取能力，欢迎参与我们的“情报小站”计划，你可以至：https://yqeupxazxi.feishu.cn/wiki/OROrwv54biwThBkbghpcxOEsnZe 感兴趣的“情报小站”微信群，我们使用 wiseflow pro 根据每个情报小站的主题每日抓取最新资讯。

如果你有合作建设特定领域的“情报小站”的想法，也欢迎与我们联系！

## Wiseflow 开源版本

自4.30版本开始，wiseflow 开源版本现已升级为与 pro 版本一样的架构，同时具有一样的 api，可无缝共享 [wiseflow+](https://github.com/TeamWiseFlow/wiseflow-plus) 生态！

## wiseflow 开源版本与 pro 版本的对比

| 功能特性 | 开源版 | Pro 版 |
| :--- | :---: | :---: |
| **监控信源支持** | web、rss | web、rss，额外七大主流中文自媒体平台 |
| **搜索源支持** | bing、github、arxiv | bing、github、arxiv，额外六大主流中文自媒体平台 |
| **安装部署** | 需手动安装环境与部署 | 免安装部署，一键运行 |
| **用户界面** | 无用户界面 | 中文 web UI 界面|
| **LLM 费用** | 用户自行订阅 LLM 服务或者自行搭建本地 LLM 服务 | 订阅已包含 LLM 调用费用 (无需额外配置) |
| **技术支持** | GitHub Issues | 付费用户微信群 |
| **价格** | 免费 | ￥488/年 |
| **适用群体** | 社区探索与项目学习 | 日常使用（个人 or 企业） |

## 🧐 wiseflow 产品定位

wiseflow 并不是类似 ChatGPT 或者 Manus 那样的通用智能体，它专注于信息监控与提取，支持用户指定信源，且以定时任务模式保证时刻获取最新信息（最大获取频率支持每天 4 次，也就是每 6 小时获取一次）。同时 wiseflow 支持从指定平台中进行全面的信息查找（比如“找人”）。

但也不要把 wiseflow 等同于传统意义上的爬虫或者RPA！ wiseflow 的获取行为完全由 LLM 驱动，使用真实浏览器（而不是无头浏览器、虚拟浏览器等）进行，且它的获取与提取动作是同时进行的：

- 创新的 HTML 智能解析机制：可自动识别关键信息与可延伸探索的链接。
- “爬查一体”策略：在爬取过程中实时由 LLM 判断与提取，仅抓取相关信息，大幅降低风控风险。
- 真正开箱即用：无需 Xpath、脚本或人工配置，普通用户也能轻松使用。

    ……

更多请参考：https://shouxiqingbaoguan.com/

## 🌟 快速开始

**只需三步即可开始使用！**

**4.2版本起，必须先安装 google chrome 浏览器（使用默认安装路径）**

**windows 用户请提前下载 git bash 工具，并在 bash 中执行如下命令 [bash下载链接](https://git-scm.com/downloads/win)**

### 📋 安装环境管理工具 uv 并下载 wiseflow 源代码

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

上述操作会完成 uv 的安装并下载 wiseflow 源代码。

### 📥 参考 env_sample 配置 .env 文件

在 wiseflow 文件夹（项目根目录）参考 env_sample 创建 .env 文件，并填入相关设定信息（主要是 llm 服务的配置）。

**wiseflow 开源版本需要用户自行配置 llm 服务**

wiseflow 不限定模型服务提供商，只要兼容 openaiSDK 请求接口格式即可。您可以选择已有的 Maas 服务或者 Ollama 等本地部署模型服务。

对于中国大陆区域用户，我们推荐使用 Siliconflow 的模型服务

😄 欢迎使用我的 [推荐链接](https://cloud.siliconflow.cn/i/WNLYbBpi) 申请，你我都会获赠￥14平台奖励

如果你更倾向使用 openai 等海外闭源模型，可以使用 AiHubMix 的模型服务，国内直连无障碍：

😄 欢迎使用我的 [AiHubMix邀请链接](https://aihubmix.com?aff=Gp54) 注册

海外用户可以使用 siliconflow 海外版：https://www.siliconflow.com/

### 🚀  起飞！

```bash
cd wiseflow
uv venv # 仅第一次执行需要
source .venv/bin/activate  # Linux/macOS
# 或者在 Windows 上：
# .venv\Scripts\activate
uv sync # 仅第一次执行需要
python core/entry.py
```

## 📚 如何在您自己的程序中使用 wiseflow 抓取出的数据

可参考 [wiseflow backend api](./core/backend/README.md)

不管是基于 wiseflow 还是基于 wiseflow-pro，我们都欢迎在如下 repo 中分享并推广您的应用案例！

- https://github.com/TeamWiseFlow/wiseflow-plus

(在此 repo 中贡献 PR， 采纳后也一样会获赠 wiseflow-pro 一年使用权)

**4.2x 版本架构与 4.30 并不完全兼容，4.2x 的最终版本（v4.29）已停止维护，如需代码参考，可以切换到“2025”分支。**

## 🛡️ 许可协议

自4.2版本起，我们更新了开源许可协议，敬请查阅： [LICENSE](LICENSE) 

商用合作，请联系 **Email：zm.zhao@foxmail.com**

## 📬 联系方式

有任何问题或建议，欢迎通过 [issue](https://github.com/TeamWiseFlow/wiseflow/issues) 留言。

有关 pro 版本的需求或合作反馈，欢迎联系 AI首席情报官“掌柜”企业微信：

<img src="docs/wechat.jpg" alt="wechat" width="360">

## 🤝 本项目基于如下优秀的开源项目：

- Crawl4ai（Open-source LLM Friendly Web Crawler & Scraper） https://github.com/unclecode/crawl4ai
- Patchright(Undetected Python version of the Playwright testing and automation library) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- MediaCrawler（xhs/dy/wb/ks/bilibili/zhihu crawler） https://github.com/NanmiCoder/MediaCrawler
- NoDriver（Providing a blazing fast framework for web automation, webscraping, bots and any other creative ideas...） https://github.com/ultrafunkamsterdam/nodriver
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
