# For Developer Only

```bash
conda create -n wiseflow python=3.10
conda activate wiseflow
cd core
pip install -r requirements.txt
```

- tasks.py background task circle process
- backend.py main process pipeline service (based on fastapi)

### WiseFlow fastapi detail

- api address http://127.0.0.1:8077/feed
- request method : post
- body :

```python
{'user_id': str, 'type': str, 'content':str， 'addition': Optional[str]}
# Type is one of "text", "publicMsg", "site" and "url"；
# user_id: str
type: Literal["text", "publicMsg", "file", "image", "video", "location", "chathistory", "site", "attachment", "url"]
content: str
addition: Optional[str] = None`
```

see more (when backend started) http://127.0.0.1:7777/docs 

### WiseFlow Repo File Structure

```
wiseflow
|- dockerfiles
|- tasks.py
|- backend.py
|- core
    |- insights
        |- __init__.py  # main process
        |- get_info.py  # module use llm to get a summary of information and match tags
    |- llms # llm service wrapper
    |- pb  # pocketbase filefolder
    |- scrapers
        |- __init__.py  # You can register a proprietary site scraper here
        |- general_scraper.py  # module to get all possible article urls for general site 
        |- general_crawler.py  # module for general article sites
        |- mp_crawler.py  # module for mp article (weixin public account) sites
   |- utils # tools
```

Although the two general-purpose page parsers included in wiseflow can be applied to the parsing of most static pages, for actual business, we still recommend that customers subscribe to our professional information service (supporting designated sources), or write their own proprietary crawlers.

See core/scrapers/README.md for integration instructions for proprietary crawlers
