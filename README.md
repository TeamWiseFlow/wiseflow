# 首席情报官（Wiseflow）

**[English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md)**

🚀 **首席情报官**（Wiseflow）是一个敏捷的信息挖掘工具，可以从网站、微信公众号、社交平台等各种信息源中按设定的关注点提炼讯息，自动做标签归类并上传数据库。

**我们缺的不是信息，而是从海量信息中过滤噪音，从而让有价值的信息显露出来**

🌱看看首席情报官是如何帮您节省时间，过滤无关信息，并整理关注要点的吧！🌱

https://github.com/TeamWiseFlow/wiseflow/assets/96130569/bd4b2091-c02d-4457-9ec6-c072d8ddfb16


## 🔥 隆重介绍 V0.3.2 版本

在充分听取社区反馈意见基础之上，我们重新提炼了 wiseflow 的产品定位，新定位更加精准也更加聚焦，V0.3.2版本即是该定位下的全新架构版本，相对于之前版本如下改进：

- 引入 [Crawlee](https://github.com/apify/crawlee-python) 基础爬虫架构，大幅提升页面获取能力。实测之前获取不到（包括获取为乱码的）页面目前都可以很好的获取了，后续大家碰到不能很好获取的页面，欢迎在 [issue #136](https://github.com/TeamWiseFlow/wiseflow/issues/136) 中进行反馈；
- 新产品定位下全新的信息提取策略——“爬查一体”，放弃文章详细提取，全面使用 llm 直接从页面中提取用户感兴趣的信息（infos），同时自动判断值得跟进爬取的链接；
- 适配最新版本（v0.23.4）的 Pocketbase，同时更新表单配置。另外新架构已经无需 GNE 等模块，requirement 依赖项目降低到8个；
- 新架构部署方案也更加简便，docker 模式支持代码仓热更新，这意味着后续升级就无需再重复docker build了。
- 更多细节，参考 [CHANGELOG](CHANGELOG.md)

🌟 注意：

V0.3.2 架构和依赖上都较之前版本有诸多变化，因此请务必重新拉取代码仓，并参考最新的部署方案重新部署，V0.3.2支持python 环境源码使用、docker 容器部署，同时我们也即将上线免部署的服务网站，注册账号就可以直接使用，敬请期待！

V0.3.2 版本效果截图：

<img alt="sample.png" src="asset/sample.png" width="1024"/>

V0.3.x 后续计划中的升级内容还有：

- 尝试引入新的 mp_crawler, 公众号文章监控无需wxbot；
- 引入对 RSS 信息源的支持；
- 引入 [SeeAct](https://github.com/OSU-NLP-Group/SeeAct) 方案，通过视觉大模型提升 wiseflow 自主深入挖掘能力。

## ✋ wiseflow 与传统的爬虫工具、AI搜索、知识库（RAG）项目有何不同？

承蒙大家的厚爱，wiseflow自2024年6月底发布 V0.3.0版本来受到了开源社区的广泛关注，甚至吸引了不少自媒体的主动报道，在此首先表示感谢！

但我们也注意到部分关注者对 wiseflow 的功能定位存在一些理解偏差，如下表格列出了 wiseflow 与传统爬虫工具、AI搜索、知识库（RAG）类项目的对比： 

|          | 与 **首席情报官（Wiseflow）** 的比较说明| 
|-------------|-----------------|
| **爬虫类工具** | 首先 wiseflow 是基于爬虫工具的项目（以目前的版本而言，wiseflow 集成了优秀的开源爬虫项目 Crwalee，而 Crawlee 的底层又是基于 beautifulsoup\playwright\httpx等大家耳熟能详的流行库）……但传统的爬虫工具都是面向开发者的，需要开发者手动去探索目标站点的结构，分析出要提取元素的 xpath 等，这不仅阻挡了普通用户，同时也毫无通用性可言，即对于不同网站（包括已有网站升级）都需要重做分析和探索。这个问题在 LLM 出现之前是无解的，而wiseflow致力的方向即是使用 LLM 自动化目标站点的分析和探索工作，从而实现“普通用户也可使用的通用爬虫”，从这个角度来说，你可以简单理解 wiseflow 为 “能自动使用爬虫工具的 AI 智能体” |
| **AI搜索** |  AI搜索主要的应用场景是**具体问题的即时问答**，举例：”XX公司的创始人是谁“、“xx品牌下的xx产品哪里有售” ，用户要的是**一个答案**；wiseflow主要的应用场景是**某一方面信息的持续采集**，比如XX公司的关联信息追踪，XX品牌市场行为的持续追踪……在这些场景下，用户能提供关注点（某公司、某品牌）、甚至能提供信源（站点 url 等），但无法提出具体搜索问题，用户要的是**一系列相关信息**| 
| **知识库（RAG）类项目** | 知识库（RAG）类项目一般是基于已有信息的下游任务，并且一般面向的是私有知识（比如企业内的操作手册、产品手册、政府部门的文件等）；wiseflow 目前并未整合下游任务，同时面向的是互联网上的公开信息，如果从“智能体”的角度来看，二者属于为不同目的而构建的智能体，RAG 类项目是“（内部）知识助理智能体”，而 wiseflow 则是“（外部）信息采集智能体”|

## 📥 安装与使用

### 1. 克隆代码仓库

🌹 点赞、fork是好习惯 🌹

```bash
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

### 2. 参考env_sample 配置 .env文件放置在 core 目录下

🌟 **这里与之前版本不同**，V0.3.2开始需要把 .env 放置在 core文件夹中。

另外 V0.3.2 起，env 配置也大幅简化了，必须的配置项目只有三项，具体如下：

- LLM_API_KEY=""  # 这还是你的大模型服务key，这是必须的
- LLM_API_BASE="https://api.siliconflow.cn/v1" # 服务接口地址，任何支持 openai sdk 的服务商都可以（推荐 siliconflow），如果直接使用openai 的服务，这一项也可以不填
- PB_API_AUTH="test@example.com|1234567890" # pocketbase 数据库的 superuser 用户名和密码，记得用 | 分隔

下面的都是可选配置：
- #VERBOSE="true" # 是否开启观测模式，开启的话，不仅会把 debug log信息记录在 logger 文件上（模式仅是输出在 console 上），同时会开启 playwright 的浏览器窗口，方便你观察抓取过程，但同时会增加抓取速度；
- #PRIMARY_MODEL="Qwen/Qwen2.5-7B-Instruct" # 主模型选择，在使用 siliconflow 服务的情况下，这一项不填就会默认调用Qwen2.5-7B-Instruct，实测基本也够用，但我更加**推荐 Qwen2.5-14B-Instruct**
- #SECONDARY_MODEL="THUDM/glm-4-9b-chat" # 副模型选择，在使用 siliconflow 服务的情况下，这一项不填就会默认调用glm-4-9b-chat。
- #PROJECT_DIR="work_dir" # 项目运行数据目录，不配置的话，默认在  `core/work_dir` ，注意：目前整个 core 目录是挂载到 container 下的，所以意味着你可以直接访问这里。
- #PB_API_BASE"="" # 只有当你的 pocketbase 不运行在默认ip 或端口下才需要配置，默认情况下忽略就行。


### 3.1 使用docker构筑 image 运行

对于国内用户，可以先配置镜像源：

最新可用 docker 镜像加速地址参考：[参考1](https://github.com/dongyubin/DockerHub) [参考2](https://www.coderjia.cn/archives/dba3f94c-a021-468a-8ac6-e840f85867ea) 

🌟 **三方镜像，风险自担。**

```bash
cd wiseflow
docker compose up
```

**注意：**

第一次运行docker container时可能会遇到报错，这其实是正常现象，因为你尚未为pb仓库创建 super user 账号。
    
此时请保持container不关闭状态，浏览器打开`http://127.0.0.1:8090/_/ `，按提示创建 super user 账号（一定要使用邮箱），然后将创建的用户名密码填入.env文件，重启container即可。

🌟 docker运行默认进入 task

### 3.2 使用python环境运行

推荐使用 conda 构建虚拟环境

```bash
cd wiseflow
conda create -n wiseflow python=3.10
conda activate wiseflow
cd core
pip install -r requirements.txt
```

之后可以参考core/scripts 中的脚本分别启动pb、task和backend （将脚本文件移动到core目录下）
    
**注意：**
   - 一定要先启动pb，至于task和backend是独立进程，先后顺序无所谓，也可以按需求只启动其中一个；
   - 需要先去这里 https://pocketbase.io/docs/ 下载对应自己设备的pocketbase客户端，并放置在 /core/pb 目录下
   - pb运行问题（包括首次运行报错等）参考 [core/pb/README.md](/pb/README.md)
   - 使用前请创建并编辑.env文件，放置在wiseflow代码仓根目录（core目录的上级），.env文件可以参考env_sample，详细配置说明见下

📚 for developer， see [/core/README.md](/core/README.md) for more
    
通过 pocketbase 访问获取的数据：
   - http://127.0.0.1:8090/_/ - Admin dashboard UI
   - http://127.0.0.1:8090/api/ - REST API
    

### 3. 配置

复制目录下的env_sample，并改名为.env, 参考如下 填入你的配置信息（LLM服务token等）
    
**windows用户如果选择直接运行python程序，可以直接在 “开始 - 设置 - 系统 - 关于 - 高级系统设置 - 环境变量“ 中设置如下项目，设置后需要重启终端生效**

   - LLM_API_KEY # 大模型推理服务API KEY
   - LLM_API_BASE # 本项目依赖openai sdk，只要模型服务支持openai接口，就可以通过配置该项正常使用，如使用openai服务，删除这一项即可
   - WS_LOG="verbose"  # 设定是否开始debug观察，如无需要，删除即可
   - GET_INFO_MODEL # 信息提炼与标签匹配任务模型，默认为 gpt-4o-mini-2024-07-18
   - REWRITE_MODEL # 近似信息合并改写任务模型，默认为 gpt-4o-mini-2024-07-18
   - HTML_PARSE_MODEL # 网页解析模型（GNE算法效果不佳时智能启用），默认为 gpt-4o-mini-2024-07-18
   - PROJECT_DIR # 数据、缓存以及日志文件存储位置，相对于代码仓的相对路径，默认不填就在代码仓
   - PB_API_AUTH='email|password' # pb数据库admin的邮箱和密码（注意一定是邮箱，可以是虚构的邮箱）
   - PB_API_BASE  # 正常使用无需这一项，只有当你不使用默认的pocketbase本地接口（8090）时才需要
    
    
### 4. 模型推荐 [2024-09-03]

经过反复测试（中英文任务）**GET_INFO_MODEL**、**REWRITE_MODEL**、**HTML_PARSE_MODEL** 三项最小可用模型分别为：**"THUDM/glm-4-9b-chat"**、**"Qwen/Qwen2-7B-Instruct"**、**"Qwen/Qwen2-7B-Instruct"**
    
目前，SiliconFlow已经官宣Qwen2-7B-Instruct、glm-4-9b-chat在线推理服务免费，这意味着您可以“零成本”使用wiseflow啦！
      
😄 如果您愿意，可以使用我的[siliconflow邀请链接](https://cloud.siliconflow.cn?referrer=clx6wrtca00045766ahvexw92)，这样我也可以获得更多token奖励 😄

⚠️ **V0.3.1更新**
      
如果您使用带explaination的复杂tag，那么glm-4-9b-chat规模的模型是无法保证准确理解的，目前测试下来针对该类型任务效果比较好的模型为 **Qwen/Qwen2-72B-Instruct** 和 **gpt-4o-mini-2024-07-18** 。
   
针对有需求使用 `gpt-4o-mini-2024-07-18` 的用户，可以尝试第三方代理 **AiHubMix**，支持国内网络环境直连、支付宝充值（实际费率相当于官网86折）

🌹 欢迎使用如下邀请链接 [AiHubMix邀请链接](https://aihubmix.com?aff=Gp54) 注册 🌹

🌍 上述两个平台的在线推理服务均兼容openai SDK，配置`.env `的`LLM_API_BASE`和`LLM_API_KEY`后即可使用。


### 5. **关注点和定时扫描信源添加**
    
启动程序后，打开pocketbase Admin dashboard UI (http://127.0.0.1:8090/_/)
    
#### 5.1 打开 tags表单

通过这个表单可以指定你的关注点，LLM会按此提炼、过滤并分类信息。
    
tags 字段说明：
   - name, 关注点名称
   - explaination，关注点的详细解释或具体约定，如 “仅限上海市官方发布的初中升学信息”（tag name为 上海初中升学信息）
   - activated, 是否激活。如果关闭则会忽略该关注点，关闭后可再次开启。开启和关闭无需重启docker容器，会在下一次定时任务时更新。

#### 5.2 打开 sites表单

通过这个表单可以指定自定义信源，系统会启动后台定时任务，在本地执行信源扫描、解析和分析。

sites 字段说明：
   - url, 信源的url，信源无需给定具体文章页面，给文章列表页面即可。
   - per_hours, 扫描频率，单位为小时，类型为整数（1~24范围，我们建议扫描频次不要超过一天一次，即设定为24）
   - activated, 是否激活。如果关闭则会忽略该信源，关闭后可再次开启。开启和关闭无需重启docker容器，会在下一次定时任务时更新。


### 6. 本地部署

如您所见，本项目最低仅需使用7b\9b大小的LLM，且无需任何向量模型，这就意味着仅仅需要一块3090RTX（24G显存）就可以完全的对本项目进行本地化部署。
    
请保证您的本地化部署LLM服务兼容openai SDK，并配置 LLM_API_BASE 即可。

注：若需让7b~9b规模的LLM可以实现对tag explaination的准确理解，推荐使用dspy进行prompt优化，但这需要累积约50条人工标记数据。详见 [DSPy](https://dspy-docs.vercel.app/)

##  🔄 如何在您自己的程序中使用 wiseflow 抓取出的数据

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

有任何问题或建议，欢迎通过 [issue](https://github.com/TeamWiseFlow/wiseflow/issues) 与我们联系。


## 🤝 本项目基于如下优秀的开源项目：

- GeneralNewsExtractor （ General Extractor of News Web Page Body Based on Statistical Learning） https://github.com/GeneralNewsExtractor/GeneralNewsExtractor
- json_repair（Repair invalid JSON documents ） https://github.com/josdejong/jsonrepair/tree/main 
- python-pocketbase (pocketBase client SDK for python) https://github.com/vaphes/pocketbase

## Citation

如果您在相关工作中参考或引用了本项目的部分或全部，请注明如下信息：

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```
