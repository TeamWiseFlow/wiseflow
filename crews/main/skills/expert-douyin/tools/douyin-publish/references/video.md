# 抖音视频发布

前置执行 `douyin-publish check`，未登录用 `douyin-publish login` 完成登录。登录态只留在 Camoufox profile，不使用 login-manager 或 hunter 的 API 会话。

完整流程优先使用统一入口预览，已有发布授权时加 `--confirm`：

```bash
douyin-publish video --video /绝对路径/video.mp4 --title "标题" --caption @/绝对路径/body.txt --cover-vertical /绝对路径/cover-vertical.jpg --cover-horizontal /绝对路径/cover-horizontal.jpg
```

统一入口及分步 `fill/run` 的 `--caption` 均支持 `@UTF-8文件路径`。先保存纯正文和话题，再传 `--caption @/绝对路径/body.txt`；文件读取失败时在浏览器操作前停止，不把多行正文拼进命令。

必须提供竖封面和横封面。按 **3:4 竖封面 + 4:3 横封面**制作，两张都要核对；关键文字避开四周 15% 边缘区。比例不符时脚本等比缩放、补浅灰底，保留完整内容；不要居中裁切导致边缘文字缺失。补底不能代替平台质量检测：`COVER_TEXT_UNSAFE` 时调整文字安全区；`COVER_BORDER_TOO_LARGE`（封面边框面积过大）时按目标比例重新构图、减少宽边框；`COVER_QUALITY_REJECTED`（封面不佳）时更换封面。不反复加宽补底、裁掉文字或绕过检测。

上传必须等视频可播放且上传/转码状态结束，不能把标题框出现当作上传完成。脚本通过真实键盘输入并读回标题和简介；提交前检查视频、标题、双封面与 AIGC 声明，任一缺失停止。

AIGC 声明与封面弹窗可能使用 `role="dialog"`、`role="modal"` 或 `semi-modal` 结构。脚本按可见性与弹窗内容识别唯一目标，嵌套容器不算多个弹窗，确认/完成按钮只在该目标内点击。同类弹窗不唯一时停止，不猜按钮、不用 Escape 绕过未保存的 AIGC 声明。续编 `fill` / `cover` 会先完成已经打开的声明弹窗；声明或封面弹窗未保存关闭前，页面上的文字/旧预览不算设置成功。

按入口上的「竖封面」/「横封面」定位，不能假设两个入口的 DOM 排列顺序。需要悬停才显示「编辑封面」时，先悬停所选缩略图，再点其中的编辑入口，不把外层标签容器当按钮。打开编辑器前，先在页面「预览封面/标题」中激活目标方向，并读回激活状态；编辑器侧边预览沿用这个方向。已有编辑器遮挡错误方向的页面选项卡时停止并保留草稿，不隔着弹窗强制点击。每次上传前再核对编辑器标题或其内部激活选项卡；页面预览方向不能代替编辑器类型校验。当前 Semi 的两个图片输入框用于首次上传/替换，均属于同一编辑器；已有上传预览时选择替换框，否则使用首次上传框。首次上传框可能因数量上限忽略后续文件，捕获选择事件不代表应用已更新预览。其他结构必须有唯一图片输入框，不使用全局 file input 下标。

简介按完整正文校验，忽略 Slate 话题节点引入的 Unicode 空白和不可见格式字符；短标题、空简介和短信验证码同样支持。设置封面后若视频元素消失，脚本只在已确认的当前草稿页重开一次，等待视频恢复，再核对视频时长、标题、简介、双封面及 AIGC 声明。返回 `DRAFT_CHANGED_AFTER_COVER` 时保留页面核查，不重传或提交。

需要页面诊断或分步处理时，用对应 wrapper 子命令。各步骤的中间态由脚本保存，不自行拼 JS、file input 序号或发布结果：

| 操作 | 命令 |
|---|---|
| 打开上传页 | `douyin-publish video open-page` |
| 上传视频并等待就绪 | `douyin-publish video upload --video /绝对路径/video.mp4` |
| 续编未提交草稿 | `douyin-publish video edit-draft` |
| 在当前草稿补传缺失视频 | `douyin-publish video upload --resume-draft --video /绝对路径/video.mp4` |
| 填表和声明 | `douyin-publish video fill --title "标题" --caption @/绝对路径/body.txt` |
| 上传并保存双封面 | `douyin-publish video cover --cover-vertical /绝对路径/vertical.jpg --cover-horizontal /绝对路径/horizontal.jpg` |
| 检查当前页面与任务 | `douyin-publish video status` |
| 校验后实际提交 | `douyin-publish video publish --confirm` |
| 核查本次提交结果 | `douyin-publish video resume` 或 `douyin-publish video get-link` |

`run` 默认只生成本地预览，`publish` 默认只提示核对当前草稿；两者只有加 `--confirm` 才实际发布。先核对账号、成片、双封面及文案；已有发布授权时继续提交。共享持久化 session `douyin`，不改 session 名，不并行发布或取数。AIGC 声明失败即停，不删除声明绕过。发现旧草稿返回 `DRAFT_PRESENT`，不自动放弃；续编前核对草稿与本次成片。

补传视频可能重建表单，清空标题、简介、封面和 AIGC 声明；`upload --resume-draft` 后重新执行 `fill` 和 `cover`，再 `publish`。`COVER_UPLOAD_TIMEOUT` 不代表封面一定没上传；先用 `status` 核查，再续编当前页面，不重传整段视频。脚本在文件选择事件中捕获本次文件（页面可能随即清空 file input），每次检查重新定位当前封面弹窗；以本次选择加新预览来源或相同文件内容判断成功，不只依赖 img load、旧 DOM 节点或任意已加载图片。文件与预览比较仅留在页面内存，不写 localStorage 或输出完整图像数据。

文件字节完全匹配本次选择时，可直接确认预览；编辑器重新编码 JPEG 并复用预览来源时，脚本核对完整图像尺寸与像素，只允许小幅编码差异，局部文字变化也须拒绝。无法确认文件内容时，新预览来源还必须符合目标比例。所有路径都须通过编辑器类型校验。`COVER_EDITOR_MISMATCH` / `COVER_PREVIEW_TAB_NOT_SELECTED` / `COVER_ENTRY_NOT_UNIQUE` / `COVER_INPUT_LAYOUT_CHANGED` 时保留草稿核查，不猜入口、上传框或继续保存/发布。

横封面可能用 Canvas 绘制预览，旧竖封面 img 仍留在弹窗 DOM。不能只查 img；Canvas 预览须与本次文件缩放后的图像内容核对，拒绝空白、透明或其他图像的画布，不只看比例或画布出现。图像解码与比较仅留在页面内存。

出现 `AIGC_DIALOG_AMBIGUOUS` / `COVER_DIALOG_AMBIGUOUS` 时保留草稿并报告当前弹窗，不关闭窗口或重传成片。`BROWSER_OPERATION_FAILED` 的 `diagnostic` 只包含异常类型及栈帧的文件名、函数、行号；将这些字段用于研发定位，不转发浏览器原始错误、Cookie、Token 或验证码。

## 短信验证与结果核查

返回 exit 4 / `SMS_VERIFICATION_REQUIRED` 表示本次提交等待用户验证，**没有确认发布成功**。脚本保留浏览器页面和提交上下文，不重跑 upload/run，不重复点发布，不调用 `douyin-publish check/login` 关闭或重开验证页。

- 用 `douyin-publish video verify-send` 真实点击「获取验证码」，核对页面倒计时；工具不会自动重复发送。
- 请用户提供验证码，将其写入当前用户拥有、权限 `0600` 的普通文件；用 `douyin-publish video verify-code --code-file /绝对路径/私有验证码文件` 真实键盘输入并点击「验证」。验证码不放命令参数、报告、记忆或 Git，使用后删除临时文件。
- 用户也可在当前窗口完成验证，再执行 `douyin-publish video resume`。续接只验证与核查原提交，不重新发布。

exit 2 表示需要恢复登录；exit 3 / `unconfirmed` 表示结果未确认，先用 `resume/get-link` 核查原任务，再检查管理页和草稿，禁止自动重发。提交过的任务未结案时会阻止新的上传、填表和发布。

未结案任务也会阻止普通登录、取数和图文操作关闭共用浏览器。仅验证页面已丢失或登录失效时，用 `douyin-publish login --resume-video` 恢复原账号，再 `resume` 核查原提交。提交记录会保留，当前短信弹窗仍在时恢复入口拒绝关闭它。

仅人工核实管理页没有本次作品、确认原提交未发布后，使用 `edit-draft --confirm-unpublished` 结案并续编。工具会先查询本次作品，若已经发布则返回确认的链接；短信验证仍在时不清除任务。不要把超时当作“确认未发布”。

`get-link` 只核查保存的本次提交：按提交前作品 ID、提交时间与完整标题筛选；没有提交记录、无匹配或有多个候选都不返回旧作品作为成功。仅 `state: published` 且有完整 ID 和 `/video/` URL 时记录成功。运行状态保存在 `~/.camoufox-cli/publications/douyin-video.json`，仅含任务资料，不保存登录凭据；不要手工删除未结案状态以重发。

正常完整发布后关闭浏览器、保留 profile；准备失败、等待验证或结果未知时保留当前页面。
