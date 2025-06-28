# AI首席情报官（Wiseflow）

**[English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

🚀 **使用大模型从海量信息、各类信源中每日挖掘你真正感兴趣的信息！**

我们缺的不是信息，而是从海量信息中过滤噪音，从而让有价值的信息显露出来

https://github.com/user-attachments/assets/2c52c010-6ae7-47f4-bc1c-5880c4bd76f3

## 🔥🔥🔥 Wiseflow 4.1 版本正式发布！

### 让 AI 站在你的立场上思考！

正如对同一事件，不同角色、不同目的下其视角也会不同一样，在对信源进行关注点提取时，如能提供角色和目的信息，将有助于模型以用户角度进行更加精准的提取。

如下图所示，针对同一篇微博博文，在关注点设定相同情况下，左侧为不额外设定角色和目的的提取结果，右侧为额外设定角色为“行业供应商”，目的为“跟踪品牌竞争动向”的提取结果。

可以明显看到，左侧提取结果偏向于一般性的事实总结，而在加入角色和目的设定后，右侧的输出结果明显发生了变化。

<img src="docs/focus_4I50_compare.jpg" alt="focus 4150 compare" width="720">


再如下图，同样的信源和关注点，左侧设定角色为“个人投资者”，右侧设定角色为”媒体记者“，可见仅仅是设定角色不同，模型提取的侧重点也会不同。

<img src="docs/focus_gold_compare.jpg" alt="focus gold compare" width="720">

**注意：**

- 如果关注点本身指向性很具体，那么角色和目的的设定对结果影响不大；
- 影响最终结果质量的第一要素永远是信源，一定要提供与关注点高度相关的信源。

有关关注点和角色设定对最终结果影响更加详细的案例，请参考 [task1](test/reports/report_v4x_llm/task1)

### 自定义精准提取

## 🧐  'deep search' VS 'wide search'

我把 wiseflow 的产品定位称为"wide search", 这是相对于目前大火的"deep search"而言。

具体而言"deep search"是面向某一具体问题由 llm 自主动态规划搜索路径，持续探索不同页面，采集到足够的信息后给出答案或者产出报告等；但是有的时候，我们并不带着具体的问题进行搜索，也并不需要深入探索，只需要广泛的信息采集（比如行业情报搜集、对象背景信息搜集、客户信息采集等），这个时候广度明显更有意义。虽然使用"deep search"也能实现这个任务，但那是大炮打蚊子，低效率高成本，而 wiseflow 就是专为这种"wide search"场景打造的利器。

## ✋ What makes wiseflow different from other ai-powered crawlers?

- 全平台的获取能力，包括网页、社交媒体（目前提供对微博和快手平台的支持）、RSS 信源、搜索引擎等；
- 独特的 html 处理流程，自动按关注点提取信息并发现值得进一步探索的链接，且仅需 14b 参数量的大模型即可很好的工作；
- 面向普通用户（而非开发者），无需人工介入提供 Xpath 等，"开箱即用"；
- 持续迭代带来的高稳定性和高可用性，以及兼顾系统资源和速度的处理效率；
- 将不仅仅是“爬虫”……

<img src="docs/wiseflow4.xscope.png" alt="4.x full scope" width="720">

(4.x 架构整体规划图。虚线框内为尚未完成的部分，希望有能力的社区开发者加入我们，贡献 PR。 所有contributor都将免费获赠 pro 版本的使用权！)

## 🌟 快速开始

**只需三步即可开始使用！**

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
- LLM_API_BASE="https://api.siliconflow.cn/v1" # LLM 服务接口地址
- JINA_API_KEY="" # 搜索引擎服务的 key （推荐 Jina，个人使用甚至无需注册即可申请）
- PRIMARY_MODEL=Qwen/Qwen3-14B # 推荐 Qwen3-14B 或同量级思考模型
- VL_MODEL=Pro/Qwen/Qwen2.5-VL-7B-Instruct # better to have

### 🚀  起飞！

```bash
cd wiseflow
uv venv # 仅第一次执行需要
source .venv/bin/activate  # Linux/macOS
# 或者在 Windows 上：
# .venv\Scripts\activate
uv sync # 仅第一次执行需要
python -m playwright install --with-deps chromium # 仅第一次执行需要
chmod +x run.sh # 仅第一次执行需要
./run.sh
```

详细使用教程请参考 [docs/manual/manual.md](./docs/manual/manual.md)

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
- SearXNG（a free internet metasearch engine which aggregates results from various search services and databases） https://github.com/searxng/searxng

## Citation

如果您在相关工作中参考或引用了本项目的部分或全部，请注明如下信息：

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```

## 友情链接

[<img src="docs/logo/siliconflow.png" alt="siliconflow" width="360">](https://siliconflow.cn/)