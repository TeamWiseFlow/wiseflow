# AI首席情报官（Wiseflow）

**[English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md)**

🚀 **使用大模型从海量信息、各类信源中每日挖掘你真正感兴趣的信息！**

我们缺的不是信息，而是从海量信息中过滤噪音，从而让有价值的信息显露出来

🌱看看AI情报官是如何帮您节省时间，过滤无关信息，并整理关注要点的吧！🌱

https://github.com/user-attachments/assets/fc328977-2366-4271-9909-a89d9e34a07b


## 🔥🔥🔥 Qwen3 Series 兼容报告

4月30日，备受瞩目的Qwen3系列发布，我们赶在假期第一时间进行了测试。

我们主要测试了Qwen3-14B、Qwen3-30B-A3B，并和GLM-4-32B-0414、DeepSeek-R1-Distill-Qwen-14B进行了对比。之所以只选择参数量不超过32b 的模型，是因为 wiseflow 任务相对简单，更大的模型并不能带来显著的改善，但会极大的增加使用成本。（wiseflow 任务的特点是难度低，但是需要反复调用）。

最终的结论： **Qwen3-14B、Qwen3-30B-A3B 在开启 think mode 的情况下，非常值得推荐！**  详细的测试报告请见 [test/reports/wiseflow_report_v40_web/Qwen3_report_0502.md](./test/reports/wiseflow_report_v40_web/Qwen3_report_0502.md)

基于此测试（同时考虑生成速度和成本因素），在 wiseflow 的使用上，我们目前推荐使用 Qwen3-30B-A3B 作为 primary model，Qwen3-14B 作为 secondary model。

如果是本地部署且显存有限的情况，推荐只使用 Qwen3-14B ，可以选择8bit量化版本。

当然你也可以继续选择免费模型实现"零成本"使用，对此，我强烈推荐智谱平台的 glm-4-flash-250414。


## 🌟 过去两周新增 contributor

  - @zhudongwork PR #360 [replace re with regex library for better performance]
  - @beat4ocean PR #361 [update docker base image to improve for playwright]


## 🧐  'deep search' VS 'wide search'

我把 wiseflow 的产品定位称为"wide search", 这是相对于目前大火的"deep search"而言。

具体而言"deep search"是面向某一具体问题由 llm 自主动态规划搜索路径，持续探索不同页面，采集到足够的信息后给出答案或者产出报告等；但是有的时候，我们没有具体的问题，也并不需要深入探索，只需要广泛的信息采集（比如行业情报搜集、对象背景信息搜集、客户信息采集等），这个时候广度明显更有意义。虽然使用"deep search"也能实现这个任务，但那是大炮打蚊子，低效率高成本，而 wiseflow 就是专为这种"wide search"场景打造的利器。


## ✋ What makes wiseflow different from other ai-powered crawlers?

最大的不同是在 scraper 阶段，我们提出了一种与目前已有爬虫都不同的 pipeline，即"爬查一体"策略。具体而言，我们放弃了传统的 filter-extractor 流程（当然这个流程也可以融入 llm，正如 crawl4ai 那样），我们也不再把单一 page 当做最小处理单元。而是在 crawl4ai 的html2markdown 基础上，再进一步将页面分块，并根据一系列特征算法，把块分为"正文块"和"外链块"，并根据分类不同采用不同的llm提取策略（依然是每个块只用 llm 分析一次，只是分析策略不同，规避 token 浪费），这个方案可以同时兼容列表页、内容页以及混排页等情况。

  - 对于"正文块"，直接按关注点进行总结提取，避免信息分散，甚至在此过程中直接完成翻译等；
  - 对于"外链块"，综合页面布局等信息，判断哪些链接值得进一步探索，哪些直接忽略，因此无需用户手动配置深度、最大爬取数量等。

这个方案其实非常类似 AI Search。

另外我们也针对特定类型的页面编写了专门的解析模块，比如微信公众号文章（居然一共有九种格式……），针对这类内容，wiseflow 目前能够提供同类产品中最好的解析效果。

## ✋ What's Next (4.x plan)?

### Crawler fetching 阶段的增强
    
3.x 架构  crawler fetching 部分完全使用 Crawl4ai，4.x中普通页面的获取我们依然会使用这个方案，但是会逐步增加对于社交平台的 fetching 方案。


### Insight 模块
    
其实真正有价值的未必是"可以抓取到的信息"，而是隐藏在这些信息之下的"暗信息"。能够智能的关联已抓取信息，并分析提炼出隐藏其下的"暗信息"就是4.x要着重打造的 insight 模块。


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

如果遇到无法获取网页的问题，可以执行如下命令：

```bash
python -m playwright install --with-deps chromium
```

详细使用教程请参考 [docs/manual.md](./docs/manual.md)


## 📚 如何在您自己的程序中使用 wiseflow 抓取出的数据

1、参考 [dashbord](dashboard) 部分源码二次开发。

注意 wiseflow 的 core 部分并不需要 dashboard，目前产品也未集成 dashboard，如果您有dashboard需求，请下载 [V0.2.1版本](https://github.com/TeamWiseFlow/wiseflow/releases/tag/V0.2.1)

2、直接从 Pocketbase 中获取数据

wiseflow 所有抓取数据都会即时存入 pocketbase，因此您可以直接操作 pocketbase 数据库来获取数据。

PocketBase作为流行的轻量级数据库，目前已有 Go/Javascript/Python 等语言的SDK。
   - Go : https://pocketbase.io/docs/go-overview/
   - Javascript : https://pocketbase.io/docs/js-overview/
   - python : https://github.com/vaphes/pocketbase
  
3、在线服务也即将推出 sync api，支持将在线抓取结果同步本地，用于构建"动态知识库"等，敬请关注：

  - 在线体验地址：https://www.aiqingbaoguan.com/ 
  - 在线服务 API 使用案例：https://github.com/TeamWiseFlow/wiseflow_plus


## 🛡️ 许可协议

本项目基于 [Apache2.0](LICENSE) 开源。

商用合作，请联系 **Email：zm.zhao@foxmail.com**

- 商用客户请联系我们报备登记，开源版本承诺永远免费。


## 📬 联系方式

有任何问题或建议，欢迎通过 [issue](https://github.com/TeamWiseFlow/wiseflow/issues) 留言。


## 🤝 本项目基于如下优秀的开源项目：

- crawl4ai（Open-source LLM Friendly Web Crawler & Scraper） https://github.com/unclecode/crawl4ai
- MediaCrawler (xhs/dy/wb/ks/bilibili/zhihu crawler) https://github.com/NanmiCoder/MediaCrawler
- NoDriver (Providing a blazing fast framework for web automation, webscraping, bots and any other creative ideas...) https://github.com/ultrafunkamsterdam/nodriver
- pocketbase (Open Source realtime backend in 1 file) https://github.com/pocketbase/pocketbase
- feedparser (Parse feeds in Python) https://github.com/kurtmckee/feedparser

本项目开发受 [GNE](https://github.com/GeneralNewsExtractor/GeneralNewsExtractor)、[AutoCrawler](https://github.com/kingname/AutoCrawler) 、[SeeAct](https://github.com/OSU-NLP-Group/SeeAct) 启发。

## Citation

如果您在相关工作中参考或引用了本项目的部分或全部，请注明如下信息：

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```
