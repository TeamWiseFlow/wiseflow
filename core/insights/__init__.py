# -*- coding: utf-8 -*-

from scrapers.general_crawler import general_crawler
from utils.general_utils import extract_urls, compare_phrase_with_list
from .get_info import get_info, pb, project_dir, logger, info_rewrite
import os
import json
from datetime import datetime, timedelta
import re
import asyncio


# The XML parsing scheme is not used because there are abnormal characters in the XML code extracted from the weixin public_msg
item_pattern = re.compile(r'<item>(.*?)</item>', re.DOTALL)
url_pattern = re.compile(r'<url><!\[CDATA\[(.*?)]]></url>')
summary_pattern = re.compile(r'<summary><!\[CDATA\[(.*?)]]></summary>', re.DOTALL)

expiration_days = 3
existing_urls = [url['url'] for url in pb.read(collection_name='articles', fields=['url']) if url['url']]


async def pipeline(url: str, cache: dict = {}):
    working_list = [url]
    while working_list:
        url = working_list[0]
        working_list.pop(0)
        logger.debug(f"start processing {url}")

        # get article process
        flag, result = await general_crawler(url, logger)
        if flag == 1:
            logger.info('get new url list, add to work list')
            to_add = [u for u in result if u not in existing_urls and u not in working_list]
            existing_urls.append(url)
            working_list.extend(to_add)
            continue
        elif flag <= 0:
            logger.error("got article failed, pipeline abort")
            # existing_urls.append(url)
            continue

        expiration = datetime.now() - timedelta(days=expiration_days)
        expiration_date = expiration.strftime('%Y-%m-%d')
        article_date = int(result['publish_time'])
        if article_date < int(expiration_date.replace('-', '')):
            logger.info(f"publish date is {article_date}, too old, skip")
            existing_urls.append(url)
            continue

        for k, v in cache.items():
            if v:
                result[k] = v

        # get info process
        logger.debug(f"article: {result['title']}")
        insights = get_info(f"title: {result['title']}\n\ncontent: {result['content']}")

        article_id = pb.add(collection_name='articles', body=result)
        if not article_id:
            await asyncio.sleep(1)
            # do again
            article_id = pb.add(collection_name='articles', body=result)
            if not article_id:
                logger.error('add article failed, writing to cache_file')
                with open(os.path.join(project_dir, 'cache_articles.json'), 'a', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)
                continue

        if not insights:
            continue

        existing_urls.append(url)
        # post process
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
            await asyncio.sleep(1)
            _ = pb.update(collection_name='articles', id=article_id, body={'tag': list(article_tags)})
            if not _:
                logger.error(f'update article failed - article_id: {article_id}')
                result['tag'] = list(article_tags)
                with open(os.path.join(project_dir, 'cache_articles.json'), 'a', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)


async def message_manager(_input: dict):
    source = _input['user_id'].split('@')[-1]
    logger.debug(f"received new task, user: {source}, Addition info: {_input['addition']}")
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
            summary_match = summary_pattern.search(item)
            summary = summary_match.group(1) if summary_match else None
            cache = {'source': source, 'abstract': summary}
            await pipeline(url, cache)

    elif _input['type'] == 'text':
        urls = extract_urls(_input['content'])
        if not urls:
            logger.debug(f"can not find any url in\n{_input['content']}\npass...")
            # todo get info from text process
            return
        await asyncio.gather(*[pipeline(url) for url in urls])

    elif _input['type'] == 'url':
        # this is remained for wechat shared mp_article_card
        # todo will do it in project awada (need finish the generalMsg api first)
        return
    else:
        return
