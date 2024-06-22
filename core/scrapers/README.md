We provide a general page parser that can intelligently retrieve article lists from sources. For each article URL, it first attempts to use `gne` for parsing, and if that fails, it will try using `llm`.

This solution allows scanning and extracting information from most general news and portal sources.

**However, we strongly recommend that users develop custom parsers for specific sources tailored to their actual business scenarios for more ideal and efficient scanning.**

We also provide a parser specifically for WeChat public articles (mp.weixin.qq.com).

**If you are willing to contribute your custom source-specific parsers to this repository, we would greatly appreciate it!**

## Custom Source Parser Development Specifications

### Specifications

**Remember It should be an asynchronous function**

1. **The parser should be able to intelligently distinguish between article list pages and article detail pages.**
2. **The parser's input parameters should only include `url` and `logger`:**
   - `url` is the complete address of the source (type `str`).
   - `logger` is the logging object (please do not configure a separate logger for your custom source parser).
3. **The parser's output should include `flag` and `result`, formatted as `tuple[int, Union[set, dict]]`:**
   - If the `url` is an article list page, `flag` returns `1`, and `result` returns a tuple of all article page URLs (`set`).
   - If the `url` is an article page, `flag` returns `11`, and `result` returns all article details (`dict`), in the following format:

     ```python
     {'url': str, 'title': str, 'author': str, 'publish_time': str, 'content': str, 'abstract': str, 'images': [str]}
     ```

     _Note: `title` and `content` cannot be empty._

     **Note: `publish_time` should be in the format `"%Y%m%d"` (date only, no `-`). If the scraper cannot fetch it, use the current date.**

   - If parsing fails, `flag` returns `0`, and `result` returns an empty dictionary `{}`.

     _`pipeline` will try other parsing solutions (if any) upon receiving `flag` 0._

   - If page retrieval fails (e.g., network issues), `flag` returns `-7`, and `result` returns an empty dictionary `{}`.

     _`pipeline` will not attempt to parse again in the same process upon receiving `flag` -7._

### Registration

After writing your scraper, place the scraper program in this folder and register the scraper in `scraper_map` under `__init__.py`, similar to:

```python
{'domain': 'crawler def name'}
```

It is recommended to use urllib.parse to get the domain:

```python
from urllib.parse import urlparse

parsed_url = urlparse("site's url")
domain = parsed_url.netloc
```