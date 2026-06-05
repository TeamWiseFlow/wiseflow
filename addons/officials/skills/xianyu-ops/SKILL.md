---
name: xianyu-ops
description: 闲鱼（goofish.com）商品搜索、查看详情、私信会话管理与回复。当用户要求在闲鱼上搜索商品、查看宝贝、读取或回复私信时触发。
metadata:
  openclaw:
    emoji: 🐟
---

# 闲鱼操作

通过 **browser 工具** 在闲鱼（goofish.com）上完成商品搜索、详情查看、私信管理。

**前提条件**：需要先通过 browser 工具登录闲鱼（在 Chrome 中打开 goofish.com 扫码登录），browser 已持有有效 session。

---

## 必做约束

- 每次操作之间保持 3-5 秒间隔，避免风控触发验证码。
- 发送私信时不要连续发送超过 10 条，每条间隔 30 秒以上。
- 出现"请先登录"、"验证码"、"安全验证"、"异常访问"等提示时，立即停止操作并告知用户需要重新登录。

---

## 登录状态检测

在页面加载后，检查页面是否出现以下关键词，命中则说明需要重新登录或被风控：

```
请先登录 / 登录后     → 需要重新登录
验证码 / 安全验证 / 异常访问 / 访问过于频繁 → 被风控，停止操作
```

---

## URL 格式

| 页面 | URL |
|------|-----|
| 商品搜索 | `https://www.goofish.com/search?q={关键词}` |
| 商品详情 | `https://www.goofish.com/item?id={item_id}` |
| 私信列表 | `https://www.goofish.com/im` |
| 私信会话 | `https://www.goofish.com/im?itemId={item_id}&peerUserId={user_id}` |
| 发布页 | `https://www.goofish.com/publish` |

---

## 工作流程

### 搜索商品

```
1. 导航到搜索页：https://www.goofish.com/search?q={关键词}
2. 等待页面加载（3-4 秒）
3. 执行登录状态检测
4. 提取搜索结果：商品卡片选择器 a[href*="/item?id="]
   - 标题：[class*="row1-wrap-title"] 或 [class*="main-title"]
   - 价格：[class*="price-wrap"] 内 [class*="number"] + [class*="decimal"]
   - 原价：[class*="price-desc"] 内 [title] 或 [style*="line-through"]
   - 成色/品牌：[class*="row2-wrap-cpv"] span[class*="cpv--"]
   - 地区：[class*="row4-wrap-seller"] [class*="seller-text"]
   - 信用标签：[class*="credit-container"] [title] 或 span
5. 从卡片 href 中提取 item_id（匹配 [?&]id=(\d+)）
```

### 查看商品详情

```
1. 导航到详情页：https://www.goofish.com/item?id={item_id}
2. 等待页面加载（2-3 秒）
3. 执行登录状态检测
4. 通过 mtop 接口获取详情（在浏览器控制台执行）：
   window.lib.mtop.request({
     api: 'mtop.taobao.idle.pc.detail',
     data: { itemId: '{item_id}' },
     type: 'POST', v: '1.0', dataType: 'json',
     needLogin: false, needLoginPC: false,
     sessionOption: 'AutoLoginOnly', ecode: 0
   })
5. 从返回的 data 中提取：
   - itemDO.title / itemDO.desc / itemDO.soldPrice / itemDO.originalPrice
   - itemDO.wantCnt / itemDO.collectCnt / itemDO.browseCnt
   - itemDO.itemLabelExtList → 找 propertyText="成色"/"品牌"/"分类" 对应的 text
   - itemDO.imageInfos → 图片 URL 列表
   - sellerDO.nick / sellerDO.sellerId / sellerDO.publishCity
   - sellerDO.xianyuSummary / sellerDO.replyRatio24h
6. 若 mtop 不可用（window.lib.mtop 未就绪），改用 DOM 提取页面上的可见信息
```

### 查看私信列表

```
1. 导航到私信页：https://www.goofish.com/im
2. 等待页面加载（4-5 秒）
3. 执行登录状态检测
4. 提取会话列表：每个会话包含
   - 对方昵称、商品标题、价格、最后一条消息
   - 未读标记、未读数量
   - 点击会话可从 URL 中解析 itemId 和 peerUserId
5. 若需获取完整 item_id / peer_user_id，逐个点击会话，从跳转 URL 中提取
```

### 读取私信内容

```
1. 导航到会话页（两种方式）：
   - 已知 item_id + user_id：https://www.goofish.com/im?itemId={item_id}&peerUserId={user_id}
   - 已在私信列表页：点击目标会话
2. 等待页面加载（2-3 秒）
3. 确认聊天输入框存在（can_input 为 true）
4. 提取可见消息列表
```

### 发送私信 / 回复

```
1. 导航到会话页（同"读取私信内容"步骤 1-3）
2. 在聊天输入框中输入消息文本
3. 触发 input 事件
4. 点击发送按钮
5. 等待 1-2 秒，确认消息已出现在聊天区域
```

---

## 错误处理

| 情况 | 处理 |
|------|------|
| 页面出现登录墙 | 停止操作，告知用户需在 goofish.com 重新扫码登录 |
| 触发验证码/风控 | 停止操作，建议用户手动访问 goofish.com 完成验证后重试 |
| mtop 接口不可用 | 改用 DOM 提取页面可见信息 |
| mtop 返回 SESSION_EXPIRED | 需要重新登录 |
| 商品不存在 | 检查 item_id 是否正确 |
| 聊天输入框不可用 | 确认会话页已正确加载，重试一次 |
