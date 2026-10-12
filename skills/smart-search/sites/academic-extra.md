# 学术研究补充站点

本站点组统一使用共享 session/profile `default`；每条 Camoufox 操作带 `--persistent`。入口常量见 [site-catalog.json](../site-catalog.json)。Google Scholar 是学术搜索；通用 Google 搜索不在本规则中。arXiv、百度学术、万方与 Wikipedia 见 [原有学术规则](academic.md)。

| 站点 | session / profile | 搜索入口 |
|---|---|---|
| Google Scholar | `default` | `https://scholar.google.com/scholar?q={keyword}&hl=zh-CN` |
| Semantic Scholar | `default` | `https://www.semanticscholar.org/`，使用页面搜索 |
| OpenAlex | `default` | `https://openalex.org/`，使用当前网页检索入口 |
| PubMed | `default` | `https://pubmed.ncbi.nlm.nih.gov/?term={keyword}` |
| DBLP | `default` | `https://dblp.org/`，使用页面搜索 |
| Crossref | `default` | `https://search.crossref.org/`，使用页面搜索 |
| CNKI/知网 | `default` | `https://oversea.cnki.net/kns/search?dbcode=CFLS&kw={keyword}&korder=SU` |

## Google Scholar

- 可搜索完整标题、关键词或作者；按页面控件限制年份、排序与文献类型。验证码按 browser-guide 处理，不持续重试。
- 提取标题、作者、出版信息、年份、主链接、可见引用数及可访问全文链接；结果的 `[PDF]`、`[HTML]` 与主文献分别保存。
- “所有版本”只在任务需要且预算允许时进入；会议稿、预印本和期刊版按 DOI/标题/版本去重，引用数标明来源和观察时间。

## Semantic Scholar

- 在首页搜索框提交关键词/标题，用页面实际提供的年份、领域、作者、文献类型等筛选。不要调用 Graph API 或推测网页 API 参数。
- 提取论文标题、作者、年份、出版渠道、论文详情链接、DOI 与可见引用/全文信息；摘要及版本状态到详情核对。
- 作者同名时核对机构、研究方向和关联作品；站点生成的摘要标记为站点摘要，不当作原文逐字引用。

## OpenAlex

- 打开主页后等待客户端界面，进入实际提供的 works、authors、sources 或 institutions 检索；类别由用户问题决定。
- 提取当前类别的名称/标题、实体详情链接、OpenAlex ID，以及页面可见的 DOI、ORCID、机构、年份和开放获取标记。
- 网页未提供搜索或要求本轮未具备的权限时，报告该入口不可用并交付缺口；不自动改用 `api.openalex.org`。元数据记录不代表全文已读取。

## PubMed

- 查询可保留 PubMed 网页支持的布尔表达式与字段标签，例如 `cancer AND 2024[dp]`，将整个表达式编码一次。
- 通过页面筛选出版日期、文献类型、语言及全文条件；区分 PubMed 收录记录、PMC 免费全文和出版商页面。
- 提取题名、作者、期刊、出版日期、PMID、DOI、摘要及可访问全文链接；医学主题结论需回到原论文核对，检索结果不直接生成诊疗建议。

## DBLP

- 通过页面搜索标题、作者或 venue；按真实界面切换 publication/person 等结果类型，不打开 API JSON 端点。
- 保存论文标题、作者、年份、会议/期刊、DBLP 详情链接、DOI/电子版链接；作者结果保存 person 页面并核对关联出版物。
- 同一论文的不同记录按 DOI 与出版版本区分；作者名字相同不能直接合并为同一人。

## Crossref

- 在搜索页输入标题、作者、DOI 或 ORCID；引用匹配时只使用当前页面提供的查询方式，不自动提交批量接口请求。
- 提取标题、作者、刊物、出版年份、DOI 与详情链接。DOI 跳转后核对出版商信息，区分 online、print 等可见日期字段。
- 元数据可能不含摘要/全文；未读到正文时只报告已核实的书目信息，不能由注册记录推断论文结论。

## CNKI/知网

- 模板为海外站主题检索；国内库或其他学科库用页面当前入口/数据库选择器，不沿用不匹配的 `dbcode` 或字段码。
- 按页面选择主题、篇名、作者、单位及日期；提取题名、作者、来源、年份/卷期、详情链接、可见摘要和 DOI。
- 下载/全文需要订阅或登录时按 browser-guide 处理，摘要与已读全文分别标记；不承诺可下载全部论文。

源码参考：[OpenCLI 学术站点](https://github.com/jackwener/OpenCLI/tree/b06ab7780e73d3021e12e0f170086c2d55675776/clis)、[SearXNG Crossref](https://github.com/searxng/searxng/blob/ad46ebd7d87666edb5f116c5b274b47f689ac6cd/searx/engines/crossref.py)。上游 API 仅用于核对能力与字段，不进入 Camoufox 搜索执行链。
