from urllib.parse import urlparse
import os
import re
# import jieba
from loguru import logger


def isURL(string):
    if string.startswith("www."):
        string = f"https://{string}"
    result = urlparse(string)
    return result.scheme != '' and result.netloc != ''


def extract_urls(text):
    # Regular expression to match http, https, and www URLs
    url_pattern = re.compile(r'((?:https?://|www\.)[-A-Za-z0-9+&@#/%?=~_|!:,.;]*[-A-Za-z0-9+&@#/%=~_|])')
    urls = re.findall(url_pattern, text)
    # urls = {quote(url.rstrip('/'), safe='/:?=&') for url in urls}
    cleaned_urls = set()
    for url in urls:
        if url.startswith("www."):
            url = f"https://{url}"
        parsed_url = urlparse(url)
        if not parsed_url.netloc:
            continue
        # remove hash fragment
        if not parsed_url.scheme:
            # just try https
            cleaned_urls.add(f"https://{parsed_url.netloc}{parsed_url.path}{parsed_url.params}{parsed_url.query}")
        else:
            cleaned_urls.add(
                f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}{parsed_url.params}{parsed_url.query}")
    return cleaned_urls


def isChinesePunctuation(char):
    # Define the Unicode encoding range for Chinese punctuation marks
    chinese_punctuations = set(range(0x3000, 0x303F)) | set(range(0xFF00, 0xFFEF))
    # Check if the character is within the above range
    return ord(char) in chinese_punctuations


def is_chinese(string):
    """
    :param string: {str} The string to be detected
    :return: {bool} Returns True if most are Chinese, False otherwise
    """
    pattern = re.compile(r'[^\u4e00-\u9fa5]')
    non_chinese_count = len(pattern.findall(string))
    # It is easy to misjudge strictly according to the number of bytes less than half.
    # English words account for a large number of bytes, and there are punctuation marks, etc
    return (non_chinese_count/len(string)) < 0.68


def extract_and_convert_dates(input_string):
    # 定义匹配不同日期格式的正则表达式
    if not isinstance(input_string, str):
        return None

    patterns = [
        r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
        r'(\d{4})/(\d{2})/(\d{2})',  # YYYY/MM/DD
        r'(\d{4})\.(\d{2})\.(\d{2})',  # YYYY.MM.DD
        r'(\d{4})\\(\d{2})\\(\d{2})',  # YYYY\MM\DD
        r'(\d{4})(\d{2})(\d{2})'  # YYYYMMDD
    ]

    matches = []
    for pattern in patterns:
        matches = re.findall(pattern, input_string)
        if matches:
            break
    if matches:
        return '-'.join(matches[0])
    return None


def get_logger(logger_name: str, logger_file_path: str):
    level = 'DEBUG' if os.environ.get("VERBOSE", "").lower() in ["true", "1"] else 'INFO'
    logger_file = os.path.join(logger_file_path, f"{logger_name}.log")
    if not os.path.exists(logger_file_path):
        os.makedirs(logger_file_path)
    logger.add(logger_file, level=level, backtrace=True, diagnose=True, rotation="50 MB")
    return logger

"""
def compare_phrase_with_list(target_phrase, phrase_list, threshold):

    Compare the similarity of a target phrase to each phrase in the phrase list.

    : Param target_phrase: target phrase (str)
    : Param phrase_list: list of str
    : param threshold: similarity threshold (float)
    : Return: list of phrases that satisfy the similarity condition (list of str)

    if not target_phrase:
        return []  # The target phrase is empty, and the empty list is returned directly.

    # Preprocessing: Segmentation of the target phrase and each phrase in the phrase list
    target_tokens = set(jieba.lcut(target_phrase))
    tokenized_phrases = {phrase: set(jieba.lcut(phrase)) for phrase in phrase_list}

    similar_phrases = [phrase for phrase, tokens in tokenized_phrases.items()
                       if len(target_tokens & tokens) / min(len(target_tokens), len(tokens)) > threshold]

    return similar_phrases
"""