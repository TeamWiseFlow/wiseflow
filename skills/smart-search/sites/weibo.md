# 微博 (Weibo)

> last_verified: 2026-06-15 | 来源：OpenCLI clis/weibo/

## 概览

- 域名：`s.weibo.com`（搜索）、`weibo.com`（主站）
- 登录要求：搜索需登录
- Auth 策略：Cookie Warmup（必须先访问首页）

## 搜索

### URL

| 类型 | URL |
|------|-----|
| 综合 | `https://s.weibo.com/weibo/{keyword}` |
| 实时/最新 | `https://s.weibo.com/realtime?q={keyword}` |
| 用户 | `https://s.weibo.com/user?q={keyword}` |
| 话题 | `https://s.weibo.com/topic?q={keyword}` |

### 按用户搜索

获取某用户指定时间范围的博文：
```
https://weibo.com/u/{uid}
```

时间范围需在页面 UI 上操作过滤，无 URL 参数。

### Cookie Warmup

1. Navigate `https://weibo.com`
2. 等待 3 秒
3. Navigate 到搜索 URL

### 分页

微博搜索使用 URL 分页：`&page={n}`（从 1 开始）

### 多关键词

URL-encode 空格

## Pitfalls

### pitfall: css_module_hash_drift

- **触发**：用 CSS module hash 选择器定位元素（如 `.publishBtn_1a2b3c`）
- **症状**：选择器在下次部署后失效
- **workaround**：用 placeholder 文本或 `data-*` 属性定位，不用 hash class

### pitfall: evaluate_envelope

- **触发**：用 `browser evaluate` 提取数据时
- **症状**：返回 `{session: ..., data: ...}` 信封格式而非原始值
- **workaround**：检查返回值是否为 `{session, data}` 对象，若是则取 `.data`

## Fallback

1. 搜索无结果 → 检查登录态 → 登录后重试
2. 仍不足 → Bing 搜 `site:weibo.com {keyword}`

## Re-entry

- 在搜索结果页 → 从当前 page 继续翻页
- 在登录页 → browser-guide 登录后重新搜索
