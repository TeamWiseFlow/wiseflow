# 全局共享技能目录

放在这里的 skill 是 wiseflow 提供的**默认全局技能**，会安装到 openclaw/skills/，对**所有 crew** 可见（内部 crew 自动继承，外部 crew 需在 DECLARED_SKILLS 中声明）。

每个 skill 是一个子目录，包含 SKILL.md 文件。

- Crew 专属的 skill 应放在 `addons/officials/crew/<template-id>/skills/` 或 `crews/<crew-id>/skills/` 中，不要放在此处。
- 通过 addon 提供的额外全局技能放在 `addons/<addon-name>/skills/` 中，不要放在此处。

## wiseflow 默认全局技能

以下全局技能原版 openclaw 并不包含，为 wiseflow 默认提供，对所有 crew 生效：

| 技能 | 用途 | 适用范围 |
|------|------|----------|
| `smart-search` | 智能搜索：驱动浏览器在 40+ 平台实时搜索，完全免费，无需 API Key | 全部 crew 可用 |
| `browser-guide` | 浏览器操作最佳实践：登录墙、验证码、懒加载、付费墙的处理指导 | 全部 crew 可用 |
| `complex-task` | 复杂任务拆解与多步执行协调 | 全部 crew 可用；**sales-cs DENIED** |
