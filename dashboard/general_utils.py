from urllib.parse import urlparse
import os
import re


def isURL(string):
    result = urlparse(string)
    return result.scheme != '' and result.netloc != ''


def isChinesePunctuation(char):
    # 定义中文标点符号的Unicode编码范围
    chinese_punctuations = set(range(0x3000, 0x303F)) | set(range(0xFF00, 0xFFEF))
    # 检查字符是否在上述范围内
    return ord(char) in chinese_punctuations


def is_chinese(string):
    """
    使用火山引擎其实可以支持更加广泛的语言检测，未来可以考虑 https://www.volcengine.com/docs/4640/65066
    判断字符串中大部分是否是中文
    :param string: {str} 需要检测的字符串
    :return: {bool} 如果大部分是中文返回True，否则返回False
    """
    pattern = re.compile(r'[^\u4e00-\u9fa5]')
    non_chinese_count = len(pattern.findall(string))
    # It is easy to misjudge strictly according to the number of bytes less than half. English words account for a large number of bytes, and there are punctuation marks, etc
    return (non_chinese_count/len(string)) < 0.68


def extract_and_convert_dates(input_string):
    # Define regular expressions that match different date formats
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
