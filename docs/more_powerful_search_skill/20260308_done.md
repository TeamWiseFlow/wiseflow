# 目的一

为 wiseflow add-on 增加一个 skill，旨在让 Agent 通过使用 skill 可以更好的操作浏览器完成各种搜索任务。替换 openclaw 内置的 web_search 工具。

## 实现方案

解析用户指令，按已知规则直接构造查询 url。对于 filter 和 sort 要求，按各平台摸索出的方法指导 agent。

其中常见社交媒体平台的搜索 url 构造和具体指导见  ./direct_url_for_search_on_media_platform.md

额外的去 /extra 文件夹下挨个分析里面的 python 脚本，提炼出查询 url，添加到本 skill 的支持列表中。

# 目的二

为 wiseflow add-on 增加一个 skill，旨在让 Agent 通过使用 skill 获取和解析 rss 信源

## 实现方案

参考 rss_parsor.py

