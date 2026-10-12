# OSBI / BD 职责与浏览器搜索评估

本次 5.7.4 调整将公开资料的提取、跟踪与分析收进 main 的 `expert-osbi`。`expert-bd` 承接潜客探索/筛选、互动和邮件等联络，平台原始资料按平台调用 `douyin-hunter` / `xhs-hunter` / `tiktok-hunter` / `kuaishou-hunter` / `x-hunter` / `weibo-hunter` / `wx-mp-hunter`；公开直播读取使用 `douyin-hunter live` / `xhs-hunter live` / `tiktok-hunter live` / `kuaishou-hunter live`；其他站点通过公共 `smart-search` 和 `browser-guide` 访问。

| 资源 | 归属 |
|---|---|
| Intel Gathering、Competitor Watch、Live Research | expert-osbi workflows |
| 原 market-research 全部研究模式 | expert-osbi 的 Market Research workflow |
| 情报存储 info-record、通用订阅解析 rss-reader | expert-osbi tools |
| Lead Hunting、Interaction、Live Interaction、IM 与互动写工具 | expert-bd |
| 邮件互动 email-ops | 保持公共技能，列入 expert-bd 工具使用清单 |
| 公开直播读取、榜单/商品和有界事件监听 | `douyin-hunter live` / `xhs-hunter live` / `tiktok-hunter live` / `kuaishou-hunter live` |

抖音直播执行器与小红书直播/IM 传输归内部 `_shared`，公开入口分开限制读取和发送方法；不复制平台请求与登录逻辑。快手原 kuaishou-live 只读 wrapper 收进 `kuaishou-hunter`，保留原命令名。TikTok/快手的运行库职责白名单随入口调整，保留依赖的业务/签名代码不变。

`db/info_record.db` 和 `db/bd_record.db` 的路径、schema 与已有记录保持兼容。bd-record 留在 BD 作为线索与联络档案，BD 的 Lead Hunting 保存公开潜客画像，筛选不代表已联络；研究报告归 `osbi/`，潜客报告与联络产物归 `bd/`。迁移不移动用户已有报告或定时配置。更新部署时需重建技能与 wrapper 软链，并按职责更新旧定时入口；Lead Hunting 仍指向 BD，其余研究 workflow 指向 OSBI；本次只修改仓库。

## smart-search 与 browser-guide

当前决定（2026-10-12）：用户明确暂不合并。smart-search 专门指导 Camoufox 浏览器搜索，按当前 crew 配置优先使用已列明的平台采集技能；普通站点共享持久化 `default` session/profile，自媒体专用 profile 与 API 登录沿用各技能约定。browser-guide 继续提供通用浏览器操作规范。六类专业来源 36 个站点已按用户选择接入，通用搜索不扩增；范围与上游差集见 [搜索上游复核](smart-search-upstream-review.md)。下方为此前的合并评估，暂不实施。

评估结论：适合合并为公共 `browser-guide` 下的搜索 workflow。当前两个入口分别有 217 行和 205 行，smart-search 后半部分重复了会话生命周期、等待/超时、snapshot ref、表单输入和登录/验证码操作；还有与 browser-guide 不同的会话示例。只负责浏览器获取后，维护一个浏览器操作入口更清楚。

站点 URL、分页、关键词编码、warmup 和结果提取知识仍应保留；它们并不是通用浏览器规范。建议结构：

```text
skills/browser-guide/
  SKILL.md                 浏览器使用入口，搜索任务指向 workflow
  workflows/search.md      选站、搜索式、去噪、采样与来源记录
  sites/                   按需读取站点参数和提取方法
```

browser-guide 的 description 应明确“网页搜索、浏览、读取”，让搜索任务能直接发现它。OSBI 负责研究问题、证据判断和分析；search workflow 只负责高效取得原始页面。

合并时一起完成：

- 平台原始资料按平台直接使用 `douyin-hunter` / `xhs-hunter` / `tiktok-hunter` / `kuaishou-hunter` / `x-hunter` / `weibo-hunter` / `wx-mp-hunter`，不保留浏览器绕行；修正当前 smart-search 默认意图表仍直指微博的遗漏。
- 会话、登录和清理规范只维护一份，搜索复用同一受控会话并关闭自己创建的会话，避免影响其他任务。
- 保留搜索范围、关键词和实际尝试次数的可核查记录；按需读取站点文件，不把站点目录全文塞进 SKILL.md。
- 同步 main/content-producer 配置样例、技能 allowlist、跨技能引用和公共目录说明；正常升级移除旧 smart-search 入口，保留用户自定义技能与配置。

smart-search/browser-guide 保持现有两个入口；当前维护方向为分别完善浏览器搜索指导与通用操作规范。
