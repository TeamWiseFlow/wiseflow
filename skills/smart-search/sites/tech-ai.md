# 技术与 AI

本站点组统一使用共享 session/profile `default`；每条 Camoufox 操作带 `--persistent`。入口常量见 [site-catalog.json](../site-catalog.json)。查询模板中的 `{keyword}` 编码一次；表单入口先 snapshot，再输入并提交。所有结果取自当前网页，不调用上游的 registry、Stack Exchange 或站点 API。

| 站点 | session / profile | 搜索入口 |
|---|---|---|
| Stack Overflow | `default` | `https://stackoverflow.com/search?q={keyword}` |
| MDN | `default` | `https://developer.mozilla.org/en-US/`，使用页面搜索 |
| Gitee | `default` | `https://gitee.com/search?q={keyword}&type=repository` |
| Hugging Face | `default` | `https://huggingface.co/models`，使用名称搜索与筛选 |
| OpenReview | `default` | `https://openreview.net/`，使用站内搜索 |
| npm | `default` | `https://www.npmjs.com/search?q={keyword}` |
| PyPI | `default` | `https://pypi.org/search/?q={keyword}` |

## Stack Overflow

- 搜索完整报错或概念，可在查询中使用页面支持的标签语法，如 `[python] asyncio`；编码整个查询一次，不单独拼接未经编码的方括号或 `#`。
- 按实际页面筛选/排序提取问题标题、问题链接、标签、票数、回答数和日期。进入问题页核对问题上下文、回答时间、适用版本及采纳状态。
- 已采纳或高票只作为线索；涉及新版本行为时用对应官方文档核对，不把旧回答改写为当前版本保证。

## MDN

- 从主页搜索框或搜索按钮进入站内搜索，选择当前页面支持的语言。需要中文版时通过页面语言切换，不猜测不存在的翻译路径。
- 提取文档标题、真实文档链接和摘要；打开正文核对 API/语法定义、实验性/废弃标记、浏览器兼容性及规范链接。
- 搜索卡片没有版本/兼容字段时读取文档，不用摘要推断所有浏览器均支持。

## Gitee

- 默认搜仓库；其他类别使用实际网页控件切换，翻页使用当前下一页链接。不要复刻 `so.gitee.com` 搜索 widget 接口。
- 提取仓库名、URL、简介、可见语言、star/fork 和更新时间。打开仓库核对 README、许可证、维护状态及上游来源，区分镜像与原创项目。

## Hugging Face

- 模型使用 `/models`；数据集和应用分别打开 `https://huggingface.co/datasets`、`https://huggingface.co/spaces`。在对应列表的名称搜索框输入关键词，按实际控件筛选任务、库、语言和许可证。
- 保存 `owner/name`、仓库链接、类别、任务、许可证、可见下载/点赞和 gated 标记；打开 model card、dataset card 或 Space 页面核对用途、版本与限制。
- 模型、数据集与 Space 分开列出；下载数和点赞数保留观察时间，不直接当作性能指标。页面要求同意访问条款时按 browser-guide 处理，不代替用户提交申请。

## OpenReview

- 从站点的搜索入口提交标题、作者或关键词；会场内检索时先进入具体会场，再使用实际页面提供的搜索/筛选。不要把 notes API 参数当作网页参数。
- 提取论文标题、作者、年份/会场、forum 详情链接；打开详情核对版本、公开摘要、公开评审和页面实际显示的决定。
- 投稿、撤稿、拒稿和接收状态以详情为准；有 forum 链接不表示已接收或正式发表。不可见评审保留缺项。

## npm

- 搜索关键词或完整包名（包含 scope 时将 `@scope/name` 整体编码）。从结果进入真实 package 页面，区分相似拼写的包。
- 提取包名、当前显示版本、简介、发布时间、仓库/主页、许可证和页面可见下载量；版本要求到包详情或仓库文档核对。
- 依赖生态研究只读取信息，不安装包；无法在页面确认的传递依赖或安全状态不补写。

## PyPI

- 使用网页搜索及其实际筛选；出现浏览器验证按 browser-guide 处理，不改用 JSON/XML-RPC 或接口绕过。
- 提取项目名、项目链接、版本、简介、更新时间；详情核对 `Requires-Python`、许可证、发布历史和本次目标平台可见的 distribution 文件。
- 同名近似包按真实项目名与发布者信息区分；没有某平台 wheel 不等于项目完全不支持该平台。

源码参考：[OpenCLI 技术站点](https://github.com/jackwener/OpenCLI/tree/b06ab7780e73d3021e12e0f170086c2d55675776/clis)、[SearXNG Hugging Face](https://github.com/searxng/searxng/blob/ad46ebd7d87666edb5f116c5b274b47f689ac6cd/searx/engines/huggingface.py)、[PyPI](https://github.com/searxng/searxng/blob/ad46ebd7d87666edb5f116c5b274b47f689ac6cd/searx/engines/pypi.py)。API-only 适配器只用于核对站点与字段，浏览器入口以实际页面为准。
