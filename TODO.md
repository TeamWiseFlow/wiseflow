- 1、按 README.md 更新其他语种 readme；
- 2、更新 .github/workflows/ 的 release 流程：自动从 https://github.com/TeamWiseFlow/openclaw_for_business 拉取最新代码，然后把本代码仓下的 wiseflow 文件夹整体放入 openclaw_for_business/addons/ ，之后打包成为一个压缩吧，发布。

注意：
- 发布可能需要我配置 github token 什么的，如果需要，详细列出步骤给我，我去网页操作；
- 最好能够做成定时任务，比如每天看一眼上游是否有更新，如果有更新则自动触发发布流程。
- 我们自己代码仓如果有新版本（新的 tag），那么自动触发 release

另外，我希望上述自动 release 流程只发生在 upstream 中，即 Teamwiseflow 那个仓，而不是 bigbrother666sh仓，但如果实在实现不了，两个仓都有这个配置也没关系。

