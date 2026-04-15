---
name: complex-task
description: 长程/复杂任务编排工作指导。接收复杂任务后，依次完成验收标准确认、计划拆分与自审、项目文件初始化、子任务文档创建、执行者-评估者 subagent 并行迭代、主 agent 巡检协调、聚合与整体评估，直至满足验收标准后交付。
metadata:
  {
    "openclaw":
      {
        "emoji": "🗂️",
      },
  }
---

# Complex Task — 复杂任务执行指导

**触发条件**：任务涉及多个交付阶段、需要协调多个 crew、或估计完成周期超过单次对话的长程任务。

**适用领域**：深度调研、自媒体内容生产、视频生成、故障排查与根因分析、多维度数据处理、配置新的对内/外 crew、开发新的技能等。

## 核心原则

- 1. 主 agent 只充当 planner 和 project manager，负责与用户确认、治理流程、维护文档、推动执行，不直接承担已拆分子任务的具体生产工作。
- 2. agent 与 subagent 的协作，不应主要依靠对话，而应主要依靠**交付物、任务文档、验收文档、结构化约束和明确 verdict**。
- 3. 计划确定后，所有子任务必须通过 `sessions_spawn` 交给 subagent；主 agent 不得代做任何子任务。
- 4. 每个子任务都必须有一对 subagent：执行者 + 评估者。最终聚合后还必须有一个单独的整体评估 subagent。
- 5. 子任务是否可接受，只能由对应 evaluator subagent 给出 verdict。不能因为“看到了新产物”就自行把状态改成完成。
- 6. 执行 subagent、评估 subagent、整体评估 subagent，都应优先从 `allowAgents` 白名单内选择最合适的 crew；如果 `allowAgents` 为空或没有合适的 crew，则 spawn 给自己。

## 术语

- **主 agent**：和用户直接交互，负责确认、编排、巡检、变更管理和最终交付。
- **执行者**：某个子任务的 executor subagent，负责依据 `task.md` 产出交付物。
- **评估者**：某个子任务的 evaluator subagent，负责依据 `acceptance.md` 判断该子任务是否可以交付。
- **GAN 模式**：执行者持续产出或修正交付物，评估者持续指出与验收标准之间的缺口；双方围绕产物和约束循环，直到评估者明确给出可交付 verdict。

---

## Phase 1 — 理解意图，制定验收标准

仔细阅读用户描述，提炼：

- **核心目标**：任务要解决什么问题？
- **交付范围**：最终产物是什么形式？
- **明确约束**：时间、资源、风格、平台、字数、数据范围、技术边界等。
- **隐含预期**：用户没明说但明显存在的质量底线。

基于以上分析，起草验收标准清单：

```text
验收标准：
  AC-1: <可观测、可验证的具体标准>
  AC-2: ...
  AC-N: ...
```

要求：

- 每条 AC 必须可观测、可验证。
- 禁止使用“质量好”“尽量完整”“适当优化”等模糊表述。
- 能转成明确指标、检查清单或测试脚本时，优先转成这些形式。

---

## Phase 2 — 与用户确认验收标准（L2）

向用户呈现：

```text
任务目标：<一句话概括>

验收标准：
  AC-1: ...
  AC-2: ...
  ...

请确认以上验收标准，或告诉我需要调整的部分。
```

等待用户明确确认。用户有修改时，更新标准后重新确认。**未经确认，不得进入 Phase 3。**

---

## Phase 3 — 制定执行计划，并用 subagent 自审拆分质量

### 3-1 任务拆解

将任务拆解为若干**子任务**。每个子任务必须可独立执行、可独立评估、可独立返工。每个子任务至少包含：

```text
子任务 T-N：<子任务名称>
  目标：<该子任务解决什么问题>
  交付物：<必须产出的具体内容，可量化>
  约束：<执行限制、事实边界、质量要求、来源范围等>
  验收重点：<本子任务最关键的检查点>
  执行者指派：<crew-id 或 self>
  评估者指派：<crew-id 或 self>
  模型层级：<strong / default>
  依赖：<无 / 依赖 T-X 完成后启动>
  执行方式：<并行 / 串行>
  返工策略：<被打回后如何继续>
```

规则：

- 只能指派 self 或当前 crew `allowAgents` 白名单内的 crew。
- 不得指派 external crew。
- 子任务之间的接口应尽量落实为文件路径、字段结构、输出格式或检查点。
- 同一个子任务内不要同时混入“探索、决策、执行、整合”四类责任。

### 3-2 计划自审：必须创建 planning reviewer subagent

在计划落地实施前，必须创建一个独立的 planning reviewer subagent，与主 agent 以 **GAN 模式**完成计划定稿。

做法：

1. 主 agent 先形成一版计划草案。
2. spawn 一个 planning reviewer subagent，向其提供：任务目标、已确认 AC、当前子任务拆分草案、依赖关系、指派方案、返工策略。
3. planning reviewer 只做结构化批评，不参与执行。它必须指出：
   - 哪些子任务粒度过粗或过细
   - 哪些依赖关系不合理
   - 哪些交付物与验收重点不匹配
   - 哪些子任务边界不清或容易重复劳动
   - 哪些约束缺失，导致后续执行者和评估者无法协作
4. 主 agent 根据批评修订计划；如 reviewer 仍指出问题，则继续迭代，直到收敛出可执行计划。

要求：

- 计划自审阶段的沟通必须围绕计划文本和约束本身，而不是开放式讨论。
- 未通过计划自审，不得进入 Phase 4 的执行准备。

### 3-3 Anti-pattern 检查

| # | 反模式 | 检查点 |
|---|--------|--------|
| A1 | 子任务粒度过粗 | 单子任务是否仍承载多个目标、估计耗时过长？ |
| A2 | 依赖关系不清 | 下游是否明确依赖哪个文件、产物或 verdict？ |
| A3 | 过度串行 | 无真实依赖的子任务是否错误地排成串行？ |
| A4 | 交付物与验收脱节 | 执行者产物是否无法支撑评估者判定？ |
| A5 | 文档无法独立执行 | 如果只给 `task.md` / `acceptance.md`，子 agent 是否仍能工作？ |
| A6 | 指派对外 crew | 是否有子任务错误地指派了 external crew？ |
| A7 | 返工路径缺失 | evaluator 打回后，是否没有明确返工入口？ |
| A8 | 过度依赖对话 | 关键信息是否没有提前落到文档与约束中？ |

---

## Phase 4 — 初始化项目文件夹与子任务文档

这一步不必与用户确认，但必须经过 planning reviewer subagent 的审查通过。
当 planning reviewer subagent 认为技术方案和计划都已经足够清晰、可执行时，主 agent 应立即按计划创建项目文件夹：
`./projects/<YYYYMMDD>-<task-slug>/`

```text
./projects/<id>/
  PROJECT.md
  tasks.json
  progress.md
  subtasks/
    T-1/
      task.md
      acceptance.md
      artifacts/
    T-2/
      task.md
      acceptance.md
      artifacts/
  final/
```

### 4-1 PROJECT.md

```markdown
# Project: <任务名称>

**ID**: <YYYYMMDD>-<task-slug>
**Created**: <日期时间>
**Status**: planned

## 目标
<一句话概括任务目标>

## 验收标准
- AC-1: ...
- AC-2: ...

## 执行总览
- 子任务数量：N
- 并行组：...
- 关键依赖：...
```

### 4-2 tasks.json

```json
{
  "project_id": "<YYYYMMDD>-<task-slug>",
  "created_at": "<ISO 8601>",
  "status": "planned",
  "subtasks": [
    {
      "id": "T-1",
      "name": "<子任务名称>",
      "executor_assignee": "<crew-id 或 self>",
      "evaluator_assignee": "<crew-id 或 self>",
      "dependencies": [],
      "status": "pending",
      "executor_status": "pending",
      "evaluator_status": "pending",
      "verdict": "unknown",
      "artifact_dir": "./projects/<id>/subtasks/T-1/artifacts/",
      "result_summary": ""
    }
  ]
}
```

建议状态流转：

- 顶层 `status`：`planned` → `executing` → `aggregating` → `overall_review` → `done`
- 子任务 `status`：`pending` → `running` → `awaiting_verdict` → `accepted` | `needs_rework` | `blocked`
- `verdict` 只能由 evaluator 或 overall evaluator 的正式结论驱动。

### 4-3 progress.md

```markdown
# Progress Log — <任务名称>

## [<时间戳>] Phase 4: 项目初始化完成
- 项目目录：./projects/<id>/
- 子任务数量：N 个
- 已创建子任务文档：T-1 ... T-N
```

### 4-4 为每个子任务创建两个文档

必须在每个子任务目录下创建两个 Markdown：

- `task.md`：详细描述子任务内容、目标、上下文、依赖、产物位置、执行约束
- `acceptance.md`：详细描述子任务验收标准、检查方法、拒收条件、评估输出格式

建议模板：

```markdown
# task.md
## 目标
## 输入与上下文
## 交付物
- 路径：./projects/<id>/subtasks/T-N/artifacts/
- 必须包含：...
## 约束
## 禁止事项
```

```markdown
# acceptance.md
## 必须满足
- AC-TN-1: ...
- AC-TN-2: ...
## 拒收条件
## 评估输出格式
- verdict: accepted | needs_rework | blocked
- findings:
  - <编号化问题清单>
- evidence:
  - <对应文件 / 事实 / 缺口>
```

---

## Phase 5 — 执行：每个子任务都以“执行者-评估者”双 subagent 并行推进

### 5-1 spawn 规范

每个子任务都必须创建两个 subagent：

- executor subagent，负责依据 `task.md` 执行
- evaluator subagent，负责依据 `acceptance.md` 评估

关键约束：

- 执行者和评估者的协作，应以 `task.md`、`acceptance.md`、`artifacts/` 内产物和结构化 verdict 为中心。
- 允许最小必要澄清，但不得把“靠聊明白需求”当作主要协作方式。
- 如果评估者没有明确给出 `accepted`，该子任务就不能进入可交付状态。

### 5-2 Executor prompt 要求

executor 至少应收到：

- `task.md` 路径
- `acceptance.md` 路径
- 产物目录路径
- 明确要求：优先通过更新交付物解决问题，而不是长篇解释

建议 executor 输出格式：

```text
执行回合：
  子任务：T-N
  本轮修改产物：
    - <文件路径>
  本轮结果摘要：
    - <1-3 条>
  需评估项：
    - <请 evaluator 针对哪些标准检查>
```

### 5-3 Evaluator prompt 要求

evaluator 至少应收到：

- `acceptance.md` 路径
- `task.md` 路径
- 产物目录路径
- 明确要求：只根据产物和标准做判断，不为执行者脑补完成度

建议 evaluator 输出格式：

```text
评估回合：
  子任务：T-N
  verdict: accepted | needs_rework | blocked
  findings:
    1. <问题或通过项>
    2. ...
  evidence:
    - <文件路径 / 事实依据 / 缺失项>
  next_action:
    - <执行者下一轮应修改什么>
```

### 5-4 GAN 式循环

每个子任务都按以下循环推进，直到 evaluator 给出 `accepted`：

1. 执行者依据 `task.md` 产出或修改交付物。
2. 评估者依据 `acceptance.md` 对产物做批判性检查。
3. 如果 verdict 为 `needs_rework`，执行者只针对 findings 返工，不重做无关部分。
4. 如果 verdict 为 `blocked`，主 agent 介入，澄清事实、修正文档或向用户确认。
5. 只有当 verdict 为 `accepted` 时，主 agent 才能把该子任务状态写为 `accepted`。

### 5-5 巡检：主 agent 必须持续跟进，但不代替评估

Phase 5 的巡检仍然是主 agent 的职责，至少包括两类工作。

**一类：推进卡住的 subagent**

- 如果任何执行者或评估者明显卡住了，例如长时间无响应、上游模型挂起、上下文中断，应主动提示简短指令，例如“继续”。
- 巡检的目标是恢复执行，不是替子 agent 完成任务。

**二类：处理问题与偏差**

- 如果执行者或评估者发现 `task.md` 或 `acceptance.md` 与事实不符，应向主 agent 提问。
- 主 agent 能判断的，直接答复并同步更新文档。
- 主 agent 拿不准的，必须反馈用户；待用户确认后，及时更新相应文档，再回复相关 subagent。
- 文档一旦更新，必须通知受影响的执行者和评估者，避免双方继续基于旧约束工作。

### 5-6 状态更新纪律

主 agent 不得：

- 因为 `artifacts/` 里出现新文件，就直接把子任务标记为完成。
- 因为执行者自称“已经好了”，就跳过 evaluator verdict。
- 因为主 agent 自己觉得“看起来差不多”，就代替 evaluator 做接受判定。

只有以下动作允许更新子任务状态：

- spawn 后，可改为 `running`
- 执行者提交产物待审时，可改为 `awaiting_verdict`
- evaluator 明确判定通过时，可改为 `accepted`
- evaluator 明确判定返工时，可改为 `needs_rework`
- 明确存在阻塞且需主 agent 介入时，可改为 `blocked`

巡检记录建议追加到 `progress.md`：

```markdown
## [<时间戳>] 巡检
- T-1: evaluator 判定 needs_rework，已要求执行者继续
- T-2: evaluator 卡住，已发送“继续”
- T-3: task.md 与事实冲突，已向用户确认并更新文档
```

---

## Phase 6 — 聚合结果

所有子任务都获得对应 evaluator 的 `accepted` verdict 后，主 agent 才能进入聚合阶段。

聚合时：

1. 检查 `tasks.json`，确认所有相关子任务 `status = accepted`
2. 读取各子任务产物，整合为统一最终成果
3. 将项目顶层状态更新为 `aggregating`
4. 在 `./projects/<id>/final/` 下生成聚合产物
5. 在 `progress.md` 追加记录

```markdown
## [<时间戳>] Phase 6: 结果聚合完成
- 已接受子任务：X / N
- 聚合产物：./projects/<id>/final/
```

**注意**：在 Phase 6 完成前，不必创建整体评估 subagent。此时各子任务的可接受性，已经由各自 evaluator 负责。

---

## Phase 7 — 整体评估与返工闭环

Phase 6 聚合完成后，必须再 spawn 一个**独立的 overall evaluator subagent**，专门评估最终整合结果。

它至少应读取：

- `PROJECT.md`
- 最终成果文件
- 全局 AC
- 必要时读取关键子任务的 `acceptance.md` 与产物摘要

其职责：

- 判断最终整合结果是否真正满足全局 AC
- 识别是“已有子任务未做到位”，还是“需要新增子任务”
- 输出结构化 verdict，而不是泛泛而谈

建议输出格式：

```text
整体评估：
  verdict: accepted | needs_rework
  findings:
    1. <全局缺口>
    2. ...
  impacted_subtasks:
    - <T-2>
    - <需要新增 T-5>
  rationale:
    - <为何当前聚合结果仍不满足全局 AC>
```

### 7-1 若整体评估通过

如果 overall evaluator 明确给出 `accepted`，进入 Phase 8。

### 7-2 若整体评估未通过

如果 overall evaluator 给出 `needs_rework`，主 agent 必须基于 findings 组织返工：

- 如果是已有子任务的缺口：更新对应 `task.md` 或 `acceptance.md`
- 如果是新增范围：创建新的子任务目录、`task.md`、`acceptance.md`
- 为受影响子任务重新创建或重启执行者与评估者
- 返回 Phase 5 执行，再经过 Phase 6 聚合，最后重新进入 Phase 7

这个循环应持续，直到 overall evaluator 认为可以交付。

如果返工轮次明显增多，主 agent 应主动向用户汇报风险、差距和拟调整方案；但不能跳过 overall evaluator 的最终判定。

---

## Phase 8 — 交付

当且仅当 overall evaluator 明确接受后：

1. 将 `tasks.json` 顶层 `status` 更新为 `done`
2. 在 `progress.md` 追加最终记录

```markdown
## [<时间戳>] Phase 8: 任务完成
- 整体评估：accepted
- 最终产物：./projects/<id>/final/
```

向用户交付：

```text
任务完成

项目目录：./projects/<id>/

最终产物：
  <路径 / 摘要>

验收确认：
  AC-1: ✅ ...
  AC-2: ✅ ...

整体评估：
  accepted
```

交付后执行常规 closeout。

---

## Anti-patterns — 常见失败模式

| # | 反模式 | 后果 | 应对 |
|---|--------|------|------|
| P1 | 子任务粒度过粗 | 单个执行者长期失控或难以评估 | 每个子任务只负责一个清晰目标 |
| P2 | 过度依赖对话 | 需求漂移、理解不一致、难追责 | 关键约束必须落到 `task.md` / `acceptance.md` |
| P3 | 执行者无 evaluator 配对 | 无法形成独立验收闭环 | 每个子任务必须成对 spawn |
| P4 | 见产物就改状态 | 误把“有文件”当“可交付” | 只有 evaluator verdict 才能决定接受 |
| P5 | 文档与事实脱节 | 子 agent 基于错误约束持续返工 | 一旦发现偏差，主 agent 立即更新文档并广播 |
| P6 | 过早整体评估 | 还未完成子任务验收就提前总评 | 只有 Phase 6 后才创建 overall evaluator |
| P7 | 指派 external crew | Spawn 失败或流程中断 | 仅指派 self 或 `allowAgents` 白名单内 crew |
| P8 | 主 agent 越权代评 | 评估失真，流程失守 | 主 agent 只治理流程，不代替 evaluator 下 verdict |

---

## Plan Mutation Protocol — 执行中计划变更

遇到以下情况，需要修改计划或文档时，遵守正式变更流程。

### 触发场景

- **子任务文档与事实冲突**：先定位冲突点，必要时向用户确认，再更新 `task.md` / `acceptance.md`
- **整体评估发现新缺口**：新增子任务，或拆分现有子任务
- **用户主动修改目标或范围**：先判断是否影响全局 AC；影响则重走对应确认流程
- **关键依赖变化**：调整子任务依赖和执行顺序，并同步受影响的执行者和评估者

### 变更记录

所有变更必须在 `progress.md` 追加：

```markdown
## [<时间戳>] 计划变更
- 变更原因：<触发场景>
- 变更内容：<新增 / 修改 / 取消哪个子任务，或更新哪份文档>
- 影响范围：<受影响的子任务 / 评估者 / 聚合结果>
- 用户确认：<已确认 / 无需确认>
```

### 必须重走确认的内容

以下内容一旦已获用户确认，后续若要修改，必须重新与用户确认：

- 全局验收标准（AC）
- 最终交付物形式
以下内容通常不需要单独等待确认，但发生重大变化时，应及时同步用户：

- 子任务总体拆分逻辑
- 关键执行顺序与重大依赖关系
