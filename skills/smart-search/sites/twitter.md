# X / Twitter

当前 crew 配置了 `x-hunter` 时优先使用；登录通过 x-hunter login/export，固定 Camoufox profile `twitter`。不要使用 x、临时会话或别的平台窗口登录。

仅未配置 x-hunter 时执行浏览器搜索，全部 Camoufox 操作保持 --session twitter --persistent；已有有头窗口时保持 --headed。

[OpenCLI 搜索操作符](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/twitter/search.js)：

```
https://x.com/search?q={keyword}&src=typed_query&f=live
```

f=live 为最新；其他分类用当前页面的 Top、People、Photos、Videos 选项确认，不猜测新 URL 参数。关键词支持 `from:账号`、`filter:images`、`filter:videos`、`filter:links`、`-filter:replies`、`-filter:nativeretweets`；将完整搜索式作为 q 编码一次。

提取实际推文正文、作者、完整 status 链接和日期，区分引用推文、原帖与转发。当前上游还用动态 GraphQL 查询，本技能不复制其查询 ID、Bearer 或接口脚本。
