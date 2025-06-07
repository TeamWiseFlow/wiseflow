# WiseFlow 安装与使用手册

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
```powershell
.\run.ps1
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

**windows 用户请执行：**
```powershell
.\install_pocketbase.ps1
```

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

如果你已经按照"快速开始"的步骤执行了 `.\run.ps1`（Windows）或 `./run.sh`（MacOS/Linux），应用已经在运行中了！

如果需要重新启动或者使用了手动安装方式，请执行：

**MacOS/Linux 用户：**

```bash
./run.sh
```

（注意：你可能需要先执行 `chmod +x run.sh` 赋予执行权限）

**Windows 用户：**

```powershell
.\run.ps1
```

（注意：你可能需要先执行 `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` 赋予执行权限）

📝 **脚本功能说明：**
- ✅ 自动检查并同步项目依赖
- ✅ 智能激活虚拟环境
- ✅ 自动判断 PocketBase 运行状态并启动
- ✅ 启动 WiseFlow 核心服务

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

4.x 版本的 docker 部署方案请等待后续，也希望有兴趣的开发者提 PR 贡献~