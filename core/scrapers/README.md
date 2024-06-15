> **This folder is intended for placing crawlers specific to particular sources. Note that the crawlers here should be able to parse the article list URL of the source and return a dictionary of article details.**
> 
> # Custom Crawler Configuration
> 
> After writing the crawler, place the crawler program in this folder and register it in the scraper_map in `__init__.py`, similar to:
> 
> ```python
> {'www.securityaffairs.com': securityaffairs_scraper}
> ```
> 
> Here, the key is the source URL, and the value is the function name.
> 
> The crawler should be written in the form of a function with the following input and output specifications:
> 
> Input:
> - expiration: A `datetime.date` object, the crawler should only fetch articles on or after this date.
> - existings: [str], a list of URLs of articles already in the database. The crawler should ignore the URLs in this list.
> 
> Output:
> - [dict], a list of result dictionaries, each representing an article, formatted as follows:
> `[{'url': str, 'title': str, 'author': str, 'publish_time': str, 'content': str, 'abstract': str, 'images': [Path]}, {...}, ...]`
> 
> Note: The format of `publish_time` should be `"%Y%m%d"`. If the crawler cannot fetch it, the current date can be used.
> 
> Additionally, `title` and `content` are mandatory fields.
> 
> # Generic Page Parser
> 
> We provide a generic page parser here, which can intelligently fetch article lists from the source. For each article URL, it will first attempt to parse using gne. If it fails, it will then attempt to parse using llm.
> 
> Through this solution, it is possible to scan and extract information from most general news and portal sources.
> 
> **However, we still strongly recommend that users write custom crawlers themselves or directly subscribe to our data service for more ideal and efficient scanning.**
