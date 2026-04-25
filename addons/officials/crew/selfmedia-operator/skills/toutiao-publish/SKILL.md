---
name: toutiao-publish
description: Publish Markdown articles to 今日头条 via docx document import. Converts Markdown (with local images embedded) to docx, then guides through Toutiao's "文档导入" upload flow.
metadata:
  {
    "openclaw":
      {
        "emoji": "📰",
        "requires": { "bins": ["python3"] }
      }
  }
---

# Toutiao Publisher — 今日头条文档导入发布

将 Markdown 稿件转为 DOCX，通过今日头条"文档导入"功能上传发布，排版效果优于手动粘贴 HTML。

---

## Step 1：Markdown → DOCX

```bash
python3 ./skills/toutiao-publish/scripts/md_to_docx.py \
  -f <markdown_file> \
  -o /tmp/toutiao_article.docx
```

**脚本行为：**
- 自动将 Markdown 中的本地图片路径嵌入 Word 文档（确保上传后图片不丢失）
- 远程图片（http/https）以占位文本代替，需上传后在编辑器补图
- 转换完成后检查文件大小：**超过 15 MB 自动删除图片**，并提示在头条编辑器中手动补图

**前置依赖：**

```bash
pip install python-docx
```

> 已包含在 addon 的 `requirements.txt` 中，初始化时会自动安装。

**Frontmatter 支持（可选，建议提供）：**

```yaml
---
title: 文章标题
author: 作者名
---
```

---

## Step 2：浏览器上传（文档导入流程）

使用 browser 工具，按以下步骤操作：

### 2-1 进入创作页面

打开今日头条创作平台：`https://mp.toutiao.com/profile_v4/graphic/publish`

### 2-2 选择文档导入

页面加载后，找到 **"文档导入"** 入口（通常在编辑器工具栏右侧或顶部菜单）。点击后弹出上传对话框。

> 如果未看到"文档导入"，可尝试路径：顶部"发文章" → 编辑器工具栏 → 点击"..."更多选项 → "文档导入"

### 2-3 上传 DOCX

**使用 `setInputFiles` 注入文件路径，不要模拟点击文件选择对话框**，直接将文件路径注入 `<input type="file">` 元素：

```
setInputFiles("input[type=file]", "/tmp/toutiao_article.docx")
```

上传后**不要立即操作编辑器**，平台需要异步解析文档并渲染到编辑器（DOM 会先清空再注入内容）。

**等待编辑区 DOM 稳定的策略：**

1. 上传后先 `snapshot`，检查编辑区是否已出现文章内容（`timeout: 30000ms`）
2. 若内容已出现，再 `snapshot` 第二次——**两次 snapshot 内容一致**，才认为 DOM 稳定
3. DOM 稳定后再继续填写标题、标签等操作，否则内容可能丢失或操作落在错误元素上

### 2-4 编辑器内检查

DOM 稳定后，在编辑器内确认：

- 标题已正确填入（若未填入，手动输入）
- 正文排版基本正确（段落、标题、列表）
- 图片显示正常（若 Step 1 提示"已删除图片"，此时手动在编辑器补图）

### 2-5 设置封面与发布选项

在编辑器右侧或底部依次完成：

1. **展示封面**：点击"添加封面"，选择文章内图片或上传单独封面图（建议 3:2 或 16:9 比例）
2. **声明首发**：勾选"声明原创/首发"复选框
3. **引用 AI**：勾选"AI 辅助创作"声明

### 2-6 预览并发布

点击 **"预览发布"** 按钮，确认预览页内容无误后点击 **"确认发布"**。

**点击发布后不要立即导航或关闭页面**，平台会进行后端校验（违禁词检测、封面生成等）。
等待跳转到文章详情页或出现"发布成功"提示后，再提取文章 URL（`timeout: 30000ms`）。

---

## Agent 行为约束

1. Step 1 脚本执行完成后，**必须先检查输出中是否有"超过 15 MB"提示**，若有，告知用户图片需手动补
2. 上传文件使用 `setInputFiles` 注入路径，**不模拟点击文件选择对话框**；注入后等待 DOM 稳定（双 snapshot 确认）再继续
3. 发布完成前需确认"声明首发"和"引用 AI"两项均已勾选
4. 点击发布后等待跳转到文章详情页或出现"发布成功"提示，再提取 URL，**不要提前关闭或导航**

---

## Error Handling

| 问题 | 处理方式 |
|------|---------|
| `缺少依赖 python-docx` | 运行 `pip install python-docx` 后重试 |
| 文件不存在 | 确认 Markdown 文件路径正确 |
| 上传后图片丢失 | 图片超出 15MB 限制被删除，在编辑器手动补图 |
| 文档导入入口找不到 | 尝试刷新页面或检查账号是否已开通创作者权限 |
| 上传解析失败 | 确认 docx 格式正常（本地用 WPS/Word 打开验证） |
