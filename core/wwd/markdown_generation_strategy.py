from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
from .base.crawl4ai_models import MarkdownGenerationResult
from .html2text import CustomHTML2Text
import regex as re
from .utils import normalize_url, url_pattern, is_valid_img_url
import os
from async_lru import alru_cache

# Pre-compile the regex pattern
# LINK_PATTERN = re.compile(r'!?\[([^\]]+)\]\(([^)]+?)(?:\s+"([^"]*)")?\)')

vl_model = os.environ.get("VL_MODEL", "")
if not vl_model:
    print("VL_MODEL not set, will skip extracting info from img, some info may be lost!")

@alru_cache(maxsize=1000)
async def extract_info_from_img(url: str) -> str:
    if not vl_model:
        return '§to_be_recognized_by_visual_llm§'
    """
    llm_output = await llm([{"role": "user",
        "content": [{"type": "image_url", "image_url": {"url": url, "detail": "high"}},
        {"type": "text", "text": "提取图片中的所有文字，如果图片不包含文字或者文字很少或者你判断图片仅是网站logo、商标、图标等，则输出NA。注意请仅输出提取出的文字，不要输出别的任何内容。"}]}],
        model=vl_model)

    return llm_output
    """
    return '§to_be_recognized_by_visual_llm§'

class MarkdownGenerationStrategy(ABC):
    """Abstract base class for markdown generation strategies."""

    def __init__(
        self,
        content_filter = None,
        options: Optional[Dict[str, Any]] = None,
        verbose: bool = False,
        content_source: str = "cleaned_html",
    ):
        self.content_filter = content_filter
        self.options = options or {}
        self.verbose = verbose
        self.content_source = content_source

    @abstractmethod
    def generate_markdown(
        self,
        input_html: str,
        base_url: str = "",
        html2text_options: Optional[Dict[str, Any]] = None,
        citations: bool = True,
        **kwargs,
    ) -> MarkdownGenerationResult:
        """Generate markdown from the selected input HTML."""
        pass


class DefaultMarkdownGenerator(MarkdownGenerationStrategy):
    """
    Default implementation of markdown generation strategy.

    How it works:
    1. Generate raw markdown from cleaned HTML.
    2. Convert links to citations.
    3. Generate fit markdown if content filter is provided.
    4. Return MarkdownGenerationResult.

    Args:
        content_filter (Optional[RelevantContentFilter]): Content filter for generating fit markdown.
        options (Optional[Dict[str, Any]]): Additional options for markdown generation. Defaults to None.
        content_source (str): Source of content to generate markdown from. Options: "cleaned_html", "raw_html", "fit_html". Defaults to "cleaned_html".

    Returns:
        MarkdownGenerationResult: Result containing raw markdown, fit markdown, fit HTML, and references markdown.
    """

    def __init__(
        self,
        content_filter = None,
        options: Optional[Dict[str, Any]] = None,
        content_source: str = "cleaned_html",
    ):
        super().__init__(content_filter, options, verbose=False, content_source=content_source)

    async def convert_links_to_citations(self, markdown: str, base_url: str = "") -> Tuple[str, dict]:
        """
        bigbrother666sh modified:
        use wisefow V3.9's preprocess instead
        """
        link_dict = {}

        # for special url formate from craw4ai-de 0.4.247
        markdown = re.sub(r'<javascript:.*?>', '<javascript:>', markdown).strip()

        # 处理图片标记 ![alt](src)，使用非贪婪匹配并考虑嵌套括号的情况
        i_pattern = r'(!\[(.*?)\]\(((?:[^()]*|\([^()]*\))*)\))'
        matches = re.findall(i_pattern, markdown, re.DOTALL)
        for _sec, alt, src in matches:
            # 替换为新格式 §alt||src§
            markdown = markdown.replace(_sec, f'§{alt}||{src}§', 1)

        async def check_url_text(text) -> str:
            # 找到所有[part0](part1)格式的片段，使用非贪婪匹配并考虑嵌套括号的情况
            link_pattern = r'(\[(.*?)\]\(((?:[^()]*|\([^()]*\))*)\))'
            matches = re.findall(link_pattern, text, re.DOTALL)
            for _sec, link_text, link_url in matches:
                # 存在""嵌套情况，需要先提取出url
                _title = re.sub(url_pattern, '', link_url, re.DOTALL).strip()
                _title = _title.strip('"')
                link_text = link_text.strip()
                if _title and _title not in link_text:
                    link_text = f"{_title} - {link_text}"
                """
                # for protecting_links model
                real_url_pattern = r'<(.*?)>'
                real_url = re.search(real_url_pattern, link_url, re.DOTALL)
                if real_url:
                    _url = real_url.group(1).strip()
                else:
                    _url = re.sub(quote_pattern, '', link_url, re.DOTALL).strip()
                """
                _url = re.findall(url_pattern, link_url)
                if not _url or _url[0].startswith(('#', 'javascript:')):
                    text = text.replace(_sec, link_text, 1)
                    continue
                url = normalize_url(_url[0], base_url)
                
                # 分离§§内的内容和后面的内容
                img_marker_pattern = r'§(.*?)\|\|(.*?)§'
                inner_matches = re.findall(img_marker_pattern, link_text, re.DOTALL)
                for alt, src in inner_matches:
                    link_text = link_text.replace(f'§{alt}||{src}§', '')

                if not link_text and inner_matches:
                    img_alt = inner_matches[0][0].strip()
                    img_src = inner_matches[0][1].strip()
                    if img_src and not img_src.startswith('#'):
                        img_src = normalize_url(img_src, base_url)
                        if not img_src:
                            link_text = img_alt
                        elif len(img_alt) > 2:
                            _key = f"[img{len(link_dict)+1}]"
                            link_dict[_key] = img_src
                            link_text = img_alt
                        elif not is_valid_img_url(img_src):
                            _key = f"[img{len(link_dict)+1}]"
                            link_dict[_key] = img_src
                            link_text = img_alt
                        else:
                            link_text = await extract_info_from_img(img_src)
                            _key = f"[img{len(link_dict)+1}]"
                            link_dict[_key] = img_src
                    else:
                        link_text = img_alt

                _key = f"[{len(link_dict)+1}]"
                link_dict[_key] = url
                text = text.replace(_sec, link_text + _key, 1)
    
            # 处理文本中的其他图片标记
            img_pattern = r'(§(.*?)\|\|(.*?)§)'
            matches = re.findall(img_pattern, text, re.DOTALL)
            remained_text = re.sub(img_pattern, '', text, re.DOTALL).strip()
            remained_text_len = len(remained_text)
            for _sec, alt, src in matches:
                if not src or src.startswith('#'):
                    text = text.replace(_sec, alt, 1)
                    continue
                img_src = normalize_url(src, base_url)
                if not img_src:
                    text = text.replace(_sec, alt, 1)
                elif remained_text_len > 5 or len(alt) > 2:
                    _key = f"[{len(link_dict)+1}]"
                    link_dict[_key] = img_src
                    text = text.replace(_sec, alt + _key, 1)
                elif not is_valid_img_url(img_src):
                    _key = f"[{len(link_dict)+1}]"
                    link_dict[_key] = img_src
                    text = text.replace(_sec, alt + _key, 1)
                else:
                    _key = f"[{len(link_dict)+1}]"
                    link_dict[_key] = img_src
                    text = text.replace(_sec, await extract_info_from_img(img_src) + _key, 1)

            # 处理文本中的"野 url"，使用更精确的正则表达式
            matches = re.findall(url_pattern, text)
            for url in matches:
                url = normalize_url(url, base_url)
                _key = f"[{len(link_dict)+1}]"
                link_dict[_key] = url
                text = text.replace(url, _key, 1)

            return text

        sections = await check_url_text(markdown)

        return sections, link_dict

    async def generate_markdown(
        self,
        input_html: str,
        base_url: str = "",
        html2text_options: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> MarkdownGenerationResult:
        """
        Generate markdown with citations from the provided input HTML.

        How it works:
        1. Generate raw markdown from the input HTML.
        2. Convert links to citations.
        4. Return MarkdownGenerationResult.

        Args:
            input_html (str): The HTML content to process (selected based on content_source).
            base_url (str): Base URL for URL joins.
            html2text_options (Optional[Dict[str, Any]]): HTML2Text options.
            options (Optional[Dict[str, Any]]): Additional options for markdown generation.

        Returns:
            MarkdownGenerationResult: Result containing raw markdown and link dict
        
        bigbrother666sh modified:
        add raw markdown preprocess as a must process
        """
        try:
            # Initialize HTML2Text with default options for better conversion
            h = CustomHTML2Text(baseurl=base_url)
            default_options = {
                "body_width": 0,  # Disable text wrapping
                "ignore_emphasis": False,
                "ignore_links": False,
                "ignore_images": False,
                "protect_links": False,
                "single_line_break": True,
                "mark_code": True,
                "escape_snob": False,
            }

            # Update with custom options if provided
            if html2text_options:
                default_options.update(html2text_options)
            elif options:
                default_options.update(options)
            elif self.options:
                default_options.update(self.options)

            h.update_params(**default_options)

            # Ensure we have valid input
            if not input_html:
                input_html = ""
            elif not isinstance(input_html, str):
                input_html = str(input_html)

            # Generate raw markdown
            try:
                raw_markdown = h.handle(input_html)
            except Exception as e:
                raw_markdown = f"Error converting HTML to markdown: {str(e)}"

            raw_markdown = raw_markdown.replace("    ```", "```")

            # Convert links to citations
            link_dict: dict = {}
            try:
                raw_markdown, link_dict = await self.convert_links_to_citations(raw_markdown, base_url)
            except Exception as e:
                raw_markdown = f"Error generating citations[wiseflow preprocess]: {str(e)}"

            # Generate fit markdown if content filter is provided
            # bigbrother666sh: content filter is not needed in wiseflow
            return MarkdownGenerationResult(
                raw_markdown=raw_markdown or "",
                link_dict=link_dict or {}
            )
        except Exception as e:
            # If anything fails, return empty strings with error message
            error_msg = f"Error in markdown generation: {str(e)}"
            return MarkdownGenerationResult(
                raw_markdown=error_msg,
                link_dict={}
            )
