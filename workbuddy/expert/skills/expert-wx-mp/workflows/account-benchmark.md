# 公众号账号对标 Workflow

用于分析对标账号或一组对标文章，形成独立 DNA，并与默认或指定 DNA 逐项比较。对标样本不得直接写入 `dna-0`；用户采纳后，只有转译后的规则可融合进基线 DNA。

## 入口判断

走本 Workflow：

- “分析对标账号”
- “看看这个号和我们风格差异”
- “这几个高转发文章有什么共同模式”
- “建一个对标 DNA”

不走本 Workflow：

- 用户明确说“把这篇文章落到某个 DNA 上” -> 走 `style-dna.md`
- 只抓文章不提炼 DNA -> 直接走 `wx-mp-hunter`
- 账号定位和默认 DNA 初始化 -> 走 `account-setup.md`

## 对标 DNA 选择

1. 每个对标对象或样本组使用一个独立 DNA，建议命名为 `dna-benchmark-{slug}`。
2. 同一组对标账号或文章复用同一个 DNA 并增量更新；不因每次交互重复新建。来源差异保留在 report 证据中。
3. 对标 DNA 不进入默认内容生产，除非用户明确采纳其中某些规则。
4. 用户指定比较基线时使用该 DNA；未指定时使用 `dna-0`。

## 分析流程

### Step 1 - 获取样本

按来源调用：

| 来源 | 工具 |
| --- | --- |
| 公众号名 | 用户提供该账号近期文章链接，再逐篇 wx-mp-hunter fetch --download-cover |
| 文章链接 | `wx-mp-hunter fetch --download-cover` |
| 专题页 / 合集页 | 用户提供目录中的文章链接，再逐篇 wx-mp-hunter fetch --download-cover |
| 本地文本 + 封面图 | 正文直接输入 profiler，封面通过 `--cover-image` 传入 |

选择建议：

1. 优先选择转发、评论信号强的文章；阅读量只作次要参考。
2. `wx-mp-hunter` 不支持互动指标；转发、评论、阅读数据只能来自用户提供的数据或截图。
3. 保留用户提供的数据线索，但不得把运营效果等同于内容质量。
4. 账号级对标至少收集 10 篇代表性文章；账号可获取文章不足 10 篇时，提供全部并说明数量限制。
5. 本版从用户提供的近期文章链接取得样本；原则上至少 10 篇，账号文章不足 10 篇时提供全部并说明。
6. 单篇文章可以形成单篇观察，但不得当成账号级稳定 DNA；多个样本才分析覆盖率和共性。

### Step 2 - 建立对标 DNA

对每篇文章执行：

```bash
wechat-style-profiler report \
  --input path/to/article.md \
  --dna-id {benchmark-dna-id} \
  --sample-id {sample-id}
```

再执行：

```bash
wechat-style-profiler build --dna-id {benchmark-dna-id}
```

Agent 必须回读原文，补齐 report，并基于全部 report 修订：

```text
wx_mp/dna/{benchmark-dna-id}/{benchmark-dna-id}.dna.md
wx_mp/dna/{benchmark-dna-id}/{benchmark-dna-id}.template.md
```

对标 DNA template 也必须固定为七个部分：选题、标题、起、承、转、合、CTA。后半五个部分是语义结构，不限制实际自然段数量；每一部分都要能从对标 DNA 文档推导。

### Step 3 - 选择比较基线

读取：

```text
wx_mp/dna/{base-dna-id}/{base-dna-id}.dna.md
wx_mp/dna/{base-dna-id}/{base-dna-id}.template.md
```

默认 `{base-dna-id}` 为 `dna-0`。若 `dna-0` 不存在，先停止比较并提示用户走 `account-setup.md` 初始化，或由用户明确指定另一个基线。

### Step 4 - 逐项比较

比较必须覆盖两层：

1. **17 维 DNA 文档**：逐个维度比较规则、证据和适用条件；封面图需比较视觉特征与 AIGC 复现要素。
2. **七部分 template**：逐项比较选题、标题、起、承、转、合、CTA 的执行方式；标题部分包含封面图风格。

每个维度和模板部分都输出四类结论：

| 类别 | 判断标准 |
| --- | --- |
| 保持 | 基线已有优势，与目标受众和商业定位一致 |
| 引入 | 对标更有效，且不冲突业务事实、合规边界和用户偏好 |
| 局部借鉴 | 只适合标题、起、承、转、合、CTA 等局部场景 |
| 不采纳 | 仅依赖孤例、冲突商业定位、风险高或难稳定执行 |

每项至少说明：

1. 基线 DNA 的规则和证据。
2. 对标 DNA 的规则和证据。
3. 差异原因或适用条件。
4. 是否建议更新基线。

### Step 5 - 采纳与更新

对比结果不自动更新基线 DNA。用户明确采纳后，选择一种方式：

1. **局部 DNA 融合**：用户决定采纳对标 DNA 的某个维度或模板部分时，直接读取对标 DNA 文档 / template 中对应内容，把它当作用户提供的一条融合要求，更新基线 DNA；不需要重新抓取参考文章，也不需要重新生成对标文章的基线 report。
2. **局部样本借鉴**：仅在用户明确希望引入原文证据、权重或 focus 时，才将对标文章重新生成属于基线 DNA 的 report，并用 `--focus` 限定采纳维度。
3. **偏好转译**：用户表达“标题更冲突一点”“开头短句更多”等要求时，按 `style-dna.md` 的用户输入转译更新，并落到七部分 template 的具体执行字段。
4. **明确不改 DNA**：仅作为本次选题或写作参考，不落盘到 DNA。

局部 DNA 融合流程：

1. 明确采纳范围：17 维中的维度、七部分中的模板部分，或两者组合。
2. 读取对标 DNA 文档 / template 的对应规则、适用条件和例外。
3. 将其整理为一条可转译的输入，必须包含来源 `dna-id`、采纳范围和具体规则。
4. 在基线 DNA 上执行无新增样本的 update：

```bash
wechat-style-profiler update \
  --dna wx_mp/dna/{base-dna-id}/{base-dna-id}.dna.md \
  --template wx_mp/dna/{base-dna-id}/{base-dna-id}.template.md \
  --user-input "采纳 {benchmark-dna-id} 的标题部分：xxx"
```

5. Agent 把该输入视作用户提供的参考要求，转译为基线 DNA 的 affected dimensions、聚合结论、写作规则和七部分 template 执行字段。
6. 融合时必须检查与基线证据、业务事实、合规边界和用户偏好的冲突；冲突保留说明，不静默覆盖。

更新后必须同步修订基线 DNA 文档与 template，并保留来源说明。
