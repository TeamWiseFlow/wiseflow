import time
from bs4 import BeautifulSoup, Comment, element, Tag, NavigableString
import json
import html
import lxml
import regex as re
import os
import platform
from array import array
from .config import MIN_WORD_THRESHOLD
import httpx
from socket import gaierror
from typing import Dict, List, Callable, Tuple, Sequence
from urllib.parse import urljoin
import xxhash
import cProfile
import pstats
from functools import wraps
import asyncio
from lxml import etree, html as lhtml
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from functools import lru_cache

from . import __version__
import psutil
import subprocess
from itertools import chain
from urllib.parse import urlparse, urljoin, urlunparse, parse_qs, urlencode


common_file_exts = [
    '.css', '.csv', '.ics', '.js',
    # Images
    '.bmp', '.gif', '.jpeg', '.jpg', '.png', '.svg', '.tiff', '.ico', '.webp',
    # Audio
    '.mp3', '.wav', '.ogg', '.m4a', '.aac', '.midi', '.mid',
    # Video
    '.mp4', '.mpeg', '.webm', '.avi', '.mov', '.flv', '.wmv', '.mkv',
    # Applications
    '.json', '.zip', '.gz', '.tar', '.rar', '.7z', '.exe', '.msi',
    # Fonts
    '.woff', '.woff2', '.ttf', '.otf',
    # Microsoft Office
    '.doc', '.dot', '.docx', '.xlsx', '.xls', '.ppt', '.pptx',
    # OpenDocument Formats
    '.odt', '.ods', '.odp',
    # Archives
    '.tar.gz', '.tgz', '.bz2',
    # Others
    '.rtf', '.apk', '.epub', '.jar', '.swf', '.ps', '.ai', '.eps',
    '.bin', '.dmg', '.iso', '.deb', '.rpm', '.sqlite',
    # PHP
    '.php', '.php3', '.php4', '.php5', '.php7', '.phtml', '.phps',
    # Additional formats
    '.yaml', '.yml', '.asp', '.jsp'
]

common_tlds = [
    '.com', '.cn', '.net', '.org', '.edu', '.gov', '.io', '.co',
    '.info', '.biz', '.me', '.tv', '.cc', '.xyz', '.app', '.dev',
    '.cloud', '.ai', '.tech', '.online', '.store', '.shop', '.site',
    '.top', '.vip', '.pro', '.ltd', '.group', '.team', '.work'
]

url_pattern = r'((?:https?://|www\.)[-A-Za-z0-9+&@#/%?=~_|!:,.;]*[-A-Za-z0-9+&@#/%=~_|])'

params_to_remove = [
    'utm_source', 'utm_medium', 'utm_campaign', 
    'utm_term', 'utm_content', 'fbclid', 'gclid',
    'utm_id', 'utm_source_platform', 'utm_creative_format',
    'utm_marketing_tactic', 'ref', 'referrer', 'source',
    'fb_action_ids', 'fb_action_types', 'fb_ref',
    'fb_source', 'action_object_map', 'action_type_map',
    'action_ref_map', '_ga', '_gl', '_gcl_au',
    'mc_cid', 'mc_eid', '_bta_tid', '_bta_c',
    'trk_contact', 'trk_msg', 'trk_module', 'trk_sid',
    'gdfms', 'gdftrk', 'gdffi', '_ke',
    'redirect_log_mongo_id', 'redirect_mongo_id',
    'sb_referrer_host', 'mkt_tok', 'mkt_unsubscribe',
    'amp', 'amp_js_v', 'amp_r', '__twitter_impression',
    's_kwcid', 'msclkid', 'dm_i', 'epik',
    'pk_campaign', 'pk_kwd', 'pk_keyword',
    'piwik_campaign', 'piwik_kwd', 'piwik_keyword',
    'mtm_campaign', 'mtm_keyword', 'mtm_source',
    'mtm_medium', 'mtm_content', 'mtm_cid',
    'mtm_group', 'mtm_placement', 'yclid',
    '_openstat', 'wt_zmc', 'wt.zmc', 'from',
    'xtor', 'xtref', 'xpid', 'xpsid',
    'xpcid', 'xptid', 'xpt', 'xps',
    'xpc', 'xpd', 'xpe', 'xpf',
    'xpg', 'xph', 'xpi', 'xpj',
    'xpk', 'xpl', 'xpm', 'xpn',
    'xpo', 'xpp', 'xpq', 'xpr',
    'xps', 'xpt', 'xpu', 'xpv',
    'xpw', 'xpx', 'xpy', 'xpz'
]

@lru_cache(maxsize=1000)
def normalize_url(url: str, base_url: str = None) -> str:
    if not url:
        return ""

    url = url.strip()
    if not url:
        return ""
    # Handle special URL schemes that shouldn't be modified
    special_schemes = ['mailto:', 'tel:', 'javascript:', 'data:']
    if any(url.lower().startswith(scheme) for scheme in special_schemes):
        return url

    if url.startswith(('www.', 'WWW.')):
        _url = f"https://{url}"
    elif url.startswith('/www.'):
        _url = f"https:/{url}"
    elif url.startswith("//"):
        _url = f"https:{url}"
    elif url.startswith(('http://', 'https://')):
        _url = url
    elif url.startswith('http:/'):
        _url = f"http://{url[6:]}"
    elif url.startswith('https:/'):
        _url = f"https://{url[7:]}"
    else:
        _url = urljoin(base_url, url)

    try:
        parsed = urlparse(_url)
        query_params = parse_qs(parsed.query)
    
        for param in params_to_remove:
            query_params.pop(param, None)
    
        new_query = urlencode(query_params, doseq=True)
    
        cleaned_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
    
        return cleaned_url

    except Exception as e:
        print(f"Error cleaning URL '{_url}': {e}")
        try:
            # More robust fallback that preserves the original URL structure
            _ss = _url.split('//')
            if len(_ss) == 2:
                return '//'.join(_ss)
            else:
                return _ss[0] + '//' + '/'.join(_ss[1:])
        except Exception as fallback_error:
            print(f"Fallback error for URL '{_url}': {fallback_error}")
            # Ultimate fallback - return the input
            return _url

def is_valid_img_url(url: str) -> bool:
    """
    Check if a URL is a valid image URL.
    """
    if not url:
        return False
    if url.startswith('data:image'):
        return True
    if not url.startswith('http'):
        return False

    clean_url = url.split('?')[0].split('#')[0].lower().rstrip('/')
    return any(clean_url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp'])

@lru_cache(maxsize=1000)
def can_process_url(url: str) -> bool:
        """
        Validate the URL format and apply filtering.
        For the starting URL (depth 0), filtering is bypassed.
        """
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False    
            if parsed.scheme not in ("http", "https"):
                return False
            if "." not in parsed.netloc:
                return False
        except Exception:
            return False

        return True

def free_port() -> int:
    """
    Determines a free port using sockets.
    """
    import socket

    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind(("127.0.0.1", 0))
    free_socket.listen(5)
    port: int = free_socket.getsockname()[1]
    free_socket.close()
    return port

def merge_chunks(
    docs: Sequence[str], 
    target_size: int,
    overlap: int = 0,
    word_token_ratio: float = 1.0,
    splitter: Callable = None
) -> List[str]:
    """Merges documents into chunks of specified token size.
    
    Args:
        docs: Input documents
        target_size: Desired token count per chunk
        overlap: Number of tokens to overlap between chunks
        word_token_ratio: Multiplier for word->token conversion
    """
    # Pre-tokenize all docs and store token counts
    splitter = splitter or str.split
    token_counts = array('I')
    all_tokens: List[List[str]] = []
    total_tokens = 0
    
    for doc in docs:
        tokens = splitter(doc)
        count = int(len(tokens) * word_token_ratio)
        if count:  # Skip empty docs
            token_counts.append(count)
            all_tokens.append(tokens)
            total_tokens += count
    
    if not total_tokens:
        return []

    # Pre-allocate chunks
    num_chunks = max(1, (total_tokens + target_size - 1) // target_size)
    chunks: List[List[str]] = [[] for _ in range(num_chunks)]
    
    curr_chunk = 0
    curr_size = 0
    
    # Distribute tokens
    for tokens in chain.from_iterable(all_tokens):
        if curr_size >= target_size and curr_chunk < num_chunks - 1:
            if overlap > 0:
                overlap_tokens = chunks[curr_chunk][-overlap:]
                curr_chunk += 1
                chunks[curr_chunk].extend(overlap_tokens)
                curr_size = len(overlap_tokens)
            else:
                curr_chunk += 1
                curr_size = 0
                
        chunks[curr_chunk].append(tokens)
        curr_size += 1

    # Return only non-empty chunks
    return [' '.join(chunk) for chunk in chunks if chunk]

class InvalidCSSSelectorError(Exception):
    pass

SPLITS = bytearray([
    # Control chars (0-31) + space (32)
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    # Special chars (33-47): ! " # $ % & ' ( ) * + , - . /
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    # Numbers (48-57): Treat as non-splits
    0,0,0,0,0,0,0,0,0,0,
    # More special chars (58-64): : ; < = > ? @
    1,1,1,1,1,1,1,
    # Uppercase (65-90): Keep
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    # More special chars (91-96): [ \ ] ^ _ `
    1,1,1,1,1,1,
    # Lowercase (97-122): Keep
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    # Special chars (123-126): { | } ~
    1,1,1,1,
    # Extended ASCII
    *([1] * 128)
])

# Additional split chars for HTML/code
HTML_CODE_CHARS = {
    # HTML specific
    '•', '►', '▼', '©', '®', '™', '→', '⇒', '≈', '≤', '≥',
    # Programming symbols  
    '+=', '-=', '*=', '/=', '=>', '<=>', '!=', '==', '===',
    '++', '--', '<<', '>>', '&&', '||', '??', '?:', '?.', 
    # Common Unicode
    '…', '"', '"', ''', ''', '«', '»', '—', '–',
    # Additional splits
    '+', '=', '~', '@', '#', '$', '%', '^', '&', '*',
    '(', ')', '{', '}', '[', ']', '|', '\\', '/', '`',
    '<', '>', ',', '.', '?', '!', ':', ';', '-', '_'
}

def advanced_split(text: str) -> list[str]:
    result = []
    word = array('u')
    
    i = 0
    text_len = len(text)
    
    while i < text_len:
        char = text[i]
        o = ord(char)
        
        # Fast path for ASCII
        if o < 256 and SPLITS[o]:
            if word:
                result.append(word.tounicode())
                word = array('u')
        # Check for multi-char symbols
        elif i < text_len - 1:
            two_chars = char + text[i + 1]
            if two_chars in HTML_CODE_CHARS:
                if word:
                    result.append(word.tounicode())
                    word = array('u')
                i += 1  # Skip next char since we used it
            else:
                word.append(char)
        else:
            word.append(char)
        i += 1
            
    if word:
        result.append(word.tounicode())
        
    return result

def calculate_semaphore_count():
    """
    Calculate the optimal semaphore count based on system resources.

    How it works:
    1. Determines the number of CPU cores and total system memory.
    2. Sets a base count as half of the available CPU cores.
    3. Limits the count based on memory, assuming 2GB per semaphore instance.
    4. Returns the minimum value between CPU and memory-based limits.

    Returns:
        int: The calculated semaphore count.
    """

    cpu_count = os.cpu_count()
    memory_gb = get_system_memory() / (1024**3)  # Convert to GB
    base_count = max(1, cpu_count // 2)
    memory_based_cap = int(memory_gb / 2)  # Assume 2GB per instance
    return min(base_count, memory_based_cap)


def get_system_memory():
    """
    Get the total system memory in bytes.

    How it works:
    1. Detects the operating system.
    2. Reads memory information from system-specific commands or files.
    3. Converts the memory to bytes for uniformity.

    Returns:
        int: The total system memory in bytes.

    Raises:
        OSError: If the operating system is unsupported.
    """

    system = platform.system()
    if system == "Linux":
        with open("/proc/meminfo", "r") as mem:
            for line in mem:
                if line.startswith("MemTotal:"):
                    return int(line.split()[1]) * 1024  # Convert KB to bytes
    elif system == "Darwin":  # macOS
        import subprocess

        output = subprocess.check_output(["sysctl", "-n", "hw.memsize"]).decode("utf-8")
        return int(output.strip())
    elif system == "Windows":
        import ctypes

        kernel32 = ctypes.windll.kernel32
        c_ulonglong = ctypes.c_ulonglong

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", c_ulonglong),
                ("ullAvailPhys", c_ulonglong),
                ("ullTotalPageFile", c_ulonglong),
                ("ullAvailPageFile", c_ulonglong),
                ("ullTotalVirtual", c_ulonglong),
                ("ullAvailVirtual", c_ulonglong),
                ("ullAvailExtendedVirtual", c_ulonglong),
            ]

        memoryStatus = MEMORYSTATUSEX()
        memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        kernel32.GlobalMemoryStatusEx(ctypes.byref(memoryStatus))
        return memoryStatus.ullTotalPhys
    else:
        raise OSError("Unsupported operating system")

def beautify_html(escaped_html):
    """
    Beautifies an escaped HTML string.

    Parameters:
    escaped_html (str): A string containing escaped HTML.

    Returns:
    str: A beautifully formatted HTML string.
    """
    # Unescape the HTML string
    unescaped_html = html.unescape(escaped_html)

    # Use BeautifulSoup to parse and prettify the HTML
    soup = BeautifulSoup(unescaped_html, "html.parser")
    pretty_html = soup.prettify()

    return pretty_html


def split_and_parse_json_objects(json_string):
    """
    Splits a JSON string which is a list of objects and tries to parse each object.

    Parameters:
    json_string (str): A string representation of a list of JSON objects, e.g., '[{...}, {...}, ...]'.

    Returns:
    tuple: A tuple containing two lists:
        - First list contains all successfully parsed JSON objects.
        - Second list contains the string representations of all segments that couldn't be parsed.
    """
    # Trim the leading '[' and trailing ']'
    if json_string.startswith("[") and json_string.endswith("]"):
        json_string = json_string[1:-1].strip()

    # Split the string into segments that look like individual JSON objects
    segments = []
    depth = 0
    start_index = 0

    for i, char in enumerate(json_string):
        if char == "{":
            if depth == 0:
                start_index = i
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                segments.append(json_string[start_index : i + 1])

    # Try parsing each segment
    parsed_objects = []
    unparsed_segments = []

    for segment in segments:
        try:
            obj = json.loads(segment)
            parsed_objects.append(obj)
        except json.JSONDecodeError:
            unparsed_segments.append(segment)

    return parsed_objects, unparsed_segments


def sanitize_html(html):
    """
    Sanitize an HTML string by escaping quotes.

    How it works:
    1. Replaces all unwanted and special characters with an empty string.
    2. Escapes double and single quotes for safe usage.

    Args:
        html (str): The HTML string to sanitize.

    Returns:
        str: The sanitized HTML string.
    """

    # Replace all unwanted and special characters with an empty string
    sanitized_html = html
    # sanitized_html = re.sub(r'[^\w\s.,;:!?=\[\]{}()<>\/\\\-"]', '', html)

    # Escape all double and single quotes
    sanitized_html = sanitized_html.replace('"', '\\"').replace("'", "\\'")

    return sanitized_html


def sanitize_input_encode(text: str) -> str:
    """Sanitize input to handle potential encoding issues."""
    try:
        try:
            if not text:
                return ""
            # Attempt to encode and decode as UTF-8 to handle potential encoding issues
            return text.encode("utf-8", errors="ignore").decode("utf-8")
        except UnicodeEncodeError as e:
            print(
                f"Warning: Encoding issue detected. Some characters may be lost. Error: {e}"
            )
            # Fall back to ASCII if UTF-8 fails
            return text.encode("ascii", errors="ignore").decode("ascii")
    except Exception as e:
        raise ValueError(f"Error sanitizing input: {str(e)}") from e


def escape_json_string(s):
    """
    Escapes characters in a string to be JSON safe.

    Parameters:
    s (str): The input string to be escaped.

    Returns:
    str: The escaped string, safe for JSON encoding.
    """
    # Replace problematic backslash first
    s = s.replace("\\", "\\\\")

    # Replace the double quote
    s = s.replace('"', '\\"')

    # Escape control characters
    s = s.replace("\b", "\\b")
    s = s.replace("\f", "\\f")
    s = s.replace("\n", "\\n")
    s = s.replace("\r", "\\r")
    s = s.replace("\t", "\\t")

    # Additional problematic characters
    # Unicode control characters
    s = re.sub(r"[\x00-\x1f\x7f-\x9f]", lambda x: "\\u{:04x}".format(ord(x.group())), s)

    return s


def replace_inline_tags(soup, tags, only_text=False):
    """
    Replace inline HTML tags with Markdown-style equivalents.

    How it works:
    1. Maps specific tags (e.g., <b>, <i>) to Markdown syntax.
    2. Finds and replaces all occurrences of these tags in the provided BeautifulSoup object.
    3. Optionally replaces tags with their text content only.

    Args:
        soup (BeautifulSoup): Parsed HTML content.
        tags (List[str]): List of tags to replace.
        only_text (bool): Whether to replace tags with plain text. Defaults to False.

    Returns:
        BeautifulSoup: Updated BeautifulSoup object with replaced tags.
    """

    tag_replacements = {
        "b": lambda tag: f"**{tag.text}**",
        "i": lambda tag: f"*{tag.text}*",
        "u": lambda tag: f"__{tag.text}__",
        "span": lambda tag: f"{tag.text}",
        "del": lambda tag: f"~~{tag.text}~~",
        "ins": lambda tag: f"++{tag.text}++",
        "sub": lambda tag: f"~{tag.text}~",
        "sup": lambda tag: f"^^{tag.text}^^",
        "strong": lambda tag: f"**{tag.text}**",
        "em": lambda tag: f"*{tag.text}*",
        "code": lambda tag: f"`{tag.text}`",
        "kbd": lambda tag: f"`{tag.text}`",
        "var": lambda tag: f"_{tag.text}_",
        "s": lambda tag: f"~~{tag.text}~~",
        "q": lambda tag: f'"{tag.text}"',
        "abbr": lambda tag: f"{tag.text} ({tag.get('title', '')})",
        "cite": lambda tag: f"_{tag.text}_",
        "dfn": lambda tag: f"_{tag.text}_",
        "time": lambda tag: f"{tag.text}",
        "small": lambda tag: f"<small>{tag.text}</small>",
        "mark": lambda tag: f"=={tag.text}==",
    }

    replacement_data = [
        (tag, tag_replacements.get(tag, lambda t: t.text)) for tag in tags
    ]

    for tag_name, replacement_func in replacement_data:
        for tag in soup.find_all(tag_name):
            replacement_text = tag.text if only_text else replacement_func(tag)
            tag.replace_with(replacement_text)

    return soup

    # for tag_name in tags:
    #     for tag in soup.find_all(tag_name):
    #         if not only_text:
    #             replacement_text = tag_replacements.get(tag_name, lambda t: t.text)(tag)
    #             tag.replace_with(replacement_text)
    #         else:
    #             tag.replace_with(tag.text)

    # return soup

def get_content_of_website(
    html, word_count_threshold=MIN_WORD_THRESHOLD, tags_to_remove=None):
    """
    bigbrother666 modified this function, 2025-05-18
    an alternative to preprocess_html_for_schema, just return cleaned_html

    How it works:
    1. Parses the HTML content using BeautifulSoup.
    2. Extracts internal/external links and media (images, videos, audios).
    3. Cleans the content by removing unwanted tags and attributes.

    Args:
        url (str): The website URL.
        html (str): The HTML content of the website.
        word_count_threshold (int): Minimum word count for content inclusion. Defaults to MIN_WORD_THRESHOLD.
        tags_to_remove (Optional[str]): tags to remove. Defaults to None.

    Returns:
        str: cleaned_html
    """

    try:
        if not html:
            return ""
        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Get the content within the <body> tag
        body = soup.body

        if not tags_to_remove:
            tags_to_remove = [
                'script', 'style', 'noscript', 'iframe', 'canvas', 'svg',
                'video', 'audio', 'source', 'track', 'map', 'area',
                'form', 'input', 'textarea', 'select', 'option', 'button',
                'fieldset', 'legend', 'label', 'datalist', 'output'
            ]

        for tag in body.find_all(tags_to_remove):
            tag.decompose()

        # Remove all attributes from remaining tags in body, except for img and a tags
        for tag in body.find_all():
            if tag.name not in ["img", "a"]:
                tag.attrs = {}

        # Recursively remove empty elements, their parent elements, and elements with word count below threshold
        def remove_empty_and_low_word_count_elements(node, word_count_threshold):
            for child in node.contents:
                if isinstance(child, element.Tag):
                    remove_empty_and_low_word_count_elements(
                        child, word_count_threshold
                    )
                    word_count = len(child.get_text(strip=True).split())
                    if (
                        len(child.contents) == 0 and not child.get_text(strip=True)
                    ) or word_count < word_count_threshold:
                        child.decompose()
            return node

        body = remove_empty_and_low_word_count_elements(body, word_count_threshold)

        def remove_small_text_tags(
            body: Tag, word_count_threshold: int = MIN_WORD_THRESHOLD
        ):
            # We'll use a list to collect all tags that don't meet the word count requirement
            tags_to_remove = []

            # Traverse all tags in the body
            for tag in body.find_all(True):  # True here means all tags
                # Check if the tag contains text and if it's not just whitespace
                if tag.string and tag.string.strip():
                    # Split the text by spaces and count the words
                    word_count = len(tag.string.strip().split())
                    # If the word count is less than the threshold, mark the tag for removal
                    if word_count < word_count_threshold:
                        tags_to_remove.append(tag)

            # Remove all marked tags from the tree
            for tag in tags_to_remove:
                tag.decompose()  # or tag.extract() to remove and get the element

            return body

        # Remove small text tags
        body = remove_small_text_tags(body, word_count_threshold)

        def is_empty_or_whitespace(tag: Tag):
            if isinstance(tag, NavigableString):
                return not tag.strip()
            # Check if the tag itself is empty or all its children are empty/whitespace
            if not tag.contents:
                return True
            return all(is_empty_or_whitespace(child) for child in tag.contents)

        def remove_empty_tags(body: Tag):
            # Continue processing until no more changes are made
            changes = True
            while changes:
                changes = False
                # Collect all tags that are empty or contain only whitespace
                empty_tags = [
                    tag for tag in body.find_all(True) if is_empty_or_whitespace(tag)
                ]
                for tag in empty_tags:
                    # If a tag is empty, decompose it
                    tag.decompose()
                    changes = True  # Mark that a change was made

            return body

        # Remove empty tags
        body = remove_empty_tags(body)

        # Flatten nested elements with only one child of the same type
        def flatten_nested_elements(node):
            for child in node.contents:
                if isinstance(child, element.Tag):
                    flatten_nested_elements(child)
                    if (
                        len(child.contents) == 1
                        and child.contents[0].name == child.name
                    ):
                        # print('Flattening:', child.name)
                        child_content = child.contents[0]
                        child.replace_with(child_content)

            return node

        body = flatten_nested_elements(body)

        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Remove consecutive empty newlines and replace multiple spaces with a single space
        cleaned_html = str(body).replace("\n\n", "\n").replace("  ", " ")

        # Sanitize the cleaned HTML content
        return sanitize_html(cleaned_html)

    except Exception as e:
        print("Error processing HTML content:", str(e))
        return ""

def extract_metadata_using_lxml(html, doc=None):
    """
    Extract metadata from HTML using lxml for better performance.
    """
    metadata = {}

    if not html and doc is None:
        return {}

    if doc is None:
        try:
            doc = lxml.html.document_fromstring(html)
        except Exception:
            return {}

    # Use XPath to find head element
    head = doc.xpath("//head")
    if not head:
        return metadata

    head = head[0]

    # Title - using XPath
    # title = head.xpath(".//title/text()")
    # metadata["title"] = title[0].strip() if title else None

    # === Title Extraction - New Approach ===
    # Attempt to extract <title> using XPath
    title = head.xpath(".//title/text()")
    title = title[0] if title else None

    # Fallback: Use .find() in case XPath fails due to malformed HTML
    if not title:
        title_el = doc.find(".//title")
        title = title_el.text if title_el is not None else None

    # Final fallback: Use OpenGraph or Twitter title if <title> is missing or empty
    if not title:
        title_candidates = (
            doc.xpath("//meta[@property='og:title']/@content") or
            doc.xpath("//meta[@name='twitter:title']/@content")
        )
        title = title_candidates[0] if title_candidates else None

    # Strip and assign title
    metadata["title"] = title.strip() if title else None

    # Meta description - using XPath with multiple attribute conditions
    description = head.xpath('.//meta[@name="description"]/@content')
    metadata["description"] = description[0].strip() if description else None

    # Meta keywords
    keywords = head.xpath('.//meta[@name="keywords"]/@content')
    metadata["keywords"] = keywords[0].strip() if keywords else None

    # Meta author
    author = head.xpath('.//meta[@name="author"]/@content')
    metadata["author"] = author[0].strip() if author else None

    # Open Graph metadata - using starts-with() for performance
    og_tags = head.xpath('.//meta[starts-with(@property, "og:")]')
    for tag in og_tags:
        property_name = tag.get("property", "").strip()
        content = tag.get("content", "").strip()
        if property_name and content:
            metadata[property_name] = content

    # Twitter Card metadata
    twitter_tags = head.xpath('.//meta[starts-with(@name, "twitter:")]')
    for tag in twitter_tags:
        property_name = tag.get("name", "").strip()
        content = tag.get("content", "").strip()
        if property_name and content:
            metadata[property_name] = content
   
   # Article metadata
    article_tags = head.xpath('.//meta[starts-with(@property, "article:")]')
    for tag in article_tags:
        property_name = tag.get("property", "").strip()
        content = tag.get("content", "").strip()
        if property_name and content:
            metadata[property_name] = content

    return metadata

def extract_metadata(html, soup=None):
    """
    Extract optimized content, media, and links from website HTML.

    How it works:
    1. Similar to `get_content_of_website`, but optimized for performance.
    2. Filters and scores images for usefulness.
    3. Extracts contextual descriptions for media files.
    4. Handles excluded tags and CSS selectors.
    5. Cleans HTML and converts it to Markdown.

    Args:
        url (str): The website URL.
        html (str): The HTML content of the website.
        word_count_threshold (int): Minimum word count for content inclusion. Defaults to MIN_WORD_THRESHOLD.
        css_selector (Optional[str]): CSS selector to extract specific content. Defaults to None.
        **kwargs: Additional options for customization.

    Returns:
        Dict[str, Any]: Extracted content including Markdown, cleaned HTML, media, links, and metadata.
    """

    metadata = {}

    if not html and not soup:
        return {}

    if not soup:
        soup = BeautifulSoup(html, "lxml")

    head = soup.head
    if not head:
        return metadata

    # Title
    title_tag = head.find("title")
    metadata["title"] = (
        title_tag.string.strip() if title_tag and title_tag.string else None
    )

    # Meta description
    description_tag = head.find("meta", attrs={"name": "description"})
    metadata["description"] = (
        description_tag.get("content", "").strip() if description_tag else None
    )

    # Meta keywords
    keywords_tag = head.find("meta", attrs={"name": "keywords"})
    metadata["keywords"] = (
        keywords_tag.get("content", "").strip() if keywords_tag else None
    )

    # Meta author
    author_tag = head.find("meta", attrs={"name": "author"})
    metadata["author"] = author_tag.get("content", "").strip() if author_tag else None

    # Open Graph metadata
    og_tags = head.find_all("meta", attrs={"property": re.compile(r"^og:")})
    for tag in og_tags:
        property_name = tag.get("property", "").strip()
        content = tag.get("content", "").strip()
        if property_name and content:
            metadata[property_name] = content

    # Twitter Card metadata
    twitter_tags = head.find_all("meta", attrs={"name": re.compile(r"^twitter:")})
    for tag in twitter_tags:
        property_name = tag.get("name", "").strip()
        content = tag.get("content", "").strip()
        if property_name and content:
            metadata[property_name] = content
    
    # Article metadata
    article_tags = head.find_all("meta", attrs={"property": re.compile(r"^article:")})
    for tag in article_tags:
        property_name = tag.get("property", "").strip()
        content = tag.get("content", "").strip()
        if property_name and content:
            metadata[property_name] = content
    
    return metadata


def extract_xml_tags(string):
    """
    Extracts XML tags from a string.

    Args:
        string (str): The input string containing XML tags.

    Returns:
        List[str]: A list of XML tags extracted from the input string.
    """
    tags = re.findall(r"<(\w+)>", string)
    return list(set(tags))


def extract_xml_data_legacy(tags, string):
    """
    Extract data for specified XML tags from a string.

    How it works:
    1. Searches the string for each tag using regex.
    2. Extracts the content within the tags.
    3. Returns a dictionary of tag-content pairs.

    Args:
        tags (List[str]): The list of XML tags to extract.
        string (str): The input string containing XML data.

    Returns:
        Dict[str, str]: A dictionary with tag names as keys and extracted content as values.
    """

    data = {}

    for tag in tags:
        pattern = f"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, string, re.DOTALL)
        if match:
            data[tag] = match.group(1).strip()
        else:
            data[tag] = ""

    return data

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

def merge_chunks_based_on_token_threshold(chunks, token_threshold):
    """
    Merges small chunks into larger ones based on the total token threshold.

    :param chunks: List of text chunks to be merged based on token count.
    :param token_threshold: Max number of tokens for each merged chunk.
    :return: List of merged text chunks.
    """
    merged_sections = []
    current_chunk = []
    total_token_so_far = 0

    for chunk in chunks:
        chunk_token_count = (
            len(chunk.split()) * 1.3
        )  # Estimate token count with a factor
        if total_token_so_far + chunk_token_count < token_threshold:
            current_chunk.append(chunk)
            total_token_so_far += chunk_token_count
        else:
            if current_chunk:
                merged_sections.append("\n\n".join(current_chunk))
            current_chunk = [chunk]
            total_token_so_far = chunk_token_count

    # Add the last chunk if it exists
    if current_chunk:
        merged_sections.append("\n\n".join(current_chunk))

    return merged_sections

def wrap_text(draw, text, font, max_width):
    """
    Wrap text to fit within a specified width for rendering.

    How it works:
    1. Splits the text into words.
    2. Constructs lines that fit within the maximum width using the provided font.
    3. Returns the wrapped text as a single string.

    Args:
        draw (ImageDraw.Draw): The drawing context for measuring text size.
        text (str): The text to wrap.
        font (ImageFont.FreeTypeFont): The font to use for measuring text size.
        max_width (int): The maximum width for each line.

    Returns:
        str: The wrapped text.
    """

    # Wrap the text to fit within the specified width
    lines = []
    words = text.split()
    while words:
        line = ""
        while (
            words and draw.textbbox((0, 0), line + words[0], font=font)[2] <= max_width
        ):
            line += words.pop(0) + " "
        lines.append(line)
    return "\n".join(lines)

def format_html(html_string):
    """
    Prettify an HTML string using BeautifulSoup.

    How it works:
    1. Parses the HTML string with BeautifulSoup.
    2. Formats the HTML with proper indentation.
    3. Returns the prettified HTML string.

    Args:
        html_string (str): The HTML string to format.

    Returns:
        str: The prettified HTML string.
    """

    soup = BeautifulSoup(html_string, "lxml.parser")
    return soup.prettify()

def fast_format_html(html_string):
    """
    A fast HTML formatter that uses string operations instead of parsing.

    Args:
        html_string (str): The HTML string to format

    Returns:
        str: The formatted HTML string
    """
    # Initialize variables
    indent = 0
    indent_str = "  "  # Two spaces for indentation
    formatted = []
    # in_content = False

    # Split by < and > to separate tags and content
    parts = html_string.replace(">", ">\n").replace("<", "\n<").split("\n")

    for part in parts:
        if not part.strip():
            continue

        # Handle closing tags
        if part.startswith("</"):
            indent -= 1
            formatted.append(indent_str * indent + part)

        # Handle self-closing tags
        elif part.startswith("<") and part.endswith("/>"):
            formatted.append(indent_str * indent + part)

        # Handle opening tags
        elif part.startswith("<"):
            formatted.append(indent_str * indent + part)
            indent += 1

        # Handle content between tags
        else:
            content = part.strip()
            if content:
                formatted.append(indent_str * indent + content)

    return "\n".join(formatted)

@lru_cache(maxsize=1000)
def get_base_domain(url: str) -> str:
    """
    Extract the base domain from a given URL, handling common edge cases.

    How it works:
    1. Parses the URL to extract the domain.
    2. Removes the port number and 'www' prefix.
    3. Handles special domains (e.g., 'co.uk') to extract the correct base.
    4. Correctly identifies and returns IP addresses.

    Args:
        url (str): The URL to extract the base domain from.

    Returns:
        str: The extracted base domain or an empty string if parsing fails.
    """
    try:
        parsed_url = urlparse(url)
        domain_from_url = parsed_url.netloc.lower()
        if not domain_from_url:
            return ""
        # special domain
        if domain_from_url.startswith('mp.weixin.qq.com'):
            return 'mp.weixin.qq.com'

        # Remove port if present
        domain_no_port = domain_from_url.split(":")[0]

        # Check if domain_no_port is an IP address
        is_ip_address = False
        if domain_no_port.count('.') == 3:
            parts_for_ip_check = domain_no_port.split('.')
            # Ensure all parts are digits and within the valid IP address range (0-255)
            if all(part.isdigit() and 0 <= int(part) <= 255 for part in parts_for_ip_check):
                is_ip_address = True
        
        if is_ip_address:
            return domain_no_port

        # Remove www prefix
        domain_no_www = re.sub(r"^www\\.", "", domain_no_port)
        
        parts = domain_no_www.split(".")
        
        # This set is from the original code; for robust TLD extraction, a dedicated library is better.
        special_second_level_domains = { 
            "co", "com", "org", "gov", "edu", "net", "mil", "int", "ac", 
            "ad", "ae", "af", "ag" 
        }

        if len(parts) > 2 and parts[-2] in special_second_level_domains:
            return ".".join(parts[-3:]) # e.g., example.co.uk
        elif len(parts) >= 2: 
            return ".".join(parts[-2:]) # e.g., example.com
        elif len(parts) == 1: 
            return parts[0] # e.g., localhost or a single-label domain
        else:
            # Fallback for empty or near-empty domain strings after processing
            return domain_no_www 
            
    except Exception:
        return ""


def is_external_url(url: str, base_url: str) -> bool:
    """
    Determines if a URL is external to a given base URL.

    How it works:
    1. Normalizes both the target URL and base URL to their base domains using `get_base_domain`.
    2. Compares these normalized base domains.
    3. Relative URLs are considered internal.
    4. URLs that cannot be parsed into a valid domain are typically considered internal or non-comparable based on test expectations.

    Args:
        url (str): The URL to check.
        base_url (str): The base URL to compare against.

    Returns:
        bool: True if the URL is external, False otherwise.
    """
    normalized_base_domain = get_base_domain(base_url)

    if not normalized_base_domain:
        # If the base_url doesn't yield a valid domain, behavior is per original tests.
        # e.g. is_external_url("https://other.com", "") is expected to be False.
        return False

    try:
        # Check if the target URL is relative (has no netloc)
        parsed_target_url = urlparse(url)
        if not parsed_target_url.netloc:  # e.g., "/path/page", "file.html", "not-a-url", "https://"
            return False # Relative URLs (or those parsed as having no domain) are internal

        normalized_target_domain = get_base_domain(url)
        
        # If normalized_target_domain is empty (e.g. for an invalid URL scheme that had a netloc but get_base_domain couldn't process)
        # This path is less likely if `if not parsed_target_url.netloc:` already caught it.
        # However, if `get_base_domain` returns "" for some valid netlocs, then comparison "" != "example.com" is True.
        # The existing tests seem to rely on the initial `parsed_target_url.netloc` check for most problematic cases.
        
        return normalized_target_domain != normalized_base_domain
        
    except Exception:
        # Fallback consistent with original behavior on parsing errors for the target URL
        return False


def clean_tokens(tokens: list[str]) -> list[str]:
    """
    Clean a list of tokens by removing noise, stop words, and short tokens.

    How it works:
    1. Defines a set of noise words and stop words.
    2. Filters tokens based on length and exclusion criteria.
    3. Excludes tokens starting with certain symbols (e.g., "↑", "▲").

    Args:
        tokens (list[str]): The list of tokens to clean.

    Returns:
        list[str]: The cleaned list of tokens.
    """

    # Set of tokens to remove
    noise = {
        "ccp",
        "up",
        "↑",
        "▲",
        "⬆️",
        "a",
        "an",
        "at",
        "by",
        "in",
        "of",
        "on",
        "to",
        "the",
    }

    STOP_WORDS = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "has",
        "he",
        "in",
        "is",
        "it",
        "its",
        "of",
        "on",
        "that",
        "the",
        "to",
        "was",
        "were",
        "will",
        "with",
        # Pronouns
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
        "me",
        "him",
        "her",
        "us",
        "them",
        "my",
        "your",
        "his",
        "her",
        "its",
        "our",
        "their",
        "mine",
        "yours",
        "hers",
        "ours",
        "theirs",
        "myself",
        "yourself",
        "himself",
        "herself",
        "itself",
        "ourselves",
        "themselves",
        # Common verbs
        "am",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "having",
        "do",
        "does",
        "did",
        "doing",
        # Prepositions
        "about",
        "above",
        "across",
        "after",
        "against",
        "along",
        "among",
        "around",
        "at",
        "before",
        "behind",
        "below",
        "beneath",
        "beside",
        "between",
        "beyond",
        "by",
        "down",
        "during",
        "except",
        "for",
        "from",
        "in",
        "inside",
        "into",
        "near",
        "of",
        "off",
        "on",
        "out",
        "outside",
        "over",
        "past",
        "through",
        "to",
        "toward",
        "under",
        "underneath",
        "until",
        "up",
        "upon",
        "with",
        "within",
        # Conjunctions
        "and",
        "but",
        "or",
        "nor",
        "for",
        "yet",
        "so",
        "although",
        "because",
        "since",
        "unless",
        # Articles
        "a",
        "an",
        "the",
        # Other common words
        "this",
        "that",
        "these",
        "those",
        "what",
        "which",
        "who",
        "whom",
        "whose",
        "when",
        "where",
        "why",
        "how",
        "all",
        "any",
        "both",
        "each",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "can",
        "cannot",
        "can't",
        "could",
        "couldn't",
        "may",
        "might",
        "must",
        "mustn't",
        "shall",
        "should",
        "shouldn't",
        "will",
        "won't",
        "would",
        "wouldn't",
        "not",
        "n't",
        "no",
        "nor",
        "none",
    }

    # Single comprehension, more efficient than multiple passes
    return [
        token
        for token in tokens
        if len(token) > 2
        and token not in noise
        and token not in STOP_WORDS
        and not token.startswith("↑")
        and not token.startswith("▲")
        and not token.startswith("⬆")
    ]

def profile_and_time(func):
    """
    Decorator to profile a function's execution time and performance.

    How it works:
    1. Records the start time before executing the function.
    2. Profiles the function's execution using `cProfile`.
    3. Prints the elapsed time and profiling statistics.

    Args:
        func (Callable): The function to decorate.

    Returns:
        Callable: The decorated function with profiling and timing enabled.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Start timer
        start_time = time.perf_counter()

        # Setup profiler
        profiler = cProfile.Profile()
        profiler.enable()

        # Run function
        result = func(self, *args, **kwargs)

        # Stop profiler
        profiler.disable()

        # Calculate elapsed time
        elapsed_time = time.perf_counter() - start_time

        # Print timing
        print(f"[PROFILER] Scraping completed in {elapsed_time:.2f} seconds")

        # Print profiling stats
        stats = pstats.Stats(profiler)
        stats.sort_stats("cumulative")  # Sort by cumulative time
        stats.print_stats(20)  # Print top 20 time-consuming functions

        return result

    return wrapper


def generate_content_hash(content: str) -> str:
    """Generate a unique hash for content"""
    return xxhash.xxh64(content.encode()).hexdigest()
    # return hashlib.sha256(content.encode()).hexdigest()


def ensure_content_dirs(base_path: str) -> Dict[str, str]:
    """Create content directories if they don't exist"""
    dirs = {
        "html": "html_content",
        "markdown": "markdown",
        "link_dict": "link_dict",
        "screenshots": "screenshot",
        "cleaned_html": "cleaned_html",
    }

    content_paths = {}
    for key, dirname in dirs.items():
        path = os.path.join(base_path, dirname)
        os.makedirs(path, exist_ok=True)
        content_paths[key] = path

    return content_paths


def configure_windows_event_loop():
    """
    Configure the Windows event loop to use ProactorEventLoop.
    This resolves the NotImplementedError that occurs on Windows when using asyncio subprocesses.

    This function should only be called on Windows systems and before any async operations.
    On non-Windows systems, this function does nothing.

    Example:
        ```python
        from crawl4ai.async_configs import configure_windows_event_loop

        # Call this before any async operations if you're on Windows
        configure_windows_event_loop()
        ```
    """
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


def truncate(value, threshold):
    if len(value) > threshold:
        return value[:threshold] + '...'  # Add ellipsis to indicate truncation
    return value

def optimize_html(html_str, threshold=200):
    root = lxml.html.fromstring(html_str)
    
    for _element in root.iter():
        # Process attributes
        for attr in list(_element.attrib):
            _element.attrib[attr] = truncate(_element.attrib[attr], threshold)
        
        # Process text content
        if _element.text and len(_element.text) > threshold:
            _element.text = truncate(_element.text, threshold)
            
        # Process tail text
        if _element.tail and len(_element.tail) > threshold:
            _element.tail = truncate(_element.tail, threshold)
    
    return lxml.html.tostring(root, encoding='unicode', pretty_print=False)

class HeadPeekr:
    @staticmethod
    async def fetch_head_section(url, timeout=0.3):
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; CrawlBot/1.0)",
            "Accept": "text/html",
            "Connection": "close"  # Force close after response
        }
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, headers=headers, follow_redirects=True)
                
                # Handle redirects explicitly by using the final URL
                if response.url != url:
                    url = str(response.url)
                    response = await client.get(url, headers=headers)
                
                content = b""
                async for chunk in response.aiter_bytes():
                    content += chunk
                    if b"</head>" in content:
                        break  # Stop after detecting </head>
                return content.split(b"</head>")[0] + b"</head>"
        except (httpx.HTTPError, gaierror) :
            return None

    @staticmethod
    async def peek_html(url, timeout=0.3):
        head_section = await HeadPeekr.fetch_head_section(url, timeout=timeout)
        if head_section:
            return head_section.decode("utf-8", errors="ignore")
        return None

    @staticmethod
    def extract_meta_tags(head_content: str):
        meta_tags = {}
        
        # Find all meta tags
        meta_pattern = r'<meta[^>]+>'
        for meta_tag in re.finditer(meta_pattern, head_content):
            tag = meta_tag.group(0)
            
            # Extract name/property and content
            name_match = re.search(r'name=["\'](.*?)["\']', tag)
            property_match = re.search(r'property=["\'](.*?)["\']', tag)
            content_match = re.search(r'content=["\'](.*?)["\']', tag)
            
            if content_match and (name_match or property_match):
                key = name_match.group(1) if name_match else property_match.group(1)
                meta_tags[key] = content_match.group(1)
                
        return meta_tags

    def get_title(head_content: str):
        title_match = re.search(r'<title>(.*?)</title>', head_content, re.IGNORECASE | re.DOTALL)
        return title_match.group(1) if title_match else None

def preprocess_html_for_schema(html_content, tags_to_remove: list[str] = None):
    """
    Preprocess HTML to reduce size while preserving structure for schema generation.
    
    Args:
        html_content (str): Raw HTML content
        text_threshold (int): Maximum length for text nodes before truncation
        attr_value_threshold (int): Maximum length for attribute values before truncation
        max_size (int): Target maximum size for output HTML
        
    Returns:
        str: Preprocessed HTML content
    """
    try:
        # Parse HTML with error recovery
        parser = etree.HTMLParser(remove_comments=True, remove_blank_text=True)
        tree = lhtml.fromstring(html_content, parser=parser)
        
        # 1. Remove HEAD section (keep only BODY)
        head_elements = tree.xpath('//head')
        for head in head_elements:
            if head.getparent() is not None:
                head.getparent().remove(head)
        
        # 2. Define tags to remove completely
        if not tags_to_remove:
            tags_to_remove = [
                'script', 'style', 'noscript', 'iframe', 'canvas', 'svg',
                'video', 'audio', 'source', 'track', 'map', 'area',
                'form', 'input', 'textarea', 'select', 'option', 'button',
                'fieldset', 'legend', 'label', 'datalist', 'output'
            ]
        
        # Remove unwanted elements
        for tag in tags_to_remove:
            elements = tree.xpath(f'//{tag}')
            for element in elements:
                if element.getparent() is not None:
                    element.getparent().remove(element)
        
        # 3. Process remaining elements to clean attributes and truncate text
        for element in tree.iter():
            # Skip if we're at the root level
            if element.getparent() is None:
                continue
                
            # Clean non-essential attributes but preserve structural ones
            attribs_to_keep = {'id', 'class', 'name', 'href', 'src', 'type', 'value', 'data-'}

            # This is more aggressive than the previous version
            # attribs_to_keep = {'id', 'class', 'name', 'type', 'value'}

            # attributes_hates_truncate = ['id', 'class', "data-"]

            # This means, I don't care, if an attribute is too long, truncate it, go and find a better css selector to build a schema
            attributes_hates_truncate = ['href', 'src', 'data-']
            
            # Process each attribute
            for attrib in list(element.attrib.keys()):
                # Keep if it's essential or starts with data-
                if not (attrib in attribs_to_keep or attrib.startswith('data-')):
                    element.attrib.pop(attrib)
                # Truncate long attribute values except for selectors
                elif attrib not in attributes_hates_truncate and len(element.attrib[attrib]) > 200:
                    element.attrib[attrib] = element.attrib[attrib][:200] + '...'
            
            # Truncate text content if it's too long
            #if element.text and len(element.text.strip()) > text_threshold:
            #    element.text = element.text.strip()[:text_threshold] + '...'
                
            # Also truncate tail text if present
            # if element.tail and len(element.tail.strip()) > text_threshold:
            #    element.tail = element.tail.strip()[:text_threshold] + '...'
        
        # 4. Detect duplicates and drop them in a single pass
        seen: dict[tuple, None] = {}
        for el in list(tree.xpath('//*[@class]')):          # snapshot once, XPath is fast
            parent = el.getparent()
            if parent is None:
                continue
            cls = el.get('class')
            if not cls:
                continue
            # ── build signature ───────────────────────────────────────────
            h = xxhash.xxh64()                              # stream, no big join()
            for txt in el.itertext():
                h.update(txt)
            sig = (el.tag, cls, h.intdigest())             # tuple cheaper & hashable

            # ── first seen? keep – else drop ─────────────
            if sig in seen and parent is not None:
                parent.remove(el)
            else:
                seen[sig] = None

        # 5. Convert back to string
        result = etree.tostring(tree, encoding='unicode', method='html')
        
        # If still over the size limit, apply more aggressive truncation
        # if len(result) > max_size:
        #    return result[:max_size] + "..."
            
        return result
    
    except Exception as e:
        # Fallback for parsing errors
        # return html_content[:max_size] if len(html_content) > max_size else html_content
        return ''
    
@lru_cache(maxsize=1000)
def extract_extension(url: str) -> str:
    """Extracts file extension from a URL."""
    # Remove scheme (http://, https://) if present
    if "://" in url:
        url = url.split("://", 1)[-1]  # Get everything after '://'

    # Remove domain (everything up to the first '/')
    path_start = url.find("/")
    path = url[path_start:] if path_start != -1 else ""

    # Extract last filename in path
    filename = path.rsplit("/", 1)[-1] if "/" in path else ""

    # Extract and validate extension
    if "." not in filename:
        return ""

    return filename.rpartition(".")[-1].lower()


def get_true_available_memory_gb() -> float:
    """Get truly available memory including inactive pages (cross-platform)"""
    vm = psutil.virtual_memory()

    if platform.system() == 'Darwin':  # macOS
        # On macOS, we need to include inactive memory too
        try:
            # Use vm_stat to get accurate values
            result = subprocess.run(['vm_stat'], capture_output=True, text=True)
            lines = result.stdout.split('\n')

            page_size = 16384  # macOS page size
            pages = {}

            for line in lines:
                if 'Pages free:' in line:
                    pages['free'] = int(line.split()[-1].rstrip('.'))
                elif 'Pages inactive:' in line:
                    pages['inactive'] = int(line.split()[-1].rstrip('.'))
                elif 'Pages speculative:' in line:
                    pages['speculative'] = int(line.split()[-1].rstrip('.'))
                elif 'Pages purgeable:' in line:
                    pages['purgeable'] = int(line.split()[-1].rstrip('.'))

            # Calculate total available (free + inactive + speculative + purgeable)
            total_available_pages = (
                pages.get('free', 0) + 
                pages.get('inactive', 0) + 
                pages.get('speculative', 0) + 
                pages.get('purgeable', 0)
            )
            available_gb = (total_available_pages * page_size) / (1024**3)

            return available_gb
        except:
            # Fallback to psutil
            return vm.available / (1024**3)
    else:
        # For Windows and Linux, psutil.available is accurate
        return vm.available / (1024**3)


def get_true_memory_usage_percent() -> float:
    """
    Get memory usage percentage that accounts for platform differences.
    
    Returns:
        float: Memory usage percentage (0-100)
    """
    vm = psutil.virtual_memory()
    total_gb = vm.total / (1024**3)
    available_gb = get_true_available_memory_gb()
    
    # Calculate used percentage based on truly available memory
    used_percent = 100.0 * (total_gb - available_gb) / total_gb
    
    # Ensure it's within valid range
    return max(0.0, min(100.0, used_percent))


def get_memory_stats() -> Tuple[float, float, float]:
    """
    Get comprehensive memory statistics.
    
    Returns:
        Tuple[float, float, float]: (used_percent, available_gb, total_gb)
    """
    vm = psutil.virtual_memory()
    total_gb = vm.total / (1024**3)
    available_gb = get_true_available_memory_gb()
    used_percent = get_true_memory_usage_percent()
    
    return used_percent, available_gb, total_gb