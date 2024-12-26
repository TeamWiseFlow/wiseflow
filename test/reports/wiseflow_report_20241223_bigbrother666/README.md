# wiseflow testing report

2024-12-23

by bigbrother666

## summary

- task number: 4
- sample number: 10
- involved models: ['deepseek-ai/DeepSeek-V2.5', 'Qwen/Qwen2.5-Coder-32B-Instruct', 'Qwen/Qwen2.5-32B-Instruct', 'Qwen/Qwen2.5-14B-Instruct', 'Qwen/Qwen2.5-Coder-7B-Instruct']
- model provider: siliconflow api

## conclusion

Overall, Qwen2.5-32B-Instruct and DeepSeek-V2.5 perform significantly better than other evaluated models.

Comparatively, Qwen2.5-32B-Instruct tends to prioritize extraction accuracy, which may result in information omission; while DeepSeek-V2.5 tends to extract as much information as possible (while maintaining certain precision), which may lead to information redundancy.

Two interesting points:

- Due to its smaller parameter size, Qwen2.5-Coder-7B-Instruct cannot understand the focus requirements well. It tends to extract all available information, but can still maintain stable output format as required by the prompt (comparatively, Qwen2.5-7B-Instruct often fails to follow the instructed output format, and even Qwen2.5-14B-Instruct tends to deviate from the instructed format). Therefore, if you don't mind mixing in excessive irrelevant information, Qwen2.5-Coder-7B-Instruct could be a cost-effective choice;

- DeepSeek-V2.5 performs remarkably well in focus information extraction and relevant link selection, but performs poorly in author and publish date extraction, even worse than Qwen2.5-7B-Instruct. The latter, while performing worse than Qwen2.5-Coder-7B-Instruct in information extraction tasks, excels at author and publish date extraction, so I would recommend using it as a secondary model.

## Detailed Test Results

| sample | DeepSeek-V2.5👍 | Qwen2.5-Coder-32B-Instruct | Qwen2.5-32B-Instruct👍 | Qwen2.5-14B-Instruct | Qwen2.5-Coder-7B-Instruct |
|--------|---------------|---------------------------|---------------------|---------------------|--------------------------|
| ab9447 | 3 | 5 | 6 | 22 | 3 |
| 53e552 | 6 | 9 | 6 | 0 | 4 |
| 8c1617 | 1 | 0 | 1 | 0 | 3 |
| eca076 | 0 | 0 | 0 | 0 | 7 |
| ffffe4 | 0 | 7 | 0 | 3 | 0 |
| 3958ab | 0 | 0 | 0 | 0 | 1 |
| 9c76f8 | 7 | 18 | 14 | 13 | 23 |
| e8c97c | 17 | 8 | 7 | 22 | 56 |
| 29229b | 12 | 11 | 4 | 29 | 14 |
| 407948 | 3 | 14 | 2 | 2 | 5 |
| total | 49 | 72 | 40 | 91 | 116 |
| cost | 0.143 | 0.126 | 0.1099 | 0.0646 | 0 |

- Scores represent the number of times the output deviated from human expectations, including omissions, extraction errors, and hallucinations, so lower scores are better.
- Cost unit is ￥, all evaluations use siliconflow api, according to siliconflow official pricing.

deepseek-ai/DeepSeek-V2.5: ￥1.33 / M Tokens

Qwen/Qwen2.5-Coder-32B-Instruct: ￥1.26 / M Tokens

Qwen/Qwen2.5-32B-Instruct: ￥1.26 / M Tokens

Qwen/Qwen2.5-14B-Instruct: ￥0.7 / M Tokens

Qwen/Qwen2.5-Coder-7B-Instruct: 0 / M Tokens (Limited time free)
