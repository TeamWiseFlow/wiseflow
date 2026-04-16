# BusinessDeveloper — Workflow

## 模式一：联盟营销（Affiliate Marketing）

### 标准流程

```
1. 接收用户提供的 Amazon 商品链接（应已包含 ?tag=your-associate-id）
2. 导航至商品页并抓取信息：
   - 商品标题
   - 当前价格
   - 评分（星级 + 评价数）
   - Feature Bullets（产品特点列表）
   - 主图 URL
3. 确认目标推广平台（可多选）：Twitter/X、TikTok、Instagram、微信公众号等
4. 为每个平台分别生成推广内容：
   - Twitter/X：≤280字 + 链接 + 3–5个 hashtag
   - TikTok/Instagram：短视频脚本/图文说明文字 + hashtag
   - 微信公众号：段落式推广文案（可调用 wenyan-formatter 排版）
5. 向用户展示所有平台的推广内容（L2 确认）
6. 用户确认后，逐平台发布（L3）：
   - Twitter: 调用 twitter-post 技能
   - TikTok: 告知用户需先准备视频素材，再用 tiktok-post 发布
   - Instagram: 调用 instagram-post 技能
```

### Amazon 商品信息抓取要点

```
导航前先 warmup：https://www.amazon.com

目标元素：
- 标题：id="productTitle"
- 价格：class 含 "a-price-whole" 或 "a-offscreen"
- 评分：id="acrPopover" 中的 title 属性
- 评价数：id="acrCustomerReviewText"
- Feature Bullets：id="feature-bullets" 内的 <li> 列表
- 主图：id="landingImage" 的 src 属性

如遇验证码或登录墙 → 停止并告知用户（不绕过）
```

---

## 模式二：本地商家外拓（Cold Outreach）

### 标准流程

```
1. 接收用户提供的：
   - 行业/关键词（如 "餐厅" / "律师事务所"）
   - 地区（如 "上海" / "北京朝阳区"）
   - 开发信模板（或使用 LLM 生成）
2. 在 Google Maps 搜索目标商家：
   https://www.google.com/maps/search/{行业}+{地区}
3. 浏览搜索结果，逐条提取商家信息：
   - 商家名称
   - 地址
   - 电话
   - 网站 URL
   （每页最多提取 20 条，向用户确认采集数量上限）
4. 对每个有网站的商家：
   a. 调用 cold-outreach 技能访问网站，提取邮箱
   b. 若主页无邮箱，尝试 /contact 或 /about 路径
5. 汇总采集结果（名称 / 网站 / 邮箱），展示给用户确认（L2）
6. 用户确认后，为每个有邮箱的商家：
   a. LLM 生成个性化开发信（基于商家名称 + 行业 + 用户提供的卖点）
   b. 调用 cold-outreach 技能发送邮件（L3）
7. 汇报发送结果：成功数 / 失败数 / 无邮箱跳过数
```

### 开发信生成原则

- 开头点名商家名称，增加个性化感
- 正文 2–3 句，重点说"对方能得到什么"，不是"我们有多好"
- 结尾一个明确的 CTA（如"方便的话可以回复这封邮件聊聊？"）
- 纯文本优先（HTML 邮件更容易进垃圾箱）
- 每封邮件之间间隔 2–3 秒，避免被 SMTP 服务器限流

---

## 邮件配置（首次使用必读）

系统需要 SMTP 凭据才能发送邮件。请确认以下环境变量已配置：

```
SMTP_SERVER    邮件服务器地址（如 smtp.gmail.com）
SMTP_PORT      端口（TLS: 587，SSL: 465）
SMTP_USER      发件人邮箱
SMTP_PASSWORD  邮箱密码或应用专用密码
SMTP_FROM      发件人显示名和地址（可选，默认使用 SMTP_USER）
```

Gmail 用户请使用"应用专用密码"（Google Account → Security → App Passwords）
