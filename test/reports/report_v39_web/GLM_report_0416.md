# wiseflow testing report

2025-04-16

by bigbrother666


On April 14, 2025, Zhipu released the new Z series inference model and glm-4 0414 series models, and simultaneously opened source the corresponding 32b and 9b version models. On the same day, siliconflow launched the MaaS service for these open-source models, and we tested their performance on the three types of tasks involved in wiseflow. After comparative testing, we can confirm:

- The glm-4 0414 full series has made significant improvements over previous versions and is now very suitable for various types of wiseflow tasks. [Interesting observation, although glm-4 0414 is not an inference model, it may have a self-thinking process during the output due to the training data of the Z series. This has both pros and cons. The downside is that its instruction following and format output capabilities may not be as good as other models of the same scale...]

- The glm-z1-flash model also performs well on various types of wiseflow tasks, but the larger-scale glm-z1-air and glm-z1-airx series (the main difference between the two is output speed) often confuse the order of the built-in <think> tag and the final result wrapping tag required by the wiseflow system prompt, leading to parsing failure. However, this does not mean that these two models are lacking in capability. Compared to the open-source versions GLM-Z1-32B-0414 and GLM-Z1-9B-0414 provided by siliconflow, the final effect is actually very good because the think content can be separated alone;

- However,  glm-z1-flash model does not perform well on source and publish_date extraction tasks, and even occasionally has hallucinations.

- The glm-z1-air on the bigmodel platform runs too slowly...

- The open-source GLM-Z1-Rumination-32B-0414 (also known as the "Rumination Model") is more skilled at task planning and tool invocation (Agent) and is not suitable for the extraction and summarization tasks involved in wiseflow;

- In fact, both the current Z1 and the GLM-4 0414 series are inclined to directly present the final result, rather than the specific XML tagging method that developers have become accustomed to, which is actually very necessary as it can greatly enhance the lower limit of guarantee.

Based on the above observations, we ultimately excluded models that are obviously unsuitable for wiseflow's business, and the performance of the other models is as follows:


## summary

- task number: 3
- sample number: 9
- involved models: ['glm-z1-flash', 'glm-4-flash-250414', 'glm-4-air-250414', 'GLM-Z1-32B-0414', 'GLM-4-32B-0414', 'GLM-Z1-9B-0414', 'GLM-4-9B-0414']
- model provider: bigmodel.cn/siliconflow api

## conclusion



|  task/price | glm-z1-flash | glm-4-flash-250414 | glm-4-air-250414 | GLM-Z1-32B-0414 | GLM-4-32B-0414 | GLM-Z1-9B-0414 | GLM-4-9B-0414 |
|--------|--------------|--------------------|-----------------|------------------|-----------------|-----------------|-----------------|
| recognize publish source and date | 6.5 | 6.5 | 7 | 7 | 7 | 6 | 6 |
| find related links | 7 | 8 | 7 | 9 | 7 | 8 | 8 |
| summarize the content | 7.5 | 6 | 8 | 7.5 | 9 | 8 | 8 |
| price(k tokens) | 0 | 0 | 0.0005 | 0.0005 | 0.0005 | 0 | 0 |

*number represents the number of times the answer is similar to a human answer, and if a certain answer is very experienced, an additional 0.5 is added.*

## Detailed Test Results

pls check
[task2](./wiseflow_report_v038_dp_bigbrother666/task2)
[task3](./wiseflow_report_v038_dp_bigbrother666/task3)
[task4](./wiseflow_report_v038_dp_bigbrother666/task4)

price reference:

https://www.bigmodel.cn/usercenter/corporateequity

https://cloud.siliconflow.cn/models?mfs=THUDM
