# WorkBuddy 开发约定

- 本目录开发小贝 main 的 WorkBuddy 适配，首个产品是单专家「自媒体获客运营专家」。所有源码、包配置、开发文档和构建入口留在本目录。
- 商业目标是让用户通过账号 DNA、小红书原生卡片生成发布、公众号诊断体验小贝，再转化 VIP Club。市场资料、首次交付与缺少 OFB_KEY 时均须保留掌柜二维码及明确会员引导；不把会员权益当作 WorkBuddy 模型赠送额度。
- 本目录不参与 OpenClaw crew 安装或 Docker 分发。合并到 `docker-distribution` 时排除 `workbuddy/`；不要通过修改原 crew 实现 WorkBuddy 行为。
- 专家包格式和本目录 `SKILL.md` 的展示字段遵循 WorkBuddy 官方规范，不生成 Codex 的 `agents/openai.yaml`，不把 WorkBuddy 专用字段回写到原 OpenClaw 技能。
- main 的已有素材加工、平台专家、BD、IR 与公共支撑技能尽量保留原工作流、脚本及资源。从零制作完整视频由用户提供成片，或交给当前 WorkBuddy 实际可用的专家/技能；不依赖 `content-producer`、IT engineer、OpenClaw gateway 或其会话工具。
- 不纳入视频号整个平台、OSBI、sales-cs-manager 和 Camoufox 依赖。其他混合技能裁剪浏览器工具，并同步修订 workflow、路由、示例和参考，不能只删脚本却留调用步骤。删除泛化重复的 xiaobei-operations，入口直接路由原生技能。
- WorkBuddy 的 wx-mp-hunter 只保留用户文章链接的 HTTP fetch、正文图片与封面下载。禁止导出 posts-list、微信客户端消息库、数据库密钥和解密代码；公众号诊断与对标用用户提供的文章链接。原 OpenClaw 技能不受此裁剪影响。
- 原生导出范围在 `native-skills.json` 声明，通过 `scripts/sync_native.py` 更新。不要手改生成的原生技能副本；适配写进同步脚本并保留来源与校验值。运行入口负责依赖、wrapper、工作空间与私有登录态隔离。
- 平台采集、发布、互动及 relay 只有接通并验收后才能声明为可用。已存在的 HTTP relay 地址不能直接当作 MCP 地址；不要配置虚构的市场专家、技能或连接器 ID。
- 回归测试及夹具放仓根 `test/workbuddy/`，按仓库约定保持 Git 忽略。生成的 ZIP 放本目录被忽略的 `dist/`。
- 保留客户端直发平台请求、relay 计算或代理既定服务的边界；凭据不进专家包、文档、示例或 Git。
- 默认 relay 必须沿用 https://relay.openclaw-for-business.com，不另建 WorkBuddy 服务。文件系统路径适配不得改写 URL/域名。
- WorkBuddy 按官方专家规范使用 agents/ 下 Markdown 正文作为系统提示词；SOUL/IDENTITY 内容由同步脚本嵌入该正文，不假设平台自动加载 OpenClaw 工作空间文件。
