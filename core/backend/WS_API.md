# WebSocket API 使用文档

## 概述

WiseFlow WebSocket API 提供前端与后端的实时通信能力，支持两个核心场景：
1. 运行时信息/异常即时推送给用户
2. 需要用户配合操作时的交互确认机制

**消息模板设计**：
- 采用消息模板编码 (`code`) + 参数 (`params`) 的设计模式
- 前后端约定固定的消息模板，通过 `code` 映射对应模板
- 使用 `params` 传递动态内容，仅支持 list 格式
- 0号 消息模板比较特殊，它的 params 里面每一个都是一个消息模板代码，需要挨个二次对应消息模板，并填充。这是专门给 task 任务error_message消息用的。
- 这种设计便于国际化、消息统一管理和维护

## 连接信息

- **连接路径**: `/ws`
- **协议**: WebSocket
- **默认端口**: 8077 (可通过环境变量 `WISEFLOW_BACKEND_PORT` 配置)

## 消息模板列表

消息统一包含两个参数：

    - msg_code, 对应不同的消息模板，前端可以灵活更换或更新模板（为后续的多语言界面以及个性化、第三方插件做基础）

    - params，是个 list，list 内每个元素都是 str，用于按顺序替换到模板里面的占位符

一共有两种消息：

    - 0~99：通知消息，建议以集中的通知栏等非打扰形式，序号越大越严重（info/warning/alart), 建议前端可以用不同形态（比如颜色展示）

        **但这里面有个特殊类型，即 0号消息模板**
        
        该模板用于任务执行后的异常总结（考虑到任务执行时我们建议用户不要同时操作电脑，且wiseflow 任务大概率是定制执行，对于任务执行中的报警信息，我们不会即时反馈，而是在任务全部执行后合并展示给用户）

        0号模板，对应不固定数量的 params，其中每个元素，其实也是一个 code（但是 str），需要根据下表（task error msg code）逐一查出对应的消息内容，然后拼接出来（这也是为了便于灵活调整以及多语言）

    - 100~199：需要用户反馈的，比如需要用户手动操作过验证或者给登录，执行好之后需要点一下通知（前端需要拿到用户操作后回发 usr_ack）。 **这类消息建议做成弹窗形式**

**下面列出的消息模板前端（或者未来的 CUI、上层 Agent 等）可以直接用，也可以根据同样的意思换成自己的语言和描述**

**0号消息模板例外，此消息级别为 warning**

### 0~99号即时 notify

| level | msg code | text template         | number of params |
|----------|----------|----------------------|------------------|
| warning | 0        | 任务执行中发现如下问题，可能影响最终结果质量，建议您及时检查相关设置：\n   | (该模板接收参数不定量，参数中每一个都是10~99号消息，需要二次对应后，拼接)              |
|info| 1       | 任务#{} 执行完成，总耗时 {} 分钟，累计发现 {} 个链接（含社交媒体帖子或创作者页面），其中 {} 个抓取失败，最终提取出有效信息 {} 个(任务使用 {} 模型， 总共调用 {} 次) 。  | 7               |
|info| 2     | wiseflow 即将开始任务执行，本次执行涉及如下任务 #{} | 1        |
|info| 3     | {} 时间段工作已结束，共处理 {} / {} 个任务 | 3     |
|info| 4     | 预检完成，定时工作已编排，最近一次工作预计将于 {} 开启，请在此之前至 “任务中心” 新建或更新任务| 1   |
|info| 5    | 将检测 {} 站点登录状态，期间程序会自动打开网页，请不要关闭，如需要您配合登录，请按提示操作。（请放心程序不会读取您的登录信息，只会在本地保留您的登录状态）| 1   |
|info| 6     | 您尚未为任务#{} 配置任何信源或搜索源，该任务本次将被略过| 1 |
|info| 7     | {} {} 时段没有符合条件可执行的任务 | 2 |
|info| 8     |任务#{} 存在待用户解决的问题，执行质量可能受影响| 1 |
|info| 9     | 代理{}:{}, 已针对 {} 平台失效或过期 | 3  |
| warning | 10   | {} 平台备用登录信息 {} 已失效，请删除，避免后续干扰  | 2    |
| warning | 11   | 任务{} 状态更新失败   | 1          |
| warning | 12  | 未得到您的确认或输入，程序运行可能会受影响   | 0        |
| warning | 13   | 遭遇网络异常，任务执行将受影响，请您确保本机网络连接正常。\n确认后请退出并再次启动 wiseflow 本地程序。 | 0        |
| warning | 14 | 打开页面 {} 超时，请您确保本机网络连接正常| 1            |
| warning | 15 | 请求 {} 内容失败，请您确保本机网络连接正常| 1            |
| warning | 16 | 预登录站点 {} 登录态检测失败，但您已确认登录或长时间未操作，相关信源抓取可能受影响| 1            |
| warning | 17 | {} 平台登录操作未能及时处理，相关信源获取可能受影响 | 1      |
| warning | 18 | {} 平台风控验证未能及时处理，相关信源获取可能受影响  | 1       |
| warning | 19 | {} 平台多次尝试依然无法获得有效登录信息，相关信源获取可能受影响  | 1       |
| warning | 20 | {} 平台触发验证页，请按程序提示手动过验证（请放心程序不会读取您的登录信息，只会在本地保留您的登录状态）| 1      |
| warning | 21 | {} 平台当前使用登录信息可能已被风控， 请按程序提示更换账号后重新登录（请放心程序不会读取您的登录信息，只会在本地保留您的登录状态）| 1       |
| warning | 22 | {} 平台本地保存登录态（含备用登录信息）均已失效或不存在，请按程序提示重新登录（请放心程序不会读取您的登录信息，只会在本地保留您的登录状态）  | 1       |
| warning | 23 | 已无法从 {} 获取有效代理，请联系供应商或检查相关配置  | 1       |
| warning | 24 | 已无法从 {} 获取有效代理，请联系供应商或检查相关配置  | 1       |
| warning | 25 | 注意：任务执行时不建议用户同时操作电脑。\n期间程序会自动打开浏览器页面进行内容抓取，请不要手动关闭这些浏览器标签，抓取完成后程序会自动清理。\n部分页面可能需要您配合重登录或过验证操作，请留意控制台页面。  | 0      |
| warning | 26 | "⚠ {} {} 时段任务执行超时, 取消所有未完成的任务" | 2    |
|alart| 70 |  无法连接本地 Google Chrome浏览器\n请至 https://www.google.com/intl/zh-CN/chrome/ 下载正版 Google Chrome浏览器，并确保安装至默认位置。\n完成后请退出并再次启动 wiseflow 本地程序。| 0   |
|alart| 71 |  微信公众号 {} 不存在，请调整相关信源设置  | 1 |
|alart| 72 |  任务 {} 存在待用户解决的错误：{}，跳过"  | 2 |
|alart| 73 |   {} 平台获取程序初始化失败，相关信源已失效，请留意相关提示或提供备用登录信息 | 1 |
|alart| 74 |   未能成功启动 web 获取器，请检查相关配置以及系统设定 | 0 |
|alart| 80 |任务#{} 存在待用户解决的致命错误：{}, 无法执行| 2 |
|alart| 88 | 任务#{} 因请求 wiseflow 服务器频繁失败，已提前终止。（可能是网络原因，如后续任务中此报警频繁出现或始终没有提取出来的 infos，请联系技术支持）|1   |
|alart| 89     |  提取解析异常。请记录如下信息并反馈至技术支持 \n {} | 1       |
|alart| 92        |  未成功启动任何获取器，{} - {} 时段工作无法启动，涉及如下 task：#{}， 请仔细核查相关配置 | 3   |
|alart| 91        |  wiseflow 本地程序版本过低，请重新下载（≥4.29） | 0  |
|alart| 93        |  因无法连接 wiseflow 服务器，{} - {} 时段工作无法启动    | 2        |
|alart| 94        |  账户大模型使用额度已耗光或订阅过期，请续购后重试。 | 0   |
|alart| 95        |  账户状态异常，可能需要重新登录。     | 0              |
|alart| 96        |  wiseflow-pro 目前只针对订阅用户，请切换订阅账户登录后重启本地程序   | 0         |
|alart| 97        |  账户大模型使用额度已耗光或订阅过期，请续购后重试。任务#{} 提前终止    | 1                |
|alart| 98        |  账户状态异常，可能需要重新登录。任务#{} 提前终止     | 1              |
|alart| 99        |  wiseflow-pro 目前只针对订阅用户，请切换订阅账户登录后重启本地程序\n任务#{} 提前终止     | 1          |

### 100~199号 prompt消息

| msg code | text template         | number of params |
|----------|----------------------|------------------|
| 100       | 尚未启用任何信源，请至 系统配置 - 信源启用配置 中进行配置 | 0 |
| 101       | 尚未配置任何任务，请至 任务中心 中进行配置 | 0 |
| 102       | 确认已在打开的 {} 浏览器页面完成登录或验证 | 1 |
| 103      | 预登录域名设定：{} 不合法，请至 系统配置 - 需要预登录的站点 中更正（将在下次任务生效） | 1 |
| 113 | 请您在程序打开的 {} 页面上完成登录操作（登录后不要关闭页面，如已经是登录状态，请直接点 “我已完成”） | 1         |
| 115 | 请您在程序打开的 {} 页面上完成验证操作（完成后不要关闭页面，如已经是完成状态，请直接点 “我已完成”） | 1         |
| 116 | 请您在程序打开的 小红书 页面上 **使用手机扫码方式** 完成登录操作（登录后不要关闭页面，如确认已处于登录状态，请直接点 “我已完成”） | 0       |
| 117 |  {} 平台当前使用登录信息可能已经被风控，请您在程序打开的页面上完成账号退出操作（退出后不要关闭页面，如确认已处于退出状态，请直接点 “我已完成”） | 1             |
| 180       | 无法正确启动代理系统，程序将以无代理模式运行 | 0 |
| 181      |  mp 平台登录请选择微信公众号账号（纯小程序账号无效）  | 0   |
| 196 | 无法连接本地 Google Chrome浏览器，wiseflow 本地程序将退出。\n请至 https://www.google.com/intl/zh-CN/chrome/ 下载正版 Google Chrome浏览器，并确保安装至默认位置后再次启动。 | 0     |
| 197       |  未成功启动任何获取器，无法执行任何任务，请仔细核查相关配置 | 0  |
| 198        |  服务器连接异常，wiseflow 本地程序将退出。请您确保本机网络连接畅通，或关注我们的运营信息。\n下次工作前请退出并再次启动 wiseflow 本地程序。   | 0    |
| 199        |  wiseflow 本地程序遭遇未知错误。请记录如下信息并反馈至技术支持 \n {} | 1       |

**绝大多数情况下，wiseflow 本地程序不会退出，因为一旦退出，前端登录这些信息，实际上也无法拿到并记录，导致后续还会提升相同的报错**

**在有限的几种不得不退出的情况下，我们都采用 prompt 消息的模式，只是为了保证用户可以看到相关信息，并有充足的反应时间，实际上此时不管是否回传确认信息，都会退出，回传确认信息会导致马上退出**

### task error msg code

| msg code | text     | 
|----------|----------|
|web_miss| 任务需要启用 web 信源（系统配置 - 信源启用配置） | 
|mp_miss| 任务需要同时启用 mp 信源和 web 信源 （系统配置 - 信源启用配置） | 
|mp_not_support| 微信公众号平台不支持输入？找人模式 | 
|mp_detail_cfg| 任务中 mp 信源详情配置不当 | 
|bili_miss| 任务需要同时启用 bili 信源（系统配置 - 信源启用配置） | 
|bili_detail_cfg| 任务中 bili 信源详情配置不当 |
|dy_miss| 任务需要同时启用 dy 信源（系统配置 - 信源启用配置） | 
|dy_detail_cfg| 任务中 dy 信源详情配置不当 | 
|ks_miss| 任务需要同时启用 ks 信源（系统配置 - 信源启用配置） | 
|ks_detail_cfg| 任务中 ks 信源详情配置不当 | 
|wb_miss| 任务需要同时启用 wb 信源（系统配置 - 信源启用配置） | 
|wb_detail_cfg| 任务中 wb 信源详情配置不当 | 
|xhs_miss| 任务需要同时启用 xhs 信源（系统配置 - 信源启用配置） | 
|xhs_detail_cfg| 任务中 xhs 信源详情配置不当(xhs 必须填入完整的创作者主页地址，地址中必须包含xsec_token 字段。) | 
|zhihu_miss| 任务需要同时启用 zhihu 信源（系统配置 - 信源启用配置） | 
|zhihu_detail_cfg| 任务中 zhihu 信源详情配置不当 | 
|focus_schema| 任务中存在着配置不当的关注点（自定义提取定义不符合规范） | 
|account_issue| 因账户状态异常（llm 调用额度耗尽），任务提前终止 | 
|network_issue| 请求 wiseflow 服务器频繁失败，任务提前终止。（可能是网络原因，如后续任务中此报警频繁出现或始终没有提取出来的 infos，请联系技术支持）| 
|mp_verify_failed| mp 平台提醒用户过验证，但用户未处理（超时或因网络问题未成功打开相关页面），相关信源结果可能受影响。| 
|mp_login_failed| mp 平台提醒用户登录，但用户未处理（超时或因网络问题未成功打开相关页面），相关信源结果可能受影响。|
|mp_account_banned| mp 平台所有用户登录信息（含备用信息）均已失效，请更换账号后重新登录。| 
|bili_account_banned| bili 平台所有用户登录信息（含备用信息）均已失效，请更换账号后重新登录。| 
|dy_account_banned| dy 平台所有用户登录信息（含备用信息）均已失效，请更换账号后重新登录。| 
|ks_account_banned| ks 平台所有用户登录信息（含备用信息）均已失效，请更换账号后重新登录。| 
|wb_account_banned| wb 平台所有用户登录信息（含备用信息）均已失效，请更换账号后重新登录。| 
|xhs_account_banned| xhs 平台所有用户登录信息（含备用信息）均已失效，请更换账号后重新登录。| 
|zhihu_account_banned| zhihu 平台所有用户登录信息（含备用信息）均已失效，请更换账号后重新登录。| 
|mp_request_failed| mp 平台存在请求失败记录，请确保相关账户状态正常、程序运行期间本机网络正常。| 
|bili_request_failed| bili 平台存在请求失败记录，请确保相关账户状态正常、程序运行期间本机网络正常。| 
|dy_request_failed| dy 平台存在请求失败记录，请确保相关账户状态正常、程序运行期间本机网络正常。| 
|ks_request_failed| ks 平台存在请求失败记录，请确保相关账户状态正常、程序运行期间本机网络正常。| 
|wb_request_failed| wb 平台存在请求失败记录，请确保相关账户状态正常、程序运行期间本机网络正常。| 
|xhs_request_failed| xhs 平台存在请求失败记录，请确保相关账户状态正常、程序运行期间本机网络正常。| 
|zhihu_request_failed| zhihu 平台存在请求失败记录，请确保相关账户状态正常、程序运行期间本机网络正常。| 
|mp_may_not_support| 任务对应的 mp 信源因平台升级可能已经不受支持，建议暂时从信源中调整出去并等待我们后续运营通知| 
|bili_may_not_support| 任务对应的 bili 信源因平台升级可能已经不受支持，建议暂时从信源中调整出去并等待我们后续运营通知| 
|dy_may_not_support| 任务对应的 dy 信源因平台升级可能已经不受支持，建议暂时从信源中调整出去并等待我们后续运营通知| 
|ks_may_not_support| 任务对应的 ks 信源因平台升级可能已经不受支持，建议暂时从信源中调整出去并等待我们后续运营通知| 
|wb_may_not_support| 任务对应的 wb 信源因平台升级可能已经不受支持，建议暂时从信源中调整出去并等待我们后续运营通知| 
|xhs_may_not_support| 任务对应的 xhs 信源因平台升级可能已经不受支持，建议暂时从信源中调整出去并等待我们后续运营通知| 
|zhihu_may_not_support| 任务对应的 zhihu 信源因平台升级可能已经不受支持，建议暂时从信源中调整出去并等待我们后续运营通知| 
|github_may_not_support| 任务对应的 github 信源因平台升级可能已经不受支持，建议暂时从信源中调整出去并等待我们后续运营通知| 
|bing_may_not_support| 任务对应的 bing 信源因平台升级可能已经不受支持，建议暂时从信源中调整出去并等待我们后续运营通知| 
|arxiv_may_not_support| 任务对应的 arxiv 信源因平台升级可能已经不受支持，建议暂时从信源中调整出去并等待我们后续运营通知| 
|no_processed_urls|任务从所提供的信源中未发现任何可能包含关注点信息的内容或链接，如果此状况持续出现，请关注信源和关注点匹配度|

## 消息格式

### 出站消息 (后端 → 前端)

#### 1. notify - 通知消息
用于信息展示，无需回传确认。

```json
{
  "type": "notify",
  "code": 0,
  "params": [1, 10, 6, 20],
  "timeout": 180,
  "ts": 1700000000.123
}
```

```json
{
  "type": "notify",
  "code": 1,
  "params": ["用户名", "5分钟前"],
  "timeout": 180,
  "ts": 1700000000.123
}
```

```json
{
  "type": "notify",
  "code": 2,
  "params": ["张三", "登录"],
  "timeout": 180,
  "ts": 1700000000.123
}
```

**字段说明:**
- `type`: 消息类型，固定为 "notify"
- `code`: 状态码，用于映射前端的消息模板；`code 0` 为 专门给 task 报警信息用的特殊消息模板
- `params`: 消息参数，仅支持 list 格式，用于填充消息模板中的动态内容
- `timeout`: 展示时长(秒)，>0 表示自动消失，0 表示需手动关闭，前端也可以忽略这个值
- `ts`: 时间戳

#### 2. prompt - 用户确认请求
需要用户操作并回传确认。

```json
{
  "type": "prompt",
  "prompt_id": "abc123def456",
  "code": 10,
  "params": ["微信公众号登录页面"],
  "actions": [{"id": "done", "label": "我已完成"}],
  "timeout": 180,
  "ts": 1700000000.123
}
```

```json
{
  "type": "prompt",
  "prompt_id": "def456ghi789",
  "code": 11,
  "params": ["example.com", "登录验证"],
  "actions": [
    {"id": "confirm", "label": "确认"},
    {"id": "cancel", "label": "取消"}
  ],
  "timeout": 180,
  "ts": 1700000000.123
}
```

**字段说明:**
- `type`: 消息类型，固定为 "prompt"
- `prompt_id`: 唯一标识符，用于关联用户回复
- `code`: 状态码，用于映射前端的消息模板；
- `params`: 消息参数，仅支持 list 格式，用于填充消息模板中的动态内容
- `actions`: 可选操作列表，每个操作包含 id 和 label
- `timeout`: 等待超时时间(秒)
- `ts`: 时间戳

#### 3. prompt_resolved - 确认完成通知
提示前端某个 prompt 已被处理完成。

```json
{
  "type": "prompt_resolved",
  "prompt_id": "abc123def456",
  "action_id": "done",
  "ts": 1700000001.234
}
```

### 入站消息 (前端 → 后端)

#### user_ack - 用户确认回复
用户点击操作后回传的确认消息。

```json
{
  "type": "user_ack",
  "prompt_id": "abc123def456",
  "action_id": "done"
}
```

**字段说明:**
- `type`: 消息类型，固定为 "user_ack"
- `prompt_id`: 对应的 prompt 标识符
- `action_id`: 用户选择的操作 ID

## 代码示例

### JavaScript 示例

```javascript
class WiseFlowWebSocket {
    constructor(url = 'ws://localhost:8077/ws') {
        this.url = url;
        this.ws = null;
        this.reconnectInterval = 5000;
    }

    connect() {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
            console.log('WebSocket 连接已建立');
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };

        this.ws.onclose = () => {
            console.log('WebSocket 连接已关闭，尝试重连...');
            setTimeout(() => this.connect(), this.reconnectInterval);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket 错误:', error);
        };
    }

    handleMessage(data) {
        switch (data.type) {
            case 'notify':
                this.showNotification(data);
                break;
            case 'prompt':
                this.showPrompt(data);
                break;
            case 'prompt_resolved':
                this.hidePrompt(data.prompt_id);
                break;
        }
    }

    showNotification(data) {
        // 根据 code 获取消息模板，使用 params 填充
        const message = this.formatMessage(data.code, data.params);
        console.log(`通知: ${message}`);
        // 实现通知UI逻辑
        if (data.timeout > 0) {
            setTimeout(() => {
                // 自动隐藏通知
            }, data.timeout * 1000);
        }
    }

    showPrompt(data) {
        // 根据 code 获取消息模板，使用 params 填充
        const message = this.formatMessage(data.code, data.params);
        console.log(`提示: ${message}`);
        // 渲染操作按钮
        data.actions.forEach(action => {
            // 创建按钮，点击时调用 sendUserAck
            console.log(`按钮: ${action.label} (${action.id})`);
        });
    }
    
    formatMessage(code, params) {
        // 消息模板映射 - 实际项目中建议从配置文件加载
        const templates = {
            0: null,  // 空模板，直接使用 params[0]
            1: '用户 {0} 在 {1} 完成了操作',
            2: '用户 {0} 执行了 {1} 操作',
            3: '正在处理 {0}，请稍候...',
            10: '请完成 {0} 后点击确认',
            11: '请在 {0} 完成 {1} 操作'
        };
        
        // code 0 为空模板，直接返回 params[0]
        if (code === 0) {
            return (params && params.length > 0) ? params[0] : '空消息';
        }
        
        let template = templates[code] || `未知消息(code: ${code})`;
        
        if (!params || !Array.isArray(params)) return template;
        
        // 替换 {0}, {1}, {2} ... 占位符
        params.forEach((param, index) => {
            template = template.replace(`{${index}}`, param);
        });
        
        return template;
    }

    sendUserAck(promptId, actionId) {
        const message = {
            type: 'user_ack',
            prompt_id: promptId,
            action_id: actionId
        };
        this.ws.send(JSON.stringify(message));
    }

    hidePrompt(promptId) {
        console.log(`隐藏提示: ${promptId}`);
        // 隐藏对应的提示UI
    }
}

// 使用示例
const wsClient = new WiseFlowWebSocket();
wsClient.connect();
```

### Python 示例

```python
import asyncio
import json
import websockets
from typing import Dict, Any

class WiseFlowWebSocketClient:
    def __init__(self, url: str = "ws://localhost:8077/ws"):
        self.url = url
        self.websocket = None

    async def connect(self):
        """建立WebSocket连接"""
        try:
            self.websocket = await websockets.connect(self.url)
            print("WebSocket 连接已建立")
            await self.listen()
        except Exception as e:
            print(f"连接失败: {e}")
            await asyncio.sleep(5)
            await self.connect()  # 重连

    async def listen(self):
        """监听消息"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self.handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("连接已关闭，尝试重连...")
            await self.connect()

    async def handle_message(self, data: Dict[str, Any]):
        """处理接收到的消息"""
        msg_type = data.get("type")
        
        if msg_type == "notify":
            await self.handle_notification(data)
        elif msg_type == "prompt":
            await self.handle_prompt(data)
        elif msg_type == "prompt_resolved":
            await self.handle_prompt_resolved(data)

    async def handle_notification(self, data: Dict[str, Any]):
        """处理通知消息"""
        code = data.get('code', 0)
        params = data.get('params')
        message = self.format_message(code, params)
        print(f"通知: {message}")
        
        # 如果有超时设置，可以实现自动消失逻辑
        timeout = data.get('timeout', 0)
        if timeout > 0:
            print(f"通知将在 {timeout} 秒后自动消失")

    async def handle_prompt(self, data: Dict[str, Any]):
        """处理用户确认请求"""
        prompt_id = data.get('prompt_id')
        code = data.get('code', 0)
        params = data.get('params')
        actions = data.get('actions', [])
        
        message = self.format_message(code, params)
        print(f"提示: {message}")
        print("可选操作:")
        for action in actions:
            print(f"  {action.get('id')}: {action.get('label')}")
        
        # 模拟用户选择第一个操作
        if actions:
            action_id = actions[0].get('id')
            await self.send_user_ack(prompt_id, action_id)
    
    def format_message(self, code: int, params) -> str:
        """格式化消息模板"""
        # 消息模板映射 - 实际项目中建议从配置文件加载
        templates = {
            0: None,  # 空模板，直接使用 params[0]
            1: '用户 {0} 在 {1} 完成了操作',
            2: '用户 {0} 执行了 {1} 操作',
            3: '正在处理 {0}，请稍候...',
            10: '请完成 {0} 后点击确认',
            11: '请在 {0} 完成 {1} 操作'
        }
        
        # code 0 为空模板，直接返回 params[0]
        if code == 0:
            return params[0] if (params and len(params) > 0) else '空消息'
        
        template = templates.get(code, f'未知消息(code: {code})')
        
        if not params or not isinstance(params, list):
            return template
            
        # 替换 {0}, {1}, {2} ... 占位符
        for i, param in enumerate(params):
            template = template.replace(f'{{{i}}}', str(param))
                
        return template

    async def handle_prompt_resolved(self, data: Dict[str, Any]):
        """处理确认完成通知"""
        prompt_id = data.get('prompt_id')
        action_id = data.get('action_id')
        print(f"提示 {prompt_id} 已完成，选择的操作: {action_id}")

    async def send_user_ack(self, prompt_id: str, action_id: str):
        """发送用户确认消息"""
        message = {
            "type": "user_ack",
            "prompt_id": prompt_id,
            "action_id": action_id
        }
        await self.websocket.send(json.dumps(message))
        print(f"已发送确认: {action_id}")

# 使用示例
async def main():
    client = WiseFlowWebSocketClient()
    await client.connect()

if __name__ == "__main__":
    asyncio.run(main())
```

## 注意事项

1. **单连接设计**: 本地单机应用，仅支持一条WebSocket连接
2. **超时处理**: prompt 消息有超时机制，默认180秒，超时后后端视为操作失败
3. **断线重连**: 连接断开后需要重新连接，不保证历史消息补偿
4. **消息格式**: 所有消息均为JSON格式，确保正确的序列化和反序列化
5. **错误处理**: 建议实现完善的错误处理和重连机制
