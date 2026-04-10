# Wiseflow Official Addon

浏览器反检测补丁 + 全局技能 + 官方 Crew 模板

本目录是 [wiseflow](https://github.com/TeamWiseFlow/wiseflow) 官方 addon 包，随代码仓发布，无需单独安装。

## 功能概览

### 1. 代码补丁（patches/）

对 OpenClaw 打的非侵入式补丁，由 `apply-addons.sh` 自动应用：

| 补丁 | 功能 |
|------|------|
| `002-disable-web-search-env-var.patch` | 添加 `OPENCLAW_DISABLE_WEB_SEARCH` 环境变量，可按需禁用内置 web_search |
| `003-act-field-validation.patch` | 强化浏览器工具的 act 字段校验，防止幻觉动作 |
| `004-web-fetch-allow-rfc2544.patch` | 允许 web fetch 访问 RFC 2544 保留地址段（内网场景） |

### 2. 全局技能（skills/）

安装后对所有 crew 可见：

| 技能 | 功能 | 备注 |
|------|------|------|
| `smart-search` | 智能搜索：驱动浏览器在 40+ 平台实时搜索，完全免费，无需 API Key | 替代 openclaw 内置 web_search |
| `browser-guide` | 浏览器操作最佳实践：登录墙、验证码、懒加载、付费墙的处理指导 | 辅助技能，减少 agent 踩坑 |
| `rss-reader` | RSS/Atom Feed 读取，支持订阅任意标准 feed 格式的内容源 | — |

### 3. Crew 模板（crew/）

官方提供的生产就绪 Crew 模板，由 `setup-crew.sh` 一键实例化：

---

#### sales-cs — 销售型客服

**类型**：对外（external）`T0` 权限

以**促进成交**为核心目标，而非单纯被动答疑。

- 首问接待、售前咨询、销售引导一体化
- 话术原则：先承接 → 再判断 → 给结论 → 推下一步
- 自动维护客户数据库（业务状态、来源渠道、意向追踪）
- 内置收款发起（payment_send）、体验邀请（exp_invite）、主动触达（proactive-send）等专属技能
- 超过 20 轮对话后自动升级人工，并记录用户不满到 feedback/

专属技能：`customer-db` / `demo_send` / `exp_invite` / `payment_send` / `proactive-send`

---

#### selfmedia-operator — 自媒体运营

**类型**：对内（internal）`T2` 权限

业务驱动的内容营销，一切产出以推广公司产品与业务为出发点。

- 两种工作模式：选题研究 → 图文输出 / 草稿扩写 → 完整文章
- 配图优先级：用户上传 > 网络免版权 > AI 生成（siliconflow-img-gen）> 历史素材复用
- 视频生成：通过 `siliconflow-video-gen` 生成短视频（文生视频 / 图生视频）
- 素材统一归档到 `campaign_assets/`，维护 index.md 方便复用
- 支持自动发布到微信公众号/知乎/头条（wenyan-publisher）、Twitter、Instagram、TikTok、YouTube

专属技能：`wenyan-publisher` / `twitter-post` / `instagram-post` / `tiktok-post` / `youtube-upload`

---

#### designer — 设计师

**类型**：对内（internal）`T2` 权限

专注视觉创意设计，结合 AI 生图能力提供配图、海报、品牌素材生成服务。

- 调用 `siliconflow-img-gen` 进行文生图和图片修改
- 配合 selfmedia-operator、business-developer 等 crew 完成视觉需求
- 可被其他 crew 通过 `sessions_spawn` 调用（allowAgents 中配置）

---

#### business-developer — 商务拓展

**类型**：对内（internal）`T2` 权限

专注商务拓展场景，具备其他 crew 不��备的商务专属技能组合。

- `connections-optimizer`：人脉关系网络优化与拓展建议
- `email-ops`：批量邮件撰写与发送（SMTP 配置）
- `pitch-deck`：融资 / 商务演示文稿生成
- `social-graph-ranker`：社交图谱关键节点分析与排序

专属技能：`connections-optimizer` / `email-ops` / `pitch-deck` / `social-graph-ranker`

---

## 安装

这是 wiseflow official addon，已随代码仓发布，通过以下脚本自动安装：

```bash
./scripts/apply-addons.sh    # 安装补丁 + 全局技能
./scripts/setup-crew.sh      # 实例化 crew 模板
```

或使用一键启动：

```bash
./scripts/dev.sh gateway     # 开发模式（含完整安装）
./scripts/reinstall-daemon.sh # 生产模式
```
