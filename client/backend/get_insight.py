from embeddings import embed_model, reranker
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain.retrievers import ContextualCompressionRetriever
from llms.dashscope_wrapper import dashscope_llm
from general_utils import isChinesePunctuation, is_chinese
from tranlsation_volcengine import text_translate
import time
import re
from pb_api import pb


max_tokens = 4000
relation_theshold = 0.525

role_config = pb.read(collection_name='roleplays', filter=f'activated=True')
_role_config_id = ''
if role_config:
    character = role_config[0]['character']
    focus = role_config[0]['focus']
    focus_type = role_config[0]['focus_type']
    good_sample1 = role_config[0]['good_sample1']
    good_sample2 = role_config[0]['good_sample2']
    bad_sample = role_config[0]['bad_sample']
    _role_config_id = role_config[0]['id']
else:
    character, good_sample1, focus, focus_type, good_sample2, bad_sample = '', '', '', '', '', ''

if not character:
    character = input('\033[0;32m 请为首席情报官指定角色设定（eg. 来自中国的网络安全情报专家）：\033[0m\n')
    _role_config_id = pb.add(collection_name='roleplays', body={'character': character, 'activated': True})

if not _role_config_id:
    raise Exception('pls check pb data, 无法获取角色设定')

if not (focus and focus_type and good_sample1 and good_sample2 and bad_sample):
    focus = input('\033[0;32m 请为首席情报官指定关注点（eg. 中国关注的网络安全新闻）：\033[0m\n')
    focus_type = input('\033[0;32m 请为首席情报官指定关注点类型（eg. 网络安全新闻）：\033[0m\n')
    good_sample1 = input('\033[0;32m 请给出一个你期望的情报描述示例（eg. 黑客组织Rhysida声称已入侵中国国有能源公司）: \033[0m\n')
    good_sample2 = input('\033[0;32m 请再给出一个理想示例（eg. 差不多一百万份包含未成年人数据（包括家庭地址和照片）的文件对互联网上的任何人都开放，对孩子构成威胁）: \033[0m\n')
    bad_sample = input('\033[0;32m 请给出一个你不期望的情报描述示例（eg. 黑客组织活动最近频发）: \033[0m\n')
    _ = pb.update(collection_name='roleplays', id=_role_config_id, body={'focus': focus, 'focus_type': focus_type, 'good_sample1': good_sample1, 'good_sample2': good_sample2, 'bad_sample': bad_sample})

# 实践证明，如果强调让llm挖掘我国值得关注的线索，则挖掘效果不好（容易被新闻内容误导，错把别的国家当成我国，可能这时新闻内有我国这样的表述）
# step by step 如果是内心独白方式，输出格式包含两种，难度增加了，qwen-max不能很好的适应，也许可以改成两步，第一步先输出线索列表，第二步再会去找对应的新闻编号
# 但从实践来看，这样做的性价比并不高，且会引入新的不确定性。
_first_stage_prompt = f'''你是一名{character}，你将被给到一个新闻列表，新闻文章用XML标签分隔。请对此进行分析，挖掘出特别值得{focus}线索。你给出的线索应该足够具体，而不是同类型新闻的归类描述，好的例子如：
"""{good_sample1}"""
不好的例子如：
"""{bad_sample}"""

请从头到尾仔细阅读每一条新闻的内容，不要遗漏，然后列出值得关注的线索，每条线索都用一句话进行描述，最终按一条一行的格式输出，并整体用三引号包裹，如下所示：
"""
{good_sample1}
{good_sample2}
"""

不管新闻列表是何种语言，请仅用中文输出分析结果。'''

_rewrite_insight_prompt = f'''你是一名{character}，你将被给到一个新闻列表，新闻文章用XML标签分隔。请对此进行分析，从中挖掘出一条最值得关注的{focus_type}线索。你给出的线索应该足够具体，而不是同类型新闻的归类描述，好的例子如：
"""{good_sample1}"""
不好的例子如：
"""{bad_sample}"""

请保证只输出一条最值得关注的线索，线索请用一句话描述，并用三引号包裹输出，如下所示：
"""{good_sample1}"""

不管新闻列表是何种语言，请仅用中文输出分析结果。'''


def _parse_insight(article_text: str, cache: dict, logger=None) -> (bool, dict):
    input_length = len(cache)
    result = dashscope_llm([{'role': 'system', 'content': _first_stage_prompt}, {'role': 'user', 'content': article_text}],
                           'qwen1.5-72b-chat', logger=logger)
    if result:
        pattern = re.compile(r'\"\"\"(.*?)\"\"\"', re.DOTALL)
        result = pattern.findall(result)
    else:
        logger.warning('1st-stage llm generate failed: no result')

    if result:
        try:
            results = result[0].split('\n')
            results = [_.strip() for _ in results if _.strip()]
            to_del = []
            to_add = []
            for element in results:
                if "；" in element:
                    to_del.append(element)
                    to_add.extend(element.split('；'))
            for element in to_del:
                results.remove(element)
            results.extend(to_add)
            results = list(set(results))
            for text in results:
                logger.debug(f'parse result: {text}')
                # qwen-72b-chat 特例
                # potential_insight = re.sub(r'编号[^：]*：', '', text)
                potential_insight = text.strip()
                if len(potential_insight) < 2:
                    logger.debug(f'parse failed: not enough potential_insight: {potential_insight}')
                    continue
                if isChinesePunctuation(potential_insight[-1]):
                    potential_insight = potential_insight[:-1]
                if potential_insight in cache:
                    continue
                else:
                    cache[potential_insight] = []
        except Exception as e:
            logger.debug(f'parse failed: {e}')

    output_length = len(cache)
    if input_length == output_length:
        return True, cache
    return False, cache


def _rewrite_insight(context: str, logger=None) -> (bool, str):
    result = dashscope_llm([{'role': 'system', 'content': _rewrite_insight_prompt}, {'role': 'user', 'content': context}],
                           'qwen1.5-72b-chat', logger=logger)
    if result:
        pattern = re.compile(r'\"\"\"(.*?)\"\"\"', re.DOTALL)
        result = pattern.findall(result)
    else:
        logger.warning(f'insight rewrite process llm generate failed: no result')

    if not result:
        return True, ''
    try:
        results = result[0].split('\n')
        text = results[0].strip()
        logger.debug(f'parse result: {text}')
        if len(text) < 2:
            logger.debug(f'parse failed: not enough potential_insight: {text}')
            return True, ''
        if isChinesePunctuation(text[-1]):
            text = text[:-1]
    except Exception as e:
        logger.debug(f'parse failed: {e}')
        return True, ''
    return False, text


def get_insight(articles: dict, titles: dict, logger=None) -> list:
    context = ''
    cache = {}
    for value in articles.values():
        if value['abstract']:
            text = value['abstract']
        else:
            if value['title']:
                text = value['title']
            else:
                if value['content']:
                    text = value['content']
                else:
                    continue
        # 这里不使用long context是因为阿里灵积经常检查出输入敏感词，但又不给敏感词反馈，对应批次只能放弃，用long context风险太大
        # 另外long context中间部分llm可能会遗漏
        context += f"<article>{text}</article>\n"
        if len(context) < max_tokens:
            continue

        flag, cache = _parse_insight(context, cache, logger)
        if flag:
            logger.warning(f'following articles may not be completely analyzed: \n{context}')

        context = ''
        # 据说频繁调用会引发性能下降，每次调用后休息1s。现在轮替调用qwen-72b和max，所以不必了。
        time.sleep(1)
    if context:
        flag, cache = _parse_insight(context, cache, logger)
        if flag:
            logger.warning(f'following articles may not be completely analyzed: \n{context}')

    if not cache:
        logger.warning('no insights found')
        return []

    # second stage: 匹配insights和article_titles
    title_list = [Document(page_content=key, metadata={}) for key, value in titles.items()]
    retriever = FAISS.from_documents(title_list, embed_model,
                                     distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT).as_retriever(search_type="similarity",
                                                                                                        search_kwargs={"score_threshold": relation_theshold, "k": 10})
    compression = ContextualCompressionRetriever(base_compressor=reranker, base_retriever=retriever)

    for key in cache.keys():
        logger.debug(f'searching related articles for insight: {key}')
        rerank_results = compression.get_relevant_documents(key)
        for i in range(len(rerank_results)):
            if rerank_results[i].metadata['relevance_score'] < relation_theshold:
                break
            cache[key].append(titles[rerank_results[i].page_content])
            if titles[rerank_results[i].page_content] not in articles:
                articles[titles[rerank_results[i].page_content]] = {'title': rerank_results[i].page_content}
        logger.info(f'{key} - {cache[key]}')

    # third stage：对于对应文章重叠率超过25%的合并，然后对于有多个文章的，再次使用llm生成insight
    # 因为实践中发现，第一次insight召回的文章标题可能都很相关，但是汇总起来却指向另一个角度的insight
    def calculate_overlap(list1, list2):
        # 计算两个列表的交集长度
        intersection_length = len(set(list1).intersection(set(list2)))
        # 计算重合率
        overlap_rate = intersection_length / min(len(list1), len(list2))
        return overlap_rate >= 0.75

    merged_dict = {}
    for key, value in cache.items():
        if not value:
            continue
        merged = False
        for existing_key, existing_value in merged_dict.items():
            if calculate_overlap(value, existing_value):
                merged_dict[existing_key].extend(value)
                merged = True
                break
        if not merged:
            merged_dict[key] = value

    cache = {}
    for key, value in merged_dict.items():
        value = list(set(value))
        if len(value) > 1:
            context = ''
            for _id in value:
                context += f"<article>{articles[_id]['title']}</article>\n"
                if len(context) >= max_tokens:
                    break
            if not context:
                continue

            flag, new_insight = _rewrite_insight(context, logger)
            if flag:
                logger.warning(f'insight {key} may contain wrong')
                cache[key] = value
            else:
                if cache:
                    title_list = [Document(page_content=key, metadata={}) for key, value in cache.items()]
                    retriever = FAISS.from_documents(title_list, embed_model,
                                                     distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT).as_retriever(
                        search_type="similarity",
                        search_kwargs={"score_threshold": 0.85, "k": 1})
                    compression = ContextualCompressionRetriever(base_compressor=reranker, base_retriever=retriever)
                    rerank_results = compression.get_relevant_documents(new_insight)
                    if rerank_results and rerank_results[0].metadata['relevance_score'] > 0.85:
                        logger.debug(f"{new_insight} is too similar to {rerank_results[0].page_content}, merging")
                        cache[rerank_results[0].page_content].extend(value)
                        cache[rerank_results[0].page_content] = list(set(cache[rerank_results[0].page_content]))
                    else:
                        cache[new_insight] = value
                else:
                    cache[new_insight] = value
        else:
            cache[key] = value

    # 排序，对应articles越多的越靠前
    # sorted_cache = sorted(cache.items(), key=lambda x: len(x[1]), reverse=True)
    logger.info('re-ranking ressult:')
    new_cache = []
    for key, value in cache.items():
        if not is_chinese(key):
            translate_text = text_translate([key], target_language='zh', logger=logger)
            if translate_text:
                key = translate_text[0]
        logger.info(f'{key} - {value}')
        new_cache.append({'content': key, 'articles': value})

    return new_cache
