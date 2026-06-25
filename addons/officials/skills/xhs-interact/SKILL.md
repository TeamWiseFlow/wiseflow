---
name: xhs-interact
description: 小红书社交互动技能。发表评论、回复评论、点赞。当用户要求评论、回复或点赞小红书帖子时触发。
metadata:
  openclaw:
    emoji: 💬
---

# 小红书社交互动

通过 **browser 工具** 代替用户在小红书（xhs）上完成社交互动。

**前提条件**：需要先通过 browser 工具登录小红书（遵循 browser-guide 第 6 节 QR 登录流程）。

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

## 关注 / 取关

### 关注用户

1. 导航到用户主页：`https://www.xiaohongshu.com/user/profile/{user_id}`
2. 等待 3 秒加载
3. 找到关注按钮（selector: `.user-actions .follow-btn` 或文本为"关注"的按钮）
4. 点击关注按钮
5. 等待 1-2 秒确认按钮变为"已关注"

### 取关用户

1. 导航到用户主页
2. 找到"已关注"按钮
3. 点击后确认弹出确认框，点击"取消关注"
4. 等待 1-2 秒确认按钮变为"关注"

---

## Pitfalls

### pitfall: xsec_token_required

- **触发**：手拼 `/explore/{feed_id}` 裸路径，没带 `xsec_token`
- **症状**：页面 403 或 redirect 到错误页（`error_code=300017` 或 `300031`）
- **workaround**：feed_id + xsec_token **必须从搜索结果/笔记列表的链接中提取**，不能手拼 URL。如果只有 feed_id，先搜索对应笔记获取 signed URL

### pitfall: like_count_compressed_format

- **触发**：读取点赞数时
- **症状**：显示 `2.1w`、`1.5万`、`1.2k` 等压缩格式而非数字
- **workaround**：解析规则：`w` = 万 = ×10000，`万` = ×10000，`k` = ×1000。例：`2.1w` = 21000，`1.5万` = 15000，`1.2k` = 1200

### pitfall: security_block_on_repeated_access

- **触发**：短时间高频互动（连续点赞/评论多个笔记）
- **症状**：页面显示"安全限制"/"访问链接异常"
- **workaround**：每次操作间隔 30-60 秒；触发后 60s 内不重试

### pitfall: comment_section_lazy_load

- **触发**：需要找到较早的评论
- **症状**：评论未出现在 DOM 中
- **workaround**：逐段向下滚动加载，每次滚动后等待 0.5-1 秒；到达 `.end-container` 说明到底部；最多滚动 7 次

### pitfall: creator_center_is_different_host

- **触发**：在主站 `www.xiaohongshu.com` 找发布/草稿入口
- **症状**：主站无完整创作者功能
- **workaround**：创作者相关操作（查看草稿、创作者数据）需访问 `creator.xiaohongshu.com`

---

## 错误处理

| 情况 | 处理 |
|------|------|
| 页面出现登录墙 | 遵循 browser-guide 第 6 节 QR 登录流程，扫码后重试 |
| 点赞状态未变化 | 重试一次，仍未变化则报告错误 |
| CDP click 超时 | 改用 JavaScript evaluate 方法：browser act kind=evaluate fn="document.querySelector('.like-wrapper').click()" |
| xsec_token 缺失/无效 | 从搜索结果链接中重新获取 signed URL，不要手拼 |
| 安全限制/访问异常 | 停止操作 60 秒后重试，或换笔记操作 |
