# GitHub

> 规则参考 [GitHub 代码搜索文档](https://docs.github.com/en/search-github/github-code-search/about-github-code-search)。固定 session/profile `default`，带 --persistent。

## 搜索

### URL

```
https://github.com/search?q={keyword}&type={type}
```

类型：`repositories` | `users` | `code` | `issues` | `pullrequests` | `discussions` | `topics` | `wikis`

### 仓库排序

- 最多星：`&s=stars&o=desc`
- 最多 fork：`&s=forks&o=desc`
- 最近更新：`&s=updated&o=desc`

### 用户排序

- 最多关注者：`&s=followers&o=desc`
- 最近加入：`&s=joined&o=desc`

### 语言过滤

优先把 `language:Python` / `language:TypeScript` 写入 q 搜索式；传统仓库搜索的 &l 参数仅在当前页面实际采用时使用。代码搜索与仓库搜索的筛选/排序不是同一套规则，不把仓库的 s/o 参数套到代码结果上。

### 多关键词

用 `+` 连接

### 示例

```
https://github.com/search?q=wiseflow+addon&type=repositories&s=stars&o=desc&l=Python
```

## Pitfalls

仓库等公开页面通常可读；**代码搜索包括公开仓库也要求登录**。按 browser-guide 在共享 `default` 持久化 profile 完成登录；新代码搜索不支持自定义排序，最多返回 100 个结果，不能宣称穷尽仓库。查询条件与原文链接需记录。
