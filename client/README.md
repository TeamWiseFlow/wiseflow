# WiseFlow Client 用户手册

对于没有二次开发需求的用户而言，使用WiseFlow客户端非常简便。**如果您是开发者，有二次开发的需要，请进入backend目录、web目录分别查看后端和前端的源代码。也可以联系我们洽谈定制版本合作（35252986@qq.com）**

## 本地客户端使用

### 1、参考如下内容创建 `.env `文件 （可以直接编辑 env_sample后再改名）

- PROJECT_DIR="xxxx" #项目缓存文件夹（相对于client文件夹的路径），如果不设定就直接放在repo下面了
- WS_LOG="verbose"  #设定是否开始debug观察，调试阶段建议开始，尤其可以观察到每一步接口调用的原始请求和返回
- LLM_API_BASE： #使用兼容openaiSDK的LLM服务或者本地大模型推理使用（不配置默认走http://localhost:8000）
- LLM_API_KEY="YOUR_DASHSCOPE_API_KEY" #大模型推理服务API KEY(注册参考最下)
- ZHIPUAI_API_KEY= #使用智谱大模型接口使用（目前只会调用glm4，model参数没有意义）
- VOLC_KEY='AK|SK' #使用火山云翻译api使用，格式为AK|SK
- EMBEDDING_MODEL_PATH='' #embedding模型的地址，注意需要填写完整的绝对路径
- RERANKER_MODEL_PATH='' #rerank模型地址，注意需要填写完整的绝对路径
- DEVICE="cuda:0" #配置的话使用GPU，不配置使用CPU。
- PB_API_AUTH='email|password' #pb数据库admin的邮箱和密码（<span style="color: red; font-weight: bold;">首次使用，先想好邮箱和密码，提前填入这里，注意一定是邮箱，可以是虚构的邮箱</span>）
- PB_API_BASE="web:8090"  #docker配置需要，参考https://stackoverflow.com/questions/70151702/how-to-network-2-separate-docker-containers-to-communicate-with-eachother

**注：上述各服务的申请与开通请参考页面最下方**

### 2、使用docker build image并启动（强烈推荐！）

```commandline
git clone git@github.com:TeamWiseFlow/wiseflow.git
cd wiseflow/client
# 创建.env后
# 首次使用，先想好邮箱和密码，提前填入PB_API_AUTH，注意一定是邮箱，可以是虚构的邮箱
docker compose up -d
```

首次使用build docker image需要大约20~40min，请耐心等待，之后正常使用启动无需等待。

首次使用docker启动后，需要先去管理后台进行配置，此时如果终端出现报错等信息可以先忽略。

**管理配置页面**

浏览器（推荐Chrome）打开 http://127.0.0.1:8090/_/

首次使用会在这里提示Admin注册，填入之前写入.env的邮箱和密码。 <span style="color: red; font-weight: bold;">一定要与env一致</span>

打开管理后台的roleplays表单，在这里可以配置llm的身份信息和关注点，这将影响信息发掘和整理的效果，同时也影响report的生成风格。

roleplays可以配置多个，但每次只会选择更改时间最新且activated为true的。

**roleplay 字段说明：**

- character 以什么身份挖掘线索（这决定了llm的关注点和立场）
- focus 关注什么方面的线索
- focus_type 线索类型
- good_samples1 你希望llm给出的线索描述模式（给两个sample）
- good_samples2 你希望llm给出的线索描述模式（给两个sample）
- bad_samples 规避的线索描述模式
- report_type 报告类型

填好之后保证activated为true，如果你使用docker desktop或者类似有界面的工具，这个时候可以在container中找到 wiseflow/api, 手动运行它就可以了。

或者在命令行中依次执行

```commandline
docker compose down
docker compose up -d
```

**最后，浏览器打开 http://127.0.0.1:8090 起飞！**

关闭客户端可以通过desktop的界面，也可以在命令行中 执行 `docker compose down`

再次启动项目可以在desktop中运行container，也可以在命令行中执行

```commandline
cd wiseflow/client 
docker compose up -d
```

如果希望能够看到终端里面的动态可以执行 `docker compose up` , 注意，如果需要观察详细的程序执行，记得在.env中开启WS_LOG=verbose

### 3、配置本地定时扫描信息源

wiseflow client内置了通用页面解析器，对于大多数新闻类静态页面可以实现较好的信息解析和提取，如果您有复杂信源扫描需求（比如社交网络信息监控等），可以邮件联系我们开通信息订阅服务（35252986@qq.com）。

本地配置信源请首先打开管理后台：http://127.0.0.1:8090/_/ （也可以通过web页面 http://127.0.0.1:8090 下方的 *数据库管理* 链接进入）

打开 **sites表单**

通过这个表单可以指定自定义信源，系统会启动后台定时任务，在本地执行信源扫描、解析和分析。

sites 字段说明：

- url, 信源的url，信源无需给定具体文章页面，给文章列表页面即可，wiseflow client中包含两个通用页面解析器，90%以上的新闻类静态网页都可以很好的获取和解析。
- per_hours, 扫描频率，单位为小时，类型为整数（1~24范围，我们建议扫描频次不要超过一天一次，即设定为24）
- activated, 是否激活。如果关闭则会忽略该信源，关闭后可再次开启。开启和关闭无需重启docker容器，会在下一次定时任务时更新。

wiseflow client自定义信源的扫描调度策略是：每小时启动一次，会先看是否有满足频率要求的指定信源，如果没有的话，会看是否集成了专有爬虫，如果有的话，每24小时会运行一遍专有爬虫。

注意：如果使用sites指定信源，专有爬虫也需要配置在这里。

----------
虽然wiseflow client中包含的两个通用页面解析器可以适用于绝大多数静态页面的解析，但对于实际业务，我们还是建议客户订阅我们的专业信息服务（支持指定信源），或者自写专有爬虫。wiseflow client支持客户自定义专有爬虫的集成。

专有爬虫的集成说明见 backend/scrapers/README.md

配置专有爬虫后，请重新进行docker build。

## 参考：不使用docker启动（适用于开发者）

首先我们依然强烈建议至少使用docker启动前端和pb（数据库），这个build仅需几分钟，image仅74M。

单独build web（含pb）无需编辑.env，直接执行 

```commandline
cd wiseflow/client
docker compose up web
```

之后编辑.env，然后执行

```commandline
cd backend
pip install -U -r requirements.txt
```

我们建议使用python3.10版本，并使用虚拟环境或者conda创建虚拟环境

backend中提供两个脚本

- backend.sh 启动backend后端服务
- tasks.sh 启动信源扫描定时任务

backend.sh 启动后可以通过 http://127.0.0.1:7777/docs 查看API详情，并基于此定制开发

## 参考：各服务注册地址

- 阿里灵积大模型接口：https://dashscope.aliyun.com/
- 火山翻译引擎：https://translate.volcengine.com/api
- embedding模型：https://github.com/netease-youdao/BCEmbedding

（模型下载方案：https://hf-mirror.com/ ）

```bash
pip install -U huggingface_hub
export HF_ENDPOINT=https://hf-mirror.com
# for non-gate model
huggingface-cli download --resume-download --local-dir-use-symlinks False bigscience/bloom-560m --local-dir bloom-560m
# for gate model
huggingface-cli download --token hf_*** --resume-download --local-dir-use-symlinks False meta-llama/Llama-2-7b-hf --local-dir Llama-2-7b-hf
```

使用url直接下载时，将 huggingface.co 直接替换为本站域名hf-mirror.com。使用浏览器或者 wget -c、curl -L、aria2c 等命令行方式即可。
下载需登录的模型需命令行添加 --header hf_*** 参数，token 获取具体参见上文。
