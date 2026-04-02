# Wiseflow Addon for OpenClaw

浏览器反检测 + Tab Recovery + Smart Search + RSS Reader
本目录是 [wiseflow](https://github.com/TeamWiseFlow/wiseflow) 提供给 [openclaw-for-business](https://github.com/TeamWiseFlow/openclaw_for_business) 的标准 addon 包。

## 功能

### 1. Tab Recovery 补丁

当 Agent 操作过程中目标标签页意外关闭或消失时，自动进行快照级别的标签页恢复，确保任务不会因标签页丢失而中断。

### 2. Smart Search（智能搜索）

替代 openclaw 内置的 `web_search`，提供更强大的搜索能力。相比原版内置的 web search tool，具备三大核心优势：

- **完全免费，无需 API Key**：不依赖任何第三方搜索 API，零成本使用
- **即时搜索，时效性最佳**：直接驱动浏览器前往目标页面或各大社交媒体平台（微博、Twitter/X、facebook 等）进行搜索，第一时间获取最新发布的内容
- **信源可自定��**：用户可以自由指定搜索源，精准匹配自己的信息需求

### 3. Browser Guide 技能

教会 agent 处��登录墙、验证码、懒加载、付费墙等场景的最佳实践。

### 4. RSS Reader 技能

支持读取 RSS/Atom Feed，可订阅任意支持标准 feed 格式的内容源。

## 安装

这是 wiseflow official addon，已随代码仓发布，无需单独安装
