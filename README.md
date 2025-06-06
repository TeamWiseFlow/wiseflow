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


## 📥 安装与使用

### 📋 系统要求

- **Python**: 3.10 - 3.12 （推荐 3.12）
- **操作系统**: macOS、Linux 或 Windows
- **Git**: 用于克隆代码仓库

### 🚀 快速开始（推荐）

**只需三步即可开始使用！**

#### 1. 克隆代码仓库

🌹 点赞、fork是好习惯 🌹

**windows 用户请提前下载 git bash 工具，并在 bash 中执行如下命令 [bash下载链接](https://git-scm.com/downloads/win)**

```bash
git clone https://github.com/TeamWiseFlow/wiseflow.git
cd wiseflow
```

#### 2. 安装 uv（Python 包管理器）

uv 是一个快速的 Python 包管理器，比传统的 pip 和 conda 都要快很多：

**macOS/Linux 用户：**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows 用户：**
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 3. 一键启动

**MacOS/Linux 用户：**
```bash
chmod +x run.sh
./run.sh
```

**Windows 用户：**
```bash
python windows_run.py
```

✨ **就是这么简单！** 启动脚本会自动完成以下工作：
- ✅ 检查环境配置
- ✅ 同步项目依赖
- ✅ 激活虚拟环境
- ✅ 启动 PocketBase 数据库
- ✅ 运行 WiseFlow 应用

### 📝 手动安装（可选）

如果您希望手动控制每个步骤，也可以按照以下步骤进行：

#### 3. 执行根目录下的 install_pocketbase 脚本

linux/macos 用户请执行 

```bash
chmod +x install_pocketbase.sh
./install_pocketbase.sh
```

**windows 用户请执行 [install_pocketbase.ps1](./install_pocketbase.ps1) 脚本**

wiseflow 3.x版本使用 pocketbase 作为数据库，你当然也可以手动下载 pocketbase 客户端 (记得下载0.23.4版本，并放入 [pb](./pb) 目录下) 以及手动完成superuser的创建(记得存入.env文件)

具体可以参考 [pb/README.md](/pb/README.md)

#### 4. 配置环境

##### 4.1 创建并激活虚拟环境

```bash
uv venv
source .venv/bin/activate  # Linux/macOS
# 或者在 Windows 上：
# .venv\Scripts\activate
```

##### 4.2 安装依赖

```bash
uv sync
```

这将安装 wiseflow 及其所有依赖，并确保依赖版本的一致性。uv sync 会读取项目的依赖声明，并同步虚拟环境。

然后安装浏览器依赖：

```bash
python -m playwright install --with-deps chromium
```

### 🔧 配置环境变量

无论是快速开始还是手动安装，都需要配置 core/.env 文件：

🌟 **这里与之前版本不同**，V3.5开始需要把 .env 放置在 [core](./core) 文件夹中。

##### 4.3.1 大模型相关配置

wiseflow 是 LLM 原生应用，请务必保证为程序提供稳定的 LLM 服务。

🌟 **wiseflow 并不限定模型服务提供来源，只要服务兼容 openAI SDK 即可，包括本地部署的 ollama、Xinference 等服务**

###### 推荐1：使用硅基流动（siliconflow）提供的 MaaS 服务

siliconflow（硅基流动）提供大部分主流开源模型的在线 MaaS 服务，凭借着自身的加速推理技术积累，其服务速度和价格方面都有很大优势。使用 siliconflow 的服务时，.env的配置可以参考如下：

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://api.siliconflow.cn/v1"
PRIMARY_MODEL="Qwen3-30B-A3B"
SECONDARY_MODEL="Qwen3-14B"
VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct"
PROJECT_DIR="work_dir"
```
      
😄 如果您愿意，可以使用我的[siliconflow邀请链接](https://cloud.siliconflow.cn/i/WNLYbBpi)，这样我也可以获得更多token奖励 🌹

###### 推荐2：使用 AiHubMix 代理的openai、claude、gemini 等海外闭源商业模型服务

如果您的信源多为非中文页面，且也不要求提取出的 info 为中文，那么更推荐您使用 openai、claude、gemini 等海外闭源商业模型。您可以尝试第三方代理 **AiHubMix**，支持国内网络环境直连、支付宝便捷支付，免去封号风险。
使用 AiHubMix 的模型时，.env的配置可以参考如下：

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://aihubmix.com/v1" # 具体参考 https://doc.aihubmix.com/
PRIMARY_MODEL="gpt-4o"
SECONDARY_MODEL="gpt-4o-mini"
VL_MODEL="gpt-4o"
PROJECT_DIR="work_dir"
```

😄 欢迎使用 [AiHubMix邀请链接](https://aihubmix.com?aff=Gp54) 注册 🌹

###### 本地部署大模型服务

以 Xinference 为例，.env 配置可以参考如下：

```
# LLM_API_KEY='' 本地服务无需这一项，请注释掉或删除
LLM_API_BASE='http://127.0.0.1:9997' # 'http://127.0.0.1:11434/v1' for ollama
PRIMARY_MODEL=启动的模型 ID
VL_MODEL=启动的模型 ID
PROJECT_DIR="work_dir"
```

##### 4.3.2 pocketbase 账号密码配置

```
PB_API_AUTH="test@example.com|1234567890" 
```

这里pocketbase 数据库的 superuser 用户名和密码，记得用 | 分隔 (如果 install_pocketbase.sh 脚本执行成功，这一项应该已经存在了)

##### 4.3.3 JINA_API_KEY 设置（用于搜索引擎服务）

至 https://jina.ai/ 领取，目前无需注册即可领取。（如有高并发或商用需求，请充值后使用）

```
JINA_API_KEY=Your_API_KEY
```

##### 4.3.4 其他可选配置

下面的都是可选配置：
- #VERBOSE="true" 

  是否开启观测模式，开启的话会把 debug 信息记录在 logger 文件上（默认仅输出在 console 上）；

- #PB_API_BASE="" 

  只有当你的 pocketbase 不运行在默认ip 或端口下才需要配置，默认情况下忽略就行。

- #LLM_CONCURRENT_NUMBER=8 

  用于控制 llm 的并发请求数量，不设定默认是1（开启前请确保 llm provider 支持设定的并发，本地大模型慎用，除非你对自己的硬件基础有信心）

## 🚀 运行与使用

### 1. 启动服务

如果你已经按照"快速开始"的步骤执行了 `./run.sh`，应用已经在运行中了！

如果需要重新启动或者使用了手动安装方式，请执行：

**MacOS/Linux 用户：**

```bash
./run.sh          # 完整启动（推荐）
./run.sh --fast    # 快速启动（跳过依赖检查）
```

**Windows 用户：**

```bash
python windows_run.py
```

📝 **脚本功能说明：**
- ✅ 自动检查并同步项目依赖
- ✅ 智能激活虚拟环境
- ✅ 自动判断 PocketBase 运行状态并启动
- ✅ 启动 WiseFlow 核心服务

💡 **快速模式：** 二次运行时可以使用 `./run.sh --fast` 跳过依赖同步，启动更快。

⚠️ **注意：** 当你使用 `Ctrl+C` 终止进程时，PocketBase 进程可能不会自动终止，需要手动关闭或重启终端。

程序会先对所有已激活（activated 设定为 true）的信源执行一次爬取任务，之后以小时为单位按设定的频率周期执行。

### 2. 访问管理界面

🌐 启动成功后，打开浏览器访问：**http://127.0.0.1:8090/_/**

这是 PocketBase 管理界面，您可以在这里配置信源和关注点。

### 3. 配置信源和关注点

#### 3.1 配置信源（sites表单）

通过这个表单可以配置信源，注意：信源需要在下一步的 focus_point 表单中被选择。

sites 字段说明：
- url, 信源的url，信源无需给定具体文章页面，给文章列表页面即可。
- type, 类型，web 或者 rss。
    
#### 3.2 配置关注点（focus_point 表单）

通过这个表单可以指定你的关注点，LLM会按此提炼、过滤并分类信息。
    
字段说明：
- focuspoint, 关注点描述（必填），如"上海小升初信息"、"招标通知"
- explanation，关注点的详细解释或具体约定，如 "仅限上海市官方发布的初中升学信息"、"发布日期在2025年1月1日之后且金额100万以上的"等
- activated, 是否激活。如果关闭则会忽略该关注点，关闭后可再次开启
- per_hour, 爬取频率，单位为小时，类型为整数（1~24范围，我们建议扫描频次不要超过一天一次，即设定为24）
- search_engine, 每次爬取是否开启搜索引擎
- sites，选择对应的信源

**注意：V3.8版本后，配置的调整无需重启程序，会在下一次执行时自动生效。**

## 🐳 Docker 部署

如果您希望使用 Docker 部署 Wiseflow，我们也提供了完整的容器化支持。

### 1. 准备工作

确保您的系统已经安装了 Docker。

### 2. 配置环境变量

将`env_docker`文件复制为根目录下的`.env`文件：

```bash
cp env_docker .env
```

### 3. 参考《[安装与使用](#-安装与使用)》修改`.env`文件

以下几个环境变量是必须按需修改的:

```bash
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://api.siliconflow.cn/v1"
PRIMARY_MODEL="Qwen3-30B-A3B"
SECONDARY_MODEL="Qwen3-14B"
VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct"
PB_SUPERUSER_EMAIL="test@example.com"
PB_SUPERUSER_PASSWORD="1234567890" #no '&' in the password and at least 10 characters
```

### 4. 启动服务

在项目根目录执行：

```bash
docker compose up -d
```

服务启动后：

- PocketBase 管理界面：http://localhost:8090/_/
- Wiseflow 服务将自动运行并连接到 PocketBase

### 5. 停止服务

```bash
docker compose down
```

### 6. 注意事项

- `./pb/pb_data`目录用于存储 PocketBase 相关文件
- `./docker/pip_cache`目录用于存储 Python 依赖包缓存, 避免重复下载安装依赖
- `./core/work_dir`目录用于存储 wiseflow 运行时的日志, 可在`.env`文件修改`PROJECT_DIR`

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

- 商用客户请联系我们报备登记，产品承诺永远免费。


## 📬 联系方式

有任何问题或建议，欢迎通过 [issue](https://github.com/TeamWiseFlow/wiseflow/issues) 留言。


## 🤝 本项目基于如下优秀的开源项目：

- crawl4ai（Open-source LLM Friendly Web Crawler & Scraper） https://github.com/unclecode/crawl4ai
- pocketbase (Open Source realtime backend in 1 file) https://github.com/pocketbase/pocketbase
- python-pocketbase (pocketBase client SDK for python) https://github.com/vaphes/pocketbase
- feedparser (Parse feeds in Python) https://github.com/kurtmckee/feedparser

本项目开发受 [GNE](https://github.com/GeneralNewsExtractor/GeneralNewsExtractor)、[AutoCrawler](https://github.com/kingname/AutoCrawler) 、[SeeAct](https://github.com/OSU-NLP-Group/SeeAct) 启发。

## Citation

如果您在相关工作中参考或引用了本项目的部分或全部，请注明如下信息：

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```
