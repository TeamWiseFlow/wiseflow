# 自媒体平台的搜索

## bilibili（哔哩哔哩，简称：b站）：

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

## 抖音(douyin，简称dy)：

- 综合搜索：https://www.douyin.com/search/{keyword}?type=general
- 视频搜索：https://www.douyin.com/search/{keyword}?type=video
- 用户搜索：https://www.douyin.com/search/{keyword}?type=user
- 直播搜索：https://www.douyin.com/search/{keyword}?type=live

多 keyword，中间用 %20 连接，如： https://www.douyin.com/search/wiseflow%20%E8%B4%9F%E9%9D%A2

type 缺省为综合搜索

如果涉及到搜索结果排序或者筛选，必须通过网页交互进行

## 微博（weibo，简称 wb）：

- 综合搜索：https://s.weibo.com/weibo/{keyword}
- 实时搜索（最新发布）：https://s.weibo.com/realtime?q={keyword}
- 搜索用户：https://s.weibo.com/user?q={keyword}
- 搜索话题：https://s.weibo.com/topic?q={keyword}

## 小红书（xiaohongshu，简称 xhs，又称 红薯）：

https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_explore_feed

小红书平台具体的搜索频道、筛选条件、排序要求等都必须通过网页交互实现

## 知乎（zhihu):

- 综合：https://www.zhihu.com/search?type=content&q={keyword}
- 用户（找人）：https://www.zhihu.com/search?q={keyword}&type=people
- 论文：https://www.zhihu.com/search?q={keyword}&type=scholar
- 专栏：https://www.zhihu.com/search?q={keyword}&type=column
- 电子书：https://www.zhihu.com/search?q={keyword}&type=publication
- 圈子：https://www.zhihu.com/search?q={keyword}&type=ring
- 话题：https://www.zhihu.com/search?q={keyword}&type=topic
- 视频：https://www.zhihu.com/search?q={keyword}&type=zvideo

多 keyword，中间用 %20 连接，如： https://www.zhihu.com/search?type=zvideo&q=wiseflow%20%E4%BB%98%E8%B4%B9

其中如下支持通过 url 构造filter 条件或者排序：

### 综和

基础：https://www.zhihu.com/search?type=content&q={keyword}

- 条件：
  - 只看回答，url 后加：&type=content&vertical=answer
  - 只看文章，url 后加：&type=content&vertical=article
  - 只看视频，url 后加：&type=content&vertical=zvideo

- 排序：
  - 最多赞同，url 后加：&sort=upvoted_count
  - 最新发布，url 后加：&sort=created_time

- 时间限制：
  - 一天内，url 后加：&time_interval=a_day
  - 一周内，url 后加：&time_interval=a_week
  - 一月内，url 后加：&time_interval=a_month
  - 三月内，url 后加：&time_interval=three_months
  - 半年内，url 后加：&time_interval=half_a_year
  - 一年内，url 后加：&time_interval=a_year

以上都可以灵活组合：比如：https://www.zhihu.com/search?q=wiseflow%20%E4%BB%98%E8%B4%B9&sort=created_time&time_interval=a_month&type=content&vertical=article

## twitter（X，推特）

- TOP：https://x.com/search?q={keyword}
- Latest：https://x.com/search?q={keyword}&f=live
- People（找人）：https://x.com/search?q={keyword}&f=user
- Media：https://x.com/search?q={keyword}&f=media
- Lists：https://x.com/search?q={keyword}&f=list

多 keyword，中间用 %20 连接，如：https://x.com/search?q=wiseflow%20%E8%BD%AF%E4%BB%B6&src=typed_query&f=list

均可叠加 Near You 选项，后面加 &lf=on， 如：https://x.com/search?q=wiseflow&f=live&lf=on

## facebook（FB，脸书）

- ALL：https://www.facebook.com/search/top/?q={keyword}
- People（找人）：https://www.facebook.com/search/people/?q={keyword}
- pages: https://www.facebook.com/search/pages?q={keyword}
- groups: https://www.facebook.com/search/groups?q={keyword}
- events: https://www.facebook.com/search/events?q={keyword}

多 keyword，中间用 %20 连接，如：https://www.facebook.com/search/top/?q=jinchen%20%E4%BD%8F%E5%8F%8B

搜索条件等都需要通过网页交互实现

## github

- Repositories：https://github.com/search?q={keyword}&type=repositories
- Users：https://github.com/search?q={keyword}&type=users
- Issues：https://github.com/search?q={keyword}&type=issues
- Pull Requests：https://github.com/search?q={keyword}&type=pullrequests
- Code：https://github.com/search?q={keyword}&type=code
- discussions https://github.com/search?q={keyword}&type=discussions
- Wikis: https://github.com/search?q={keyword}&type=wikis
- topics: https://github.com/search?q={keyword}&type=topics

多 keyword，中间用 + 连接，如：https://github.com/search?q=wiseflow+addon&type=topics

### Repositories 支持的搜素条件：

- most stars: &s=stars&o=desc
- fewest stars: &s=stars&o=asc
- most forks: &s=forks&o=desc
- fewest forks: &s=forks&o=asc
- recently updated: &s=updated&o=desc
- latest recently updated: &s=updated&o=asc

### users 支持的搜素条件：

- most followers: &s=followers&o=desc
- fewest followers: &s=followers&o=asc
- most recently joined: &s=joined&o=desc
- least recently joined: &s=joined&o=asc
- most repositories: &s=repositories&o=desc
- fewest repositories: &s=repositories&o=asc

repositories 和 user 搜索都支持添加 语言作为过滤，&l=HTML

如：https://github.com/search?q=wiseflow+language%3AHTML&type=users&s=repositories&o=desc&l=HTML

支持的语言过滤：HTML, CSS, JavaScript, Python, Ruby, Java, C++, PHP, Swift, Go, Kotlin, TypeScript, Rust, Scala, Haskell, Lua, Shell, Dockerfile, JSON, YAML, Markdown, SVG, 
