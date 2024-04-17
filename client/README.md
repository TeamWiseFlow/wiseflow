# 用法

### 1、参考如下内容创建 `.env `文件 （可以直接编辑 env_sample后再改名）

- PROJECT_DIR="AWtest" #项目缓存文件夹（相对于repo的路径），如果不设定就直接放在repo下面了
- WS_LOG="verbose"  #设定是否开始debug观察，调试阶段建议开始，尤其可以观察到每一步接口调用的原始请求和返回
- LLM_API_BASE： #使用本地大模型推理服务使用（本地加载大模型）的 host:port, 不配置默认走http://localhost:8000
- DASHSCOPE_API_KEY="YOUR_DASHSCOPE_API_KEY" #使用阿里灵积大模型推理服务使用
- ZHIPUAI_API_KEY= #使用智谱大模型接口使用（目前只会调用glm4，model参数没有意义）
- VOLC_KEY='AK|SK' #使用火山云翻译api使用，格式为AK|SK
- EMBEDDING_MODEL_PATH='' #embedding模型的地址，
- RERANKER_MODEL_PATH='' #rerank模型地址
- DEVICE="cuda:0" #配置的话使用GPU，不配置使用CPU。
- PB_API_AUTH='email|password' #pb数据库admin的邮箱和密码（一定是admin的，一定给邮箱）

### 3、编辑 config.ini 文件 （可以直接修改这个目录下面的 config.ini)

- character 以什么身份挖掘线索（这决定了llm的关注点和立场）
- focus 关注什么方面的线索
- focus_type 线索类型
- good_samples1 你希望llm给出的线索描述模式（给两个sample）
- good_samples2 你希望llm给出的线索描述模式（给两个sample）
- bad_samples 规避的线索描述模式
- report_type 报告类型

### 4、编辑 sites.txt 文件

这个文件指定了需要本地执行的监控的信源，一行一个网址，支持随时更改，每次执行任务前会读取最新的。

如果你只爬取配置了专有爬虫的信源的话，可以直接编辑scrapers/__init__.py 中的scraper_map，这里都留空就好

专有爬虫的说明见 backend/scrapers/README.md

**注：虽然wiseflow client配置了通用爬虫，对于新闻类静态网页有一定的爬取和解析效果，但我们还是强烈建议使用我们的数据订阅服务或者自写专业爬虫。**

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