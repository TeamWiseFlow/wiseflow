# -*- coding: utf-8 -*-
from utils.pb_api import PbTalker
from utils.general_utils import get_logger, extract_and_convert_dates, is_chinese, isURL
from agents.get_info import *
from agents.insights import InsightExtractor
import json
from scrapers import *
from utils.zhipu_search import run_v4_async
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, CacheMode
from datetime import datetime
import feedparser
from plugins import PluginManager
from connectors import ConnectorBase, DataItem
from references import ReferenceManager

project_dir = os.environ.get("PROJECT_DIR", "")
if project_dir:
    os.makedirs(project_dir, exist_ok=True)

wiseflow_logger = get_logger('wiseflow', project_dir)
pb = PbTalker(wiseflow_logger)

model = os.environ.get("PRIMARY_MODEL", "")
if not model:
    raise ValueError("PRIMARY_MODEL not set, please set it in environment variables or edit core/.env")
secondary_model = os.environ.get("SECONDARY_MODEL", model)

# Initialize plugin manager
plugin_manager = PluginManager(plugins_dir="core")

# Initialize reference manager
reference_manager = ReferenceManager(storage_path=os.path.join(project_dir, "references"))

# Initialize insight extractor
insight_extractor = InsightExtractor(pb_client=pb)

async def info_process(url: str, 
                       url_title: str, 
                       author: str, 
                       publish_date: str, 
                       contents: list[str], 
                       link_dict: dict, 
                       focus_id: str,
                       get_info_prompts: list[str]):
    wiseflow_logger.debug('info summarising by llm...')
    infos = await get_info(contents, link_dict, get_info_prompts, author, publish_date, _logger=wiseflow_logger)
    if infos:
        wiseflow_logger.debug(f'get {len(infos)} infos, will save to pb')

    for info in infos:
        info['url'] = url
        info['url_title'] = url_title
        info['tag'] = focus_id

        # Process insights for each info item
        try:
            content = info.get('content', '')
            if content:
                # Extract insights from the content
                insights = await insight_extractor.process_item({
                    'id': info.get('id', str(uuid.uuid4())),
                    'content': content,
                    'title': info.get('title', url_title),
                    'url': url,
                    'author': author,
                    'publish_date': publish_date
                })
                
                # Add insights to the info object
                info['insights'] = insights
                wiseflow_logger.debug(f'Added insights to info item: {len(str(insights))} bytes')
        except Exception as e:
            wiseflow_logger.error(f'Error processing insights: {e}')
        
        # Save to database
        await pb.create('infos', info)

async def process_data_with_plugins(data_item: DataItem, focus: dict, get_info_prompts: list[str]):
    """Process a data item using the appropriate processor plugin."""
    # Get the focus point processor
    processor_name = "text_processor"
    processor = plugin_manager.get_plugin(processor_name)
    
    if not processor:
        wiseflow_logger.warning(f"Processor {processor_name} not found, falling back to default processing")
        # Fall back to default processing
        if data_item.content_type.startswith("text/"):
            await info_process(
                data_item.url or "", 
                data_item.metadata.get("title", ""), 
                data_item.metadata.get("author", ""), 
                data_item.metadata.get("publish_date", ""), 
                [data_item.content], 
                {}, 
                focus["id"],
                get_info_prompts
            )
        return
    
    try:
        # Process the data item
        processed_data = processor.process(data_item, {
            "focus_point": focus.get("focuspoint", ""),
            "explanation": focus.get("explanation", ""),
            "prompts": get_info_prompts
        })
        
        # Save processed data
        if processed_data and processed_data.processed_content:
            for info in processed_data.processed_content:
                if isinstance(info, dict):
                    info['url'] = data_item.url or ""
                    info['url_title'] = data_item.metadata.get("title", "")
                    info['tag'] = focus["id"]
                    _ = pb.add(collection_name='infos', body=info)
                    if not _:
                        wiseflow_logger.error('add info failed, writing to cache_file')
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                        with open(os.path.join(project_dir, f'{timestamp}_cache_infos.json'), 'w', encoding='utf-8') as f:
                            json.dump(info, f, ensure_ascii=False, indent=4)
    except Exception as e:
        wiseflow_logger.error(f"Error processing data item: {e}")


async def collect_from_connector(connector_name: str, params: dict) -> list[DataItem]:
    """Collect data from a connector."""
    connector = plugin_manager.get_plugin(connector_name)
    
    if not connector or not isinstance(connector, ConnectorBase):
        wiseflow_logger.error(f"Connector {connector_name} not found or not a valid connector")
        return []
    
    try:
        return connector.collect(params)
    except Exception as e:
        wiseflow_logger.error(f"Error collecting data from connector {connector_name}: {e}")
        return []


async def main_process(focus: dict, sites: list):
    wiseflow_logger.debug('new task initializing...')
    focus_id = focus["id"]
    focus_point = focus["focuspoint"].strip()
    explanation = focus["explanation"].strip() if focus["explanation"] else ''
    wiseflow_logger.debug(f'focus_id: {focus_id}, focus_point: {focus_point}, explanation: {explanation}, search_engine: {focus["search_engine"]}')
    existing_urls = {url['url'] for url in pb.read(collection_name='infos', fields=['url'], filter=f"tag='{focus_id}'")}
    focus_statement = f"{focus_point}"
    date_stamp = datetime.now().strftime('%Y-%m-%d')
    if is_chinese(focus_point):
        focus_statement = f"{focus_statement}\n注：{explanation}（目前日期是{date_stamp}）"
    else:
        focus_statement = f"{focus_statement}\nNote: {explanation}(today is {date_stamp})"

    if is_chinese(focus_statement):
        get_link_sys_prompt = get_link_system.replace('{focus_statement}', focus_statement)
        # get_link_sys_prompt = f"今天的日期是{date_stamp}，{get_link_sys_prompt}"
        get_link_suffix_prompt = get_link_suffix
        get_info_sys_prompt = get_info_system.replace('{focus_statement}', focus_statement)
        # get_info_sys_prompt = f"今天的日期是{date_stamp}，{get_info_sys_prompt}"
        get_info_suffix_prompt = get_info_suffix
    else:
        get_link_sys_prompt = get_link_system_en.replace('{focus_statement}', focus_statement)
        # get_link_sys_prompt = f"today is {date_stamp}, {get_link_sys_prompt}"
        get_link_suffix_prompt = get_link_suffix_en
        get_info_sys_prompt = get_info_system_en.replace('{focus_statement}', focus_statement)
        # get_info_sys_prompt = f"today is {date_stamp}, {get_info_sys_prompt}"
        get_info_suffix_prompt = get_info_suffix_en
    
    get_link_prompts = [get_link_sys_prompt, get_link_suffix_prompt, secondary_model]
    get_info_prompts = [get_info_sys_prompt, get_info_suffix_prompt, model]

    # Load plugins if not already loaded
    if not plugin_manager.plugins:
        wiseflow_logger.info("Loading plugins...")
        plugins = plugin_manager.load_all_plugins()
        wiseflow_logger.info(f"Loaded {len(plugins)} plugins")
        
        # Initialize plugins with configurations
        configs = {}  # Load configurations from database or config files
        results = plugin_manager.initialize_all_plugins(configs)
        
        for name, success in results.items():
            if success:
                wiseflow_logger.info(f"Initialized plugin: {name}")
            else:
                wiseflow_logger.error(f"Failed to initialize plugin: {name}")

    # Process references
    references = []
    if focus.get("references"):
        try:
            references = json.loads(focus["references"])
        except:
            references = []
    
    for reference in references:
        ref_type = reference.get("type")
        ref_content = reference.get("content")
        
        if not ref_type or not ref_content:
            continue
        
        if ref_type == "url" and ref_content not in existing_urls:
            # Add URL to sites for processing
            sites.append({"url": ref_content, "type": "web"})
        elif ref_type == "text":
            # Process text reference
            data_item = DataItem(
                source_id=f"text_reference_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                content=ref_content,
                metadata={"title": reference.get("name", "Text Reference"), "type": "text"},
                content_type="text/plain"
            )
            await process_data_with_plugins(data_item, focus, get_info_prompts)

    working_list = set()
    if focus.get('search_engine', False):
        query = focus_point if not explanation else f"{focus_point}({explanation})"
        search_intent, search_content = await run_v4_async(query, _logger=wiseflow_logger)
        _intent = search_intent['search_intent'][0]['intent']
        _keywords = search_intent['search_intent'][0]['keywords']
        wiseflow_logger.info(f'\nquery: {query} keywords: {_keywords}')
        search_results = search_content['search_result']
        for result in search_results:
            if 'content' not in result or 'link' not in result:
                continue
            url = result['link']
            if url in existing_urls:
                continue
            if '（发布时间' not in result['title']:
                title = result['title']
                publish_date = ''
            else:
                title, publish_date = result['title'].split('（发布时间')
                publish_date = publish_date.strip('）')
                # 严格匹配YYYY-MM-DD格式
                date_match = re.search(r'\d{4}-\d{2}-\d{2}', publish_date)
                if date_match:
                    publish_date = date_match.group()
                    publish_date = extract_and_convert_dates(publish_date)
                else:
                    publish_date = ''
                    
            title = title.strip() + '(from search engine)'
            author = result.get('media', '')
            if not author:
                author = urlparse(url).netloc
            texts = [result['content']]
            await info_process(url, title, author, publish_date, texts, {}, focus_id, get_info_prompts)

    # Determine concurrency for this focus point
    concurrency = focus.get("concurrency", 1)
    if concurrency < 1:
        concurrency = 1
    
    # Create a semaphore to limit concurrency
    semaphore = asyncio.Semaphore(concurrency)

    recognized_img_cache = {}
    for site in sites:
        if site.get('type', 'web') == 'rss':
            try:
                feed = feedparser.parse(site['url'])
            except Exception as e:
                wiseflow_logger.warning(f"{site['url']} RSS feed is not valid: {e}")
                continue
            rss_urls = {entry.link for entry in feed.entries if entry.link and isURL(entry.link)}
            wiseflow_logger.debug(f'get {len(rss_urls)} urls from rss source {site["url"]}')
            working_list.update(rss_urls - existing_urls)
        else:
            if site['url'] not in existing_urls and isURL(site['url']):
                working_list.add(site['url'])

    # Try to use the web connector plugin if available
    web_connector = plugin_manager.get_plugin("web_connector")
    if web_connector and isinstance(web_connector, ConnectorBase):
        wiseflow_logger.info("Using web connector plugin for data collection")
        
        # Process sites in parallel with concurrency control
        tasks = []
        for url in working_list:
            tasks.append(process_url_with_connector(url, web_connector, focus, get_info_prompts, semaphore))
        
        if tasks:
            await asyncio.gather(*tasks)
    else:
        # Fall back to the original crawler implementation
        wiseflow_logger.info("Web connector plugin not available, using default crawler")
        crawler = AsyncWebCrawler(config=browser_cfg)
        await crawler.start()
        
        # Process URLs with concurrency control
        tasks = []
        for url in working_list:
            tasks.append(process_url_with_crawler(url, crawler, focus_id, existing_urls, get_link_prompts, get_info_prompts, recognized_img_cache, semaphore))
        
        if tasks:
            await asyncio.gather(*tasks)
        
        await crawler.close()
    
    wiseflow_logger.debug(f'task finished, focus_id: {focus_id}')


async def process_url_with_connector(url, connector, focus, get_info_prompts, semaphore):
    """Process a URL using a connector with concurrency control."""
    async with semaphore:
        try:
            wiseflow_logger.debug(f"Processing URL with connector: {url}")
            data_items = await collect_from_connector("web_connector", {"urls": [url]})
            
            for data_item in data_items:
                await process_data_with_plugins(data_item, focus, get_info_prompts)
        except Exception as e:
            wiseflow_logger.error(f"Error processing URL {url} with connector: {e}")


async def process_url_with_crawler(url, crawler, focus_id, existing_urls, get_link_prompts, get_info_prompts, recognized_img_cache, semaphore):
    """Process a URL using the crawler with concurrency control."""
    async with semaphore:
        try:
            wiseflow_logger.debug(f"Processing URL with crawler: {url}")
            
            has_common_ext = any(url.lower().endswith(ext) for ext in common_file_exts)
            if has_common_ext:
                wiseflow_logger.debug(f'{url} is a common file, skip')
                return

            parsed_url = urlparse(url)
            existing_urls.add(f"{parsed_url.scheme}://{parsed_url.netloc}")
            existing_urls.add(f"{parsed_url.scheme}://{parsed_url.netloc}/")
            domain = parsed_url.netloc
                
            crawler_config.cache_mode = CacheMode.WRITE_ONLY if url in [s['url'] for s in sites] else CacheMode.ENABLED
            try:
                result = await crawler.arun(url=url, config=crawler_config)
            except Exception as e:
                wiseflow_logger.error(e)
                return
            if not result.success:
                wiseflow_logger.warning(f'{url} failed to crawl')
                return
            metadata_dict = result.metadata if result.metadata else {}

            if domain in custom_scrapers:
                result = custom_scrapers[domain](result)
                raw_markdown = result.content
                used_img = result.images
                title = result.title
                if title == 'maybe a new_type_article':
                    wiseflow_logger.warning(f'we found a new type here,{url}\n{result}')
                base_url = result.base
                author = result.author
                publish_date = result.publish_date
            else:
                raw_markdown = result.markdown
                media_dict = result.media if result.media else {}
                used_img = [d['src'] for d in media_dict.get('images', [])]
                title = ''
                base_url = ''
                author = ''
                publish_date = ''
            if not raw_markdown:
                wiseflow_logger.warning(f'{url} no content\n{result}\nskip')
                return
            wiseflow_logger.debug('data preprocessing...')
            if not title:
                title = metadata_dict.get('title', '')
            if not base_url:
                base_url = metadata_dict.get('base', '')
            if not base_url:
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

            if not author:
                author = metadata_dict.get('author', '')
            if not publish_date:
                publish_date = metadata_dict.get('publish_date', '')

            link_dict, links_parts, contents, recognized_img_cache = await pre_process(raw_markdown, base_url, used_img, recognized_img_cache, existing_urls)

            if link_dict and links_parts:
                wiseflow_logger.debug('links_parts exists, more links detecting...')
                links_texts = []
                for _parts in links_parts:
                    links_texts.extend(_parts.split('\n\n'))
                more_url = await get_more_related_urls(links_texts, link_dict, get_link_prompts, _logger=wiseflow_logger)
                if more_url:
                    wiseflow_logger.debug(f'get {len(more_url)} more related urls, will add to working list')
                    # Instead of adding to working_list, create new tasks for these URLs
                    for new_url in more_url - existing_urls:
                        existing_urls.add(new_url)
                        asyncio.create_task(process_url_with_crawler(new_url, crawler, focus_id, existing_urls, get_link_prompts, get_info_prompts, recognized_img_cache, semaphore))
                
            if not contents:
                return

            if not author or author.lower() == 'na' or not publish_date or publish_date.lower() == 'na':
                wiseflow_logger.debug('no author or publish date from metadata, will try to get by llm')
                main_content_text = re.sub(r'!\[.*?]\(.*?\)', '', raw_markdown)
                main_content_text = re.sub(r'\[.*?]\(.*?\)', '', main_content_text)
                alt_author, alt_publish_date = await get_author_and_publish_date(main_content_text, secondary_model, _logger=wiseflow_logger)
                if not author or author.lower() == 'na':
                    author = alt_author if alt_author else parsed_url.netloc
                if not publish_date or publish_date.lower() == 'na':
                    publish_date = alt_publish_date if alt_publish_date else ''

            publish_date = extract_and_convert_dates(publish_date)

            await info_process(url, title, author, publish_date, contents, link_dict, focus_id, get_info_prompts)
        except Exception as e:
            wiseflow_logger.error(f"Error processing URL {url} with crawler: {e}")


async def process_focus_point(focus_id: str, focus_point: str, explanation: str, sites: list, search_engine: bool = False):
    # ... existing code ...

    # After processing all sites, perform collective insights analysis
    try:
        # Get all infos for this focus point
        infos = await pb.get_all('infos', {'filter': f'tag="{focus_id}"'})
        
        if infos and len(infos) > 0:
            wiseflow_logger.info(f'Generating collective insights for focus point {focus_id} with {len(infos)} items')
            
            # Process the collection to extract collective insights
            collective_insights = await insight_extractor.process_collection([
                {
                    'id': info.get('id', ''),
                    'content': info.get('content', ''),
                    'title': info.get('title', ''),
                    'url': info.get('url', ''),
                    'created': info.get('created', ''),
                    'summary': info.get('summary', '')
                }
                for info in infos
            ])
            
            # Save collective insights to database
            collective_insights['focus_id'] = focus_id
            collective_insights['focus_point'] = focus_point
            await insight_extractor.store_insights_in_db(collective_insights, 'collective_insights')
            
            # Also save to file for backup
            insights_dir = os.path.join(project_dir, 'insights')
            os.makedirs(insights_dir, exist_ok=True)
            insight_extractor.save_insights(
                collective_insights, 
                os.path.join(insights_dir, f'insights_{focus_id}_{datetime.now().strftime("%Y%m%d")}.json')
            )
            
            wiseflow_logger.info(f'Collective insights generated and saved for focus point {focus_id}')
    except Exception as e:
        wiseflow_logger.error(f'Error generating collective insights: {e}')