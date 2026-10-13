# Project Application（项目申报）

帮用户准备、跟踪各类外部申报项目：高新技术企业认定、加速器申请、政府补贴、行业奖项。涵盖材料生成 + 时间线管理 + 状态跟踪。

软著 / 商标 / 专利等知识产权申报不在本 workflow 范围，不承接。

**依赖**：当前实际可用的公开资料检索能力（行业数据 / 竞品分析）、Investor Materials Workflow（BP / One-Pager）、`ir-record`（applications 表状态跟踪）。

## 适用场景

用户说：

- "我想申请高新技术企业认定 / 专精特新 / 科技型中小企业"
- "我看到 X 加速器在招创业团队，能帮我准备申请吗"
- "政府有 Y 补贴项目，截止日期 Z，能帮我看下材料吗"
- "我要申报 X 行业奖项"

## 常见申报类型

| 类型 | 典型材料 | 材料协作 |
|------|---------|---------|
| 高新技术企业认定 | 知识产权 + 研发费用 + 人员名单 + 财务审计 | 当前实际可用的公开资料检索能力 |
| 加速器申请 | BP + One-Pager + 团队介绍 + 牵引数据 | Investor Materials Workflow（包内） |
| 政府补贴 | 申报书 + 财务报表 + 项目实施方案 | 当前实际可用的公开资料检索能力（行业数据）|
| 行业奖项 | 案例描述 + 客户证言 + 量化数据 | 当前实际可用的公开资料检索能力（行业 baseline）|

---

## 工作流

### Step 1: 问清申报项目

问用户：

- **申报项目名称**（具体哪个 / 哪个机构的）
- **截止日期**
- **所需材料清单**（用户已知；如未知 → 让用户去官网看要求，AI 不替用户读官网）
- **已有什么材料** / **缺什么材料**

### Step 2: 拆任务 + 材料协作

按材料清单拆任务，按边界委派：

| 材料 | 委派给 |
|------|--------|
| 行业市场数据 / 竞品分析 | 当前实际可用的公开资料检索能力 |
| BP / One-Pager | Investor Materials Workflow（包内） |

各部分输出后，整合成"申报书完整版"。

### Step 3: 时间线 + 提醒

写入 `ir-record` 的 `applications` 表：

```bash
ir-record record-application \
  --name "2026 国高认定" \
  --type "high-tech-enterprise" \
  --organizer "科技部" \
  --deadline "2026-09-30" \
  --status "planning"
```

截止提醒默认靠用户反馈 / 主动查询（`ir-record query-applications --upcoming 7`）；用户希望自动提醒时，启用定时模式（见包内 `scheduling.md`），心跳会查即将截止的申报。

### Step 4: 状态跟踪

```
planning → preparing → submitted → reviewing → approved/rejected
```

每状态变更：

```bash
ir-record update-application --id <rowid> --status <new>
```

跟踪结果（如"已提交 / 已通过 / 未通过"）也写入 `applications` 表。

---

## 与其他环节的关系

- **当前实际可用的公开资料检索能力**（顶层技能）：行业数据（多个申报类型需要）
- **Investor Materials Workflow**（包内）：加速器申请等需要 BP / One-Pager
- **商业模式打磨**（IR 模式 1）：申报前先打磨商业模式（很多申报材料要先有清晰的商业故事）

---

## Pitfalls

### pitfall: 替用户读官网

- **症状**：用户问"X 加速器需要什么材料"，Agent 直接编
- **workaround**：让用户去官网看，AI 协助整理已读到的内容

### pitfall: 跨截止日期未提醒

- **症状**：用户提了 deadline 但没在 ir-record 记
- **workaround**：**所有** deadline 必记 `applications` 表；需要自动提醒时启用定时模式（见 `scheduling.md`）

### pitfall: 申报材料不更新状态

- **症状**：用户说"我已经提交了"，但 `applications.status` 还是 preparing
- **workaround**：每次用户反馈进度，立即调 `ir-record update-application`

---

## Notes

- 财务审计报告、税务证明等"硬材料"由用户/会计师提供，AI 不替生成
- 申报通过率不承诺，AI 只保证材料齐整 / 表达清晰 / 时间线追踪
