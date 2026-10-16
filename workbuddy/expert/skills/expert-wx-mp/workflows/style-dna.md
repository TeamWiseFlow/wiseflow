# 公众号风格 DNA 创建与更新 Workflow

本 Workflow 只负责风格 DNA 三层产物的创建与更新：判断样本来源、选择目标 DNA、整理用户提供的正文和封面、调用 `wechat-style-profiler` 生成或更新 report / DNA 文档 / template。17 维提取与聚合方法以 `tools/wechat-style-profiler/` 为准。

边界说明：

- 账号初始化、定位梳理与默认 `dna-0` 初始化走 `account-setup.md`（该 workflow 会调用本 workflow 的样本获取与更新机制）。
- 账号对标分析走 `account-benchmark.md`；本 workflow 只承担对标 DNA 的三层产物生成与更新，以及采纳后并入基线 DNA 的更新。
- DNA 如何被用于写稿（含仿写、改写、小绿书）由 `content-production.md` 规定，改稿由 `editing.md` 规定；本 workflow 不描述生产过程。

DNA 只描述选题、标题、内容结构与表达策略。排版由 `generate-wenyan-theme` 独立管理，不参与 DNA 采样、组合或评分。

## 入口判断

走本 Workflow：

- “建 DNA / 更新 DNA / 提炼文章风格”
- “把这篇文章落到某个 DNA 上”
- “提取下这个账号的风格DNA”

不走本 Workflow：

- “帮我写篇稿 / 出几篇 / 照着这篇仿写 / 这篇的主题我们也写一篇 / 发小绿书”（使用 DNA 生产）-> 走 `content-production.md`
- “改改这篇 / 润色 / 换风格” -> 走 `editing.md`
- “看数据 / 复盘 / 诊断这篇” -> 走 `review.md`
- “照着这篇排版” -> 走 `generate-wenyan-theme`
- “只换颜色 / 字体 / 间距” -> 走 `generate-wenyan-theme`
- “起号 / 梳理账号定位” -> 先走 `account-setup.md`
- “分析对标账号 / 对比风格差异” -> 走 `account-benchmark.md`

## 目标 DNA 选择

1. 用户明确指定 `dna-id` 时，使用该 DNA。
2. 用户明确说“落到默认 DNA”或未指定目标时，使用 `dna-0`。
3. 用户意图是账号对标、模式对比时，走 `account-benchmark.md`，对标样本必须进入独立 `dna-id`，不得直接写入 `dna-0`。
4. 找不到目标 DNA 文档时，先走 `account-setup.md` 建立 `dna-0`，或按用户明确指定的新 `dna-id` 初始化。

默认规则：

- 除 `account-benchmark.md` 分流的对标样本外，未特别分流的新参考文章累积到 `dna-0`。
- `dna-0` 不代表某个参考账号，而是当前工作区的默认内容生产规则集。
- 用户可以随时把样本、偏好或局部借鉴明确落到任意已有 DNA。

## 存储结构

```text
wx_mp/dna/{dna-id}/
  reports/
    {sample-id}.report.md
  covers/
    {sample-id}.{ext}
  {dna-id}.dna.md
  {dna-id}.template.md
```

- 原始文章可以临时保存在 `wx_mp/ref/{dna-id}/articles/`，也可以来自用户提供的路径。
- 生成后的 DNA report 必须进入目标 DNA 的 `reports/` 目录。
- `sample-id` 必须可读且稳定；覆盖同名 report 前，先向用户说明该文件会被重算。

## 样本获取

本版不自动读取公众号链接、账号或合集。文章链接只作出处；只有名称或链接时，请用户补充正文与封面。

| 用户材料 | 处理 |
| --- | --- |
| 本地 Markdown / 文本或粘贴正文 | 读取或保存为 .md / .txt，作为 profiler 输入 |
| Word / PDF / HTML | 用当前实际可用的文件读取能力整理正文，保留标题与原文证据 |
| 文章封面或截图 | 使用用户提供的本地图片，封面通过 --cover-image 传入 |
| 公众号名、文章链接、合集目录 | 记录出处，请用户提供需要分析的实际内容 |

1. 剔除重复或正文缺失样本；截图只能支持其中实际可读的内容，缺失部分请用户补充。
2. 保留用户提供的账号、标题、出处 URL、发布时间，以及本地文件路径；缺失元数据不编造。
3. 一个样本生成单篇 report，多个样本聚合统计。账号级初始化和对标的样本要求按对应 workflow 执行；不足时先交付已有样本的观察并注明覆盖范围。
4. 阅读、转发、评论等数据只使用用户提供的截图或导出文件。
5. 封面必须由用户提供；缺少时记录未提供，不以正文图片或想象补齐。

## 建立或重建 DNA

适用场景：目标 DNA 下还没有 report，或用户要求基于当前输入整体重建。

### Step 1 - 准备样本

把可用文章整理为 `.md` / `.txt`，并确定目标 `dna-id`。未指定时使用 `dna-0`。

### Step 2 - 生成单篇 report

每篇文章执行一次：

```bash
wechat-style-profiler report \
  --input path/to/article.md \
  --dna-id {dna-id} \
  --sample-id {sample-id} \
  --cover-image path/to/cover.jpg
```

可选参数：

- `--weight N`：用户明确强调某篇参考价值时使用。
- `--focus DIMENSION`：用户明确说只借鉴标题、结构、语气等局部时使用，可重复传入。

Agent 生成 scaffold 后必须回读原文，补齐 17 维单篇结论、原文证据和可复用信号；封面图维度必须由视觉模型读取本地封面图，输出可复现的 AIGC 提示词要素。

### Step 3 - 聚合 DNA

```bash
wechat-style-profiler build --dna-id {dna-id}
```

Agent 聚合时必须读取全部 report，结合权重、focus、高频共性、高权重偏好、孤例和例外，修订：

```text
wx_mp/dna/{dna-id}/{dna-id}.dna.md
wx_mp/dna/{dna-id}/{dna-id}.template.md
```

Template 聚合要求：

1. 固定输出七个部分：选题、标题、起、承、转、合、CTA。
2. 选题和标题保持 profiler 规定的两行形态。
3. 起、承、转、合、CTA 是固定语义部分，不是固定物理段落数；每个部分可对应一个或多个自然段。
4. 每个部分必须写入 DNA 文档中对应维度的执行要求，包括本段任务、切入或推进方式、结构、句式、语气、素材、必须做和避免项。
5. 所有模板规则必须能从 DNA 文档推导；Agent 不得为了填满七部分而编造样本没有的规则。

多个样本时，定性结论必须说明覆盖多少篇；单篇特征只能写成单篇观察，不得伪装成稳定共性。

## 更新已有 DNA

适用场景：目标 DNA 已存在，新增样本、偏好、局部借鉴或表现反馈。

### 新增样本

1. 先为新文章生成属于目标 DNA 的 report。
2. 再执行：

```bash
wechat-style-profiler update \
  --input wx_mp/dna/{dna-id}/reports/{sample-id}.report.md \
  --dna wx_mp/dna/{dna-id}/{dna-id}.dna.md \
  --template wx_mp/dna/{dna-id}/{dna-id}.template.md
```

3. Agent 根据新的加权统计和 17 维证据，同步修订 DNA 文档与 template。

### 用户偏好

用户意见不是直接入库的规则。Agent 必须先理解其指向，再转译到具体维度和执行要求，例如“短句比例提升”应落到句式节奏、词汇句式、段落微操等维度。

来自另一个 DNA 文档或 template 的局部结论，也按用户提供的参考要求处理：必须记录来源 `dna-id`、采纳范围、具体规则和冲突说明，再转译到当前 DNA 的对应维度与七部分 template。已有 DNA 的局部融合不要求用户再次提供完整原文。

可传入：

```bash
--user-input "短句比例提升"
```

转译结果写入 DNA 文档的“用户输入转译区”，并以可执行规则进入 template 的对应部分。原话不能成为 template 里的抽象口号。

### 局部借鉴

用户只希望借鉴某篇的标题、开头或结构时：

1. 为该文章生成目标 DNA 的 report。
2. 用 `--focus` 限定参与影响的维度。
3. 更新 DNA 文档与 template，并在报告中保留来源和 focus 说明。

### 表现反馈

来源：`content-calibrator` 的 DNA 表现评估报告（`wx_mp/dna/{dna-id}/evals/*.eval.md`）。评估回答「这个 DNA 好不好、哪些部分好/不好」，本 workflow 负责把**用户确认采纳**的评估结论转译进 DNA。

1. 前提：评估报告已存在，且用户逐条确认了要采纳的建议（未确认的建议不动 DNA）。
2. 每条采纳建议按参考输入处理：转译到具体维度和执行要求（如「完读率持续走低，起部铺垫过长」→ 起部分切入方式 + 句式节奏维度），经 `wechat-style-profiler update --user-input` 传入。
3. 转译结果写入 DNA 文档的「表现反馈区」（与「用户输入转译区」并列），每条记录：来源 eval 文件、affected dimensions、DNA 文档修改、template 修改。
4. 同步修订 template 对应部分；表现反馈只改规则表达，不引入样本未覆盖的新风格。
5. 趋势类证据（比值走向）只支持方向性调整（加强/弱化既有规则），不支持凭空新增维度规则——新增规则仍需样本或用户输入支撑。

## DNA 使用接口

本 Workflow 不描述如何用 DNA 生产：生产 workflow 自行读取 `wx_mp/dna/{dna-id}/{dna-id}.dna.md` 与 `{dna-id}.template.md`，按 template 七部分执行，见 `content-production.md` / `editing.md`。

反馈回流判定：来自生产、改稿或复盘的成稿风格修改意见，先判断是否可复用偏好——只有可复用偏好才经本 workflow「更新已有 DNA」进入 DNA；单次修改留在稿件审阅记录，不动 DNA。参考文章的风格吸收（“把这篇的风格融入到我们的 DNA”）属于本 workflow 的新增样本 / 局部借鉴场景，不是生产流程的一部分。发布数据驱动的风格优化走「表现反馈」：`content-calibrator` 评估产出建议 → 用户逐条确认 → 本 workflow 转译进 DNA；评估本身不改 DNA。

## 对标接口

对标账号或一组对标文章不得默认落入现有 DNA；分析流程、逐项对比与采纳判断以 `account-benchmark.md` 为准。本 Workflow 只承担两件事：

1. 对标 DNA 的三层产物生成与更新：使用独立 `dna-id`（如 `dna-benchmark-{slug}`，同组后续更新复用），样本获取、report、build/update 同本 workflow 的创建/更新流程。
2. 用户采纳后，按「更新已有 DNA」执行并入基线 DNA 的更新：局部 DNA 融合、局部样本借鉴或偏好转译；默认优先局部 DNA 融合，不要求重新提取原文。

## 编排原则

- Workflow 负责选择路径和衔接工具，不复制 profiler 的 17 维定义。
- Agent 判断必须回读原文和 report，不能只依赖统计表。
- 样本统计描述内容模式，不替代事实核查、合规审核和商业判断。
- 用户确认只用于初始化方向或采纳建议，不是登记资产的前置门槛。
