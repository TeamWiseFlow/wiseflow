/**
 * suppress-stale-reply — wiseflow official plugin
 *
 * 抑制被后续用户消息取代的 agent 回复：当用户连续发送 A/B/C 三条消息且间隔
 * 很短时，只把对最新消息（C）的回复发给用户；reply2A / reply2B 仍会写入
 * agent 历史（下一轮生成可见），但不会被真正发送。
 *
 * 依赖 wiseflow patch 001，后者把 originating inbound seq 透传到
 * `message_received` 与 `message_sending` hook 的 `metadata.originatingInboundSeq`。
 *
 * 不变量：
 *   - 内容以 "/" 开头的 reply（如 /kb、/cc）永不拦截——这类是 agent 生成的
 *     "指令型回复"，需要完整流过后续 message_sending hook 链，不能被 short-circuit。
 *   - 通过环境变量 `OPENCLAW_SUPPRESS_STALE_REPLY=0` 关闭整个插件。
 */

import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

type InboundMetadata = {
  originatingInboundSeq?: number;
  originatingFrom?: string;
} & Record<string, unknown>;

function peerKey(
  channelId: string | undefined,
  accountId: string | undefined,
  peer: string,
): string {
  return `${channelId ?? ""}|${accountId ?? ""}|${peer}`;
}

function coerceSeq(metadata: unknown): number | undefined {
  if (!metadata || typeof metadata !== "object") {
    return undefined;
  }
  const seq = (metadata as InboundMetadata).originatingInboundSeq;
  return typeof seq === "number" && Number.isFinite(seq) ? seq : undefined;
}

export default definePluginEntry({
  id: "suppress-stale-reply",
  name: "Suppress Stale Reply",
  description:
    "Drops agent replies superseded by newer inbound user messages (history preserved)",
  register(api) {
    if (process.env.OPENCLAW_SUPPRESS_STALE_REPLY === "0") {
      api.logger.info("suppress-stale-reply: disabled via OPENCLAW_SUPPRESS_STALE_REPLY=0");
      return;
    }

    const latestInboundSeqByPeer = new Map<string, number>();

    api.on("message_received", (event, ctx) => {
      const seq = coerceSeq(event.metadata);
      if (seq === undefined) {
        return;
      }
      const key = peerKey(ctx.channelId, ctx.accountId, event.from);
      const current = latestInboundSeqByPeer.get(key) ?? 0;
      if (seq > current) {
        latestInboundSeqByPeer.set(key, seq);
      }
    });

    api.on("message_sending", (event, ctx) => {
      if (event.content.trimStart().startsWith("/")) {
        return;
      }
      const turnSeq = coerceSeq(event.metadata);
      if (turnSeq === undefined) {
        return;
      }
      // Use originatingFrom (the inbound sender address) as the peer key so it
      // matches what was stored during message_received. The event.to field uses
      // the encoded delivery address which differs in format from event.from.
      const peer = (event.metadata as InboundMetadata).originatingFrom ?? event.to;
      const key = peerKey(ctx.channelId, ctx.accountId, peer);
      const latestSeq = latestInboundSeqByPeer.get(key);
      if (latestSeq !== undefined && turnSeq < latestSeq) {
        api.logger.debug(
          `suppress-stale-reply: cancel reply for turn=${turnSeq} (latest=${latestSeq}) peer=${key}`,
        );
        return { cancel: true };
      }
      return;
    });
  },
});
