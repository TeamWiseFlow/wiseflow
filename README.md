# 首席情报官

**欢迎使用首席情报官**

首席情报官（wiseflow）是一个完备的领域（行业）信息情报采集与分析系统，该系统面向普通用户开源免费，同时我们提供更加专业的行业情报信息订阅服务，欢迎联系我们获取更多信息。

Email：[zm.zhao@foxmail.com](zm.zhao@foxmail.com) 

**首席情报官目前版本主要功能点：**

- 每日关注简报列表
- 入库文章列表、详情，支持一键翻译（简体中文）
- 关注点一键搜索（使用搜狗引擎）
- 关注点一键报告生成（直接生成word文档）
- 行业情报信息订阅（邮件zm.zhao@foxmail.com联系开通）
- 数据库管理
- 支持针对特定站点的自定义爬虫集成，并提供本地定时扫描任务……

**产品介绍视频：**

![wiseflow](/asset/demo.mp4)

## getting started

我们为普通用户提供了本地运行的client，我们强烈建议使用我们提供的docker镜像，但您也可以使用源码运行。

```commandline
git clone git@openi.pcl.ac.cn:wiseflow/wiseflow.git
cd wiseflow/client
```

之后参考[client](/client/README.md)

## SDK & API （coming soon）

我们将很快提供local SDK和subscribe service API服务。

通过local sdk，用户可以无需客户端进行订阅数据同步，并在本地通过python api进行灵活调用，这样wiseflow就可以成为任意RAG系统的数据来源之一。

而subscribe service将使用户可以将订阅数据查询和推送服务嫁接到自己的微信公众号、微信客服、网站以及各类GPTs bot平台上（我们也会发布各平台的插件）。

**wiseflow架构图**

![wiseflow架构图](asset/wiseflow_arch.png)
