# wiseflow Custom Parser Instructions

## Overview
wiseflow is committed to processing all pages through a universal process (an intelligent agent driven by large models that can autonomously use web scraping tools).

Currently, we use the popular web scraping framework Crawlee (playwright) for unified management in page acquisition. After practical testing, Crawlee performs well in terms of speed and compatibility, and has a robust task queue management module, so customizations are generally unnecessary for web page acquisition.

For page information parsing, wiseflow uses large models by default, but users can configure custom parsers for specific domains.

## Custom Parser Configuration Instructions

### 1. Scraper Function Definition
The Scraper should be a function (not a class).

### 2. Function Parameters
The function receives two input parameters (passed by the wiseflow framework):
- `html`: This is the rendered page HTML code obtained by wiseflow through Crawlee's playwright_crawler, of type `str`. The scraper can directly use libraries like `bs` and `parsel` for parsing;
- `url`: The URL address of the current page, of type `str` (only for special operations, can be ignored if not needed).

### 3. Function Return Values
The Scraper output is limited to three:

#### 3.1 `article`
The parsed page details, of type `dict`, with the following format:

```python
{
    'author': ..., 
    'publish_date': ..., 
    'content': ...
}
```

- The types of the above values are all required to be `str`, with the date format being `YYYY-MM-DD`, and the screenshot being a **file path**, which can be a relative path to the core directory or an absolute path, with the file type being `png`.

**Note:**
1. `'content'` must be present and not empty, otherwise subsequent extraction cannot be triggered;
2. `'author'` and `'publish_date'` should be included if possible, otherwise wiseflow will automatically use the domain corresponding to the demain and the current date.

#### 3.2 `links`
The links parsed from the corresponding page, the type can be `set` or `dict`:

- If it is a `set`, all will be added to the task queue.
- If it is a `dict`, llm will be called to select URLs worth adding to the task queue (based on your focus point), with the format of the `dict` as follows:

```python
{
    'text': text information corresponding to the external link, 
    'url': url corresponding to the external link
}
```

wiseflow will use this as input to determine the links worth continuing to crawl using llm.

#### 3.3 `infos`
The list of noteworthy information extracted from the corresponding page, of type `list`, with elements being `dict`, in the following format:

```python
{
    'tag': id of the focuspoint, 
    'content': specific info content
}
```

**Note that the id of the focuspoint must match the focus_points table in pb**

### 4. Register Custom Parser
Register in `core/custom_scraper/__init__.py`, for reference:

```python
from .mp import mp_scarper

customer_crawler_map = {'mp.weixin.qq.com': mp_scarper}
```

Note that the key uses the domain name, which can be obtained using `urllib.parse`:

```python
from urllib.parse import urlparse

parsed_url = urlparse("site's url")
domain = parsed_url.netloc
```