from urllib.parse import urlparse
import os
import re
import jieba


def isURL(string):
    result = urlparse(string)
    return result.scheme != '' and result.netloc != ''


def extract_urls(text):
    url_pattern = re.compile(r'https?://[-A-Za-z0-9+&@#/%?=~_|!:.;]+[-A-Za-z0-9+&@#/%=~_|]')
    urls = re.findall(url_pattern, text)

    # Filter out those cases that only match to'www. 'without subsequent content,
    # and try to add the default http protocol prefix to each URL for easy parsing
    cleaned_urls = [url for url in urls if isURL(url)]
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
        return ''.join(matches[0])
    return None


def get_logger_level() -> str:
    level_map = {
        'silly': 'CRITICAL',
        'verbose': 'DEBUG',
        'info': 'INFO',
        'warn': 'WARNING',
        'error': 'ERROR',
    }
    level: str = os.environ.get('WS_LOG', 'info').lower()
    if level not in level_map:
        raise ValueError(
            'WiseFlow LOG should support the values of `silly`, '
            '`verbose`, `info`, `warn`, `error`'
        )
    return level_map.get(level, 'info')


def compare_phrase_with_list(target_phrase, phrase_list, threshold):
    """
    Compare the similarity of a target phrase to each phrase in the phrase list.

    : Param target_phrase: target phrase (str)
    : Param phrase_list: list of str
    : param threshold: similarity threshold (float)
    : Return: list of phrases that satisfy the similarity condition (list of str)
    """
    if not target_phrase:
        return []  # The target phrase is empty, and the empty list is returned directly.

    # Preprocessing: Segmentation of the target phrase and each phrase in the phrase list
    target_tokens = set(jieba.lcut(target_phrase))
    tokenized_phrases = {phrase: set(jieba.lcut(phrase)) for phrase in phrase_list}

    similar_phrases = [phrase for phrase, tokens in tokenized_phrases.items()
                       if len(target_tokens & tokens) / min(len(target_tokens), len(tokens)) > threshold]

    return similar_phrases
