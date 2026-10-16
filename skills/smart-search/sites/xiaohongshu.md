# 小红书

当前 crew 配置了 `xhs-hunter` 时优先使用该技能；PC API 登录与 Creator 登录、浏览器 profile 分开，不因浏览器搜索成功就覆盖 PC 会话。

仅未配置 xhs-hunter 时使用本浏览器规则。固定 session/profile `xhs-browse`，每条 Camoufox 命令带 --persistent。

[OpenCLI 搜索规则](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/xiaohongshu/search.js)：

```
https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes
```

等待真实结果卡片或登录提示后 snapshot。DOM 可参考 section 中含 `/search_result/` 或 `/explore/` 的笔记链接，不只依赖 section.note-item；不要把用户名、广告或空骨架误判为笔记。

保存实际返回的完整笔记 URL，保留 xsec_token/xsec_source。打开详情后再确认正文、作者与可见互动计数；推荐区、猜你想搜和重复卡片应剔除。限频/验证码停止本轮站内搜索，不修改请求签名或改用直连 API。
