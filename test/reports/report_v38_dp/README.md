# wiseflow testing report

2025-02-7

by bigbrother666

## summary

- task number: 3
- sample number: 9
- Benchmark model: DeepSeek-R1-Distill-Qwen-32B/DeepSeek-V3
- involved models: [DeepSeek-R1-Distill-Qwen-7B', 'DeepSeek-R1-Distill-Qwen-14B', 'DeepSeek-R1-Distill-Llama-8B', 'DeepSeek-R1']
- model provider: siliconflow api/Deepseek Official Platform

## conclusion

Based on the test results from the samples, the DeepSeek series (including the distillation series based on Qwen2.5) does not exhibit a significant performance improvement over the Qwen2.5 14B~72B series. However, the inference time has increased substantially (by up to 100 times!), accompanied by a slight increase in hallucination probability.  

The suspected reason for this behavior is that the information extraction tasks required by WiseFlow do not necessitate complex reasoning processes. However, the increased complexity in reasoning significantly prolongs inference time while also introducing new possibilities for hallucinations.

## Detailed Test Results

pls check
[task2](./task2)
[task3](./task3)
[task4](./task4)
