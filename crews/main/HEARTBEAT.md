# Main Agent — Heartbeat

## Daily Reminder Check

Run once per day or when explicitly asked to refresh onboarding state.

Checklist:

1. Read `~/.openclaw/openclaw.json`.
2. Count internal crew excluding `main`.
3. Check whether `it-engineer` has a direct work channel binding.
4. Check whether `hrbp` is enabled and whether it has a direct work channel binding.
5. Check whether any external crew exists without required binding.
6. Check whether Media Operator workspace still has an incomplete `BOOTSTRAP.md`.
7. Check whether `pending-followup.json` exists.
8. Update `reminder.json` via `./skills/reminder/scripts/update-reminders.py`.
9. Surface only due reminders that are not snoozed or recently shown.

## Reminder Triggers

- Internal crew count excluding `main` > 3 → recommend Feishu or WeCom work channel.
- First external crew request or HRBP enablement → require HRBP/work channel planning.
- First work channel binding and IT Engineer lacks binding → ask whether to bind IT Engineer too.
- HRBP enabled or about to be enabled and lacks binding → ask whether to bind HRBP too.
- Pending Gateway restart followup → verify recovery and report.
- Media Operator BOOTSTRAP incomplete → guide initialization.

## Health Check

- Status: operational
- Active sub-agents: see live `openclaw.json` and MEMORY.md supplement
- User entry channel: `openclaw-weixin` direct chat
