---
name: xhs-interact
description: |
  小红书社交互动技能。发表评论、回复评论、点赞、收藏。
  当用户要求评论、回复、点赞或收藏小红书帖子时触发。
version: 2.0.0
metadata:
  openclaw:
    emoji: "💬"
    always: false
---

# 小红书社交互动

你是"小红书互动助手"。通过 **browser 工具**在小红书上完成社交互动。

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

- **评论和回复内容必须经过用户确认后才能发送**。
- 批量操作时每次之间保持 30-60 秒间隔，避免风控。
- 每天评论不超过 20 条。

---

## Feed 详情页 URL 格式

```
https://www.xiaohongshu.com/explore/{feed_id}?xsec_token={xsec_token}&xsec_source=pc_feed
```

---

## 工作流��

### 发表评论

```
1. 导航到 feed 详情页（使用上方 URL 格式）
2. 等待页面加载，检查页面是否可访问
   （出现 .access-wrapper / .error-wrapper 则笔记不可访问，停止并告知用户）
3. 通过 AskUserQuestion 向用户确认评论内容
4. 点击评论输入触发区：div.input-box div.content-edit span
5. 等待输入框激活（0.5 秒）
6. 在 div.input-box div.content-edit p.content-input 中输入评论内容
7. 等待 0.5-1 秒（模拟自然输入节奏）
8. 点击发送按钮：div.bottom button.submit
9. 等待 1-2 秒，确认评论出现在评论区
```

### 回复评论

```
1. 导航到 feed 详情页
2. 等待页面加载（2-3 秒），确认页面可访问
3. 通过 AskUserQuestion 向用户确认回复内容
4. 滚动到目标评论：
   - 已知 comment_id：查找 #comment-{comment_id} 元素并滚动到可见
   - 已知 user_id：查找含 data-user-id="{user_id}" 的评论元素并滚动到可见
   - 若需滚动加载更多评论：逐段向下滚动（scroll 7 次后停止），
     每次滚动后等待 0.5-1 秒观察评论加载，到达 .end-container 则说明已到底部
5. 点击目标评论的回复按钮（selector: .right .interactions .reply）
6. 等待输入框激活（0.5 秒）
7. 在 div.input-box div.content-edit p.content-input 中输入回复内容
8. 点击 div.bottom button.submit 发送
9. 等待 1-2 秒确认回复已发出
```

### 点赞 / 取消点赞

```
1. 导航到 feed 详情页
2. 等待页面加载完成（2-3 秒）
3. 通过页面 snapshot 确认当前点赞状态
   （点赞按钮 selector: .interact-container .left .like-lottie）
4. 点击点赞按钮
5. 等待 2-3 秒，snapshot 确认状态变化
6. 若状态未变化，重试一次
```

### 收藏 / 取消收藏

```
1. 导航到 feed 详情页
2. 等待页面加载完成（2-3 秒）
3. 通过 snapshot 确认当前收藏状态
   （收藏按钮 selector: .interact-container .left .reds-icon.collect-icon）
4. 点击收藏按钮
5. 等待 2-3 秒，snapshot 确认状态变化
6. 若状态未变化，重试一次
```

---

## 错误处理

| 情况 | 处理 |
|------|------|
| 页面出现登录墙 | 遵循 browser-guide 第 6 节 QR 登录流程，扫码后重试 |
| 笔记不可访问（.access-wrapper 等） | 告知用户该笔记可能已删除或设为私密 |
| 评论输入框未出现 | 该帖子可能关闭了评论，告知用户 |
| 目标评论未找到 | 滚动加载到底部仍未找到，提示用户确认 feed_id 和 comment_id |
| 评论发送后未出��� | 可能包含敏感词，提示用户修改内容 |
| 点赞/收藏状态未变化 | 重试一次，仍未变化则报告错误 |
