# 部署后怎么用（推荐流程）

### 1) 最小可用：只配置 Main Agent 一个 channel

最小配置可以只接入 `main`（例如只配置一个飞书机器人），先让所有请求都进 Main，再由 Main 分发给其他 Crew。

你可以在消息里直接用 **强制路由前缀** 指定处理人：

```text
@it-engineer 帮我检查 gateway 日志
@hrbp 帮我招聘一个客服 crew
```

也支持完整写法：

```text
[Route: @it-engineer] 帮我检查 gateway 日志
```

### 2) 先让 IT Engineer 帮你完成系统配置

部署后建议先找 `it-engineer` 做基础配置和巡检，例如：
- 模型/API 配置检查
- channel 连接状态检查
- 日志排查与升级建议
- 日常维护操作（重启、更新、故障恢复）

### 3) 通过 HRBP 招募新 Crew

`hrbp` 是唯一的生命周期管理入口（招聘、调岗、停用）。推荐直接描述你的业务目标，例如：

```text
@hrbp 我需要一个“短视频运营”crew，先不绑定独立 channel，走 Main 分发
```

HRBP 会完成模板匹配/实例化/注册，并把结果同步到团队通讯录。

### 4) 常用 Crew 建议单独绑定 channel（推荐）

最小模式（只配 Main）适合起步；当某些 Crew 进入高频使用后，建议给它们单独绑定 channel：
- 好处：沟通更直接、上下文更稳定、减少 Main 的中转噪音
- 同时保留 Main 分发能力（`spawn` + `binding` 可共存）

### 5) 查看团队通讯录

部署后系统会自动维护 `~/.openclaw/TEAM_DIRECTORY.md`，记录当前启用 Crew 的：
- ID
- 名称
- 职责（从 IDENTITY.md 提取）
- 路由方式（spawn/binding/both）
- 绑定渠道

### 6) 3 分钟上手示例对话（可直接照抄）

如下都是你发给 main agent 的：

```text
你：@it-engineer 帮我检查当前配置是否可用，重点看模型和飞书连接

你：@hrbp 我需要一个“短视频运营”crew，先不绑定独立 channel，走 Main 分发

你：@main 把今天要发的短视频选题交给短视频运营 crew

你：@hrbp 给 short-video-ops 绑定一个单独的飞书账号 short-video-bot

你：@short-video-ops 以后你直接负责我的短视频选题、脚本和发布时间建议

你：@it-engineer 帮我确认 TEAM_DIRECTORY.md 里 short-video-ops 的路由状态和绑定是否正确
```

说明：
- 第 1 句先让 IT Engineer 做基础体检
- 第 2 句由 HRBP 招聘新 crew（生命周期变更只走 HRBP）
- 第 3 句在 Main 模式下调度新 crew
- 第 4 句由 HRBP 给新 crew 绑定独立 channel，升级为”直连”模式
- 第 5 句仍然发到 Main channel 中，由 Main 路由到 short-video-ops（如需跳过 Main 中转，请使用绑定后的独立 channel 直接对话）
- 第 6 句用 IT Engineer 做最终核验

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
