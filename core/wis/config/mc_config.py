# 基础配置 for media crawler

# 具体值参见media_platform.xxx.field下的枚举值，暂时只支持小红书
SORT_TYPE = "popularity_descending"

# 具体值参见media_platform.xxx.field下的枚举值，暂时只支持抖音
PUBLISH_TIME_TYPE = 0

# 爬取开始页数 默认从第一页开始
START_PAGE = 1

# 爬取视频/帖子的数量控制
CRAWLER_MAX_NOTES_COUNT = 50

# 并发爬虫数量控制（请勿对平台发起大规模请求⚠️⚠️）
MAX_CONCURRENCY_NUM = 1

# 搜索上溯时间，单位小时，默认6个月
SEARCH_UP_TIME = 24 * 30 * 6

# 创作者搜索上溯时间，单位小时，默认1周
CREATOR_SEARCH_UP_TIME = 24 * 7

# 是否开启爬评论模式, 默认不开启爬评论
ENABLE_GET_COMMENTS = True

# 是否开启爬二级评论模式, 默认不开启爬二级评论
ENABLE_GET_SUB_COMMENTS = True

# 有的帖子评论数量太大了，这个变量用于一个帖子评论的最大数量，0表示不限制
# use pro Edition with the IP proxy, so you can safely add this...
PER_NOTE_MAX_COMMENTS_COUNT = 30

# 微博搜索模式，DEFAULT: 综合（默认），REAL_TIME: 实时，POPULAR: 热门，VIDEO: 视频
WEIBO_SEARCH_TYPE = "DEFAULT"

KUAISHOU_PLATFORM_NAME = 'ks'
WEIBO_PLATFORM_NAME = 'wb'

PLATFORM_LOGIN_URLS = {
    KUAISHOU_PLATFORM_NAME: 'https://www.kuaishou.com/',
    WEIBO_PLATFORM_NAME: 'https://m.weibo.cn/',
}

KUAISHOU_API = 'https://www.kuaishou.com/graphql'
WEIBO_API_URL = 'https://m.weibo.cn'