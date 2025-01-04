# Test Script Documentation

## Web Content Fetching and Parsing

[craw4ai_fetching.py](./craw4ai_fetching.py)

## HTML Content Parsing

[deep_scraper_test.py](./deep_scraper_test.py)

## Visual Large Model Information Extraction

[get_visual_info_for_samples.py](./get_visual_info_for_samples.py)

## Large Model Information Extraction Testing

[get_info_test.py](./get_info_test.py)

    - To create focus point descriptions for test tasks, refer to [reports/wiseflow_report_v036_bigbrother666/task0/focus_point.json](./reports/wiseflow_report_v036_bigbrother666/task0/focus_point.json)

    - To modify the prompt for get_info, edit [prompts.py](./prompts.py)

# Result Submission and Sharing

Wiseflow is an open source project aiming to create an "information crawling tool for everyone" through collective contributions!

At this stage, **submitting test results is equivalent to submitting project code** - you'll be accepted as a contributor and may even be invited to participate in commercial projects!

Test results should be submitted to the [reports](./reports) directory. Create a subdirectory for each test named `{test_content}_{test_date}_{tester}`, for example:

```bash
mkdir -p reports/wiseflow_report_v036_bigbrother666
```

Please submit all test samples and the original output results of the program run, and create a README.md file in the directory to record the test content, test date, tester, test models, conclusions, statistical tables, etc.

Finally, edit the [reports/README.md](./reports/README.md) file, add the directory name of the test result to the index, so that others can view it.
