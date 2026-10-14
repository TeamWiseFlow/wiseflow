---
name: xiaobei-video-handoff
description: Prepare finished videos for social media operations or hand off a confirmed production brief to an actually available WorkBuddy expert or skill.
description_zh: 接收用户成片并准备运营材料，或将明确制作需求交给实际可用的 WorkBuddy 专家或技能。
description_en: Finished-video campaign preparation and production handoff through available WorkBuddy capabilities.
version: 0.3.3
author: TeamWiseFlow
user-invocable: true
---

# 视频成片运营与制作交接

## 用户已经有成片

确认 WorkBuddy 能访问用户给出的最终视频文件；链接只代表来源，不能假装已经下载或观看。已有文件可使用本次可用的媒体检查/播放能力了解内容、时长、比例、字幕和声音。没有检查能力时明确哪些参数由用户提供，不能编造检测结果。

结合业务事实和目标账号，交付标题、简介、话题、封面文案、目标平台及发布安排。用户有封面时优先使用；需要封面图片时只调用实际可用的制作技能。稿件、封面描述和文件必须区分。

已确认成片和发布授权时，按目标平台原生专家 workflow 执行；缺少工具时交付完整发布材料，不声称已上传或发布。

抖音侧仅交付发布材料。用户本次实际提供了外部发布入口时，按该入口检查双封面与声明；交付或保存封面图片不等于平台双封面设置成功。只有所接发布工具的实际检查证明封面和需要的 AIGC 声明已保存，才继续提交；声明/封面弹窗卡住时保留成片与草稿，不绕过声明。

## 已有素材先直接加工

抽段、拼接、配乐、字幕与画面集锦直接使用 `video-edit`；按讲话内容做口播轻剪用 `talking-head-cut`，交付前用 `video-review` 自检。封面用 `awk-img-gen`，原生群聊与问答卡片用 `native-ui-card`。这些技能和脚本已随本包提供，不将已有素材加工一概转给外部专家。

## 需要从零制作完整视频

根据 [Brief 模板](templates/brief.md) 整理产品事实、目标读者、主题、信息要点、CTA、素材绝对路径、口播稿、目标平台、时长/比例与交付要求。只保留有依据的要求，不预设当前制作技能不支持的工作流名。

先核对用户当前已安装/可调用的 WorkBuddy 专家、技能、工具说明和文件权限。不存在可用列表或调用入口时，直接交付可复制 Brief，并请用户返回最终成片与封面；不要编造专家名或市场 ID。

有真实调用入口时，读取所选能力说明，判断能否完成所需媒体类型和输出，再把确认的 Brief 与它可访问的素材交给它。没有 AgentTool 时不能假装召唤成功；仅生成调用建议也不代表已经委托。

确认用户已授权的制作范围；外部能力涉及新增付费时按本次费用约定处理。用户已确认需求与预算后继续，不因执行阶段重复确认同一事项。

返回产物后核对实际视频、封面和交付说明，按 Brief 验收，再交回发布流程。失败或未完成时回报实际状态，不代替外部制作能力偷偷启用本包没有的渲染器。

小贝负责业务、选题、用户口播终稿和发布文案；外部制作方负责具体制作实现。成片未返回前，小贝可以继续其他内容工作，不把该视频标记为可发布。
