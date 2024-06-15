from llms.openai_wrapper import openai_llm
# from llms.siliconflow_wrapper import sfa_llm
import re
from utils.general_utils import get_logger_level
from loguru import logger
from utils.pb_api import PbTalker
import os
import locale


get_info_model = os.environ.get("GET_INFO_MODEL", "gpt-3.5-turbo")
rewrite_model = os.environ.get("REWRITE_MODEL", "gpt-3.5-turbo")

project_dir = os.environ.get("PROJECT_DIR", "")
if project_dir:
    os.makedirs(project_dir, exist_ok=True)
logger_file = os.path.join(project_dir, 'insights.log')
dsw_log = get_logger_level()
logger.add(
    logger_file,
    level=dsw_log,
    backtrace=True,
    diagnose=True,
    rotation="50 MB"
)

pb = PbTalker(logger)

focus_data = pb.read(collection_name='tags', filter=f'activated=True')
focus_list = [item["name"] for item in focus_data if item["name"]]
focus_dict = {item["name"]: item["id"] for item in focus_data if item["name"]}

sys_language, _ = locale.getdefaultlocale()

if sys_language == 'zh_CN':

    system_prompt = f'''请仔细阅读用户输入的新闻内容，并根据所提供的类型列表进行分析。类型列表如下：
{focus_list}

如果新闻中包含上述任何类型的信息，请使用以下格式标记信息的类型，并提供仅包含时间、地点、人物和事件的一句话信息摘要：
<tag>类型名称</tag>仅包含时间、地点、人物和事件的一句话信息摘要

如果新闻中包含多个信息，请逐一分析并按一条一行的格式输出，如果新闻不涉及任何类型的信息，则直接输出：无。
务必注意：1、严格忠于新闻原文，不得提供原文中不包含的信息；2、对于同一事件，仅选择一个最贴合的tag，不要重复输出；3、仅用一句话做信息摘要，且仅包含时间、地点、人物和事件；4、严格遵循给定的格式输出。'''

    rewrite_prompt = '''请综合给到的内容，提炼总结为一个新闻摘要。给到的内容会用XML标签分隔。请仅输出总结出的摘要，不要输出其他的信息。'''

else:

    system_prompt = f'''Please carefully read the user-inputted news content and analyze it based on the provided list of categories:
{focus_list}

If the news contains any information related to the above categories, mark the type of information using the following format and provide a one-sentence summary containing only the time, location, who involved, and the event:
<tag>Category Name</tag> One-sentence summary including only time, location, who, and event.

If the news includes multiple pieces of information, analyze each one separately and output them in a line-by-line format. If the news does not involve any of the listed categories, simply output: N/A.
Important guidelines to follow: 1) Adhere strictly to the original news content, do not provide information not contained in the original text; 2) For the same event, select only the most fitting tag, avoiding duplicate outputs; 3) Summarize using just one sentence, and limit it to time, location, who, and event only; 4) Strictly comply with the given output format.'''

    rewrite_prompt = "Please synthesize the content provided, which will be segmented by XML tags, into a news summary. Output only the summarized abstract without including any additional information."


def get_info(article_content: str) -> list[dict]:
    # logger.debug(f'receive new article_content:\n{article_content}')
    result = openai_llm([{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': article_content}],
                        model=get_info_model, logger=logger)

    # results = pattern.findall(result)
    texts = result.split('<tag>')
    texts = [_.strip() for _ in texts if '</tag>' in _.strip()]
    if not texts:
        logger.info(f'can not find info, llm result:\n{result}')
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
            info = ''.join(strings[1:])
            info = info.strip()
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


def info_rewrite(contents: list[str]) -> str:
    context = f"<content>{'</content><content>'.join(contents)}</content>"
    try:
        result = openai_llm([{'role': 'system', 'content': rewrite_prompt}, {'role': 'user', 'content': context}],
                            model=rewrite_model, temperature=0.1, logger=logger)
        return result.strip()
    except Exception as e:
        if logger:
            logger.warning(f'rewrite process llm generate failed: {e}')
        else:
            print(f'rewrite process llm generate failed: {e}')
        return ''
