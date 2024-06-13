from scrapers import *
from utils.general_utils import extract_urls, compare_phrase_with_list
from insights.get_info import get_info, pb, project_dir, logger
from insights.rewrite import info_rewrite
import os
import json
from datetime import datetime, timedelta
from urllib.parse import urlparse
import re
import time


# 用正则不用xml解析方案是因为公众号消息提取出来的xml代码存在异常字符
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
        # 遍历所有<item>内容，提取<url>和<summary>
        for item in items:
            url_match = url_pattern.search(item)
            url = url_match.group(1) if url_match else None
            if not url:
                logger.warning(f"can not find url in \n{item}")
                continue
            # url处理，http换成https, 去掉chksm之后的部分
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
        # 0、先检查是否已经爬取过
        if url in existing_urls:
            logger.debug(f"{url} has been crawled, skip")
            continue

        logger.debug(f"fetching {url}")
        # 1、选择合适的爬虫fetch article信息
        if url.startswith('https://mp.weixin.qq.com') or url.startswith('http://mp.weixin.qq.com'):
            flag, article = mp_crawler(url, logger)
            if flag == -7:
                # 对于mp爬虫，-7 的大概率是被微信限制了，等待1min即可
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
            # -7 代表网络不同，用其他爬虫也没有效果
            logger.info(f"cannot fetch {url}")
            continue

        if flag != 11:
            logger.info(f"{url} failed with mp_crawler and simple_crawler")
            flag, article = llm_crawler(url, logger)
            if flag != 11:
                logger.info(f"{url} failed with llm_crawler")
                continue

        # 2、判断是否早于 当日- expiration_days ，如果是的话，舍弃
        expiration_date = datetime.now() - timedelta(days=expiration_days)
        expiration_date = expiration_date.strftime('%Y-%m-%d')
        article_date = int(article['publish_time'])
        if article_date < int(expiration_date.replace('-', '')):
            logger.info(f"publish date is {article_date}, too old, skip")
            continue

        article['source'] = source
        if cache[url]:
            article['abstract'] = cache[url]

        # 3、使用content从中提炼信息
        insights = get_info(f"标题：{article['title']}\n\n内容：{article['content']}")
        # 提炼info失败的article不入库，不然在existing里面后面就再也不会处理了，但提炼成功没有insight的article需要入库，后面不再分析。

        # 4、article入库
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
        # insight 比对去重与合并, article打标签，insight入库
        article_tags = set()
        # 从数据库中读取过去expiration_days的insight记录，避免重复
        old_insights = pb.read(collection_name='insights', filter=f"updated>'{expiration_date}'", fields=['id', 'tag', 'content', 'articles'])
        for insight in insights:
            article_tags.add(insight['tag'])
            insight['articles'] = [article_id]
            # 从old_insights 中挑出相同tag的insight，组成 content: id 的反查字典
            old_insight_dict = {i['content']: i for i in old_insights if i['tag'] == insight['tag']}
            # 因为要比较的是抽取出来的信息短语是否讲的是一个事情，用向量模型计算相似度未必适合且过重
            # 因此这里使用一个简化的方案，直接使用jieba分词器，计算两个短语之间重叠的词语是否超过90%
            similar_insights = compare_phrase_with_list(insight['content'], list(old_insight_dict.keys()), 0.65)
            if similar_insights:
                to_rewrite = similar_insights + [insight['content']]
                new_info_content = info_rewrite(to_rewrite, logger)
                if not new_info_content:
                    continue
                insight['content'] = new_info_content
                # 合并关联article、删除旧insight
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
