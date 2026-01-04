import hashlib, json, time
import regex as re
from .config import config
from core.async_logger import wis_logger
from core.tools.general_utils import _env_to_bool
from .basemodels import CrawlResult
from .llmuse import *
from .chunking_strategy import ChunkingStrategy, MaxLengthChunking
from .extraction_strategy import ExtractionStrategy
from .markdown_generation_strategy import DefaultMarkdownGenerator, WeixinArticleMarkdownGenerator
from .utils import split_and_parse_json_objects
import asyncio
from datetime import datetime
from typing import Optional, TYPE_CHECKING, Tuple, Any, List, Dict
if TYPE_CHECKING:
    from core.async_database import AsyncDatabaseManager
    from .async_cache import SqliteCache


APLPLY_FAILED_TIMES_THRESHOLD = 12
VERBOSE = _env_to_bool(os.environ.get('WISEFLOW_VERBOSE', 'False'), False)

_chunker = MaxLengthChunking(max_length=config['MAX_CHUNK_SIZE'])
default_markdown_generator = DefaultMarkdownGenerator()
weixin_markdown_generator = WeixinArticleMarkdownGenerator()

def extract_xml_data(tags, string):
    """
    Extract data for specified XML tags from a string, returning the longest content for each tag.

    How it works:
    1. Finds all occurrences of each tag in the string using regex.
    3. Returns a dictionary of tag-content pairs.

    Args:
        tags (List[str]): The list of XML tags to extract.
        string (str): The input string containing XML data.

    Returns:
        Dict[str, str]: A dictionary with tag names as keys and longest extracted content as values.
    """

    if '</think>' in string:
        string = string.split('</think>')[1]

    data = {}

    for tag in tags:
        pattern = f"<{tag}>(.*?)</{tag}>"
        matches = re.findall(pattern, string, re.DOTALL)
        
        if matches:
            # Find the longest content for this tag
            # longest_content = max(matches, key=len).strip()
            # 改为返回所有匹配
            data[tag] = matches
        else:
            data[tag] = []

    return data

def hash_calculate(text: str) -> str:
    if not text:
        return ''
    if not isinstance(text, str):
        text = str(text)
    # 1. 移除所有空白字符（包括空格、换行、制表符等）
    no_whitespace = ''.join(text.split())
    if len(no_whitespace) <= 16:
        # 可能对搜集验证页特征有帮助
        wis_logger.debug(f"text is too short: {text}")
        # 太短的也没意义，大概率是网页末端
        return ''
     # 2. 全部转为小写
    lower_text = no_whitespace.lower()
    # 3. 计算MD5
    md5_hash = hashlib.md5(lower_text.encode('utf-8')).hexdigest()

    return md5_hash

async def info_process(info_blocks:list[str],
    type: str,
    url: str = '',
    title: str = '',
    author: str = '',
    publish_date: str = '',
    link_dict: dict = {},
    markdown: str = '') -> List[dict]:

    infos = []
    if type == 'schema':
        info_prefix = ''
    else:
        if publish_date and isinstance(publish_date, str):
            publish_date = publish_date.split('T')[0]
        info_prefix = f'//{author} {publish_date}//' if (author or publish_date) else ''

    for block in info_blocks:
        block = block.strip()
        if len(block) < 3:
            continue

        # bad case sellections
        block = block.removeprefix('根据提供的信息，').strip()
        if block.startswith(('无相关信息', '没有找到', '未找到', '无法提取', '没有发现')):
            continue

        url_tags = re.findall(r'\[(?:img)?\d+]', block)
        refences = ''
        for _tag in url_tags:
            if _tag in link_dict:
                refences += f'{_tag}: {link_dict[_tag]}\n'
            else:
                if _tag not in markdown:
                    block = block.replace(_tag, '') 
                    # case:original text contents, eg [2025]文
                    wis_logger.info(f"[bad case - llm humullate]: info extraction, generated tag: {_tag} which not in raw markdown")
            if type == 'schema':
                block = block.replace(_tag, '')

        infos.append({'type': type, 
                      'content': f'{info_prefix}{block}', 
                      'refers': refences, 
                      'source_url': url, 
                      'source_title': title,
                      'created': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    return infos

class ExtractManager:
    def __init__(self, focus: dict, db_manager: "AsyncDatabaseManager", cache_manager: "SqliteCache"):
        self.focus = focus
        self.db_manager = db_manager
        self.cache_manager = cache_manager
        self.apply_count = 0
        self.apply_failed = 0

        self.focus_id = focus["id"]
        custom_schema = focus["custom_schema"].strip() if focus["custom_schema"] else ''
        self.schema = {}
        schema_str = ''
        if custom_schema:
        # 解析 custom_schema 字符串为 schema dict
        # 支持格式如 "姓名 | 联系方式 | 备注" 或 "姓名 | 联系方式（仅限手机号） | 备注" (支持全角 ｜ 和半角 |)
            fields = [f.strip() for f in re.split(r'[|｜]', custom_schema) if f.strip()]
            for field in fields:
                # 匹配字段名和括号内容（支持中文和英文括号）
                match = re.match(r"^(.*?)\s*(?:（(.*?)）|\((.*?)\))?$", field)
                if match:
                    key = match.group(1).strip()
                    key = re.sub(r"^[（()]*(.*?)[）)]*$", r"\1", key)
                    key = key.strip()
                    # 1. 如果 key 只有一个字符，且是英文或数字，或者全部由标点符号构成，则舍弃
                    if not key or (len(key) == 1 and re.fullmatch(r"[A-Za-z0-9]", key)) or not re.search(r'[a-zA-Z\u4e00-\u9fff]', key):
                        continue
                    # 2. 去掉 value 前后可能残存的中英文括号
                    value = match.group(2) or match.group(3) or ""
                    value = re.sub(r"^[（()]*(.*?)[）)]*$", r"\1", value)
                    value = value.strip()
                    self.schema[key] = f"({value})" if value else ""

            if not self.schema:
                # 这时无法执行，且该任务后续也没有办法执行了
                raise ValueError("focus_schema")
            schema_str = json.dumps(self.schema, indent=2, ensure_ascii=False)
            schema_str = '\n'.join('    ' + line for line in schema_str.split('\n'))
            
        # build focus information string
        focuspoint = focus["focuspoint"]
        restrictions = focus["restrictions"] if focus["restrictions"] else ''
        role = focus["role"] if focus["role"] else ''
        purpose = focus["purpose"] if focus["purpose"] else ''
        self.focus_statement = f"{restrictions}({focuspoint})"
        role_purpose = "/".join([x for x in [role, purpose] if x])
        if role_purpose:
            self.focus_statement += f" - {role_purpose}"
        
        # prepare prompt
        role_and_purpose = ''
        if role:
            role_and_purpose = f"角色: {role}\n"
        if purpose:
            role_and_purpose += f"目的: {purpose}\n"
        if role_and_purpose:
            role_and_purpose += f"任务:\n"

        focus_str = ""
        if focuspoint:
            focus_str += f"<keywords>{focuspoint}</keywords>"
        if restrictions:
            focus_str += f"\n<selection_conditions>{restrictions}</selection_conditions>"
        if focus["explanation"]:
            focus_str += f"\n<explanation>{focus['explanation']}</explanation>"
        
        focus_str = focus_str.strip()
        self.prompt_only_links = role_and_purpose + PROMPT_EXTRACT_BLOCKS_ONLY_LINKS.replace('{FOCUS_POINT}', focus_str)
        self.prompt_only_info = role_and_purpose + PROMPT_EXTRACT_BLOCKS_ONLY_INFO.replace('{FOCUS_POINT}', focus_str)   
        if schema_str:
            self.prompt = role_and_purpose + PROMPT_EXTRACT_SCHEMA_WITH_INSTRUCTION.replace('{SCHEMA}', schema_str)
        else:
            self.prompt = role_and_purpose + PROMPT_EXTRACT_BLOCKS.replace('{FOCUS_POINT}', focus_str)

    async def __call__(self, article: Optional[CrawlResult] = None, mode: Optional[str] = 'both', **kwargs) -> Tuple[int, set]:
        # 统一异步函数，多种用途，除了解析外，未来还可以灵活搭配其他方案，用作 article 对象的更新
        markdown = kwargs.get('markdown', article.markdown if article else None)
        link_dict = kwargs.get('link_dict', article.link_dict if article else {})
        url = kwargs.get('url', article.url if article else "")
        title = kwargs.get('title', article.title if article else "")
        author = kwargs.get('author', article.author if article else "")
        publish_date = kwargs.get('publish_date', article.publish_date if article else "")
        html = kwargs.get('html', article.html if article else None)
        cleaned_html = kwargs.get('cleaned_html', article.cleaned_html if article else None)
        metadata = kwargs.get('metadata', article.metadata if article else {})

        if mode == 'only_link' and config['EXCLUDE_EXTERNAL_LINKS'] and "mp.weixin.qq.com" in url:
            return 0, set()
    
        if not markdown:
            if not html and not cleaned_html:
                wis_logger.info(f"[HTML TO MARKDOWN] ✗ {url} no markdown, cleaned_html or html, skip")
                await self.cache_manager.delete(url)
                return 0, set()
            
            if "mp.weixin.qq.com" in url:
                result = await weixin_markdown_generator.generate_markdown(
                    html,      # raw_html
                    cleaned_html,
                    url,       # base_url
                    metadata
                )
            else:
                result = await default_markdown_generator.generate_markdown(
                    html,      # raw_html
                    cleaned_html,
                    url,       # base_url
                    metadata
                )
            
            error_msg, ps_title, ps_author, publish, markdown, link_dict = result
            if error_msg:
                wis_logger.warning(f"[HTML TO MARKDOWN] ✗ {url}\n{error_msg}")
                return 0, set()
            
            if not markdown:
                # 大概率抓取那个环节其实失败了
                wis_logger.warning(f"[HTML TO MARKDOWN] ✗ {url} cannot get content, possibly failed on crawling")
                await self.cache_manager.delete(url)
                return 0, set()
            
            if not title or "mp.weixin.qq.com" in url:
                title = ps_title
            if not author or "mp.weixin.qq.com" in url:
                author = ps_author
            if not publish_date or "mp.weixin.qq.com" in url:
                publish_date = publish
        
            if article and url:
                article.title = title
                article.author = author
                article.publish_date = publish_date
                article.link_dict = link_dict
                article.markdown = markdown
                article.metadata = metadata
                article.html = html
                article.cleaned_html = cleaned_html
                article.url = url
                await self.cache_manager.set(url, article.model_dump(), 60*5)

        if mode == 'only_link' and not link_dict:
            return 0, set()

        mode = mode if link_dict else 'only_info'
        if config['EXCLUDE_EXTERNAL_LINKS'] and "mp.weixin.qq.com" in url:
            # for weixin article, artilces from different creators share same domain but should be excluded here (even fetching will cause risk control)
            mode = 'only_info'
        
        sections = _chunker.chunk(markdown)
        infos = []
        link_blocks = []
        # custom_schema_blocks = []
        date_stamp: str = datetime.now().strftime("%Y-%m-%d")
        date_time_notify = f"\n另外说一句，今天是 {date_stamp}。"
        sec_pre = ''
        if title:
            sec_pre += f'{title}\n'
        if author:
            sec_pre += f'作者（发布机构）: {author}\n'
        if publish_date:
            sec_pre += f'发布日期: {publish_date}\n'
        if sec_pre:
            sec_pre += '\n'
        
        if not link_dict:
            if mode == 'only_link':
                return 0, set()
            mode = 'only_info'

        for section in sections:
            content_hash = await asyncio.get_event_loop().run_in_executor(
                None,  # 使用默认线程池
                hash_calculate,
                section
            )
            if not content_hash:
                continue

            # 从缓存中检查该内容是否已经被当前focus_id处理过
            cache_namespace = f"focus_{self.focus_id}"
            cache_key = f"{content_hash}"
            
            # 检查缓存中是否已存在处理记录
            cached_result = await self.cache_manager.get(cache_key, namespace=cache_namespace)
            if cached_result:
                wis_logger.info(f"Content already processed: hash={content_hash[:8]}..., focus_id={self.focus_id}")
                continue
            # 先存一次，避免相同内容短时间并发导致重复提交
            await self.cache_manager.set(cache_key, True, 0, namespace=cache_namespace)
            sec_infos = []
            sec_link_blocks = []
            # 5. perform completion
            if mode == 'only_link' or (self.schema and mode != 'only_info'):
                model = performance_model # for this stage
                messages=[{"role": "user", "content": self.prompt_only_links.replace('{HTML}', sec_pre + markdown) + date_time_notify}]
                if VERBOSE:
                    print(f"\n\033[32mprompt:\033[0m\n\033[34m{messages[0]['content']}\033[0m")

                llm_response = await llm_async(
                    messages=messages,
                    model=model,
                    temperature=0.1
                )
                if VERBOSE:
                    reply_text = llm_response.choices[0].message.content if llm_response else 'failed'
                    print(f"\n\033[32mresponse:\033[0m\n\033[34m{reply_text}\033[0m")
                    print(f"\033[35mmodel:\033[0m\033[36m{model}\033[0m")

                if llm_response:
                    try:
                        result = extract_xml_data(["links"], llm_response.choices[0].message.content)
                        sec_link_blocks.extend(result.get("links"))
                    except Exception as e:
                        _msg = f"link result parse error: {e}"
                        wis_logger.error(_msg)
                else:
                    _msg = "LLM Service Temporarily Unavailable"
                    wis_logger.error(_msg)
            else:
                if self.schema:
                    model = performance_model # for this stage
                    messages=[{"role": "user", "content": self.prompt.replace('{HTML}', sec_pre + markdown) + date_time_notify}]
                else:
                    model = selected_model # for this stage
                    messages=[{"role": "user", "content": self.prompt_only_info.replace('{HTML}', sec_pre + markdown) + date_time_notify}]

                if VERBOSE:
                    print(f"\n\033[32mprompt:\033[0m\n\033[34m{messages[0]['content']}\033[0m")
                
                llm_response = await llm_async(
                    messages=messages,
                    model=model,
                    temperature=0.1
                )

                if VERBOSE:
                    reply_text = llm_response.choices[0].message.content if llm_response else 'failed'
                    print(f"\n\033[32mresponse:\033[0m\n\033[34m{reply_text}\033[0m")
                    print(f"\033[35mmodel:\033[0m\033[36m{model}\033[0m")

                if llm_response:
                    if self.schema:
                        try:
                            result = extract_xml_data(["json"], llm_response.choices[0].message.content)
                            sec_infos = await info_process(result.get("json", []), 'schema', url, title, author, publish_date, link_dict, markdown)
                        except Exception as e:
                            _msg = f"custom schema result parse error: {e}"
                            wis_logger.error(_msg)
                    else:
                        try:
                            if mode == 'only_info':
                                result = extract_xml_data(["info"], llm_response.choices[0].message.content)
                            else:
                                result = extract_xml_data(["info", "links"], llm_response.choices[0].message.content)
                                sec_link_blocks.extend(result.get("links"))

                            sec_infos = await info_process(result.get("info", []), 'journal', url, title, author, publish_date, link_dict, markdown)
                        except Exception as e:
                            _msg = f"info result parse error: {e}"
                            wis_logger.error(_msg)
                else:
                    _msg = "LLM Service Tempetally Unavailable"
                    wis_logger.error(_msg)
                
                if VERBOSE:
                    print("=== Token Usage Summary ===")
                    print(f"Completion: {llm_response.usage.completion_tokens:>12,} tokens")
                    print(f"Prompt: {llm_response.usage.prompt_tokens:>12,} tokens")
                    print(f"Total: {llm_response.usage.total_tokens:>12,} tokens")
                    
            self.apply_count += 1
            if not sec_infos and not sec_link_blocks:
                self.apply_failed += 1
                # 要把缓存中的记录删掉
                await self.cache_manager.delete(cache_key, namespace=cache_namespace)
                if self.apply_failed >= APLPLY_FAILED_TIMES_THRESHOLD:
                    wis_logger.warning(f"Focus {self.focus_id} apply failed times threshold reached, raise RuntimeError")
                    raise RuntimeError("88")
                continue

            infos.extend(sec_infos)
            link_blocks.extend(sec_link_blocks)

        # 先解析 links，'/n'.jion后直接提取即可
        more_links = set()
        hallucination_times = 0
        links = re.findall(r'\[\d+]', '\n'.join(link_blocks))
        for link in links:
            if link not in link_dict:
                hallucination_times += 1
                continue
            more_links.add(link_dict[link])

        wis_logger.debug(f"returned from server and parse {len(more_links)} links")
        if hallucination_times > 0:
            hallucination_rate = round((hallucination_times / len(links)) * 100, 2) if len(links) > 0 else 'NA'
            wis_logger.info(
                f"[QualityAssessment] Focus {self.focus_id} - link extraction, hallucination times: {hallucination_times}, hallucination rate: {hallucination_rate} %")
        
        if mode == 'only_link':
            return 0, more_links
        
        # 解析 infos 存储过程，注意过滤 **empty** 和 空内容
        info_count = 0
        for info in infos:
            if not info or not isinstance(info, dict):
                continue

            if info.get('content', '') in ['**empty**', '']:
                continue

            if info.get('type', '') == 'schema':
                info['content'] = await asyncio.get_event_loop().run_in_executor(
                    None,  # 使用默认线程池
                    self._parse_custom_schema_block,
                    info['content']
                )
                if not info['content']:
                    continue
            
            info_count += 1
            if self.db_manager:
                await self.db_manager.add_info(
                    focus_statement=self.focus_statement,
                    focus_id=self.focus_id,
                    **info
                )
        # 根据抽取结果判断是否需要缓存（作为信源级已经缓存5h了，这里其实是判断这是文章页还是列表页，标准是提取出 info 且提取出的links 不超过5个）：
        if (mode == 'only_info' or (info_count > 0 and len(more_links) < 5)) and markdown and url:
            await self.cache_manager.update_ttl(url, 60*24*config['WEB_ARTICLE_TTL'])
        
        return info_count, more_links

    def _parse_custom_schema_block(self, schema_block: str) -> str:
        hallucination_times = 0
        try:
            results = json.loads(schema_block)
        except json.JSONDecodeError:
            wis_logger.info("json loads from response failed, fallback to use split_and_parse")
            hallucination_times += 1
            results, unparsed = split_and_parse_json_objects(schema_block)
            if unparsed:
                wis_logger.info(f"some generated parts can not be parsed: {unparsed}")

        schema_keys = self.schema.keys()
        filtered_results = []
        for result in results:
            # 将 keys() 转换为列表，避免在遍历时修改字典导致的问题
            for key in list(result.keys()):
                if key not in schema_keys:
                    hallucination_times += 1
                    del result[key]
            for key in schema_keys:
                if key not in result:
                    hallucination_times += 1
                    result[key] = ''
            
            # 检查如果 result 的全部 value 都是空值，则返回 None （这倒也不能说是 llm 失败，它可能是为了保证结果等于schema）
            if all(not value or (isinstance(value, str) and value.strip() == '') for value in result.values()):
                continue
            filtered_results.append(result)
            
        if hallucination_times > 0:
            hallucination_rate = round((hallucination_times / len(results)) * 100, 2) if len(results) > 0 else 'NA'
            wis_logger.info(
                f"[QualityAssessment] Focus {self.focus_id} - custom schema extraction, hallucination times: {hallucination_times}, hallucination rate: {hallucination_rate} %")
        
        if not filtered_results:
            return ''
        return json.dumps(filtered_results, indent=2, ensure_ascii=False)
        
    def custom_run(self, extractor: ExtractionStrategy, chunking: ChunkingStrategy, article: CrawlResult, *q, **kwargs) -> List[Dict[str, Any]]:
        """
        用于运行 Crawl4ai 提供的LLM-free extractor（ Json 提取器或者 Regex 提取器）
        未与主流程（数据库、缓存库）打通，仅仅是为了兼容使用
        用户必须提供 extractor 和 chunking 输入
        必须接受 article 输入
        """
        if not article.html and not article.cleaned_html and not article.markdown:
            wis_logger.info(f"{article.url} has no required content to extract, skip")
            return []
        
        url = article.url or ''
        content = article.html or article.cleaned_html or article.markdown
        sections = chunking.chunk(content)

        t1 = time.perf_counter()
        try:
            results = extractor.run(url, sections, *q, **kwargs)
            # Log extraction completion
            wis_logger.info(f"[EXTRACT] ✓ {url:.30}... | ⏱: {int((time.perf_counter() - t1) * 1000) / 1000:.2f}s")
            return results
        except Exception as e:
            wis_logger.error(f"[EXTRACT] ✗ {url:.30}... | {e}")
            return []
