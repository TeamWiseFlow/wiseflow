# LLM Selection Test Report For Wiseflow4.2 [Latest]

## Test DateTime

Sep-12, 2025

## Test Models

We extensively selected **all** models from siliconflow.cn with output prices not exceeding ¥4/M. Through testing on [report_v4x_json/task0](./report_v4x_json/task0) and [report_v4x_llm/task1](./report_v4x_llm/task1), we filtered out models that performed significantly poorly (with at least one sample showing non-compliant output format or extremely poor results), and finally selected the following models for multi-task evaluation:

 - ByteDance-Seed/Seed-OSS-36B-Instruct
 - Qwen/Qwen3-32B
 - Qwen/Qwen3-14B
 - Qwen/Qwen3-30B-A3B-Thinking-2507

We also selected 'gpt-5-nano' and 'openai/gpt-oss-20b' (both using the proxy interface provided by aihubmix) as comparison models.

## Test Samples & Results

### 1. [report_v4x_json/task0](./report_v4x_json/task0)

Simple structured extraction of potential customer contact information (Chinese), multiple samples, each sample contains one or zero (interference sample) pieces of information or links to be extracted.

#### Results (Top 3):

1. Qwen3-32B

2. ByteDance-Seed/Seed-OSS-36B-Instruct

3. Qwen3-14B (equivalent to openai/gpt-oss-20b)

gpt-5-nano performed poorly.


### 2. [report_v4x_json/task1](./report_v4x_json/task1)

Simple structured extraction of store contact information (Chinese), single sample, sample contains multiple pieces of information to be extracted, but should not extract any links.

#### Results (Top 3):

1. Qwen3-32B / ByteDance-Seed/Seed-OSS-36B-Instruct ('gpt-5-nano', 'openai/gpt-oss-20b' equivalent)

2. Qwen3-14B / Qwen/Qwen3-30B-A3B-Thinking-2507

### 3. [report_v4x_json/task9](./report_v4x_json/task9)

Complex structured information extraction (Chinese). Multiple samples, each sample has significantly different content and layout, focuspoint contains restriction information, schema contains 7 items, samples may contain relevant information but cannot guarantee complete compliance with schema and focuspoint restriction requirements.

#### Results (Top 3):

1. ByteDance-Seed/Seed-OSS-36B-Instruct

2. Qwen3-32B ('gpt-5-nano', 'openai/gpt-oss-20b' equivalent)

3. Qwen3-14B

**All models could extract information as required, but none could extract only "real estate" auction information as specified.**


### 4. [report_v4x_llm/task1](./report_v4x_llm/task1)

Simple information extraction with role-based perspective extraction (Chinese). Multiple samples, each sample contains one or zero (interference sample) pieces of information or links to be extracted.

#### Results (Top 3):

1. ByteDance-Seed/Seed-OSS-36B-Instruct

2. Qwen3-14B

3. Qwen3-32B / Qwen3-30B-A3B-Thinking-2507

'gpt-5-nano' and 'openai/gpt-oss-20b' both performed poorly in this test, with gpt-oss-20b even worse than gpt-5-nano.

### 5. [report_v4x_llm/task4](./report_v4x_llm/task4)

Customer review information extraction (mixed Chinese-English samples, English focuspoint), requiring accurate extraction of customer reviews for specified product information from chaotically formatted web pages.
The challenge is that only SAMSUNG 990 PRO reviews should be extracted, but the text also contains a large number of SAMSUNG 990 EVO reviews.

#### Results (Top 3):

1. Qwen3-32B

2. ByteDance-Seed/Seed-OSS-36B-Instruct / Qwen3-30B-A3B-Thinking-2507

3. Qwen3-14B 

openai/gpt-oss-20b failed to connect during one sample test.
From the results, openai/gpt-oss-20b and gpt-5-nano performed similarly in this test, better than Qwen3-14B but worse than ByteDance-Seed/Seed-OSS-36B-Instruct.

### 6. [report_v4x_llm/task5](./report_v4x_llm/task5)

WeChat public account article effective information extraction (Chinese), multiple samples, including article list type and article type, with many samples containing only similar but actually irrelevant content.
Expected to select only relevant links from article list types and only relevant info from articles.

#### Results (Top 3):

1. ByteDance-Seed/Seed-OSS-36B-Instruct (equivalent to openai/gpt-oss-20b)

2. Qwen/Qwen3-30B-A3B-Thinking-2507 (equivalent to gpt-5-nano)

3. Qwen3-14B 

### 7. [report_v4x_llm/task3](./report_v4x_llm/task3)

Product information extraction from official websites (mixed Chinese-English samples, Chinese focuspoint), requiring extraction of specified type product information from various formatted pages.

#### Results (Top 3):

1. ByteDance-Seed/Seed-OSS-36B-Instruct 

2. Qwen3-14B / Qwen3-32B (equivalent to openai/gpt-oss-20b)

3. Qwen/Qwen3-30B-A3B-Thinking-2507 (equivalent to gpt-5-nano)

In this sample test, ByteDance-Seed/Seed-OSS-36B-Instruct was "far ahead."

## Historical Reports

- [extract info from pics test](./extract_info_from_pics_test_20241222_bigbrother666/README.md) by bigbrother666 2024-12-22
- ~~[wiseflow V0.36 report]() by bigbrother666 2025-01-04~~
- ~~[wiseflow V0.37 report]() by bigbrother666 2025-01-17~~
- ~~[wiseflow V0.38 report]() by bigbrother666 2025-02-07~~
- [GLM_series report](./report_v39_web/GLM_report_0416.md) by bigbrother666 2025-04-16
- [Qwen3 series report](./report_v39_web/Qwen3_report_0502.md) by bigbrother666 2025-05-02
