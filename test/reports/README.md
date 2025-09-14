# LLM Selection Test Report For Wiseflow4.2 [Latest]

## test datetime

Sep-12, 2025

## test models

我们广泛选取了siliconflow.cn上 **所有** 输出价格不超过 ￥4/M 的模型，通过 [report_v4x_json/task0](./report_v4x_json/task0) 和 [report_v4x_llm/task1](./report_v4x_llm/task1) 两个任务的测试，过滤掉了表现明显不佳（至少一个样本上输出不符合格式或者结果超差）的模型，最终遴选出如下模型参与多任务测评：

 - ByteDance-Seed/Seed-OSS-36B-Instruct
 - Qwen/Qwen3-32B
 - Qwen/Qwen3-14B
 - Qwen/Qwen3-30B-A3B-Thinking-2507

同时选择 'gpt-5-nano', 'openai/gpt-oss-20b' （均使用由 aihubmix 提供的转接接口）, 作为对比模型。

## test samples & Results

### 1. [report_v4x_json/task0](./report_v4x_json/task0)

简单的潜在客户联系方式结构化提取（中文），多样本，每个样本上含有一条或零条（干扰样本）待提取信息或链接

#### 结果（最优的前三）：

1、Qwen3-32B

2、ByteDance-Seed/Seed-OSS-36B-Instruct

3、Qwen3-14B （等效 openai/gpt-oss-20b）

gpt-5-nano效果不佳


### 2. [report_v4x_json/task1](./report_v4x_json/task1)

简单的门店联系方式结构化提取（中文），单样本，样本上含有多条信息待提取，但不应提取任何链接。

#### 结果（最优的前三）：

1、Qwen3-32B / ByteDance-Seed/Seed-OSS-36B-Instruct （'gpt-5-nano', 'openai/gpt-oss-20b' 等效）

2、Qwen3-14B / Qwen/Qwen3-30B-A3B-Thinking-2507

### 3. [report_v4x_json/task9](./report_v4x_json/task9)

复杂的结构化信息提取（中文）。多样本，每个样本的内容、布局都有很大区别，focuspoint 带有限制信息，schema 含有7条内容， 样本内可能还有相关信息，但不能保证完全符合 schema 和 focuspoint 限制要求。

#### 结果（最优的前三）：

1、ByteDance-Seed/Seed-OSS-36B-Instruct

2、Qwen3-32B（'gpt-5-nano', 'openai/gpt-oss-20b' 等效）

3、Qwen3-14B

**都能按要求结构化提取信息，但都不能按要求只提取“房地产类“拍卖信息**


### 4. [report_v4x_llm/task1](./report_v4x_llm/task1)

简单的信息提取，分角色立场提取（中文）。多样本，每个样本上含有一条或零条（干扰样本）待提取信息或链接。

#### 结果（最优的前三）：

1、ByteDance-Seed/Seed-OSS-36B-Instruct

2、Qwen3-14B

3、Qwen3-32B / Qwen3-30B-A3B-Thinking-2507

'gpt-5-nano', 'openai/gpt-oss-20b' 此测试效果均不佳，gpt-oss-20b甚至不如gpt-5-nano

### 5. [report_v4x_llm/task4](./report_v4x_llm/task4)

客户评论信息提取（中英文混合样本， 英文focuspoint），需要从混乱排版的网页中准确提取指定产品信息的客户评价。
难点在于指定只需要提取SAMSUNG 990 PRO 的评价，但是文本中还包含大量SAMSUNG 990 EVO的评价。

#### 结果（最优的前三）：

1、Qwen3-32B

2、ByteDance-Seed/Seed-OSS-36B-Instruct / Qwen3-30B-A3B-Thinking-2507

3、Qwen3-14B 

openai/gpt-oss-20b 一个样本测试时连通失败。
结果上看本次测试 openai/gpt-oss-20b 和 gpt-5-nano 效果近似，好于 Qwen3-14B 但差于 ByteDance-Seed/Seed-OSS-36B-Instruct

### 6. [report_v4x_llm/task5](./report_v4x_llm/task5)

微信公众号文章有效信息提取（中文），多样本，包括文章列表类型和文章类型，大量样本只含有很多近似但实际不相关的内容。
预期应该从文章列表类型中只挑选出相关 link，从文章中只挑选出相关 info。

#### 结果（最优的前三）：

1、ByteDance-Seed/Seed-OSS-36B-Instruct (openai/gpt-oss-20b 等效)

2、Qwen/Qwen3-30B-A3B-Thinking-2507 （gpt-5-nano 等效）

3、Qwen3-14B 

### 7. [report_v4x_llm/task3](./report_v4x_llm/task3)

从官网中提取产品信息提取（中英文混合样本， 中文focuspoint），需要从各种排版的页面中提取指定类型的产品信息。

#### 结果（最优的前三）：

1、ByteDance-Seed/Seed-OSS-36B-Instruct 

2、Qwen3-14B / Qwen3-32B  (openai/gpt-oss-20b 等效)

3、Qwen/Qwen3-30B-A3B-Thinking-2507 （gpt-5-nano 等效）

在这个样本的测试中，ByteDance-Seed/Seed-OSS-36B-Instruct 可谓“遥遥领先”。

## 历史报告

- [extract info from pics test](./extract_info_from_pics_test_20241222_bigbrother666/README.md) by bigbrother666 2024-12-22
- ~~[wiseflow V0.36 report]() by bigbrother666 2025-01-04~~
- ~~[wiseflow V0.37 report]() by bigbrother666 2025-01-17~~
- ~~[wiseflow V0.38 report]() by bigbrother666 2025-02-07~~
- [GLM_series report](./report_v39_web/GLM_report_0416.md) by bigbrother666 2025-04-16
- [Qwen3 series report](./report_v39_web/Qwen3_report_0502.md) by bigbrother666 2025-05-02
