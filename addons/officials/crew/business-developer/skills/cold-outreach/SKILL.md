---
name: cold-outreach
description: Find local businesses on Google Maps, extract contact emails from their websites, generate personalized outreach emails with LLM, and send via SMTP. Full pipeline for B2B cold email campaigns.
metadata:
  {
    "openclaw":
      {
        "emoji": "📧",
        "always": false,
        "requires": { "bins": ["python3"] },
        "requiredEnv": ["SMTP_SERVER", "SMTP_USER", "SMTP_PASSWORD"],
        "optionalEnv": ["SMTP_PORT", "SMTP_FROM", "SILICONFLOW_API_KEY"],
      },
  }
---

# Cold Outreach 技能

Use this skill when:
- User wants to find local businesses in a specific niche and location
- You need to extract business contact information from Google Maps
- You need to generate and send personalized cold outreach emails

---

## Step 1 — Find Businesses on Google Maps

```
1. Warm up: navigate to https://www.google.com/maps

2. Perform the search:
   https://www.google.com/maps/search/{niche}+{location}
   Example: https://www.google.com/maps/search/餐厅+上海朝阳区

3. Wait 3 seconds for results to load

4. For each visible business card in the sidebar:
   Extract:
   - Business name (visible heading)
   - Rating (if shown)
   - Address (if shown)
   - Phone number (if shown)
   - Website URL (if a link icon is present → click to get URL, then go back)

5. Scroll down to load more results (up to the user-specified limit, default: 20)

6. If Google shows CAPTCHA or "unusual traffic" → stop immediately, report to user

7. Save collected data to: ./outreach_data/businesses_YYYY-MM-DD.csv
```

CSV format:
```
name,address,phone,website,email
"上海味道餐厅","上海市朝阳区xxx路123号","010-12345678","https://example.com",""
```

---

## Step 2 — Extract Emails from Websites

For each business that has a website URL:

```
Method A — xurl (fast, for static sites):
  Use xurl to GET the homepage
  Apply regex: \b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b
  If email found → record it

Method B — browser (for JS-rendered sites, if Method A fails):
  Navigate to the homepage
  If no email found on homepage → try /contact and /about paths
  Search for "mailto:" links or visible email text

If no email found after both methods → leave email column empty, log "no_email"
```

Pause 0.5–1 second between each website request to avoid rate limiting.

---

## Step 3 — Generate Personalized Outreach Emails

For each business with a valid email address, generate a personalized email:

```
LLM Prompt:
"Write a brief, personalized cold outreach email in [Chinese/English].

Business name: {business_name}
Industry: {niche}
Our offer: {user_provided_value_proposition}

Rules:
- Subject line: concise, specific to their business (NOT generic)
- Body: 3–4 sentences max
  1. Opening: reference their specific business (show you did research)
  2. Value: what we can do for them (focus on their benefit, not our product)
  3. CTA: one clear, low-friction ask (e.g., 'Would you be open to a 15-minute call?')
- Plain text only (no HTML, no markdown)
- No pushy sales language

Return JSON:
{
  'subject': '...',
  'body': '...'
}"
```

---

## Step 4 — Send Emails via SMTP

For each business with subject + body generated:

```bash
python3 ./skills/cold-outreach/scripts/send_email.py \
  --to "{business_email}" \
  --subject "{subject}" \
  --body "{body}"
```

Wait 2–3 seconds between each send.

**Track results in real time:**
- ✅ Sent successfully → log to `outreach_data/sent_YYYY-MM-DD.csv`
- ❌ Failed → log to `outreach_data/failed_YYYY-MM-DD.csv` with error reason

---

## send_email.py Usage

```bash
# Send with inline body text
python3 ./skills/cold-outreach/scripts/send_email.py \
  --to "target@example.com" \
  --subject "Subject line" \
  --body "Email body text"

# Send with body from file
python3 ./skills/cold-outreach/scripts/send_email.py \
  --to "target@example.com" \
  --subject "Subject line" \
  --body-file ./outreach_data/template.txt
```

Returns JSON:
```json
{"ok": true, "to": "target@example.com", "message": "sent"}
{"ok": false, "to": "target@example.com", "error": "Connection refused"}
```

---

## SMTP Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SMTP_SERVER` | SMTP hostname | `smtp.gmail.com` |
| `SMTP_PORT` | Port (default: 587) | `587` |
| `SMTP_USER` | Login / sender address | `you@gmail.com` |
| `SMTP_PASSWORD` | Password or app password | `xxxx xxxx xxxx` |
| `SMTP_FROM` | Display name + address | `张三 <you@gmail.com>` |

**Gmail users**: Must use App Passwords (Google Account → Security → App Passwords). Regular passwords will be rejected.

**QQ Mail**: use SMTP password from QQ mail settings → POP3/SMTP, server: `smtp.qq.com`, port `587`.

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Google CAPTCHA | Stop collection, report to user |
| Business website returns 4xx/5xx | Log as "unreachable", skip email extraction |
| SMTP auth failure | Stop sending, check credentials with user |
| SMTP connection refused | Check SMTP_SERVER and SMTP_PORT |
| `SMTPDataError: 550` spam rejection | Stop sending — email content flagged as spam, revise template |

---

## Anti-Spam Best Practices

- Personalize each email (business name at minimum)
- Send no more than 50–100 emails per day from a single address
- Include a genuine unsubscribe note: "如不希望收到此类邮件，请直接回复告知，谢谢。"
- Use a real business email, not a free webmail (gmail.com for cold outreach has high spam rate)
