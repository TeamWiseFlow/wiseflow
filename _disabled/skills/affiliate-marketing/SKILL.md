---
name: affiliate-marketing
description: Scrape Amazon product details via browser and generate platform-optimized promotional content (Twitter/X, Instagram, WeChat) using LLM. No third-party API needed — browser-based extraction only.
metadata:
  {
    "openclaw":
      {
        "emoji": "🛒",
        "always": false,
      },
  }
---

# Affiliate Marketing 技能

Use this skill when:
- User provides an Amazon product affiliate link
- You need to generate promotional content for multiple social media platforms
- You need to cross-post a product pitch to Twitter/X, Instagram, or WeChat

**Prerequisites**: Browser session must be able to access amazon.com (international) or amazon.cn (China).

---

## Step 1 — Extract Product Information from Amazon

```
1. Navigate to https://www.amazon.com (warmup — wait for homepage to load)
2. Navigate to the affiliate product URL provided by the user
3. Wait 2–3 seconds for full page render
4. Extract the following elements:

   Title:
     - Find element with id="productTitle"
     - text().strip()

   Price:
     - Try id="priceblock_ourprice" first
     - Fallback: find element with class containing "a-price-whole"
     - Fallback: find element with class "a-offscreen" (screen-reader price)

   Rating:
     - Find id="acrPopover", read the title attribute (e.g., "4.5 out of 5 stars")
     - OR find element with class "a-icon-alt"

   Review Count:
     - Find id="acrCustomerReviewText" → text (e.g., "1,234 ratings")

   Feature Bullets:
     - Find id="feature-bullets"
     - Extract all <li> text items (skip "Make sure this fits" disclaimer)
     - Keep top 3–5 most relevant features

   Main Image URL:
     - Find id="landingImage" or id="imgBlkFront"
     - Read the "src" or "data-old-hires" attribute

5. If any element is missing, skip it and continue with available data
6. If CAPTCHA or "To discuss automated access" appears → stop and report to user
```

---

## Step 2 — Build the Affiliate Link

Verify the URL already contains the affiliate tag (`?tag=` or `&tag=`). If it doesn't:
1. Ask the user for their Amazon Associate Tag
2. Append `?tag={associate_tag}` to the product URL (clean URL: `https://www.amazon.com/dp/{ASIN}?tag={tag}`)

---

## Step 3 — Generate Promotional Content

Use LLM to generate platform-specific content. Call the LLM with the product data collected:

### Twitter/X version (≤280 characters)
```
Prompt: "Write a promotional tweet for this Amazon product. Include 3 relevant hashtags.
Under 280 characters including the link placeholder [LINK].
Product: {title}
Price: {price}
Key features: {top_3_features}
Tone: enthusiastic but honest
Return ONLY the tweet text."
```
After generation, replace `[LINK]` with the actual affiliate URL.

### Instagram caption
```
Prompt: "Write an Instagram caption for this Amazon product.
Structure: 1 hook sentence + 3-4 feature highlights as emoji bullet points + CTA + hashtags (10-15 tags at the end).
Product: {title}, Price: {price}, Rating: {rating}
Features: {features}
Return ONLY the caption."
```

---

## Step 4 — Review & Distribute

1. Present all generated content to user for review (L2)
2. User selects which platforms to publish to
3. Execute publishing (L3):
   - Twitter: call `twitter-post` skill
   - Instagram: call `instagram-post` skill with the product main image URL

---

## Common Amazon DOM Caveats

| Issue | What to do |
|-------|-----------|
| Price shows "$0.00" or missing | Look for "See price in cart" — report to user, use "See price in cart" as placeholder |
| Feature bullets not found | Use product description instead (id="productDescription") |
| Page redirects to login | Amazon session issue — try without warmup or report to user |
| Different page layout (A+ content) | Extract from title + description only |
| CAPTCHA | Stop immediately, report to user |

---

## Notes

- Always include the affiliate tag in the final link — this is how commissions are tracked
- Do not fabricate product features or fake reviews
- If product is out of stock, mention it honestly or skip the campaign
- use `browser-guide` skill to perform browser actions