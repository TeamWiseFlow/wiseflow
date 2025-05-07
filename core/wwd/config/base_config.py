# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。


# 基础配置
import os
from typing import List


PLATFORM = "wb"
KEYWORDS = "浦东 小升初 2025"

# 具体值参见media_platform.xxx.field下的枚举值，暂时只支持小红书
SORT_TYPE = "popularity_descending"

# 具体值参见media_platform.xxx.field下的枚举值，暂时只支持抖音
PUBLISH_TIME_TYPE = 0
CRAWLER_TYPE = "search"  # 爬取类型，search(关键词搜索) | detail(帖子详情)| creator(创作者主页数据) | homefeed(首页推荐)

# 数据保存类型选项配置,支持三种类型：csv、db、json
SAVE_DATA_OPTION = "json"  # csv or db or json

# 爬取开始页数 默认从第一页开始
START_PAGE = 1

# 爬取视频/帖子的数量控制
CRAWLER_MAX_NOTES_COUNT = 12

# 并发爬虫数量控制（请勿对平台发起大规模请求，并发控制仅限用于学习python的并发控制技术⚠️⚠️）
MAX_CONCURRENCY_NUM = 1

# 是否开启爬评论模式, 默认不开启爬评论
ENABLE_GET_COMMENTS = True

# 是否开启爬二级评论模式, 默认不开启爬二级评论
ENABLE_GET_SUB_COMMENTS = False

# 有的帖子评论数量太大了，这个变量用于一个帖子评论的最大数量，0表示不限制
PER_NOTE_MAX_COMMENTS_COUNT = 0

# 是否开启日志打印输出到文件中
COER_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK_DIR = os.path.join(COER_DIR, "work_dir")

# 已废弃⚠️⚠️⚠️指定小红书需要爬虫的笔记ID列表
# 已废弃⚠️⚠️⚠️ 指定笔记ID笔记列表会因为缺少xsec_token和xsec_source参数导致爬取失败
# XHS_SPECIFIED_ID_LIST = [
#     "66fad51c000000001b0224b8",
#     # ........................
# ]

# 指定小红书需要爬虫的笔记URL列表, 目前要携带xsec_token和xsec_source参数
# xsec_token和xsec_source是有时效的，需要在web端打开一个小红书笔记，复制地址栏的url参数
XHS_SPECIFIED_NOTE_URL_LIST = [
    # "https://www.xiaohongshu.com/explore/66fad51c000000001b0224b8?xsec_token=AB3rO-QopW5sgrJ41GwN01WCXh6yWPxjSoFI9D5JIMgKw=&xsec_source=pc_search"
    # ........................
]

# 已废弃⚠️⚠️⚠️指定小红书创作者ID列表
# 已废弃⚠️⚠️⚠️ 指定小红书创作者ID列表会因为缺少xsec_token和xsec_source参数导致爬取主页和主页的笔记列表失败
# 指定小红书创作者ID列表
# XHS_CREATOR_ID_LIST = [
#     "66215710000000000303097b",
#     # ........................
# ]

# 指定小红书创作者主页url列表, 需要携带xsec_token和xsec_source参数
XHS_CREATOR_URL_LIST = [
    "https://www.xiaohongshu.com/user/profile/57eac44f82ec390709962976?xsec_token=ABH53bxuX45gNaE5O_N6cHYyNll8nheUV-ZkdHbeChBkM=&xsec_source=pc_feed"
    # ........................
]

# 指定微博平台需要爬取的帖子列表
WEIBO_SPECIFIED_ID_LIST = [
    "4887640643735572",
    "5140489359855411",
    "5158260315785788",
    "5159733955133829",
    "5148960914675288"
]
# 指定weibo创作者ID列表
WEIBO_CREATOR_ID_LIST = [
    "7368601887 ",
    # ........................
]

# 指定贴吧需要爬取的帖子列表
TIEBA_SPECIFIED_ID_LIST: List[str] = []

# 指定贴吧名称列表，爬取该贴吧下的帖子
TIEBA_NAME_LIST: List[str] = [
    # "盗墓笔记"
]

TIEBA_CREATOR_URL_LIST = [
    "https://tieba.baidu.com/home/main/?id=tb.1.7f139e2e.6CyEwxu3VJruH_-QqpCi6g&fr=frs",
    # "https://tieba.baidu.com/home/main?id=tb.1.b9cd9508.4BEzoO0ZJbCkecLh-M4fKQ&fr=index"  # 主页帖子没有加载更多的case
    # ........................
]


# 指定bili创作者ID列表(这里是up主页面的ID)
BILI_CREATOR_ID_LIST = [
    "434377496",
    # ........................
]

# 指定B站平台需要爬取的视频bvid列表
BILI_SPECIFIED_ID_LIST = [
    "BV1d54y1g7db",
    "BV1Sz4y1U77N",
    "BV14Q4y1n7jz",
    # ........................
]

# 指定抖音需要爬取的ID列表
DY_SPECIFIED_ID_LIST = [
    "7280854932641664319",
    "7202432992642387233",
    # ........................
]

# 指定Dy创作者ID列表(sec_id)
DY_CREATOR_ID_LIST = [
    "MS4wLjABAAAATJPY7LAlaa5X-c8uNdWkvz0jUGgpw4eeXIwu_8BhvqE",
    # ........................
]


# 指定快手平台需要爬取的ID列表
KS_SPECIFIED_ID_LIST = ["3xf8enb8dbj6uig", "3x6zz972bchmvqe"]

# 指定快手创作者ID列表
KS_CREATOR_ID_LIST = [
    "3x6vn89cmqrimvm",
    # ........................
]


# 指定知乎创作者主页url列表
ZHIHU_CREATOR_URL_LIST = [
    "https://www.zhihu.com/people/yd1234567",
    # ........................
]

# 指定知乎需要爬取的帖子ID列表（仅支持下面这四种url链接的爬取）
ZHIHU_SPECIFIED_ID_LIST = [
    "https://www.zhihu.com/question/826896610/answer/4885821440",  # 回答
    "https://zhuanlan.zhihu.com/p/673461588",  # 文章
    "https://www.zhihu.com/zvideo/1539542068422144000",  # 视频
    # 爬取知乎指定问题下的答案列表，最大数量也由 CRAWLER_MAX_NOTES_COUNT 控制
    "https://www.zhihu.com/question/659910649",
]
