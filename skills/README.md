# 全局共享技能目录

放在这里的 skill 会安装到 openclaw/skills/，对**所有 crew** 可见（内部 crew 自动继承，外部 crew 需在 DECLARED_SKILLS 中声明）。

每个 skill 是一个子目录，包含 SKILL.md 文件。Agent 专属的 skill 应放在 `crews/<template-id>/skills/` 中，不要放在此处。

## 当前全局技能

| 技能 | 用途 | 所需环境变量 | 备注 |
|------|------|------------|------|
| `siliconflow-img-gen` | 文生图 / 改图（SiliconFlow Images API） | `SILICONFLOW_API_KEY` | selfmedia-operator / designer / video-producer 常用 |
| `siliconflow-video-gen` | 文生视频 / 图生视频（SiliconFlow Video API，Wan2.2） | `SILICONFLOW_API_KEY` | selfmedia-operator / video-producer 常用 |
| `council` | 四声议会决策：模糊决策时召集 Architect / Skeptic / Pragmatist / Critic 并行子 agent 进行结构化辩论 | 无 | 全部 crew 可用（sales-cs 除外） |
| `complex-task` | 复杂任务拆解与多步执行协调 | 无 | 全部 crew 可用；sales-cs DENIED（客服场景不适用） |
| `connections-optimizer` | 人脉关系网络优化与拓展建议 | 无 | **仅 business-developer**；其余 internal crew DENIED |
| `email-ops` | 批量邮件撰写与发送 | SMTP 配置 | **仅 business-developer**；其余 internal crew DENIED |
| `pitch-deck` | 融资 / 商务演示文稿生成 | 无 | **仅 business-developer**；其余 internal crew DENIED |
| `social-graph-ranker` | 社交图谱关键节点分析与排序 | 无 | **仅 business-developer**；其余 internal crew DENIED |

> official-plus addon 额外提供的全局技能（wx-mp-hunter、xhs-hunter、wxwork-moments、wxwork-drive 等）参见 `addons/official-plus/README.md`。
