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

When a page shows a login wall (sign-in form, "please log in" banner, OAuth redirect, etc.):

1. **Try the browser's built-in password manager first**: check whether the login form has auto-filled credentials from saved passwords. If so, use them to complete the login.
2. If no saved credentials are available, **do NOT make up usernames or passwords, and do NOT attempt to register a new account**.
3. Send a message to the user: _"xx 页面需要登录，浏览器中没有预存密码，请在浏览器中完成登录或注册，完成后请通知我。"_（xx 为页面标题）.
4. Wait for the user to confirm.
5. If no response arrives within **5 minutes**, assume the user is unavailable and continue with whatever content is accessible.

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
