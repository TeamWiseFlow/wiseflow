# from llms.openai_wrapper import openai_llm
from llms.dashscope_wrapper import dashscope_llm
# from llms.siliconflow_wrapper import sfa_llm


rewrite_prompt = '''请综合给到的内容，提炼总结为一个新闻摘要。
给到的内容会用XML标签分隔。
请仅输出总结出的摘要，不要输出其他的信息。'''

model = "qwen2-7b-instruct"


def info_rewrite(contents: list[str], logger=None) -> str:
    context = f"<content>{'</content><content>'.join(contents)}</content>"
    try:
        result = dashscope_llm([{'role': 'system', 'content': rewrite_prompt}, {'role': 'user', 'content': context}],
                               model=model, temperature=0.1, logger=logger)
        return result.strip()
    except Exception as e:
        if logger:
            logger.warning(f'rewrite process llm generate failed: {e}')
        else:
            print(f'rewrite process llm generate failed: {e}')
        return ''
