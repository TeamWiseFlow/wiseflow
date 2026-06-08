# Wiseflow Security Guide

## Overview

Wiseflow extends OpenClaw with multi-agent capabilities. This document describes the security model and best practices.

## Command Execution Tiers

Wiseflow uses a 4-tier permission system for shell command execution:

| Tier | Name | Policy | Use Case |
|------|------|--------|----------|
| T0 | read-only | `security: deny` | External crews (default) - no shell access |
| T1 | basic-shell | `security: allowlist` (read-only commands) | Low-risk internal crews |
| T2 | dev-tools | `security: allowlist` (dev tools + read) | Main Agent, HRBP, Selfmedia Operator |
| T3 | admin | `security: allowlist` + extended list | IT Engineer - system administration |

### Key Security Decisions

1. **Command substitution is blocked**: `$()` and backticks are not allowed in any tier to prevent arbitrary code execution bypass.

2. **IT Engineer uses allowlist, not full**: Unlike unrestricted `security: full`, IT Engineer uses an extended allowlist (`exec-approvals.json`) that covers necessary sysadmin commands while maintaining audit trail.

3. **User confirmation for unlisted commands**: IT Engineer has `ask: "on-miss"` which prompts the user before executing any command not in the allowlist.

## Removed Dangerous Defaults

The following configurations have been removed from the default template:

### 1. SSRF Private Network Access

**Removed:**
```json
"browser": {
  "ssrfPolicy": {
    "dangerouslyAllowPrivateNetwork": true
  }
}
```

**Reason:** Allowing browsers to access private networks (192.168.x.x, 10.x.x.x, etc.) enables potential attacks on internal services.

**If you need it:** Add it back manually and ensure your internal network is properly segmented.

### 2. Unrestricted Exec for IT Engineer

**Changed from:**
```json
"tools": {
  "exec": {
    "security": "full",
    "ask": "off"
  }
}
```

**Changed to:**
```json
"tools": {
  "exec": {
    "security": "allowlist",
    "ask": "on-miss"
  }
}
```

**Reason:** `security: full` with `ask: off` allows any command without user confirmation, which is dangerous if the agent is compromised via prompt injection.

## Patch Security Notes

### 001-relax-exec-allowlist-shell-syntax.patch

This patch relaxes some shell syntax restrictions to enable practical use cases:

**Allowed (for usability):**
- `&&` - command chaining
- `||` - conditional execution
- `;` - command separation
- `<`, `>` - file redirection

**Still Blocked (for security):**
- `$()` - command substitution
- `` ` `` - backtick command substitution
- `\n`, `\r` - newlines (multi-command injection)

The rationale: Chaining operators are useful for scripting and their behavior is predictable. Command substitution, however, allows executing arbitrary commands whose output becomes part of another command - this is a common injection vector.

## Best Practices

### For Users

1. **Review exec-approvals.json**: Customize the allowlist for your IT Engineer based on your actual needs.

2. **Monitor command logs**: Enable `command-logger` hook to audit all executed commands.

3. **Use per-channel isolation**: Keep `dmScope: "per-channel-peer"` to isolate sessions.

4. **Don't expose to untrusted networks**: Run wiseflow behind a firewall or VPN.

### For Developers

1. **New crews default to T0**: Any new crew template should start with `security: deny` unless explicitly needed.

2. **Document permission requirements**: If your addon needs elevated permissions, document why in the addon.json description.

3. **Avoid `security: full`**: Prefer extending the allowlist over granting unrestricted access.

## Reporting Security Issues

Please report security vulnerabilities to: zm.zhao # foxmail.com (replace # with @)

Do not open public issues for security vulnerabilities.
