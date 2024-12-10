# 首席情报官（Wiseflow）

**[English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md)**

🚀 **首席情报官**（Wiseflow）是一个敏捷的信息挖掘工具，可以从网站、微信公众号、社交平台等各种信息源中按设定的关注点提炼讯息，自动做标签归类并上传数据库。

**我们缺的不是信息，而是从海量信息中过滤噪音，从而让有价值的信息显露出来**

🌱看看首席情报官是如何帮您节省时间，过滤无关信息，并整理关注要点的吧！🌱



## 🔥 隆重介绍 V0.3.5 版本

在充分听取社区反馈意见基础之上，我们重新提炼了 wiseflow 的产品定位，新定位更加聚焦，V0.3.5版本即是该定位下的全新架构版本：

- 引入 [Crawlee](https://github.com/apify/crawlee-python) 作为基础爬虫和任务管理框架，大幅提升页面获取能力。实测之前获取不到（包括获取为乱码的）页面目前都可以很好的获取了，后续大家碰到不能很好获取的页面，欢迎在 [issue #136](https://github.com/TeamWiseFlow/wiseflow/issues/136) 中进行反馈；
- 新产品定位下全新的信息提取策略——“爬查一体”，放弃文章详细提取，爬取过程中即使用 llm 直接提取用户感兴趣的信息（infos），同时自动判断值得跟进爬取的链接，**你关注的才是你需要的**；
- 适配最新版本（v0.23.4）的 Pocketbase，同时更新表单配置。另外新架构已经无需 GNE 等模块，requirement 依赖项目降低到8个；
- 新架构部署方案也更加简便，docker 模式支持代码仓热更新，这意味着后续升级就无需再重复docker build了。
- 更多细节，参考 [CHANGELOG](CHANGELOG.md)

🌟 **V0.3.x 后续计划**

- 引入 [SeeAct](https://github.com/OSU-NLP-Group/SeeAct) 方案，通过视觉大模型指导复杂页面的操作，如滚动、点击后出现信息等情况（V0.3.6）；
- 尝试支持微信公众号免wxbot订阅（V0.3.7）；
- 引入对 RSS 信息源的支持（V0.3.8）;
- 尝试引入 LLM 驱动的轻量级知识图谱，帮助用户从 infos 中建立洞察（V0.3.9）。

## ✋ wiseflow 与传统的爬虫工具、AI搜索、知识库（RAG）项目有何不同？

wiseflow自2024年6月底发布 V0.3.0版本来受到了开源社区的广泛关注，甚至吸引了不少自媒体的主动报道，在此首先表示感谢！

但我们也注意到部分关注者对 wiseflow 的功能定位存在一些理解偏差，如下表格通过与传统爬虫工具、AI搜索、知识库（RAG）类项目的对比，代表了我们目前对于 wiseflow 产品最新定位思考。

|          | 与 **首席情报官（Wiseflow）** 的比较说明| 
|-------------|-----------------|
| **爬虫类工具** | 首先 wiseflow 是基于爬虫工具的项目（以目前版本而言，我们基于爬虫框架 Crawlee），但传统的爬虫工具在信息提取方面需要人工的介入，提供明确的 Xpath 等信息……这不仅阻挡了普通用户，同时也毫无通用性可言，对于不同网站（包括已有网站升级后）都需要人工重做分析，并更新提取代码。wiseflow致力于使用 LLM 自动化网页的分析和提取工作，用户只要告诉程序他的关注点即可，从这个角度来说，可以简单理解 wiseflow 为 “能自动使用爬虫工具的 AI 智能体” |
| **AI搜索** |  AI搜索主要的应用场景是**具体问题的即时问答**，举例：”XX公司的创始人是谁“、“xx品牌下的xx产品哪里有售” ，用户要的是**一个答案**；wiseflow主要的应用场景是**某一方面信息的持续采集**，比如XX公司的关联信息追踪，XX品牌市场行为的持续追踪……在这些场景下，用户能提供关注点（某公司、某品牌）、甚至能提供信源（站点 url 等），但无法提出具体搜索问题，用户要的是**一系列相关信息**| 
| **知识库（RAG）类项目** | 知识库（RAG）类项目一般是基于已有信息的下游任务，并且一般面向的是私有知识（比如企业内的操作手册、产品手册、政府部门的文件等）；wiseflow 目前并未整合下游任务，同时面向的是互联网上的公开信息，如果从“智能体”的角度来看，二者属于为不同目的而构建的智能体，RAG 类项目是“（内部）知识助理智能体”，而 wiseflow 则是“（外部）信息采集智能体”|

## 📥 安装与使用

### 1. 克隆代码仓库

🌹 点赞、fork是好习惯 🌹

```bash
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

### 2. 参考 env_sample 配置 .env 文件放置在 core 目录下

🌟 **这里与之前版本不同**，V0.3.5开始需要把 .env 放置在 core文件夹中。

另外 V0.3.5 起，env 配置也大幅简化了，必须的配置项目只有三项，具体如下：

- LLM_API_KEY=""

    大模型服务key，这是必须的

- LLM_API_BASE="https://api.siliconflow.cn/v1" 

    服务接口地址，任何支持 openai sdk 的服务商都可以，如果直接使用openai 的服务，这一项也可以不填

- PB_API_AUTH="test@example.com|1234567890" 

  pocketbase 数据库的 superuser 用户名和密码，记得用 | 分隔

下面的都是可选配置：
- #VERBOSE="true" 

  是否开启观测模式，开启的话，不仅会把 debug log信息记录在 logger 文件上（默认仅输出在 console 上），同时会开启 playwright 的浏览器窗口，方便观察抓取过程；

- #PRIMARY_MODEL="Qwen/Qwen2.5-7B-Instruct"

    主模型选择，在使用 siliconflow 服务的情况下，这一项不填就会默认调用Qwen2.5-7B-Instruct，实测基本也够用，但我更加**推荐 Qwen2.5-14B-Instruct**

- #SECONDARY_MODEL="THUDM/glm-4-9b-chat" 

    副模型选择，在使用 siliconflow 服务的情况下，这一项不填就会默认调用glm-4-9b-chat。

- #PROJECT_DIR="work_dir" 

    项目运行数据目录，不配置的话，默认在  `core/work_dir` ，注意：目前整个 core 目录是挂载到 container 下的，所以意味着你可以直接访问这里。

- #PB_API_BASE="" 

  只有当你的 pocketbase 不运行在默认ip 或端口下才需要配置，默认情况下忽略就行。

### 3.1 使用docker运行

✋ V0.3.5版本架构和依赖与之前版本有较大不同，请务必重新拉取代码，删除旧版本镜像（包括外挂的 pb_data 文件夹），重新build！

对于国内用户，可以先配置镜像源：

最新可用 docker 镜像加速地址参考：[参考1](https://github.com/dongyubin/DockerHub) [参考2](https://www.coderjia.cn/archives/dba3f94c-a021-468a-8ac6-e840f85867ea) 

**三方镜像，风险自担。**

之后

```bash
cd wiseflow
docker compose up
```

**注意：**

第一次运行docker container时程序可能会报错，这是正常现象，请按屏幕提示创建 super user 账号（一定要使用邮箱），然后将创建的用户名密码填入.env文件，重启container即可。

🌟 docker方案默认运行 task.py ，即会周期性执行爬取-提取任务（启动时会立即先执行一次，之后每隔一小时启动一次）

### 3.2 使用python环境运行

✋ V0.3.5版本架构和依赖与之前版本有较大不同，请务必重新拉取代码，删除（或重建）pb_data

推荐使用 conda 构建虚拟环境

```bash
cd wiseflow
conda create -n wiseflow python=3.10
conda activate wiseflow
cd core
pip install -r requirements.txt
```

之后去这里 [下载](https://pocketbase.io/docs/) 对应的 pocketbase 客户端，放置到 [/pb](/pb) 目录下。然后

```bash
chmod +x run.sh
./run_task.sh # if you just want to scan sites one-time (no loop), use ./run.sh
```

这个脚本会自动判断 pocketbase 是否已经在运行，如果未运行，会自动拉起。但是请注意，当你 ctrl+c 或者 ctrl+z 终止进程时，pocketbase 进程不会被终止，直到你关闭terminal。

另外与 docker 部署一样，第一次运行时可能会出现报错，请按屏幕提示创建 super user 账号（一定要使用邮箱），然后将创建的用户名密码填入.env文件，再次运行即可。

当然你也可以在另一个 terminal 提前运行并设定 pocketbase（这会避免第一次的报错），具体可以参考 [pb/README.md](/pb/README.md)

### 4. 模型推荐 [2024-12-09]

虽然参数量越大的模型意味着更佳的性能，但经过实测，**使用 Qwen2.5-7b-Instruct 和 glm-4-9b-chat 模型，即可以达到基本的效果**。不过综合考虑成本、速度和效果，我更加推荐主模型
**（PRIMARY_MODEL）使用Qwen2.5-14B-Instruct**。

这里依然强烈推荐使用 siliconflow（硅基流动）的 MaaS 服务，提供多个主流开源模型的服务，量大管饱，Qwen2.5-7b-Instruct 和 glm-4-9b-chat 目前提供免费服务。（主模型使用Qwen2.5-14B-Instruct情况下，爬取374个网页，有效抽取43条 info，总耗费￥3.07）
      
😄 如果您愿意，可以使用我的[siliconflow邀请链接](https://cloud.siliconflow.cn?referrer=clx6wrtca00045766ahvexw92)，这样我也可以获得更多token奖励 🌹

**如果您的信源多为非中文页面，且也不要求提取出的 info 为中文，那么更推荐您使用 openai 或者 claude 等海外厂家的模型。**
   
您可以尝试第三方代理 **AiHubMix**，支持国内网络环境直连、支付宝便捷支付，免去封号风险；

😄 欢迎使用如下邀请链接 [AiHubMix邀请链接](https://aihubmix.com?aff=Gp54) 注册 🌹

🌟 **请注意 wiseflow 本身并不限定任何模型服务，只要服务兼容 openAI SDK 即可，包括本地部署的 ollama、Xinference 等服务**


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

商用以及定制合作，请联系 **Email：35252986@qq.com**

- 商用客户请联系我们报备登记，产品承诺永远免费。


## 📬 联系方式

有任何问题或建议，欢迎通过 [issue](https://github.com/TeamWiseFlow/wiseflow/issues) 留言。


## 🤝 本项目基于如下优秀的开源项目：

- crawlee-python （A web scraping and browser automation library for Python to build reliable crawlers. Works with BeautifulSoup, Playwright, and raw HTTP. Both headful and headless mode. With proxy rotation.） https://github.com/apify/crawlee-python
- json_repair（Repair invalid JSON documents ） https://github.com/josdejong/jsonrepair/tree/main 
- python-pocketbase (pocketBase client SDK for python) https://github.com/vaphes/pocketbase
- SeeAct（a system for generalist web agents that autonomously carry out tasks on any given website, with a focus on large multimodal models (LMMs) such as GPT-4Vision.） https://github.com/OSU-NLP-Group/SeeAct

同时受 [GNE](https://github.com/GeneralNewsExtractor/GeneralNewsExtractor)、[AutoCrawler](https://github.com/kingname/AutoCrawler) 启发。

## Citation

如果您在相关工作中参考或引用了本项目的部分或全部，请注明如下信息：

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```