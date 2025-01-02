# Wiseflow Custom Scraper Documentation

## Overview

wiseflow aims to automate web crawling and information extraction processes using large language models' understanding and analysis capabilities, known as the "integrated crawling and analysis" architecture. Therefore, the scraper in wiseflow's product context differs slightly from traditional positioning - here it only refers to the data preprocessing that converts rendered HTML from web crawlers into a format suitable for large models to "read and understand".

Its input is rendered HTML code (along with the website's base_url), and it outputs three values:

- `action_dict`: Executable elements on the page, type `dict`, formatted as follows:

```python
{
    'item_name': {"type": interaction type, "values": ["value1", "value2"]}
}
```

This content allows the LLM to determine whether actions need to be taken and what actions to take, in order to obtain further required information.

- `link_dict`: Dictionary of all links on the page, type `dict`, formatted as follows:

```python
{
    'link_key': "link_url"
}
```

where the key is a unique identifier for the page link. In general_scraper, sequential numbering is used to generate these, such as url1, url2, url3, etc.

This content allows the LLM to extract links that may contain information relevant to user interests. The extracted links are added to the crawler's queue.

- `text`: Concatenation of all text on the page, type `str`

The LLM extracts user-relevant information from this.

*I've actually done many experiments with this mechanism, including having the LLM directly analyze HTML code (removing unnecessary tags or segmenting), and using visual large models combined with webpage screenshots for analysis. After considering implementation complexity, interference and exception handling capabilities, time cost, and effectiveness, the current approach proved optimal. While I've always been excited about the visual large model approach, in practice I found that obtaining interference-free webpage screenshots isn't easy - you need to consider various scenarios like cookie warnings (many of which aren't simple popups), window size settings, and the resulting potential multi-round processing... Most crucially, I discovered that with proper webpage text processing, pure text analysis performs better than visual large models... Of course, the key here is HTML processing - you can't expect good results from feeding entire HTML directly to the LLM, and even rough extraction of all text and links sent to the LLM rarely yields good results, while also consuming more tokens and extending processing time...*

The general_scraper currently used by wiseflow includes processing for many common HTML elements, including tables, lists, images, videos, audio, forms, buttons, links, text, etc. It can convert these elements uniformly into text suitable for LLM "reading and understanding". Particularly for link processing, general_scraper replaces links with numbered tags rather than mixing URLs directly into the text, which both avoids interference with the LLM and reduces token consumption while ensuring URL accuracy.

general_scraper has been tested and found suitable for most common pages, and through analysis of the link_dict and text proportion characteristics, it's easy to determine whether a page is a list page or an article page.

However, if special extraction logic is needed for specific sites, you can refer to general_scraper to configure custom scraper.

## Custom Scraper Development:

Custom scraper must meet the following specifications to be integrated into the main process:

- The Scraper should be a function (not a class).

- Input parameters:
  - `html`: Rendered page HTML code, type `str`. The scraper can directly use libraries like `bs` or `parsel` for parsing;
  - `base_url`: The current page's base URL address, type `str` (only for special operations, can be ignored if not needed).

    *Currently wiseflow only supports using the built-in crawler (Crawlee['playwright_crawler']) for page retrieval, so input parameters are all passed to the scraper by the main process.*

- Output parameters:

    - `action_dict`: Executable elements on the page, type `dict`, formatted as follows:

    ```python
    {
        'item_name': {"type": interaction type, "values": ["value1", "value2"]}
    }
    ```

    This content allows the LLM to determine whether actions need to be taken and what actions to take, in order to obtain further required information.

    - `link_dict`: Dictionary of all links on the page, type `dict`, formatted as follows:

    ```python
    {
        'link_key': "link_url"
    }
    ```

    - `text`: Concatenation of all text on the page, type `str`
    
    The LLM extracts user-relevant information from this.
 
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