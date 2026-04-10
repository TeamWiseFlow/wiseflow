---
name: browser-guide
description: Best practices for using the managed browser — handling login walls, CAPTCHAs, lazy-loaded content, paywalls, and tab cleanup.
metadata:
  {
    "openclaw":
      {
        "emoji": "🌐",
        "always": true,
      },
  }
---

# Browser Best Practices

Follow these rules whenever you use the `browser` tool to interact with web pages.

## 1. Login Prompts

When a page shows a login wall, first identify which login mechanism is offered, then follow the matching procedure below.

**General constraint: retry at most 2 times per login attempt — frequent retries risk account suspension.**

### 1-A. Browser saved credentials

1. Check whether the login form has auto-filled credentials from saved passwords. If so, use them.
2. On failure, continue to 1-B / 1-C / 1-D as appropriate.

### 1-B. QR Code login

When the login page shows a QR code (WeChat Official Account backend, Xiaohongshu creator centre, X/Twitter, etc.):

1. Use `snapshot` to locate the QR code image element. Download / screenshot it and save it to `/tmp/` (e.g., `/tmp/xhs_qr.png`).
2. Read the file with the `Read` tool so it is displayed inline to the user:
   ```
   Read: /tmp/xhs_qr.png
   ```
3. Notify the user:
   > "**[平台名称]** 登录已失效（或首次使用），请用 **[平台]** APP 扫描以下二维码登录。扫码并在手机上点击确认后，回复"已扫码"。"
4. **Stop and wait** for the user to reply "已扫码"、"好了"、"扫完了" or any equivalent confirmation before continuing.
5. While waiting, poll the page every **3 seconds** using `snapshot` for signs of successful login (URL change, QR code disappears, dashboard/avatar appears). If auto-detected, resume immediately without waiting for the user reply.
6. If no scan occurs within **3 minutes** and no reply arrives, send: _"扫码超时，将继续处理当前可访问的内容。"_ and proceed.

### 1-C. SMS verification login

When the login page asks for a phone number and SMS verification code:

1. Ask the user for the registered phone number for this platform:
   > "**[平台名称]** 需要手机验证码登录，请告知您在该平台注册的手机号。"
2. Once received, enter the phone number and trigger the SMS code request. Attempt at most **2 times** if the first trigger fails.
3. Ask the user for the verification code:
   > "短信验证码已发送，请将收到的验证码回复给我。"
4. Enter the code and complete login. If login fails, inform the user and proceed with accessible content — **do not retry a third time**.

### 1-D. Username / password login

When only a username + password form is available:

1. Check for browser-saved credentials first (see 1-A).
2. If none, ask the user for their preference:
   > "**[平台名称]** 需要账号密码登录，浏览器中未找到预存密码。请选择：① 您自行在浏览器中登录后告知我，② 告知用户名和密码由我代为登录。"
3. If the user chooses ②, receive the credentials and attempt login. Retry at most **2 times** on failure.
4. If login fails after 2 attempts, inform the user and continue with accessible content.

### 1-E. Fallback — login not possible

If login cannot be completed for any reason (timeout, user unavailable, repeated failures):

- **Do NOT stop or abort the task.**
- Continue with whatever content is accessible in the non-logged-in state.
- At the end, include a note in the result: _"注：[平台名称] 未能完成登录，以下内容来自未登录状态，可能不完整。"_

## 2. Simple Verification / CAPTCHA

When a page shows a one-click verification challenge (e.g., a button labelled "去验证", "Verify", "I'm not a robot", or a simple checkbox):

1. Try clicking the verification button/checkbox directly.
2. Wait a few seconds for the page to refresh.
3. Take a snapshot to check whether normal content has loaded.
4. If the page now shows the expected content, continue your task.

## 3. Complex Verification Fallback

If the simple click in Step 2 above **fails** — the page still shows a challenge, the challenge is a puzzle/slider/image-selection CAPTCHA, or an error occurs:

1. **Do NOT retry blindly.** Stop attempting automated verification.
2. Send a message to the user: _"xx 页面有验证码，我无法解决，请在浏览器中完成，完成后请通知我。"_（xx 为页面标题）.
3. Wait for the user to confirm.
4. If no response arrives within **5 minutes**, continue with whatever content is accessible.

## 4. Lazy-Loaded Content

When a page uses lazy loading (infinite scroll, "load more" sections, content that appears only after scrolling):

1. Before scrolling, assess whether the not-yet-loaded content is **relevant** to the current task.
2. If relevant, simulate human-like scrolling: scroll down incrementally, pause briefly between scrolls to allow content to load, then take a snapshot to capture the new content.
3. Repeat until the needed content is visible or no more new content loads.
4. Do NOT scroll too fast, do it as a human would. After 7 times of scrolling, you should stop this turn.
5. If not relevant, skip scrolling and work with what is already loaded.

## 5. Paywall / Subscription Walls

When a page indicates that content is behind a paywall or requires a specific subscription (e.g., "Subscribe to continue reading", "Continue reading with a WSJ subscription", premium-only banners):

1. Send a message to the user describing the situation: _"xx 页面需要订阅，请在浏览器中登录有效账号或者完成付费，完成后请通知我。"_（xx 为页面标题）.
2. Wait for the user to confirm.
3. If no response arrives within **5 minutes**, continue with whatever content is accessible (summary, headline, or any visible excerpt).
