from bs4 import BeautifulSoup, Comment, element, Tag, NavigableString
import json
import lxml
import regex as re
import platform
from urllib.parse import urljoin
import xxhash
import asyncio
from lxml import etree, html as lhtml
from urllib.parse import urlparse, urlunparse
from functools import lru_cache
from .config import config
from . import __version__
import psutil
import subprocess
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
    '.yaml', '.yml', '.asp']

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

def extract_urls(text):
    # Regular expression to match http, https, and www URLs
    urls = re.findall(url_pattern, text)
    # urls = {quote(url.rstrip('/'), safe='/:?=&') for url in urls}
    cleaned_urls = set()
    for url in urls:
        if url.startswith(("www.", "WWW.")):
            url = f"https://www.{url[4:]}"

        try:
            parsed = urlparse(url)
            if not parsed.netloc or not parsed.scheme:
                continue
            cleaned_urls.add(url)
        except Exception:
            continue

    return cleaned_urls

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

def can_process_url(url: str) -> bool:
        """
        Validate the URL format and apply filtering.
        For the starting URL (depth 0), filtering is bypassed.
        """
        for forbidden_domain in config['FORBIDDEN_DOMAINS']:
            if forbidden_domain in url:
                return False

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


def get_content_of_website(
    html, tags_to_remove=None):
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
    # from .config import config
    word_count_threshold = config['MIN_WORD_THRESHOLD']

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
            body: Tag, word_count_threshold: int = config['MIN_WORD_THRESHOLD']
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


def extract_date_from_url(url: str) -> str:
    """
    Extract date from URL path or query parameters.
    
    Supports common URL date patterns:
    - /2024/01/15/article-title
    - /2024-01-15/article
    - /20240115/article
    - /news/2024/1/15/
    - ?date=2024-01-15
    
    Args:
        url: The URL to extract date from
        
    Returns:
        str: Date string in YYYY-MM-DD format, or empty string if not found
    """
    if not url:
        return ""
    
    try:
        parsed = urlparse(url)
        path = parsed.path
        query = parsed.query
        
        # Pattern 1: YYYY/MM/DD or YYYY-MM-DD in path
        pattern1 = re.search(r'/(\d{4})[-/](\d{1,2})[-/](\d{1,2})(?:/|$)', path)
        if pattern1:
            year, month, day = pattern1.groups()
            year, month, day = int(year), int(month), int(day)
            if 1990 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                return f"{year:04d}-{month:02d}-{day:02d}"
        
        # Pattern 2: YYYYMMDD in path (8 consecutive digits)
        pattern2 = re.search(r'/(\d{4})(\d{2})(\d{2})(?:/|[^0-9]|$)', path)
        if pattern2:
            year, month, day = pattern2.groups()
            year, month, day = int(year), int(month), int(day)
            if 1990 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                return f"{year:04d}-{month:02d}-{day:02d}"
        
        # Pattern 3: Check query parameters for date
        if query:
            params = parse_qs(query)
            for key in ['date', 'publish_date', 'pubdate', 'd', 'dt']:
                if key in params and params[key]:
                    date_val = params[key][0]
                    # Try to parse YYYY-MM-DD or YYYYMMDD
                    date_match = re.match(r'^(\d{4})[-/]?(\d{2})[-/]?(\d{2})$', date_val)
                    if date_match:
                        year, month, day = date_match.groups()
                        year, month, day = int(year), int(month), int(day)
                        if 1990 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                            return f"{year:04d}-{month:02d}-{day:02d}"
        
        # Pattern 4: YYYY/M/D (single digit month/day)
        pattern4 = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})(?:/|$)', path)
        if pattern4:
            year, month, day = pattern4.groups()
            year, month, day = int(year), int(month), int(day)
            if 1990 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                return f"{year:04d}-{month:02d}-{day:02d}"
        
    except Exception:
        pass
    
    return ""