# from llms.dashscope_wrapper import dashscope_llm
from llms.openai_wrapper import openai_llm
# from llms.siliconflow_wrapper import sfa_llm
import re
from utils.general_utils import get_logger_level
from loguru import logger
from utils.pb_api import PbTalker
import os


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

model = "glm-4-flash"
focus_data = pb.read(collection_name='tags', filter=f'activated=True')
focus_list = [item["name"] for item in focus_data if item["name"]]
focus_dict = {item["name"]: item["id"] for item in focus_data if item["name"]}

system_prompt = f'''请仔细阅读用户输入的新闻内容，并根据所提供的类型列表进行分析。类型列表如下：
{focus_list}

如果新闻中包含上述任何类型的信息，请使用以下格式标记信息的类型，并提供仅包含时间、地点、人物和事件的一句话信息摘要：
<tag>类型名称</tag>仅包含时间、地点、人物和事件的一句话信息摘要

如果新闻中包含多个信息，请逐一分析并按一条一行的格式输出，如果新闻不涉及任何类型的信息，则直接输出：无。
务必注意：1、严格忠于新闻原文，不得提供原文中不包含的信息；2、对于同一事件，仅选择一个最贴合的tag，不要重复输出；3、仅用一句话做信息摘要，且仅包含时间、地点、人物和事件；4、严格遵循给定的格式输出。'''

# pattern = re.compile(r'\"\"\"(.*?)\"\"\"', re.DOTALL)


def get_info(article_content: str) -> list[dict]:
    # logger.debug(f'receive new article_content:\n{article_content}')
    result = openai_llm([{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': article_content}],
                        model=model, logger=logger)

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
        sources = re.findall(r'内容：\((.*?) 文章\)', article_content)
        if sources and sources[0]:
            info = f"【{sources[0]} 公众号】 {info}"

        cache.append({'content': info, 'tag': focus_dict[tag]})

    return cache
