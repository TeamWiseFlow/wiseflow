# 全局共享技能目录

放在这里的 skill 会安装到 openclaw/skills/，对**所有 crew** 可见（内部 crew 自动继承，外部 crew 需在 DECLARED_SKILLS 中声明）。

每个 skill 是一个子目录，包含 SKILL.md 文件。Crew 专属的 skill 应放在 `addons/officials/crew/<template-id>/skills/` 或 `crews/<crew-id>/skills/` 中，不要放在此处。

## wiseflow 额外提供的默认全局技能

如下全局技能原版 openclaw 并不包含，为 wiseflow 额外提供：

| 技能 | 用途 | 所需环境变量 | 适用范围 |
|------|------|------------|----------|
| `complex-task` | 复杂任务拆解与多步执行协调 | 无 | 全部 crew 可用；**sales-cs DENIED**（客服场景不适用） |
| `connections-optimizer` | 人脉关系网络优化与拓展建议 | 无 | **仅 business-developer**；其余 crew DENIED |
