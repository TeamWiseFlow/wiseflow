#!/usr/bin/env node
/**
 * send.mjs — Proactive awada message sender
 *
 * Usage:
 *   node scripts/send.mjs \
 *     --user-id-external "黄子奇ᐪᒻ" \
 *     --text "您好，昨天咱们聊过专业版的事，不知道今天方便看看吗？"
 *
 * platform 和 lane 从 ~/.openclaw/openclaw.json 的 channels.awada 读取。
 * channel_id 和 tenant_id 固定为 "0"。
 * Mirrors publishTextToAwada() from awada-extension/src/publisher.ts.
 * Exit 0 on success (prints stream message ID), exit 1 on error.
 */

import { readFileSync } from "node:fs";
import { randomUUID } from "node:crypto";
import { homedir } from "node:os";
import { join } from "node:path";
import Redis from "ioredis";

// ── Arg parsing ──────────────────────────────────────────────────────────────

function getArg(name) {
  const idx = process.argv.indexOf(name);
  if (idx === -1 || idx >= process.argv.length - 1) return null;
  return process.argv[idx + 1];
}

const userIdExternal = getArg("--user-id-external");
const text = getArg("--text");

if (!userIdExternal || !text) {
  console.error("Usage: node send.mjs --user-id-external <id> --text <message>");
  process.exit(1);
}

// ── Load openclaw config ─────────────────────────────────────────────────────

const configPath = join(homedir(), ".openclaw", "openclaw.json");
let cfg;
try {
  cfg = JSON.parse(readFileSync(configPath, "utf8"));
} catch (err) {
  console.error(`❌ Cannot read config: ${configPath}: ${err.message}`);
  process.exit(1);
}

const awadaCfg = cfg?.channels?.awada ?? {};
const redisUrl = awadaCfg.redisUrl;
const platform = awadaCfg.platform || "wechat";
const lane = awadaCfg.lane || "user";

if (!redisUrl) {
  console.error("❌ channels.awada.redisUrl not set in ~/.openclaw/openclaw.json");
  process.exit(1);
}

// ── Build OutboundEvent (mirrors awada-extension redis-types.ts) ─────────────

const event = {
  schema_version: 1,
  event_id: randomUUID(),
  reply_to_event_id: randomUUID(),
  type: "REPLY_MESSAGE",
  timestamp: Math.floor(Date.now() / 1000),
  correlation_id: randomUUID(),
  trace_id: randomUUID(),
  target: {
    platform,
    tenant_id: "0",
    lane,
    user_id_external: userIdExternal,
    channel_id: "0",
  },
  payload: [{ type: "text", text }],
};

// ── Publish to Redis outbound stream ─────────────────────────────────────────

const streamKey = `awada:events:outbound:${lane}`;
const redis = new Redis(redisUrl, { lazyConnect: false, enableReadyCheck: false });

try {
  const messageId = await redis.xadd(streamKey, "*", "data", JSON.stringify(event));
  if (!messageId) throw new Error("xadd returned null");
  console.log(messageId);
} catch (err) {
  console.error(`❌ Redis xadd failed: ${err.message}`);
  process.exit(1);
} finally {
  redis.disconnect();
}
