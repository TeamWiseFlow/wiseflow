# 首席情报官（Wiseflow）

**[English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md)**

🚀 **AI情报官**（Wiseflow）是一个敏捷的信息挖掘工具，可以从各种给定信源中依靠大模型的思考与分析能力精准抓取特定信息，全程无需人工参与。

**我们缺的不是信息，而是从海量信息中过滤噪音，从而让有价值的信息显露出来**

🌱看看AI情报官是如何帮您节省时间，过滤无关信息，并整理关注要点的吧！🌱

https://github.com/user-attachments/assets/fc328977-2366-4271-9909-a89d9e34a07b

## 🔥 V0.3.7 来了

本次升级带来了 wxbot 的整合方案，方便大家添加微信公众号作为信源，具体见 [weixin_mp/README.md](./weixin_mp/README.md)

我们也提供了专门针对微信公众号文章的提取器，同时也设计了自定义提取器接口，方便用户根据实际需求进行定制。

本次升级也进一步强化了信息提取能力，不仅极大优化了页面中链接的分析，还使得7b、14b 这种规模的模型也能比较好的完成基于复杂关注点（explanation中包含时间、指标限制这种）的提取。

另外本次升级还适配了 Crawl4ai 0.4.247 版本，以及做了诸多程序改进，具体见 [CHANGELOG.md](./CHANGELOG.md)

感谢如下社区贡献者在这一阶段的 PR：

  - @ourines 贡献了 install_pocketbase.sh 脚本 (docker运行方案被暂时移除了，感觉大家用起来也不是很方便……)
  - @ibaoger 贡献了 windows 下的pocketbase 安装脚本
  - @tusik 贡献了异步 llm wrapper

**V0.3.7版本再次引入SECONDARY_MODEL，这主要是为了降低使用成本**
  
### V0.3.7 测试报告

在最新的提取策略下，我们发现7b 这种规模的模型也能很好的执行链接分析与提取任务，测试结果请参考 [report](./test/reports/wiseflow_report_v037_bigbrother666/README.md)

不过信息总结任务目前还是推荐大家使用不低于 32b 规模的模型，具体推荐请参考最新的 [env_sample](./env_sample)

继续欢迎大家提交更多测试结果，共同探索 wiseflow 在各种信源下的最佳使用方案。

现阶段，**提交测试结果等同于提交项目代码**，同样会被接纳为contributor，甚至受邀参加商业化项目！具体请参考 [test/README.md](./test/README.md) 


🌟**V0.3.x 计划**

- ~~尝试支持微信公众号免wxbot订阅（V0.3.7）；【已完成】~~
- 引入对 RSS 信息源和搜索引擎的支持（V0.3.8）;
- 尝试部分支持社交平台（V0.3.9）。

## ✋ wiseflow 与传统的爬虫工具、AI搜索、知识库（RAG）项目有何不同？

wiseflow自2024年6月底发布 V0.3.0版本来受到了开源社区的广泛关注，甚至吸引了不少自媒体的主动报道，在此首先表示感谢！

但我们也注意到部分关注者对 wiseflow 的功能定位存在一些理解偏差，如下表格通过与传统爬虫工具、AI搜索、知识库（RAG）类项目的对比，代表了我们目前对于 wiseflow 产品最新定位思考。

|          | 与 **首席情报官（Wiseflow）** 的比较说明| 
|-------------|-----------------|
| **爬虫类工具** | 首先 wiseflow 是基于爬虫工具的项目，但传统的爬虫工具在信息提取方面需要人工的提供明确的 Xpath 等信息……这不仅阻挡了普通用户，同时也毫无通用性可言，对于不同网站（包括已有网站升级后）都需要人工重做分析，更新程序。wiseflow致力于使用 LLM 自动化网页的分析和提取工作，用户只要告诉程序他的关注点即可。 如果以 Crawl4ai 为例对比说明，Crawl4ai 是会使用 llm 进行信息提取的爬虫，而wiseflow 则是会使用爬虫工具的llm信息提取器。|
| **AI搜索** |  AI搜索主要的应用场景是**具体问题的即时问答**，举例：”XX公司的创始人是谁“、“xx品牌下的xx产品哪里有售” ，用户要的是**一个答案**；wiseflow主要的应用场景是**某一方面信息的持续采集**，比如XX公司的关联信息追踪，XX品牌市场行为的持续追踪……在这些场景下，用户能提供关注点（某公司、某品牌）、甚至能提供信源（站点 url 等），但无法提出具体搜索问题，用户要的是**一系列相关信息**| 
| **知识库（RAG）类项目** | 知识库（RAG）类项目一般是基于已有信息的下游任务，并且一般面向的是私有知识（比如企业内的操作手册、产品手册、政府部门的文件等）；wiseflow 目前并未整合下游任务，同时面向的是互联网上的公开信息，如果从“智能体”的角度来看，二者属于为不同目的而构建的智能体，RAG 类项目是“（内部）知识助理智能体”，而 wiseflow 则是“（外部）信息采集智能体”|

**wiseflow 0.4.x 版本将关注下游任务的集成， 引入 LLM 驱动的轻量级知识图谱，帮助用户从 infos 中建立洞察。**

## 📥 安装与使用

### 1. 克隆代码仓库

🌹 点赞、fork是好习惯 🌹

**windows 用户请提前下载 git bash 工具，并在 bash 中执行如下命令** [bash下载链接](https://git-scm.com/downloads/win)

```bash
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

### 2. 执行根目录下的 install_pocketbase 脚本

linux/macos 用户请执行 

```bash
chmod +x install_pocketbase
./install_pocketbase
```

**windows 用户请执行 [install_pocketbase.ps1](./install_pocketbase.ps1) 脚本**

wiseflow 0.3.x版本使用 pocketbase 作为数据库，你当然也可以手动下载 pocketbase 客户端 (记得下载0.23.4版本，并放入 [pb](./pb) 目录下) 以及手动完成superuser的创建(记得存入.env文件)

具体可以参考 [pb/README.md](/pb/README.md)

### 3. 继续配置 core/.env 文件

🌟 **这里与之前版本不同**，V0.3.5开始需要把 .env 放置在 [core](./core) 文件夹中。

#### 3.1 大模型相关配置

wiseflow 是 LLM 原生应用，请务必保证为程序提供稳定的 LLM 服务。

🌟 **wiseflow 并不限定模型服务提供来源，只要服务兼容 openAI SDK 即可，包括本地部署的 ollama、Xinference 等服务**

#### 推荐1：使用硅基流动（siliconflow）提供的 MaaS 服务

siliconflow（硅基流动）提供大部分主流开源模型的在线 MaaS 服务，凭借着自身的加速推理技术积累，其服务速度和价格方面都有很大优势。使用 siliconflow 的服务时，.env的配置可以参考如下：

```bash
export LLM_API_KEY=Your_API_KEY
export LLM_API_BASE="https://api.siliconflow.cn/v1"
export PRIMARY_MODEL="Qwen/Qwen2.5-32B-Instruct"
export SECONDARY_MODEL="Qwen/Qwen2.5-7B-Instruct"
export VL_MODEL="OpenGVLab/InternVL2-26B"
```
      
😄 如果您愿意，可以使用我的[siliconflow邀请链接](https://cloud.siliconflow.cn?referrer=clx6wrtca00045766ahvexw92)，这样我也可以获得更多token奖励 🌹

#### 推荐2：使用 AiHubMix 代理的openai、claude、gemini 等海外闭源商业模型服务

如果您的信源多为非中文页面，且也不要求提取出的 info 为中文，那么更推荐您使用 openai、claude、gemini 等海外闭源商业模型。您可以尝试第三方代理 **AiHubMix**，支持国内网络环境直连、支付宝便捷支付，免去封号风险。
使用 AiHubMix 的模型时，.env的配置可以参考如下：

```bash
export LLM_API_KEY=Your_API_KEY
export LLM_API_BASE="https://aihubmix.com/v1" # 具体参考 https://doc.aihubmix.com/
export PRIMARY_MODEL="gpt-4o"
export SECONDARY_MODEL="gpt-4o-mini"
export VL_MODEL="gpt-4o"
```

😄 欢迎使用 [AiHubMix邀请链接](https://aihubmix.com?aff=Gp54) 注册 🌹

#### 本地部署大模型服务

以 Xinference 为例，.env 配置可以参考如下：

```bash
# LLM_API_KEY='' 本地服务无需这一项，请注释掉或删除
export LLM_API_BASE='http://127.0.0.1:9997'
export PRIMARY_MODEL=启动的模型 ID
export VL_MODEL=启动的模型 ID
```

#### 3.2 pocketbase 账号密码配置

```bash
export PB_API_AUTH="test@example.com|1234567890" 
```

这里pocketbase 数据库的 superuser 用户名和密码，记得用 | 分隔 (如果 install_pocketbase.sh 脚本执行成功，这一项应该已经存在了)

#### 3.3 其他可选配置

下面的都是可选配置：
- #VERBOSE="true" 

  是否开启观测模式，开启的话会把 debug 信息记录在 logger 文件上（默认仅输出在 console 上）；

- #PROJECT_DIR="work_dir" 

    项目运行数据目录，不配置的话，默认在  `core/work_dir` ，注意：目前整个 core 目录是挂载到 container 下的，所以意味着你可以直接访问这里。

- #PB_API_BASE="" 

  只有当你的 pocketbase 不运行在默认ip 或端口下才需要配置，默认情况下忽略就行。

- #LLM_CONCURRENT_NUMBER=8 

  用于控制 llm 的并发请求数量，不设定默认是1（开启前请确保 llm provider 支持设定的并发，本地大模型慎用，除非你对自己的硬件基础有信心）
  
  感谢 @tusik 贡献的异步 llm wrapper

### 4. 运行程序

✋ V0.3.5版本架构和依赖与之前版本有较大不同，请务必重新拉取代码，删除（或重建）pb_data

推荐使用 conda 构建虚拟环境（当然你也可以忽略这一步，或者使用其他 python 虚拟环境方案）

```bash
conda create -n wiseflow python=3.10
conda activate wiseflow
```

之后运行

```bash
cd wiseflow
cd core
pip install -r requirements.txt
chmod +x run.sh
./run_task.sh # if you just want to scan sites one-time (no loop), use ./run.sh
```

🌟 这个脚本会自动判断 pocketbase 是否已经在运行，如果未运行，会自动拉起。但是请注意，当你 ctrl+c 或者 ctrl+z 终止进程时，pocketbase 进程不会被终止，直到你关闭terminal。

run_task.sh 会周期性执行爬取-提取任务（启动时会立即先执行一次，之后每隔一小时启动一次）, 如果仅需执行一次，可以使用 run.sh 脚本。

### 5. **关注点和定时扫描信源添加**
    
启动程序后，打开pocketbase Admin dashboard UI (http://127.0.0.1:8090/_/)
    
#### 5.1 打开 focus_point 表单

通过这个表单可以指定你的关注点，LLM会按此提炼、过滤并分类信息。
    
字段说明：
- focuspoint, 关注点描述（必填），如”上海小升初信息“、”加密货币价格“
- explanation，关注点的详细解释或具体约定，如 “仅限上海市官方发布的初中升学信息”、“BTC、ETH 的现价、涨跌幅数据“等
- activated, 是否激活。如果关闭则会忽略该关注点，关闭后可再次开启。

注意：focus_point 更新设定（包括 activated 调整）后，**需要重启程序才会生效。**

#### 5.2 打开 sites表单

通过这个表单可以指定自定义信源，系统会启动后台定时任务，在本地执行信源扫描、解析和分析。

sites 字段说明：
- url, 信源的url，信源无需给定具体文章页面，给文章列表页面即可。
- per_hours, 扫描频率，单位为小时，类型为整数（1~24范围，我们建议扫描频次不要超过一天一次，即设定为24）
- activated, 是否激活。如果关闭则会忽略该信源，关闭后可再次开启。

**sites 的设定调整，无需重启程序。**


## 📚 如何在您自己的程序中使用 wiseflow 抓取出的数据

1、参考 [dashbord](dashboard) 部分源码二次开发。

注意 wiseflow 的 core 部分并不需要 dashboard，目前产品也未集成 dashboard，如果您有dashboard需求，请下载 [V0.2.1版本](https://github.com/TeamWiseFlow/wiseflow/releases/tag/V0.2.1)

2、直接从 Pocketbase 中获取数据

wiseflow 所有抓取数据都会即时存入 pocketbase，因此您可以直接操作 pocketbase 数据库来获取数据。

PocketBase作为流行的轻量级数据库，目前已有 Go/Javascript/Python 等语言的SDK。
   - Go : https://pocketbase.io/docs/go-overview/
   - Javascript : https://pocketbase.io/docs/js-overview/
   - python : https://github.com/vaphes/pocketbase

## 🛡️ 许可协议

本项目基于 [Apache2.0](LICENSE) 开源。

商用合作，请联系 **Email：zm.zhao@foxmail.com**

- 商用客户请联系我们报备登记，产品承诺永远免费。


## 📬 联系方式

有任何问题或建议，欢迎通过 [issue](https://github.com/TeamWiseFlow/wiseflow/issues) 留言。


## 🤝 本项目基于如下优秀的开源项目：

- crawl4ai（Open-source LLM Friendly Web Crawler & Scraper） https://github.com/unclecode/crawl4ai
- pocketbase (Open Source realtime backend in 1 file) https://github.com/pocketbase/pocketbase
- python-pocketbase (pocketBase client SDK for python) https://github.com/vaphes/pocketbase

本项目开发受 [GNE](https://github.com/GeneralNewsExtractor/GeneralNewsExtractor)、[AutoCrawler](https://github.com/kingname/AutoCrawler) 、[SeeAct](https://github.com/OSU-NLP-Group/SeeAct) 启发。

## Citation

如果您在相关工作中参考或引用了本项目的部分或全部，请注明如下信息：

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```
