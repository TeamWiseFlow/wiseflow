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