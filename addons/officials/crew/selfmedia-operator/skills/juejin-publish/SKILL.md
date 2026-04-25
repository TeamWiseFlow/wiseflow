---
name: juejin-publish
description: 发布文章到掘金平台。使用浏览器自动化完成发布流程，包括导入 Markdown、处理本地图片、选择分类、添加标签、上传封面图、发布。当用户要求发布内容到掘金时触发。
---

# 掘金文章发布

通过浏览器自动化将 Markdown 文章发布到掘金平台。

## 发布入口

```
https://juejin.cn/creator/tool/import/self
```

## 核心原则（研发建议）

### 1. 文件上传

- ✅ 使用 `setInputFiles` 注入文件路径，**不要模拟点击文件选择对话框**
- ✅ 上传后**必须等待平台完成 Markdown 解析渲染**，不能立即操作编辑器
- ✅ 建议：上传后先 `snapshot` 确认编辑区内容已出现，再继续填写标题/标签
- ✅ timeout 建议 **30000ms**

### 2. DOM 稳定等待

平台拿到 Markdown 文件后会异步渲染到编辑器，这个过程 DOM 会抖动（内容先清空再注入）。

**在编辑区内容稳定前点击或输入会导致内容丢失或操作落在错误元素上。**

**策略**：`snapshot` 两次，若两次内容一致则认为 DOM 稳定，再继续操作。

### 3. 发布确认

点击发布按钮后**不要立即导航或关闭**，平台会做后端校验（违禁词、封面生成等）。

- 等待跳转到文章详情页，或
- 出现「发布成功」提示，再提取 URL
- timeout 建议 **30000ms**

---

## 发布流程

### Step 1: 进入文章导入页面并上传文件

1. 打开 https://juejin.cn/creator/tool/import/self
2. 点击 **"创作工具 - 文章导入发布"**
3. **使用 setInputFiles 上传文件**（不要模拟点击文件选择对话框）：
   ```javascript
   // 找到文件输入框
   const fileInput = document.querySelector('input[type="file"][accept*=".md"]');
   // 使用 browser 工具的 setInputFiles 注入文件路径
   ```
4. **等待 DOM 稳定**：
   - 上传后等待 3-5 秒，让平台完成 Markdown 解析
   - snapshot 两次确认编辑区内容一致
   - timeout 建议 30000ms

### Step 2: 处理本地图片（重要）

⚠️ **掘金 Markdown 导入不支持本地路径图片！**

导入后需要手动处理图片：

1. **删除本地图片链接**：在编辑器中找到 `![alt](/local/path/image.png)` 格式的图片，记录本地路径后删除
2. **使用编辑器上传图片**：点击编辑器工具栏的 **"图片"** 按钮，手动上传对应的图片文件

**示例**：

```markdown
<!-- 导入后的原文 -->
![ChatGPT vs Agent 对比](/home/user/campaign_assets/img-1/00.png)

<!-- 删除后，用编辑器图片按钮重新上传，得到 -->
![ChatGPT vs Agent 对比](https://p3-juejin.byteimg.com/xxx.png)
```

### Step 3: 检查并调整标题

确保标题输入框中的标题正确。如需修改：

```javascript
document.querySelector('.title-input').value = '新标题';
```

### Step 4: 点击发布按钮

点击编辑器右上角的 **"发布"** 按钮，打开发布设置弹窗。

### Step 5: 选择分类

掘金文章分类包括：
- 后端
- 前端
- Android
- iOS
- **人工智能**（AI 相关文章选择此项）
- 开发工具
- 代码人生
- 阅读

通过 JavaScript 选择分类：

```javascript
const categories = document.querySelectorAll('.item');
for (const cat of categories) {
  if (cat.textContent.trim() === '人工智能') {
    cat.click();
    break;
  }
}
```

### Step 6: 添加标签

标签有助于文章被更多人发现。常用标签：

| 主题 | 推荐标签 |
|------|----------|
| AI/Agent | AI, Agent, OpenAI, ChatGPT, AIGC |
| 前端 | JavaScript, TypeScript, React, Vue |
| 后端 | Node.js, Python, Go, Java |

添加标签方法：

```javascript
// 1. 点击标签输入框
const tagInput = document.querySelectorAll('.byte-select__input')[0];
tagInput.focus();

// 2. 输入标签名
tagInput.value = 'AI';
tagInput.dispatchEvent(new Event('input', { bubbles: true }));

// 3. 从下拉选项中选择
const options = document.querySelectorAll('.byte-select-option');
for (const opt of options) {
  if (opt.textContent.trim() === 'AI') {
    opt.click();
    break;
  }
}
```

### Step 7: 上传封面图

封面图用于首页信息流展示，建议尺寸 **192×128px**。

**封面图来源优先级**：
1. 文章中已有的配图（从 `campaign_assets/` 中选取）
2. 调用 `siliconflow-img-gen` 生成封面图

**上传方法**：

```javascript
// 1. 点击上传封面按钮
const uploadBtn = document.querySelector('button[class*="add_cover"]');
if (uploadBtn) {
  uploadBtn.click();
}

// 2. 使用 browser 工具的 upload action 上传图片
// browser action=upload inputRef=<file input ref> paths=["/path/to/cover.png"]
```

**生成封面图示例**（如果需要）：

```bash
# 使用 siliconflow-img-gen 生成封面
# 提示词应简洁，突出文章主题
# 例如："AI Agent digital worker, minimalist style, blue and white theme"
```

### Step 8: 确认发布并获取链接

点击「确定并发布」按钮后：

1. **不要立即导航或关闭页面**
2. **等待后端校验完成**（违禁词检查、封面生成等）
3. **等待跳转到文章详情页**或出现「发布成功」提示
4. timeout 建议 **30000ms**

```javascript
const btns = document.querySelectorAll('button');
for (const btn of btns) {
  if (btn.textContent.includes('确定并发布')) {
    btn.click();
    break;
  }
}
```

### Step 9: 获取发布链接

发布成功后，页面会显示文章链接：

```javascript
const link = document.querySelector('a[href*="/spost/"]');
// 文章 URL: link.href
```

## 注意事项

1. **本地图片问题**：掘金 Markdown 导入不支持本地路径图片，必须手动删除后用编辑器重新上传
2. **网络图片**：Markdown 中的网络图片 URL 可以正常显示
3. **URL 格式**：使用超链接格式 `[text](url)` 而非直接暴露 URL
4. **分类必选**：必须选择一个分类才能发布
5. **标签建议**：建议添加 2-3 个相关标签
6. **封面图建议**：建议上传封面图，提升文章在首页信息流的展示效果

## 代码仓库地址格式

文章末尾的项目地址使用超链接格式：

```markdown
> wiseflow 是一个开源的数字员工团队框架。[GitHub](https://github.com/TeamWiseFlow/wiseflow) 搜索 wiseflow（国内用户可在 [atomgit](https://atomgit.com/wiseflow/wiseflow) 搜索）。
```

## 示例工作流

```bash
# 1. 打开 https://juejin.cn/creator/tool/import/self
# 2. 点击 "创作工具 - 文章导入发布"
# 3. 使用 setInputFiles 上传 Markdown 文件（不要模拟点击文件选择对话框）
# 4. 等待 DOM 稳定：snapshot 两次确认编辑区内容一致
# 5. 处理本地图片：删除本地路径图片，用编辑器图片按钮重新上传
# 6. 检查标题
# 7. 点击发布 → 选择分类 → 添加标签
# 8. 上传封面图
# 9. 点击确定并发布
# 10. 等待跳转到文章详情页或出现「发布成功」提示
# 11. 记录发布链接到 published_articles_track.md
```
