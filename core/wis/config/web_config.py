# Chunk token threshold
CHUNK_TOKEN_THRESHOLD = 2**11  # 2048 tokens
OVERLAP_RATE = 0.1
WORD_TOKEN_RATE = 1.3

# Threshold for the minimum number of word in a HTML tag to be considered
MIN_WORD_THRESHOLD = 1
IMAGE_DESCRIPTION_MIN_WORD_THRESHOLD = 1
EXCLUDE_EXTERNAL_LINKS = True
IMPORTANT_ATTRS = ["src", "href", "alt", "title", "width", "height", "data-src"]
ONLY_TEXT_ELIGIBLE_TAGS = [
    "b",
    "i",
    "u",
    "span",
    "del",
    "ins",
    "sub",
    "sup",
    "strong",
    "em",
    "code",
    "kbd",
    "var",
    "s",
    "q",
    "abbr",
    "cite",
    "dfn",
    "time",
    "small",
    "mark",
]

SOCIAL_MEDIA_DOMAINS = [
    "facebook.com",
    "twitter.com",
    "x.com",
    "linkedin.com",
    "instagram.com",
    "pinterest.com",
    "tiktok.com",
    "snapchat.com",
    "reddit.com",
    "weibo.com",
    "m.weibo.cn",
    "m.weibo.com",
    "service.weibo.com",
    "zhihu.com",
    "zhuanlan.zhihu.com",
    "douyin.com",
    "bilibili.com",
    "xiaohongshu.com",
    "kuaishou.com",
]

MAX_METRICS_HISTORY = 1000
URL_LOG_SHORTEN_LENGTH = 30
SHOW_DEPRECATION_WARNINGS = True
SCREENSHOT_HEIGHT_TRESHOLD = 10000
PAGE_TIMEOUT = 60000
DOWNLOAD_PAGE_TIMEOUT = 60000
