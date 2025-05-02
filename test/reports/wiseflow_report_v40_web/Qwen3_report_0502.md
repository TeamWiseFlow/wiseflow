# wiseflow testing report

2025-05-02

by bigbrother666


On April 30, 2025, Alibab released the new Qwen3 series...

Full test on the latest real wiseflow samples... and with 'GLM-4-32B-0414' and DeepSeek-R1-Distill-Qwen-14B as the competitor.


## summary

- task number: 5
- sample number: 9
- involved models: ['Qwen/Qwen3-14B', 'Qwen/Qwen3-30B-A3B', 'THUDM/GLM-4-32B-0414', 'DeepSeek-R1-Distill-Qwen-14B']
- model provider: siliconflow api

* I don't use models expensive than GLM-4-32B-0414 for the following tow resons:

    - ￥1.89/M Tokens price is not feasible for mass use；
    - We also do not see more expensive models such as Qwen/Qwen3-32B and Qwen/Qwen3-235B-A22B have significantly better performance on wiseflow tasks, see: 
    [task1](./task1)
    [task2](./task2)
    [task3](./task3)

## conclusion

|   | Qwen/Qwen3-14B | Qwen/Qwen3-30B-A3B | THUDM/GLM-4-32B-0414 | DeepSeek-R1-Distill-Qwen-14B |
|--------|--------------|--------------------|-----------------|------------------|
| not good at get link task |40 | 49| 34 | 48 |
| not good at get info task |1 | 1| 5| 7 |
| total cost for test | 0.2937| 0.4331| 0.8419| ---- |
| speed | normal | low | super-fast | low |


## Detailed Test Results

pls check
[task4](./task4)
[task7](./task7)
[task8](./task8)
[task9](./task9)
[task10](./task10)

price reference:

https://cloud.siliconflow.cn/models
