---
name: reminder
description: Maintain Main Agent reminder.json for onboarding, work channel recommendations, HRBP enablement, Media Operator bootstrap, and Gateway restart followups.
metadata:
  openclaw:
    emoji: 🔔
---

# Reminder

Use this skill during Main Agent heartbeat or when the user asks for onboarding status.

Commands:

- `python ./skills/reminder/scripts/update-reminders.py`

The script updates `~/.openclaw/workspace-main/reminder.json`.

Do not notify repeatedly. Respect `lastNotifiedAt`, `snoozedUntil`, and `status` fields when present.
