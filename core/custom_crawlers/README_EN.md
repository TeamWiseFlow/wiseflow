wiseflow is dedicated to processing all pages through a set of general workflows (llm-agent that can autonomously use crawling tools).

However, we also reserve the flexibility for customers to handle custom processing. You can add and register custom crawlers for specific domains here.

Please follow the guidelines below:

1. The crawler should be a function (not a class);

2. It only accepts two parameters: **url** (the URL to process, please provide only one URL, not a list, as the main function will handle queue logic) and **logger** object (which means you should not add a logging object to your custom crawler, wiseflow will manage it uniformly);

3. The output must be two items: one is the parsed article details `article`, which is a dict object, and the other is a dictionary of external links `link_dict`, which is also a dict object.

The format for `article` is as follows (note that 'content' is required and cannot be empty, other fields can be omitted, and any additional key-value information will be ignored):

`{'url': ..., 'title': ..., 'author': ..., 'publish_date': ..., 'screenshot': ..., 'content': ...(not empty)}`

All values in the above dictionary should be of type **str**, the date format should be **YYYY-MM-DD**, and the screenshot should be a **file path**, which can be a relative path to the core directory or an absolute path, with the file type being **png**.

**Note:**
- 'content' must exist and not be empty, otherwise it will not trigger subsequent extraction, and the article will be discarded. This is the only required non-empty item;
- 'author' and 'publish_date' are strongly recommended, otherwise wiseflow will automatically use the domain name corresponding to the domain and the current date as substitutes.

The format for `link_dict` is as follows:

`{'text': text information corresponding to the external link, 'url': URL corresponding to the external link}`

wiseflow will use this as input and use LLM to determine which links are worth further crawling.

4. Register in `core/custom_crawlers/__init__.py`, refer to:


```pyhton
from .mp import mp_crawler

customer_crawler_map = {'mp.weixin.qq.com': mp_crawler}
```

Note that the key should be the domain name, which can be obtained using `urllib.parse`:

```pyhton
from urllib.parse import urlparse

parsed_url = urlparse("site's url")
domain = parsed_url.netloc
```
