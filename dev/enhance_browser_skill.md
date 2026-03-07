我们需要强化下 browser-guide SKILL，对于部分基于社交平台的搜索或者创作者主页查询，直接使用规则构造 url ，而不是多步点击操作。我总结的规律如下：

# 自媒体平台的搜索

## bilibili（哔哩哔哩\b站）：

https://search.bilibili.com/{channel}?keyword={keyword}

keyword 多个的话，之间用 + 连接

channel 可选：

- 综合：all
- 视频：video
- 番剧：bangumi
- 影视：pgc
- 直播：live
- 专栏：article
- 用户：upuser

每个 channel 都可以指定搜索规则（默认不指定任何），具体规则如下：

### all

支持的搜索规则包括：
- 最多播放：&order=click
- 最新发布：&order=pubdate
- 最多弹幕：&order=dm
- 最多收藏：&order=stow

示例：

- 默认搜索：https://search.bilibili.com/all?keyword=%E8%8D%AF%E5%B1%8B%E5%B0%91%E5%A5%B3%E7%9A%84%E5%91%A2%E5%96%83
- 最多播放：https://search.bilibili.com/all?keyword=%E8%8D%AF%E5%B1%8B%E5%B0%91%E5%A5%B3%E7%9A%84%E5%91%A2%E5%96%83&order=click

### video

支持的搜索规则包括：
- 最多播放：&order=click
- 最新发布：&order=pubdate
- 最多弹幕：&order=dm
- 最多收藏：&order=stow

示例：

- 默认搜索：https://search.bilibili.com/video?keyword=%E8%8D%AF%E5%B1%8B%E5%B0%91%E5%A5%B3%E7%9A%84%E5%91%A2%E5%96%83
- 最新发布：https://search.bilibili.com/video?keyword=%E8%8D%AF%E5%B1%8B%E5%B0%91%E5%A5%B3%E7%9A%84%E5%91%A2%E5%96%83&order=pubdate

### bangumi

这个 channel 不支持搜索规则，只有默认搜索

### pgc

这个 channel 不支持搜索规则，只有默认搜索

### live

支持的搜索规则包括（默认是搜全部）：

- 搜主播：&search_type=live_user
- 搜直播间：&search_type=live_room
- 按最新开播顺序搜直播间:search_type=live_room&order=live_time

示例：

- 默认搜索(搜全部）：https://search.bilibili.com/live?keyword=%E8%8D%AF%E5%B1%8B%E5%B0%91%E5%A5%B3%E7%9A%84%E5%91%A2%E5%96%83
- 按最新开播顺序搜直播间：https://search.bilibili.com/live?keyword=%E8%8D%AF%E5%B1%8B%E5%B0%91%E5%A5%B3%E7%9A%84%E5%91%A2%E5%96%83&search_type=live_room&order=live_time

### article

支持的搜索规则包括：
- 最新发布：&order=pubdate
- 最多点击：&order=click
- 最受欢迎：&order=attention
- 最多评论：&order=scores

示例：

- 默认搜索：https://search.bilibili.com/article?keyword=%E8%8D%AF%E5%B1%8B%E5%B0%91%E5%A5%B3%E7%9A%84%E5%91%A2%E5%96%83
- 最多评论：https://search.bilibili.com/article?keyword=%E8%8D%AF%E5%B1%8B%E5%B0%91%E5%A5%B3%E7%9A%84%E5%91%A2%E5%96%83&order=scores

### upuser

支持的搜索规则包括：
- 粉丝数由高到低：&order=fans
- 粉丝数由低到高：&order=fans&order_sort=1
- 会员等级由高到低：&order=level
- 会员等级由低到高：&order=level&order_sort=1

示例：

- 默认搜索：https://search.bilibili.com/upuser?keyword=%E8%8D%AF%E5%B1%8B%E5%B0%91%E5%A5%B3%E7%9A%84%E5%91%A2%E5%96%83
- 粉丝数由高到低：https://search.bilibili.com/upuser?keyword=%E8%8D%AF%E5%B1%8B%E5%B0%91%E5%A5%B3%E7%9A%84%E5%91%A2%E5%96%83&order=fans

## 








你也可以看看，给出建议，我们以何种形式把这些规则增加到browser-guide SKILL中：

直接写到 skill 的 markdown 中，还是做个脚本供他调用，异或做成其他的 skill，然后根据需要调用？
