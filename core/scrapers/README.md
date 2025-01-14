## 配置自定义 Crawl4ai 抓取 config

如果信源需要对应特殊的抓取配置，可以在 `core/scrapers/__init__.py` 中编辑对应的 crawler_config，并在 `custom_fetching_configs` 中注册。

## 解析器（Scraper）

对于从网页内容中提取关注信息这一任务而言，直接把 html 编码送给 llm 并不是一个好主意。在该类型任务中，我们期待 llm 表现的类似人类，侧重点在于内容的理解，而不是 html 的解析。且不说直接送入 html 编码还会造成额外（非常大量）的 token 消耗和处理效率的降低。

将 html 转为易于意思理解的 markdown 是目前领域内比较通用的做法，这方面 Crawl4ai 提供了比较成熟的解决方案。

然而这指的是一般情况，天下没有万能的招数，对于某些特定的信源，Crawl4ai 的默认解析器并不能很好的工作，比如微信公众号文章，这个时候我们就需要为信源自定义解析器。

简单的说，解析器的作用就是将 html 编码转为 markdown 文本，并在这个过程中尽量过滤不必要信息（因为后一步是通过 llm 进行提炼，所以这一步要求不高），但也尽可能的保留 html 版面布局信息（这很重要）。

### deep_scraper

我们进一步发现，直接将 markdown 全文送入 llm 解析也存在缺陷。

我在这里仅举一个例子：

*很多网站喜欢在文章页面底部或者侧边栏加入推荐阅读板块，如果说这些推荐阅读只是链接列表还好，但事实上，很多时候他们还包括内容简介，这些简介的长度并不短，甚至有可能跟页面主体正文长度相当。这个时候如果我们将 markdown 整体扔给 llm，就会发现很难为llm 指定明确的工作策略——如果直接舍弃这些推荐阅读内容（先不说很难指定清晰的舍弃策略），但我们不能保证这里面不包含关注点内容；而如果保留这些内容，那么很可能 llm 就无法聚焦该页面的核心内容。或者 llm 会从这些简介中进行信息提取，但是这些简介对应额外的链接，这些后续的链接也会在后面进行爬取，这就可能带来提取出大量重复信息的情况。*

事实上，这里我们需要做的工作是分块，这有点类似 RAG 系统中的 chunk ，但不同的是，这里我们不需要考虑 chunk 的粒度，而是需要考虑页面布局的粒度。因为我们面对的是 html 页面，而不是 pdf、word……

这一点很重要，我们需要按 html 的页面布局进行分块，而不是按语义逻辑分块！因为这影响了后续我们如何判断对不同的块采用合同提取策略。这也就是 wiseflow 为何不使用已有的文档智能工具，而是自写了 deep_scraper 的原因。

当然，另一个选择是直接使用视觉大模型进行 layout 的识别，但实践中我们也发现，这需要能够获取不受干扰的网页截图，但这个操作会极大增加系统复杂度以及降低处理速度，且效果并不稳定（比如对于页面弹窗的处理……）。

另一个不使用文档智能和视觉大模型的原因，是因为相比于 pdf、word 这种完全的非结构数据， html 编码本身就已经包含了全部 layout 信息，转化为 markdown 的过程实际上也保留了这些信息（通过\n # 这些符号），所以直接通过一定的规则对 markdown 进行分块并分别处理是可行的。

这就是 wiseflow deep_scraper 的主要功能，归纳起来：1、按布局信息对markdown进行分块；2、分析每个块的类型，并按不同策略进行预处理，便于最终 llm 的提取。

### 注册自定义解析器

wiseflow 的默认工作流程是： 

*crawl4ai 获取 html，并初步转化为raw_markdown（此过程应用默认的 config） --> deep_scraper 进行分块处理 --> 分块后的内容 送入 llm 进行信息提取。*

如前所言，如果需要为特定信源配置特殊的 crawl4ai 获取策略（包括 raw_markdown 的转化策略），可以在 `core/scrapers/__init__.py` 中注册自定义的crawler_config；

同时也可以为特定信源配置自定义的 scraper，自定义 scraper 的输入为crawl4ai的fetching_result，输出为将要被送入 llm 进行分析的链接字典和文本块列表。使用自定义 scraper 时，wiseflow 的处理流程为：

*crawl4ai 获取 html，并初步转化为raw_markdown（此过程应用默认的 config或指定 config） --> 自定义 scraper 进行分块处理 --> 分块后的内容 送入 llm 进行信息提取。*

自定义 scraper 可以内部调用deep_scraper作为后处理流程（如mp_scraper），也可以完全自定义全部流程。

scraper 输入的 fetch_result 为一个 dict，格式如下：








输出为 ScraperResultData，包含 url、content、links、images 四个字段。

在 `core/scrapers/__init__.py` 中注册，参考：

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