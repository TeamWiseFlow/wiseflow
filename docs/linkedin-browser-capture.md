# LinkedIn 浏览器调试材料

当前已按用户决定暂缓，等待上游进展；不需要继续抓取。本说明留作以后恢复时确认请求入口/参数的参考，届时按实际缺口选择材料。

## 1. 人员搜索（先做这一项）

1. 在平时能够正常使用领英的浏览器中打开开发者工具，进入 Network，清空旧请求并勾选 Preserve log。
2. 搜索一次 `engineer`，切到人员结果；等待真实结果出现。
3. 查看 Fetch/XHR 中承载搜索结果、返回200的请求。若没有对应 XHR，查看 Doc 分类中的搜索页面请求；新版页面可能直接返回渲染内容。
4. 提供该请求的完整 URL、Method、Query String / Request Payload、Content-Type，以及请求使用的 User-Agent。保留 `queryId`、`variables`、`x-li-*` 等结构与字段；Cookie 不需要重复粘贴。
5. 响应只需要一小段字段结构，保留键名、嵌套层级和数据类型。姓名、个人标识、联系方式替换为示例值；如果响应是 HTML、流式文本或二进制，先提供 Content-Type 与 Preview 中显示的格式，不必转成 JSON。

选择请求时按响应内容判断，不以200或URL参数含`search_people`判断：

- `/tscp-serving/dtag` 是本次已确认的广告请求。响应包含 `LinkedIn Follow Company`、`sponsoredAccount`、`sponsoredCreative`、`SAS_DYNAMIC_AD_FOLLOW_COMPANY` 或广告追踪字段时排除；不需要重放该请求或解析其trackingCode。
- 当前页面URL应是 `/search/results/people/`；`/search/results/all/` 是全部结果。先点“人员”，清空旧请求后刷新，避免从全部结果页的广告流中选错。
- 可先按请求名中的 `graphql`、`voyager`、`flagship-web`、`search` 查找候选，但必须打开Response/Preview，确认其包含中间结果区的人员资料链接/姓名/职位，或承载这些结果的结构化/渲染数据。
- 如果Fetch/XHR没有结果数据，选择Doc中路径为 `/search/results/people/` 的主文档请求。如果仍无法判断，先提供这次导航产生的请求Name列表与类型，不必粘贴每条完整响应。

如果方便使用 Copy as cURL，可粘贴移除 Cookie/Authorization 后的请求，外加响应的字段结构。客户端会使用此前明确提供的会话；若成功请求使用不同的临时会话字段，再具体核对。

若浏览器Network显示Remote address为本机代理（如127.0.0.1端口），这也是对照两端网络出口的线索；浏览器本机的localhost地址不能直接作为远端测试服务器的代理地址。

## 2. 自己的个人页

打开自己的个人页，并展开 About/关于。提供负责载入基本资料和 About 的成功请求，字段要求同上。需要区别基本资料与 About 是否同一个请求，以及当前页面是 GraphQL、Rest.li JSON 还是 SDUI 渲染数据。

## 3. 消息读取/收件上下文

打开已有会话或企业页的消息窗口，提供负责加载会话、收件方和输入框上下文的只读请求。只需字段结构、URL/Method/Payload，不需要消息正文。此项用于核对 mailbox/recipient/topic，打开窗口即可，不用发送测试消息。

如果之后要验证真实发送，需要另行明确一个测试收件对象和具体消息；当前补丁只生成旧请求结构的预览，真实发送保持未实现状态。
