# LinkedinApis 源码复核与测试

**当前决定（2026-10-12）：用户要求暂缓本轮探索、修复与接入，等待上游实质进展后再复核。抓包协作和真实请求测试到此停止，保留现有原型、补丁及测试证据。下文的补测/抓包步骤是恢复工作时的参考，不是当前待办。**

2026-10-12。审阅对象：[cv-cat/LinkedinApis](https://github.com/cv-cat/LinkedinApis)，完整参考 clone 位于 `/home/ctyun/wiseflow-pro/LinkedinApis`。首轮审阅后，用户授权尝试修复和探索能力；修复位于该参考仓的 `exploration/linkedin-20261012` 工作分支，尚未接入现役技能或部署服务。

源码基线：`f221e49a026a0556b06783e6927b3c432b890d4d`。最新提交为 2026-08-18 的 README 修改；业务代码和 `static/Linkein.js` 最后修改于 2026-04-10。6 个历史提交中，6 月、7 月、8 月的三次提交均只修改 README，不能把 8 月 README 更新视为接口适配更新。

## 结论

本地 `static/Linkein.js` 是 UUID 格式转换代码，用于发送消息的 `trackingId`；它不是请求签名，也不是结果解析器。该逻辑可以用 Python 标准库替代，无需为它保留 Node/PyExecJS。

项目可作为 LinkedIn 私有网页接口的参考，但原样集成前需要修复明确的打包、编码和解析问题。首轮无登录态；用户随后提供 Cookie 的补测曾确认登录身份，但原 queryId 发现未成功，个人资料读取也未完成。至少当前账号的这条原样读取链路没有验收通过，不能认定所有 Voyager 接口已经失效。

## 修复与能力探索（用户授权后的最新状态）

探索补丁仅保存在仓外参考区：`~/wiseflow-pro/linkedin-apis-exploration-20261012/exploration.patch`，对应上游基线 f221e49，不随产品仓库或安装包分发。补丁保存 11 个源文件变更，已在干净基线 worktree 执行 `git apply --check`。修改没有提交/推送，用户 Cookie 和原始私人响应不在补丁中。

| 能力 | 当前真实验证 | 本轮实现/修复 | 下一步缺口 |
|---|---|---|---|
| 会话身份 `get_me` | 早前真实200并确认身份；修复版复测遭302 | 增加标准入口；必须同时有有效JSON和身份字段，避免仅凭Cookie/HTTP200判成功 | 当前浏览器的成功请求/UA，用于核对请求层 |
| queryId 发现 | 已登录首页/14个公开资源曾200，但没有旧模块/搜索queryId | 搜索所有script src，不依赖nonce；兼容旧模块属性顺序及存在于资源中的新版queryId字符串；缺项明确报告 | 当前搜索请求入口、queryId/variables或SDUI数据格式 |
| GraphQL `search_some` | 没有当前queryId，未调用平台搜索 | 修复原查询的Rest.li嵌套值与外层URL编码、起始参数校验 | 成功的搜索请求，确认当前变量结构；本地构造通过不等于平台接受 |
| 人员搜索 `search_people` | 新增网页读取候选，真实请求302 | 在HTTP HTML中提取主结果区的人员链接/名称，去重，限制10条；不伪造headline/地区 | 成功的搜索页面或数据请求；尚未实号验证解析 |
| 个人资料 `get_user_info` | 修复版真实个人页请求302 | 移除UUID/vendor/固定included位置依赖；优先按目标身份读取页面内结构化数据，其次读取可见姓名/About；缺字段标明 | 成功的个人页/基本资料/About响应；headline可能缺失 |
| 公司/学校 `get_company_info` | 新增候选，真实公司页请求302 | 结构化Organization/Corporation数据或可见标题读取，校验落地页面，保留字段缺口 | 成功公司页响应，不把页面中的其他公司当作目标 |
| 消息上下文 `get_send_msg_info` | 尚无当前消息窗口的成功响应 | 唯一sender/recipient提取，不再盲取第一个URN；多候选或缺项明确拒绝 | 消息窗口初始化的只读请求，验证mailbox/recipient/topic |
| `send_msg` | 未真实发送 | 修复trackingId和原请求结构的预览；返回sent=false，confirm=true也拒绝发送 | 当前写请求、明确测试对象/内容和收据校验，之后再实现发送 |

独立可修部分已经落地：纯Python UUID转换、Cookie解析/CSRF、Rest.li与URL编码、有限超时/请求预算、循环重定向/错误Content-Type识别、静态资源凭据隔离、精确资料/公司身份核对、FastAPI方法白名单与结构化错误，以及App.py/5011启动入口。默认监听localhost，实验curl后端和真实UA由环境变量选择；没有失败后自动切换客户端。

**测试：34项离线回归通过**，覆盖真实问题的构造/解析、错误身份拒绝、Cookie/CSRF、重定向有界停止、静态资产不带凭据、消息上下文歧义拒绝、预览不发请求与服务错误输出。它们不是34个已通过的LinkedIn平台接口。App.py的CLI帮助入口正常；未构建Docker镜像。

复测真实请求时，`get_me`、个人页、公司页、人员搜索分别尝试一次，均得到HTTP302，修复版返回`REDIRECT_LOOP`而不再生成IndexError/无限重试。去掉路由/其他浏览器Cookie、使用curl_cffi Chrome传输的控制测试也未消除302。响应Server为Cloudflare，Set-Cookie更新`__cf_bm`；这纠正了此前仅根据重定向推测普通路由Cookie的方向，但仍不能确定拒绝原因或认定账号失效。

公开JS的独立复核：14个资源都可匿名HTTP200下载；无原固定搜索模块，也无本次匹配的`voyagerSearchDashClusters.<hash>`。其中发现`/voyager/api/voyagerSearchDashSearchHome`、`/voyager/api/voyagerSocialDashNormComments`等路径线索。前者是搜索首页线索，不能当作人员搜索；路径存在不能证明参数/权限/接口实号可用，因此本轮不启用这些额外API。

后续恢复时先对照上游基线f221e49的业务/协议变化；若仍需浏览器成功请求，所需字段留在 [浏览器调试说明](linkedin-browser-capture.md)，届时再按实际缺口收集。读取能力后续归具体`linkedin-hunter`，经验证的互动/联络工具归`expert-bd`；当前暂缓接入，保留探索分支。

用户随后提供的200样本是 `/tscp-serving/dtag`，其响应明确含 `LinkedIn Follow Company`、`sponsoredAccount`、`sponsoredCreative` 与 `SAS_DYNAMIC_AD_FOLLOW_COMPANY`，属于搜索页面的关注公司广告。不能据参数 `z=search_people` 判定它是人员搜索接口；没有重放广告/点击/追踪请求，也不保存该响应的个人字段与追踪串。页面URL为 `/search/results/all/`，未取得真正的人员搜索成功请求；用户现已决定暂缓抓包。

测试与脱敏结果：`test/linkedin-apis/test_repairs.py`、`repair-regressions.json`、`verify_repaired_live.py`、`repaired-live-results.json`、`transport-results.json` / `transport-curl-results.json`、`public-assets-analysis.json`。最初audit/authenticated脚本记录上游未修复基线的历史证据，当前探索分支不再按旧脚本的实现假设重跑。

## 用户 Cookie 补测（2026-10-12）

Cookie 仅从用户在本会话提供的内容读入测试进程内存；不落凭据文件、不导入 Camoufox profile、不使用上游 `.env`。脱敏结果在 `test/linkedin-apis/authenticated-results.json` 与 `authenticated-detail-results.json`。静态资源请求不携带 Cookie 或 CSRF；没有发送真实消息。

| 检查 | 实际观察 | 可得结论 |
|---|---|---|
| 会话身份 | 首次 `/voyager/api/me` HTTP 200，返回 normalized JSON 的 data/included，有身份字段 | 用户提供的 Cookie 至少在该次请求中有效；不是单凭 li_at 存在推断登录 |
| 原 queryId 发现 | 已登录首页 HTTP 200，非登录页；其 14 个 JS 资源均 HTTP 200，原 `get_search_query_id` 返回 None | 原函数未在这批资源中找到固定的 `search-cluster-collection.graphql` 模块，发现链路失败 |
| 首页结构 | 页面有 SDUI 标记；资源路径为 `/aero-v1/sc/h/assets/*.js`，没有源码依赖的旧 UUID、memberRelationship 与 vendor/fastboot 标记 | 当前账号返回的资源结构与旧实现假定不同；不能由此推广到所有账号或宣称 GraphQL 已被取消 |
| 原 GraphQL 搜索 | 没有取得 queryId，所以没有发起 `search_some` 平台请求 | 搜索未验收；不能写成“GraphQL 搜索接口已经返回错误/失效” |
| 个人资料读取 | 后续页面请求收到 HTTP 302，Location 指向同址；有界处理后原 `get_user_info` 抛 IndexError | 原实现缺少状态与缺项处理；未取得成功的资料页面，尚不能单独判定个人资料 API 已失效 |
| 搜索网页与消息能力 | 人员搜索网页同样出现同址 302，未取到结果；没有发送消息 | 未验证浏览器网页替代方案或真实消息发送能力 |

第一次发现流程先读取身份与首页，再下载 14 个公开资源。最初测试请求预算没有为后续个人页预留空间，导致该项只产生测试脚本预算异常；该结果不作为上游故障证据。补测另外分配网页请求预算并限制重定向，得到上表 HTTP 302/IndexError。

同址重定向的初版处理没有正确沿用服务端路由 Cookie；测试脚本已改为内存会话、吸收 Set-Cookie，并禁止无限重定向。此后仍见同址 302，原因未确认；不继续重复请求，不将其归因为账号失效、风控或接口取消。

**接入判断：原项目至少需要重新适配当前资源发现与响应处理，再完成只读验收；本轮没有直接移植技能。** UUID/trackingId 的结论不变：它是格式转换，不是签名。

## JS 的实际调用链

1. `send_msg()` 生成 UUID v4，将 UUID 原字符串填入消息的 `originToken`。
2. `generate_trackingId()` 通过 PyExecJS 调用本地 JS 的 `Fl(uuid)`。
3. `Fl` 调用 UUID 校验/解析函数，把 UUID 转为 16 个字节，再逐字节 `String.fromCharCode` 拼成长度 16 的字符串。
4. 返回字符串被放入发送消息 JSON 的 `trackingId`；没有私钥、摘要算法、请求正文参与或结果解析逻辑。

针对程序生成的合法 UUID v4，其输出等价于 `uuid.UUID(value).bytes.decode("latin-1")`。JS 校验器还会检查 UUID 格式/版本；替代时保留合法输入约束。

**本地 JS 和远端 JS 分开看**：搜索/主页需要的 GraphQL `queryId` 是 Python 下载 LinkedIn 页面引用的远端 `static.licdn.com` 资源后，通过正则提取已有的查询标识；不是本地 JS 计算的签名。响应则在 Python 中用 `.json()` 和字段路径处理。

变量命名 `sign_js` 不能作为签名证据；同一工具文件中的 `generate_requests_params()` 调用 `generateRequestParams`，而本地 JS 并未定义该函数。此 helper 在已审阅业务代码中没有调用点，不应误认为已经实现一套通用签名机制。

源码：[UUID 转换](https://github.com/cv-cat/LinkedinApis/blob/f221e49a026a0556b06783e6927b3c432b890d4d/static/Linkein.js)、[Python 桥接](https://github.com/cv-cat/LinkedinApis/blob/f221e49a026a0556b06783e6927b3c432b890d4d/utils/link_utils.py)、[实际业务调用](https://github.com/cv-cat/LinkedinApis/blob/f221e49a026a0556b06783e6927b3c432b890d4d/link_apis.py)。

## 能力范围（首轮验证，认证补测以上表为准）

| 方法 | 实现范围 | 本轮验证状态 |
|---|---|---|
| `get_search_query_id` | 读取登录页面引用的 JS，以固定模块名提取搜索 queryId | 原格式夹具成功；真实无登录态页面没有 queryId |
| `search_some` | 调用 Voyager GraphQL 搜索，`resultType=ALL`，返回原始 JSON | 本地请求构造验证；未进行登录后平台调用 |
| `get_user_info` | 从个人页面提取身份/资源信息，查询姓名、headline、About | 原数组布局夹具成功；真实无登录态请求受阻 |
| `get_send_msg_info` | 从企业/学校页面 HTML 提取 mailbox/recipient 信息 | 代码审阅，未做实号验证 |
| `send_msg` | pagesMessaging 消息创建请求；面向企业/学校主页 | UUID 与桥接逻辑离线验证；未发送真实消息 |

这不是完整 LinkedIn 采集/互动 SDK。搜索返回值没有归一化为人员列表；公司/学校主页消息也不能直接认定为普通成员之间的私信。没有从此项目证明职位搜索、发帖、评论、好友邀请等能力。

Cookie 和 CSRF 依赖有效登录态：公共请求头从 `JSESSIONID` 去掉引号后生成 CSRF header；主页方法还要求原始 Cookie 字符串存在带双引号的 `JSESSIONID`。项目没有登录流程、会话持久化或失效恢复封装。

## 已复现的问题

| 问题 | 本地证据 | 影响与处理方向 |
|---|---|---|
| JS 桥接 cwd 指向不存在的 `static/node_modules` | 原样 `generate_trackingId()` 抛 `FileNotFoundError`；仅在内存中将 cwd 改为存在的 `static` 后相同 JS 成功 | 原始消息请求会在构造 payload 时失败；可移除无必要的 Node 桥接 |
| npm 安装指导缺少 manifest | `static/package.json` 及其他 npm manifest 不在仓库中 | README 的安装说明不完整；本地 JS 实际没有外部 npm 依赖 |
| Docker 启动入口错误 | CMD 为 `python main.py`，文件不存在；同样命令退出码 2 | 实际入口为 `App.py`；EXPOSE 5000 与服务默认 5011 也不一致。未构建镜像 |
| 查询字符串缺少编码 | 通过原 `search_some` 和 requests 的请求准备过程，`R&D (AI), C++` 无法作为完整关键词保留 | 修复外层 URL 编码，并分别确认 Voyager variables 内部语法的转义；不能只替换空格 |
| Cookie 分隔过严 | `li_at=synthetic;JSESSIONID="synthetic-csrf"` 无空格时请求头构造抛 `KeyError`；标准分隔样本成功 | 用可靠 Cookie 解析，校验缺失字段并报告登录失效 |
| queryId 提取依赖固定 bundle 格式 | 原模块名、nonce 和属性顺序夹具成功；去掉 nonce 返回 None，交换 id/typeName 顺序抛 `IndexError` | 这是人工兼容性夹具，不代表当前登录网页已经变化；需核对当前资源结构并处理缺项 |
| 主页结果依赖固定数组下标 | 同样实体移动 included 数组位置后，About 抛 `KeyError('topComponents')`、姓名/headline 抛 `KeyError('headline')` | 不以 `included[14]` / `[4]` 定位实体；按实体类型、URN 与引用关系读取，并允许 About 缺失 |
| 未使用 helper 的 JS 函数缺失 | 在有效 cwd 下调用 `generate_requests_params` 抛 `ReferenceError` | 删除无调用点 helper，不能按函数名宣称存在通用签名 |

源码还显示所有 HTTP 请求未设 timeout、未在解析前检查状态/Content-Type，多处正则直接 `[0]`，错误页易表现成解析异常。首页 queryId 请求和主页 JS 资源请求也没有一致传递 proxies；UA/clientVersion 是硬编码的旧浏览器/网页版本。上述为源码风险，不当作已实测的当前平台拒绝原因。

源码：[接口实现](https://github.com/cv-cat/LinkedinApis/blob/f221e49a026a0556b06783e6927b3c432b890d4d/link_apis.py)、[Cookie/URL 工具](https://github.com/cv-cat/LinkedinApis/blob/f221e49a026a0556b06783e6927b3c432b890d4d/utils/link_utils.py)、[Dockerfile](https://github.com/cv-cat/LinkedinApis/blob/f221e49a026a0556b06783e6927b3c432b890d4d/Dockerfile)。

## 首轮测试证据与边界

- 测试脚本与结果在仓根忽略目录 `test/linkedin-apis/`；依赖只安装到其中独立 `.venv`，未修改产品依赖、上游源码、运行配置或账号状态。
- Python 3.12.3 / Node v26.8.2 环境下执行 18 项离线检查：8 项成功，10 项暴露问题或兼容性约束。这里包括人为改动 bundle/数组布局的夹具，不能把该比例解释为平台接口成功率。
- 4 个合法 UUID 样本（含大小写、零 UUID）与 Python UUID 字节结果一致，无效 UUID 被拒绝；本地 FastAPI ASGI 只读路由在 mock 下正常返回 200。这不等于已成功调用 LinkedIn。
- 真实请求首页返回 HTTP 200，但标题为“领英: 登录或注册”，没有 `script[nonce]`，原 `get_search_query_id` 返回 None。
- 真实请求 README 中的个人页示例返回 HTTP 999，没有源码依赖的页面字段，原 `get_user_info` 抛 `IndexError`。这只能证明本轮无登录态访问未成功，不证明该个人页不存在或登录后 API 已失效。
- 本机没有 `~/.camoufox-cli/profiles/linkedin`。未读取其他平台 Cookie，未使用上游 `.env` 中的登录材料；没有真实搜索/资料查询的认证验收，也没有发送消息。

复现入口（依赖已在隔离 venv 中安装）：

```bash
test/linkedin-apis/.venv/bin/python test/linkedin-apis/audit.py --network
```

后续适配的只读验收应覆盖：使用明确的当前会话并核对真实 UA，适配当前网页资源的 queryId 发现或经确认的读取入口；验证单页简单关键词搜索、带中文/特殊字符的搜索及一例有/无 About 的个人资料读取。浏览器路径必须使用固定 `linkedin` 持久 profile；本次用户 Cookie 仅用于 HTTP 补测，不自动导入该 profile。记录状态、真实字段和缺项，Cookie/响应中的私人字段不写日志。发送消息需要另外指定测试收件页面和消息内容，本轮未授权这一外部写操作。

## 与现有架构的关系

目前保留公共 `smart-search` 的 LinkedIn Camoufox 搜索规则。若后续决定移植，搜索/资料读取应新增具体 `linkedin-hunter` 技能；pagesMessaging 写操作归 `expert-bd` 的具体工具。`expert-osbi` 继续只编排专业提取/跟踪/分析，不内置这组 HTTP 接口。

本机 catbus 参考基线 `7739ed22` 的平台文档与实现未见 LinkedIn；没有可沿用的 LinkedIn 实号验收记录，不能借用其他平台“已测试”状态。
