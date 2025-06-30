# Test Script Documentation

## Web Content Fetching and Parsing

[fetching_test.py](./fetching_test.py)

```
python fetching_test.py -S 'url1,url2...'
```

## HTML Content Parsing

[html2md_test.py](./html2md_test.py)

```
python html2md_test.py -F 'json_file_path' -R 'record save path'
```

## Large Model Information Extraction Testing

[get_info_test.py](./get_info_test.py)

    - To create focus point descriptions for test tasks, refer to [reports/wiseflow_report_v036_bigbrother666/task0/focus_point.json](./reports/wiseflow_report_v036_bigbrother666/task0/focus_point.json)

```
python get_info_test.py -D 'sample dir' -I 'include ap'
```

*-I whether to test LLM extraction of author and publish date*

# Result Submission and Sharing

Wiseflow is an open source project aiming to create an "information crawling tool for everyone" through collective contributions!

At this stage, **submitting test results is equivalent to submitting project code** - you'll be accepted as a contributor and may even be invited to participate in commercial projects!

Test results should be submitted to the [reports](./reports) directory. Create a subdirectory for each test named `{test_content}_{test_date}_{tester}`, for example:

```bash
mkdir -p reports/wiseflow_report_v036_bigbrother666
```

Please submit all test samples and the original output results of the program run, and create a README.md file in the directory to record the test content, test date, tester, test models, conclusions, statistical tables, etc.

Finally, edit the [reports/README.md](./reports/README.md) file, add the directory name of the test result to the index, so that others can view it.
