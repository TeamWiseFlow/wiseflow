import os
import json
import requests
from datetime import datetime, timedelta, date
from scrapers import scraper_map
from scrapers.general_scraper import general_scraper
from urllib.parse import urlparse
from get_insight import get_insight, pb, logger
from general_utils import is_chinese
from tranlsation_volcengine import text_translate
import concurrent.futures


# 一般用于第一次爬虫时，避免抓取过多太久的文章，同时超过这个天数的数据库文章也不会再用来匹配insight
expiration_date = datetime.now() - timedelta(days=90)
expiration_date = expiration_date.date()
expiration_str = expiration_date.strftime("%Y%m%d")


class ServiceProcesser:
    def __init__(self, record_snapshot: bool = False):
        self.project_dir = os.environ.get("PROJECT_DIR", "")
        # 1. base initialization
        self.cache_url = os.path.join(self.project_dir, 'scanning_task')
        os.makedirs(self.cache_url, exist_ok=True)
        # 2. load the llm
        # self.llm = LocalLlmWrapper() # if you use the local-llm

        if record_snapshot:
            snap_short_server = os.environ.get('SNAPSHOTS_SERVER', '')
            if not snap_short_server:
                raise Exception('SNAPSHOTS_SERVER is not set.')
            self.snap_short_server = f"http://{snap_short_server}"
        else:
            self.snap_short_server = None

        logger.info('scanning task init success.')

    def __call__(self, expiration: date = expiration_date, sites: list[str] = None):
        # 先清空一下cache
        logger.info(f'wake, prepare to work, now is {datetime.now()}')
        cache = {}
        logger.debug(f'clear cache -- {cache}')
        # 从pb数据库中读取所有文章url
        # 这里publish_time用int格式，综合考虑下这个是最容易操作的模式，虽然糙了点
        existing_articles = pb.read(collection_name='articles', fields=['id', 'title', 'url'], filter=f'publish_time>{expiration_str}')
        all_title = {}
        existings = []
        for article in existing_articles:
            all_title[article['title']] = article['id']
            existings.append(article['url'])

        # 定义扫描源列表，如果不指定就默认遍历scraper_map, 另外这里还要考虑指定的source不在scraper_map的情况，这时应该使用通用爬虫
        sources = sites if sites else list(scraper_map.keys())
        new_articles = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for site in sources:
                if site in scraper_map:
                    futures.append(executor.submit(scraper_map[site], expiration, existings))
                else:
                    futures.append(executor.submit(general_scraper, site, expiration, existings, logger))
            concurrent.futures.wait(futures)
            for future in futures:
                try:
                    new_articles.extend(future.result())
                except Exception as e:
                    logger.error(f'error when scraping-- {e}')

        for value in new_articles:
            if not value:
                continue
            from_site = urlparse(value['url']).netloc
            from_site = from_site.replace('www.', '')
            from_site = from_site.split('.')[0]
            if value['abstract']:
                value['abstract'] = f"({from_site} 报道){value['abstract']}"
            value['content'] = f"({from_site} 报道){value['content']}"
            value['images'] = json.dumps(value['images'])

            article_id = pb.add(collection_name='articles', body=value)

            if article_id:
                cache[article_id] = value
                all_title[value['title']] = article_id
            else:
                logger.warning(f'add article {value} failed, writing to cache_file')
                with open(os.path.join(self.cache_url, 'cache_articles.json'), 'a', encoding='utf-8') as f:
                    json.dump(value, f, ensure_ascii=False, indent=4)

        if not cache:
            logger.warning(f'no new articles. now is {datetime.now()}')
            return

        # insight 流程
        new_insights = get_insight(cache, all_title)
        if new_insights:
            for insight in new_insights:
                if not insight['content']:
                    continue
                insight_id = pb.add(collection_name='insights', body=insight)
                if not insight_id:
                    logger.warning(f'write insight {insight} to pb failed, writing to cache_file')
                    with open(os.path.join(self.cache_url, 'cache_insights.json'), 'a', encoding='utf-8') as f:
                        json.dump(insight, f, ensure_ascii=False, indent=4)
                for article_id in insight['articles']:
                    raw_article = pb.read(collection_name='articles', fields=['abstract', 'title', 'translation_result'], filter=f'id="{article_id}"')
                    if not raw_article or not raw_article[0]:
                        logger.warning(f'get article {article_id} failed, skipping')
                        continue
                    if raw_article[0]['translation_result']:
                        continue
                    if is_chinese(raw_article[0]['title']):
                        continue
                    translate_text = text_translate([raw_article[0]['title'], raw_article[0]['abstract']], target_language='zh', logger=logger)
                    if translate_text:
                        related_id = pb.add(collection_name='article_translation', body={'title': translate_text[0], 'abstract': translate_text[1], 'raw': article_id})
                        if not related_id:
                            logger.warning(f'write article_translation {article_id} failed')
                        else:
                            _ = pb.update(collection_name='articles', id=article_id, body={'translation_result': related_id})
                            if not _:
                                logger.warning(f'update article {article_id} failed')
                    else:
                        logger.warning(f'translate article {article_id} failed')
        else:
            # 尝试把所有文章的title作为insigts，这是备选方案
            if len(cache) < 25:
                logger.info('generate_insights-warning: no insights and no more than 25 articles so use article title as insights')
                for key, value in cache.items():
                    if value['title']:
                        if is_chinese(value['title']):
                            text_for_insight = value['title']
                        else:
                            text_for_insight = text_translate([value['title']], logger=logger)
                        if text_for_insight:
                            insight_id = pb.add(collection_name='insights', body={'content': text_for_insight[0], 'articles': [key]})
                            if not insight_id:
                                logger.warning(f'write insight {text_for_insight[0]} to pb failed, writing to cache_file')
                                with open(os.path.join(self.cache_url, 'cache_insights.json'), 'a',
                                          encoding='utf-8') as f:
                                    json.dump({'content': text_for_insight[0], 'articles': [key]}, f, ensure_ascii=False, indent=4)
            else:
                logger.warning('generate_insights-error: can not generate insights, pls re-try')
        logger.info(f'work done, now is {datetime.now()}')

        if self.snap_short_server:
            logger.info(f'now starting article snapshot with {self.snap_short_server}')
            for key, value in cache.items():
                if value['url']:
                    try:
                        snapshot = requests.get(f"{self.snap_short_server}/zip", {'url': value['url']}, timeout=60)
                        file = open(snapshot.text, 'rb')
                        _ = pb.upload('articles', key, 'snapshot', key, file)
                        file.close()
                    except Exception as e:
                        logger.warning(f'error when snapshot {value["url"]}, {e}')
            logger.info(f'now snapshot done, now is {datetime.now()}')
