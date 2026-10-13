# 技能保留与裁剪范围

原生技能 34 个，WorkBuddy 适配技能 2 个；原生资源与扩展流程 389 个、逻辑命令 58 个。由 sync_native.py 生成。

保留 main 与公共技能的原工作流、脚本、模板、素材和共享运行库。操作只走 xiaobei-runtime 统一入口；下表没有 wrapper 的技能按其手册执行内容工作。脚本存在不等于平台账号已连接或实号验收通过。

| 原生技能 | 包内命令入口 |
| --- | --- |
| `aigc-video-gen` | `aigc-video-gen` |
| `awk-img-gen` | `awk-img-gen` |
| `awk-tts` | `awk-tts` |
| `bgm-library` | `bgm-library` |
| `content-calibrator` | `content-calibrator` |
| `council` | 内容方法与工作流，无独立 wrapper |
| `douyin-hunter` | `douyin-hunter` / `douyin-login` |
| `email-ops` | `email-ops` |
| `expert-bd` | `bd-record` / `douyin-im` / `douyin-interact` / `douyin-live` / `tiktok-im` / `tiktok-interact` / `tiktok-live` / `twitter-im` / `twitter-interact` / `xhs-im` / `xhs-live` |
| `expert-douyin` | `douyin-style-profiler` |
| `expert-ir` | `ir-record` |
| `expert-kuaishou` | `kuaishou-engagement` / `kuaishou-publish` / `kuaishou-style-profiler` |
| `expert-tiktok` | `tiktok-engagement` / `tiktok-publish` / `tiktok-style-profiler` |
| `expert-twitter` | `twitter-engagement` / `twitter-post` / `twitter-style-profiler` |
| `expert-wx-mp` | `generate-wenyan-theme` / `wechat-style-profiler` / `wx-mp-publisher` |
| `expert-xhs` | `xhs-engagement` / `xhs-publish` / `xhs-pugongying` / `xhs-qianfan` / `xhs-style-profiler` |
| `kuaishou-hunter` | `kuaishou-hunter` / `kuaishou-live` |
| `native-ui-card` | `native-ui-card` |
| `pexels-footage` | `pexels-footage` |
| `pitch-deck` | `pitch-deck-extract` / `pitch-deck-longimage` / `pitch-deck-pptx` |
| `pixabay-footage` | `pixabay-footage` |
| `platform-runtime` | 内容方法与工作流，无独立 wrapper |
| `published-track` | `published-track` |
| `talking-head-cut` | `talking-head-cut` |
| `tiktok-hunter` | `tiktok-hunter` |
| `video-edit` | `video-edit` |
| `video-review` | `video-review` |
| `viral-chaser` | `viral-chaser` |
| `weibo-hunter` | `weibo-hunter` |
| `weibo-publish` | `weibo-publish` |
| `wxwork-drive` | `wxwork-drive` |
| `wxwork-moments` | `wxwork-moments` |
| `x-hunter` | `x-hunter` |
| `xhs-hunter` | `xhs-hunter` |

## 删除的技能

| 技能 | 原因 |
| --- | --- |
| `wx-mp-hunter` | WorkBuddy 版整体移除公众号自动采集，文章正文、封面与排版参考由用户提供 |
| `expert-osbi` | 首版按用户要求不包含 OSBI |
| `expert-wx-channel` | 本版整体移除视频号平台，发布和取数依赖浏览器 |
| `sales-cs-manager` | WorkBuddy 单专家不管理 OpenClaw 客服 crew |
| `zhihu-publish` | 依赖 Camoufox |
| `ui-demo` | 依赖 Camoufox 录屏；使用用户录屏或 WorkBuddy 可用录屏能力 |
| `browser-guide` | 专用于 Camoufox |
| `smart-search` | 专用于 Camoufox；检索使用 WorkBuddy 实际可用能力 |
| `web-form-fill` | 依赖 Camoufox |

## 混合技能中删除的工具与资源

| 路径 | 原因 |
| --- | --- |
| `expert-wx-mp/tools/generate-wenyan-theme/scripts/collect-theme-sources.js` | 移除依赖公众号采集的脚本，替换为用户本地 HTML 整理入口 |
| `expert-douyin/tools/douyin-publish` | Camoufox 发布 |
| `expert-douyin/tools/douyin-engagement` | 从 Camoufox profile 读取发布凭据 |
| `expert-douyin/tools/_shared/publish_browser.py` | Camoufox 内部运行库 |
| `expert-douyin/tools/_shared/publish-login.md` | 已删除的创作者浏览器登录指导 |
| `_shared/aigc_common.py` | 原仓空占位文件；真实实现保留在 aigc-video-gen/scripts/aigc_common.py |
| `expert-wx-mp/tools/wx-mp-engagement` | Camoufox 创作者取数 |
| `platform-runtime/scripts/login.mjs` | Camoufox 登录/导出；API 业务与快手 HTTP 登录保留 |
| `platform-runtime/scripts/browser-snapshot.js` | Camoufox 浏览器登录快照 |
| `_shared/browser_publish_text.py` | 仅供已移除的浏览器发布技能使用 |

## 保留但改变入口的能力

- native-ui-card 保留渲染、模板、头像及样式，仅用 Chromium，不包含 Camoufox 回退。
- 公众号文章正文、封面、排版参考和后台数据由用户提供；主题工具仅整理用户本地 HTML，不采集链接或账号。
- X/TikTok/微博保留 API 与原写操作检查，通过私有文件 import-session 在线核验后导入；不含浏览器登录/导出。快手 HTTP 登录保留。
- Council 保留四声分析。有实际子任务工具才并行委托；没有时明确标注同会话角色分析。
- 完整视频制作不打包 content-producer，已有素材加工由 video-edit、talking-head-cut、video-review 执行。
- HTTP/API 与已有 relay 客户端保留，不预置凭据。Camoufox 发布与取数缺失步骤接受用户资料或 WorkBuddy 当前真实可用的工具。

## 官方服务与角色

- 默认 relay：https://relay.openclaw-for-business.com，沿用现有官方服务，不另建 WorkBuddy relay。
- 小贝 SOUL.md / IDENTITY.md 嵌入 agents/xiaobei-growth.md 系统提示词；不依赖平台自动加载这些文件。
- 掌柜二维码随 avatars/ofb_contact.png 打包，xiaobei-runtime contact 可复制到用户工作空间用于展示。
- 已删除 xiaobei-operations 的泛化重复指导，入口直接路由原生专家与具体任务 workflow。
