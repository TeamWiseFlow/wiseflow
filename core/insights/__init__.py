# -*- coding: utf-8 -*-

from scrapers import *
from utils.general_utils import extract_urls, compare_phrase_with_list
from .get_info import get_info, pb, project_dir, logger, info_rewrite
import os
import json
from datetime import datetime, timedelta
from urllib.parse import urlparse
import re


# The XML parsing scheme is not used because there are abnormal characters in the XML code extracted from the weixin public_msg
item_pattern = re.compile(r'<item>(.*?)</item>', re.DOTALL)
url_pattern = re.compile(r'<url><!\[CDATA\[(.*?)]]></url>')
summary_pattern = re.compile(r'<summary><!\[CDATA\[(.*?)]]></summary>', re.DOTALL)

expiration_days = 3
existing_urls = [url['url'] for url in pb.read(collection_name='articles', fields=['url']) if url['url']]


async def get_articles(urls: list[str], expiration: datetime, cache: dict = {}) -> list[dict]:
    articles = []
    for url in urls:
        logger.debug(f"fetching {url}")
        if url.startswith('https://mp.weixin.qq.com') or url.startswith('http://mp.weixin.qq.com'):
            flag, result = await mp_crawler(url, logger)
        else:
            flag, result = await general_crawler(url, logger)

        if flag != 11:
            continue

        existing_urls.append(url)
        expiration_date = expiration.strftime('%Y-%m-%d')
        article_date = int(result['publish_time'])
        if article_date < int(expiration_date.replace('-', '')):
            logger.info(f"publish date is {article_date}, too old, skip")
            continue

        if url in cache:
            for k, v in cache[url].items():
                if v:
                    result[k] = v
        articles.append(result)

    return articles


async def pipeline(_input: dict):
    cache = {}
    source = _input['user_id'].split('@')[-1]
    logger.debug(f"received new task, user: {source}, Addition info: {_input['addition']}")

    global existing_urls
    expiration_date = datetime.now() - timedelta(days=expiration_days)

    # If you can get the url list of the articles from the input content, then use the get_articles function here directly;
    # otherwise, you should use a proprietary site scaper (here we provide a general scraper to ensure the basic effect)

    if _input['type'] == 'publicMsg':
        items = item_pattern.findall(_input["content"])
        # Iterate through all < item > content, extracting < url > and < summary >
        for item in items:
            url_match = url_pattern.search(item)
            url = url_match.group(1) if url_match else None
            if not url:
                logger.warning(f"can not find url in \n{item}")
                continue
            # URL processing, http is replaced by https, and the part after chksm is removed.
            url = url.replace('http://', 'https://')
            cut_off_point = url.find('chksm=')
            if cut_off_point != -1:
                url = url[:cut_off_point-1]
            if url in existing_urls:
                logger.debug(f"{url} has been crawled, skip")
                continue
            if url in cache:
                logger.debug(f"{url} already find in item")
                continue
            summary_match = summary_pattern.search(item)
            summary = summary_match.group(1) if summary_match else None
            cache[url] = {'source': source, 'abstract': summary}
        articles = await get_articles(list(cache.keys()), expiration_date, cache)

    elif _input['type'] == 'site':
        # for the site url, Usually an article list page or a website homepage
        # need to get the article list page
        # You can use a general scraper, or you can customize a site-specific crawler, see scrapers/README_CN.md
        urls = extract_urls(_input['content'])
        if not urls:
            logger.debug(f"can not find any url in\n{_input['content']}")
            return
        articles = []
        for url in urls:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            if domain in scraper_map:
                result = scraper_map[domain](url, expiration_date.date(), existing_urls, logger)
            else:
                result = await general_scraper(url, expiration_date.date(), existing_urls, logger)
            articles.extend(result)

    elif _input['type'] == 'text':
        urls = extract_urls(_input['content'])
        if not urls:
            logger.debug(f"can not find any url in\n{_input['content']}\npass...")
            return
        articles = await get_articles(urls, expiration_date)

    elif _input['type'] == 'url':
        # this is remained for wechat shared mp_article_card
        # todo will do it in project awada (need finish the generalMsg api first)
        articles = []
    else:
        return

    for article in articles:
        logger.debug(f"article: {article['title']}")
        insights = get_info(f"title: {article['title']}\n\ncontent: {article['content']}")

        article_id = pb.add(collection_name='articles', body=article)
        if not article_id:
            # do again
            article_id = pb.add(collection_name='articles', body=article)
            if not article_id:
                logger.error('add article failed, writing to cache_file')
                with open(os.path.join(project_dir, 'cache_articles.json'), 'a', encoding='utf-8') as f:
                    json.dump(article, f, ensure_ascii=False, indent=4)
                continue

        if not insights:
            continue

        article_tags = set()
        old_insights = pb.read(collection_name='insights', filter=f"updated>'{expiration_date}'", fields=['id', 'tag', 'content', 'articles'])
        for insight in insights:
            article_tags.add(insight['tag'])
            insight['articles'] = [article_id]
            old_insight_dict = {i['content']: i for i in old_insights if i['tag'] == insight['tag']}

            # Because what you want to compare is whether the extracted information phrases are talking about the same thing,
            # it may not be suitable and too heavy to calculate the similarity with a vector model
            # Therefore, a simplified solution is used here, directly using the jieba particifier, to calculate whether the overlap between the two phrases exceeds.

            similar_insights = compare_phrase_with_list(insight['content'], list(old_insight_dict.keys()), 0.65)
            if similar_insights:
                to_rewrite = similar_insights + [insight['content']]
                new_info_content = info_rewrite(to_rewrite)
                if not new_info_content:
                    continue
                insight['content'] = new_info_content
                # Merge related articles and delete old insights
                for old_insight in similar_insights:
                    insight['articles'].extend(old_insight_dict[old_insight]['articles'])
                    if not pb.delete(collection_name='insights', id=old_insight_dict[old_insight]['id']):
                        # do again
                        if not pb.delete(collection_name='insights', id=old_insight_dict[old_insight]['id']):
                            logger.error('delete insight failed')
                    old_insights.remove(old_insight_dict[old_insight])

            insight['id'] = pb.add(collection_name='insights', body=insight)
            if not insight['id']:
                # do again
                insight['id'] = pb.add(collection_name='insights', body=insight)
                if not insight['id']:
                    logger.error('add insight failed, writing to cache_file')
                    with open(os.path.join(project_dir, 'cache_insights.json'), 'a', encoding='utf-8') as f:
                        json.dump(insight, f, ensure_ascii=False, indent=4)

        _ = pb.update(collection_name='articles', id=article_id, body={'tag': list(article_tags)})
        if not _:
            # do again
            _ = pb.update(collection_name='articles', id=article_id, body={'tag': list(article_tags)})
            if not _:
                logger.error(f'update article failed - article_id: {article_id}')
                article['tag'] = list(article_tags)
                with open(os.path.join(project_dir, 'cache_articles.json'), 'a', encoding='utf-8') as f:
                    json.dump(article, f, ensure_ascii=False, indent=4)
