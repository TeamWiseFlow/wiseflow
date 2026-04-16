---
name: twitter-post
description: Compose and publish a post (text, image, or video) to Twitter/X using the browser. Supports single and thread posts.
metadata:
  {
    "openclaw":
      {
        "emoji": "🐦",
        "always": false,
      },
  }
---

# Twitter/X 发布技能

Use this skill when:
- The user wants to post text, images, or video to Twitter/X
- You need to share a created article excerpt or key insights on X
- You need to cross-post content to international audiences

**Prerequisites**: The browser session must be logged in to x.com. Warm up with a homepage visit if session is cold.

---

## Cookie Warmup

Always navigate to `https://x.com` first and confirm the feed loads (not a login page) before proceeding.

---

## Workflow: Post Plain Text

```
1. Navigate to https://x.com/compose/post
2. Wait for the compose box to load
3. Click into the text area and type the content
   - Plain text only (no Markdown)
   - Max 280 characters for standard accounts
4. Verify character count — trim if over limit
5. Click the "Post" button
6. Wait for success confirmation (URL changes or "Your post was sent" toast)
7. Extract and report the post URL
```

---

## Workflow: Post with Image

```
1. Navigate to https://x.com/compose/post
2. Wait for the compose box to load
3. Click the media icon (camera/photo button below compose box)
4. Upload the image file using the file picker
5. Wait for image upload to complete (thumbnail appears)
6. Type the caption text in the compose box
7. Click "Post"
8. Wait for confirmation and report the post URL
```

---

## Workflow: Post with Video

```
1. Navigate to https://x.com/compose/post
2. Click the media icon
3. Upload the video file (MP4 recommended, max 512MB, max 2min 20sec)
4. Wait for video processing — this can take 30–120 seconds
5. Type the caption in the compose box
6. Click "Post"
7. Wait for upload confirmation and report the post URL
```

---

## Workflow: Thread (multiple posts)

```
1. Navigate to https://x.com/compose/post
2. Type the first tweet
3. Click the "+" icon to add another tweet to the thread
4. Type the second tweet
5. Repeat for each additional tweet
6. Click "Post all" to publish the full thread
```

---

## Content Limits

| Type | Limit |
|------|-------|
| Text | 280 characters (standard) |
| Images | Up to 4 per post |
| Video | Max 512 MB, max 2m 20s |
| GIF | Max 15 MB |

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Login page appears | Session expired — inform user to re-login via browser |
| Character limit exceeded | Trim content or use thread format |
| Media upload fails | Retry once; check file format and size |
| Rate limit error | Wait 15 minutes before retrying |
| Post button greyed out | Content is empty or over limit — check before clicking |

---

## Notes

- Do NOT mention internal tool names or errors in any post
- All post content must comply with X's terms of service
- If posting on behalf of company: verify the content tone matches the company voice in MEMORY.md
