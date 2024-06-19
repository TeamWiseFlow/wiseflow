我们提供了一个通用页面解析器，该解析器可以智能获取信源文章列表。对于每个文章 URL，会先尝试使用 `gne` 进行解析，如果失败，再尝试使用 `llm` 进行解析。

通过这个方案，可以实现对大多数普通新闻类、门户类信源的扫描和信息提取。

**然而，我们依然强烈建议用户根据实际业务场景编写针对特定信源的专有解析器，以实现更理想且高效的扫描。**

此外，我们提供了一个专门针对微信公众号文章（mp.weixin.qq.com）的解析器。

**如果您愿意将您撰写的特定信源专有解析器贡献至本代码仓库，我们将不胜感激！**

## 专有信源解析器开发规范

### 规范

**记住：这应该是一个异步函数**

1. **解析器应能智能区分文章列表页面和文章详情页面。**
2. **解析器入参只包括 `url` 和 `logger` 两项：**
   - `url` 是信源完整地址（`str` 类型）
   - `logger` 是日志对象（请勿为您的专有信源解析器单独配置 `logger`）
3. **解析器出参包括 `flag` 和 `result` 两项，格式为 `tuple[int, Union[list, dict]]`：**
   - 如果 `url` 是文章列表页面，`flag` 返回 `1`，`result` 返回解析出的全部文章页面 URL 列表（`list`）。
   - 如果 `url` 是文章页面，`flag` 返回 `11`，`result` 返回解析出的全部文章详情（`dict`），格式如下：

     ```python
     {'url': str, 'title': str, 'author': str, 'publish_time': str, 'content': str, 'abstract': str, 'images': [str]}
     ```

     _注意：`title` 和 `content` 两项不能为空。_

     **注意：`publish_time` 格式为 `"%Y%m%d"`（仅日期，没有 `-`)，如果爬虫抓不到可以用当天日期。**

   - 如果解析失败，`flag` 返回 `0`，`result` 返回空字典 `{}`。

     _`pipeline` 收到 `flag` 0 会尝试其他解析方案（如有）。_

   - 如果页面获取失败（如网络问题），`flag` 返回 `-7`，`result` 返回空字典 `{}`。

     _`pipeline` 收到 `flag` -7， 同一进程内不会再次尝试解析。_

### 注册

写好爬虫后，将爬虫程序放在该文件夹，并在 `__init__.py` 下的 `scraper_map` 中注册爬虫，类似：

```python
{'domain': 'crawler def name'}
```

建议使用 urllib.parse 获取 domain：

```python
from urllib.parse import urlparse

parsed_url = urlparse("site's url")
domain = parsed_url.netloc
```