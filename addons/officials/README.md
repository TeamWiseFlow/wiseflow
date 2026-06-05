# Wiseflow Official Addon

wiseflow 开源社区版本自带的官方 addon，在 wiseflow 默认全局技能（`skills/`）和基础补丁（`patches/`）之上，提供额外的全局技能和 Crew 模板。

## 1. 额外全局技能（skills/）

安装后对所有 crew 可见（受 DENIED_SKILLS / DECLARED_SKILLS 限制）：

| 技能 | 功能 | 所需环境变量 | 适用范围 |
|------|------|------------|----------|
| `rss-reader` | RSS/Atom Feed 读取，支持订阅任意标准 feed 格式的内容源 | — | 全部 crew 可用 |
| `siliconflow-img-gen` | 文生图、图片修改（SiliconFlow API） | `SILICONFLOW_API_KEY` | designer、selfmedia-operator |
| `pexels-footage` | Pexels 免版权图片/视频搜索与下载 | `PEXELS_API_KEY` | designer、selfmedia-operator |
| `pixabay-footage` | Pixabay 免版权图片/视频搜索与下载（Pexels 备选） | `PIXABAY_API_KEY` | designer、selfmedia-operator |
| `council` | 召集四方视角对商业模式、融资策略等关键决策进行结构化辩论 | — | **仅 ir**；其余 crew DENIED |
| `connections-optimizer` | 人脉关系网络优化与拓展建议 | — | **仅 business-developer**；其余 crew DENIED |
| `email-ops` | 批量邮件撰写与 SMTP 发送 | `SMTP_SERVER` `SMTP_USER` `SMTP_PASSWORD` | **仅 business-developer**；其余 crew DENIED |
| `pitch-deck` | 融资/商务演示文稿生成，零依赖单文件 HTML 输出 | — | **仅 business-developer / ir**；其余 crew DENIED |
| `ppt-maker` | 从文稿内容生成专业 PPTX，支持模板/参考图风格提取、AI 配图 | — | **仅 business-developer / ir**；其余 crew DENIED |
| `social-graph-ranker` | 社交图谱关键节点分析与排序 | — | **仅 business-developer**；其余 crew DENIED |
| `web-form-fill` | 网络表单填报，从信息搜集到浏览器填报的完整工作流 | — | **仅 ir**；其余 crew DENIED |
| `xhs-interact` | 小红书社交互动：发表评论、回复评论、点赞 | — | **仅 business-developer**；其余 crew DENIED |
| `xianyu-ops` | 闲鱼商品搜索、详情查看、私信会话管理与回复 | — | **仅 business-developer**；其余 crew DENIED |

## 2. Crew 模板（crew/）

官方提供的生产就绪 Crew 模板，由 `setup-crew.sh` 一键实例化：

| Crew / 技能层 | 核心能力 |
|---|---|
| **selfmedia-operator** | 日常灵感记录、素材搜集；选题研究→图文输出、草稿扩写→完整文章；短视频 AI 生成；多平台发布；可自主调用 designer 完成配图 |
| **business-developer** | 商业情报采集、潜客挖掘、评论区互动拓展；人脉网络优化、邮件触达；融资/商务演示文稿生成 |
| **ir** | 商业模式打磨与定期复盘；融资路演材料制作；投资人发掘与跟进；项目申报；软件著作权登记 |
| **sales-cs** | 首问接待、售前咨询、销售引导一体化；客户数据库自动维护；内置收款发起、体验邀请、自动后续跟进；智能判断升级人工 |
| **designer** | 文生图、图片修改；可被其他 crew 通过 `sessions_spawn` 调用 |

---

#### ir — 投资人关系专员

**类型**：对内（internal）`T1` 权限

老板的商业打磨合伙人和融资执行手——核心价值是长期积累 + 定期复盘迭代商业模式，在此基础上执行融资相关事务。

三大工作块：
- **商业模式打磨**：记录创业思路/经验教训，定期 council 复盘，梳理迭代商业模式，维护 BP，制作融资路演材料
- **项目申报**：上网填报创业比赛/项目申请/软件著作权登记，防重复，可定期总结
- **投资人发掘与跟进**：主动发掘和跟进投资人，国内场景主要在社交平台操作

专属技能：`ir-record` / `investor-hunting` / `investor-materials` / `investor-outreach` / `market-research` / `swcr-register`

---

#### selfmedia-operator — 自媒体运营

**类型**：对内（internal）`T2` 权限

业务驱动的内容营销，一切产出以推广公司产品与业务为出发点。

- 两种工作模式：选题研究 → 图文输出 / 草稿扩写 → 完整文章
- 配图优先级：用户上传 > 网络免版权 > AI 生成（siliconflow-img-gen）> 历史素材复用
- 视频制作：通过 `t2video` 技能完成短视频制作（TTS 语音合成 + AI 视频片段生成 + 素材组装）
- 素材统一归档到 `campaign_assets/`，维护 index.md 方便复用
- 支持自动发布到微信公众号、知乎、头条、掘金、Medium、Twitter/X、Instagram、TikTok、YouTube、抖音、Facebook、Threads、Pinterest 等平台

专属技能：`wenyan-publisher` / `twitter-post` / `instagram-publish` / `tiktok-publish` / `youtube-publish` / `douyin-publish` / `toutiao-publish` / `juejin-publish` / `facebook-publish` / `threads-publish` / `pinterest-publish` / `xhs-content-ops` / `t2video` / `highlight-clipper` / `published-track`

---

#### business-developer — 商务拓展

**类型**：对内（internal）`T2` 权限

专注商务拓展场景，具备其他 crew 不具备的商务专属技能组合。

- **情报采集**：`intel-gathering` 定时监控信源提取商业情报；`info-record` 情报去重与查询
- **潜客挖掘**：`lead-hunting` 自媒体平台按策略探索潜在客户；`bd-record` 追踪数据库去重
- **互动拓展**：`comment-engagement` 在评论区以留言/回复/私信方式拓展潜在客户
- **人脉触达**：`connections-optimizer` 人脉网络优化；`email-ops` 批量邮件撰写与发送
- **演示文稿**：`pitch-deck` HTML 演示文稿；`ppt-maker` PPTX 演示文稿
- **社交分析**：`social-graph-ranker` 社交图谱关键节点排序

专属技能：`intel-gathering` / `info-record` / `lead-hunting` / `bd-record` / `comment-engagement` / `connections-optimizer` / `email-ops` / `pitch-deck` / `ppt-maker` / `social-graph-ranker`

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

#### designer — 设计师

**类型**：对内（internal）`T2` 权限

专注视觉创意设计，结合 AI 生图能力提供配图、海报、品牌素材生成服务。

- 调用 `siliconflow-img-gen` 进行文生图和图片修改
- 配合 selfmedia-operator、business-developer 等 crew 完成视觉需求
- 可被其他 crew 通过 `sessions_spawn` 调用（allowAgents 中配置）

专属技能：`design-system-picker` / `init-workspace`

---

---

## 五 Crew 协同：自动化获客全链路管线

以上五个 Crew 模板并非孤立工具，它们共同构成了一套**端到端的自动化获客闭环**——从内容种草、主动拓客，到客服转化，全链路无人值守自动运转：

```
  ┌─────────────────────┐     ┌──────────────────────┐
  │  selfmedia-operator │     │  business-developer  │
  │   [内容种草 · 引流] │     │   [主动触达 · 拓客]  │
  │                     │     │                      │
  │ 多平台持续发布内容  │     │ 情报采集 & 潜客挖掘  │
  │ 吸引潜在用户自然关注│     │ 评论区互动 & 邮件触达│
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

  ┌──────────────────────┐
  │          ir          │
  │   [融资 · 著作权]   │
  │                      │
  │ 商业模式打磨 & 复盘  │
  │ 投资人发掘与跟进     │
  │ 项目申报 & 软著登记  │
  └──────────────────────┘
```

| 阶段 | Crew | 核心职责 |
|------|------|----------|
| 内容引流 | `selfmedia-operator` | 在微信公众号、知乎、头条、掘金、Twitter/X、Instagram、TikTok、YouTube 等平台持续输出内容，吸引自然流量进入 |
| 主动拓客 | `business-developer` | 商业情报采集、潜客挖掘、评论区互动拓展、批量邮件冷触达、商务 pitch 生成 |
| 融资支持 | `ir` | 商业模式打磨与定期复盘、投资人发掘与跟进、项目申报与软件著作权登记 |
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

## AI 生图服务推荐

`siliconflow-img-gen` 技能依赖 [SiliconFlow](https://cloud.siliconflow.cn/i/WNLYbBpi) API，用于文生图、图片修改。

`siliconflow-video-gen` 和 `siliconflow-tts` 已迁移为 video-producer（official-plus addon）内置技能。开源版 `selfmedia-operator` 内置的 `t2video` 技能同样集成了 SiliconFlow 视频生成和 TTS 能力。

[硅基流动（SiliconFlow）](https://cloud.siliconflow.cn/i/WNLYbBpi) 提供国内领先的生图和生视频模型，注册并实名认证即可领取免费代金券。

👉 使用[推荐链接](https://cloud.siliconflow.cn/i/WNLYbBpi)注册，你我各得 ¥16 平台奖励

配置好 API Key 后，在 `~/.openclaw/openclaw.json` 中设置环境变量：

```json
{
  "gateway": {
    "env": {
      "SILICONFLOW_API_KEY": "your-api-key-here"
    }
  }
}
```

---

## 软件依赖安装（IT Engineer 执行一次）

以下 skill 包含 Node.js 本地依赖，**需在初始化部署后由 IT Engineer 手动执行一次**，之后 agent 可直接调用无需再安装：

| Crew | Skill | 安装命令 |
|------|-------|---------|
| selfmedia-operator | wenyan-publisher | `bash -c "cd ~/.openclaw/workspace-media-operator/skills/wenyan-publisher && npm install"` |

> 如果 workspace 路径与上述不同，请替换为实际路径（通常为 `~/.openclaw/workspace-<crew名称>/skills/<skill名称>`）。
