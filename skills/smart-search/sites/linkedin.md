# LinkedIn

> 规则参考 [OpenCLI 职位搜索](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/linkedin/search.js) 与 [人员搜索](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/linkedin/people-search.js)。固定 session/profile `default`，带 --persistent。

## 搜索

### 职位搜索

```
https://www.linkedin.com/jobs/search/?keywords={keyword}&location={location}
```

### 人员搜索

```
https://www.linkedin.com/search/results/people/?keywords={keyword}
```

### 公司搜索

```
https://www.linkedin.com/search/results/companies/?keywords={keyword}
```

### Cookie Warmup

1. Navigate `https://www.linkedin.com`
2. 等待 5 秒
3. Navigate 到搜索 URL

### 多关键词

用 `%20` 连接

## Pitfalls

### pitfall: login_wall_strict

- **触发**：几乎所有 LinkedIn 内容需登录
- **症状**：未登录时显示登录墙或截断内容
- **workaround**：在共享 `default` profile 完成用户登录并核对结果页，首页初始化不能替代登录

### pitfall: people_search_aggressive

- **触发**：人员搜索翻页过多
- **症状**：触发 LinkedIn 频率限制
- **workaround**：默认遵守 smart-search 每站两次搜索导航/翻页预算，人员搜索还受平台商业使用额度限制，达到提示即停止

## 提取与筛选

人员结果不宜依赖随机 CSS 类；先 snapshot 定位 main 区域，再按真实 /in/ 主页链接与相邻姓名、简介、地点读取。没有已验证的个人主页链接时列为待核实，不把按钮、推荐或重复文本当成新人员。职位的公司、经验、类型、发布时间和远程条件从当前页面筛选控件设置；不要复制上游 Voyager API 的过滤参数到页面 URL。

## Fallback

1. 搜索无结果 → 检查登录态
2. 仍不足 → Bing 搜 `site:linkedin.com {keyword}`
