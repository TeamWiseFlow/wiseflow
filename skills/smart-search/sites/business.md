# 商业与行业

本站点组统一使用共享 session/profile `default`；每条 Camoufox 操作带 `--persistent`。入口常量见 [site-catalog.json](../site-catalog.json)。`{keyword}` 按 URL 参数或路径片段编码一次；页面筛选、翻页和权限以实际界面为准。

| 站点 | session / profile | 搜索入口 |
|---|---|---|
| 36氪 | `default` | `https://www.36kr.com/search/articles/{keyword}` |
| 招标剑鱼 | `default` | `https://www.jianyu360.cn/jylab/supsearch/index.html?keywords={keyword}&selectType=title&searchGroup=1` |
| 国家法律法规库 | `default` | `https://flk.npc.gov.cn/index.html`，使用页面搜索表单 |
| 1688 | `default` | `https://s.1688.com/selloffer/offer_search.htm?charset=utf8&keywords={keyword}` |

## 36氪

- 默认搜索文章；用户指定公司或机构时通过页面实际可用的类别切换，不把文章搜索误作企业数据库查询。
- 等待结果卡片挂载，提取标题、文章真实链接、作者/来源、摘要和可见发布时间。打开原文核对公司名、融资轮次、金额和事件日期；转载发布时间与事件日期分别记录。
- 以文章链接去重，排除广告/推荐位；只收录本轮可见文章，不能据搜索条数推算行业规模。

## 招标剑鱼

- 默认模板按标题搜索。需要全文、地区、行业、公告类型或时间范围时操作实际筛选控件，记录最终条件；不要把上游接口的类型码当作网页参数。
- 提取公告标题、详情链接、地区、公告类型、发布时间、招标/采购单位；金额和截止时间到详情核对。分别标记招标公告、更正公告和中标/成交结果。
- 详情存在原始采购平台链接时保存该链接，并核对是否为同一项目；预算、最高限价和中标金额分别记录。
- 登录/会员限制按 browser-guide 处理；摘要不含联系方式时保留缺项，不把遮挡字段猜成完整联系人。

## 国家法律法规库

- 在首页真实搜索框输入名称或关键词并提交；用页面控件选法规类型、公布机关、效力状态和日期。通过 snapshot 定位控件，不执行内部 Vue router 或复刻接口请求。
- 提取文件全名、详情链接、文件类型、公布机关、效力状态、公布日期、施行日期。状态未显示时打开详情核对，仍不可得则标记缺项。
- 同名文件按公布/修订版本区分；引用条文时读取正文并保存条号。发布日期和施行日期不得混用。

## 1688

- 使用 `default` profile；登录和验证按 browser-guide 执行。按页面实际控件筛选地区、供应商、规格、起订量和排序，不套用接口参数。
- 提取商品名、真实商品链接、店铺/供应商、规格、展示价格及币种、阶梯价、起订量和发货地；打开详情核对价格适用数量与规格。
- 批发报价、优惠后价和运费分别记录；“已售”等页面指标保留原名称和观察时间，不推算供应商总收入。

源码参考：[OpenCLI 36氪](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/36kr/search.js)、[剑鱼](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/jianyu/search.js)、[法规库](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/gov-law/search.js)、[1688](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/1688/shared.js)。只使用网页导航与可见 DOM。
