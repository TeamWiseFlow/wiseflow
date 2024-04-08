import os
import time
import json
import uuid
from get_logger import get_logger
from pb_api import PbTalker
from get_report import get_report
from get_search import search_insight
from tranlsation_volcengine import text_translate


class BackendService:
    def __init__(self, name: str = 'backend_server'):
        self.name = name
        self.project_dir = os.environ.get("PROJECT_DIR", "")
        # 1. base initialization
        self.cache_url = os.path.join(self.project_dir, name)
        os.makedirs(self.cache_url, exist_ok=True)
        self.logger = get_logger(name=self.name, file=os.path.join(self.project_dir, f'{self.name}.log'))

        # 2. load the llm
        # self.llm = LocalLlmWrapper()
        self.pb = PbTalker(self.logger)
        self.memory = {}
        # self.scholar = Scholar(initial_file_dir=os.path.join(self.project_dir, "files"), use_gpu=use_gpu)
        self.logger.info(f'{self.name} init success.')

    def report(self, insight_id: str, topics: list[str], comment: str) -> dict:
        """
        :param insight_id: insight在pb中的id
        :param topics:  书写报告的主题和大纲，必传，第一个值是标题，后面是段落标题，可以传空列表，AI就自由发挥
        :param comment:  修改意见，可以传‘’
        :return: 成功的话返回更新后的insight_id（其实跟原id一样）, 不成功返回空字符
        """
        self.logger.debug(f'got new report request insight_id {insight_id}')
        insight = self.pb.read('insights', filter=f'id="{insight_id}"')
        if not insight:
            self.logger.error(f'insight {insight_id} not found')
            return self.build_out(-2, 'insight not found')

        article_ids = insight[0]['articles']
        if not article_ids:
            self.logger.error(f'insight {insight_id} has no articles')
            return self.build_out(-2, 'can not find articles for insight')

        article_list = [self.pb.read('articles',
                                     fields=['title', 'abstract', 'content', 'url', 'publish_time'], filter=f'id="{_id}"')
                        for _id in article_ids]
        article_list = [_article[0] for _article in article_list if _article]

        if not article_list:
            self.logger.debug(f'{insight_id} has no valid articles')
            return self.build_out(-2, f'{insight_id} has no valid articles')

        content = insight[0]['content']
        # 这里把所有相关文章的content都要翻译成中文了，分析使用中文，因为涉及到部分专有词汇维护在火山的账户词典上，大模型并不了解
        # 发现翻译为中文后，引发灵积模型敏感词检测概率增加了，暂时放弃……
        if insight_id in self.memory:
            memory = self.memory[insight_id]
        else:
            memory = ''

        docx_file = os.path.join(self.cache_url, f'{insight_id}_{uuid.uuid4()}.docx')
        flag, memory = get_report(content, article_list, memory, topics, comment, docx_file, logger=self.logger)
        self.memory[insight_id] = memory

        if flag:
            file = open(docx_file, 'rb')
            message = self.pb.upload('insights', insight_id, 'docx', f'{insight_id}.docx', file)
            file.close()
            if message:
                self.logger.debug(f'report success finish and update to pb-{message}')
                return self.build_out(11, message)
            else:
                self.logger.error(f'{insight_id} report generate successfully, however failed to update to pb.')
                return self.build_out(-2, 'report generate successfully, however failed to update to pb.')
        else:
            self.logger.error(f'{insight_id} failed to generate report, finish.')
            return self.build_out(-11, 'report generate failed.')

    def build_out(self, flag: int, answer: str = "") -> dict:
        return {"flag": flag, "result": [{"type": "text", "answer": answer}]}

    def translate(self, article_ids: list[str]) -> dict:
        """
        :param article_ids: 待翻译的文章id列表
        :return: 成功的话flag 11。负数为报错，但依然可能部分任务完成，可以稍后再次调用
        返回中的msg记录了可能的错误
        这个函数的作用是遍历列表中的id， 如果对应article——id中没有translation_result，则触发翻译，并更新article——id记录
        执行本函数后，如果收到flag 11，则可以再次从pb中请求article-id对应的translation_result
        """
        self.logger.debug(f'got new translate task {article_ids}')
        flag = 11
        msg = ''
        key_cache = []
        en_texts = []
        k = 1
        for article_id in article_ids:
            raw_article = self.pb.read(collection_name='articles', fields=['abstract', 'title', 'translation_result'],
                                       filter=f'id="{article_id}"')
            if not raw_article or not raw_article[0]:
                self.logger.warning(f'get article {article_id} failed, skipping')
                flag = -2
                msg += f'get article {article_id} failed, skipping\n'
                continue
            if raw_article[0]['translation_result']:
                self.logger.debug(f'{article_id} translation_result already exist, skipping')
                continue

            key_cache.append(article_id)
            en_texts.append(raw_article[0]['title'])
            en_texts.append(raw_article[0]['abstract'])

            if len(en_texts) < 16:
                continue

            self.logger.debug(f'translate process - batch {k}')
            translate_result = text_translate(en_texts, logger=self.logger)
            if translate_result and len(translate_result) == 2*len(key_cache):
                for i in range(0, len(translate_result), 2):
                    related_id = self.pb.add(collection_name='article_translation',
                                             body={'title': translate_result[i], 'abstract': translate_result[i+1],
                                                   'raw': key_cache[int(i/2)]})
                    if not related_id:
                        self.logger.warning(f'write article_translation {key_cache[int(i/2)]} failed')
                    else:
                        _ = self.pb.update(collection_name='articles', id=key_cache[int(i/2)],
                                           body={'translation_result': related_id})
                        if not _:
                            self.logger.warning(f'update article {key_cache[int(i/2)]} failed')
                self.logger.debug('done')
            else:
                flag = -6
                self.logger.warning(f'translate process - api out of service, can not continue job, aborting batch {key_cache}')
                msg += f'failed to batch {key_cache}'

            en_texts = []
            key_cache = []

            # 10次停1s，避免qps超载
            k += 1
            if k % 10 == 0:
                self.logger.debug('max token limited - sleep 1s')
                time.sleep(1)

        if en_texts:
            self.logger.debug(f'translate process - batch {k}')
            translate_result = text_translate(en_texts, logger=self.logger)
            if translate_result and len(translate_result) == 2*len(key_cache):
                for i in range(0, len(translate_result), 2):
                    related_id = self.pb.add(collection_name='article_translation',
                                             body={'title': translate_result[i], 'abstract': translate_result[i+1],
                                                   'raw': key_cache[int(i/2)]})
                    if not related_id:
                        self.logger.warning(f'write article_translation {key_cache[int(i/2)]} failed')
                    else:
                        _ = self.pb.update(collection_name='articles', id=key_cache[int(i/2)],
                                           body={'translation_result': related_id})
                        if not _:
                            self.logger.warning(f'update article {key_cache[int(i/2)]} failed')
                self.logger.debug('done')
            else:
                self.logger.warning(f'translate process - api out of service, can not continue job, aborting batch {key_cache}')
                msg += f'failed to batch {key_cache}'
                flag = -6
        self.logger.debug('translation job done.')
        return self.build_out(flag, msg)

    def more_search(self, insight_id: str) -> dict:
        """
        :param insight_id: insight在pb中的id
        :return: 成功的话返回更新后的insight_id（其实跟原id一样）, 不成功返回空字符
        """
        self.logger.debug(f'got search request for insight： {insight_id}')
        insight = self.pb.read('insights', filter=f'id="{insight_id}"')
        if not insight:
            self.logger.error(f'insight {insight_id} not found')
            return self.build_out(-2, 'insight not found')

        article_ids = insight[0]['articles']
        if article_ids:
            article_list = [self.pb.read('articles', fields=['url'], filter=f'id="{_id}"') for _id in article_ids]
            url_list = [_article[0]['url'] for _article in article_list if _article]
        else:
            url_list = []

        flag, search_result = search_insight(insight[0]['content'], url_list, logger=self.logger)
        if flag <= 0:
            self.logger.debug('no search result, nothing happen')
            return self.build_out(flag, 'search engine error or no result')

        for item in search_result:
            new_article_id = self.pb.add(collection_name='articles', body=item)
            if new_article_id:
                article_ids.append(new_article_id)
            else:
                self.logger.warning(f'add article {item} failed, writing to cache_file')
                with open(os.path.join(self.cache_url, 'cache_articles.json'), 'a', encoding='utf-8') as f:
                    json.dump(item, f, ensure_ascii=False, indent=4)

        message = self.pb.update(collection_name='insights', id=insight_id, body={'articles': article_ids})
        if message:
            self.logger.debug(f'insight search success finish and update to pb-{message}')
            return self.build_out(11, insight_id)
        else:
            self.logger.error(f'{insight_id} search success, however failed to update to pb.')
            return self.build_out(-2, 'search success, however failed to update to pb.')
