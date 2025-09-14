# WiseFlow 安装与使用手册

**3.x 用户需要完全删除原代码仓和 pb 文件夹，并重新克隆 4.x 代码仓，否则无法正常启动。**

**4.0 用户升级4.1版本，拉取最新代码后，先执行一下 ./pb/pocketbase migrate 命令，否则无法正常启动。**

**4.2版本起，请先下载 google chrome浏览器，并按默认路径安装**

## 📋 系统要求

- **Python**: 3.10 - 3.12 （推荐 3.12）
- **操作系统**: macOS、Linux 或 Windows
- **硬件要求**: 8GB 内存以上（使用在线 llm 服务情况下）

## 📥 使用说明

wiseflow4.x 用户操作界面使用 pocketbase （虽然我不喜欢，但暂时没有更优方案）

### 1. 访问界面

🌐 启动成功后，打开浏览器访问：**http://127.0.0.1:8090/_/**

### 2. 配置信源和关注点

切换到 focus_point 表单

通过这个表单可以指定你的关注点，LLM会按此提炼、过滤并分类信息。
    
字段说明：
- focuspoint（必须）, 关注点描述，告诉大模型你想要什么信息，如"上海小升初信息"、"招标通知"
- restrictions（可选），关注点筛选约束，告诉大模型需要排除什么信息，如 "仅限上海市官方发布的初中升学信息"、"发布日期在2025年1月1日之后且金额100万以上的"等
- explanation（可选），对于一些特殊概念或者专业术语的解释，避免大模型误解，比如“小升初是指小学升初中”
- activated, 是否激活。如果关闭则会忽略该关注点，关闭后可再次开启
- freq, 爬取频率，单位为小时，类型为整数（我们建议扫描频次不要超过一天一次，即设定为24，最小值为2，即每2小时抓取一次）
- search, 配置详细的搜索源，目前支持 bing、github、arxiv 和 ebay。
- sources，选择对应的信源

#### 💡 关注点的写法非常重要，直接决定了信息提取是否能够达到您的要求，具体而言：

  - 如果您的使用场景是行业信息、学术信息、政策信息追踪等，并且您的信源中包含了广泛的搜索，那么关注点应该使用类似搜索引擎的关键词模式，同时在限制和解释中进行约束，并在必要的情况下设定角色和目的；

  - 如果您的使用场景是竞争对手跟踪、背景调查等，信源非常具体，比如多为竞争对手主页、官方账号等，那么关注点只需填入您的关注角度，比如“降价信息”、“新产品信息”等；

**focus_point 配置的调整无需重启程序，会在下一次执行时自动生效。** 

在 sources 页面或者 focus_points 绑定信源页面中均可以添加信息源，信源添加字段说明：

- type, 类型，目前支持：web、rss、wb（微博）、ks（快手）、mp（微信公众号(4.0暂不支持，需要等待4.1)）
- creators, 需要爬取的创作者id（多个使用‘，’分隔），这一项仅对 ks、wb 和 mp 有效，其中 ks和 mp 支持填入 ‘homefeed’（代表每次获取系统推送内容）。这一项也可以不填，则信源只用于搜索

  *注意，id 要使用平台对应的网页版中的主页链接，比如微博的 id 是 https://m.weibo.cn/profile/2656274875，则 id 为 2656274875*

- url, 信源对应的链接，这一项仅对 rss 和 web 类型有效。

### 3. 结果查看

- infos 页面 存储最终提取的有用信息；
- crawled_data 页面 存储爬取的原始数据；
- ks_cache 页面 存储快手缓存数据；
- wb_cache 页面 存储微博缓存数据；

## 🌟 部署安装

**部署安装仅需三步！**

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
- LLM_API_BASE="" # LLM 服务接口地址（中国大陆地区用户推荐使用siliconflow，其他地区用户请留空）
- PRIMARY_MODEL=ByteDance-Seed/Seed-OSS-36B-Instruct # 价格敏感且提取不复杂的场景可以使用 Qwen3-14B
- VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct" # 视觉模型，可选但最好有。用于分析必要的页面图片（程序会根据上下判定是否有必要分析，不会每张图都提取一次），最低使用Qwen2.5-VL-7B-Instruct即可

### 🚀  起飞！

```bash
cd wiseflow
uv venv # 仅第一次执行需要
source .venv/bin/activate  # Linux/macOS
# 或者在 Windows 上：
# .venv\Scripts\activate
uv sync # 仅第一次执行需要
chmod +x run.sh # 仅第一次执行需要
./run.sh
```

✨ **就是这么简单！** 启动脚本会自动完成以下工作：
- ✅ 检查环境配置
- ✅ 同步项目依赖
- ✅ 激活虚拟环境
- ✅ 启动 PocketBase 数据库
- ✅ 运行 WiseFlow 应用

程序会先对所有已激活（activated 设定为 true）的信源执行一次爬取任务，之后以小时为单位按设定的频率周期执行。

⚠️ **注意：** 当你使用 `Ctrl+C` 终止进程时，PocketBase 进程可能不会自动终止，需要手动关闭或重启终端。


### 📝 手动安装（可选）

如果您希望手动控制每个步骤，也可以按照以下步骤进行：

#### 1. 执行根目录下的 install_pocketbase 脚本

linux/macos 用户请执行 

```bash
chmod +x install_pocketbase.sh
./install_pocketbase.sh
```

**windows 用户请执行：**
```powershell
.\install_pocketbase.ps1
```

#### 2. 创建并激活虚拟环境

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

最后启动主服务：

```bash
python core/run_task.py
# 或者在 Windows 上：
# python core\run_task.py
```

在需要使用 pocketbase 用户界面时，启动 pocketbase 服务：

```bash
cd wiseflow/pb
./pocketbase serve
```

或者在 Windows 上：

```powershell
cd wiseflow\pb
.\pocketbase.exe serve
```

### 🔧 配置环境变量

无论是快速开始还是手动安装，都需要参考 env_sample 文件，并创建 .env 文件：

#### 1. 大模型相关配置

wiseflow 是 LLM 原生应用，请务必保证为程序提供稳定的 LLM 服务。

🌟 **wiseflow 并不限定模型服务提供来源，只要服务兼容 openAI SDK 即可，包括本地部署的 ollama、Xinference 等服务**

##### 推荐1：使用硅基流动（siliconflow）提供的 MaaS 服务

siliconflow（硅基流动）提供大部分主流开源模型的在线 MaaS 服务，凭借着自身的加速推理技术积累，其服务速度和价格方面都有很大优势。使用 siliconflow 的服务时，.env的配置可以参考如下：

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://api.siliconflow.cn/v1"
- PRIMARY_MODEL=ByteDance-Seed/Seed-OSS-36B-Instruct # 价格敏感且提取不复杂的场景可以使用 Qwen3-14B
VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct"
CONCURRENT_NUMBER=6
```
      
😄 如果您愿意，可以使用我的[siliconflow邀请链接](https://cloud.siliconflow.cn/i/WNLYbBpi)，这样我也可以获得更多token奖励 🌹

##### 推荐2：使用 AiHubMix 代理的openai、claude、gemini 等海外闭源商业模型服务

使用 AiHubMix 的模型时，.env的配置可以参考如下：

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://aihubmix.com/v1" # 具体参考 https://doc.aihubmix.com/
PRIMARY_MODEL="o3-mini" #or openai/gpt-oss-20b
VL_MODEL="gpt-4o-mini"
CONCURRENT_NUMBER=6
```

😄 欢迎使用 [AiHubMix邀请链接](https://aihubmix.com?aff=Gp54) 注册 🌹

##### 本地部署大模型服务

以 Xinference 为例，.env 配置可以参考如下：

```
# LLM_API_KEY='' 本地服务无需这一项，请注释掉或删除
LLM_API_BASE='http://127.0.0.1:9997' # 'http://127.0.0.1:11434/v1' for ollama
PRIMARY_MODEL=启动的模型 ID
VL_MODEL=启动的模型 ID
CONCURRENT_NUMBER=1 # 根据实际硬件资源决定
```

#### 3. 其他可选配置

下面的都是可选配置：
- #VERBOSE="true" 

  是否开启观测模式，开启的话会把 debug 信息记录在 logger 文件上（默认仅输出在 console 上）；

- #CONCURRENT_NUMBER=6

  用于控制 llm 的并发请求数量，不设定默认是1（开启前请确保 llm provider 支持设定的并发，本地大模型慎用，除非你对自己的硬件基础有信心）


## 🐳 Docker 部署

4.x 版本的 docker 部署方案未经测试，我们即将推出一键安装包

## 🌹 付费服务

开源不易 ☺️ 文档书写和咨询答疑更是耗费时间，如果您愿意提供支持，我们将提供更优质的服务~

- 详细教程视频 + 3次邮件答疑 + 加入付费用户微信群（作者本人在群内）： ￥36.88

购买方式：扫描如下付款码，然后添加微信: bigbrother666sh，并提供付款截图。

(添加好友后最长8小时会通过，也可以通过邮箱 35252986@qq.com 联系)

<img src="alipay.png" alt="支付宝付款码" width="300">      <img src="weixinpay.jpg" alt="微信付款码" width="300">
