# 测试脚本说明

## 网页内容获取和解析

[fetching_test.py](./fetching_test.py)

```
python fetching_test.py -S 'url1,url2...'
```

## html 内容解析

[html2md_test.py](./html2md_test.py)

```
python html2md_test.py -F 'json_file_path' -R 'record save path'
```

## 大模型信息提取测试

[get_info_test.py](./get_info_test.py)

    - 为测试任务创建 关注点说明，可以参考 [reports/wiseflow_report_v036_bigbrother666/task0/focus_point.json](./reports/wiseflow_report_v036_bigbrother666/task0/focus_point.json),

```
python get_info_test.py -D 'sample dir' -I 'include ap'
```

# 结果提交与共享

wiseflow 是一个开源项目，希望通过大家共同的贡献，打造“人人可用的信息爬取工具”！

现阶段，**提交测试结果等同于提交项目代码**，同样会被接纳为contributor，甚至受邀参加商业化项目！

测试结果提交请统一放入 [reports](./reports) 目录下，并为单次测试创建子目录，名称为 `{测试内容}_{测试时间}_{测试者}`，例如：

```bash
mkdir -p reports/wiseflow_report_v036_bigbrother666
```

请将所有测试 sample 和程序运行的原始输出结果一并提交，并在目录下创建 README.md 文件，记录测试内容、测试时间、测试者、测试模型、结论、统计表格等。

最后编辑 [reports/README.md](./reports/README.md) 文件，将测试结果的目录名添加到 index 中，以便于他人查看。
