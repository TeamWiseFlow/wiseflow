# Configure Custom Crawl4ai Fetching Config

If a source requires special fetching configuration, you can edit the corresponding crawler_config in `core/scrapers/__init__.py` and register it in `custom_fetching_configs`.

# Scraper

For the task of extracting focused information from web content, directly feeding HTML code to LLM is not a good idea. This would greatly increase the complexity of extraction, introduce more interference, and result in additional (very large) token consumption and reduced processing efficiency.

Converting HTML to markdown that is easy to understand semantically is a common practice in the field, and Crawl4ai provides a relatively mature solution for this.

However, this refers to general cases. There is no one-size-fits-all solution. For certain specific sources, Crawl4ai's default parser may not work well, such as WeChat public account articles. In these cases, we need to customize scrapers for the sources.

Simply put, the scraper's role is to convert HTML code to markdown text, filtering out unnecessary information during this process (since the next step is refinement through LLM, requirements here are not high), while preserving HTML layout information as much as possible (this is important).

You don't need to complete the final information extraction through the scraper. This work will ultimately be done using LLM - in fact, before that we have a step called pre-process, whose main function is to reasonably segment the article markdown and properly transform URLs and images. In fact, this module is a major innovation point of this project - the scraper only needs to provide raw_markdown suitable for pre-process and a list of valuable images.

## Custom Scraper

The fetch_result input to the scraper is either a dict or a Crawl4ai CrawlResult object containing the following fields:

- url: str, the webpage URL
- html: str, the webpage HTML code
- cleaned_html: str, cleaned HTML code
- markdown: str, cleaned markdown code
- media: dict, contains media information like images, videos, audio etc.
- metadata: dict, contains webpage metadata like title, author, publish time etc.

The scraper output is ScraperResultData, see details in `core/scrapers/scraper_data.py`.

## Register Custom Scraper

After writing the scraper, register it in `core/scrapers/__init__.py`, for example:

```python
from .mp import mp_scraper

custom_scrapers = {'mp.weixin.qq.com': mp_scraper}
```

Note that the key uses the domain name, which can be obtained using `urllib.parse`:

```python
from urllib.parse import urlparse

parsed_url = urlparse("site's url")
domain = parsed_url.netloc
```