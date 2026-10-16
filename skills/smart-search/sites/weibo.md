# 微博

当前 crew 配置了 `weibo-hunter` 时优先使用；登录通过 weibo-hunter login/export，固定 Camoufox session/profile `weibo`。已配置技能失败时不自动改走浏览器。

仅未配置 weibo-hunter 时执行本浏览器规则，每条 Camoufox 命令带 --session weibo --persistent；已有有头登录窗口时保持 --headed。

[OpenCLI 搜索规则](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/weibo/search.js)：

```
https://s.weibo.com/weibo?q={keyword}
```

等待实际卡片后 snapshot。可参考 .card-wrap 及 `feed_list_content_full` / `feed_list_content` 正文节点，优先取完整正文；保留作者、页面时间和完整帖子链接，不把缩略 ID 用于后续动作。

同一原帖的转发、摘要与重复卡片分开识别；点赞数等未显示时保留缺项。登录墙/验证页不能当作没有讨论。发微博、评论、私信和点赞都不属于本搜索规则。
