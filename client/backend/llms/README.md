## 使用阿里灵积提供的API接口服务

export DASHSCOPE_API_KEY=

```python
from llms.dashscope_wrapper import dashscope_llm

result = dashscope_llm([{'role': 'system', 'content': '''}, {'role': 'user', 'content': '''}], 'qwen-72b-chat',
                       logger=logger)
```

## 使用智谱提供的API接口服务（暂时只支持glm4）

export ZHIPUAI_API_KEY=

```python
from llms.zhipu_wrapper import zhipuai_llm

result = zhipuai_llm([{'role': 'system', 'content': ''}, {'role': 'user', 'content': ''}], logger=logger)
```

## 对于本地部署模型的支持

**注意：requirements.txt中并不包含lmdeploy需要的依赖，如果使用的话，需要先额外安装**

目前使用internLM提供的本地模型部署加速框架，具体参考： https://github.com/InternLM/lmdeploy

这里提供了qwen1.5-7b的部署脚本供参考

【暂时使用这个wrapper不能使用model参数，实际上也不起作用，使用哪个模型由本地运行的服务决定】

```python
from llms.lmdeploy_wrapper import lmdeploy_llm

result = lmdeploy_llm([{'role': 'system', 'content': ''}, {'role': 'user', 'content': ''}], logger=logger)
```

**注意：使用本地LLM，需要先设置LLM的本地服务地址，可以通过环境变量设置**

`export LLM_API_BASE=http://127.0.0.1:6003`  (不设置默认值为http://127.0.0.1:6003）


## message格式（openAI API格式)

以上wrapper都使用同一套message格式，如下：

[{"role":str, "content":str},{"role":str, "content":str},...]

其中"role"有如下几种：
- "user"：用户
- "assistant"：助手（AI模型生成的回复）
- "function"：函数（用户调用的函数）
- "system"：对话头（AI模型在本轮对话扮演的角色，或者其他meta信息）

另外每条message还有两个可选键：
- "function_call"：用户调用的函数的信息，包括函数名和参数
- "name"：函数的名字（用于函数回复）

wrapper会直接返回回复的str，目前版本用不到function_call, 所以wrapper暂时也没集成，下一个版本可能会根据需要加上，细节可以参考如下：

**备注：**
- function_call可选项用来表示assistant希望调用的工具（所以它应该出现在AI的回复中），它的内容是一个字典，包含name和arguments两个键，其中arguments是一个json字符串，包含函数的参数。
- 而role为function的message代表tool执行后的结果，它包含可选键值name，代表函数的名字，content，代表函数的返回值（json字符串）。
- 更多详情参考openai api cookbook：https://beta.openai.com/docs/developer-tools/api-cookbook
