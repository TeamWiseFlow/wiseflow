---
name: complex-task
description: 长程/复杂任务编排工作指导。接收复杂任务后，依次完成验收标准确认、执行计划制定、项目文件初始化、子模块 spawn 并行执行、巡检汇总、结果迭代，直至满足验收标准后交付。
metadata:
  {
    "openclaw":
      {
        "emoji": "🗂️",
      },
  }
---

# Complex Task — 复杂任务执行��导

**触发条件**：任务涉及多个交付阶段、需要协调多个 crew、或估计完成周期超过单次对话的长程任务。

**适用领域**：深度调研、自媒体内容生产、视频生成、故障排查与根因分析、跨平台发布、多维度数据处理等通用复杂任务。

---

## Phase 1 — 理解意图，制定验收标准

仔细阅读用户描述，提炼：

- **核心目标**：任务要解决什么问题？
- **交付范围**：产物是什么形式（报告、内容、数据、分析结论、视频脚本…）？
- **明确约束**：已知的限制条件（时间、资源、风格、平台、字数…）
- **隐含预期**：用户可能没说出口但必须满足的质量底线

基于以上分析，起草 **验收标准清单**：

```
验收标准（示例格式）：
  AC-1: <可观测、可验证的具体标准>
  AC-2: ...
  AC-N: ...
```

> 每条验收标准必须可观测、可验证，避免模糊表述（如"质量好"），改用具体指标（如"报告不少于 3000 字"、"覆盖 5 个以上信息源"、"包含配图方案"、"根因分析涵盖 X 个维度"）。

---

## Phase 2 — 与用户确认验收标准（L2）

将 Phase 1 的验收标准呈现给用户：

```
任务目标：<一句话概括>

验收标准：
  AC-1: ...
  AC-2: ...
  ...

请确认以上验收标准，或告诉我需要调整的部分。
```

等待用户明确确认。用户有修改时，更新标准后重新确认。**未经确认，不得进入 Phase 3。**

---

## Phase 3 — 制定执行计划并初始化项目文件夹

### 3-1 任务拆解

将任务拆解为若干**子模块**，每个子模块包含：

```
模块 M-N：<模块名称>
  交付物：<必须产出的具体内容，可量化>
  约束：<执行限制、依赖关系、质量要求>
  指派：<crew-id 或 self>
  依赖：<无 / 依赖 M-X 完成后启动>
  执行方式：<并行 / 串行>
```

**指派规则（关键约束）**：
- 只能指派自己（self）或当前 crew `allowAgents` 白名单内的 crew
- 不得指派 external crew（external crew 不接受 spawn）
- 如需某 crew 的能力但 `allowAgents` 不包含它，在计划中标注"需人工路由"，在 Phase 4 向用户说明

**执行顺序**：
- 无依赖关系的模块：标注**并行**，执行时同时 spawn
- 有依赖关系的模块：标注依赖链，按序执行

### 3-2 初始化项目文件夹

完成任务拆解后，立即在当前工作目录创建项目文件夹，格式为
`./projects/<YYYYMMDD>-<task-slug>/`（task-slug 用英文小写+连字符表示任务主题，例如 `ai-industry-research`）：

```
./projects/<id>/
  PROJECT.md      ← 项目概览与验收标准（人类可读）
  features.json   ← 模块清单与状态追踪（机器可读）
  progress.md     ← 执行日志（按时间追加，永不覆盖）
  outputs/        ← 各子模块交付物存放目录
    M-1/
    M-2/
    ...
```

**PROJECT.md 内容**：

```markdown
# Project: <任务名称>

**ID**: <YYYYMMDD>-<task-slug>
**Created**: <日期时间>
**Status**: planning

## 目标

<一句话概括任务目标>

## 验收标准

- AC-1: ...
- AC-2: ...

## 备注
```

**features.json 内容**：

```json
{
  "project_id": "<YYYYMMDD>-<task-slug>",
  "created_at": "<ISO 8601>",
  "status": "planning",
  "modules": [
    {
      "id": "M-1",
      "name": "<模块名称>",
      "deliverable": "<交付物描述>",
      "constraints": "<约束>",
      "assigned_to": "<crew-id 或 self>",
      "dependencies": [],
      "parallel_group": 1,
      "status": "pending",
      "result_summary": ""
    }
  ]
}
```

status 流转：`pending` → `in_progress` → `done` | `failed`

**progress.md 初始内容**：

```markdown
# Progress Log — <任务名称>

## [<时间戳>] Phase 3: 项目初始化完成
- 项目目录：./projects/<id>/
- 模块数量：N 个（并行 M 个 / 串行 K 个）
```

---

## Phase 4 — 与用户确认执行计划（L3）

将完整计划发送给用户：

```
执行计划（共 N 个模块）

  项目目录：./projects/<id>/

  M-1: <名称>  →  指派: <crew>  [并行组 1]
    交付物: ...
    约束: ...

  M-2: <名称>  →  指派: <crew>  [并行组 1]
    交付物: ...
    约束: ...

  M-3: <名称>  →  指派: <crew>  [依赖 M-1 + M-2，串行]
    交付物: ...
    约束: ...

  执行顺序：并行组 1 [M-1, M-2]  →  M-3

请确认计划，或指出需要调整的部分。
```

等待用户明确确认。**L3 确认，未经确认不得 spawn 任何子 agent。**

用户确认后，更新 features.json 顶层 `status` 为 `executing`，并在 progress.md 追加：

```markdown
## [<时间戳>] Phase 4: 用户确认，开始执行
```

---

## Phase 5 — 执行：spawn 子模块

### 5-1 spawn 规范

每次调用 `sessions_spawn` 前：
1. 将该模块在 features.json 中的 `status` 更新为 `in_progress`
2. 在 progress.md 追加启动记录

**结构化 spawn 任务描述**（每个子模块的完整 prompt）：

```
## 任务：<模块名称>

### 目标与交付物
<具体说明要达成的结果，可量化；说明产物应存放到以下路径>
产物存放路径：./projects/<id>/outputs/<M-N>/

### 约束
<执行限制：风格、格式、字数、平台、信息来源范围等>

### 上下文
<前置模块的关键输出，或任务背景中需要了解的信息>
<无前置依赖时写：无>

### 完成标志
<明确的完成信号，例如：生成 report.md 并包含 X 个小节 / 输出 JSON 含 result 字段 / 确认视频脚本字数不少于 N>

完成后将产物路径和结果摘要汇报给我。
```

### 5-2 并行与串行控制

- **并行组**：同一组内的模块同时调用 `sessions_spawn`，无需等待单个完成
- **串行**：等待前置模块完成并收到结果摘要后，再 spawn 后续模块

### 5-3 巡检（Check-in）

对于耗时较长的并行阶段，每等待一段时间后执行一次巡检：

1. 检查 `./projects/<id>/outputs/<M-N>/` 目录是否有新产物生成
2. 如模块已完成但尚未主动汇报，确认其状态并更新 features.json
3. 在 progress.md 追加巡检记录：

   ```markdown
   ## [<时间戳>] 巡检
   - M-1: done — 产物: ./projects/<id>/outputs/M-1/report.md
   - M-2: in_progress — 尚未产出文件
   ```

4. 如某模块超出预估时间 × 2 仍未完成，在 progress.md 记录超时警告，并向用户简要汇报，请求指导

---

## Phase 6 — 聚合结果

所有子模块执行完毕后：

1. 遍历 features.json，确认所有模块 `status = done`
2. 检查是否有 `status = failed` 的模块 → 记录缺口，继续聚合，后处理缺口
3. 读取各模块产出，整合为**统一的最终成果**（格式由 Phase 1 的交付范围决定）
4. 更新 features.json 顶层 `status` 为 `reviewing`
5. 在 progress.md 追加：

   ```markdown
   ## [<时间戳>] Phase 6: 结果聚合完成
   - 模块完成：X / N
   - 产物清单：<列出各模块主要产物路径>
   ```

---

## Phase 7 — 验收评估与迭代

逐条检查验收标准：

```
验收评估：
  AC-1: ✅ / ❌  — <简要说明>
  AC-2: ✅ / ❌  — ...
  ...

结论：<全部通过 / 存在 N 条未达标>
```

**若全部通过** → 进入交付（Phase 8）

**若存在未达标项** → 针对性返工：
- 识别导致未达标的子模块
- 仅对相关模块重新制定修复计划（不重跑整个任务）
- 向用户简要说明差距和修复方案（L2）
- 用户无异议后，spawn 修复子模块，更新 features.json 中对应 `status` 为 `in_progress`，返回 Phase 6 重新评估
- **迭代上限：3 轮**。若第 3 轮仍有未达标项，暂停并向用户汇报，请求指导

---

## Phase 8 — 交付

更新 features.json 顶层 `status` 为 `done`，在 progress.md 追加最终记录：

```markdown
## [<时间戳>] Phase 8: 任务完成
- 验收结果：全部通过
- 迭代轮次：N 轮
- 最终产物：./projects/<id>/outputs/
```

向用户交付：

```
任务完成！

项目目录：./projects/<id>/

最终产物：
  <产物路径 / 内容摘要>

验收确认：
  AC-1: ✅ ...
  AC-2: ✅ ...

备注：<迭代轮次、主要挑战、可复用的经验>
```

交付后执行常规 Closeout（参见 TEMPLATES.md）。
