wiseflow 致力于通过一套通用流程（使用视觉大模型驱动的可以自主使用爬虫工具的智能体）处理所有页面。

不过我们也为客户保留自定义处理的灵活性。

为添加自定义处理逻辑单元请遵照如下规范：

1、逻辑处理单元应该是一个函数（而不是类）；

2、入参只接受两个：url（要处理的 url，请只提供一个 url，而不是列表，因为主函数会处理队列逻辑） 和 logger 对象（这意味着不要为你的自定义处理单元添加日志对象）；

3、出参需要返回解析后的文章详情（dict），和信息列表（list），以及解析出来的需要添加到工作队列的 url 结合（元组）。出参必须同时返回这三个结果，没有的话，可以分别传出 {} [] set()

article 的字典必须包括 'url'（str）， 'title'（str）， 'author'（str）， 'publish_date'（date 日期对象，注意是日期）四个键值，额外可以添加一个 'sceenshort' 值是一个 png 文件的路径。

4、在 core/custom_crawlers/__init__.py 中注册，参考：

```pyhton
from .mp_crawler import mp_crawler

customer_crawler_map = {'mp.weixin.qq.com': mp_crawler}
```

注意键使用域名，可以使用 urllib.parse获取：

```pyhton
from urllib.parse import urlparse

parsed_url = urlparse("site's url")
domain = parsed_url.netloc
```