# 浏览器自动化反检测方案调研报告

> 调研日期：2026-02-20
> 目标：评估 rebrowser-patches 与 patchright 两个方案，为 OpenClaw 集成反检测能力提供技术路线

---

## 一、问题背景

### 1.1 为什么本地 AI 助手也需要反检测

OpenClaw 作为本地 AI 助手，通过浏览器执行用户指令（比价、填表、读取信息、搜索等）。目标网站不区分"本地助手"和"恶意爬虫"——检测到自动化特征就会触发防御：

- 电商比价 → 触发验证码或封 IP
- 表单提交 → 被拒绝
- 银行/邮箱 → 风控要求重新验证
- Google 搜索 → CAPTCHA
- 后台管理 → WAF 拦截

### 1.2 Playwright 的主要检测泄露点

| 泄露点 | 检测原理 | 严重程度 |
|--------|---------|---------|
| `Runtime.enable` CDP 调用 | 激活 Runtime domain 后浏览器内部行为变化，反爬脚本可通过侧信道检测 | **致命** |
| `Console.enable` CDP 调用 | 类似 Runtime.enable 的侧信道 | 高 |
| `--enable-automation` 启动参数 | 设置 `navigator.webdriver = true` | 高 |
| `//# sourceURL=pptr:evaluate` | 注入脚本带有特征性 sourceURL 注释 | 中 |
| `__playwright_utility_world__` | utility world 名称可被检测 | 中 |
| init script 通过 CDP 注入 | `Page.addScriptToEvaluateOnNewDocument` 有检测方法 | 中 |
| Playwright 自带 Chromium | 定制版浏览器与正版 Chrome 有指纹差异 | 中（connectOverCDP 时不存在） |
| 大量自动化启动参数 | 参数组合本身是指纹 | 低-中 |

### 1.3 OpenClaw 当前状态

- 使用 `playwright-core@1.58.2`
- 已经通过 `chromium.connectOverCDP()` 连接浏览器（不用 launch）
- Extension relay 模式下连接用户真实 Chrome，零启动参数
- 但 **Playwright driver 层的 CDP 泄露未处理**（Runtime.enable、Console.enable 等）

---

## 二、方案 A：rebrowser-patches

### 2.1 项目概况

- GitHub: `rebrowser/rebrowser-patches` (1.2k stars)
- 生态：rebrowser-playwright-core（drop-in 替代包）、rebrowser-puppeteer 等
- 方式：对现有 playwright-core 源码打补丁（Unix `patch` 命令）
- 支持：Puppeteer + Playwright

### 2.2 修补内容

#### Runtime.enable 修复 — 3 种模式

**模式 1：`addBinding`（默认，推荐）**

```
原理：
1. 生成随机名称 binding（如 "x7k2m9q"）
2. 通过 Runtime.addBinding 注册（不需要 Runtime.enable）
3. 在 isolated world 中 dispatch 自定义事件触发 binding
4. 从 Runtime.bindingCalled 回调拿到真实 executionContextId
5. 用该 contextId 做后续 Runtime.evaluate

优势：
- 完全不调用 Runtime.enable
- 保留对 main world 的完整访问（能读页面变量）
- 支持 web workers 和 iframes
```

**模式 2：`alwaysIsolated`**

```
原理：所有脚本执行都在 Page.createIsolatedWorld 创建的隔离上下文中

优势：完全隔离，防止 MutationObserver 检测
劣势：无法访问 main world 变量，不支持 web workers
```

**模式 3：`enableDisable`**

```
原理：快速 enable → 捕获 context ID → 立即 disable

优势：完整 main world 访问
劣势：有短暂时间窗口可能被检测到
```

#### 其他修复

| 补丁 | 效果 | 配置 |
|------|------|------|
| sourceURL 伪装 | `pptr:evaluate` → `app.js`（可自定义） | `REBROWSER_PATCHES_SOURCE_URL=jquery.min.js` |
| utility world 名称 | `__puppeteer_utility_world__` → `util`（可自定义） | `REBROWSER_PATCHES_UTILITY_WORLD_NAME=util` |

### 2.3 未修复的内容

- Console.enable — 未处理（但也未禁用，保留了完整功能）
- init script 注入方式 — 仍走 CDP
- CSP — 未处理
- Closed Shadow Root — 未处理
- 启动参数 — 未修改（需自行配置）
- 指纹伪装 — 不在范围内

### 2.4 配置方式

```bash
# 环境变量（运行时可切换）
REBROWSER_PATCHES_RUNTIME_FIX_MODE=addBinding    # 默认
REBROWSER_PATCHES_RUNTIME_FIX_MODE=alwaysIsolated
REBROWSER_PATCHES_RUNTIME_FIX_MODE=enableDisable
REBROWSER_PATCHES_RUNTIME_FIX_MODE=0              # 禁用

REBROWSER_PATCHES_SOURCE_URL=app.js
REBROWSER_PATCHES_UTILITY_WORLD_NAME=util
REBROWSER_PATCHES_DEBUG=1
```

### 2.5 集成方式

```bash
# 方式 1：打补丁（npm install 后需重新执行）
npx rebrowser-patches@latest patch --packageName playwright-core

# 方式 2：替换包（推荐，一劳永逸）
# package.json:
#   "playwright-core": "1.58.2" → "rebrowser-playwright-core": "1.58.2"
# 无需改 import 路径
```

方案 A 测试下来与 openclaw 存在一定兼容性问题。

openclaw 使用 playwright 1.58.2 版本，但是 rebrowser-patches 最新只在 playwright 1.52.0 版本上进行过全面测试。

openclaw 高度依赖 playwright 的私有 api，比如 _snapshotForAI() 等。应用 rebrowser-patches 后，此接口无法工作。

---

## 三、方案 B：Patchright

### 3.1 项目概况

- GitHub: `Kaliiiiiiiiii-Vinyzu/patchright` + `patchright-python` (1.1k stars)
- 方式：fork Playwright 源码，通过 ts-morph AST 重写 22 个核心模块，编译为独立包
- 支持：仅 Playwright
- 自动化：每小时检查 Playwright 新版本，自动 patch 并发布

### 3.2 修补内容

| 补丁 | 详情 |
|------|------|
| **Runtime.enable 移除** | 从 crPage、crDevTools、crServiceWorker 中直接删除调用 |
| **Console.enable 禁用** | 完全移除 Console domain |
| **启动参数清理** | 移除 `--enable-automation` 等 6 个参数，添加 `--disable-blink-features=AutomationControlled` |
| **init script 注入** | 改为 HTTP route interception → 在 HTML `<head>` 中注入 `<script>` 标签 |
| **CSP bypass** | 自动修改 Content-Security-Policy，添加 nonce/unsafe-inline |
| **sourceURL 移除** | 删除所有 `//# sourceURL` 注释 |
| **Service Worker** | 静默阻止注册（移除 console.warn 暴露信息） |
| **Closed Shadow Root** | 支持穿透 mode:'closed' 的 Shadow DOM |
| **evaluate() 改造** | 新增 `isolated_context` 参数（默认 true） |

### 3.3 代价

| 失去的能力 | 影响 |
|-----------|------|
| **Console API 完全禁用** | `page.on("console")` 永远不触发 |
| **page.pause() 调试** | 未知是否受影响 |
| **Console 日志收集** | 需要替代方案（JS 注入） |

### 3.4 集成方式

```bash
# 必须改 import 路径
# package.json:
#   "playwright-core": "1.58.2" → "patchright-core": "1.57.0"
# 所有源码:
#   import { chromium } from "playwright-core" → import { chromium } from "patchright-core"
```

已在本仓库落地（2026-02-22）：

- `openclaw/package.json` 已切换到 `patchright-core@1.57.0`（当前 npm 可用最新版本）
- `openclaw/src/browser/*` 中所有 `playwright-core` import 已切换为 `patchright-core`
- `scripts/dev.sh` / `scripts/apply-patches.sh` 已移除 rebrowser 自动补丁流程
- 上游改动已生成业务补丁：`patches/001-switch-playwright-to-patchright-core.patch`

### 3.5 已知问题（来自 GitHub Issues）

- `#94` 新版本反而被检测到（dist-info 暴露）
- `#100` Cloudflare 403 错误
- `#101` Google Anti-Bot 触发
- `#170` Sannysoft 检测到 patchright

---

## 四、方案对比

### 4.1 核心差异

| 维度 | rebrowser-patches | Patchright |
|------|-------------------|-----------|
| **修补方式** | 运行时打补丁 / drop-in 包 | 编译时 fork 重写 |
| **改动侵入性** | 低 — 可一键回退 | 高 — 需改所有 import |
| **Runtime.enable** | 3 种模式可选，默认 addBinding | 单一方案 isolated context |
| **Console API** | **保留** | **禁用** |
| **main world 访问** | ✅ addBinding 模式完整保留 | ⚠️ isolated context 有局限 |
| **init script 注入** | 未改（仍走 CDP） | ✅ 改为 HTML 注入 |
| **CSP bypass** | 未处理 | ✅ 自动处理 |
| **Closed Shadow Root** | 未处理 | ✅ 支持穿透 |
| **启动参数清理** | 未处理（需自行配置） | ✅ 自动清理 |
| **配置灵活性** | 环境变量运行时切换 | 编译时固定 |
| **`_snapshotForAI` 兼容** | 大概率兼容（改动面小） | 风险较高（重写面广） |
| **OpenClaw console 收集** | ✅ 不受影响 | ❌ 需要改造 |
| **GitHub dependents** | 有 drop-in 替代包生态 | 0 个已知依赖项目 |
| **反检测通过率** | 未公开完整测试 | 声称通过 Cloudflare/Kasada/Datadome 等（但有 issue 反馈失败） |

### 4.2 适用场景判断

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| **OpenClaw 集成（首选）** | rebrowser-patches | Console API 保留、改动小、风险低、可回退 |
| **需要最激进反检测** | Patchright | init script HTML 注入 + CSP bypass + closed shadow root |
| **快速验证可行性** | rebrowser-patches | 一行命令打补丁，不改代码 |
| **长期维护** | 两者均可 | rebrowser 有 drop-in 包；patchright 自动跟踪上游 |

---

## 五、OpenClaw 集成改造方案

### 5.1 Phase 1：最小改动验证（rebrowser-patches）

**目标**：零代码修改，验证基本兼容性

```bash
cd openclaw
# 打补丁
npx rebrowser-patches@latest patch --packageName playwright-core

# 设置环境变量
export REBROWSER_PATCHES_RUNTIME_FIX_MODE=addBinding
export REBROWSER_PATCHES_SOURCE_URL=app.js
export REBROWSER_PATCHES_UTILITY_WORLD_NAME=util

# 启动 OpenClaw 并测试
```

**验证清单**：
- [ ] OpenClaw 正常启动
- [ ] `_snapshotForAI()` 正常工作
- [ ] `page.on("console")` 事件正常触发
- [ ] `page.evaluate()` 正常执行
- [ ] 页面导航和元素交互正常
- [ ] Extension relay 模式正常工作
- [ ] 非 Extension 模式正常工作

### 5.2 Phase 2：反检测效果测试

**目标**：量化反检测提升

使用以下检测网站逐一测试：

| 检测站 | URL | 测试项 |
|--------|-----|-------|
| CreepJS | `https://nicepkg.github.io/nicepkg-test/` | 综合指纹 |
| Sannysoft | `https://bot.sannysoft.com/` | navigator.webdriver 等 |
| Incolumitas | `https://bot.incolumitas.com/` | 高级检测 |
| Browserscan | `https://browserscan.net/` | 浏览器指纹 |
| Pixelscan | `https://pixelscan.net/` | 指纹一致性 |

**测试矩阵**（6 种组合）：

```
                          未打补丁    rebrowser-patches
非 Extension 模式:          A1              A2
Extension + 真实 Chrome:    B1              B2
```

**对比指标**：
- 各检测站得分/通过项
- `navigator.webdriver` 值
- Runtime.enable 是否泄露
- CreepJS Trust Score

### 5.3 Phase 3：Patchright 对比测试

**目标**：评估 Patchright 的额外收益是否值得代价

```bash
cd openclaw
# 替换包
# package.json: "playwright-core" → "patchright-core"
# 批量替换 import（8 个文件）
# 改造 console 收集逻辑

# 同样跑 Phase 2 的测试矩阵
```

**额外验证**：
- [ ] `_snapshotForAI()` 是否兼容（最关键）
- [ ] Console 收集替代方案是否可靠
- [ ] init script HTML 注入是否带来额外通过率

### 5.4 Phase 4：生产化改造（基于 Phase 2/3 结果选择方案）

**如果选 rebrowser-patches**：
```json
// package.json
{
  "dependencies": {
    "rebrowser-playwright-core": "1.58.2"  // 替代 playwright-core
  }
}
```

**额外加固**（无论选哪个方案）：
- [ ] OpenClaw 非 Extension 模式：添加 `--disable-blink-features=AutomationControlled` 到启动参数
- [ ] OpenClaw 非 Extension 模式：移除 `--enable-automation` 等自动化参数
- [ ] 审查 `cdp.ts` 中的 `Runtime.enable` 直接调用，评估是否可以移除
- [ ] Extension 模式：考虑添加 `chrome.runtime.onStartup` 自动重连

---

## 六、OpenClaw raw CDP 层清理

OpenClaw 自有的 `cdp.ts` 直接通过 WebSocket 发送 CDP 命令，绕过了 Playwright driver：

```typescript
// 这些调用不经过 Playwright，不受 rebrowser-patches / patchright 影响
send("Runtime.enable")
send("Runtime.evaluate", { expression, awaitPromise })
send("Runtime.terminateExecution")
```

**需要评估**：
1. `Runtime.enable` 是否可以移除？在只做 `Runtime.evaluate` 的场景下，某些 Chrome 版本不需要先 enable
2. `Runtime.terminateExecution` 是否需要先 enable？需测试
3. 如果必须 enable，可以参考 rebrowser-patches 的 enableDisable 模式（快速 enable → 拿到 contextId → 立即 disable）

---

## 七、检测面全景图

改造完成后，两种模式的检测面：

### 非 Extension 模式（rebrowser-patches + 参数清理）

```
✅ 已消除:
  - Runtime.enable 泄露（rebrowser-patches addBinding 模式）
  - sourceURL 特征（rebrowser-patches）
  - utility world 名称（rebrowser-patches）
  - navigator.webdriver（--disable-blink-features=AutomationControlled）
  - --enable-automation 参数

⚠️ 仍存在:
  - --remote-debugging-port 参数（必需）
  - Console.enable（rebrowser-patches 未处理）
  - Playwright ���带 Chromium 指纹（如果不用 connectOverCDP）
  - OpenClaw cdp.ts 的 Runtime.enable（需单独清理）
  - init script 通过 CDP 注入（rebrowser-patches 未改）
```

### Extension + 真实 Chrome 模式（rebrowser-patches + 参数清理）

```
✅ 已消除:
  - Runtime.enable 泄露
  - sourceURL 特征
  - utility world 名称
  - navigator.webdriver
  - --remote-debugging-port（Extension 不需要）
  - --enable-automation（Extension 不需要）
  - 浏览器指纹差异（真实 Chrome）
  - 空 Profile（真实用户 Profile）
  - 所有自动化启动参数（零参数）

⚠️ 仍存在:
  - Console.enable
  - OpenClaw cdp.ts 的 Runtime.enable（需单独清理）
  - init script 通过 CDP 注入
  - Chrome 扩展可能被探测（chrome://extensions 可见）
  - chrome.debugger 调试横幅（页面 JS 不可检测，但用户可见）
```

如果用 Patchright 替代 rebrowser-patches，Console.enable 和 init script 注入也可以消除，但代价是失去 Console API 和更高的兼容风险。

---

## 八、参考文件索引

### 项目源码

| 项目 | 关键文件 | 用途 |
|------|---------|------|
| OpenClaw | `src/browser/pw-session.ts:335` | `chromium.connectOverCDP()` 连接入口 |
| OpenClaw | `src/browser/pw-session.ts:217-283` | 页面事件监听（含 console） |
| OpenClaw | `src/browser/pw-tools-core.snapshot.ts:54-62` | `_snapshotForAI()` 调用 |
| OpenClaw | `src/browser/extension-relay.ts` | Extension relay 服务器 |
| OpenClaw | `assets/chrome-extension/background.js` | 扩展核心逻辑 |
| OpenClaw | `src/browser/cdp.ts` | Raw CDP 层（含 Runtime.enable） |
| rebrowser-patches | `patches/playwright-core/src.patch` | Playwright 核心补丁 |
| rebrowser-patches | `scripts/patcher.js` | 补丁应用脚本 |
| Patchright | `patchright_driver_patch.js` | 主编排脚本 |
| Patchright | `driver_patches/crPagePatch.js` | 最大补丁（~470 行） |
| Patchright | `driver_patches/crNetworkManagerPatch.js` | HTTP 注入补丁（~465 行） |

### 检测原理参考

| 检测向量 | 说明 |
|---------|------|
| `Runtime.enable` leak | CDP domain 激活后浏览器内部行为变化，可被页面 JS 通过侧信道检测 |
| `navigator.webdriver` | `--enable-automation` 会设置此属性为 true |
| `sourceURL` fingerprint | 注入脚本的 `//# sourceURL=pptr:evaluate` 注释暴露自动化框架 |
| utility world detection | 命名为 `__playwright_utility_world__` 的执行上下文可被枚举 |
| Chrome binary fingerprint | Playwright 自带 Chromium 的 UA/WebGL/内部 API 与正版 Chrome 有差异 |
| launch args fingerprint | 大量 `--disable-*` 参数的组合是自动化特征 |
| empty profile | 无历史记录、无 Cookie、空 localStorage 是强自动化信号 |

---

## 九、明日实验计划

### 优先级排序

1. **rebrowser-patches 基础验证**（Phase 1）— 30 分钟
   - 打补丁 → 启动 OpenClaw → 基本功能测试

2. **反检测效果量化**（Phase 2）— 1 小时
   - 6 种组合 × 5 个检测站 = 30 次测试

3. **Patchright 验证**（Phase 3，如果 Phase 2 不够好）— 1-2 小时
   - 替换包 → 兼容性测试 → 反检测测试

4. **cdp.ts 清理评估**（Phase 4）— 视前几步结果而定

### 预期结论

- 如果 rebrowser-patches 的 addBinding 模式能通过主流检测站且 OpenClaw 功能正常 → 选 rebrowser-patches
- 如果 rebrowser-patches 不够且 Patchright 额外通过了关键检测 → 评估 Patchright 的兼容成本是否可接受
- 如果两者都不够 → 考虑组合方案（rebrowser-patches + 额外 JS 注入补充）
