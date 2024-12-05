from core.llms.openai_wrapper import openai_llm as llm
# from core.llms.siliconflow_wrapper import sfa_llm
import re
from core.utils.general_utils import is_chinese, extract_and_convert_dates, extract_urls
from loguru import logger
from core.utils.pb_api import PbTalker
import os
from datetime import datetime, date
from urllib.parse import urlparse
import json_repair


class GeneralInfoExtractor:
    def __init__(self, pb: PbTalker, _logger: logger) -> None:
        self.pb = pb
        self.logger = _logger
        self.model = os.environ.get("PRIMARY_MODEL", "Qwen/Qwen2.5-7B-Instruct") # better to use "Qwen/Qwen2.5-14B-Instruct"
        self.secondary_model = os.environ.get("SECONDARY_MODEL", "THUDM/glm-4-9b-chat")

        # collect tags user set in pb database and determin the system prompt language based on tags
        focus_data = pb.read(collection_name='focus_points', filter=f'activated=True')
        if not focus_data:
            self.logger.info('no activated tag found, will ask user to create one')
            focus = input('It seems you have not set any focus point, WiseFlow need the specific focus point to guide the following info extract job.'
                          'so please input one now. describe what info you care about shortly: ')
            explanation = input('Please provide more explanation for the focus point (if not necessary, pls just type enter: ')
            focus_data.append({"name": focus, "explaination": explanation,
                               "id": pb.add('focus_points', {"focuspoint": focus, "explanation": explanation})})

        self.focus_list = [item["focuspoint"] for item in focus_data]
        self.focus_dict = {item["focuspoint"]: item["id"] for item in focus_data}
        focus_statement = ''
        for item in focus_data:
            tag = item["name"]
            expl = item["explaination"]
            focus_statement = f"{focus_statement}#{tag}\n"
            if expl:
                focus_statement = f"{focus_statement}解释：{expl}\n"

        if is_chinese(focus_statement):
            self.get_info_prompt = f'''作为信息提取助手，你的任务是从给定的网页文本中提取与以下用户兴趣点相关的内容。兴趣点列表及其解释如下：

{focus_statement}\n
在进行信息提取时，请遵循以下原则：

- 理解每个兴趣点的含义，确保提取的内容与之相关。
- 如果兴趣点有进一步的解释，确保提取的内容符合这些解释的范围。
- 忠于原文，你的任务是从网页文本中识别和提取与各个兴趣点相关的信息，并不是总结和提炼。
- 不管给定的原文是何种语言，请保证使用中文输出你的提取结果。

另外请注意给定的网页文本是通过爬虫程序从html代码中提取出来的，所以请忽略里面不必要的空格、换行符等。'''
            self.get_info_suffix = '''如果上述网页文本中包含兴趣点相关的内容，请按照以下json格式输出提取的信息（文本中可能包含多条有用信息，请不要遗漏）：
[{"focus": 兴趣点名称, "content": 提取的内容}]

示例：
[{"focus": "旅游景点", "content": "北京故宫，地址：北京市东城区景山前街4号，开放时间：8:30-17:00"}, {"focus": "美食推荐", "content": "来王府井小吃街必吃北京烤鸭、炸酱面"}]

如果网页文本中不包含任何与兴趣点相关的信息，请仅输出：[]。'''
            self.get_more_link_prompt = f"作为一位高效的信息筛选助手，你的任务是根据给定的兴趣点，从给定的文本及其对应的URL中挑选出最值得关注的URL。兴趣点及其解释如下：\n\n{focus_statement}"
            self.get_more_link_suffix = "请逐条分析上述 文本：url 对。首先输出你的分析依据，然后给出是否挑选它的结论，如果决定挑选该条，在结论后复制输出该条的 url，否则的话直接进入下一条的分析。请一条一条的分析，不要漏掉任何一条。"
        else:
            self.get_info_prompt = f'''As an information extraction assistant, your task is to extract content related to the following user focus points from the given web page text. The list of focus points and their explanations is as follows:

{focus_statement}\n
When extracting information, please follow the principles below:

- Understand the meaning of each focus point and ensure that the extracted content is relevant to it.
- If a focus point has further explanations, ensure that the extracted content conforms to the scope of these explanations.
- Stay true to the original text; your task is to identify and extract information related to each focus point from the web page text, not to summarize or refine it.

Please note that the given web page text is extracted from HTML code via a crawler, so please ignore any unnecessary spaces, line breaks, etc.'''
            self.get_info_suffix = '''If the above webpage text contains content related to points of interest, please output the extracted information in the following JSON format (the text may contain multiple useful pieces of information, do not miss any):
[{"focus": "Point of Interest Name", "content": "Extracted Content"}]

Example:
[{"focus": "Tourist Attraction", "content": "The Forbidden City, Beijing, Address: No. 4 Jingshan Front Street, Dongcheng District, Opening Hours: 8:30-17:00"}, {"focus": "Food Recommendation", "content": "Must-try at Wangfujing Snack Street: Beijing Roast Duck, Noodles with Soybean Paste"}]

If the webpage text does not contain any information related to points of interest, please output only: []'''
            self.get_more_link_prompt = f"As an efficient information filtering assistant, your task is to select the most noteworthy URLs from a set of texts and their corresponding URLs based on the given focus points. The focus points and their explanations are as follows:\n\n{focus_statement}"
            self.get_more_link_suffix =  "Please analyze the above text: URL pairs. First, output your analysis basis, and then give the conclusion on whether to select it. If you decide to select this item, then copy and output the URL of this item following the conclusion; otherwise, proceed directly to the analysis of the next item. Analyze one by one, do not miss any one."

    async def get_author_and_publish_date(self, text: str) -> tuple[str, str]:
        system_prompt = "As an information extraction assistant, your task is to accurately extract the source (or author) and publication date from the given webpage text. It is important to adhere to extracting the information directly from the original text. If the original text does not contain a particular piece of information, please replace it with NA"
        suffix = '''Please output the extracted information in the following JSON format:
{"source": source or article author (use "NA" if this information cannot be extracted), "publish_date": extracted publication date (keep only the year, month, and day; use "NA" if this information cannot be extracted)}'''

        content = f'<text>\n{text}\n</text>\n\n{suffix}'
        llm_output = await llm([{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': content}],
                           model=self.secondary_model, max_tokens=50, temperature=0.1, response_format={"type": "json_object"})

        self.logger.debug(f'get_author_and_publish_date llm output:\n{llm_output}')
        if not llm_output:
            return '', ''
        result = json_repair.repair_json(llm_output, return_objects=True)
        self.logger.debug(f"decoded_object: {result}")
        if not isinstance(result, dict):
            self.logger.debug("failed to parse from llm output")
            return '', ''
        if 'source' not in result or 'publish_date' not in result:
            self.logger.debug("failed to parse from llm output")
            return '', ''

        return result['source'], result['publish_date']

    async def get_more_related_urls(self, link_dict: dict) -> set[str]:
        if not link_dict:
            return set()
        content = ''
        for key, value in link_dict.items():
            content = f"{content}{key}: {value}\n"
        result = await llm([{'role': 'system', 'content': self.get_more_link_prompt}, {'role': 'user', 'content': f'{content}\n{self.get_more_link_suffix}'}],
                           model=self.secondary_model, temperature=0.1)

        self.logger.debug(f'get_more_related_urls llm output:\n{result}')
        urls = extract_urls(result)
        raw_urls = list(link_dict.values())
        for url in urls:
            if url not in raw_urls:
                self.logger.debug(f"{url} not in link_dict, it's model's Hallucination")
                urls.remove(url)
        return urls

    async def get_info(self, text: str, domain: str) -> list[dict]:
        # logger.debug(f'receive new article_content:\n{article_content}')
        content = f'<text>\n{text}\n</text>\n\n{self.get_info_suffix}'
        result = await llm([{'role': 'system', 'content': self.get_info_prompt}, {'role': 'user', 'content': content}],
                           model=self.model, temperature=0.1, response_format={"type": "json_object"})













domain = urlparse(url).netloc

def get_info(article_content: str) -> list[dict]:
    # logger.debug(f'receive new article_content:\n{article_content}')
    result = openai_llm([{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': article_content}],
                        model=get_info_model, logger=logger, temperature=0.1)

    # results = pattern.findall(result)
    texts = result.split('<tag>')
    texts = [_.strip() for _ in texts if '</tag>' in _.strip()]
    if not texts:
        logger.debug(f'can not find info, llm result:\n{result}')
        return []

    cache = []
    for text in texts:
        try:
            strings = text.split('</tag>')
            tag = strings[0]
            tag = tag.strip()
            if tag not in focus_list:
                logger.info(f'tag not in focus_list: {tag}, aborting')
                continue
            info = strings[1]
            info = info.split('\n\n')
            info = info[0].strip()
        except Exception as e:
            logger.info(f'parse error: {e}')
            tag = ''
            info = ''

        if not info or not tag:
            logger.info(f'parse failed-{text}')
            continue

        if len(info) < 7:
            logger.info(f'info too short, possible invalid: {info}')
            continue

        if info.startswith('无相关信息') or info.startswith('该新闻未提及') or info.startswith('未提及'):
            logger.info(f'no relevant info: {text}')
            continue

        while info.endswith('"'):
            info = info[:-1]
            info = info.strip()

        # 拼接下来源信息
        sources = re.findall(r'\[from (.*?)]', article_content)
        if sources and sources[0]:
            info = f"[from {sources[0]}] {info}"

        cache.append({'content': info, 'tag': focus_dict[tag]})

    return cache
