---
name: ui-demo
description: 录制精美的产品 UI demo 视频。当用户需要录制演示视频、功能演示、操作教程或利益相关方展示视频时使用。输出带可见鼠标、自然节奏和专业字幕的 WebM 视频。
metadata:
  {
    "openclaw":
      {
        "emoji": "🎥",
        "always": false,
        "requires": { "bins": ["node"] },
      },
  }
---

# UI Demo Video Recorder

使用 patchright `recordVideo` + 注入的鼠标覆盖层、字幕和自然节奏，录制精美的 Web 应用演示视频。

> **CDP 模式**：通过 patchright 连接 wiseflow 内置 Chrome（不启动新进程）。录制结束后只关闭 context，不关闭 Chrome。

## When to Use

- 用户需要"演示视频"、"产品录屏"、"功能演示"或"操作教程"
- 需要制作用于文档、用户引导或投资人/客户展示的视频

## Three-Phase Process

**Discover → Rehearse → Record**。禁止跳过直接录制。

---

## Phase 1: Discover（browser tool）

在写录制脚本之前，用 **browser tool** 逐一导航到流程中的每个页面，了解真实的页面结构。

**目标：建立每个页面的字段映射表**，用于 Phase 3 脚本中的选择器。

每个页面重点关注：

- **表单字段类型**：是 `<input>`、`<textarea>`、`<select>` 还是自定义 combobox / contenteditable？
- **Select 选项**：确认实际选项值。Placeholder 选项（通常 value 为 `""` 或 `"0"`）看起来非空但实际无效，跳过。
- **按钮精确文本**：如 `"Submit"`、`"Submit Request"`、`"Save"`。
- **必填字段**：尝试提交空表单，观察验证报错。
- **动态字段**：填写某字段后，确认是否有新字段出现。
- **登录态**：如需登录，先通过 browser-guide 完成登录，再进行 Discovery。

**输出**：整理每个页面的字段映射，例如：

```
/purchase-requests/new:
  - Budget Code: <select>（4 个真实选项，第一个是 placeholder）
  - Desired Delivery: <input type="date">
  - Context: <textarea>（不是 input）
  - Submit: <button> text="Submit Request"
```

---

## Phase 2: Rehearse（browser tool）

不录制，在 browser tool 中**手动走一遍完整流程**，验证每一步都能顺利完成。

- 按照 Phase 1 的字段映射，逐步导航、填写、点击
- 每个操作后确认页面状态符合预期
- 发现不符时，修正字段映射再重试
- 全流程无误后，才进入 Phase 3 写录制脚本

> Phase 2 的价值在于消灭"脚本假设"——字段顺序、选择器、等待时机，都在这里确认，不留到录制时爆。

---

## Phase 3: Record（Node.js 脚本）

Phase 1/2 确认后，编写录制脚本。`recordVideo` 必须通过 patchright Node.js 脚本完成，无法通过 browser tool 实现。

### Recording Principles

#### 1. Storytelling Flow

将视频规划为一个故事，默认结构：

- **Entry**：登录或导航到起始点
- **Context**：浏览周围环境让观众先定向
- **Action**：执行主要工作流步骤
- **Variation**：展示次要功能（可选）
- **Result**：展示结果或最终状态

#### 2. Pacing（节奏）

| 时机 | 等待时长 |
|------|---------|
| 登录后 | 4s |
| 导航后 | 3s |
| 点击按钮后 | 2s |
| 主要步骤之间 | 1.5-2s |
| 最后一个动作后 | 3s |
| 打字延迟 | 25-40ms / 字符 |

#### 3. Cursor Overlay（鼠标覆盖层）

注入 SVG 箭头光标，每次导航后重新注入（导航会销毁覆盖层）：

```javascript
async function injectCursor(page) {
  await page.evaluate(() => {
    if (document.getElementById('demo-cursor')) return;
    const cursor = document.createElement('div');
    cursor.id = 'demo-cursor';
    cursor.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M5 3L19 12L12 13L9 20L5 3Z" fill="white" stroke="black" stroke-width="1.5" stroke-linejoin="round"/>
    </svg>`;
    cursor.style.cssText = `
      position: fixed; z-index: 999999; pointer-events: none;
      width: 24px; height: 24px; transition: left 0.1s, top 0.1s;
      filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.3));
    `;
    cursor.style.left = '0px'; cursor.style.top = '0px';
    document.body.appendChild(cursor);
    document.addEventListener('mousemove', e => {
      cursor.style.left = e.clientX + 'px';
      cursor.style.top = e.clientY + 'px';
    });
  });
}
```

#### 4. Mouse Movement（鼠标移动）

禁止光标瞬移，点击前先平滑移动到目标：

```javascript
async function moveAndClick(page, locator, label, opts = {}) {
  const { postClickDelay = 800, ...clickOpts } = opts;
  const el = typeof locator === 'string' ? page.locator(locator).first() : locator;
  try {
    await el.scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);
    const box = await el.boundingBox();
    if (box) {
      await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 10 });
      await page.waitForTimeout(400);
    }
    await el.click(clickOpts);
  } catch (e) {
    console.error(`WARNING: moveAndClick failed on "${label}": ${e.message}`);
    return false;
  }
  await page.waitForTimeout(postClickDelay);
  return true;
}
```

#### 5. Typing（打字）

可见打字，不要瞬间填充：

```javascript
async function typeSlowly(page, locator, text, label, charDelay = 35) {
  const el = typeof locator === 'string' ? page.locator(locator).first() : locator;
  await moveAndClick(page, el, label);
  await el.fill('');
  await el.pressSequentially(text, { delay: charDelay });
  await page.waitForTimeout(500);
  return true;
}
```

#### 6. Subtitles（字幕）

在视口底部注入字幕条，每次导航后重新注入：

```javascript
async function injectSubtitleBar(page) {
  await page.evaluate(() => {
    if (document.getElementById('demo-subtitle')) return;
    const bar = document.createElement('div');
    bar.id = 'demo-subtitle';
    bar.style.cssText = `
      position: fixed; bottom: 0; left: 0; right: 0; z-index: 999998;
      text-align: center; padding: 12px 24px;
      background: rgba(0,0,0,0.75); color: white;
      font-family: -apple-system, "Segoe UI", sans-serif;
      font-size: 16px; font-weight: 500; letter-spacing: 0.3px;
      transition: opacity 0.3s; pointer-events: none;
    `;
    bar.textContent = ''; bar.style.opacity = '0';
    document.body.appendChild(bar);
  });
}

async function showSubtitle(page, text) {
  await page.evaluate(t => {
    const bar = document.getElementById('demo-subtitle');
    if (!bar) return;
    bar.textContent = t; bar.style.opacity = t ? '1' : '0';
  }, text);
  if (text) await page.waitForTimeout(800);
}
```

字幕规范：不超过 60 字符，使用 `Step N - 动作` 格式，UI 已能说明问题时清空。

#### 7. Smooth Scroll

```javascript
await page.evaluate(() => window.scrollTo({ top: 400, behavior: 'smooth' }));
await page.waitForTimeout(1500);
```

### Script Template

```javascript
'use strict';
const { chromium } = require('patchright');
const path = require('path');
const fs = require('fs');

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';
const CDP_URL  = process.env.CDP_URL  || 'http://localhost:9222';
const VIDEO_DIR = path.join(__dirname, 'output');
const OUTPUT_NAME = 'demo-FEATURE.webm';

// 在此粘贴 injectCursor、injectSubtitleBar、showSubtitle、moveAndClick、typeSlowly 函数

(async () => {
  const browser = await chromium.connectOverCDP(CDP_URL);

  // 从 openclaw 现有 context 继承登录态（避免录制视频出现登录流程）
  const existingContexts = browser.contexts();
  const cookies = existingContexts.length > 0
    ? await existingContexts[0].cookies()
    : [];

  const context = await browser.newContext({
    recordVideo: { dir: VIDEO_DIR, size: { width: 1280, height: 720 } },
    viewport: { width: 1280, height: 720 }
  });
  if (cookies.length > 0) await context.addCookies(cookies);

  const page = await context.newPage();

  try {
    await injectCursor(page);
    await injectSubtitleBar(page);

    // Step 1 - 登录（cookies 已注入，通常直接跳过；若目标应用跨域或 cookie 失效则执行表单登录）
    await page.goto(`${BASE_URL}/login`);
    await page.waitForTimeout(2000);
    const alreadyLoggedIn = await page.locator('[data-testid="user-avatar"], .user-menu, .avatar').first().isVisible().catch(() => false);
    if (!alreadyLoggedIn) {
      await showSubtitle(page, 'Step 1 - 登录');
      await typeSlowly(page, 'input[name="email"]',    'demo@example.com', 'Email');
      await typeSlowly(page, 'input[name="password"]', 'demo-password',    'Password');
      await moveAndClick(page, 'button[type="submit"]', 'Login');
      await page.waitForTimeout(4000);
      await showSubtitle(page, '');
    }

    await page.goto(`${BASE_URL}/dashboard`);
    await injectCursor(page);
    await injectSubtitleBar(page);
    await showSubtitle(page, 'Step 2 - 概览');
    // 巡览 dashboard

    await showSubtitle(page, 'Step 3 - 主要流程');
    // 操作序列

    await showSubtitle(page, 'Step 4 - 结果');
    await page.waitForTimeout(3000);
    await showSubtitle(page, '');

  } catch (err) {
    console.error('DEMO ERROR:', err.message);
  } finally {
    await context.close();
    const video = page.video();
    if (video) {
      const src = await video.path();
      const dest = path.join(VIDEO_DIR, OUTPUT_NAME);
      fs.copyFileSync(src, dest);
      console.log('Video saved:', dest);
    }
    // 不调用 browser.close() — Chrome 由 wiseflow 管理
  }
})();
```

运行：

```bash
node demo-script.cjs
```

---

## Checklist Before Recording

- [ ] Phase 1 完成，每个页面字段映射已确认
- [ ] Phase 2 完成，全流程手动走通无报错
- [ ] 脚本选择器来自 Phase 1/2 的实际观察，无假设
- [ ] 每次导航后重新调用 `injectCursor` 和 `injectSubtitleBar`
- [ ] 所有点击使用 `moveAndClick`（含描述性 label）
- [ ] 可见输入使用 `typeSlowly`
- [ ] 滚动使用 smooth 模式
- [ ] 关键过渡点有 `showSubtitle`

## Common Pitfalls

1. 导航后光标消失 → 重新注入
2. 视频速度太快 → 增加停顿
3. 光标瞬移 → 点击前先 `moveAndClick`
4. Select placeholder 看起来非空 → Phase 1 时确认 value 是否为 `""` 或 `"0"`
5. 弹窗感觉突兀 → 确认前增加阅读停顿
6. 视频文件路径随机 → `copyFileSync` 到固定名称
