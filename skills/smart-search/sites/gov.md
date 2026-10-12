# 政府与政策

> 搜索入口和结果区参考 [OpenCLI](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/gov-policy/search.js)。固定 session/profile `default`，带 --persistent。

## 国务院政策搜索

```
https://sousuo.www.gov.cn/sousuo/search.shtml?code=17da70961a7&dataTypeId=107&searchWord={keyword}
```

搜索 www.gov.cn 上的官方政策文件。不需要 Warmup。

## Pitfalls

政策结果可能延迟挂载；先 snapshot 确认结果区，可参考 .basic_result_content .item / .js_basic_result_content .item。保留文件标题、发布机关、发文/发布日期及真实 gov.cn 链接，空骨架和结构变化不能判为“无政策”。只使用网页检索，不复制上游后台请求。
