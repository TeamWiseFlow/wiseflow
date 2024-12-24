# 测试脚本说明

## 网页内容获取和解析

[fetching_for_sample.py](./fetching_for_sample.py)

- 使用前编辑脚本 `sites` 和 `save_dir` 变量，指定要爬取的网站和保存的目录

## 从已解析的网页内容中提取关注内容或相关链接【可同时测试多个模型】

[get_info_test.py](./get_info_test.py)

- 使用前编辑脚本 `sample_dir` 变量，指定要解析的网页内容目录（一般就是 fetching_for_sample.py 中保存的目录，要保证这里有已经解析好的网页内容，至少包含 `text.txt` 文件和 `link_dict.json` 文件）
- 为测试任务创建 关注点说明，可以参考 [reports/wiseflow_report_20241223_bigbrother666/task0/focus_point.json](./reports/wiseflow_report_20241223_bigbrother666/task0/focus_point.json),

    注意：对应不同关注点的 sample文件，需要放入不同的文件夹下，具体结构可以参考 [reports/wiseflow_report_20241223_bigbrother666](./reports/wiseflow_report_20241223_bigbrother666)
- 使用前编辑脚本 `models` 和 `vl_model` 变量，指定要测试的模型

要更改 get_info 的 prompt，请编辑 [prompts.py](./prompts.py), 如果要使用非 openai SDK的数据格式的provider，请编辑 [openai_wrapper.py](./openai_wrapper.py)

# 结果提交与共享

wiseflow 是一个开源项目，希望通过大家共同的贡献，打造“人人可用的信息爬取工具”！

现阶段，**提交测试结果等同于提交项目代码**，同样会被接纳为contributor，甚至受邀参加商业化项目！

测试结果提交请统一放入 [reports](./reports) 目录下，并为单次测试创建子目录，名称为 `{测试内容}_{测试时间}_{测试者}`，例如：

```bash
mkdir -p reports/wiseflow_report_20241223_bigbrother666
```

请将所有测试 sample 和程序运行的原始输出结果一并提交，并在目录下创建 README.md 文件，记录测试内容、测试时间、测试者、测试模型、结论、统计表格等。

最后编辑 [reports/README.md](./reports/README.md) 文件，将测试结果的目录名添加到 index 中，以便于他人查看。
