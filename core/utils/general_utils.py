from urllib.parse import urlparse, urljoin, urlunparse, parse_qs, urlencode
import os
import regex as re
# import jieba
from loguru import logger


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


def normalize_url(url: str, base_url: str = None) -> str:
    url = url.strip()
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
        parsed = urlparse(url)
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
        print(f"Error cleaning URL: {e}")
        _ss = _url.split('//')
        if len(_ss) == 2:
            return '//'.join(_ss)
        else:
            return _ss[0] + '//' + '/'.join(_ss[1:])


def isURL(string):
    if string.startswith("www."):
        string = f"https://{string}"
    result = urlparse(string)
    return result.scheme != '' and result.netloc != ''


def extract_urls(text):
    # Regular expression to match http, https, and www URLs
    urls = re.findall(url_pattern, text)
    # urls = {quote(url.rstrip('/'), safe='/:?=&') for url in urls}
    cleaned_urls = set()
    for url in urls:
        if url.startswith("www."):
            url = f"https://{url}"

        try:
            parsed = urlparse(url)
            if not parsed.netloc or not parsed.scheme:
                continue

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
            cleaned_urls.add(cleaned_url)
        except Exception:
            continue

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
    if not isinstance(input_string, str) or len(input_string) < 8:
        return ''

    patterns = [
        r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
        r'(\d{4})/(\d{2})/(\d{2})',  # YYYY/MM/DD
        r'(\d{4})\.(\d{2})\.(\d{2})',  # YYYY.MM.DD
        r'(\d{4})\\(\d{2})\\(\d{2})',  # YYYY\MM\DD
        r'(\d{4})(\d{2})(\d{2})',  # YYYYMMDD
        r'(\d{4})年(\d{2})月(\d{2})日'  # YYYY年MM月DD日
    ]

    matches = []
    for pattern in patterns:
        matches = re.findall(pattern, input_string)
        if matches:
            break
    if matches:
        return '-'.join(matches[0])
    return ''


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
