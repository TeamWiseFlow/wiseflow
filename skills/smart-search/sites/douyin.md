# 抖音

当前 crew 配置了 `douyin-hunter` 时优先读取并使用该技能；其独立 API 会话由 douyin-login 管理，不使用本文件作为失败后的浏览器绕行。

仅未配置 douyin-hunter 的 crew 按本文件执行浏览器搜索。使用固定 session/profile `douyin`，每条 Camoufox 命令带 --persistent；登录、验证码与正在进行的发布任务须串行处理。浏览器登录不代表 API 登录就位。

[OpenCLI 搜索规则](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/douyin/search.js)：

```
https://www.douyin.com/search/{keyword}?type=video
```

keyword 作为路径段编码。等待真实视频结果卡片，snapshot 后按结果区提取；可参考 `[data-e2e="scroll-list"]` 下的视频链接，避免依赖随机 CSS 类。仅有空骨架或登录遮罩时停止取数，按 browser-guide 确认登录，不当作搜索无结果。

保留完整作品/作者链接和实际可见文字。卡片未显示播放、评论或分享数时标注不可得，不补零，不自行构造签名 API。
