wiseflow 致力于通过一套通用流程（使用大模型驱动的可以自主使用爬虫工具的智能体）处理所有页面。

不过我们也为客户保留自定义处理的灵活性。您可以在这里添加并注册针对特定域名的自定义爬虫。

请遵照如下规范：

1、爬虫应该是一个函数（而不是类）；

2、入参只接受两个：**url**（要处理的 url，请只提供一个 url，而不是列表，因为主函数会处理队列逻辑） 和 **logger** 对象（这意味着不要为你的自定义爬虫添加日志对象，wiseflow 会统一管理）；

3、出参必须为两个，一个是解析后的文章详情 article，类型为 dict，另一个是从页面解析出的外链字典 link_dict，类型也是 dict。

article 的字典格式如下（注意，'content' 是必须的，其他也可以没有，另外额外的键值信息会被忽略）：

`{'url': ..., 'title': ..., 'author': ..., 'publish_date': ..., 'screenshot': ..., 'content': ...(not empty)}`

上述值的类型都要求为 **str**， 日期格式为 **YYYY-MM-DD**，screenshot 为**文件路径**，可以是相对于 core目录的相对路径也可以是绝对路径，文件类型为 **png**。

**注意：**
- 'content' 要有且不为空，不然无法触发后续的提取，文章也会被舍弃。这是唯一要求不为空的项；
- 'author' 和 'publish_date' 尽量有，不然 wiseflow 会自动用域名对应 demain 和 当日日期代替。

link_dict 的格式如下：
`{'text': 外链对应的文字信息， 'url': 外链对应的 url}`

wiseflow 会以这个为输入，使用 llm 判断值得继续爬取的链接。

4、在 core/custom_crawlers/__init__.py 中注册，参考：

```pyhton
from .mp import mp_crawler

customer_crawler_map = {'mp.weixin.qq.com': mp_crawler}
```

注意键使用域名，可以使用 urllib.parse获取：

```pyhton
from urllib.parse import urlparse

parsed_url = urlparse("site's url")
domain = parsed_url.netloc
```