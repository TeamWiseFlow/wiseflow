# AI首席情报官（Wiseflow）

**[English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md)**

🚀 **使用大模型从海量信息、各类信源中每日挖掘你真正感兴趣的信息！**

我们缺的不是信息，而是从海量信息中过滤噪音，从而让有价值的信息显露出来

## 🔥🔥🔥 Wiseflow 4.0 版本正式发布！

https://github.com/user-attachments/assets/de7d802f-8bd0-496a-86a9-80da25264f94

（在线服务目前因为技术原因，尚未切换到4.0核心，我们正在加速升级中）

在长达三个月的等待后，我们终于迎来了 wiseflow 4.0 版本的正式发布！

该版本带来了全新的4.x 架构，引入了对社交媒体信源的支持，并带来了诸多新特性。

🌟 4.x 内置 WIS Crawler（基于 Crawl4ai，MediaCrawler 和 Nodriver 深度重构整合），已经可以完美支持网页和社交媒体，4.0 版本先行提供对微博和快手平台的支持，后续计划陆续新增的平台包括：
微信公众号、小红书、抖音、b站、知乎……

4.x 架构带来的其他新特性包括：

- 全新的架构，混合使用异步和线程池，大大提升处理效率（同时降低内存消耗）；
- 继承了 Crawl4ai 0.6.3 版本的 dispacher 能力，提供更精细的内存管理能力；
- 深度整合了 3.9 版本中的 Pre-Process 和 Crawl4ai 的 Markdown Generation流程， 规避了重复处理；
- 优化了对 RSS 信源的支持；
- 优化了代码仓文件结构，更加清晰且符合当代 python 项目规范；
- 改为使用 uv 进行依赖管理，并优化了 requirement.txt 文件；
- 优化了启动脚本（提供提供 windows 版本），真正做到"一键启动"；
- 优化配置与部署流程，后台程序不再依赖 pocketbase 服务，因此无需在 .env 中提供 pocketbase 的账密，也不限定 pocketbase 的版本。

## 🧐  'deep search' VS 'wide search'

我把 wiseflow 的产品定位称为"wide search", 这是相对于目前大火的"deep search"而言。

具体而言"deep search"是面向某一具体问题由 llm 自主动态规划搜索路径，持续探索不同页面，采集到足够的信息后给出答案或者产出报告等；但是有的时候，我们并不带着具体的问题进行搜索，也并不需要深入探索，只需要广泛的信息采集（比如行业情报搜集、对象背景信息搜集、客户信息采集等），这个时候广度明显更有意义。虽然使用"deep search"也能实现这个任务，但那是大炮打蚊子，低效率高成本，而 wiseflow 就是专为这种"wide search"场景打造的利器。

## ✋ What makes wiseflow different from other ai-powered crawlers?

- 全平台的获取能力，包括网页、社交媒体（目前提供对微博和快手平台的支持）、RSS 信源、搜索引擎等；
- 不仅是抓取，而是自动分析和过滤，且仅需 14b 参数量的大模型即可很好的工作；
- 面向普通用户（而非开发者），无需写代码，"开箱即用"；
- 持续迭代带来的高稳定性和高可用性，以及兼顾系统资源和速度的处理效率；
- （未来）通过 insight 模块提供挖掘隐藏在已获取信息之下的"暗信息"的能力

……… 同时期待感兴趣的开发者加入我们，共同打造人人可用的 AI 首席情报官！


## 🚀 快速开始

**只需三步即可开始使用！**

### 📋 下载项目源代码并安装 uv 和 pocketbase

- for MacOS/Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

- for Windows:

**windows 用户请提前下载 git bash 工具，并在 bash 中执行如下命令 [bash下载链接](https://git-scm.com/downloads/win)**

```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

🌟 上述操作会完成 uv 的安装，pocketbase 的安装请参考 [pocketbase docs](https://pocketbase.io/docs/)

也可以尝试使用 install_pocketbase.sh (for MacOS/Linux) 或 install_pocketbase.ps1 (for Windows) 来安装。

### 📥 参考 env_sample 配置 .env 文件

在 wiseflow 文件夹（项目根目录）参考 env_sample 创建 .env 文件，并填入相关设定信息

### 🚀 起飞！

- for MacOS/Linux:

```bash
cd wiseflow
./run.sh
```

（注意：可能需要先执行 `chmod +x run.sh` 赋予执行权限）

- for Windows:

```bash
cd wiseflow
.\run.ps1
```

（注意：可能需要先执行 `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` 赋予执行权限）

如果遇到无法启动虚拟浏览器的问题，可以执行如下命令：

```bash
python -m playwright install --with-deps chromium
```

详细使用教程请参考 [docs/manual.md](./docs/manual.md)

## 📚 如何在您自己的程序中使用 wiseflow 抓取出的数据

wiseflow 所有抓取数据都会即时存入 pocketbase，因此您可以直接操作 pocketbase 数据库来获取数据。

PocketBase作为流行的轻量级数据库，目前已有 Go/Javascript/Python 等语言的SDK。  

在线服务也即将推出 sync api，支持将在线抓取结果同步本地，用于构建"动态知识库"等，敬请关注：

  - 在线体验地址：https://www.aiqingbaoguan.com/ 
  - 在线服务 API 使用案例：https://github.com/TeamWiseFlow/wiseflow_plus


## 🛡️ 许可协议

本项目基于 [Apache2.0](LICENSE) 开源。

商用合作，请联系 **Email：zm.zhao@foxmail.com**

- 商用客户请联系我们报备登记，开源版本承诺永远免费。

## 📬 联系方式

有任何问题或建议，欢迎通过 [issue](https://github.com/TeamWiseFlow/wiseflow/issues) 留言。

## 🤝 本项目基于如下优秀的开源项目：

- Crawl4ai（Open-source LLM Friendly Web Crawler & Scraper） https://github.com/unclecode/crawl4ai
- MediaCrawler（xhs/dy/wb/ks/bilibili/zhihu crawler） https://github.com/NanmiCoder/MediaCrawler
- NoDriver（Providing a blazing fast framework for web automation, webscraping, bots and any other creative ideas...） https://github.com/ultrafunkamsterdam/nodriver
- Pocketbase（Open Source realtime backend in 1 file） https://github.com/pocketbase/pocketbase
- Feedparser（Parse feeds in Python） https://github.com/kurtmckee/feedparser

本项目开发受 [GNE](https://github.com/GeneralNewsExtractor/GeneralNewsExtractor)、[AutoCrawler](https://github.com/kingname/AutoCrawler) 、[SeeAct](https://github.com/OSU-NLP-Group/SeeAct) 启发。

## Citation

如果您在相关工作中参考或引用了本项目的部分或全部，请注明如下信息：

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```
