# 配置自定义 Crawl4ai 抓取 config

如果信源需要对应特殊的抓取配置，可以在 `core/scrapers/__init__.py` 中编辑对应的 crawler_config，并在 `custom_fetching_configs` 中注册。

# 解析器（Scraper）

对于从网页内容中提取关注信息这一任务而言，直接把 html 编码送给 llm 并不是一个好主意，这会极大的增加提取任务的复杂度，引入更多干扰，并且产生额外（非常大量）的 token 消耗和处理效率的降低。

将 html 转为易于意思理解的 markdown 是目前领域内比较通用的做法，这方面 Crawl4ai 提供了比较成熟的解决方案。

然而这指的是一般情况，天下没有万能的招数，对于某些特定的信源，Crawl4ai 的默认解析器并不能很好的工作，比如微信公众号文章，这个时候我们就需要为信源自定义解析器。

简单的说，解析器的作用就是将 html 编码转为 markdown 文本，并在这个过程中尽量过滤不必要信息（因为后一步是通过 llm 进行提炼，所以这一步要求不高），但也尽可能的保留 html 版面布局信息（这很重要）。

你并不需要通过解析器完成最终的信息提取，这个工作最终还是会使用 llm 完成——甚至在这之前我们还有一个被称为pre-process的步骤，它的主要功能是将待处理的文章 markdown 合理切块并将 url 和图片等进行合理的转化，事实上，这个模块是本项目的一大创新点——解析器只需要提供适合 pre-process 的 markdown(我们称为 raw_markdown)和有价值的图片列表即可。

## 自定义解析器

scraper 输入的 fetch_result 为一个 dict 或者是 crawl4ai 的 CrawlResult 对象，它包含如下字段：

- url: str, 网页的 url
- html: str, 网页的 html 编码
- cleaned_html: str, 经过清洗的 html 编码
- markdown: str, 经过清洗的 markdown 编码
- media: dict, 包含图片、视频、音频等媒体信息
- metadata: dict, 包含网页的元数据，如标题、作者、发布时间等

scraper 的输出为 ScraperResultData，具体见 `core/scrapers/scraper_data.py`。

## 注册自定义解析器

编写好 scraper 后，在 `core/scrapers/__init__.py` 中注册，参考：

```python
from .mp import mp_scarper

customer_scrapers = {'mp.weixin.qq.com': mp_scarper}
```

注意键使用域名，可以使用 `urllib.parse` 获取：


```python
from urllib.parse import urlparse

parsed_url = urlparse("site's url")
domain = parsed_url.netloc
```