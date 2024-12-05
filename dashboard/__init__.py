import os
import time
import json
import uuid
from get_report import get_report, logger, pb
from get_search import search_insight
from tranlsation_volcengine import text_translate


class BackendService:
    def __init__(self):
        self.project_dir = os.environ.get("PROJECT_DIR", "")
        # 1. base initialization
        self.cache_url = os.path.join(self.project_dir, 'backend_service')
        os.makedirs(self.cache_url, exist_ok=True)

        # 2. load the llm
        # self.llm = LocalLlmWrapper()
        self.memory = {}
        # self.scholar = Scholar(initial_file_dir=os.path.join(self.project_dir, "files"), use_gpu=use_gpu)
        logger.info('backend service init success.')

    def report(self, insight_id: str, topics: list[str], comment: str) -> dict:
        logger.debug(f'got new report request insight_id {insight_id}')
        insight = pb.read('agents', filter=f'id="{insight_id}"')
        if not insight:
            logger.error(f'insight {insight_id} not found')
            return self.build_out(-2, 'insight not found')

        article_ids = insight[0]['articles']
        if not article_ids:
            logger.error(f'insight {insight_id} has no articles')
            return self.build_out(-2, 'can not find articles for insight')

        article_list = [pb.read('articles', fields=['title', 'abstract', 'content', 'url', 'publish_time'], filter=f'id="{_id}"')
                        for _id in article_ids]
        article_list = [_article[0] for _article in article_list if _article]

        if not article_list:
            logger.debug(f'{insight_id} has no valid articles')
            return self.build_out(-2, f'{insight_id} has no valid articles')

        content = insight[0]['content']
        if insight_id in self.memory:
            memory = self.memory[insight_id]
        else:
            memory = ''

        docx_file = os.path.join(self.cache_url, f'{insight_id}_{uuid.uuid4()}.docx')
        flag, memory = get_report(content, article_list, memory, topics, comment, docx_file)
        self.memory[insight_id] = memory

        if flag:
            file = open(docx_file, 'rb')
            message = pb.upload('agents', insight_id, 'docx', f'{insight_id}.docx', file)
            file.close()
            if message:
                logger.debug(f'report success finish and update to: {message}')
                return self.build_out(11, message)
            else:
                logger.error(f'{insight_id} report generate successfully, however failed to update to pb.')
                return self.build_out(-2, 'report generate successfully, however failed to update to pb.')
        else:
            logger.error(f'{insight_id} failed to generate report, finish.')
            return self.build_out(-11, 'report generate failed.')

    def build_out(self, flag: int, answer: str = "") -> dict:
        return {"flag": flag, "result": [{"type": "text", "answer": answer}]}

    def translate(self, article_ids: list[str]) -> dict:
        """
        just for chinese users
        """
        logger.debug(f'got new translate task {article_ids}')
        flag = 11
        msg = ''
        key_cache = []
        en_texts = []
        k = 1
        for article_id in article_ids:
            raw_article = pb.read(collection_name='articles', fields=['abstract', 'title', 'translation_result'], filter=f'id="{article_id}"')
            if not raw_article or not raw_article[0]:
                logger.warning(f'get article {article_id} failed, skipping')
                flag = -2
                msg += f'get article {article_id} failed, skipping\n'
                continue
            if raw_article[0]['translation_result']:
                logger.debug(f'{article_id} translation_result already exist, skipping')
                continue

            key_cache.append(article_id)
            en_texts.append(raw_article[0]['title'])
            en_texts.append(raw_article[0]['abstract'])

            if len(en_texts) < 16:
                continue

            logger.debug(f'translate process - batch {k}')
            translate_result = text_translate(en_texts, logger=logger)
            if translate_result and len(translate_result) == 2*len(key_cache):
                for i in range(0, len(translate_result), 2):
                    related_id = pb.add(collection_name='article_translation', body={'title': translate_result[i], 'abstract': translate_result[i+1], 'raw': key_cache[int(i/2)]})
                    if not related_id:
                        logger.warning(f'write article_translation {key_cache[int(i/2)]} failed')
                    else:
                        _ = pb.update(collection_name='articles', id=key_cache[int(i/2)], body={'translation_result': related_id})
                        if not _:
                            logger.warning(f'update article {key_cache[int(i/2)]} failed')
                logger.debug('done')
            else:
                flag = -6
                logger.warning(f'translate process - api out of service, can not continue job, aborting batch {key_cache}')
                msg += f'failed to batch {key_cache}'

            en_texts = []
            key_cache = []

            # 10次停1s，避免qps超载
            k += 1
            if k % 10 == 0:
                logger.debug('max token limited - sleep 1s')
                time.sleep(1)

        if en_texts:
            logger.debug(f'translate process - batch {k}')
            translate_result = text_translate(en_texts, logger=logger)
            if translate_result and len(translate_result) == 2*len(key_cache):
                for i in range(0, len(translate_result), 2):
                    related_id = pb.add(collection_name='article_translation', body={'title': translate_result[i], 'abstract': translate_result[i+1], 'raw': key_cache[int(i/2)]})
                    if not related_id:
                        logger.warning(f'write article_translation {key_cache[int(i/2)]} failed')
                    else:
                        _ = pb.update(collection_name='articles', id=key_cache[int(i/2)], body={'translation_result': related_id})
                        if not _:
                            logger.warning(f'update article {key_cache[int(i/2)]} failed')
                logger.debug('done')
            else:
                logger.warning(f'translate process - api out of service, can not continue job, aborting batch {key_cache}')
                msg += f'failed to batch {key_cache}'
                flag = -6
        logger.debug('translation job done.')
        return self.build_out(flag, msg)

    def more_search(self, insight_id: str) -> dict:
        logger.debug(f'got search request for insight： {insight_id}')
        insight = pb.read('agents', filter=f'id="{insight_id}"')
        if not insight:
            logger.error(f'insight {insight_id} not found')
            return self.build_out(-2, 'insight not found')

        article_ids = insight[0]['articles']
        if article_ids:
            article_list = [pb.read('articles', fields=['url'], filter=f'id="{_id}"') for _id in article_ids]
            url_list = [_article[0]['url'] for _article in article_list if _article]
        else:
            url_list = []

        flag, search_result = search_insight(insight[0]['content'], logger, url_list)
        if flag <= 0:
            logger.debug('no search result, nothing happen')
            return self.build_out(flag, 'search engine error or no result')

        for item in search_result:
            new_article_id = pb.add(collection_name='articles', body=item)
            if new_article_id:
                article_ids.append(new_article_id)
            else:
                logger.warning(f'add article {item} failed, writing to cache_file')
                with open(os.path.join(self.cache_url, 'cache_articles.json'), 'a', encoding='utf-8') as f:
                    json.dump(item, f, ensure_ascii=False, indent=4)

        message = pb.update(collection_name='agents', id=insight_id, body={'articles': article_ids})
        if message:
            logger.debug(f'insight search success finish and update to: {message}')
            return self.build_out(11, insight_id)
        else:
            logger.error(f'{insight_id} search success, however failed to update to pb.')
            return self.build_out(-2, 'search success, however failed to update to pb.')
