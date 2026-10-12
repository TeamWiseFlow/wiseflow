# smart-search 上游复核与站点接入

2026-10-12：smart-search 与 browser-guide 独立保留。前者专用于 Camoufox 浏览器搜索，后者提供通用浏览器操作。用户确认新增六类专业来源，共 36 个站点；通用搜索候选不接入，仍使用现有 Bing、百度和夸克。

同日补充：普通浏览器搜索站点直接共享 Camoufox 内置 `default` profile，省略 `--session` 并保留 `--persistent`，不另设搜索专用 profile。包括需要登录的站点和新增 36 站；自媒体专用 profile 与各技能的 API 登录态按原约定保留，不按普通站点或类别另建 profile。本地 CLI 的参数解析和默认持久化路径均已核对。

源码基线：[OpenCLI b06ab778](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/cli-manifest.json)、[SearXNG ad46ebd7](https://github.com/searxng/searxng/blob/ad46ebd7d87666edb5f116c5b274b47f689ac6cd/searx/settings.yml)。完整参考 clone 位于 wiseflow-pro；不运行上游应用或安装其浏览器扩展。

统计采用 OpenCLI 已注册 access=read 且命令名含 search/find/query 的站点，共 101 个；SearXNG settings.yml 共 352 个引擎配置条目，包含同站不同分类、API、需 Key、默认关闭及内部数据源，不能将条目数当作可用网站数。

下方完整差集保留首次复核时的快照；其中“未覆盖”指当时没有可执行的站点规则，不代表本轮接入后的状态。当前接入范围以六类规则和 [站点配置](../skills/smart-search/site-catalog.json) 为准。上游有适配器不表示 Camoufox 页面路径已验收，API-only 与登录条件分别处理。

## 已调整的现有规则

| 规则 | 核对与调整 | 证据 |
|---|---|---|
| arXiv | 网页 searchtype 使用 title/author/abstract；删除独立 XML API 指导，区分公告日期与更新日期 | [实际搜索表单](https://arxiv.org/search/) |
| Bing/百度/夸克 | 分页以实际网页链接为准；夸克补 layout=html、page 与 tl_request；不承诺首页访问即可解除验证 | [Bing](https://github.com/searxng/searxng/blob/ad46ebd7d87666edb5f116c5b274b47f689ac6cd/searx/engines/bing.py)、[夸克](https://github.com/searxng/searxng/blob/ad46ebd7d87666edb5f116c5b274b47f689ac6cd/searx/engines/quark.py) |
| GitHub | 公开仓库代码搜索仍要求登录；代码搜索与仓库搜索的排序/过滤规则分开 | [GitHub 文档](https://docs.github.com/en/search-github/github-code-search/about-github-code-search) |
| 知乎 | 不把 search_v3 接口的类型、limit/offset、paging.next 当作网页分页/筛选保证 | [OpenCLI](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/zhihu/search.js) |
| B站 | 移除字幕 API 指导；WBI/search_type 与页面类别分开，页面卡片未显示的指标保留缺项 | [OpenCLI](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/bilibili/search.js) |
| YouTube | 保留已匹配的 sp 筛选值，明确仅一个 sp；补新旧卡片/Shorts 结构和不能用接口续查的约束 | [OpenCLI](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/youtube/search.js) |
| LinkedIn/Reddit/雪球 | 固定 profile 与真实登录核验，实际页面控件/DOM 提取；API 参数不冒充页面规则 | [LinkedIn](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/linkedin/people-search.js)、[Reddit](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/reddit/search.js)、[雪球](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/xueqiu/search.js) |
| HN/V2EX/贴吧 | HN 按页面筛选；V2EX 去掉首页 ?q= 的假搜索入口；贴吧 pn 为从 1 开始的页码 | [HN](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/hackernews/search.js)、[V2EX](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/v2ex)、[贴吧](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/tieba/search.js) |
| Reuters/BBC | Reuters 当前上游都用接口，不再保证旧 /search/news?blob=；从页面搜索控件进入或查公开索引；BBC 去掉 URL 尾部误写的反引号 | [OpenCLI](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/reuters/search.js)、[SearXNG](https://github.com/searxng/searxng/blob/ad46ebd7d87666edb5f116c5b274b47f689ac6cd/searx/engines/reuters.py) |
| 国务院/万方/Amazon | URL 保留，补延迟挂载、实际结果识别与不可访问字段的处理 | [国务院](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/gov-policy/search.js)、[万方](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/wanfang/search.js)、[Amazon](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/amazon/search.js) |
| 抖音/小红书/X/微博 | main 配置采集技能时优先该技能；未配置的 crew 可按既有平台的浏览器页面规则，固定对应 profile，读取可见结果 | [OpenCLI clis](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis) |

验证范围：源码对照、公开 HTTP 状态/表单与本地规则一致性；未登录实际平台做全链路 Camoufox 验收。Reuters 两个候选页均返回 401，不能据此宣称新旧 URL 有效或已失效。V2EX 首页 200 也不代表存在搜索功能。

## 用户确认的接入范围

| 方向 | 接入站点 | 浏览器规则 |
|---|---|---|
| 商业与行业（4） | 36氪、招标剑鱼、国家法律法规库、1688 | [商业规则](../skills/smart-search/sites/business.md) |
| 技术与 AI（7） | Stack Overflow、MDN、Gitee、Hugging Face、OpenReview、npm、PyPI | [技术规则](../skills/smart-search/sites/tech-ai.md) |
| 学术研究（7） | Google Scholar、Semantic Scholar、OpenAlex、PubMed、DBLP、Crossref、CNKI | [学术补充规则](../skills/smart-search/sites/academic-extra.md) |
| 招聘与合作需求（5） | BOSS直聘、51job、Indeed、脉脉、Upwork | [招聘规则](../skills/smart-search/sites/recruiting.md) |
| 产品与口碑（7） | 豆瓣、什么值得买、京东、淘宝、大众点评、虎扑、即刻 | [口碑规则](../skills/smart-search/sites/consumer.md) |
| 设计与内容参考（6） | Pinterest、Pixiv、ArtStation、Flickr、Unsplash、Openverse | [设计规则](../skills/smart-search/sites/design.md) |

未接入通用候选 Google、DuckDuckGo、Brave、Startpage、Sogou、Qwant、Mojeek。Google Scholar 属于已确认的学术来源，不属于通用网页搜索。

新增 36 站全部使用共享持久化 `default` profile，配置与入口集中在 `site-catalog.json`；SKILL.md 和分组规则列明名称。原站支持网页查询的保留网页模板，上游仅提供 API 的改为主页/真实表单操作；51job 明确排除 `/api/job/search-pc`，脉脉企业人才入口保留实际权限条件，OpenAlex/Openverse 网页不可用时报告缺口。未移植 Chrome bridge、HTTP 引擎、API key 或私有接口。

新增规则完成源码对照及本地链接、清单和 profile 一致性检查；没有对 36 个站点逐站登录进行 Camoufox 全链路验收。规则存在不等于当前账号/网络已可访问。

以下附上首次复核的完整差集；本轮只接入上表 36 个站点，其余条目继续保留为评估资料，不自动添加。

## OpenCLI：首次复核的未覆盖平台快照

| 站点 ID | 域名 | 只读搜索命令 | 上游方式 | 本地现状 | 源文件 |
|---|---|---|---|---|---|
| 1688 | www.1688.com | search | cookie | 未维护规则 | 1688/search.js |
| 1point3acres | www.1point3acres.com | search | cookie | 未维护规则 | 1point3acres/search.js |
| 36kr | www.36kr.com | search | public | 仅提到域名/源建议，未维护规则 | 36kr/search.js |
| 51job | we.51job.com | search | cookie | 未维护规则 | 51job/search.js |
| apple-podcasts |  | search | public | 未维护规则 | apple-podcasts/search.js |
| archive | archive.org | search | public | 未维护规则 | archive/search.js |
| bluesky | public.api.bsky.app | search | public | 未维护规则 | bluesky/search.js |
| booking | www.booking.com | search | public | 仅提到域名/源建议，未维护规则 | booking/search.js |
| boss | www.zhipin.com | search | intercept | 未维护规则 | boss/search.js |
| brave | search.brave.com | search | public | 未维护规则 | brave/search.js |
| cnki | oversea.cnki.net | search | cookie | 未维护规则 | cnki/search.js |
| coupang | www.coupang.com | search | cookie | 未维护规则 | coupang/search.js |
| crates | crates.io | search | public | 未维护规则 | crates/search.js |
| ctrip | hotels.ctrip.com | hotel-search, search | cookie, public | 仅提到域名/源建议，未维护规则 | ctrip/hotel-search.js, ctrip/search.js |
| dblp | dblp.org | search | public | 未维护规则 | dblp/search.js |
| dianping | www.dianping.com | search | cookie | 未维护规则 | dianping/search.js |
| dictionary | api.dictionaryapi.dev | search | public | 未维护规则 | dictionary/search.js |
| dockerhub | hub.docker.com | search | public | 未维护规则 | dockerhub/search.js |
| dongchedi |  | search | public | 未维护规则 | dongchedi/search.js |
| douban | search.douban.com | search | cookie | 未维护规则 | douban/search.js |
| duckduckgo | html.duckduckgo.com | search | public | 仅提到域名/源建议，未维护规则 | duckduckgo/search.js |
| facebook | www.facebook.com | search | cookie | 未维护规则 | facebook/search.js |
| flathub | flathub.org | search | public | 未维护规则 | flathub/search.js |
| gitee | gitee.com | search | public | 未维护规则 | gitee/search.js |
| google | google.com | search | public | 仅提到域名/源建议，未维护规则 | google/search.js |
| google-scholar | scholar.google.com | search | public | 未维护规则 | google-scholar/search.js |
| gov-law | flk.npc.gov.cn | search | public | 未维护规则 | gov-law/search.js |
| hltv | www.hltv.org | search | ui | 未维护规则 | hltv/search.js |
| hupu | bbs.hupu.com | search | public | 未维护规则 | hupu/search.js |
| imdb | www.imdb.com | search | public | 未维护规则 | imdb/search.js |
| indeed | www.indeed.com | search | cookie | 未维护规则 | indeed/search.js |
| instagram | www.instagram.com | search | cookie | 未维护规则 | instagram/search.js |
| jd | search.jd.com | search | cookie | 未维护规则 | jd/search.js |
| jianyu | www.jianyu360.cn | search | cookie | 未维护规则 | jianyu/search.js |
| jike | web.okjike.com | search | cookie | 未维护规则 | jike/search.js |
| linkedin-learning | www.linkedin.com | search | cookie | 未维护规则 | linkedin-learning/search.js |
| linux-do | linux.do | search | cookie | 未维护规则 | linux-do/search.js |
| maimai | maimai.cn | search-talents | cookie | 未维护规则 | maimai/search-talents.js |
| maven | search.maven.org | search | public | 未维护规则 | maven/search.js |
| mdn | developer.mozilla.org | search | public | 未维护规则 | mdn/search.js |
| medium | medium.com | search | cookie | 未维护规则 | medium/search.js |
| nowcoder | www.nowcoder.com | search | cookie | 未维护规则 | nowcoder/search.js |
| npm | registry.npmjs.org | search | public | 未维护规则 | npm/search.js |
| nuget | api.nuget.org | search | public | 未维护规则 | nuget/search.js |
| oeis | oeis.org | search | public | 未维护规则 | oeis/search.js |
| openalex | api.openalex.org | search | public | 未维护规则 | openalex/search.js |
| openreview | openreview.net | search | public | 未维护规则 | openreview/search.js |
| osv | osv.dev | query | public | 未维护规则 | osv/query.js |
| packagist | packagist.org | search | public | 未维护规则 | packagist/search.js |
| pinterest | www.pinterest.com | search-boards, search-pins, search-users | cookie | 未维护规则 | pinterest/search-boards.js, pinterest/search-pins.js, pinterest/search-users.js |
| pixiv | www.pixiv.net | search | cookie | 未维护规则 | pixiv/search.js |
| powerchina | bid.powerchina.cn | search | cookie | 未维护规则 | powerchina/search.js |
| pubmed | pubmed.ncbi.nlm.nih.gov | search | public | 未维护规则 | pubmed/search.js |
| rubygems | rubygems.org | search | public | 未维护规则 | rubygems/search.js |
| semanticscholar | api.semanticscholar.org | search | public | 未维护规则 | semanticscholar/search.js |
| sinablog | blog.sina.com.cn | search | public | 未维护规则 | sinablog/search.js |
| smzdm | www.smzdm.com | search | cookie | 未维护规则 | smzdm/search.js |
| spotify |  | search | public | 未维护规则 | spotify/spotify.js |
| stackoverflow | stackoverflow.com | search | public | 仅提到域名/源建议，未维护规则 | stackoverflow/search.js |
| steam | store.steampowered.com | search | public | 未维护规则 | steam/search.js |
| substack | substack.com | search | public | 未维护规则 | substack/search.js |
| taobao | s.taobao.com | search | cookie | 未维护规则 | taobao/search.js |
| trip | trip.com | hotel-search, search | cookie, public | 未维护规则 | trip/hotel-search.js, trip/search.js |
| tvmaze | tvmaze.com | search | public | 未维护规则 | tvmaze/search.js |
| upwork | www.upwork.com | search | cookie | 未维护规则 | upwork/search.js |
| weread | weread.qq.com | book-search, search | public | 未维护规则 | weread/book-search.js, weread/search.js |
| weread-official | weread.qq.com | search | public | 未维护规则 | weread-official/search.js |
| wikidata | www.wikidata.org | search | public | 未维护规则 | wikidata/search.js |
| xianyu | www.goofish.com | search | cookie | 未维护规则 | xianyu/search.js |
| yahoo | search.yahoo.com | search | public | 未维护规则 | yahoo/search.js |
| zlibrary | z-library.im | search | cookie | 未维护规则 | zlibrary/search.js |
| zsxq | wx.zsxq.com | search | cookie | 未维护规则 | zsxq/search.js |

首次复核差集共 72 个平台 ID；部分已在本轮接入，当前规则以上方接入表为准。平台可能有多个域名或别名，未把同一服务的命令数量计作不同站点。

已有站点规则的 OpenCLI 平台：amazon、arxiv、baidu-scholar、bilibili、gov-policy、hackernews、linkedin、reddit、reuters、tieba、wanfang、wikipedia、xueqiu、youtube、zhihu。

main 已有采集路由（不作为新站点自动增加）：douyin、xiaohongshu/rednote、tiktok、twitter、weibo、weixin；实际能力按 douyin-hunter、xhs-hunter、tiktok-hunter、x-hunter、weibo-hunter、wx-mp-hunter 的说明核验。

内部账户/协作搜索未纳入公开站点候选：chatgpt、confluence、gemini、gmail、jira、mubu、slock。这些项目的搜索功能不等于公开信息检索。

## SearXNG：首次复核的未覆盖引擎快照

同站的图片/新闻/视频等分类仍分别列出，便于评估新增能力；并非每行都是不同网站。JSON/API 路径与需 Key 的项目须先另行核对网页入口。“API/Key 未标注”不代表无需 Key。disabled 是上游默认关闭，inactive 是上游不装载，不作为本技能可用性证据。

| 引擎条目 | 网站/实例 | 类别 | 返回方式 / Key | 上游默认状态 | 本地现状 | 源模块 |
|---|---|---|---|---|---|---|
| 360search | https://www.so.com/ | general | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/360search.py |
| 360search videos | https://tv.360kan.com/ | videos | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/360search_videos.py |
| 500px | https://500px.com | stock images | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/500px.py |
| 9gag | https://9gag.com/ | social media | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/9gag.py |
| abcnyheter | 实例/站点需核对 | general | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| acfun | https://www.acfun.cn/ | videos | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/acfun.py |
| astrophysics data system | https://ui.adsabs.harvard.edu/ | science, scientific publications | JSON / 需 Key | inactive | 未维护规则 | searx/engines/astrophysics_data_system.py |
| alpine linux packages | https://www.alpinelinux.org | packages, it | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/alpinelinux.py |
| annas archive | https://annas-archive.gl/ | files, books | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/annas_archive.py |
| ansa | https://www.ansa.it | news | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/ansa.py |
| apk mirror | https://www.apkmirror.com | it, apps | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/apkmirror.py |
| apple app store | https://www.apple.com/app-store/ | it, apps | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/apple_app_store.py |
| ahmia | http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion | onions | HTML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/ahmia.py |
| anaconda | 实例/站点需核对 | it | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| arch linux wiki | https://wiki.archlinux.org/ | it, software wikis | HTML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/archlinux.py |
| nixos wiki | https://wiki.nixos.org/ | it, software wikis | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/mediawiki.py |
| artic | https://www.artic.edu | images | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/artic.py |
| artstation | https://www.artstation.com/ | images | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/artstation.py |
| avalw | 实例/站点需核对 | general | 方式未标注 / Key 未标注 | inactive | 未维护规则 | searx/engines/json_engine.py |
| ayo | 实例/站点需核对 | general | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| azure | https://www.portal.azure.com | it, cloud | JSON / 需 Key | inactive | 未维护规则 | searx/engines/azure.py |
| bandcamp | https://bandcamp.com/ | music | HTML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/bandcamp.py |
| baidu kaifa | https://www.baidu.com | it | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/baidu.py |
| bing videos | https://www.bing.com/videos | videos, web | HTML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/bing_videos.py |
| bitchute | https://bitchute.com | videos | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/bitchute.py |
| bitbucket | 实例/站点需核对 | it, repos | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| boardreader | https://boardreader.com | general, social media | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/boardreader.py |
| bpb | https://www.bpb.de | general | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/bpb.py |
| btdigg | https://btdig.com | files | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/btdigg.py |
| openverse | https://openverse.org/ | images | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/openverse.py |
| media.ccc.de | https://media.ccc.de | videos | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/ccc_media.py |
| cachy os packages | https://cachyos.org | packages, it | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/cachy_os.py |
| chefkoch | https://www.chefkoch.de |  | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/chefkoch.py |
| chinaso news | https://www.chinaso.com/ | news | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/chinaso.py |
| cl0q | 实例/站点需核对 | general | 方式未标注 / Key 未标注 | inactive | 未维护规则 | searx/engines/json_engine.py |
| cloudflareai | https://ai.cloudflare.com |  | JSON / 需 Key | inactive | 未维护规则 | searx/engines/cloudflareai.py |
| core.ac.uk | https://core.ac.uk | science, scientific publications | JSON / 需 Key | inactive | 未维护规则 | searx/engines/core.py |
| crossref | https://www.crossref.org/ | science, scientific publications | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/crossref.py |
| crowdview | 实例/站点需核对 | general | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/json_engine.py |
| yep | https://yep.com/ | general | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/yep.py |
| currency | https://duckduckgo.com/ | currency, general | JSONP / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/currency_convert.py |
| deezer | https://deezer.com | music | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/deezer.py |
| destatis | https://www.destatis.de |  | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/destatis.py |
| deviantart | https://www.deviantart.com/ | images | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/deviantart.py |
| devicons | https://devicon.dev/ | images, icons | JSON / Key 未标注 | disabled | 未维护规则 | searx/engines/devicons.py |
| ddg definitions | https://duckduckgo.com/ |  | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/duckduckgo_definitions.py |
| docker hub | https://hub.docker.com | it, packages | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/docker_hub.py |
| encyclosearch | 实例/站点需核对 | general | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/json_engine.py |
| europepmc | https://europepmc.org/ | science, scientific publications | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/europepmc.py |
| erowid | 实例/站点需核对 |  | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| elasticsearch | https://www.elastic.co | general | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/elasticsearch.py |
| wikidata | https://wikidata.org/ | general | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/wikidata.py |
| dogpile | https://www.dogpile.com | general | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/dogpile.py |
| dogpile images | https://www.dogpile.com | images | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/dogpile.py |
| dogpile videos | https://www.dogpile.com | videos | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/dogpile.py |
| dogpile news | https://www.dogpile.com | news | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/dogpile.py |
| duckduckgo | https://lite.duckduckgo.com/lite/ | general, web | HTML / 无需 Key（上游声明） | 启用配置 | 仅提到域名或已有其他素材技能 | searx/engines/duckduckgo.py |
| duckduckgo web | https://duckduckgo.com/ | general | JSON / 无需 Key（上游声明） | disabled | 仅提到域名或已有其他素材技能 | searx/engines/duckduckgo_web.py |
| duckduckgo images | https://duckduckgo.com/ | images | JSON (site requires js to get images) / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/duckduckgo_extra.py |
| duckduckgo videos | https://duckduckgo.com/ | videos | JSON (site requires js to get images) / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/duckduckgo_extra.py |
| duckduckgo news | https://duckduckgo.com/ | news | JSON (site requires js to get images) / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/duckduckgo_extra.py |
| duckduckgo weather | https://duckduckgo.com/ | weather | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/duckduckgo_weather.py |
| apple maps | https://www.apple.com/maps/ | map | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/apple_maps.py |
| emojipedia | https://emojipedia.org |  | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/emojipedia.py |
| tineye | https://tineye.com | general | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/tineye.py |
| etymonline | 实例/站点需核对 | dictionaries | 方式未标注 / Key 未标注 | 启用配置 | 未维护规则 | searx/engines/xpath.py |
| ebay | https://www.ebay.com | shopping | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/ebay.py |
| 1x | https://1x.com/ | stock images | HTML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/www1x.py |
| fastbot | 实例/站点需核对 | general | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| fdroid | https://f-droid.org/ | it, apps | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/fdroid.py |
| findborg | https://www.findborg.com | general | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/findborg.py |
| findborg images | https://www.findborg.com | images | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/findborg.py |
| findborg videos | https://www.findborg.com | videos | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/findborg.py |
| findborg news | https://www.findborg.com | news | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/findborg.py |
| findfiles | https://findfiles.net | files | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/findfiles.py |
| findfiles images | https://findfiles.net | images | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/findfiles.py |
| findfiles videos | https://findfiles.net | videos | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/findfiles.py |
| findfiles music | https://findfiles.net | music | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/findfiles.py |
| findthatmeme | https://findthatmeme.com | images | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/findthatmeme.py |
| fireball | https://fireball.com | general | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/fireball.py |
| fireball news | https://fireball.com | news | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/fireball.py |
| fireball videos | https://fireball.com | videos | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/fireball.py |
| flaticon | https://www.flaticon.com | images, icons | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/flaticon.py |
| flickr | https://www.flickr.com | images | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/flickr_noapi.py |
| flickr_api | https://www.flickr.com | images | JSON / 需 Key | inactive | 未维护规则 | searx/engines/flickr.py |
| free software directory | https://directory.fsf.org/ | it, software wikis | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/mediawiki.py |
| freesound | https://freesound.org |  | JSON / 需 Key | inactive | 未维护规则 | searx/engines/freesound.py |
| frinkiac | https://frinkiac.com | images | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/frinkiac.py |
| fynd | 实例/站点需核对 | general | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| fyyd | https://fyyd.de |  | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/fyyd.py |
| gabanza | 实例/站点需核对 | general | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| geizhals | https://geizhals.de | shopping | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/geizhals.py |
| genius | https://genius.com/ | music, lyrics | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/genius.py |
| gentoo | https://wiki.gentoo.org/ | it, software wikis | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/mediawiki.py |
| giphy | https://giphy.com | images | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/giphy.py |
| gitlab | https://gitlab.com | it, repos | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/gitlab.py |
| codeberg | https://about.gitea.com | it, repos | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/gitea.py |
| gitea.com | https://about.gitea.com | it, repos | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/gitea.py |
| gmx | https://search.gmx.com | general | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/gmx.py |
| goodreads | https://www.goodreads.com |  | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/goodreads.py |
| google | https://www.google.com | general, web | XML / 无需 Key（上游声明） | disabled | 仅提到域名或已有其他素材技能 | searx/engines/google.py |
| google images | https://images.google.com | images, web | XML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/google_images.py |
| google news | https://www.google.com | news | XML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/google_news.py |
| google videos | https://www.google.com | videos, web | XML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/google_videos.py |
| google cse | https://www.google.com | general, web | JSONP / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/google_cse.py |
| google cse images | https://www.google.com | images, web | JSONP / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/google_cse.py |
| google scholar | https://scholar.google.com | science, scientific publications | HTML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/google_scholar.py |
| google play apps | https://play.google.com/ | it, apps | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/google_play.py |
| google play movies | https://play.google.com/ | videos | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/google_play.py |
| grokipedia | https://grokipedia.com | general | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/grokipedia.py |
| material icons | https://fonts.google.com/icons | images, icons | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/material_icons.py |
| habrahabr | 实例/站点需核对 | it | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| hex | https://hex.pm/ | it, packages | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/hex.py |
| crates.io | https://crates.io/ | it, packages, cargo | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/crates.py |
| hoogle | 实例/站点需核对 | it, packages | 方式未标注 / Key 未标注 | 启用配置 | 未维护规则 | searx/engines/xpath.py |
| iconify | https://iconify.design | images, icons | JSON / Key 未标注 | disabled | 未维护规则 | searx/engines/iconify.py |
| iseek | https://www.iseek.com | general | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/iseek.py |
| il post | https://www.ilpost.it | news | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/il_post.py |
| huggingface | https://huggingface.co/ | it, repos | JSON / 无需 Key（上游声明） | disabled | 仅提到域名或已有其他素材技能 | searx/engines/huggingface.py |
| huggingface datasets | https://huggingface.co/ | it, repos | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/huggingface.py |
| huggingface spaces | https://huggingface.co/ | it, repos | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/huggingface.py |
| imdb | https://imdb.com/ | movies | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/imdb.py |
| imgur | https://imgur.com/ | images | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/imgur.py |
| ina | https://www.ina.fr/ | videos | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/ina.py |
| ipernity | https://www.ipernity.com | images | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/ipernity.py |
| iqiyi | https://www.iqiyi.com/ | videos | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/iqiyi.py |
| jina | https://jina.ai | general | JSON / 需 Key | inactive | 未维护规则 | searx/engines/jina.py |
| kavunka demo | 实例/站点需核对 | general | 方式未标注 / Key 未标注 | inactive | 未维护规则 | searx/engines/xpath.py |
| keenable | https://keenable.ai | general | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/keenable.py |
| kozmonavt | 实例/站点需核对 |  | 方式未标注 / Key 未标注 | inactive | 未维护规则 | searx/engines/xpath.py |
| jisho | https://jisho.org | dictionaries | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/jisho.py |
| kickass | https://kickasstorrents.to | files | HTML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/kickass.py |
| kukei | 实例/站点需核对 | general, blogs | 方式未标注 / Key 未标注 | inactive | 未维护规则 | searx/engines/xpath.py |
| lemmy communities | https://lemmy.ml/ | social media | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/lemmy.py |
| lemmy users | https://lemmy.ml/ | social media | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/lemmy.py |
| lemmy posts | https://lemmy.ml/ | social media | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/lemmy.py |
| lemmy comments | https://lemmy.ml/ | social media | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/lemmy.py |
| library genesis | 实例/站点需核对 | files | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| z-library | https://zlibrary-global.se | files, books | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/zlibrary.py |
| libretranslate | https://libretranslate.com | general, translate | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/libretranslate.py |
| littlelayer | 实例/站点需核对 | general, blogs | 方式未标注 / Key 未标注 | inactive | 未维护规则 | searx/engines/json_engine.py |
| lingva | https://github.com/thedaviddelta/lingva-translate | general, translate | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/lingva.py |
| lobste.rs | 实例/站点需核对 | it | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| lucide | https://lucide.dev/ | images, icons | JSON / Key 未标注 | disabled | 未维护规则 | searx/engines/lucide.py |
| luxxle | https://luxxle.com | general | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/luxxle.py |
| luxxle images | https://luxxle.com | images | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/luxxle.py |
| luxxle videos | https://luxxle.com | videos | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/luxxle.py |
| luxxle news | https://luxxle.com | news | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/luxxle.py |
| magnific | https://www.magnific.com | stock images | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/magnific.py |
| marginalia | https://marginalia.nu | general, blogs | JSON / 需 Key | inactive | 未维护规则 | searx/engines/marginalia.py |
| mastodon users | https://joinmastodon.org/ | social media | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/mastodon.py |
| mastodon hashtags | https://joinmastodon.org/ | social media | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/mastodon.py |
| mdn | 实例/站点需核对 | it | 方式未标注 / Key 未标注 | 启用配置 | 未维护规则 | searx/engines/json_engine.py |
| metacpan | https://metacpan.org/ | it, packages | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/metacpan.py |
| microsoft learn | https://learn.microsoft.com | it | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/microsoft_learn.py |
| mixcloud | https://www.mixcloud.com/ | music | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/mixcloud.py |
| mozhi | https://codeberg.org/aryak/mozhi | general, translate | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/mozhi.py |
| mwmbl | https://github.com/mwmbl/mwmbl | general | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/mwmbl.py |
| neocities | https://neocities.org/ | general, blogs | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/neocities.py |
| niconico | https://www.nicovideo.jp/ | videos | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/niconico.py |
| npm | https://npms.io/ | it, packages | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/npm.py |
| nyaa | https://nyaa.si/ | files | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/nyaa.py |
| mankier | 实例/站点需核对 | it | 方式未标注 / Key 未标注 | 启用配置 | 未维护规则 | searx/engines/json_engine.py |
| odysee | https://odysee.com/ | videos | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/odysee.py |
| ollama | https://ollama.com | it, repos | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/ollama.py |
| openairedatasets | 实例/站点需核对 | science | 方式未标注 / Key 未标注 | 启用配置 | 未维护规则 | searx/engines/json_engine.py |
| openairepublications | 实例/站点需核对 | science | 方式未标注 / Key 未标注 | 启用配置 | 未维护规则 | searx/engines/json_engine.py |
| openalex | https://openalex.org/ | science, scientific publications | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/openalex.py |
| openclipart | https://openclipart.org/ | images | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/openclipart.py |
| openlibrary | https://openlibrary.org | general, books | 方式未标注 / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/openlibrary.py |
| openmeteo | https://open-meteo.com | weather | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/open_meteo.py |
| openstreetmap | https://www.openstreetmap.org/ | map | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/openstreetmap.py |
| openrepos | 实例/站点需核对 | files | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| packagist | 实例/站点需核对 | it, packages | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/json_engine.py |
| pdbe | https://www.ebi.ac.uk/pdbe | science | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/pdbe.py |
| pexels | https://www.pexels.com | stock images | JSON / 无需 Key（上游声明） | 启用配置 | 仅提到域名或已有其他素材技能 | searx/engines/pexels.py |
| photon | https://photon.komoot.io | map | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/photon.py |
| picjumbo | https://picjumbo.com | stock images | HTML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/picjumbo.py |
| pinterest | https://www.pinterest.com/ | images | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/pinterest.py |
| piped | https://github.com/TeamPiped/Piped/ | videos | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/piped.py |
| piped.music | https://github.com/TeamPiped/Piped/ | music | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/piped.py |
| piratebay | https://thepiratebay.org | files | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/piratebay.py |
| pixabay images | https://pixabay.com | stock images | JSON / 无需 Key（上游声明） | disabled | 仅提到域名或已有其他素材技能 | searx/engines/pixabay.py |
| pixabay videos | https://pixabay.com | videos | JSON / 无需 Key（上游声明） | disabled | 仅提到域名或已有其他素材技能 | searx/engines/pixabay.py |
| pixiv | https://www.pixiv.net/ | images | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/pixiv.py |
| podchaser | https://www.podchaser.com |  | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/podchaser.py |
| pub.dev | 实例/站点需核对 | packages, it | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| public domain image archive | https://pdimagearchive.org | images | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/public_domain_image_archive.py |
| pubmed | https://www.ncbi.nlm.nih.gov/pubmed/ | science, scientific publications | XML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/pubmed.py |
| pypi | https://pypi.org | it, packages | HTML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/pypi.py |
| quark images | https://quark.sm.cn/ | images | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/quark.py |
| qwant | https://www.qwant.com/ | general, web | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/qwant.py |
| qwant news | https://www.qwant.com/ | news | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/qwant.py |
| qwant images | https://www.qwant.com/ | images, web | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/qwant.py |
| qwant videos | https://www.qwant.com/ | videos, web | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/qwant.py |
| radio browser | https://www.radio-browser.info/ | music, radio | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/radio_browser.py |
| rawweb | 实例/站点需核对 | general, blogs | 方式未标注 / Key 未标注 | inactive | 未维护规则 | searx/engines/json_engine.py |
| rottentomatoes | https://www.rottentomatoes.com/ | movies | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/rottentomatoes.py |
| searchmysite | 实例/站点需核对 | general, blogs | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| searchrockit | https://searchrockit.com | general | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/searchrockit.py |
| searchrockit images | https://searchrockit.com | images | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/searchrockit.py |
| searchrockit news | https://searchrockit.com | news | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/searchrockit.py |
| selfhst icons | https://selfh.st/icons/ | images, icons | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/selfhst.py |
| sepiasearch | https://sepiasearch.org | videos | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/sepiasearch.py |
| shopify stock | https://www.shopify.com/stock-photos | stock images | HTML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/shopify_stock.py |
| sogou | https://www.sogou.com/ | general | HTML / 无需 Key（上游声明） | disabled | 仅提到域名或已有其他素材技能 | searx/engines/sogou.py |
| sogou images | https://pic.sogou.com/ | images | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/sogou_images.py |
| sogou videos | https://v.sogou.com/ | videos | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/sogou_videos.py |
| sogou wechat | https://weixin.sogou.com/ | news | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/sogou_wechat.py |
| soundcloud | https://soundcloud.com | music | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/soundcloud.py |
| stackoverflow | https://stackexchange.com | it, q&a | JSON / 无需 Key（上游声明） | 启用配置 | 仅提到域名或已有其他素材技能 | searx/engines/stackexchange.py |
| stocksnap | https://stocksnap.io | stock images | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/stocksnap.py |
| askubuntu | https://stackexchange.com | it, q&a | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/stackexchange.py |
| superuser | https://stackexchange.com | it, q&a | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/stackexchange.py |
| discuss.python | https://discourse.org/ | it, q&a | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/discourse.py |
| caddy.community | https://discourse.org/ | it, q&a | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/discourse.py |
| pi-hole.community | https://discourse.org/ | it, q&a | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/discourse.py |
| privacywall | https://privacywall.org | general | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/privacywall.py |
| privacywall images | https://privacywall.org | images | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/privacywall.py |
| privacywall videos | https://privacywall.org | videos | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/privacywall.py |
| seekninja | https://seek.ninja | general | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/seekninja.py |
| semantic scholar | https://www.semanticscholar.org/ | science, scientific publications | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/semantic_scholar.py |
| springer nature | https://www.springernature.com/ | science, scientific publications | JSON / 需 Key | inactive | 未维护规则 | searx/engines/springer.py |
| startpage | https://startpage.com | general, web | HTML / 无需 Key（上游声明） | inactive | 仅提到域名或已有其他素材技能 | searx/engines/startpage.py |
| startpage news | https://startpage.com | news, web | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/startpage.py |
| startpage images | https://startpage.com | images, web | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/startpage.py |
| steam | https://store.steampowered.com/ |  | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/steam.py |
| tokyotoshokan | https://www.tokyotosho.info/ | files | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/tokyotoshokan.py |
| solidtorrents | https://www.solidtorrents.to/ | files | HTML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/solidtorrents.py |
| tagesschau | https://tagesschau.de | general, news | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/tagesschau.py |
| tiger | https://tiger.ch | general | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/tiger.py |
| tiger news | https://tiger.ch | news | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/tiger.py |
| tmdb | 实例/站点需核对 | movies | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| tonline | 实例/站点需核对 |  | 方式未标注 / Key 未标注 | inactive | 未维护规则 | searx/engines/tonline.py |
| tonline images | 实例/站点需核对 | images | 方式未标注 / Key 未标注 | inactive | 未维护规则 | searx/engines/tonline.py |
| tonline videos | 实例/站点需核对 | videos | 方式未标注 / Key 未标注 | inactive | 未维护规则 | searx/engines/tonline.py |
| tonline news | 实例/站点需核对 | news | 方式未标注 / Key 未标注 | inactive | 未维护规则 | searx/engines/tonline.py |
| torch | 实例/站点需核对 | onions | 方式未标注 / Key 未标注 | 启用配置 | 未维护规则 | searx/engines/xpath.py |
| Torznab EZTV | 实例/站点需核对 | files | XML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/torznab.py |
| tusksearch | https://tusksearch.com | general | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/tusksearch.py |
| tusksearch images | https://tusksearch.com | images | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/tusksearch.py |
| tusksearch videos | https://tusksearch.com | videos | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/tusksearch.py |
| tusksearch news | https://tusksearch.com | news | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/tusksearch.py |
| unsplash | https://unsplash.com | stock images | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/unsplash.py |
| unobtanium | 实例/站点需核对 | general, blogs | 方式未标注 / Key 未标注 | inactive | 未维护规则 | searx/engines/xpath.py |
| yandex | https://yandex.com/ | general | HTML / 无需 Key（上游声明） | disabled | 仅提到域名或已有其他素材技能 | searx/engines/yandex.py |
| yandex images | https://yandex.com/ | images | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/yandex.py |
| yandex api | https://yandex.cloud/en/services/search-api | general, web | XML / 需 Key | inactive | 未维护规则 | searx/engines/yandex_api.py |
| yandex music | https://music.yandex.ru | music | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/yandex_music.py |
| yahoo | https://search.yahoo.com/ | general, web | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/yahoo.py |
| yahoo news | https://news.yahoo.com | news | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/yahoo_news.py |
| youtube_api | https://www.youtube.com/ | videos, music | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/youtube_api.py |
| dailymotion | https://www.dailymotion.com | videos | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/dailymotion.py |
| vimeo | https://vimeo.com/ | videos | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/vimeo.py |
| wiby | 实例/站点需核对 | general, blogs | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/json_engine.py |
| wikibooks | https://{language}.wikibooks.org/ | general, wikimedia | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/mediawiki.py |
| wikinews | https://{language}.wikinews.org/ | news, wikimedia | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/mediawiki.py |
| wikiquote | https://{language}.wikiquote.org/ | general, wikimedia | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/mediawiki.py |
| wikisource | https://{language}.wikisource.org/ | general, wikimedia | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/mediawiki.py |
| wikispecies | https://species.wikimedia.org/ | general, science, wikimedia | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/mediawiki.py |
| wiktionary | https://{language}.wiktionary.org/ | dictionaries, wikimedia | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/mediawiki.py |
| wikiversity | https://{language}.wikiversity.org/ | general, wikimedia | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/mediawiki.py |
| wikivoyage | https://{language}.wikivoyage.org/ | general, wikimedia | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/mediawiki.py |
| wikicommons.images | https://commons.wikimedia.org/ | images | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/wikicommons.py |
| wikicommons.videos | https://commons.wikimedia.org/ | videos | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/wikicommons.py |
| wikicommons.audio | https://commons.wikimedia.org/ | music | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/wikicommons.py |
| wikicommons.files | https://commons.wikimedia.org/ | files | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/wikicommons.py |
| wolframalpha | https://www.wolframalpha.com/ | general | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/wolframalpha_noapi.py |
| wolframalpha_api | https://www.wolframalpha.com | general | XML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/wolframalpha_api.py |
| dictzone | https://dictzone.com/ | general, translate | HTML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/dictzone.py |
| mymemory translated | https://mymemory.translated.net/ | general, translate | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/translated.py |
| 1337x | https://1337x.to/ | files | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/1337x.py |
| duden | https://www.duden.de | dictionaries | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/duden.py |
| seznam | https://www.seznam.cz/ | general, web | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/seznam.py |
| deepl | https://deepl.com | general, translate | JSON / 需 Key | inactive | 未维护规则 | searx/engines/deepl.py |
| mojeek | https://mojeek.com | general, web | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/mojeek.py |
| mojeek images | https://mojeek.com | images, web | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/mojeek.py |
| mojeek news | https://mojeek.com | news, web | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/mojeek.py |
| moviepilot | https://www.moviepilot.de | movies | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/moviepilot.py |
| national vulnerability database | https://nvd.nist.gov | it | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/nvd.py |
| naver | https://search.naver.com | general, web | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/naver.py |
| naver images | https://search.naver.com | images | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/naver.py |
| naver news | https://search.naver.com | news | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/naver.py |
| naver videos | https://search.naver.com | videos | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/naver.py |
| neosearch | https://neosearch.org | general | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/neosearch.py |
| rubygems | 实例/站点需核对 | it, packages | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| peertube | https://joinpeertube.org | videos | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/peertube.py |
| mediathekviewweb | https://mediathekviewweb.de/ | videos | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/mediathekviewweb.py |
| yacy | https://yacy.net/ | general | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/yacy.py |
| yacy images | https://yacy.net/ | images | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/yacy.py |
| rumble | https://rumble.com/ | videos | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/rumble.py |
| reloado | 实例/站点需核对 | general | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| repology | https://repology.org | packages, it | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/repology.py |
| resulthunter | https://resulthunter.com | general | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/resulthunter.py |
| resulthunter images | https://resulthunter.com | images | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/resulthunter.py |
| searchch | 实例/站点需核对 |  | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| searchzee | https://searchzee.com | general | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/searchzee.py |
| searchzee news | https://searchzee.com | news | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/searchzee.py |
| startpagina | https://startpagina.nl | general | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/startpagina.py |
| startpagina images | https://startpagina.nl | images | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/startpagina.py |
| startpagina videos | https://startpagina.nl | videos | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/startpagina.py |
| startpagina news | https://startpagina.nl | news | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/startpagina.py |
| swisscows | https://swisscows.com | general | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/swisscows.py |
| swisscows images | https://swisscows.com | images | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/swisscows.py |
| swisscows videos | https://swisscows.com | videos | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/swisscows.py |
| swisscows news | https://swisscows.com | news | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/swisscows_news.py |
| wordnik | https://www.wordnik.com | dictionaries, define | HTML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/wordnik.py |
| woxikon.de synonyme | 实例/站点需核对 | dictionaries | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| tootfinder | https://www.tootfinder.ch | social media | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/tootfinder.py |
| uxwing | https://uxwing.com | images, icons | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/uxwing.py |
| voidlinux | https://voidlinux.org/packages/ | packages, it | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/voidlinux.py |
| vuhuv | https://vuhuv.com | general | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/vuhuv.py |
| vuhuv images | https://vuhuv.com | images | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/vuhuv.py |
| vuhuv videos | https://vuhuv.com | videos | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/vuhuv.py |
| wallhaven | https://wallhaven.cc/ | images | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/wallhaven.py |
| wikimini | 实例/站点需核对 | general | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| wttr.in | https://wttr.in | weather | JSON / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/wttr.py |
| xonaly | 实例/站点需核对 | general | 方式未标注 / Key 未标注 | inactive | 未维护规则 | searx/engines/xpath.py |
| xprivo | https://www.xprivo.com | general | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/xprivo.py |
| xprivo news | https://www.xprivo.com | news | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/xprivo.py |
| xprivo videos | https://www.xprivo.com | videos | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/xprivo.py |
| zapmeta | 实例/站点需核对 | general | 方式未标注 / Key 未标注 | disabled | 未维护规则 | searx/engines/xpath.py |
| braveapi | https://api.search.brave.com/ | general, web | JSON / 需 Key | inactive | 未维护规则 | searx/engines/braveapi.py |
| brave | https://search.brave.com/ | general, web | HTML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/brave.py |
| brave.images | https://search.brave.com/ | images, web | HTML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/brave.py |
| brave.videos | https://search.brave.com/ | videos, web | HTML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/brave.py |
| brave.news | https://search.brave.com/ | news | HTML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/brave.py |
| exaapi | https://exa.ai | general, web | JSON / 需 Key | inactive | 未维护规则 | searx/engines/exaapi.py |
| lib.rs | https://lib.rs | it, packages | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/lib_rs.py |
| sourcehut | https://sourcehut.org | it, repos | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/sourcehut.py |
| bt4g | https://bt4gprx.com | files | XML / 无需 Key（上游声明） | 启用配置 | 未维护规则 | searx/engines/bt4g.py |
| pkg.go.dev | https://pkg.go.dev/ | packages, it | HTML / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/pkg_go_dev.py |
| senscritique | https://www.senscritique.com/ | movies | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/senscritique.py |
| minecraft wiki | https://minecraft.wiki/ | software wikis | JSON / 无需 Key（上游声明） | disabled | 未维护规则 | searx/engines/mediawiki.py |
| sina | 实例/站点需核对 | news | 方式未标注 / Key 未标注 | inactive | 未维护规则 | searx/engines/json_engine.py |
| metacrawler | https://s1search.co | general | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/s1search.py |
| zoo search | https://s1search.co | general | HTML / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/s1search.py |
| s1search | https://s1search.co | general | JSON / 无需 Key（上游声明） | inactive | 未维护规则 | searx/engines/s1search_rampjs.py |

共 338 个待评估引擎条目，包含现有站点的新分类；完整上游条目数为 352。
