import { randomUUID } from "crypto";
import type { ClawdbotConfig } from "openclaw/plugin-sdk/feishu";
import { resolveAwadaAccount } from "./accounts.js";
import { buildOutboundTarget, publishOutboundEvent } from "./send.js";
import type { OutboundEvent } from "./redis-types.js";

/**
 * Publish a proactive (non-reply) text message to an awada platform.
 *
 * Use this when the agent initiates a message rather than responding to an inbound event.
 * The caller must supply the target user details explicitly.
 */
export async function publishTextToAwada(params: {
  cfg: ClawdbotConfig;
  accountId?: string;
  /** Target user external ID (e.g. wxid or worktool userId) */
  userId: string;
  /** Channel ID from the platform (e.g. weixin room or conversation id) */
  channelId: string;
  /** Tenant ID (use empty string if not applicable) */
  tenantId?: string;
  text: string;
}): Promise<string> {
  const { cfg, accountId, userId, channelId, tenantId = "", text } = params;

  const account = resolveAwadaAccount({ cfg, accountId });
  if (!account.redisUrl) {
    throw new Error("[awada] redisUrl not configured");
  }
  if (!account.platform) {
    throw new Error("[awada] platform not configured — required for proactive sends");
  }

  const target = buildOutboundTarget({
    platform: account.platform,
    lane: account.lane,
    user_id_external: userId,
    channel_id: channelId,
    tenant_id: tenantId,
  });

  const event: OutboundEvent = {
    schema_version: 1,
    event_id: randomUUID(),
    reply_to_event_id: randomUUID(),
    type: "REPLY_MESSAGE",
    timestamp: Math.floor(Date.now() / 1000),
    correlation_id: randomUUID(),
    trace_id: randomUUID(),
    target,
    payload: [{ type: "text", text }],
  };

  return publishOutboundEvent(account.redisUrl, event);
}
