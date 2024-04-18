# WiseFlow Client 用户手册

对于普通用户而言，使用WiseFlow客户端非常简便。**如果您是开发者，有二次开发的需要，请进入backend目录、web目录分别查看后端和前端的源代码。**

## 普通用户使用

### 1、参考如下内容创建 `.env `文件 （可以直接编辑 env_sample后再改名）

- PROJECT_DIR="xxxx" #项目缓存文件夹（相对于client文件夹的路径），如果不设定就直接放在repo下面了
- WS_LOG="verbose"  #设定是否开始debug观察，调试阶段建议开始，尤其可以观察到每一步接口调用的原始请求和返回
- LLM_API_BASE： #使用本地大模型推理服务使用（本地加载大模型）的 host:port, 不配置默认走http://localhost:8000
- DASHSCOPE_API_KEY="YOUR_DASHSCOPE_API_KEY" #使用阿里灵积大模型推理服务使用
- ZHIPUAI_API_KEY= #使用智谱大模型接口使用（目前只会调用glm4，model参数没有意义）
- VOLC_KEY='AK|SK' #使用火山云翻译api使用，格式为AK|SK
- EMBEDDING_MODEL_PATH='' #embedding模型的地址，
- RERANKER_MODEL_PATH='' #rerank模型地址
- DEVICE="cuda:0" #配置的话使用GPU，不配置使用CPU。
- PB_API_AUTH='email|password' #pb数据库admin的邮箱和密码（一定是admin的，一定给邮箱）

**注：上述各服务的申请与开通请参考页面最下方**

### 2、强烈建议普通用户


### 3、管理配置页面 —— http://127.0.0.1:8090/_/

#### roleplays 表单

在这里可以配置llm的身份信息和关注点，这将直接决定信息发掘和过滤的效果，可以配置多个，但每次只会选择更改时间最新的且activated为true的。

**更改roleplay需要重启服务（最简单的办法是重启下docker 容器）**

roleplay 字段说明：

- character 以什么身份挖掘线索（这决定了llm的关注点和立场）
- focus 关注什么方面的线索
- focus_type 线索类型
- good_samples1 你希望llm给出的线索描述模式（给两个sample）
- good_samples2 你希望llm给出的线索描述模式（给两个sample）
- bad_samples 规避的线索描述模式
- report_type 报告类型

#### sites 表单

通过这个表单可以指定自定义信源，系统会启动后台定时任务，在本地执行信源爬取、解析和分析。

sites 字段说明：

- url, 信源的url，信源无需给定具体文章页面，给文章列表页面即可，wiseflow client中包含两个通用页面解析器，90%以上的新闻类静态网页都可以很好的获取和解析（我们建议爬取频次不要超过一天一次）。
- per_hours, 爬取频率，单位为小时，类型为整数（1~24范围）
- activated, 是否激活。如果关闭则会忽略该信源，关闭后可再次开启。开启和关闭无需重启docker容器，会在下一次定时任务时更新。

注意：

1、wiseflow client自定义信源的爬取调度策略是：每小时启动一次，会先看是否有满足频率要求的指定信源，

2、虽然wiseflow client中包含的两个通用页面解析器可以适用于绝大多数静态页面的解析，但对于实际业务，我们还是建议客户订阅我们的专业信息推动服务，或者自写专有爬虫。wiseflow client支持客户自定义专有爬虫的集成。

专有爬虫的集成说明见 backend/scrapers/README.md

配置专有爬虫后，请单独进行docker build。

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