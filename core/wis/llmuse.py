from openai import AsyncOpenAI as OpenAI
from openai import RateLimitError, APIError
from typing import List
import os
import asyncio
from core.async_logger import wis_logger

base_url = os.environ.get('LLM_API_BASE', "")
token = os.environ.get('LLM_API_KEY', "")
performance_model = os.environ.get("PERFORMANCE_MODEL", "")
selected_model = os.environ.get("SELECTED_MODEL", "")
vl_model = os.environ.get("VL_MODEL", "")
qa_model = os.environ.get("QA_MODEL", performance_model)

if not base_url and not token:
    raise ValueError("LLM_API_BASE or LLM_API_KEY must be set")
elif base_url and not token:
    client = OpenAI(base_url=base_url, api_key="not_use")
elif not base_url and token:
    client = OpenAI(api_key=token)
else:
    client = OpenAI(api_key=token, base_url=base_url)

concurrent_number = int(os.environ.get('LLM_CONCURRENT_NUMBER', 1))

# 全局信号量对象，避免重复创建
_semaphore = None
_semaphore_lock = asyncio.Lock()

async def get_semaphore():
    """获取全局信号量对象，确保单例模式"""
    global _semaphore
    if _semaphore is None:
        async with _semaphore_lock:
            if _semaphore is None:
                _semaphore = asyncio.Semaphore(concurrent_number)
    return _semaphore

async def cleanup_semaphore():
    """清理信号量资源"""
    global _semaphore
    _semaphore = None

async def llm_async(messages: List, model: str, **kwargs):
    max_retries = 3
    wait_time = 20

    semaphore = await get_semaphore()
    async with semaphore:  # 使用信号量控制并发
        for retry in range(max_retries):
            try:
                response = await client.chat.completions.create(
                    messages=messages,
                    model=model,
                    **kwargs
                )
                return response
            except RateLimitError as e:
                # rate limit error, retry
                if retry == max_retries - 1:
                    error_msg = f"{model} Rate limit error: {str(e)}. Already Retried {max_retries} times."
                    wis_logger.warning(error_msg)
            except APIError as e:
                if hasattr(e, 'status_code'):
                    if e.status_code in [400, 401, 413]:
                        # client error, no need to retry
                        error_msg = f"{model} API error: {e.status_code}. Detail: {str(e)}"
                        if model in ["Pro/Qwen/Qwen2.5-VL-7B-Instruct", "Pro/THUDM/GLM-4.1V-9B-Thinking"]:
                            # 特定模型报错没有跟踪意义，比如硅基的这个视觉模型，大部分是 图片url 无法访问 或者 尺寸不对，我也无法让原始网站做更改……
                            return '§图片无法访问§'
                        wis_logger.warning(error_msg)
                        wis_logger.info(f"messages: {messages}")
                        return None
                    else:
                        # other API error, retry
                        error_msg = f"{model} API error: {e.status_code}. Retry {retry+1}/{max_retries}."
                        wis_logger.warning(error_msg)
                else:
                    # unknown API error, retry
                    error_msg = f"{model} Unknown API error: {str(e)}. Retry {retry+1}/{max_retries}."
                    wis_logger.warning(error_msg)
            except Exception as e:
                # other exception, retry
                error_msg = f"{model} Unexpected error: {str(e)}. Retry {retry+1}/{max_retries}."
                wis_logger.warning(error_msg)

            if retry < max_retries - 1:
                # exponential backoff strategy
                await asyncio.sleep(wait_time)
                # next wait time is doubled
                wait_time *= 2


PROMPT_EXTRACT_BLOCKS = """Based on the following keywords and filtering criteria, extract information from the <main-content> area of the given <markdown>, and discover links worth further exploration from the entire <markdown>:

{FOCUS_POINT}

Below is the markdown content:
<markdown>
{HTML}
</markdown>

The above markdown content is derived from the webpage's HTML and may have been chunked.
All links (a elements or img elements) in the original HTML have been converted to reference tags (like "[x]").

For information extraction, be sure to follow these precautions:
- If you determine this is an article list page, skip information extraction immediately and proceed to link discovery.
- Only extract information from the <main-content> area of the markdown. If there is no <main-content> area, skip information extraction immediately and proceed to link discovery.
- Pay special attention to constraints in the filtering criteria (if any), such as time limits, numerical limits, topic limits, etc. Ensure the extracted information meets the requirements, but do not include any explanations or reasons in the final output.
- If there is no information related to the keywords and meeting the filtering criteria in the <main-content> area, skip information extraction immediately and proceed to link discovery.
- If multiple pieces of information are extracted, merge them into a single coherent message containing all key points. Do not start with phrases like "the markdown mentions" or "the given text says"; I hate that, just provide the summarized information directly.

For link discovery, be sure to follow these precautions:
- You can find links worth further exploration from the entire markdown (represented as reference tags like [x]).
- Use the context to judge whether the content corresponding to the link is likely to contain the information we need.
- For the found link reference tags, output them along with the sentences where they are located, one per line.

If relevant information or links can be extracted, wrap them in <info></info> and <links></links> tags respectively, as shown below:

<info>
Extracted information (if there are multiple pieces of information, merge them into one; if none, keep it empty. Never provide any explanations, reasons, or descriptions here; I'm not interested in those)
</info>

<links>
Sentence 1 containing reference tag
Sentence 2 containing reference tag
...
</links>
"""

PROMPT_EXTRACT_BLOCKS_ONLY_INFO = """Based on the following keywords and filtering criteria, extract information from the <main-content> area of the given <markdown>:

{FOCUS_POINT}

Below is the markdown content:
<markdown>
{HTML}
</markdown>

The above markdown content is derived from the webpage's HTML and may have been chunked.
All reference links (a elements or img elements) in the original HTML have been converted into reference tags (like "[x]").

Be sure to follow these precautions:
- Only extract information from the <main-content> area of the markdown. If there is no <main-content> area, end the task directly without providing any explanations, reasons, or descriptions.
- If you determine this is an article list page, end the task directly without providing any explanations, reasons, or descriptions.
- Pay special attention to constraints in the filtering criteria (if any), such as time limits, numerical limits, topic limits, etc. Ensure the extracted information meets the requirements, but do not include any explanations or reasons in the final output.
- If there is no information related to the keywords and meeting the filtering criteria in the <main-content> area, end the task directly without providing any explanations, reasons, or descriptions.
- If multiple pieces of information are extracted, merge them into a single coherent message containing all key points. Do not start with phrases like "the markdown mentions" or "the given text says"; I hate that, just provide the summarized information directly.

If relevant information can be extracted, wrap it in <info></info> tags as shown below:

<info>
Extracted information (if there are multiple pieces of information, merge them into one; if none, keep it empty. Never provide any explanations, reasons, or descriptions here; I'm not interested in those)
</info>
"""

PROMPT_EXTRACT_BLOCKS_ONLY_LINKS = """Based on the following keywords and filtering criteria, discover links worth further exploration from the given <markdown> (represented as reference tags like [x]):

{FOCUS_POINT}

Below is the markdown content:
<markdown>
{HTML}
</markdown>

The above markdown content is derived from the webpage's HTML and may have been chunked.
All links (a elements or img elements) in the original HTML have been converted into reference tags (like "[x]").

Be sure to follow these precautions:
- Use the context to judge whether the content corresponding to the link is likely to contain the information we need.
- For the found link reference tags, output them along with the sentences where they are located, one per line.

If relevant links can be extracted, wrap them in <links></links> tags as shown below:

<links>
Sentence 1 containing reference tag
Sentence 2 containing reference tag
...
</links>
"""

PROMPT_EXTRACT_SCHEMA_WITH_INSTRUCTION = """The following is content from a webpage:
<url>{URL}</url>
<url_content>
{HTML}
</url_content>

Now extract information from <url_content> based on the following schema and return a list of JSON objects:
<schema>
{SCHEMA}
</schema>

Extraction Instructions:
Return the extracted information as a list of JSON objects, where each object corresponds to a valid piece of information extracted from the webpage, and ensure their order is consistent with the order in which they appear on the webpage. Wrap the entire JSON list in <json>...</json> XML tags.

Quality Check:
Before outputting the final answer, carefully check if the returned JSON is complete, contains all the information requested by the user, and is valid JSON that can be parsed by json.loads() without errors or omissions. The output JSON objects should strictly match the schema.

Avoid Common Errors:
- Do not use "//" or "#" to add any comments in the JSON output. This will cause parsing errors.
- Ensure the JSON format is correct, with curly braces, square brackets, and commas all in the right places.
- Do not omit the closing </json> tag at the end of the JSON output.
- Do not generate Python code to show how to complete the task; it is your task to extract the information and return it in JSON format.

Result:
Output the final list of JSON objects, wrapped in <json>...</json> XML tags. Ensure the tags are correctly closed.
"""

VL_PROMPT_EXTRACT_TEXT_FROM_IMG = """Extract all text from the image. If the image contains no text, very little text, or is judged to be just a website logo, trademark, icon, etc., output a short description of the image wrapped in ().
Note: either output the extracted text directly or output a short description of the image (wrapped in ()). Do not provide any explanations, reasons, or descriptions; I'm not interested in those."""
