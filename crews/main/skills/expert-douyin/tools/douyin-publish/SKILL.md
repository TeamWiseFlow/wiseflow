---
name: douyin-publish
description: 使用 Camoufox 持久化创作者会话登录并发布抖音视频或图文；支持本地预览、分步填表与配乐、短信续接和取链。
---

# 抖音发布

发布使用 Camoufox 持久化 session `douyin`，登录态保存在 profile。本人作品取数由 douyin-engagement 通过 HTTP 完成，仅在进程内临时读取同一 profile 的 cookie/UA。不要调用 login-manager，不手工导出或导入 cookie，不使用 hunter 的 API 会话代替发布会话。

## 登录与检查

```bash
douyin-publish login
douyin-publish check
```

`login` 打开有头创作者中心，请用户完成扫码或页面验证；返回 `awaiting_user_login` 不代表已经登录。用户完成后用 `check` 验证创作者接口，检查会关闭浏览器进程并保留 profile。未登录返回 exit 2；验证码、风控和接口异常停止处理，不无限重试。

## 视频与图文

先展示目标账号、文件、标题和正文，执行不带 `--confirm` 的命令生成本地预览；用户已授权后在同一命令加 `--confirm`。

```bash
douyin-publish video run --video /绝对路径/video.mp4 --title "标题" --caption @/绝对路径/body.txt --cover-vertical /绝对路径/vertical.jpg --cover-horizontal /绝对路径/horizontal.jpg
douyin-publish note run --images /绝对路径/1.png /绝对路径/2.png --title "标题" --caption @/绝对路径/body.txt --original-sound
```

`video/note run` 是一键流程；原来的 `video --video …`、`note --images …` 简写仍可用。分步提交 `video publish` 和 `note publish` 同样必须加 `--confirm`；不带时只返回核对提示，不操作浏览器。上传、填表、配乐等分步操作按下方参考说明执行。

先将已确认的纯正文和话题写入 UTF-8 `body.txt`，用 `--caption @/绝对路径/body.txt` 由脚本读取。相对路径按当前工作目录解析；路径含空格时给整个 `@路径` 参数加引号。文件读取失败或正文超长时在浏览器操作前停止；预览的 `caption` 是实际正文。文件须有真实换行，不把标题或交付说明放进正文，不用 `$(cat ...)` 或将多行正文拼进命令。短文字仍支持直接传入；以 `@` 开头的参数一律按文件路径处理，文件内容只读取一次，正文里的 `@提及` 按原文保留。`video/note fill/run --caption` 均支持文件。

视频入口保留浏览器 AIGC 声明流程，不支持 `--declaration none`。图文默认声明 AI，可按实际来源传 `--declaration none`；原声图文必须明确传 `--original-sound`。视频分步操作、草稿修复与短信续接先读 [视频操作说明](references/video.md)；图文配乐和分步操作先读 [图文操作说明](references/note.md)。

视频提交必须有 3:4 竖封面与 4:3 横封面。比例不符时等比补底保留完整内容，不裁掉边缘文字；补底过宽也可能被平台拒绝，两张封面都要通过页面检测。`COVER_BORDER_TOO_LARGE` / `COVER_QUALITY_REJECTED` 时按目标比例重新构图或更换封面，不反复加宽补底或跳过检测。缺视频、标题或双封面即停止，不点击发布。

封面与 AIGC 声明必须在唯一可见的目标弹窗内保存；支持 dialog/modal/Semi Modal，不能只看 `role="dialog"` 或页面文字就判断已完成。已有声明弹窗时用 `video fill` / `cover` 续编，脚本先完成声明再操作正文/封面；同类弹窗不唯一或设置未保存时停止并保留草稿。浏览器异常的安全定位字段见 `references/video.md`。

封面预览检测须确认本次选择的文件，并重新查找当前弹窗；相同图片可能复用缓存而没有新 load 事件，弹窗也可能重建。`COVER_UPLOAD_TIMEOUT` 不代表上传一定失败，先用 `video status` 核查并续编当前草稿，不重传整段视频或点击发布。

封面入口按「竖封面」/「横封面」名称定位，不按排列顺序选。上传前须确认当前编辑器标题或内部激活选项卡与目标类型一致；`COVER_EDITOR_MISMATCH` 时停止并保留草稿。上传框只从当前编辑器内选择，首次上传/替换输入框不代表两个封面方向；不能通过放宽图片比例检测掩盖传错槽位。

视频 exit 4 / `awaiting_verification` 表示等待用户短信验证，页面保持打开；读视频操作说明，用 `douyin-publish video verify-send`、`douyin-publish video verify-code --code-file`，或由用户在当前窗口验证后 `douyin-publish video resume`。不要重跑发布或用 check/login 关闭验证页。

未结案的视频任务会阻止普通登录、取数和图文操作关闭共用浏览器。仅验证页面已丢失或登录失效时，用 `douyin-publish login --resume-video` 恢复原账号，随后 `douyin-publish video resume` 核查原提交；该入口保留提交记录，当前短信弹窗仍在时拒绝关闭。

只在返回确认的完整作品 ID 与公开链接后入库。exit 3、超时或取链失败时，到作品管理页核实；视频用 `douyin-publish video resume` 或 `douyin-publish video get-link` 核查保存的本次任务，不用全局最新旧作品代替；图文用 `douyin-publish note get-link --title "完整标题"`。未提交的失败草稿用 `douyin-publish video edit-draft` 续编。禁止自动重发。已停用 API 发布及其 job-file/status/verify 子命令，不用它们核查浏览器任务。

发布和取数共用排他锁，串行执行。单账号每 24h 视频和图文合计 ≤5 条；风控后至少 30 分钟不重试。
