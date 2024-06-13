"""mostly copy from https://github.com/netease-youdao/QAnything
awsome work!
"""
# import traceback
from urllib.parse import urlparse
import time
import os
import re
import jieba


def isURL(string):
    result = urlparse(string)
    return result.scheme != '' and result.netloc != ''


def extract_urls(text):
    url_pattern = re.compile(r'https?://[-A-Za-z0-9+&@#/%?=~_|!:.;]+[-A-Za-z0-9+&@#/%=~_|]')
    urls = re.findall(url_pattern, text)

    # 过滤掉那些只匹配到 'www.' 而没有后续内容的情况，并尝试为每个URL添加默认的http协议前缀以便解析
    cleaned_urls = [url for url in urls if isURL(url)]
    return cleaned_urls


def isChinesePunctuation(char):
    # 定义中文标点符号的Unicode编码范围
    chinese_punctuations = set(range(0x3000, 0x303F)) | set(range(0xFF00, 0xFFEF))
    # 检查字符是否在上述范围内
    return ord(char) in chinese_punctuations


def get_time(func):
    def inner(*arg, **kwargs):
        s_time = time.time()
        res = func(*arg, **kwargs)
        e_time = time.time()
        print('函数 {} 执行耗时: {} 秒'.format(func.__name__, e_time - s_time))
        return res
    return inner


'''
def safe_get(req: Request, attr: str, default=None):
    try:
        if attr in req.form:
            return req.form.getlist(attr)[0]
        if attr in req.args:
            return req.args[attr]
        if attr in req.json:
            return req.json[attr]
        # if value := req.form.get(attr):
        #     return value
        # if value := req.args.get(attr):
        #     return value
        # """req.json执行时不校验content-type，body字段可能不能被正确解析为json"""
        # if value := req.json.get(attr):
        #     return value
    except BadRequest:
        logging.warning(f"missing {attr} in request")
    except Exception as e:
        logging.warning(f"get {attr} from request failed:")
        logging.warning(traceback.format_exc())
    return default
'''


def truncate_filename(filename, max_length=200):
    # 获取文件名后缀
    file_ext = os.path.splitext(filename)[1]

    # 获取不带后缀的文件名
    file_name_no_ext = os.path.splitext(filename)[0]

    # 计算文件名长度，注意中文字符
    filename_length = len(filename.encode('utf-8'))

    # 如果文件名长度超过最大长度限制
    if filename_length > max_length:
        # 生成一个时间戳标记
        timestamp = str(int(time.time()))
        
        # 计算剩余的文件名长度
        remaining_length = max_length - len(file_ext) - len(timestamp) - 1  # -1 是为了下划线
        
        # 截取文件名并添加标记
        file_name_no_ext = file_name_no_ext[:remaining_length]
        new_filename = file_name_no_ext + '_' + timestamp + file_ext
    else:
        new_filename = filename

    return new_filename


def read_files_with_extensions():
    # 获取当前脚本文件的路径
    current_file = os.path.abspath(__file__)

    # 获取当前脚本文件所在的目录
    current_dir = os.path.dirname(current_file)

    # 获取项目根目录
    project_dir = os.path.dirname(current_dir)

    directory = project_dir + '/data'
    print(f'now reading {directory}')
    extensions = ['.md', '.txt', '.pdf', '.jpg', '.docx', '.xlsx', '.eml', '.csv'] 
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(tuple(extensions)):
                file_path = os.path.join(root, file)
                yield file_path


def validate_user_id(user_id):
    # 定义正则表达式模式
    pattern = r'^[A-Za-z][A-Za-z0-9_]*$'
    # 检查是否匹配
    if isinstance(user_id, str) and re.match(pattern, user_id):
        return True
    else:
        return False


def is_chinese(string):
    """
    使用火山引擎其实可以支持更加广泛的语言检测，未来可以考虑 https://www.volcengine.com/docs/4640/65066
    判断字符串中大部分是否是中文
    :param string: {str} 需要检测的字符串
    :return: {bool} 如果大部分是中文返回True，否则返回False
    """
    pattern = re.compile(r'[^\u4e00-\u9fa5]')
    non_chinese_count = len(pattern.findall(string))
    # 严格按照字节数量小于一半判断容易误判，英文单词占字节较大,且还有标点符号等
    return (non_chinese_count/len(string)) < 0.68


def extract_and_convert_dates(input_string):
    # 定义匹配不同日期格式的正则表达式
    patterns = [
        r'(\d{4})-(\d{2})-(\d{2})',  # 匹配YYYY-MM-DD格式
        r'(\d{4})/(\d{2})/(\d{2})',  # 匹配YYYY/MM/DD格式
        r'(\d{4})\.(\d{2})\.(\d{2})',  # 匹配YYYY.MM.DD格式
        r'(\d{4})\\(\d{2})\\(\d{2})',  # 匹配YYYY\MM\DD格式
        r'(\d{4})(\d{2})(\d{2})'  # 匹配YYYYMMDD格式
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
    比较一个目标短语与短语列表中每个短语的相似度。

    :param target_phrase: 目标短语 (str)
    :param phrase_list: 短语列表 (list of str)
    :param threshold: 相似度阈值 (float)
    :return: 满足相似度条件的短语列表 (list of str)
    """
    # 检查目标短语是否为空
    if not target_phrase:
        return []  # 目标短语为空，直接返回空列表

    # 预处理：对目标短语和短语列表中的每个短语进行分词
    target_tokens = set(jieba.lcut(target_phrase))
    tokenized_phrases = {phrase: set(jieba.lcut(phrase)) for phrase in phrase_list}

    # 比较并筛选
    similar_phrases = [phrase for phrase, tokens in tokenized_phrases.items()
                       if len(target_tokens & tokens) / min(len(target_tokens), len(tokens)) > threshold]

    return similar_phrases

"""
# from InternLM/huixiangdou 
# another awsome work
    def process_strings(self, str1, replacement, str2):
        '''Find the longest common suffix of str1 and prefix of str2.'''
        shared_substring = ''
        for i in range(1, min(len(str1), len(str2)) + 1):
            if str1[-i:] == str2[:i]:
                shared_substring = str1[-i:]

        # If there is a common substring, replace one of them with the replacement string and concatenate  # noqa E501
        if shared_substring:
            return str1[:-len(shared_substring)] + replacement + str2

        # Otherwise, just return str1 + str2
        return str1 + str2

    def clean_md(self, text: str):
        '''Remove parts of the markdown document that do not contain the key
        question words, such as code blocks, URL links, etc.'''
        # remove ref
        pattern_ref = r'\[(.*?)\]\(.*?\)'
        new_text = re.sub(pattern_ref, r'\1', text)

        # remove code block
        pattern_code = r'```.*?```'
        new_text = re.sub(pattern_code, '', new_text, flags=re.DOTALL)

        # remove underline
        new_text = re.sub('_{5,}', '', new_text)

        # remove table
        # new_text = re.sub('\|.*?\|\n\| *\:.*\: *\|.*\n(\|.*\|.*\n)*', '', new_text, flags=re.DOTALL)   # noqa E501

        # use lower
        new_text = new_text.lower()
        return new_text
"""