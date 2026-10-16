# 通用浏览器搜索

使用固定 session/profile `default`，全部 Camoufox 命令带 --persistent。先读 smart-search 的范围与预算规则。参数来源：[Bing](https://github.com/searxng/searxng/blob/ad46ebd7d87666edb5f116c5b274b47f689ac6cd/searx/engines/bing.py)、[百度](https://github.com/searxng/searxng/blob/ad46ebd7d87666edb5f116c5b274b47f689ac6cd/searx/engines/baidu.py)、[夸克](https://github.com/searxng/searxng/blob/ad46ebd7d87666edb5f116c5b274b47f689ac6cd/searx/engines/quark.py)。

## Bing

```
https://www.bing.com/search?q={keyword}
https://www.bing.com/news/search?q={keyword}
https://www.bing.com/images/search?q={keyword}
```

关键词编码后放入 q。时间条件可在页面选择并复核当前结果；网页搜索常见候选参数 `filters=ex1:"ez1"`（天）/`ez2`（周）/`ez3`（月），参数需 URL 编码，不能仅凭 URL 认定过滤已生效。

传统翻页 first 候选为 `(页码-1)*10+1`，但当前结果数和下一页可能由 JS 决定。优先使用页面真实下一页链接；SearXNG 当前 Bing 网页引擎也不承诺分页和时间筛选，不把公式当作始终有效。

提取真实结果区的标题、摘要与链接，通常为 `#b_results` 中的普通结果。Bing 的 `/ck/a?` 可能是重定向链接，访问原文后记录最终公开 URL；广告或装饰图标不是正文。

## 百度

```
https://www.baidu.com/s?wd={keyword}
https://image.baidu.com/search/index?tn=baiduimage&ie=utf-8&word={keyword}
```

网页分页候选 pn 为 0、10、20……，优先采用页面实际下一页。时间筛选使用页面控件，不把 SearXNG REST 返回格式、JSON 选项或移动端图片请求参数当作网页搜索规则。遇到百度安全验证按 browser-guide 处理。

## 夸克

```
https://quark.sm.cn/s?q={keyword}&layout=html&page=1
```

page 从 1 开始；时间候选 tl_request：4 天、3 周、2 月、1 年。需要筛选时复核实际页面，不以参数存在代替结果核验。仅保留网页搜索入口，图片接口未收纳进本技能。

通用搜索不必无条件访问首页。返回验证码、登录墙或空骨架时分别处理，不将防护页当作零结果；最多两次搜索导航的预算仍适用。
