# wiseflow testing report

2025-01-17

by bigbrother666

## summary

- task number: 4
- sample number: 8
- Benchmark model: Qwen2.5-72B-Instruct
- involved models: ['Qwen/Qwen2.5-7B-Instruct', 'Qwen/Qwen2.5-14B-Instruct', 'Qwen/Qwen2.5-32B-Instruct', 'deepseek-ai/DeepSeek-V2.5']
- model provider: siliconflow api

## conclusion

- by the new method, 7b size model can achieve similar performance as 32b size model in the links part filtering task.

## Detailed Test Results

| sample | Qwen2.5-14B-Instruct 👍 | Qwen2.5-32B-Instruct| DeepSeek-V2.5| Qwen2.5-7B-Instruct |
|--------|---------------------|---------------------|-----------------|--------------------------|
| **total diff from benchmark in all samples** | **24** | **26** | **58** | **38** |

**note**

Qwen2.5-7B-Instruct model can achieve significant performance improvement by increasing the batch size of single processing, therefore, in V0.3.7 version, we increased the batch size of link processing and reintroduced the concept of Secondary Model, with Qwen2.5-7B-Instruct as the default recommendation.

siliconflow official pricing:

    deepseek-ai/DeepSeek-V2.5: ￥1.33 / M Tokens

    Qwen/Qwen2.5-32B-Instruct: ￥1.26 / M Tokens

    Qwen/Qwen2.5-14B-Instruct: ￥0.7 / M Tokens

    Qwen/Qwen2.5-72B-Instruct: ￥4.13 / M Tokens