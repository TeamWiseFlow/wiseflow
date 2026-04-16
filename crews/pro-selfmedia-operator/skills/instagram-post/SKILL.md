---
name: instagram-post
description: Publish a photo, video, or carousel to Instagram using the browser. Supports feed posts and Reels.
metadata:
  {
    "openclaw":
      {
        "emoji": "📸",
        "always": false,
      },
  }
---

# Instagram 发布技能

Use this skill when:
- The user wants to publish a photo or video to Instagram Feed or Reels
- You need to cross-post an image or short video to Instagram
- You need to set caption, hashtags, and alt text

**Prerequisites**: Browser session must be logged in to instagram.com.

---

## Cookie Warmup

Navigate to `https://www.instagram.com` first and confirm the feed loads (not a login screen).

---

## Workflow: Post Photo or Single Video (Feed)

```
1. Navigate to https://www.instagram.com
2. Wait for feed to load
3. Click the "+" (Create) button in the top navigation bar (or left sidebar)
4. In the "Create new post" dialog, click "Post"
5. Click "Select from computer" and upload the media file
   - Photo: JPG/PNG, min 1080px on shortest side (square 1:1 or 4:5 portrait recommended)
   - Video: MP4/MOV, max 60 seconds for Feed, 15–90 seconds for Reels
6. Crop/resize the image if prompted (choose the appropriate aspect ratio)
7. Click "Next"
8. (Optional) Apply a filter or do manual adjustments → Click "Next"
9. On the caption screen:
   - Write the caption (max 2200 characters)
   - Add hashtags at the end (max 30 per post)
   - Add location if relevant
   - Add collaborators if needed
   - Toggle "Advanced settings" for:
     - Alt text (for accessibility)
     - Audience restrictions
10. Click "Share"
11. Wait for confirmation and report the post URL
```

---

## Workflow: Post Reel (Short Video ≤ 90s)

```
1. Navigate to https://www.instagram.com
2. Click "+" → Select "Reel"
3. Upload video file (MP4/MOV, 9:16 preferred, max 90 seconds)
4. Trim clip if needed
5. Add audio (optional) — use original audio or select from Instagram's music library
6. Select cover frame
7. Click "Next"
8. Write caption + hashtags
9. Click "Share"
```

---

## Workflow: Carousel (Multiple Photos/Videos)

```
1. Click "+" → Post
2. Click the layers icon (Select Multiple) before choosing the first file
3. Select up to 10 photos/videos in order
4. Click "Next" twice (through filters screen)
5. Write caption + hashtags
6. Click "Share"
```

---

## Caption Best Practices

- First sentence = hook (shown in feed preview)
- Main body: 2–4 sentences of context or story
- Hashtag block at end: mix popular (#instagram, #photography) with niche tags
- Emoji sparingly to increase personality
- Call to action (CTA) in last line: "Save this" / "Share with someone who needs this"

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Login screen appears | Session expired — inform user to re-login |
| File format not accepted | Convert to JPG/PNG (photos) or MP4 H.264 (video) |
| Video too long | Trim to 60s (Feed) or 90s (Reels) |
| Post button unavailable | Check if caption or media step is incomplete |
| "Action blocked" error | Account may have hit limits — wait 1 hour before retrying |

---

## Notes

- Instagram's UI evolves — navigate by intent if elements have moved
- Always confirm post URL or profile page after completion
- Do NOT post content that violates Instagram Community Standards
