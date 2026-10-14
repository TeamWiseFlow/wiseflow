# WorkBuddy 开发约定

- 本目录开发小贝 main 的 WorkBuddy 适配，首个产品是单专家「自媒体获客运营专家」。所有源码、包配置、开发文档和构建入口留在本目录。
- 当前审核版只展示实际能力与必要的服务依赖。腾讯包中不得包含会员方案、服务定价、联系二维码或任务完成后的主动推广；只在当前实际步骤需要 relay 且接入未配置时，简短提示到 https://openclaw-for-business.com/ 查看接入方式。已有凭证不重复提示，本地内容工作不要求 relay。
- 本目录不参与 OpenClaw crew 安装或 Docker 分发。合并到 `docker-distribution` 时排除 `workbuddy/`；不要通过修改原 crew 实现 WorkBuddy 行为。
- 专家包格式和本目录 `SKILL.md` 的展示字段遵循 WorkBuddy 官方规范，不生成 Codex 的 `agents/openai.yaml`，不把 WorkBuddy 专用字段回写到原 OpenClaw 技能。
- main 的已有素材加工、平台专家、BD、IR 与公共支撑技能尽量保留原工作流、脚本及资源。从零制作完整视频由用户提供成片，或交给当前 WorkBuddy 实际可用的专家/技能；不依赖 `content-producer`、IT engineer、OpenClaw gateway 或其会话工具。
- 不纳入视频号整个平台、OSBI、sales-cs-manager 和 Camoufox 依赖。其他混合技能裁剪浏览器工具，并同步修订 workflow、路由、示例和参考，不能只删脚本却留调用步骤。删除泛化重复的 xiaobei-operations，入口直接路由原生技能。
- WorkBuddy 整体排除 wx-mp-hunter；公众号诊断、对标、DNA、仿写与排版使用用户提供的正文、封面、本地 HTML 或截图。仅有账号名或链接时补问内容，不借助宿主或其他工具恢复公众号自动采集。原 OpenClaw 技能不受此裁剪影响。
- 用户主动询问完整版或明确要了解当前包之外的能力时，回应实际差异及官方源码/安装链接：[GitHub](https://github.com/TeamWiseFlow/xiaobei) / [AtomGit 国内线路](https://atomgit.com/wiseflow/xiaobei)。不在正常任务、配置错误或任务完成后自动推广下载；不把完整版下载说成自动补齐当前专家，也不自动安装。
- 原生导出范围在 `native-skills.json` 声明，通过 `scripts/sync_native.py` 更新。不要手改生成的原生技能副本；适配写进同步脚本并保留来源与校验值。运行入口负责依赖、wrapper、工作空间与私有登录态隔离。
- 平台采集、发布、互动及 relay 只有接通并验收后才能声明为可用。已存在的 HTTP relay 地址不能直接当作 MCP 地址；不要配置虚构的市场专家、技能或连接器 ID。
- 回归测试及夹具放仓根 `test/workbuddy/`，按仓库约定保持 Git 忽略。生成的 ZIP 放本目录被忽略的 `dist/`。
- 保留客户端直发平台请求、relay 计算或代理既定服务的边界；凭据不进专家包、文档、示例或 Git。
- 默认 relay 必须沿用 https://relay.openclaw-for-business.com，不另建 WorkBuddy 服务。文件系统路径适配不得改写 URL/域名。
- WorkBuddy 按官方专家规范使用 agents/ 下 Markdown 正文作为系统提示词；SOUL/IDENTITY 内容由同步脚本嵌入该正文，不假设平台自动加载 OpenClaw 工作空间文件。
