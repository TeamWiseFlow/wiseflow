from llms.openai_wrapper import openai_llm as llm
# from core.llms.siliconflow_wrapper import sfa_llm
from utils.general_utils import is_chinese, extract_and_convert_dates, extract_urls
from loguru import logger
from utils.pb_api import PbTalker
import os, re
from datetime import datetime
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
            focus_data.append({"focuspoint": focus, "explanation": explanation,
                               "id": pb.add('focus_points', {"focuspoint": focus, "explanation": explanation})})

        # self.focus_list = [item["focuspoint"] for item in focus_data]
        self.focus_dict = {item["focuspoint"]: item["id"] for item in focus_data}
        focus_statement = ''
        for item in focus_data:
            tag = item["focuspoint"]
            expl = item["explanation"]
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
            self.get_more_link_suffix = '''请逐条分析，先逐一给出分析依据，最终将挑选出的 url 按一行一条的格式输出，最终输出的 url 列表整体用三引号包裹，三引号内不要有其他内容，如下是输出格式示例：
"""
url1
url2
...
"""'''
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
            self.get_more_link_suffix = '''Please analyze one by one, first give the analysis basis one by one, and finally output the selected URLs in a row-by-row format. The final output URL list is wrapped in three quotes as a whole, and there should be no other content in the three quotes. Here is an example of the output format:
"""
url1
url2
...
"""'''

    async def get_author_and_publish_date(self, text: str) -> tuple[str, str]:
        if not text:
            return "NA", "NA"

        if len(text) > 1024:
            text = f'{text[:500]}......{text[-500:]}'

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
            self.logger.warning("failed to parse from llm output")
            return '', ''
        if 'source' not in result or 'publish_date' not in result:
            self.logger.warning("failed to parse from llm output")
            return '', ''

        return result['source'], extract_and_convert_dates(result['publish_date'])

    async def get_more_related_urls(self, link_dict: dict, og_url: str) -> set[str]:
        if not link_dict:
            return set()
        self.logger.debug(f'{len(link_dict)} items to analyze')
        urls = set()
        content = ''
        for key, value in link_dict.items():
            content = f"{content}{key}: {value}\n"
            if len(content) > 512:
                result = await llm([{'role': 'system', 'content': self.get_more_link_prompt},
                                    {'role': 'user', 'content': f'{content}\n{self.get_more_link_suffix}'}],
                                   model=self.model, temperature=0.1)
                self.logger.debug(f'get_more_related_urls llm output:\n{result}')
                result = re.findall(r'"""(.*?)"""', result, re.DOTALL)
                if result:
                    result = result[0].strip()
                    # self.logger.debug(f"cleaned output: {result}")
                    urls.update(extract_urls(result))
                content = ''

        if content:
            result = await llm([{'role': 'system', 'content': self.get_more_link_prompt},
                                {'role': 'user', 'content': f'{content}\n{self.get_more_link_suffix}'}],
                               model=self.model, temperature=0.1)
            self.logger.debug(f'get_more_related_urls llm output:\n{result}')
            result = re.findall(r'"""(.*?)"""', result, re.DOTALL)
            if result:
                result = result[0].strip()
                # self.logger.debug(f"cleaned output: {result}")
                urls.update(extract_urls(result))

        raw_urls = set(link_dict.values())
        urls.discard(og_url)
        hallucination_urls = urls - raw_urls
        if hallucination_urls:
            self.logger.warning(f"{hallucination_urls} not in link_dict, it's model's Hallucination")

        return urls & raw_urls 

    async def get_info(self, text: str, info_pre_fix: str, link_dict: dict) -> list[dict]:
        if not text:
            return []

        content = f'<text>\n{text}\n</text>\n\n{self.get_info_suffix}'
        result = await llm([{'role': 'system', 'content': self.get_info_prompt}, {'role': 'user', 'content': content}],
                           model=self.model, temperature=0.1, response_format={"type": "json_object"})
        self.logger.debug(f'get_info llm output:\n{result}')
        if not result:
            return []

        result = json_repair.repair_json(result, return_objects=True)
        if not isinstance(result, list):
            self.logger.warning("failed to parse from llm output")
            return []
        if not result:
            self.logger.debug("no info found")
            return []

        system = '''判断给定的信息是否与网页文本相符。信息将用标签<info></info>包裹，网页文本则用<text></text>包裹。请遵循如下工作流程:
1、尝试找出网页文本中所有与信息对应的文本片段（可能有多处）；
2、基于这些片段给出是否相符的最终结论，最终结论仅为“是”或“否”'''
        suffix = '先输出找到的所有文本片段，再输出最终结论（仅为是或否）'

        final = []
        for item in result:
            if 'focus' not in item or 'content' not in item:
                self.logger.warning(f"not quality item: {item}, it's model's Hallucination")
                continue
            if item['focus'] not in self.focus_dict:
                self.logger.warning(f"{item['focus']} not in focus_list, it's model's Hallucination")
                continue
            if not item['content']:
                continue
            
            if item['content'] in link_dict:
                self.logger.debug(f"{item['content']} in link_dict, aborting")
                continue

            judge = await llm([{'role': 'system', 'content': system},
                               {'role': 'user', 'content': f'<info>\n{item["content"]}\n</info>\n\n<text>\n{text}\n</text>\n\n{suffix}'}],
                               model=self.secondary_model, temperature=0.1)
            self.logger.debug(f'judge llm output:\n{judge}')
            if not judge:
                self.logger.warning("failed to parse from llm output, skip checking")
                final.append({'tag': self.focus_dict[item['focus']], 'content': f"{info_pre_fix}{item['content']}"})
                continue

            to_save = False
            for i in range(min(7, len(judge))):
                char = judge[-1 - i]
                if char == '是':
                    to_save = True
                    break
                elif char == '否':
                    break
            if not to_save:
                self.logger.info(f"secondary model judge {item} not faithful to article text, aborting")
                continue
            final.append({'tag': self.focus_dict[item['focus']], 'content': f"{info_pre_fix}{item['content']}"})

        if not final:
            self.logger.info("no quality result from llm output")
        return final

    async def __call__(self, text: str, link_dict: dict, base_url: str, author: str = None, publish_date: str = None) -> tuple[list, set, str, str]:
        if not author and not publish_date and text:
            author, publish_date = await self.get_author_and_publish_date(text)

        if not author or author.lower() == 'na':
            author = urlparse(base_url).netloc

        if not publish_date or publish_date.lower() == 'na':
            publish_date = datetime.now().strftime('%Y-%m-%d')

        related_urls = await self.get_more_related_urls(link_dict, base_url)

        info_prefix = f"//{author} {publish_date}//"
        lines = text.split('\n')
        text = ''
        infos = []
        for line in lines:
            text = f'{text}{line}'
            if len(text) > 2048:
                cache = await self.get_info(text, info_prefix, link_dict)
                infos.extend(cache)
                text = ''
        if text:
            cache = await self.get_info(text, info_prefix, link_dict)
            infos.extend(cache)

        return infos, related_urls, author, publish_date
