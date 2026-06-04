---
name: web-form-fill
description: 网络表单填报技能 — 从信息搜集到浏览器填报的完整工作流，确保框架受控组件正确写入、页面切换前暂存、最终提交由用户确认。
metadata:
  openclaw:
    emoji: 📝
---

# Web Form Fill — 网络表单填报技能

面向在线表单填报场景：申报系统、比赛报名、补贴申请、信息登记等。核心原则：**先看后填、模拟真人、切页必存、提交由人**。

**依赖技能**：`browser-guide`（浏览器操作最佳实践）

---

## 工作流程

### Step 1：全量信息搜集

**打开浏览器后，先完整浏览整个表单，不要急着填。**

1. 从第一个页面/栏位开始，逐页点击所有 tab/步骤/栏位
2. 每到一个新页面，记录：
   - 页面/栏位名称
   - 所有字段的 **label、类型、是否必填、字数限制、格式要求**
   - 需要上传的附件类型和格式要求
   - 任何特殊控件（下拉单选/多选、日期选择器、级联选择、富文本编辑器等）
3. 随时将搜集结果写入一个 markdown 文件（建议命名为 `form-fields-{项目简称}.md`），保持与表单相同的页面/段落结构
4. 浏览过程中 **不要填写任何内容**，只看和记

**markdown 文件结构示例**：

```markdown
# XX大赛申报 — 字段清单

## 概要
- 项目名称 [必填] [text] [限50字]
- 行业分类 [必填] [级联下拉] 一级→二级
- 科技创新领域 [必填] [下拉单选]
- 参赛渠道 [必填] [下拉多选]
- 以投代评 [必填] [radio: 是/否]
- 服务需求 [多选] 最多3项
- 期望融资金额 [必填] [number] 万元
- 股权释放比例 [必填] [number] %

## 参赛项目情况
- 项目名称 [必填] [text] （概要中已填，此处联动）
- 前沿技术热点归属 [必填] [text] 最多5个关键词，逗号分隔
- 项目主要技术、产品及服务 [必填] [富文本] 2000字以内，可插入图片
- 项目产品市场分析及竞争优势 [必填] [富文本] 2000字以内
- 商业模式 [必填] [富文本] 1000字以内

## 企业基本信息表
...

## 附件
- 营业执照 [必填] [PDF/图片]
- ...
```

### Step 2：填写字段清单

回到 markdown 文件，逐项填写准备好的内容：

1. 根据已有资料（MEMORY.md、工作区文件、用户之前提供的信息）直接填入
2. 缺失的信息 **主动问用户**，不要自己编造
3. 找不到且用户也未指定的附件，列出清单请用户准备
4. 每个富文本字段，先写纯文本内容，后续在浏览器中输入

**问用户的典型场景**：
- "XX字段应该选择哪个选项？"
- "XX附件文件在工作区中未找到，请提供文件路径或上传。"
- "XX选项选是还是否？"

### Step 3：浏览器填报

信息齐全后，打开浏览器逐页填报。

#### 3-A. 填报顺序

1. 回到表单第一页/栏位
2. 按 markdown 文件中的顺序逐字段填写
3. 每填完一页/栏位，检查是否有 **暂存/保存** 按钮，有则点击
4. 切换到下一页/栏位前，**必须确认当前页已暂存**
5. 重复直到所有页面填完

#### 3-B. 字段填写方法（关键！）

**核心原则：每个字段都要「尝试 → 验证 → 失败则降级重试」。不同网站拦截程度不同，没有一种方法能通吃所有情况。**

##### 文本输入字段（input / textarea / contenteditable）

对每个文本字段，**按以下顺序逐级尝试，每级尝试后立即验证，验证通过则停止，失败则清空重来**：

| 级别 | 方法 | 原理 | 适用场景 | 失效场景 |
|------|------|------|---------|---------|
| A | CDP `Input.insertText` | 走浏览器真实输入管线，一次性插入整段文本 | **大多数原生 input 和简单受控组件**：Vue/React/Svelte v-model、原生 input | 有输入 mask 的字段、拦截 insertText 的站点、**Slate/wangEditor 等 contenteditable 编辑器可能不吃** |
| S | JS dispatch `beforeinput` 事件 | 从 JS 层手动构建 `InputEvent('beforeinput', {inputType:'insertText'})` 并 dispatch，走 Slate 的原生事件管道 | **Slate/wangEditor/Tiptap 等 contenteditable 编辑器** — 这些编辑器监听 `beforeinput` 而非 `input`，CDP `insertText` 不一定能触发 | 非 Slate 的 contenteditable、原生 input |
| B | CDP 逐字 `Input.dispatchKeyEvent` | 模拟逐键按下，每个字符发 keyDown → char → keyUp | 输入 mask 字段、只监听 keydown/keyup 的组件、insertText 被拦截的站点 | 监听 composition 事件的中文输入场景、非常长的文本（太慢） |
| C | JS Clipboard 粘贴 | `document.execCommand('insertText', false, text)` | 部分 contenteditable 编辑器、允许粘贴的输入框 | 禁止粘贴的站点、已废弃 execCommand 的浏览器、**Slate 不感知 execCommand 的 DOM 变更** |
| D | JS native setter + dispatchEvent | 用 `Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set` 绕过框架拦截设值，再手动 `dispatchEvent('input')` + `dispatchEvent('change')` | 简单 Vue/React v-model 绑定、CDP 完全不可用时 | **Slate/wangEditor 等非 input 编辑器**（无 `.value` 属性）、依赖逐字验证的组件 |

**⚠️ Slate/wangEditor 的致命坑**：

Slate 系编辑器（wangEditor、Tiptap 等）与普通受控组件有本质区别，必须注意：

1. **Slate 监听 `beforeinput`，不监听 `input`** — 普通 Vue/React 组件靠 `input` 事件同步状态，Slate 靠 `beforeinput`。所以级别 D 的 `dispatchEvent('input')` 对 Slate 完全无效
2. **`execCommand` 改的是 DOM，Slate 不知道** — `document.execCommand('insertText')` 直接修改 DOM，但 Slate 的内部数据模型不变，下次 Slate 重渲染会覆盖掉
3. **Slate 处理 `beforeinput` 后 DOM 更新有延迟** — `beforeinput` 被 Slate 接管后，文本已写入 Slate 数据模型，但 DOM 渲染要等微任务队列跑完。**验证时不能立即读 `textContent`，必须延迟 50ms+ 再验证**
4. **清空也必须走 Slate 管道** — 对 contenteditable 编辑器，直接 Backspace 键事件可能被 Slate 拦截后走不同路径。正确方式是 dispatch `beforeinput({inputType: 'deleteContentBackward'})`

**如何判断当前字段是否为 Slate 编辑器**：
- 检查 DOM 特征：`[data-slate-editor]`、`[data-slate-node]`
- 检查 class：`.w-e-text-container`（wangEditor）
- 如果是 Slate 编辑器，**跳过级别 A，直接从级别 S 开始尝试**

**每级尝试的完整流程**：

```
对每个字段：
  1. scrollIntoView 确保在视口内
  2. 点击聚焦（对 input：点击输入框；对 contenteditable：点击编辑区域）
  3. 清空已有内容（见下方清空方式）
  4. 判断字段类型：
     - 如果是 Slate/contenteditable 编辑器 → 从级别 S 开始
     - 如果是普通 input/textarea → 从级别 A 开始
  5. 按级别依次尝试：
     a. 用当前方法写入文本
     b. 验证写入是否生效（见下方验证规则）
     c. 如果验证通过 → 本字段完成，进入下一个字段
     d. 如果验证失败 → 清空内容，降级到下一级别重试
  6. 如果所有级别都失败 → 记录该字段为"无法自动填写"，最后告知用户手动填写
```

**各级别操作细节**：

**级别 A — CDP `Input.insertText`**（普通 input/textarea 首选）：
```
1. 聚焦（点击元素）
2. 清空已有内容
3. CDP Input.insertText: "要填入的文本"
4. 验证
```

**级别 S — JS dispatch `beforeinput` 事件**（Slate/contenteditable 编辑器首选）：
```
1. 聚焦（点击编辑器内容区域，确认 activeElement 是编辑器或其子节点）
2. 清空已有内容（用 beforeinput deleteContentBackward，见下方清空方式）
3. 对文本中每个字符 ch：
   Runtime.evaluate:
     const be = new InputEvent('beforeinput', {
       inputType: 'insertText',
       data: ch,
       bubbles: true,
       cancelable: true,
       composed: true
     });
     editor.dispatchEvent(be);
   短暂等待（10-20ms）
4. 延迟 50ms 后验证（Slate DOM 更新有延迟）
```

**级别 B — 逐字 `dispatchKeyEvent`**：
```
1. 聚焦（点击元素）
2. 清空已有内容
3. 对文本中每个字符 ch：
   - Input.dispatchKeyEvent: type=keyDown, key=ch, code=KeyX
   - Input.dispatchKeyEvent: type=char, text=ch
   - Input.dispatchKeyEvent: type=keyUp, key=ch, code=KeyX
   - 短暂等待（20-50ms，模拟人类打字节奏）
4. 验证
注意：中文等非 ASCII 字符，用 type=char 事件 + text 参数传递
```

**级别 C — JS Clipboard 粘贴**：
```
1. 聚焦（点击元素）
2. 清空已有内容
3. Runtime.evaluate: document.execCommand('insertText', false, '要填入的文本')
4. 延迟 50ms 后验证
注意：对 Slate 编辑器此方法大概率无效（execCommand 改 DOM 不改 Slate 模型），但仍可一试
```

**级别 D — native setter + dispatchEvent**（仅适用于 <input>/<textarea>，**不适用于 contenteditable**）：
```
1. 聚焦（点击元素）
2. 清空已有内容
3. Runtime.evaluate:
   const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
   setter.call(el, '要填入的文本');
   el.dispatchEvent(new Event('input', {bubbles: true}));
   el.dispatchEvent(new Event('change', {bubbles: true}));
4. 验证
```

**清空已有内容**：

对 **普通 input/textarea**：
```
1. triple-click 全选（Input.dispatchMouseEvent clickCount=3）
2. Backspace 删除
3. 如果 triple-click 无效，改用 Ctrl+A → Delete
```

对 **contenteditable / Slate 编辑器**：
```
1. 聚焦编辑器
2. 全选：Ctrl+A（Input.dispatchKeyEvent keyDown key=a modifiers=2）
3. 删除：dispatch beforeinput 事件
   Runtime.evaluate:
     editor.dispatchEvent(new InputEvent('beforeinput', {
       inputType: 'deleteContentBackward',
       bubbles: true,
       cancelable: true,
       composed: true
     }));
4. 如果 beforeinput 删除无效，回退到 Backspace 键事件
5. 延迟 50ms 后验证内容为空
```

**禁止的方式**：
- ❌ 直接设 `innerHTML` — Slate/Vue 不会感知，placeholder 不消失，暂存后内容丢失
- ❌ 直接设 `textContent` — 同上
- ❌ 直接赋值 `el.value = "xxx"` 不发事件 — 框架完全无感知
- ❌ 不聚焦就直接写值 — 不会触发任何事件
- ❌ 对 Slate 编辑器用 `dispatchEvent('input')` — Slate 不监听 input 事件，只监听 beforeinput
- ❌ 对 Slate 编辑器用 `execCommand` — 改 DOM 不改 Slate 数据模型，下次渲染被覆盖

##### 下拉选择（select）

逐级尝试：

| 级别 | 方法 |
|------|------|
| A | 点击 select 打开下拉面板 → 点击目标选项 |
| B | 点击 select → 键盘方向键选择 → Enter 确认 |
| C | native setter 设值 + dispatchEvent('change') |

自定义下拉（非原生 `<select>`，如 Element Plus el-select、Ant Design Select）：
- 需要先点击触发按钮打开弹层
- 在弹层中找到目标选项点击
- 部分组件支持键盘搜索：聚焦 → 输入关键字过滤 → 选择

##### Radio / Checkbox

1. `Input.dispatchMouseEvent` 点击目标选项
2. 验证选中状态
3. 如果点击无效，尝试用键盘：聚焦 → Space 切换

##### 日期选择器

逐级尝试：

| 级别 | 方法 |
|------|------|
| A | 点击日期输入框 → 在弹出的日历面板中逐年/月/日点击 |
| B | 点击日期输入框聚焦 → 用级别 A/B 文本输入方法输入日期字符串 |
| C | native setter 设值 + dispatchEvent |

##### 文件上传

1. 找到 `<input type="file">` 或上传按钮
2. 如果工作区内有对应文件，通过 CDP `DOM.setFileInputFiles` 设置文件路径
3. 如果文件不在本机，告知用户手动上传

#### 3-C. 填写验证（每级尝试后必须执行）

| 控件类型 | 验证方式 | 通过条件 | 注意 |
|---------|---------|---------|------|
| 普通 input | 检查 `el.value` 和 placeholder 可见性 | `el.value` 包含预期内容 且 placeholder 不可见 | 可立即验证 |
| contenteditable / Slate 编辑器 | 检查 `editor.textContent.trim()` 和 placeholder 元素 | `textContent` 包含预期内容 且 placeholder 元素 `display: none` | **必须延迟 50ms 再验证** — Slate 处理 beforeinput 后 DOM 更新有延迟 |
| 下拉 select | 检查选中项文本 | 选中项文本与预期一致 | 可立即验证 |
| radio/checkbox | 检查 `el.checked` | 选中状态符合预期 | 可立即验证 |

**contenteditable 验证的具体实现**：
```javascript
// 等待 Slate DOM 更新后验证
await new Promise(r => setTimeout(r, 50));
const text = editor.textContent.trim();
const ph = editor.closest('.w-e-text-container')
  ?.querySelector('.w-e-text-placeholder');
const phHidden = !ph || getComputedStyle(ph).display === 'none';
const passed = text.length > 0 && phHidden;
```

**验证失败的处理**：
1. 清空当前字段内容（避免残留脏数据）
2. 降级到下一级别方法重试
3. 所有级别都失败 → 记录到"无法自动填写"清单，继续填下一个字段

#### 3-D. 页面切换规则

**切换页面/栏位前，必须执行**：

1. 检查当前页面是否有 **暂存 / 保存 / 保存草稿** 按钮
2. 如果有，点击暂存，等待"保存成功"提示
3. 暂存后，验证关键字段值是否还在（防止暂存失败丢数据）
4. 然后再切换页面

**如果当前页没有暂存按钮**：
- 检查是否有自动保存指示（"已自动保存"提示、保存状态图标等）
- 如果没有自动保存，截图告知用户当前页无保存机制，请用户确认是否继续

### Step 4：提交前确认

**所有页面填写完成后**：

1. 从第一页开始，逐页检查所有字段值是否正确
2. 截图或导出最终表单内容，发送给用户审阅
3. 明确告知用户：**"所有内容已填写完毕，请检查确认后手动提交，或明确告知我提交。"**
4. **禁止自动点击"提交"按钮**，必须等用户明确指令

---

## 常见问题与对策

### 问题：填入内容后 placeholder 不消失

**原因**：直接操作 DOM 绕过了框架响应式系统（Vue/React/Slate），框架内部状态仍为空。

**解决**：按 3-B 节的逐级尝试策略填写。对普通 input 优先 CDP `Input.insertText`；对 Slate 编辑器优先 dispatch `beforeinput` 事件。每级尝试后验证，失败则降级。

### 问题：暂存后切换页面，内容丢失

**原因**：同上 — 框架内部状态为空，暂存提交的是空值。

**验证方法**：暂存后，导航到其他页面再回来，检查字段是否仍有值。

### 问题：Slate/wangEditor 编辑器填入后验证显示为空

**原因**：Slate 处理 `beforeinput` 后，文本已写入数据模型但 DOM 还没渲染完。立即读 `textContent` 会读到空值。

**解决**：验证前延迟 50ms+，等 Slate 微任务队列跑完再读 `textContent`。

### 问题：富文本编辑器无法输入

**对策**：
1. 确认点击的是编辑器内容区域（`[contenteditable="true"]`），而非工具栏
2. 确认 `document.activeElement` 是编辑器或其子节点
3. 判断是否为 Slate 编辑器（`[data-slate-editor]`），是则从级别 S（beforeinput）开始尝试
4. 如果以上都无效，尝试先点击工具栏按钮（如加粗）激活编辑器，再重新尝试

### 问题：下拉选项不在视口中

**对策**：
1. 先滚动下拉面板使目标选项可见
2. 或用键盘导航：聚焦 select → 按方向键选择目标项 → 按 Enter 确认

### 问题：表单有防机器人检测

**对策**：
1. 填写速度不要太快，字段间适当等待（0.5-1秒）
2. 不要用 JS 直接操作 DOM
3. 如果触发验证码，按 `browser-guide` 的 CAPTCHA 处理流程操作

---

## 速查：填写操作模板

### 聚焦元素

```
1. Runtime.evaluate: el.scrollIntoView({block:'center'})
2. Runtime.evaluate: el.getBoundingClientRect() → {x, y, width, height}
3. Input.dispatchMouseEvent: mousePressed at (x+width/2, y+height/2)
4. Input.dispatchMouseEvent: mouseReleased
```

### 清空已有内容 — 普通 input/textarea

```
1. 聚焦元素（见上）
2. Input.dispatchMouseEvent: mousePressed clickCount=3 (triple-click 全选)
3. Input.dispatchMouseEvent: mouseReleased clickCount=3
4. Input.dispatchKeyEvent: keyDown Backspace
5. Input.dispatchKeyEvent: keyUp Backspace
6. 验证: el.value 为空
```
如果 triple-click 无效，改用 Ctrl+A：
```
2. Input.dispatchKeyEvent: keyDown key=a modifiers=2 (Ctrl)
3. Input.dispatchKeyEvent: keyUp key=a modifiers=2
```

### 清空已有内容 — contenteditable / Slate 编辑器

```
1. 聚焦编辑器
2. Input.dispatchKeyEvent: keyDown key=a modifiers=2 (Ctrl+A 全选)
3. Input.dispatchKeyEvent: keyUp key=a modifiers=2
4. Runtime.evaluate:
   editor.dispatchEvent(new InputEvent('beforeinput', {
     inputType: 'deleteContentBackward',
     bubbles: true, cancelable: true, composed: true
   }));
5. 等待 50ms
6. 验证: editor.textContent.trim() 为空
```
如果 beforeinput 删除无效，回退到 Backspace 键事件。

### 级别 A — CDP insertText（普通 input 首选）

```
1. 聚焦 + 清空
2. Input.insertText: "要填入的内容"
3. 验证: el.value 非空 且 placeholder 不可见
```

### 级别 S — JS dispatch beforeinput（Slate/contenteditable 编辑器首选）

```
1. 聚焦 + 清空（用 beforeinput 方式清空）
2. 对每个字符 ch:
   Runtime.evaluate:
     editor.dispatchEvent(new InputEvent('beforeinput', {
       inputType: 'insertText', data: ch,
       bubbles: true, cancelable: true, composed: true
     }));
   等待 10-20ms
3. 等待 50ms（Slate DOM 更新延迟）
4. 验证: editor.textContent.trim() 非空 且 placeholder display=none
```

### 级别 B — 逐字 dispatchKeyEvent

```
1. 聚焦 + 清空
2. 对每个字符 ch:
   Input.dispatchKeyEvent: type=keyDown, key=ch
   Input.dispatchKeyEvent: type=char, text=ch
   Input.dispatchKeyEvent: type=keyUp, key=ch
   等待 20-50ms
3. 验证
```

### 级别 C — JS Clipboard 粘贴

```
1. 聚焦 + 清空
2. Runtime.evaluate: document.execCommand('insertText', false, '要填入的内容')
3. 等待 50ms（contenteditable DOM 更新延迟）
4. 验证
```

### 级别 D — native setter + dispatchEvent（仅 input/textarea）

```
1. 聚焦 + 清空
2. Runtime.evaluate:
   const s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
   s.call(el, '要填入的内容');
   el.dispatchEvent(new Event('input', {bubbles: true}));
   el.dispatchEvent(new Event('change', {bubbles: true}));
3. 验证
```
