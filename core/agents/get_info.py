from llms.openai_wrapper import openai_llm as llm
# from core.llms.siliconflow_wrapper import sfa_llm
from utils.general_utils import is_chinese, extract_and_convert_dates, extract_urls
from loguru import logger
from utils.pb_api import PbTalker
import os, re
from datetime import datetime
from urllib.parse import urlparse
import json_repair


list_judge_threshold = 0.007
valid_list_min_length = 10
min_content_length = 420

common_file_exts = [
    'jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'svg', 'm3u8',
    'mp4', 'mp3', 'wav', 'avi', 'mov', 'wmv', 'flv', 'webp', 'webm',
    'zip', 'rar', '7z', 'tar', 'gz', 'bz2',
    'txt', 'csv', 'xls', 'xlsx', 'ppt', 'pptx',
    'json', 'xml', 'yaml', 'yml', 'css', 'js', 'php', 'asp', 'jsp'
]
common_tlds = [
    '.com', '.cn', '.net', '.org', '.edu', '.gov', '.io', '.co',
    '.info', '.biz', '.me', '.tv', '.cc', '.xyz', '.app', '.dev',
    '.cloud', '.ai', '.tech', '.online', '.store', '.shop', '.site',
    '.top', '.vip', '.pro', '.ltd', '.group', '.team', '.work'
]

def find_article_or_list(link_dict: dict, text: str) -> (bool, bool, dict, str):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    text = '\n'.join(lines)
    for key, value in link_dict.items():
        link_dict[key] = value.lower()

    text_no_tags = re.sub(r'<\w{1,5}>', '', text)
    text_no_urls = re.sub(r'\[url\d+]', '', text_no_tags)
    content_length = len(text_no_urls)

    valid_url = set()
    for url in link_dict.values():
        has_common_ext = any(url.endswith(ext) for ext in common_file_exts)
        has_common_tld = any(url.endswith(tld) or url.endswith(tld + '/') for tld in common_tlds)
        if not has_common_ext and not has_common_tld:
            valid_url.add(url)

    valid_url_rate = len(valid_url) / content_length
    is_list = valid_url_rate > list_judge_threshold and len(valid_url) > valid_list_min_length
    need_more_info = content_length < min_content_length
    return is_list, need_more_info, link_dict, text


class GeneralInfoExtractor:
    def __init__(self, pb: PbTalker, _logger: logger) -> None:
        self.pb = pb
        self.logger = _logger
        self.model = os.environ.get("PRIMARY_MODEL", "")
        self.secondary_model = os.environ.get("SECONDARY_MODEL", "")

        if not self.model or not self.secondary_model:
            self.logger.error("PRIMARY_MODEL or SECONDARY_MODEL not set, can't continue")
            raise ValueError("PRIMARY_MODEL or SECONDARY_MODEL not set, please set it in environment variables or edit core/.env")

        self.vl_model = os.environ.get("VL_MODEL", "")

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
            self.get_info_prompt = f'''作为信息提取助手，你的任务是从给定的网页文本中抽取任何与下列关注点之一相关的信息。关注点列表及其解释如下：

{focus_statement}\n
在进行信息提取时，请遵循以下原则：

- 理解每个关注点的含义，确保提取的内容至少与其中之一相关
- 如果关注点有进一步的解释，确保提取的内容符合这些解释的范围
- 忠于原文，你的任务是从网页文本中抽取相关信息，而不是提炼、总结和改写
- 对于最终输出的信息，请保证主体、时间、地点等关键要素的清晰明确，为此可能需要综合上下文进行提取
- 如果提取的内容中包括类似“<mp4>”、“[url1]”这样的片段，务必原样保留'''

            self.get_info_suffix = '''请先复述一遍关注点及其解释，再对原文进行分析。如果网页文本中包含关注点相关的内容，请按照以下json格式输出提取的信息：
{"focus": 关注点名称, "content": 提取的内容}

如果有多条相关信息，请按一行一条的格式输出，最终输出的结果整体用三引号包裹，三引号内不要有其他内容，如下是输出格式示例：
"""
{"focus": 关注点1名称, "content": 提取内容1}
{"focus": 关注点2名称, "content": 提取内容2}
...
"""

如果网页文本中不包含任何相关的信息，请保证三引号内为空。'''

            self.get_more_link_prompt = f'''你将被给到一段处理过的网页文本，在这些文本中所有的url链接都已经被替换为类似"[url120]"这样的标签，并置于与其关联的文本后面。
你的任务是从网页文本中抽取任何与下列关注点之一相关的文本片段。关注点列表及其解释如下：

{focus_statement}\n
在进行抽取时，请遵循以下原则：

- 理解每个关注点的含义，确保提取的内容至少与其中之一相关
- 如果关注点有进一步的解释，确保提取的内容符合这些解释的范围
- 只抽取以标签（类似"[url120]"这样）结尾的文本片段
- 维持抽取出的文本片段的原样，尤其不要遗漏其后的标签'''

            self.get_more_link_suffix = '''请先复述一遍关注点及其解释，再对原文逐行进行抽取，最终将挑选出的文本片段按一行一条的格式输出，并整体用三引号包裹，三引号内不要有其他内容，如下是输出格式示例：
"""
文本1
文本2
...
"""'''

            self.info_judge_prompt = '''判断给定的信息是否与网页文本相符。信息将用标签<info></info>包裹，网页文本则用<text></text>包裹。请遵循如下工作流程:
1、尝试找出网页文本中所有与信息相关的片段（有多少找多少，没有的话则跳过）；
2、判断信息是否与这些片段在关键要素上一致，请特别注意主语、日期、地点以及数字这些。'''

            self.info_judge_suffix = '先输出找到的所有文本片段，再输出最终结论（仅为“是”或“否”）'
        else:
            self.get_info_prompt = f'''As an information extraction assistant, your task is to extract any information from the given webpage text that relates to at least one of the following focus points. The list of focus points and their explanations are as follows:

{focus_statement}\n
When extracting information, please follow these principles:

- Understand the meaning of each focus point and ensure the extracted content relates to at least one of them
- If a focus point has further explanations, ensure the extracted content aligns with those explanations
- Stay faithful to the original text - your task is to extract relevant information, not to refine, summarize or rewrite
- For the final output, ensure key elements like subject, time, location etc. are clearly specified, which may require synthesizing context
- If the extracted content includes fragments like "<mp4>" or "[url1]", make sure to preserve them exactly as they appear'''

            self.get_info_suffix = '''First, please restate the focus points and their explanations, then analyze the original text. If the webpage text contains content related to the focus points, please output the extracted information in the following JSON format:
{"focus": focus point name, "content": extracted content}

If there are multiple relevant pieces of information, output them one per line, with the entire output wrapped in triple quotes. There should be no other content within the triple quotes. Here is an example of the output format:
"""
{"focus": focus point 1 name, "content": extracted content 1}
{"focus": focus point 2 name, "content": extracted content 2}
...
"""

If the webpage text does not contain any relevant information, ensure the content within the triple quotes is empty.'''

            self.get_more_link_prompt = f'''You will be given a processed webpage text where all URL links have been replaced with tags like "[url120]" and placed after their associated text.
Your task is to extract any text fragments from the webpage text that relate to any of the following focus points. The list of focus points and their explanations are as follows:

{focus_statement}\n
When extracting, please follow these principles:

- Understand the meaning of each focus point and ensure the extracted content relates to at least one of them
- If a focus point has further explanations, ensure the extracted content aligns with those explanations
- Only extract text fragments that end with tags (like "[url120]")
- Maintain the text fragments exactly as they appear, especially don't omit their trailing tags'''

            self.get_more_link_suffix = '''First, please restate the focus points and their explanations, then analyze the original text line by line. Finally, output the selected text fragments one per line, with the entire output wrapped in triple quotes. There should be no other content within the triple quotes. Here is an example of the output format:
"""
text1
text2
...
"""'''

            self.info_judge_prompt = '''Determine whether the given information matches the webpage text. The information will be wrapped in <info></info> tags, and the webpage text will be wrapped in <text></text> tags. Please follow this workflow:
1. Try to find all text fragments in the webpage text that are related to the information (find as many as possible, skip if none);
2. Determine whether the information is consistent with these fragments in key elements, paying special attention to subjects, dates, locations, and numbers.'''

            self.info_judge_suffix = 'First, output all found text fragments, then output the final conclusion (only "Y" or "N").'

    async def get_author_and_publish_date(self, text: str) -> tuple[str, str]:
        if not text:
            return "", ""

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

        if not isinstance(result, dict):
            self.logger.warning("failed to parse from llm output")
            return '', ''
        if 'source' not in result or 'publish_date' not in result:
            self.logger.warning("failed to parse from llm output")
            return '', ''

        return result['source'], extract_and_convert_dates(result['publish_date'])

    async def _generate_results(self, text: str, mode: str) -> set:
        if mode == 'get_info':
            system_prompt = self.get_info_prompt
            suffix = self.get_info_suffix
            batch_size = 2048
        elif mode == 'get_link':
            system_prompt = self.get_more_link_prompt
            suffix = self.get_more_link_suffix
            batch_size = 1024
        else:
            self.logger.error(f"unknown mode: {mode}")
            return set()

        lines = text.split('\n')
        cache = set()
        text_batch = ''
        for line in lines:
            text_batch = f'{text_batch}\n{line}'
            if len(text_batch) > batch_size:
                content = f'<text>\n{text_batch}\n</text>\n\n{suffix}'
                result = await llm(
                    [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': content}],
                    model=self.model, temperature=0.1)
                self.logger.debug(f"llm output: {result}")
                result = re.findall(r'\"\"\"(.*?)\"\"\"', result, re.DOTALL)
                if not result:
                    self.logger.warning("bad generate result")
                    text_batch = ''
                    continue
                for item in result:
                    item = item.strip()
                    if not item:
                        continue
                    item = item.split('\n')
                    cache.update(item)
                text_batch = ''

        if text_batch:
            content = f'<text>\n{text_batch}\n</text>\n\n{suffix}'
            result = await llm(
                [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': content}],
                model=self.model, temperature=0.1)
            self.logger.debug(f"llm output: {result}")
            result = re.findall(r'\"\"\"(.*?)\"\"\"', result, re.DOTALL)
            if not result:
                self.logger.warning("bad generate result")
                return cache
            for item in result:
                item = item.strip()
                if not item:
                    continue
                item = item.split('\n')
                cache.update(item)
        return cache
    
    async def _extract_info_from_img(self, text, link_dict) -> str:
        cache = {}
        pattern = r'<img>\[url\d+\]'
        matches = re.findall(pattern, text)
        for match in matches:
            key = match.split('[url')[1][:-1]
            url = link_dict.get(f'url{key}', '')
            if not url:
                continue
        
            if url in cache:
                replace_text = cache[url]
            else:
                if any(url.endswith(tld) or url.endswith(tld + '/') for tld in common_tlds):
                    continue
                if any(url.endswith(ext) for ext in common_file_exts if ext not in ['jpg', 'jpeg', 'png']):
                    continue
                llm_output = await llm([{"role": "user",
                                    "content": [{"type": "image_url", "image_url": {"url": url, "detail": "high"}},
                                                {"type": "text", "text": "提取图片中的所有文字，如果图片不包含文字或者文字很少或者你判断图片仅是网站logo、商标、图标等，则输出NA。注意请仅输出提取出的文字，不要输出别的任何内容。"}]}],
                                                model=self.vl_model)
                self.logger.debug(f"vl model output: \n{llm_output}\n")
                replace_text = llm_output
                cache[url] = replace_text
            text = text.replace(match, f'{replace_text}{match}', 1)
        return text

    async def get_more_related_urls(self, link_dict: dict, text: str) -> list[str]:
        raw_result = await self._generate_results(text, 'get_link')
        final_result = set()
        for item in raw_result:
            if '[url' not in item:
                self.logger.warning(f"bad generate result: {item}")
                continue
            url_tags = re.findall(r'\[url\d+]', item)
            if not url_tags:
                self.logger.warning(f"bad generate result: {item}")
                continue
            for url_tag in url_tags:
                url_tag = url_tag[1:-1]
                if url_tag not in link_dict:
                    self.logger.warning(f"bad generate result: {item}")
                    continue
                result_url = link_dict[url_tag]
                if any(result_url.endswith(tld) or result_url.endswith(tld + '/') for tld in common_tlds):
                    continue
                if any(result_url.endswith(ext) for ext in common_file_exts if ext not in ['jpg', 'jpeg', 'png']):
                    continue
                final_result.add(result_url)
        return list(final_result)

    async def get_info(self, link_dict: dict, text: str, info_pre_fix: str) -> list[dict]:
        raw_result = await self._generate_results(text, 'get_info')
        final = []
        for item in raw_result:
            result = json_repair.repair_json(item, return_objects=True)
            if not isinstance(result, dict):
                self.logger.warning(f"bad generate result: {item}")
                continue
            if not result:
                continue
            if 'focus' not in result or 'content' not in result:
                self.logger.warning(f"bad generate result: {item}")
                continue
            if not item['focus'] or item['focus'] not in self.focus_dict:
                self.logger.warning(f"bad generate result: {item}")
                continue
            if not item['content']:
                self.logger.warning(f"bad generate result: {item}")
                continue
            if item['content'] in link_dict:
                continue

            judge = await llm([{'role': 'system', 'content': self.info_judge_prompt},
                               {'role': 'user', 'content': f'<info>\n{item["content"]}\n</info>\n\n<text>\n{text}\n</text>\n\n{self.info_judge_suffix}'}],
                               model=self.secondary_model, temperature=0.1)
            self.logger.debug(f'judge llm output:\n{judge}')
            if not judge:
                self.logger.warning("failed to parse from llm output, skip checking")
                self.logger.info(f"<info>\n{item['content']}\n</info>\n\n<text>\n{text}\n</text>")
                self.logger.info(judge)
                content = item['content']
                url_tags = re.findall(r'\[url\d+]', content)
                for url_tag in url_tags:
                    url_tag = url_tag[1:-1]
                    _url = link_dict.get(url_tag, '')
                    if _url:
                        content = content.replace(url_tag, _url)
                final.append({'tag': self.focus_dict[item['focus']], 'content': f"{info_pre_fix}{content}"})
                continue

            to_save = False
            for i in range(min(7, len(judge))):
                char = judge[-1 - i]
                if char == '是' or char == 'Y':
                    to_save = True
                    break
                elif char == '否' or char == 'N':
                    break
            if not to_save:
                self.logger.warning("secondary model judge not faithful to article text, aborting")
                self.logger.info(f"<info>\n{item['content']}\n</info>\n\n<text>\n{text}\n</text>")
                self.logger.info(judge)
                continue

            content = item['content']
            url_tags = re.findall(r'\[url\d+]', content)
            for url_tag in url_tags:
                url_tag = url_tag[1:-1]
                _url = link_dict.get(url_tag, '')
                if _url:
                    content = content.replace(url_tag, _url)
            final.append({'tag': self.focus_dict[item['focus']], 'content': f"{info_pre_fix}{content}"})
        
        return final

    async def __call__(self, link_dict: dict, text: str, base_url: str, author: str = None, publish_date: str = None) -> tuple[bool, list]:
        is_list, need_more_info, link_dict, text = find_article_or_list(link_dict, text)
        if is_list:
            self.logger.info("may be a article list page, get more urls ...")
            return True, await self.get_more_related_urls(link_dict, text)
            
        if need_more_info:
            self.logger.info("may be a article page need to get more text from images...")
            text = await self._extract_info_from_img(text, link_dict)
            self.logger.debug(f"extended text: \n{text}\n")

        if not author and not publish_date and text:
            author, publish_date = await self.get_author_and_publish_date(text)

        if not author or author.lower() == 'na':
            author = urlparse(base_url).netloc

        if not publish_date or publish_date.lower() == 'na':
            publish_date = datetime.now().strftime('%Y-%m-%d')

        info_prefix = f"//{author} {publish_date}//"

        return False, await self.get_info(link_dict, text, info_prefix)
