# 部署后怎么用（推荐流程）

### 推荐上手三步走

以下三个场景是最典型的初始配置流程，对话内容可直接照抄。

---

#### 第一步：通过 Main Agent 招募对内 Crew（以新媒体小编为例）

> 适用 crew 类型：**internal**（在 Main Agent 的频道中操作）

**1.1 招募新媒体小编**

```text
你（在 main 频道）：
帮我招募一个新媒体小编，用 selfmedia-operator 模板，ID 就叫 selfmedia-operator

# Main Agent 会展示招募方案，等你确认
你：确认

# Main Agent 完成实例化，提示重启 Gateway
```

**1.2 向小编植入业务背景**

实例化完成、重启 Gateway 后，告诉 Main Agent 向小编注入背景信息（或者等单独绑定小编 channel 后，直接跟小编说）：

```text
你：
帮我把以下背景信息注入新媒体小编的工作记忆：
- 公司：<你的公司名称>，做 <主营业务一句话>
- 运营平台：微信公众号 <账号名> + 小红书
- 账号调性：<风格定位，如”技术圈硬核但不失活泼”>
- 目标读者：<典型受众描述>
- 发布节奏：每周 2 篇，周二和周五
- 禁忌话题：<不可提及的竞品或话题>

# Main Agent 会更新 selfmedia-operator 的 MEMORY.md 和 USER.md
```

**1.3 开始使用**

```text
你（在 main 频道，直接路由）：
@selfmedia-operator 帮我写一篇关于 <选题> 的文章，面向 <目标读者>

# 或者给新媒体小编绑定独立频道后直接对话
```

---

#### 第二步：通过 HRBP 招募对外 Crew（以销售客服为例）

> 适用 crew 类型：**external**（在 HRBP 的频道中操作）

**2.1 告诉 HRBP 你的业务背景和需求**

```text
你（在 hrbp 频道）：
我需要招募一个微信销售客服，基于 sales-cs 模板。
业务背景如下：
- 公司：<你的公司名称>
- 产品：<核心产品/服务名称>，<一句话说清楚能帮客户解决什么>
- 付费层级：<例如：免费体验版 → VIP会员 → 企业订阅>
- 客服对外称呼：<如”小明助手”>
- 负责人微信：<负责人微信号>（客户复杂问题时升级人工）
- 绑定渠道：飞书，账号 ID <channel_account_id>
```

**2.2 HRBP 配置实例并引导你填写业务内容**

```text
# HRBP 会展示实例化方案，等你确认
你：确认

# HRBP 完成实例化，并请你提供以下内容填写到客服手册：
# - 产品 FAQ（常见问题答案）
# - 付费方式和购买链接
# - 反馈问卷链接
# - 开票申请工单链接

你：
产品常见问题如下：
Q：<问题1>？A：<答案1>
Q：<问题2>？A：<答案2>
购买链接：<链接>
反馈问卷：<链接>
开票工单：<链接>

# HRBP 把这些内容写入 sales-cs 实例的 MEMORY.md
```

**注意：对外 crew 必须单独绑定对外服务 channel，推荐使用代码仓中的 awada extension**

**2.3 重启 Gateway，销售客服上线**

```text
你：确认，帮我重启 Gateway

# 或在终端手动执行：
# ./scripts/dev.sh gateway
```

---

#### 第三步：通过 IT Engineer 日常运维

> IT Engineer 是内置的系统级 crew，无需招募，通过 Main Agent 频道路由

**3.1 系统巡检**

```text
你（在 main 频道）：
@it-engineer 帮我做一次系统巡检，重点检查：
- 模型/API 配置是否正常
- 各 crew 的 channel 绑定状态
- 最近有没有异常日志
```

**3.2 升级系统**

```text
你：@it-engineer 帮我把系统升级到最新版本

# IT Engineer 会执行 ./scripts/upgrade.sh 并报告结果
```

**3.3 排查故障**

```text
你：
@it-engineer 新媒体小编今天回复说”工具调用失败”，帮我查一下原因

# IT Engineer 会检查日志、配置，定位问题并修复
```

**3.4 查看团队通讯录**

```text
你：帮我看一下现在团队里有哪些 crew，以及各自的绑定状态

# Main Agent 会读取 TEAM_DIRECTORY.md，输出当前团队状态
```

---

#### 3 分钟速查（可直接照抄）

```text
# 招募对内 crew（在 main 频道）
你：帮我招募一个新媒体小编，用 selfmedia-operator 模板

# 注入业务背景（在 main 频道）
你：帮我把以下背景注入新媒体小编：[业务背景...]

# 招募对外 crew（在 hrbp 频道）
你：我需要招募一个微信销售客服，基于 sales-cs 模板，[业务背景...]

# 系统巡检（在 main 频道路由）
你：@it-engineer 做一次系统巡检

# 查看团队状态
你：帮我看一下现在有哪些 crew 在运行
```

# 生产部署

```bash
# 构建 + 安装后台服务（自动启动 + 开机自启 + 崩溃重启）
cd wiseflow && pnpm build && cd ..
./scripts/reinstall-daemon.sh
```

日后升级只需要执行：

```bash
./scripts/upgrade.sh
```

> **从自己的 fork 同步**（而非官方仓库）：如果你 fork 了本项目并做了定制，希望 `upgrade.sh` 从自己的 fork 拉取，只需确保 `origin` 指向你的 fork，运行时在提示处输入 `y` 即可：
> ```bash
> git remote set-url origin https://github.com/YOUR_ORG/wiseflow.git
> ./scripts/upgrade.sh   # 提示 "Remote is not the official OFB repo" 时输入 y
> ```

## 常用命令

```bash
./scripts/dev.sh gateway              # 开发模式启动
./scripts/dev.sh gateway --port 18789 # 指定端口
./scripts/dev.sh cli config           # CLI 操作
./scripts/upgrade.sh                  # 升级 OFB + openclaw 引擎
./scripts/reinstall-daemon.sh         # 生产部署

# Agent 管理
./scripts/setup-crew.sh               # 手动安装/重装 Agent 系统
./scripts/setup-crew.sh --force       # 覆盖已有 workspace
./scripts/setup-crew.sh --denied-skills hrbp:slack,github
```

## Addon 开发

详见 **[addon_development.md](./addon_development.md)**（英文），涵盖：

- OpenClaw 版本锁定机制（`openclaw.version` 文件的读取方式）
- Addon 目录结构和 `addon.json` 规范
- 四层加载机制（overrides → patches → skills → crew）
- 本地开发与测试流程
- 发布与上架方式

## 文档

- [多 crew 系统架构](docs/crew-system.md) - 架构设计和组件说明
- [快速上手](docs/quick-start.md) - 安装和使用指南
- [OpenClaw 分析](docs/introduce_to_clawd_by_claude.md) - 上游代码架构分析
- [Crews v2 设计文档](crews/DESIGN.md) - Template → Instance 机制与完整设计细节

## 许可证

MIT License
