# 小贝 WorkBuddy 适配

小贝 main 的单专家产品「自媒体获客运营专家」，帮助用户运营小红书、微信公众号、抖音、快手、TikTok、X 和微博等平台的账号，通过定位、创作、已有素材加工、支持的发布与互动、数据复盘实现获客。“十个同赛道账号 DNA”“小红书原生卡片生成并发布”“公众号账号诊断”是三条代表性体验入口；平台与配套能力详见市场 README 的表格。专家角色保留 main 的 SOUL/IDENTITY 身份与风格，市场和任务交付提供掌柜二维码与会员引导，转化 VIP Club。

`expert/README.md` 是市场介绍；本文件面向开发。当前包含 35 个原生技能包、2 个适配技能、392 个原生资源与任务扩展，以及 59 个逻辑命令。保留平台专家、BD、IR、已有视频加工与公共技能；整体删除视频号、OSBI、sales-cs-manager、Camoufox 和泛化运营模块。完整取舍见 [技能范围](docs/skill-inventory.md)。

## 同步与构建

从仓根依次执行：

```bash
python3 workbuddy/scripts/sync_native.py
python3 workbuddy/scripts/validate_expert.py
python3 workbuddy/scripts/build_expert.py
```

产物为 `workbuddy/dist/xiaobei-growth-0.3.1.zip`。包保留 `.codebuddy-plugin/`、脚本权限、掌柜二维码与完整资源；不包含依赖缓存、测试、用户资料或凭据。导出选择 Git 跟踪的 main/public 源文件，并加入本目录 extensions/ 的具体任务流程；保留来源、校验值与适配说明。SOUL/IDENTITY 源文件或品牌素材变化后，校验同样要求重新同步。

不要手改导出的原生副本。裁剪改 native-skills.json，宿主和工作流差异改 scripts/sync_native.py 与 scripts/adapt_workflows.py；新任务流程放 extensions/。入口提示词可直接改，改后同步以刷新角色来源与校验值。同步不改变原 OpenClaw 技能或本机部署。

## 运行与依赖

`xiaobei-runtime` 将原 wrapper 名映射为包内命令，在用户私有缓存准备执行副本和依赖。数据库、作品、DNA 与校准文件写用户选择的工作空间；账号与配置默认位于独立 `~/.xiaobei-workbuddy/`，不借用 `~/.openclaw` 或 Camoufox profile。

WorkBuddy 命令环境需 Node 22+、Python 3.10+、Bash；doctor 检查基础运行时。首次调用按需准备 Python/Node 依赖、FFmpeg/FFprobe 和 Chromium；setup --full 可预装。Python 依赖统一列于本目录 requirements.txt，Node 依赖保持原 per-skill package.json。平台 HTTP/API、relay 签名与代理边界保持原架构，OFB_KEY 等服务配置通过私有环境文件提供。

默认 relay 始终为 https://relay.openclaw-for-business.com，WorkBuddy 沿用既有会员凭证与官方服务。产品价格、权益和二维码路径在 .codebuddy-plugin/product.json；xiaobei-runtime contact 无网络地将二维码复制到用户工作空间并返回可展示的真实路径。

抖音/小红书 API 和快手 HTTP 登录保留；X/TikTok/微博移除浏览器登录，运行入口支持用户授权的私有会话文件导入，在线核验后才保存，TikTok 写操作原门槛仍保留。外部模型服务凭据和额度需要按所选技能配置，不能视为 WorkBuddy 的模型额度。

公众号采集仅支持用户提供文章链接的 HTTP 获取与正文图片、封面下载。导出时按依赖树保留 fetch 代码，移除发布列表、微信客户端消息库、数据库密钥与解密实现；账号诊断和 DNA 工作流使用用户文章链接。原 OpenClaw 的 wx-mp-hunter 保持完整能力。

## 校验与预览

```bash
python3 -m unittest discover -s test/workbuddy -v
```

测试覆盖原生记录、校准、工作空间隔离、实际视频加工、卡片出图，以及 ZIP 解压后独立运行。测试与夹具遵循仓库约定，位于被 Git 忽略的 test/workbuddy/。自动检查不等于 WorkBuddy 市场实机验收或平台账号验收；上架前还需核对技能加载、依赖安装、账号授权与真实任务，见 [实施与验收](docs/implementation-plan.md)。

Linux 隔离目录已验证全量 Python/Node 初始化、四平台运行库加载与 HTML → 长图 → PPTX → 提取流程。完成 setup --full 后，可用 `python3 test/workbuddy/check_installed_runtime.py --state /该独立状态目录` 重跑 deck 和平台离线能力清单检查；该检查不登录或请求真实平台。

`workbuddy/` 独立开发，不合入 docker-distribution，不参与现有 crew 安装和 Docker 打包。
