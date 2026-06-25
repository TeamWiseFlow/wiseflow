# GitHub

> last_verified: 2026-06-15

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

`&l={language}`（如 `&l=Python`、`&l=TypeScript`）

### 多关键词

用 `+` 连接

### 示例

```
https://github.com/search?q=wiseflow+addon&type=repositories&s=stars&o=desc&l=Python
```

## Pitfalls

无特殊 pitfalls。GitHub 搜索公开可用，不需要 Cookie Warmup。
