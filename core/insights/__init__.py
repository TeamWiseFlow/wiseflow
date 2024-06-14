from ..scrapers import *
from ..utils.general_utils import extract_urls, compare_phrase_with_list
from .get_info import get_info, pb, project_dir, logger, info_rewrite
import os
import json
from datetime import datetime, timedelta
from urllib.parse import urlparse
import re
import time


# The XML parsing scheme is not used because there are abnormal characters in the XML code extracted from the weixin public_msg
item_pattern = re.compile(r'<item>(.*?)</item>', re.DOTALL)
url_pattern = re.compile(r'<url><!\[CDATA\[(.*?)]]></url>')
summary_pattern = re.compile(r'<summary><!\[CDATA\[(.*?)]]></summary>', re.DOTALL)

expiration_days = 3
existing_urls = [url['url'] for url in pb.read(collection_name='articles', fields=['url']) if url['url']]


def pipeline(_input: dict):
    cache = {}
    source = _input['user_id'].split('@')[-1]
    logger.debug(f"received new task, user: {source}, MsgSvrID: {_input['addition']}")

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
            if url in cache:
                logger.debug(f"{url} already find in item")
                continue
            summary_match = summary_pattern.search(item)
            summary = summary_match.group(1) if summary_match else None
            cache[url] = summary
        urls = list(cache.keys())

    elif _input['type'] == 'text':
        urls = extract_urls(_input['content'])
        if not urls:
            logger.debug(f"can not find any url in\n{_input['content']}\npass...")
            return
    elif _input['type'] == 'url':
        urls = []
        pass
    else:
        return

    global existing_urls

    for url in urls:
        if url in existing_urls:
            logger.debug(f"{url} has been crawled, skip")
            continue

        logger.debug(f"fetching {url}")
        if url.startswith('https://mp.weixin.qq.com') or url.startswith('http://mp.weixin.qq.com'):
            flag, article = mp_crawler(url, logger)
            if flag == -7:
                # For mp crawlers, the high probability of -7 is limited by WeChat, just wait 1min.
                logger.info(f"fetch {url} failed, try to wait 1min and try again")
                time.sleep(60)
                flag, article = mp_crawler(url, logger)
        else:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            if domain in scraper_map:
                flag, article = scraper_map[domain](url, logger)
            else:
                flag, article = simple_crawler(url, logger)

        if flag == -7:
            #  -7 means that the network is different, and other crawlers have no effect.
            logger.info(f"cannot fetch {url}")
            continue

        if flag != 11:
            logger.info(f"{url} failed with mp_crawler and simple_crawler")
            flag, article = llm_crawler(url, logger)
            if flag != 11:
                logger.info(f"{url} failed with llm_crawler")
                continue

        expiration_date = datetime.now() - timedelta(days=expiration_days)
        expiration_date = expiration_date.strftime('%Y-%m-%d')
        article_date = int(article['publish_time'])
        if article_date < int(expiration_date.replace('-', '')):
            logger.info(f"publish date is {article_date}, too old, skip")
            continue

        article['source'] = source
        if cache[url]:
            article['abstract'] = cache[url]

        insights = get_info(f"title: {article['title']}\n\ncontent: {article['content']}")

        try:
            article_id = pb.add(collection_name='articles', body=article)
        except Exception as e:
            logger.error(f'add article failed, writing to cache_file - {e}')
            with open(os.path.join(project_dir, 'cache_articles.json'), 'a', encoding='utf-8') as f:
                json.dump(article, f, ensure_ascii=False, indent=4)
            continue

        existing_urls.append(url)

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
                    pb.delete(collection_name='insights', id=old_insight_dict[old_insight]['id'])
                    old_insights.remove(old_insight_dict[old_insight])

            try:
                insight['id'] = pb.add(collection_name='insights', body=insight)
                # old_insights.append(insight)
            except Exception as e:
                logger.error(f'add insight failed, writing to cache_file - {e}')
                with open(os.path.join(project_dir, 'cache_insights.json'), 'a', encoding='utf-8') as f:
                    json.dump(insight, f, ensure_ascii=False, indent=4)

        try:
            pb.update(collection_name='articles', id=article_id, body={'tag': list(article_tags)})
        except Exception as e:
            logger.error(f'update article failed - article_id: {article_id}\n{e}')
            article['tag'] = list(article_tags)
            with open(os.path.join(project_dir, 'cache_articles.json'), 'a', encoding='utf-8') as f:
                json.dump(article, f, ensure_ascii=False, indent=4)
