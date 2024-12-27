# wiseflow 自定义解析器说明

## 概述

wiseflow 致力于利用大模型的理解和分析能力自动化爬虫与信息提取流程，即所谓的“爬查一体”架构， 因此 scraper 在 wiseflow 产品语境内与传统定位稍有不同，在这里它仅是指将爬虫获取的已渲染的 html 转化为便于大模型“阅读和理解”的数据前处理过程。

它的输入是 已渲染的 html 编码（配合网站的 base_url），输出是三个值：

- `action_dict`：页面中可执行的元素项目，类型为 `dict`，格式如下：

```python
{
    'item_name': {"type": 交互类型, "values": ["value1", "value2"]}
}
```

这个内容供 llm 判断是否需要采取行动以及采取什么行动，从而可以进一步获得需要的信息。

- `link_dict`：页面中所有链接的字典，类型为 `dict`，格式如下：

```python
{
    'link_key': "link_url"
}
```

其中 key 是页面链接的唯一编号，general_scraper 中使用顺序编号生成，比如 url1, url2, url3 等。

这个内容供 llm 从中提取可能包含用户关注点信息的链接，被提取的链接会被加入爬虫获取队列。

- `text`：页面中所有文字的拼接，类型为 `str`

llm 从中提取用户关注点信息。


*有关这个机制其实我做过很多实验，包括让 llm 直接分析 html 编码（去除不必要标签或者分段），以及使用视觉大模型结合网页截图进行分析，最终发现综合考虑实现复杂度、抗干扰和异常能力、时间成本以及效果，目前方案是最优的。其中视觉大模型方案虽然我一直很期待，但实践中发现获取无干扰的网页截图并不容易，需要考虑各种情况，比如 cookie 警告等（很多 cookie 警告并不是简单的弹窗）、窗口大小设定以及因此带来的可能的多轮处理等……最关键的是，最终我发现如果网页文本处理得当，纯文本分析的效果是优于视觉大模型的……当然这里面的关键就是对 html 的处理，你不能指望把整个 html直接喂给 llm，那自然得不到好的结果，甚至粗糙的提取全部的文本和链接送给 llm 也很难得到好的结果,并且这样还会很烦 token，且拉长单次处理时间……*

wiseflow 目前搭配的 general_scraper 包括了对诸多常见 html 元素的处理，包括表格、列表、图片、视频、音频、表单、按钮、链接、文本等， 它能将这些元素统一转为适合 llm “阅读和理解”的文本，尤其是对于链接的处理，general_scraper 将链接替换为带编号的tag，而不是直接在文字中混入 url，一方面避免了对 llm 的干扰，同时也降低了token 的消耗，并且保证了 url 的准确。

general_scraper 目前被测试适合绝大部分常见的页面，并且通过分析得到的 link_dict 和 text 比例特征，很容易判断出页面是列表页面还是文章页面。

不过如果对于特定站点需要使用特殊的提取逻辑，您可以参考 general_scraper 配置自定义解析器。

## 自定义解析器的开发：

自定义解析器需要满足如下规格，否则无法被主流程整合：

- Scraper 应该是一个函数（而不是类）。

- 入参：
  - `html`：渲染后的页面 html 编码，类型为 `str`，scraper 可以直接使用 `bs` `parsel`等库进行解析；
  - ` base_url`：当前页面的 base url 地址，类型为 `str`（仅是为了特殊操作，用不到的话可以直接忽略）。

    *目前 wiseflow 仅支持使用内置的爬虫（Crawlee['playwright_crawler']）进行页面获取，因此入参都是由主流程传递给 scraper 的。*

- 出参：

    - `action_dict`：页面中可执行的元素项目，类型为 `dict`，格式如下：

    ```python
    {
        'item_name': {"type": 交互类型, "values": ["value1", "value2"]}
    }
    ```

    这个内容供 llm 判断是否需要采取行动以及采取什么行动，从而可以进一步获得需要的信息。

    - `link_dict`：页面中所有链接的字典，类型为 `dict`，格式如下：

    ```python
    {
        'link_key': "link_url"
    }
    ```

    - `text`：页面中所有文字的拼接，类型为 `str`
    
    llm 从中提取用户关注点信息。
 
## 自定义解析器的注册

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