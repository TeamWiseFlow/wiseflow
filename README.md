# 📈 首席情报官（Wiseflow）

**首席情报官**（Wiseflow）是一个敏捷的信息挖掘工具，可以从社交平台消息、微信公众号、群聊等各种信息源中提炼简洁的讯息，自动做标签归类并上传数据库。让你轻松应对信息过载，精准掌握你最关心的内容。

## 🌟 功能特色

- 🚀 **原生 LLM 应用**  
  我们精心选择了最适合的 7B~9B 开源模型，最大化降低使用成本，且利于数据敏感用户随时切换到本地部署模式。

- 🌱 **轻量化设计**  
  没有使用任何向量模型，系统开销很小，无需 GPU，适合任何硬件环境。

- 🗃️ **智能信息提取和分类**  
  从各种信息源中自动提取信息，并根据用户关注点进行标签化和分类管理。

- 🌍 **实时动态知识库**  
  能够与现有的 RAG 类项目整合，作为动态知识库提升知识管理效率。

- 📦 **流行的 Pocketbase 数据库**  
  数据库和界面使用 Pocketbase，不管是直接用 Web 阅读，还是通过 Go 工具读取，都很方便。

## 🔄 对比分析

| 特点           | 首席情报官（Wiseflow）  | Markdown_crawler  | firecrawler | RAG 类项目       |
| -------------- | ----------------------- | ----------------- | ----------- | ---------------- |
| **信息提取**   | ✅ 高效                 | ❌ 限制于 Markdown | ❌ 仅网页   | ⚠️ 提取后处理    |
| **信息分类**   | ✅ 自动                 | ❌ 手动           | ❌ 手动     | ⚠️ 依赖外部工具  |
| **模型依赖**   | ✅ 7B~9B 开源模型       | ❌ 无模型         | ❌ 无模型   | ✅ 向量模型      |
| **硬件需求**   | ✅ 无需 GPU             | ✅ 无需 GPU       | ✅ 无需 GPU | ⚠️ 视具体实现而定 |
| **可整合性**   | ✅ 动态知识库           | ❌ 低             | ❌ 低       | ✅ 高            |

## 📥 安装与使用

1. **克隆代码仓库**

    ```bash
    git clone https://github.com/your-username/wiseflow.git
    cd wiseflow
    ```

2. **安装依赖**

    ```bash
    pip install -r requirements.txt
    ```

3. **配置**

    在 `config.yaml` 中配置你的信息源和关注点。

4. **启动服务**

    ```bash
    python main.py
    ```

5. **访问 Web 界面**

    打开浏览器，访问 `http://localhost:8000`。

## 📚 文档与支持

- [使用文档](docs/usage.md)
- [开发者指南](docs/developer.md)
- [常见问题](docs/faq.md)

## 🤝 贡献指南

欢迎对项目进行贡献！请阅读 [贡献指南](CONTRIBUTING.md) 以了解详细信息。

## 🛡️ 许可协议

本项目基于 [Apach2.0](LICENSE) 开源。

商用以及定制合作，请联系 Email：35252986@qq.com 

（商用客户请联系我们报备登记，产品承诺永远免费。）

（对于定制客户，我们会针对您的信源和数据情况，提供专有解析器开发、信息提取和分类策略优化、llm模型微调以及私有化部署服务）

## 📬 联系方式

有任何问题或建议，欢迎通过 [issue](https://github.com/your-username/wiseflow/issues) 与我们联系。


## change log

【2024.5.8】增加对openai SDK的支持，现在可以通过调用llms.openai_wrapper使用所有兼容openai SDK的大模型服务，具体见 [client/backend/llms/README.md](client/backend/llms/README.md)


## getting started

首席情报官提供了开箱即用的本地客户端，对于没有二次开发需求的用户可以通过如下简单五个步骤即刻起飞！

1、克隆代码仓

```commandline
git clone git@github.com:TeamWiseFlow/wiseflow.git
cd wiseflow/client
```

4、参考  /client/env_sample 编辑.env文件;

5、运行 `docker compose up -d` 启动（第一次需要build image，时间较长）


# Citation

如果您在相关工作中参考或引用了本项目的部分或全部，请注明如下信息：

```
Author：Wiseflow Team
https://openi.pcl.ac.cn/wiseflow/wiseflow
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```
# After many comparisons, we recommend the following model for the two tasks of this project (combining effectiveness, speed, and cost performance).
# At the same time, we recommend the siliconflow platform, which can provide online reasoning services for the following two models at a more favorable price
# The siliconflow platform is compatible with openai sdk, which makes the program simple
# Therefore, unless you have experimented and found that there are better options for your data, it is not recommended to change the following two parameters
#  (although you have the right to make any changes at any time).