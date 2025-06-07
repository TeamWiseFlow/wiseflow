import argparse
from random import Random
from .crawler_util import *
from .time_util import *
# from bs4 import BeautifulSoup
# from ...utils import url_pattern, normalize_url


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def get_random_str(random_len: int = 12) -> str:
    """
    获取随机字符串
    :param random_len:
    :return:
    """
    random_str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    _random = Random()
    for i in range(random_len):
        random_str += chars[_random.randint(0, length)]
    return random_str


def random_delay_time(min_time: int = 1, max_time: int = 3) -> int:
    """
    获取随机延迟时间
    :param min_time:
    :param max_time:
    :return:
    """
    return random.randint(min_time, max_time)

"""
def process_html_string(html_string: str) -> tuple[str, dict[str, str]]:

    Processes a string containing HTML, extracts text and links from <a> and <img> tags,
    stores links in a dictionary, and replaces tags with their textual content.

    Args:
        html_string: The input string possibly containing HTML.

    Returns:
        A tuple containing:
            - The processed string with HTML tags handled.
            - A dictionary mapping generated keys (e.g., "[1]", "[2]") to extracted URLs.

    link_dict: dict[str, str] = {}
    soup = BeautifulSoup(html_string, 'html.parser')

    # Remove all <span class='url-icon'> tags
    for span_tag in soup.find_all('span', class_='url-icon'):
        span_tag.decompose()
    
    # Process <img> tags first
    # Iterate over a copy of the list of tags
    for img_tag in list(soup.find_all('img')):
        # Use 'alt' attribute as the text for <img> tags
        text = img_tag.get('alt', '') 
        
        link_url = img_tag.get('src')

        if not link_url:
            img_tag.replace_with(text)
            continue
        
        link_url = normalize_url(link_url)

        if not link_url.startswith(('http://', 'https://', 'data:image')):
            img_tag.replace_with(text)
            continue
        
        key = f"[{len(link_dict) + 1}]"
        link_dict[key] = link_url
            
        # Replace the <img> tag with its alt text
        img_tag.replace_with(text+key)

    # Process <a> tags
    # Iterate over a copy of the list of tags, as we are modifying the soup tree
    for a_tag in list(soup.find_all('a')):
        # Extract text content from the <a> tag and its children
        text = a_tag.get_text(separator=' ', strip=True)
        if text.startswith('#') and text.endswith('#'):
            a_tag.decompose()
            continue
        
        href = a_tag.get('href')
        if not href:
            a_tag.replace_with(text)
            continue
        
        href = normalize_url(href)
        
        # 处理mailto和tel链接, 将值添加到文本中
        if href.startswith(('mailto:', 'tel:')):
            a_tag.replace_with(text + href)
            continue
            
        if not href.startswith(('http://', 'https://')):
            a_tag.replace_with(text)
            continue

        key = f"[{len(link_dict) + 1}]"
        link_dict[key] = href
        
        # Replace the <a> tag with its extracted text content
        a_tag.replace_with(text+key)

    # Get the final text from the modified soup.
    # This step effectively handles "other tags" by stripping them and 
    # concatenating their text content.
    processed_text = soup.get_text(separator=' ', strip=True)

    # 处理文本中的"野 url"，使用更精确的正则表达式
    matches = re.findall(url_pattern, processed_text)
    for url in matches:
        url = normalize_url(url)
        _key = f"[{len(link_dict)+1}]"
        link_dict[_key] = url
        processed_text = processed_text.replace(url, _key, 1)

    return processed_text, link_dict
"""