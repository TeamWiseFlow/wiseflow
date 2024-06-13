**这个文件夹下可以放置对应特定信源的爬虫，注意这里的爬虫应该是可以解析信源文章列表url并返回文章详情dict的**

# 专有爬虫配置

写好爬虫后，将爬虫程序放在这个文件夹，并在__init__.py下的scraper_map中注册爬虫，类似：

```python
{'www.securityaffairs.com': securityaffairs_scraper}
```

其中key就是信源地址，value是函数名

爬虫应该写为函数形式，出入参约定为：

输入：
- expiration： datetime的date.date()对象，爬虫应该只抓取这之后（含这一天）的文章
- existings：[str], 数据库已有文章的url列表，爬虫应该忽略这个列表里面的url

输出：
- [dict]，返回结果列表，每个dict代表一个文章，格式如下：
`[{'url': str, 'title':  str, 'author':  str,  'publish_time':  str, 'content':  str, 'abstract':  str, 'images': [Path]}, {...},  ...]`

注意：publish_time格式为`"%Y%m%d"`， 如果爬虫抓不到可以用当天日期

另外，title和content是必须要有的

# 通用页面解析器

我们这里提供了一个通用页面解析器，该解析器可以智能获取信源文章列表，接下来对于每一个文章url，会先尝试使用 gne 进行解析，如果失败的话，再尝试使用llm进行解析。

通过这个方案，可以实现对大多数普通新闻类、门户类信源的扫描和信息提取。

**然而我们依然强烈建议用户自行写专有爬虫或者直接订阅我们的数据服务，以实现更加理想且更加高效的扫描。**