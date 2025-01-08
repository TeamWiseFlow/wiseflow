# -*- coding: utf-8 -*-
import asyncio

from loguru import logger
import os, re
from utils.pb_api import PbTalker
from llms.openai_wrapper import openai_llm as llm
# from core.llms.siliconflow_wrapper import sfa_llm # or other llm wrapper
from utils.general_utils import is_chinese, extract_and_convert_dates


async def get_author_and_publish_date(text: str, model: str) -> tuple[str, str]:
    if not text:
        return "", ""

    if len(text) > 100:
        text = text[20:]

    if len(text) > 2048:
        text = f'{text[:2048]}......'

    system_prompt = "As an information extraction assistant, your task is to accurately extract the source (or author) and publication date from the given webpage text. It is important to adhere to extracting the information directly from the original text. If the original text does not contain a particular piece of information, please replace it with NA"
    suffix = '''Please output the extracted information in the following format(output only the result, no other content):
"""source or article author (use "NA" if this information cannot be extracted)//extracted publication date (keep only the year, month, and day; use "NA" if this information cannot be extracted)"""'''

    content = f'<text>\n{text}\n</text>\n\n{suffix}'
    llm_output = await llm([{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': content}],
                           model=model, max_tokens=50, temperature=0.1)

    ap_ = llm_output.strip().strip('"').strip('//')

    if '//' not in ap_:
        print(f"failed to parse from llm output: {ap_}")
        return '', ''

    ap = ap_.split('//')

    return ap[0], extract_and_convert_dates(ap[1])


async def extract_info_from_img(task: list, vl_model: str) -> dict:
    cache = {}
    for url in task:
        llm_output = await llm([{"role": "user",
        "content": [{"type": "image_url", "image_url": {"url": url, "detail": "high"}},
        {"type": "text", "text": "提取图片中的所有文字，如果图片不包含文字或者文字很少或者你判断图片仅是网站logo、商标、图标等，则输出NA。注意请仅输出提取出的文字，不要输出别的任何内容。"}]}],
        model=vl_model)

        cache[url] = llm_output
    return cache


def extract_info(llm_text: str):
    cache = set()
    extracted_result = re.findall(r'\"\"\"(.*?)\"\"\"', llm_text, re.DOTALL)
    if extracted_result:
        pass
    else:
        extracted_result = re.findall(r'```(.*?)```', llm_text, re.DOTALL)

    cache.add(extracted_result[-1])
    return cache


class GeneralInfoExtractor:
    def __init__(self, pb: PbTalker, _logger: logger) -> None:
        self.pb = pb
        self.logger = _logger
        self.model = os.environ.get("PRIMARY_MODEL", "")

        if not self.model:
            self.logger.error("PRIMARY_MODEL not set, can't continue")
            raise ValueError("PRIMARY_MODEL not set, please set it in environment variables or edit core/.env")

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
            focus_statement = f"{focus_statement}//{tag}//\n"
            if expl:
                if is_chinese(expl):
                    focus_statement = f"{focus_statement}解释：{expl}\n"
                else:
                    focus_statement = f"{focus_statement}Explanation: {expl}\n"

        if is_chinese(focus_statement):
            self.get_info_prompt = f'''你将被给到一段使用<text></text>标签包裹的网页文本，请分别按如下关注点对网页文本提炼摘要。关注点列表及其解释如下：

{focus_statement}\n
在提炼摘要时，请遵循以下原则：
- 理解每个关注点的含义以及进一步的解释（如有），确保摘要与关注点强相关并符合解释（如有）的范围
- 摘要应当详实、充分，使用简体中文（如果原文是英文，请翻译成简体中文）
- 摘要信息务必忠于原文'''

            self.get_info_suffix = '''请对关注点逐一生成摘要，不要遗漏任何关注点，如果网页文本与关注点无关，可以对应输出"NA"。输出结果整体用三引号包裹，三引号内不要有其他内容。如下是输出格式示例：
"""
//关注点1//
摘要1
//关注点2//
摘要2
//关注点3//
NA
...
"""'''
            self.get_more_link_prompt = f'''你将被给到数行格式为"<编号>//内容//"的文本，你的任务是逐条分析这些文本，并分别与如下关注点之一相关联。关注点列表及其解释如下：

{focus_statement}\n
在进行关联分析时，请遵循以下原则：

- 理解每个关注点的含义
- 如果关注点有进一步的解释，确保提取的内容符合这些解释的范围'''

            self.get_more_link_suffix = '''请分行逐条输出结果，每一条的输出格式为"<编号>//关注点名称//"，如果某条内容不与任何关注点相关，请输出"<编号>//NA//"。输出结果整体用三引号包裹，三引号内不要有其他内容。如下是输出格式示例：
"""
<t1>//关注点1名称//
<t2>//关注点2名称//
<t3>//NA//
...
"""'''

        else:
            self.get_info_prompt = f'''You will be given a webpage text wrapped in <text></text> tags. Please extract summaries from the text according to the following focus points. The list of focus points and their explanations are as follows:

{focus_statement}\n
When extracting summaries, please follow these principles:
- Understand the meaning of each focus point and its explanation (if any), ensure the summary strongly relates to the focus point and aligns with the explanation (if any)
- The summary should be detailed and comprehensive
- The summary should be faithful to the original text'''

            self.get_info_suffix = '''Please generate summaries for each focus point, don't miss any focus points. If the webpage text is not related to a focus point, output "NA" for that point. The entire output should be wrapped in triple quotes with no other content inside. Here is an example of the output format:
"""
//Focus Point 1//
Summary 1
//Focus Point 2//
Summary 2
//Focus Point 3//
NA
...
"""'''

            self.get_more_link_prompt = f'''You will be given several lines of text in the format "<index>//content//". Your task is to analyze each line and associate it with one of the following focus points. The list of focus points and their explanations are as follows:

{focus_statement}\n
When performing the association analysis, please follow these principles:

- Understand the meaning of each focus point
- If a focus point has further explanation, ensure the extracted content aligns with the scope of these explanations'''

            self.get_more_link_suffix = '''Please output the results line by line. Each line should be in the format "<index>//focus point name//". If a line is not related to any focus point, output "<index>//NA//". The entire output should be wrapped in triple quotes with no other content inside. Here is an example of the output format:
"""
<t1>//Focus Point 1//
<t2>//Focus Point 2// 
<t3>//NA//
...
"""'''

    async def _generate_results(self, lines: list, mode: str) -> set:
        if mode == 'get_info':
            system_prompt = self.get_info_prompt
            suffix = self.get_info_suffix
            batch_size = 5000
        elif mode == 'get_link':
            system_prompt = self.get_more_link_prompt
            suffix = self.get_more_link_suffix
            batch_size = 2048
        else:
            self.logger.error(f"unknown mode: {mode}")
            return set()

        cache = set()
        batches = []
        text_batch = ''
        for line in lines:
            text_batch += f'{line}\n'
            if len(text_batch) > batch_size:
                content = f'<text>\n{text_batch}</text>\n\n{suffix}'
                batches.append({'system_prompt': system_prompt, 'content': content})
                text_batch = ''

        if text_batch:
            content = f'<text>\n{text_batch}</text>\n\n{suffix}'
            batches.append({'system_prompt': system_prompt, 'content': content})

        self.logger.info(f"LLM tasks size: {len(batches)}")
        tasks = [
            llm(
                    [{'role': 'system', 'content': batch['system_prompt']}, {'role': 'user', 'content': batch['content']}],
                    model=self.model, temperature=0.1
                )
            for batch in batches]
        results = await asyncio.gather(*tasks)
        for res in results:
            if res:
                cache.update(extract_info(res))

        return cache

    async def get_more_related_urls(self, link_dict: dict) -> set:
        _to_be_processed = []
        link_map = {}
        for i, (url, des) in enumerate(link_dict.items()):
            des = des.replace('\n', ' ')
            _to_be_processed.append(f'<t{i+1}>//{des}//')
            link_map[f'<t{i+1}'] = url

        raw_result = await self._generate_results(_to_be_processed, 'get_link')
        final_result = set()
        for result in raw_result:
            for item in result.split('\n'):
                if not item:
                    continue
                segs = item.split('>')
                if len(segs) != 2:
                    self.logger.debug(f"bad generate result: {item}")
                    continue
                _index, focus = segs
                _index = _index.strip()
                focus = focus.strip().strip('//')
                if focus == 'NA':
                    continue
                if focus not in self.focus_dict or _index not in link_map:
                    self.logger.debug(f"bad generate result: {item}")
                    continue
                # self.logger.debug(f"{link_map[_index]} selected")
                final_result.add(link_map[_index])
        return final_result

    async def get_info(self, text: str, text_links: dict, info_pre_fix: str) -> list[dict]:
        raw_result = await self._generate_results(text.split('\n'), 'get_info')
        final = []
        for item in raw_result:
            self.logger.debug(f"llm output:\n{item}")
            segs = item.split('//')
            i = 0
            while i < len(segs) - 1:
                focus = segs[i].strip()
                if not focus:
                    i += 1
                    continue
                if focus not in self.focus_dict:
                    self.logger.debug(f"bad generate result: {item}")
                    i += 1
                    continue
                content = segs[i+1].strip().strip('摘要').strip(':').strip('：')
                i += 2
                if not content or content == 'NA':
                    continue
                """
                maybe can use embedding retrieval to judge
                """

                url_tags = re.findall(r'\[(Ref_\d+)]', content)
                refences = {url_tag: text_links[url_tag] for url_tag in url_tags if url_tag in text_links}

                final.append({'tag': self.focus_dict[focus], 'content': f"{info_pre_fix}{content}", 'references': refences})
        
        return final

    async def __call__(self, link_dict: dict, text: str, text_links: dict, author: str, publish_date: str) -> tuple[set, list]:
        info_prefix = f"//{author} {publish_date}//"
        return await self.get_more_related_urls(link_dict), await self.get_info(text, text_links, info_prefix)
