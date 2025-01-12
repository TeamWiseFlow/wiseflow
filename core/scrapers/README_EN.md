## Custom Scraper Registration

Register in `core/scrapers/__init__.py`, for example:

```python
from .mp import mp_scarper

customer_scrapers = {'mp.weixin.qq.com': mp_scarper}
```

Note that the key should use the domain name, which can be obtained using `urllib.parse`:


```python
from urllib.parse import urlparse

parsed_url = urlparse("site's url")
domain = parsed_url.netloc
```