# wiseflow testing report

2025-01-04

by bigbrother666

## summary

- task number: 4
- sample number: 6
- involved models: ['Qwen/Qwen2.5-14B-Instruct', 'Qwen/Qwen2.5-32B-Instruct', 'deepseek-ai/DeepSeek-V2.5', 'Qwen/Qwen2.5-72B-Instruct']
- model provider: siliconflow api

## conclusion

- If your source pages are relatively simple with small amounts of information per page, considering cost and time (mainly time), Qwen2.5-32B-Instruct is recommended

    *Although Qwen2.5-32B-Instruct appears to have high total deductions, this mainly occurs in list selection. For pure article content extraction, its performance is very good, even better than DeepSeek-V2.5*

- If your source pages contain more links, have complex layouts, and you don't want to miss any information, DeepSeek-V2.5 is recommended

## Detailed Test Results

| sample | Qwen2.5-14B-Instruct | Qwen2.5-32B-Instruct👍 | DeepSeek-V2.5👍 | Qwen2.5-72B-Instruct |
|--------|---------------------|---------------------|-----------------|--------------------------|
| ab9447 | 3 | 1 | 2 | 2.5 |
| 775d04 | 2 | 0.5 | 2 | 1.5 |
| 348a2f | 1 | 0 | 1 | 0 |
| ae2d03 | 14 | 17.5 | 8 | 13 |
| df9e89 | 10 | 11 | 3 | 8 |
| e78068 | 2.5 | 0.5 | 1.5 | 2.5 |
| **total** | **32.5** | **30.5** | **16.5** | **27.5** |
| **cost(￥)** | **0.0221** | **0.04** | **0.0474** | **0.1334** |

- Scores represent the number of times the output deviated from human expectations, including omissions, extraction errors, and not_so_good
- for omissions and errors, one time is one point; for not_so_good, one time is 0.5 point; lower scores mean better.
- Cost unit is ￥, all evaluations use siliconflow api, according to siliconflow official pricing.

    deepseek-ai/DeepSeek-V2.5: ￥1.33 / M Tokens

    Qwen/Qwen2.5-32B-Instruct: ￥1.26 / M Tokens

    Qwen/Qwen2.5-14B-Instruct: ￥0.7 / M Tokens

    Qwen/Qwen2.5-72B-Instruct: ￥4.13 / M Tokens

**Additionally, during testing we found that models below 14B parameters performed poorly, so they were not included in this test report.**