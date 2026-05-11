---
name: toutiao-publish
description: Publish Markdown articles to 今日头条 via docx document import. Converts
  Markdown (with local images embedded) to docx, then guides through Toutiao's "文档导入"
  upload flow.
metadata:
  openclaw:
    emoji: 📰
    requires:
      bins:
      - python3
---

# 今日头条文章发布

## 通用约束

- 文件上传前必须先将文件复制到 `/tmp/openclaw/uploads/`(browser 工具沙箱限制)
- **「文档导入」弹窗的 file input 不能用 `browser upload` 工具**,必须用 CDP 脚本注入(见 Step 2 步骤 3)
- 遇到 `browser failed: timed out. Restart the OpenClaw gateway ...` 错误时,**不需要重启、不需要报错**!等待 30 秒后在原页面继续操作即可。若仍无法操作,再等 30 秒;若还不行,尝试关闭浏览器后重开;只有关闭重开后仍报错才是真的出错,需停止并反馈用户。
- 标题输入使用 `type` + `slowly: true`,不要用 `fill()`
- 发布按钮点击后只等待 + 汇报 URL,不重试

## Step 1:Markdown → DOCX

### ⚠️ 重要：必须在原目录下转换（禁止复制到 /tmp/ 再转）

```bash
# ❌ 错误做法：不要这样！
cp article.md /tmp/
python3 ./skills/toutiao-publish/scripts/md_to_docx.py -f /tmp/article.md  # 图片路径解析会失败！

# ✅ 正确做法：在原 markdown 所在目录（图片同目录）下转换
python3 ./skills/toutiao-publish/scripts/md_to_docx.py -f output_articles/some-article/article.md
```

**根因**：markdown 中的图片使用相对路径（如 `![alt](img1.jpg)`），`md_to_docx` 脚本基于 markdown 文件所在目录解析图片路径。如果将 markdown 复制到 `/tmp/` 再转换，脚本在 `/tmp/` 下找不到对应图片，导致 docx 中图片缺失。

**正确的完整操作**：

```bash
# 1. 在原 markdown 文件所在目录执行转换
python3 ./skills/toutiao-publish/scripts/md_to_docx.py -f output_articles/<article-folder>/article.md

# 2. 将生成的 docx 复制到 uploads 目录用于浏览器上传
cp output_articles/<article-folder>/article.docx /tmp/openclaw/uploads/toutiao_article.docx
```

`-o` 参数可选;不指定时,DOCX 自动输出到与 markdown 同目录,文件名与 markdown 相同(扩展名 `.docx`)。

**除非用户明确指示存储路径和文件名,否则不必指定 `-o` 参数**,直接使用默认输出路径和文件名即可。

脚本自动将本地图片嵌入 Word 文档;超过 15 MB 时自动删除图片,或者将图片进行压缩,保证最终的 docx 文档大小在限制内。

## Step 2:浏览器发布

```
1. Navigate to https://mp.toutiao.com/profile_v4/graphic/publish
   Confirm the page loads (not a login page)

2. Click the doc-import toolbar button - it is an ICON-ONLY button with no visible text.
   Selector: .syl-toolbar-tool.doc-import button
   (It is the last button in the toolbar, after the final divider on the right)
   A modal with title "文档导入" will appear.

3. ⚠️ DO NOT use `browser upload` for this file input - it does not work here.
   Instead, inject the file via CDP script:
   ```bash
   python3 ./skills/toutiao-publish/scripts/cdp_set_file.py /tmp/openclaw/uploads/toutiao_article.docx
   ```
   Expected output: `OK: 文件已注入 → ...`
   Wait up to 30s for the modal to close automatically and the editor to render the imported content.

4. Verify the title and body content are correctly rendered

5. Upload cover image via CDP script:
   ```bash
   cp <cover_image> /tmp/openclaw/uploads/cover.jpg
   python3 ./skills/toutiao-publish/scripts/cdp_cover_upload.py /tmp/openclaw/uploads/cover.jpg
   ```
   Expected output: `OK: 封面上传完成`
   ⚠️ DO NOT use `browser upload` or click "本地上传" manually - use the CDP script only.

6. Set publishing options:
   - 投放广告:选择 "投放广告赚收益"
   - 作品声明:勾选 "引用 AI"
   - 声明原创/首发(如适用)

7. Click "预览并发布" button
   A preview floating layer will appear

   ⚠️ 预览浮层中的按钮（「确认发布」「返回编辑」）不在 snapshot 可见范围内（浮层 DOM 动态渲染），且需要等待 3~4 秒才会出现。用 evaluate 轮询查找：
   ```js
   Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim() === '确认发布')
   ```

8. 在预览浮层中找到发布按钮并点击。按钮文字有两种可能：「确认发布」或「发布」，按此顺序查找，找到任一即 click：
   ```js
   const btn = Array.from(document.querySelectorAll('button')).find(
     b => b.textContent.trim() === '确认发布' || b.textContent.trim() === '发布'
   );
   if (btn) btn.click();
   ```
   The article will be submitted for review

9. After publishing:
   - The article will NOT appear in the "已发布" list immediately
   - It will appear in the "审核中" list
   - Once it appears in "审核中", the publishing is considered successful
   - Report the success status to the user
```

## Error Handling

| 问题 | 处理方式 |
|------|---------|
| 缺少 python-docx | `pip install python-docx` 后重试 |
| 脚本提示"超过 15 MB" | 图片压缩后，重新放入 docx 文档后重试，或者适当删除图片后重试 |
| 缺少 websocket-client | `pip install websocket-client` 后重试 CDP 脚本 |
| 文档导入入口找不到 | 确保页面已完全加载后再查找,selector: `.syl-toolbar-tool.doc-import button`(工具栏最右侧图标按钮) |
| CDP 脚本报 `未找到 file input` | 弹窗未打开,先用 browser click 触发 doc-import 按钮再运行脚本 |
| 封面上传无响应 | 不要用 browser upload,改用 `cdp_cover_upload.py` 脚本注入 |
