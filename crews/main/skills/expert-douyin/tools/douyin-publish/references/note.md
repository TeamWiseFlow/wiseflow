# 抖音图文发布

前置执行 `douyin-publish check`，未登录用 `douyin-publish login` 在持久化有头窗口完成登录；不使用 login-manager、不导出或导入 cookie。

原声图文先预览 `douyin-publish note --images /绝对路径/1.png /绝对路径/2.png --title "标题" --caption @/绝对路径/body.txt --original-sound`，已有发布授权时加 `--confirm`。图片按参数顺序上传，默认 AI 声明，纯实拍按实际来源使用 `--declaration none`。

统一入口及分步 `fill/run` 的 `--caption` 均支持 `@UTF-8文件路径`。先保存纯正文和话题，再传 `--caption @/绝对路径/body.txt`；文件读取失败时在浏览器操作前停止，不把多行正文拼进命令。

需要页面配乐时使用分步流程：

```bash
douyin-publish note upload --images /绝对路径/1.png /绝对路径/2.png
douyin-publish note music-list
douyin-publish note music-select --choice "返回的明确候选"
douyin-publish note fill --title "标题" --caption @/绝对路径/body.txt --declaration ai
douyin-publish note publish --confirm
douyin-publish note get-link --title "完整标题"
```

`music-select` 必须使用真实候选，核实配乐选择后再发布；没有明确选配乐时，`publish` 需加 `--original-sound`。原声一键流程 `run` 必须明确 `--original-sound`。

`run` 默认只生成本地预览，`publish` 默认只提示核对当前草稿；两者只有加 `--confirm` 才实际发布，提交前必须已有用户授权。标题 ≤20 字、正文 ≤1000 字，图片 1–35 张，单张非空且 ≤50MB。共享 session `douyin` 和排他锁，不与视频发布或取数并行。

取链只接受完整标题对应的唯一图文候选，进入图文编辑页核对完整标题与 mid。出现多个候选、exit 3、超时或 `LINK_UNCONFIRMED` 时停止，到管理页人工核实，禁止自动重发。只有确认的完整 ID 和 `/note/` 链接才能入库。
