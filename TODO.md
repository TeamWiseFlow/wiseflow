- 1、按 README.md 更新其他语种 readme；
- 2、更新 .github/workflows/ 的 release 流程：自动从 https://github.com/TeamWiseFlow/openclaw_for_business 拉取最新代码，然后把本代码仓下的 wiseflow 文件夹整体放入 openclaw_for_business/addons/ ，之后打包成为一个压缩吧，发布。

注意：
- 发布可能需要我配置 github token 什么的，如果需要，详细列出步骤给我，我去网页操作；
- release 的触发机制： **upstream**（TeamWiseflow 正式仓库）每次合并 PR 后通过 github actions 自动更新版本号并触发 release 打包发布
