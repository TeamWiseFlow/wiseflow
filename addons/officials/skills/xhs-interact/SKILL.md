---
name: xhs-interact
description: 小红书社交互动技能。发表评论、回复评论、点赞。当用户要求评论、回复或点赞小红书帖子时触发。
metadata:
  openclaw:
    emoji: 💬
---

# 小红书社交互动

通过 **browser 工具** 代替用户在小红书（xhs）上完成社交互动。

**前提条件**：需要先通过 browser 工具登录小红书（遵循 browser-guide 第 6 节 QR 登录流程），browser 已持有有效 session。

---

## 获取 feed_id 和 xsec_token

所有互动操作需要 `feed_id` 和 `xsec_token`，从浏览器地址栏获取：

```
笔记 URL 格式：
https://www.xiaohongshu.com/explore/{feed_id}?xsec_token={xsec_token}&xsec_source=pc_feed

示例：
https://www.xiaohongshu.com/explore/64abc123def456?xsec_token=ABxxxxxx&xsec_source=pc_feed
→ feed_id    = 64abc123def456
→ xsec_token = ABxxxxxx
```

---

## 必做约束

- 批量操作时每次之间保持 30-60 秒间隔，避免风控。
- 每天评论不超过 20 条。

---

## Feed 详情页 URL 格式

```
https://www.xiaohongshu.com/explore/{feed_id}?xsec_token={xsec_token}&xsec_source=pc_feed
```

---

## 工作流程

### 发表评论

```
1. 导航到 feed 详情页（使用上方 URL 格式）
2. 等待页面加载，检查页面是否可访问
   （出现 .access-wrapper / .error-wrapper 则笔记不可访问，停止并告知用户）
3. 输入评论内容到 .content-input 元素
4. 触发 input 事件
5. 点击发送按钮
6. 等待 1-2 秒，确认评论出现在评论区
```

### 回复评论

```
1. 导航到 feed 详情页
2. 等待页面加载（2-3 秒），确认页面可访问
3. 滚动到目标评论：
   - 已知 comment_id：查找 #comment-{comment_id} 元素并滚动到可见
   - 已知 user_id：查找含 data-user-id="{user_id}" 的评论元素并滚动到可见
   - 若需滚动加载更多评论：逐段向下滚动（scroll 7 次后停止），
     每次滚动后等待 0.5-1 秒观察评论加载，到达 .end-container 则说明已到底部
4. 点击目标评论的回复按钮（selector: .interactions .reply）
5. 输入回复内容到 .content-input 元素
6. 触发 input 事件
7. 点击发送按钮
8. 等待 1-2 秒确认回复已发出
```

### 点赞 / 取消点赞

**选择器**：`.like-wrapper`（推荐）或 `.interact-container .left .like-wrapper`

```
1. 导航到 feed 详情页
2. 等待页面加载完成（2-3 秒）
3. 通过页面 snapshot 或 JS 检查当前点赞状态
   - 已点赞：.like-wrapper 元素包含 like-active 类
4. 点击点赞按钮：
   - 方式 A（CDP click）：browser act kind=click ref=xxx
   - 方式 B（JS evaluate，推荐）：document.querySelector('.like-wrapper').click()
5. 等待 1-2 秒，确认状态变化
6. 若状态未变化，重试一次
```

**CDP 模式提示**：若 CDP click 超时，改用 JavaScript evaluate 方法：
```javascript
// 点击点赞按钮
document.querySelector('.like-wrapper').click();

// 检查点赞状态
document.querySelector('.like-wrapper').classList.contains('like-active') ? '已点赞' : '未点赞';
```

---

## 错误处理

| 情况 | 处理 |
|------|------|
| 页面出现登录墙 | 遵循 browser-guide 第 6 节 QR 登录流程，扫码后重试 |
| 点赞状态未变化 | 重试一次，仍未变化则报告错误 |
| CDP click 超时 | 改用 JavaScript evaluate 方法：browser act kind=evaluate fn="document.querySelector('.like-wrapper').click()" |
