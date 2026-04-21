# Wiseflow Official Addon

wiseflow 开源社区版本自带的官方 addon，在 wiseflow 默认全局技能（`skills/`）和基础补丁（`patches/`）之上，提供额外的全局技能和 Crew 模板。

## 1. 额外全局技能（skills/）

安装后对所有 crew 可见（受 DENIED_SKILLS / DECLARED_SKILLS 限制）：

| 技能 | 功能 | 所需环境变量 | 适用范围 |
|------|------|------------|----------|
| `rss-reader` | RSS/Atom Feed 读取，支持订阅任意标准 feed 格式的内容源 | — | 全部 crew 可用 |
| `siliconflow-img-gen` | 文生图、图片修改（SiliconFlow API） | `SILICONFLOW_API_KEY` | designer、selfmedia-operator |
| `siliconflow-video-gen` | 文生视频 / 图生视频（SiliconFlow API） | `SILICONFLOW_API_KEY` | selfmedia-operator |
| `connections-optimizer` | 人脉关系网络优化与拓展建议 | — | **仅 business-developer**；其余 crew DENIED |
| `email-ops` | 批量邮件撰写与 SMTP 发送 | `SMTP_SERVER` `SMTP_USER` `SMTP_PASSWORD` | **仅 business-developer**；其余 crew DENIED |
| `pitch-deck` | 融资/商务演示文稿生成，支持读取 .pptx 文件内容 | — | **仅 business-developer**；其余 crew DENIED |
| `social-graph-ranker` | 社交图谱关键节点分析与排序 | — | **仅 business-developer**；其余 crew DENIED |

## 2. Crew 模板（crew/）

官方提供的生产就绪 Crew 模板，由 `setup-crew.sh` 一键实例化：

| Crew / 技能层 | 核心能力 |
|---|---|
| **selfmedia-operator** | 日常灵感记录、素材搜集；选题研究→图文输出、草稿扩写→完整文章；短视频 AI 生成；支持掘金 / Medium / 知乎 / 头条 / Twitter / Instagram / TikTok / YouTube 发布；可自主调用 designer 完成配图 |
| **business-developer** | 人脉关系网络优化与拓展建议；批量邮件撰写与发送；融资 / 商务演示文稿生成；社交图谱关键节点分析与排序 |
| **sales-cs** | 首问接待、售前咨询、销售引导一体化；客户数据库自动维护（业务状态、来源渠道、意向追踪）；内置收款发起、体验邀请、遇到客户说晚些聊等情况自动后续跟进；智能判断升级人工 |
| **designer** | 文生图、图片修改；可被其他 crew 通过 `sessions_spawn` 调用 |

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
- 支持自动发布到知乎/头条/掘金/Medium（wenyan-publisher）、Twitter、Instagram、TikTok、YouTube

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

专注商务拓展场景，具备其他 crew 不具备的商务专属技能组合。

- `connections-optimizer`：人脉关系网络优化与拓展建议
- `email-ops`：批量邮件撰写与发送（SMTP 配置）
- `pitch-deck`：融资 / 商务演示文稿生成
- `social-graph-ranker`：社交图谱关键节点分析与排序

专属技能：`connections-optimizer` / `email-ops` / `pitch-deck` / `social-graph-ranker`

---

---

## 四 Crew 协同：自动化获客全链路管线

以上四个 Crew 模板并非孤立工具，它们共同构成了一套**端到端的自动化获客闭环**——从内容种草、主动拓客，到客服转化，全链路无人值守自动运转：

```
  ┌─────────────────────┐     ┌──────────────────────┐
  │  selfmedia-operator │     │  business-developer  │
  │   [内容种草 · 引流] │     │   [主动触达 · 拓客]  │
  │                     │     │                      │
  │ 多平台持续发布内容  │     │ 人脉分析 & 邮件冷触达│
  │ 吸引潜在用户自然关注│     │ 锁定并主动找到目标客 │
  └────────┬────────────┘     └──────────┬───────────┘
           │      ↑                      │      ↑
           │   按需 spawn             按需 spawn
           │      │                      │
           │   ┌──┴──────────────────────┴──┐
           │   │          designer          │
           │   │      [视觉创作支援]        │
           │   │  配图 / 海报 / 品牌素材    │
           │   └────────────────────────────┘
           │                      │
           └──────────┬───────────┘
                      │  流量 & 线索汇聚
               ┌──────▼───────┐
               │   sales-cs   │
               │  [线索转化]  │
               │              │
               │ 7×24 在线    │
               │以成交为目标  │
               │ 收款 & 追踪  │
               └──────────────┘
```

| 阶段 | Crew | 核心职责 |
|------|------|----------|
| 内容引流 | `selfmedia-operator` | 在微信公众号、知乎、头条、Twitter、Instagram、TikTok、YouTube 等平台持续输出内容，吸引自然流量进入 |
| 主动拓客 | `business-developer` | 人脉关系网络分析、批量邮件冷触达、商务 pitch 生成，主动锁定并触达目标客户 |
| 视觉支援 | `designer` | 按需被 selfmedia-operator 或 business-developer 通过 `sessions_spawn` 唤起，提供配图、海报、品牌素材 |
| 线索转化 | `sales-cs` | 7×24 小时在线接客，以促成交为核心目标，内置收款发起、意向追踪、超限自动升级人工等机制 |

**适用场景**：

- 直接作为自身业务的全自动获客基础设施部署
- 嵌入现有营销体系，作为 AI 驱动的增长引擎
- 验证从内容种草到客服转化全链路 AI 自动化的可行性

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

---

## 软件依赖安装（IT Engineer 执行一次）

以下 skill 包含 Node.js 本地依赖，**需在初始化部署后由 IT Engineer 手动执行一次**，之后 agent 可直接调用无需再安装：

| Crew | Skill | 安装命令 |
|------|-------|---------|
| selfmedia-operator | wenyan-publisher | `bash -c "cd ~/.openclaw/workspace-media-operator/skills/wenyan-publisher && npm install"` |

> 如果 workspace 路径与上述不同，请替换为实际路径（通常为 `~/.openclaw/workspace-<crew名称>/skills/<skill名称>`）。
