# Test Script Documentation

## Web Content Fetching and Parsing

[fetching_for_sample.py](./fetching_for_sample.py)

- Before using, edit the `sites` and `save_dir` variables in the script to specify target websites and save directory

## Extract Focus Content or Related Links from Parsed Web Content [Multiple Models Can Be Tested Simultaneously]

[get_info_test.py](./get_info_test.py)

- Before using, edit the `sample_dir` variable in the script to specify the directory of parsed web content (generally the directory saved by fetching_for_sample.py, which must contain parsed web content including at least `text.txt` file and `link_dict.json` file)
- Create focus point descriptions for test tasks, refer to [reports/wiseflow_report_20241223_bigbrother666/task0/focus_point.json](./reports/wiseflow_report_20241223_bigbrother666/task0/focus_point.json)

    Note: Sample files for different focus points need to be placed in different folders, refer to the structure in [reports/wiseflow_report_20241223_bigbrother666](./reports/wiseflow_report_20241223_bigbrother666)
- Before using, edit the `models` and `vl_model` variables in the script to specify models to test

To modify get_info prompts, edit [prompts.py](./prompts.py). For providers not using OpenAI SDK data format, edit [openai_wrapper.py](./openai_wrapper.py)

# Result Submission and Sharing

Wiseflow is an open source project aiming to create an "information crawling tool for everyone" through collective contributions!

At this stage, **submitting test results is equivalent to submitting project code** - you'll be accepted as a contributor and may even be invited to participate in commercial projects!

Test results should be submitted to the [reports](./reports) directory. Create a subdirectory for each test named `{test_content}_{test_date}_{tester}`, for example:

```bash
mkdir -p reports/wiseflow_report_20241223_bigbrother666
```

Please submit all test samples and the original output results of the program run, and create a README.md file in the directory to record the test content, test date, tester, test models, conclusions, statistical tables, etc.

Finally, edit the [reports/README.md](./reports/README.md) file, add the directory name of the test result to the index, so that others can view it.
