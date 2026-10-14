---
name: "kuaishou-style-profiler"
description: "快手定性内容 DNA 的样本报告、聚合模板和增量更新。"
description_zh: "快手定性内容 DNA 的样本报告、聚合模板和增量更新。"
description_en: "kuaishou-style-profiler: native Xiaobei workflows, tools and reusable resources."
version: "0.3.3"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。



# 快手内容 DNA

```bash
kuaishou-style-profiler report --input /绝对路径/样本文字稿.md --sample-id sample-01 --dna-id dna-0 --kind video
kuaishou-style-profiler build --dna-id dna-0 --kind video
```

完整 report/build/update 参数使用 `kuaishou-style-profiler --help` 与各子命令 --help。输入是已核对来源、正文、图组或视频转写的 Markdown 样本；统计 scaffold 不能替代 Agent 回读素材后的定性结论。视频与图文/文字分别建 DNA，不混合样本统计。

默认产物保存在 `kuaishou/dna/<dna-id>/`。report 逐篇描述观测与依据；build 回读全部报告，记录样本分母、共性、局部借鉴和例外，再完善 DNA 文档与 template。用户偏好要转译到具体维度；少量样本不得称为稳定风格。update 合并报告但仍需重新检查结论与模板。DNA 调整经用户确认后写入，不把内容统计当评分。

视频重点：选题与观看理由、标题/封面、内容创意、业务植入、CTA、视频形态与制作规格、可选口播与账号运营。图文/文字重点：首句/标题、正文语气、图组视觉、内容创意、业务植入与 CTA；缺媒体的文字样本明确标注视觉维度不适用。
