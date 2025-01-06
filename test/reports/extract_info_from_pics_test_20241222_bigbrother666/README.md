# extract info from pics test

2024-12-22

by bigbrother666

## test solution


- Used [./vl_pic_test.py](./vl_pic_test.py) to test image information extraction capabilities of vision language models currently available on the siliconflow platform (test samples are images from Chinese webpages, see script for details).

- The main task is to extract text information from images as a supplement when webpage information is insufficient.

- Designed both Chinese and English prompts for testing.

## conclusion

Overall, OpenGVLab/InternVL2-26B performs best when using Chinese prompts.

## Detailed Test Results

| Model | Prompt Language | Missing Characters | Output Not Following Instructions | Recognition Errors | Hallucinations | Total Score | Rating |
|-------|----------------|-------------------|--------------------------|-------------------|----------------|--------------|---------|
| Qwen/Qwen2-VL-72B-Instruct | cn prompt | 2 | 1 | 3 | 0 | 6 | |
| | en prompt | 2 | 1 | 1 | 0 | 4 | 👍 |
| OpenGVLab/InternVL2-26B | cn prompt | 1 | 0 | 2 | 0 | 3 | 👍👍 |
| | en prompt | 0 | 2 | 3 | 0 | 5 | |
| Pro/Qwen/Qwen2-VL-7B-Instruct | cn prompt | 1 | 1 | 2 | 1 | 5 | |
| | en prompt | 0 | 2 | 3 | 0 | 5 | |
| Pro/OpenGVLab/InternVL2-8B | cn prompt | 3 | 2 | 2 | 0 | 7 | |
| | en prompt | 2 | 2 | 4 | 1 | 9 | |
| deepseek-ai/deepseek-vl2 | cn prompt | 1 | 1 | 1 | 1 | 4 | 👍 |
| | en prompt | 3 | 0 | 1 | 4 | 8 | |