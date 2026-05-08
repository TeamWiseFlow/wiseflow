/**
 * 掘金编辑器 CodeMirror 内容注入助手
 * 
 * 使用方法：在浏览器控制台（或通过 browser evaluate）调用以下函数
 * 
 * 依赖：页面已加载掘金编辑器 (https://juejin.cn/editor/drafts/new)
 */

/**
 * 清空编辑器内容
 */
async function clearEditor() {
  const cmTextarea = document.querySelector('.CodeMirror textarea');
  if (!cmTextarea) {
    throw new Error('未找到 CodeMirror 编辑器，请确认当前页面是掘金编辑器页面');
  }
  
  cmTextarea.focus();
  await sleep(300);
  
  // Ctrl+A 全选
  cmTextarea.dispatchEvent(new KeyboardEvent('keydown', {
    key: 'a', code: 'KeyA', keyCode: 65,
    ctrlKey: true, bubbles: true, cancelable: true
  }));
  
  await sleep(300);
  
  // Backspace 删除
  cmTextarea.dispatchEvent(new KeyboardEvent('keydown', {
    key: 'Backspace', code: 'Backspace', keyCode: 8,
    bubbles: true, cancelable: true
  }));
  
  await sleep(500);
  return true;
}

/**
 * 向编辑器注入 Markdown 内容
 * @param {string} markdownContent - 要注入的 Markdown 内容
 */
async function injectContent(markdownContent) {
  const cmTextarea = document.querySelector('.CodeMirror textarea');
  if (!cmTextarea) {
    throw new Error('未找到 CodeMirror 编辑器');
  }
  
  // 先清空
  await clearEditor();
  
  // 聚焦
  cmTextarea.focus();
  await sleep(200);
  
  // 使用原生 value setter 设置内容（绕过 React/Vue 的 value 绑定）
  const nativeSetter = Object.getOwnPropertyDescriptor(
    HTMLTextAreaElement.prototype, 'value'
  ).set;
  nativeSetter.call(cmTextarea, markdownContent);
  
  // 触发 input 事件让 CodeMirror 处理内容
  cmTextarea.dispatchEvent(new Event('input', { bubbles: true }));
  
  await sleep(1000);
  
  // 验证注入结果
  const cmLines = document.querySelectorAll('.CodeMirror-line');
  return {
    success: cmLines.length > 1,
    lineCount: cmLines.length,
    firstLine: cmLines[0]?.textContent?.substring(0, 60) || ''
  };
}

/**
 * 设置文章标题
 * @param {string} title - 文章标题
 */
async function setTitle(title) {
  const titleInput = document.querySelector('textarea[placeholder*="输入文章标题"]');
  if (!titleInput) {
    throw new Error('未找到标题输入框');
  }
  
  titleInput.focus();
  await sleep(200);
  
  const nativeSetter = Object.getOwnPropertyDescriptor(
    HTMLTextAreaElement.prototype, 'value'
  ).set;
  nativeSetter.call(titleInput, title);
  titleInput.dispatchEvent(new Event('input', { bubbles: true }));
  titleInput.dispatchEvent(new Event('change', { bubbles: true }));
  
  await sleep(300);
  return titleInput.value === title;
}

/**
 * 获取当前编辑器统计信息
 */
function getEditorStats() {
  // 从页面上的字符数/行数/正文字数区域读取
  const statsElements = document.querySelectorAll('.bytemd-editor + div strong, [class*="editor"] strong');
  // 更可靠的方式：从包含 "字符数" "行数" "正文字数" 的区域读取
  const allText = document.body.innerText;
  const charMatch = allText.match(/字符数:\s*(\d+)/);
  const lineMatch = allText.match(/行数:\s*(\d+)/);
  const wordMatch = allText.match(/正文字数:\s*(\d+)/);
  
  return {
    charCount: charMatch ? parseInt(charMatch[1]) : 0,
    lineCount: lineMatch ? parseInt(lineMatch[1]) : 0,
    wordCount: wordMatch ? parseInt(wordMatch[1]) : 0
  };
}

/**
 * 检查编辑器是否就绪
 */
function isEditorReady() {
  const cmEl = document.querySelector('.CodeMirror');
  const cmTextarea = document.querySelector('.CodeMirror textarea');
  return !!(cmEl && cmTextarea);
}

/**
 * 等待编辑器加载就绪
 * @param {number} maxWaitMs - 最大等待时间（毫秒）
 */
async function waitForEditor(maxWaitMs = 10000) {
  const startTime = Date.now();
  while (Date.now() - startTime < maxWaitMs) {
    if (isEditorReady()) {
      return true;
    }
    await sleep(500);
  }
  throw new Error('编辑器加载超时');
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ===== 一键发布辅助函数 =====

/**
 * 完整发布流程：填充内容 + 标题，然后打开发布对话框
 * @param {object} article - { title: string, content: string, category?: string }
 */
async function prepareArticle(article) {
  // 1. 等待编辑器就绪
  console.log('[1/4] 等待编辑器就绪...');
  await waitForEditor();
  
  // 2. 注入内容
  console.log('[2/4] 注入文章内容...');
  const contentResult = await injectContent(article.content);
  console.log(`  内容注入: ${contentResult.success ? '成功' : '失败'}, ${contentResult.lineCount} 行`);
  
  // 3. 设置标题
  console.log('[3/4] 设置标题...');
  const titleResult = await setTitle(article.title);
  console.log(`  标题设置: ${titleResult ? '成功' : '失败'}`);
  
  // 4. 获取统计信息
  console.log('[4/4] 获取统计信息...');
  await sleep(1000);
  const stats = getEditorStats();
  console.log(`  字符数: ${stats.charCount}, 行数: ${stats.lineCount}, 正文字数: ${stats.wordCount}`);
  
  return {
    contentInjected: contentResult.success,
    titleSet: titleResult,
    stats
  };
}
