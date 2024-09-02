from llms.openai_wrapper import openai_llm
# from llms.siliconflow_wrapper import sfa_llm
import re
from utils.general_utils import get_logger_level, is_chinese
from loguru import logger
from utils.pb_api import PbTalker
import os


get_info_model = os.environ.get("GET_INFO_MODEL", "gpt-3.5-turbo")
rewrite_model = os.environ.get("REWRITE_MODEL", "gpt-3.5-turbo")

project_dir = os.environ.get("PROJECT_DIR", "")
if project_dir:
    os.makedirs(project_dir, exist_ok=True)
logger_file = os.path.join(project_dir, 'wiseflow.log')
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
if not focus_data:
    logger.error('no activated tag found, please set at least one')
    exit(1)

focus_list = [item["name"] for item in focus_data if item["name"]]
focus_dict = {item["name"]: item["id"] for item in focus_data if item["name"]}
lang_term = ''.join([f'{item["name"]}{item["explaination"]}' for item in focus_data if item["name"]])
focus_statement = '\n'.join([f'<tag>{item["name"]}</tag>{item["explaination"]}' for item in focus_data if item["name"] and item["explaination"]])

if is_chinese(lang_term):
    if focus_statement:
        system_prompt = f'''请仔细阅读用户输入的新闻内容，并根据所提供的类型标签列表进行分析。类型标签列表如下：
{focus_list}

各标签的含义如下：
{focus_statement}

如果新闻中包含上述任何类型的信息，请使用以下格式标记信息的类型标签，并提供仅包含时间、地点、人物和事件的一句话信息摘要：
<tag>类型名称</tag>仅包含时间、地点、人物和事件的一句话信息摘要

务必注意：1、严格忠于新闻原文，不得提供原文中不包含的信息；2、对于同一事件，仅选择一个最贴合的标签，不要重复输出；3、如果新闻中包含多个信息，请逐一分析并按一条一行的格式输出，如果新闻不涉及任何类型的信息，则直接输出：无。'''
    else:
        system_prompt = f'''请仔细阅读用户输入的新闻内容，并根据所提供的类型标签列表进行分析。类型标签列表如下：
{focus_list}

如果新闻中包含上述任何类型的信息，请使用以下格式标记信息的类型标签，并提供仅包含时间、地点、人物和事件的一句话信息摘要：
<tag>类型名称</tag>仅包含时间、地点、人物和事件的一句话信息摘要

务必注意：1、严格忠于新闻原文，不得提供原文中不包含的信息；2、对于同一事件，仅选择一个最贴合的标签，不要重复输出；3、如果新闻中包含多个信息，请逐一分析并按一条一行的格式输出，如果新闻不涉及任何类型的信息，则直接输出：无。'''

    rewrite_prompt = '''请综合给到的内容，提炼总结为一个新闻摘要。给到的内容会用XML标签分隔。请仅输出总结出的摘要，不要输出其他的信息。'''

else:
    if focus_statement:
        system_prompt = f'''Please carefully read the news content provided by the user and analyze it according to the list of type labels given below:
{focus_list}

The meanings of each label are as follows:
{focus_statement}

If the news contains any information of the aforementioned types, please mark the type label of the information using the following format and provide a one-sentence summary containing only the time, location, people involved, and event:
<tag>TypeLabel</tag>A one-sentence summary containing only the time, location, people involved, and event

Please be sure to: 1. Strictly adhere to the original text and do not provide information not contained in the original; 2. For the same event, choose only one most appropriate label and do not repeat the output; 3. If the news contains multiple pieces of information, analyze them one by one and output them in a one-line-per-item format. If the news does not involve any of the types of information, simply output: None.'''
    else:
        system_prompt = f'''Please carefully read the news content provided by the user and analyze it according to the list of type labels given below:
{focus_list}

If the news contains any information of the aforementioned types, please mark the type label of the information using the following format and provide a one-sentence summary containing only the time, location, people involved, and event:
<tag>TypeLabel</tag>A one-sentence summary containing only the time, location, people involved, and event

Please be sure to: 1. Strictly adhere to the original text and do not provide information not contained in the original; 2. For the same event, choose only one most appropriate label and do not repeat the output; 3. If the news contains multiple pieces of information, analyze them one by one and output them in a one-line-per-item format. If the news does not involve any of the types of information, simply output: None.'''

    rewrite_prompt = "Please synthesize the content provided, which will be segmented by XML tags, into a news summary. Output only the summarized abstract without including any additional information."


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
