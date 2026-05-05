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

- 文件上传前必须先将文件复制到 `/tmp/openclaw/uploads/`（browser 工具沙箱限制）
- **「文档导入」弹窗的 file input 不能用 `browser upload` 工具**，必须用 CDP 脚本注入（见 Step 2 步骤 3）
- 遇到 `browser failed: timed out. Restart the OpenClaw gateway ...` 错误时，**不需要重启、不需要报错**！等待 30 秒后在原页面继续操作即可。若仍无法操作，再等 30 秒；若还不行，尝试关闭浏览器后重开；只有关闭重开后仍报错才是真的出错，需停止并反馈用户。
- 标题输入使用 `type` + `slowly: true`，不要用 `fill()`
- 浏览器超时只汇报，不执行 `browser stop/start`
- 发布按钮点击后只等待 + 汇报 URL，不重试

## Step 1：Markdown → DOCX

```bash
python3 ./skills/toutiao-publish/scripts/md_to_docx.py -f <markdown_file>
cp <markdown_dir>/article.docx /tmp/openclaw/uploads/toutiao_article.docx
```

`-o` 参数可选；不指定时，DOCX 自动输出到与 markdown 同目录，文件名与 markdown 相同（扩展名 `.docx`）。

**除非用户明确指示存储路径和文件名，否则不必指定 `-o` 参数**，直接使用默认输出路径和文件名即可。

脚本自动将本地图片嵌入 Word 文档；超过 15 MB 时自动删除图片，或者将图片进行压缩，保证最终的 docx 文档大小在限制内。

## Step 2：浏览器发布

```
1. Navigate to https://mp.toutiao.com/profile_v4/graphic/publish
   Confirm the page loads (not a login page)

2. Click the doc-import toolbar button — it is an ICON-ONLY button with no visible text.
   Selector: .syl-toolbar-tool.doc-import button
   (It is the last button in the toolbar, after the final divider on the right)
   A modal with title "文档导入" will appear.

3. ⚠️ DO NOT use `browser upload` for this file input — it does not work here.
   Instead, inject the file via CDP script:
   ```bash
   python3 ./skills/toutiao-publish/scripts/cdp_set_file.py /tmp/openclaw/uploads/toutiao_article.docx
   ```
   Expected output: `OK: 文件已注入 → ...`
   Wait up to 30s for the modal to close automatically and the editor to render the imported content.

4. Verify the title and body content are correctly rendered

5. Click "添加封面" area
   Upload the cover image file (cp to /tmp/openclaw/uploads/ first)
   Wait for the thumbnail to appear

6. Set publishing options:
   - 投放广告：选择 "投放广告赚收益"
   - 作品声明：勾选 "引用 AI"
   - 声明原创/首发（如适用）

7. Click "预览并发布" button
   A preview floating layer will appear

   ⚠️ 忽略预览浮层内容，直接在页面上找 "发布" 按钮

8. Click "发布" button (在页面上找，不在 preview layer 内)
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
| 脚本提示"超过 15 MB" | 告知用户图片需在编辑器手动补图 |
| 缺少 websocket-client | `pip install websocket-client` 后重试 CDP 脚本 |
| 文档导入入口找不到 | 确保页面已完全加载后再查找，selector: `.syl-toolbar-tool.doc-import button`（工具栏最右侧图标按钮） |
| CDP 脚本报 `未找到 file input` | 弹窗未打开，先用 browser click 触发 doc-import 按钮再运行脚本 |
| 上传后内容为空 | 再等 15s 检查一次；若仍空，建议用户本地验证 docx 格式 |
| 封面上传无响应 | 尝试再次 click 封面区域后上传；若仍失败，告知用户手动上传封面 |
| 浏览器超时 | 汇报超时位置，提示用户在浏览器中继续操作 |
