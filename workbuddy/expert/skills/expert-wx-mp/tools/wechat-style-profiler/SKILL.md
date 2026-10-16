---
name: "wechat-style-profiler"
description: "为单篇文章提取 17 维 DNA report，按 DNA ID 聚合历史 report 生成 DNA 文档，并推导完整的 DNA template。"
description_zh: "为单篇文章提取 17 维 DNA report，按 DNA ID 聚合历史 report 生成 DNA 文档，并推导完整的 DNA template。"
description_en: "wechat-style-profiler: native Xiaobei workflows, tools and reusable resources."
version: "0.3.3"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。


# wechat-style-profiler

## 产物模型

```text
单篇文章 -> DNA report
同一个 DNA 目录下的全部 report + 权重/focus -> DNA 文档
DNA 文档 -> DNA template
```

- **DNA report**：单篇文章的 17 维提取结果。
- **DNA 文档**：聚合历史 report 后得到的风格与选题规则。
- **DNA template**：由 DNA 文档推导出的写作模板，供生产时直接执行。

## 存储结构

DNA 以 DNA ID 为主体存储，一个 DNA 可以持续放入任意数量文章，文章可以来自一个或多个参考账号。

```text
wx_mp/dna/{dna-id}/
  reports/
    {sample-id}.report.md
  covers/
    {sample-id}.{ext}
  {dna-id}.dna.md
  {dna-id}.template.md
```

原始资料（文章正文）可以临时来自任何位置（建议 `wx_mp/ref/{dna-id}/articles/`）；生成后的 DNA report 必须进入对应 DNA 的 `reports/` 目录。

## 职责边界

- 输入正文支持 `.md` / `.txt`；`.docx` 先由 Agent 提取为文本。
- 统计只作为聚合证据底座，不评分、不替代定性判断。
- 17 维语义判断由 Agent 回读原文完成；封面图维度必须由视觉模型读取本地图片完成。
- 不输出排版主题、合规结论、账号权重或风格评分。
- 不要求用户确认或登记 INDEX。

## Report - 单篇提取

```bash
wechat-style-profiler report \
  --input path/to/article.md \
  --dna-id {dna-id} \
  --sample-id {sample-id} \
  --cover-image path/to/cover.jpg
```

默认输出：

```text
wx_mp/dna/{dna-id}/reports/{sample-id}.report.md
```

可配置权重：

```bash
--weight 3
```

可限制该篇只在某些维度参与借鉴：

```bash
--focus title-style
--focus sentence-rhythm
```

Agent 生成 scaffold 后必须回读原文，补齐每个维度的单篇结论、原文证据和可复用写作信号。
封面图维度必须读取 `--cover-image` 指向的本地图片，并通过视觉模型补齐主体、构图、色彩、光线、质感、风格、文字视觉、品牌元素、避免项和 AIGC 复现提示词要素。没有封面图时记录“未提供”，不得编造。

## Build - 聚合 DNA 文档与模板

```bash
wechat-style-profiler build --dna-id {dna-id}
```

默认读取：

```text
wx_mp/dna/{dna-id}/reports/
```

默认输出：

```text
wx_mp/dna/{dna-id}/{dna-id}.dna.md
wx_mp/dna/{dna-id}/{dna-id}.template.md
```

也可显式传入一个或多个 report 文件/目录：

```bash
wechat-style-profiler build \
  --input path/to/reports \
  --dna-id {dna-id}
```

Agent 聚合时必须：

1. 读取全部 DNA report，不能只看统计表。
2. 按每个 report 的 `weight` 和 `focus` 判断影响范围。
3. 区分高频共性、高权重偏好、局部借鉴、孤例和例外。
4. 为每个维度写聚合结论、报告依据和写作规则。
5. 确保 DNA 文档能够完整推导 template。

## DNA Template

Template 是生产模板，不是概念解释。必须从 DNA 文档的 17 个维度推导，至少包含：

- 选题角度、受众关系
- 标题类型、参考标题、封面图风格和封面 AIGC 提示词要素
- 起、承、转、合、CTA 五个固定语义部分
- 每个部分的本段任务、切入或推进方式、结构、句式、语气、素材、必须做和避免项

模板整体固定为七个部分：选题、标题、起、承、转、合、CTA。固定的是语义结构，不是物理段落数量；任一部分可以对应一个或多个自然段，也可以不出现小标题。

五个写作部分必须充分吸收 DNA 文档中的维度结论：

| 部分 | 主要推导来源 |
| --- | --- |
| 起 | 起承转合微操、选题角度、段落结构、句式节奏、语气与基调、素材或论据 |
| 承 | 起承转合微操、文章结构模式、论证逻辑、用词习惯、词汇与句式、节奏感、专业度体现 |
| 转 | 起承转合微操、修辞手法、情感表达、思维特征、句式节奏 |
| 合 | 起承转合微操、文章结构模式、情绪强度曲线、高潮与回落方式、签名式标记、语气 |
| CTA | 选题与受众关联、语气与基调、词汇与句式 |

## Update - 增量聚合

```bash
wechat-style-profiler update \
  --input wx_mp/dna/{dna-id}/reports/{new-sample}.report.md \
  --dna wx_mp/dna/{dna-id}/{dna-id}.dna.md \
  --template wx_mp/dna/{dna-id}/{dna-id}.template.md
```

脚本会合并 DNA 文档记录的历史 report 与新 report，重新计算加权统计，并保留 Agent 已完成内容。Agent 仍需重新审视聚合结论，再同步修订 DNA 文档和 template。

`--input` 可省略。省略时表示没有新增样本，只基于历史 report、既有 DNA 文档和用户输入做融合；适用于采纳另一个 DNA 文档或 template 中的局部规则。此时仍必须通过 `--user-input` 传入要融合的要求，并由 Agent 转译到具体维度。

## 用户输入转译

用户输入是参考信息，不是可直接入库的 DNA 规则。

```bash
--user-input "短句比例提升"
```

Agent 必须把输入转译到具体维度，例如：

```text
sentence-rhythm：提高短句比例，连续长句不超过两句
vocabulary-syntax：优先使用动词驱动的短表达
narrative-micro-operations：转折处使用一句成段强化节奏
```

处理要求：

1. 在 DNA 文档的“用户输入转译区”记录 affected dimensions、DNA 修改和 template 修改。
2. 把原话转译成可执行的聚合结论与写作规则。
3. Template 只写转译后的执行规则，不直接抄用户原话。
4. 与样本证据冲突时保留冲突说明，由用户选择优先级。

## Focus ID

| ID | 维度 |
|---|---|
| `topic-angle` | 选题角度 |
| `title-style` | 标题特征 |
| `cover-image` | 封面图 |
| `word-habit` | 用词习惯 |
| `vocabulary-syntax` | 词汇与句式 |
| `sentence-rhythm` | 句式节奏 |
| `tone` | 语气与基调 |
| `paragraph-structure` | 段落结构 |
| `article-structure` | 文章结构模式 |
| `argument-logic` | 论证逻辑 |
| `rhythm` | 节奏感 |
| `rhetoric` | 修辞手法 |
| `emotion` | 情感表达 |
| `thinking` | 思维特征 |
| `professionalism` | 专业度体现 |
| `signature` | 签名式标记 |
| `narrative-micro-operations` | 起承转合微操 |

## 统计与分词

脚本统计句段、标点、人称等指标；中文高频信号使用相邻二字组合，仅作为候选线索。Agent 必须回读原文判断它是否真是口头禅或签名式表达。

当前不引入 jieba。若后续候选噪声明显，可把 jieba 作为候选词挖掘器加入仓库级依赖，但分词结果不能直接作为 DNA 结论。

## 参考资料

- `references/style-17d-framework.md`
