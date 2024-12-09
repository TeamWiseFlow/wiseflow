# wiseflow 自定义解析器说明

## 概述
wiseflow 致力于通过一套通用流程（使用大模型驱动的可以自主使用爬虫工具的智能体）处理所有页面。

目前在页面获取方面我们使用流行的爬虫框架 Crawlee（playwright）进行统一管理，经过实测 Crawlee 在速度和兼容性方面都非常不错，且有着完善的任务队列管理模块，因此网页获取方面一般无需自定义。

对于页面信息的解析，wiseflow 默认使用大模型，但用户可以为特定域名配置自定义解析器。

## 自定义解析器配置说明

### 1. Scraper 函数定义
Scraper 应该是一个函数（而不是类）。

### 2. 函数参数
该函数接收两个入参（wiseflow 框架传入）：
- `html`：这是 wiseflow 通过 Crawlee 的 playwright_crawler 获取到的渲染后的页面 html 代码，类型为 `str`，scraper 可以直接使用 `bs` `parsel`等库进行解析；
- `url`：当前页面的 url 地址，类型为 `str`（仅是为了特殊操作，用不到的话可以直接忽略）。

### 3. 函数返回值
Scraper 出参限定为三个：

#### 3.1 `article`
解析出的页面详情，类型为 `dict`，格式如下：

```python
{
    'author': ..., 
    'publish_date': ..., 
    'content': ...
}
```

- 上述值的类型都要求为 `str`，日期格式为 `YYYY-MM-DD`。

**注意：**
1. `'content'` 要有且不为空，不然无法触发后续的提取；
2. `'author'` 和 `'publish_date'` 尽量有，不然 wiseflow 会自动用域名对应 demain 和 当日日期代替。

#### 3.2 `links`
对应页面解析出的链接，类型可以是 `set`，也可以是 `dict`：

- 如果是 `set`，则会全部被加入任务队列。
- 如果是 `dict`，则会调用 llm 从中挑取值得加入任务队列的 url（根据你的 focus point），`dict` 的格式如下：

```python
{
    'text': 外链对应的文字信息, 
    'url': 外链对应的 url
}
```

wiseflow 会以这个为输入，使用 llm 判断值得继续爬取的链接。

#### 3.3 `infos`
对应页面抽取出的值得关注的信息列表，类型是 `list`，元素为 `dict`，格式为：

```python
{
    'tag': focuspoint 的 id, 
    'content': 具体 info 内容
}
```

**注意，focuspoint 的 id 要和 pb 中 focus_points 表一致**

### 4. 注册自定义解析器
在 `core/custom_scraper/__init__.py` 中注册，参考：

```python
from .mp import mp_scarper

customer_crawler_map = {'mp.weixin.qq.com': mp_scarper}
```

注意键使用域名，可以使用 `urllib.parse` 获取：

```python
from urllib.parse import urlparse

parsed_url = urlparse("site's url")
domain = parsed_url.netloc
```