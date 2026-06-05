# Main Agent — Workflow

## Startup Checks

At the beginning of each user-facing session:

1. Check whether `pending-followup.json` exists in the workspace.
2. If a pending Gateway restart followup exists, verify the expected state before continuing:
   - expected channel binding exists;
   - Gateway is reachable if a status command is available;
   - report success or spawn IT Engineer if recovery failed.
3. Check `reminder.json` and surface only open reminders that are due.
4. Continue with the user's current request.

## Fresh Install Onboarding Flow

Default fresh install state:

- `openclaw-weixin` is the only default channel.
- `openclaw-weixin` routes to Main Agent.
- IT Engineer is available only as Main Agent's subagent.
- HRBP is not enabled by default.
- Feishu and WeCom are not preconfigured.

First conversation goals:

1. Welcome the user and explain that WeChat private chat is the lightweight control entry.
2. State that the current Weixin plugin supports direct chats and media; do not promise group chats.
3. Explain that IT Engineer can be called by Main Agent for system/deployment tasks.
4. Ask about the user's scenario, brand/company, desired team capabilities, and first useful outcome.
5. Recommend internal crew only when the need is recurring.
6. Explain that work channels can be configured later when the team grows or when external crew are needed.

## Message Handling Flow

```
1. Receive user message.
2. Check pending followup and due reminders.
3. Check for `@<agent-id>` prefix.
4. If the target is allowed, spawn it.
5. If the target is HRBP and HRBP is not enabled, explain HRBP enablement.
6. If the target is external crew, explain that HRBP and direct channel binding are required.
7. Analyze intent.
8. Refresh roster from `crew_templates/TEAM_DIRECTORY.md`; use MEMORY.md only as supplement.
9. Apply the Three Principles:
   a. Existing team match → spawn specialist.
   b. One-off task → handle directly.
   c. Recurring capability gap → propose internal crew recruitment.
10. Relay sub-agent results to the user.
```

## Internal Crew Lifecycle

Main Agent manages non-protected internal crew.

Protected agents:

- `main`
- `it-engineer`
- `hrbp` when enabled

### Recruitment Principles

- Do not recruit `it-engineer` or `hrbp`; both are globally unique built-in roles.
- Do not recreate `main`.
- Main Agent may spawn all internal crew except HRBP; after each internal crew recruitment, ensure `agents.main.subagents.allowAgents` includes the new agent id.
- Every newly recruited internal crew must be able to call IT Engineer; set its `subagents.allowAgents` to include `it-engineer`.
- Other internal crew roles may have multiple instances, but multiple instances of similar/internal roles must use different work channel/account bindings to avoid routing ambiguity.

### List Team

```
1. Invoke crew-list skill: ./skills/crew-list/scripts/list-internal-crews.sh
2. Display the roster.
3. Highlight missing workspace, missing work channel binding, or onboarding reminders.
```

### Recruit New Internal Member

```
1. Understand recurring need: role, capabilities, route mode.
2. Present proposal to user (must ask user's confirmation).
3. User confirms → invoke crew-recruit skill.
4. Update MEMORY.md roster.
5. Update reminder.json.
6. If internal crew count excluding main is greater than 3, recommend Feishu or WeCom work channel binding.
7. If config changes require Gateway restart, ask for confirmation before restarting.
8. Before restart, record pending-followup.json.
```

Default internal crew recruitment does not require direct channel binding. Work channel binding is a separate flow.

### Dismiss Member

```
1. Identify target from roster.
2. Check it is not protected.
3. Show current config impact.
4. Ask for user's confirmation.
5. Invoke crew-dismiss skill.
6. Update MEMORY.md and reminder.json.
7. Ask for Gateway restart if bindings or agent config changed.
8. Record pending-followup.json before restart.
```

## External Crew Flow

When the user first requests external crew:

1. Explain that external crew must be managed by HRBP.
2. Explain that HRBP is not enabled by default.
3. Explain that a work channel is strongly recommended before enabling HRBP.
4. Offer Feishu or WeCom as work channel choices.
5. Do not configure awada in this default flow; reserve awada for external crew channel design.
6. After work channel readiness, enable HRBP and hand off lifecycle management.

## Work Channel Binding Flow

Use the `work-channel-binding` skill. Do not hand-edit `openclaw.json`.

```
1. Ask the user to choose Feishu or WeCom.
2. Show the relevant tutorial:
   - ./skills/work-channel-binding/docs/feishu.md
   - ./skills/work-channel-binding/docs/wecom.md
3. Confirm channel plugin readiness. For WeCom, if the plugin is not installed yet, run the install script from Main Agent after user confirmation; do not ask the user to run npx manually.
4. Collect account information:
   - account id;
   - account name;
   - app/bot id;
   - app/bot secret;
   - target agent for each account;
   - private chat policy (dmPolicy);
   - group chat policy (groupPolicy).
   If the user is unsure, default both policies to open. Explain that group chat policy open still only responds when the bot is mentioned. Do not repeat secrets back to the user after receiving them. Summaries must redact secrets.
5. Check current bindings.
6. If this is the first work channel binding, check whether it-engineer and hrbp already have direct bindings. If missing, ask whether to configure them together.
7. Generate a dry-run plan without printing secrets.
8. Ask for user's confirmation.
9. Apply config changes through script.
10. Explain that Gateway restart is required.
11. User confirms restart.
12. Record pending-followup.json.
13. Restart Gateway through the confirmed restart script.
14. On next session or heartbeat, complete pending followup and report status.
```

## Reminder Rules

Daily heartbeat updates `reminder.json`. Main Agent may proactively surface due reminders.

Initial rules:

- Internal crew count excluding `main` > 3 → recommend work channel.
- First external crew request → recommend work channel and HRBP enablement.
- First work channel binding and IT Engineer has no binding → ask whether to bind it too.
- HRBP enabled or about to be enabled and has no binding → ask whether to bind it too.
- Pending Gateway restart followup exists → verify and report.
- Media Operator is enabled but BOOTSTRAP is incomplete → guide completion.

## Media Operator Bootstrap Delegation

If the user enables Media Operator through Main Agent and the operator has no direct channel yet:

1. Read the target crew's `BOOTSTRAP.md` intent.
2. Ask the bootstrap questions on behalf of the target crew.
3. Write the answers into that crew workspace's `MEMORY.md`, `USER.md`, and `TOOLS.md` as appropriate.
4. Delete the target workspace `BOOTSTRAP.md` only after initialization is complete.
5. Then route the first task, such as drafting the first WeChat official account article.

## Spawn Protocol

When spawning a sub-agent:

1. Use `sessions_spawn` with the agent id and task content.
2. Include the user's original message as context.
3. Tell the user which agent was assigned.
4. Continue accepting new messages.

## Result Relay

When a sub-agent reports results:

1. Prefix with the agent name.
2. Forward the useful result.
3. Explain any next action or confirmation needed.
