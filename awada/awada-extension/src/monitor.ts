import Redis from "ioredis";
import type { ClawdbotConfig, RuntimeEnv } from "openclaw/plugin-sdk/feishu";
import { resolveAwadaAccount } from "./accounts.js";
import { createConsumerClient } from "./redis-client.js";
import { handleAwadaMessage } from "./message-handler.js";
import type { InboundEvent } from "./redis-types.js";

const DEFAULT_CONSUMER_GROUP = "openclaw";
const DEFAULT_CONSUMER_NAME = "openclaw_bot";
const DEFAULT_BLOCK_MS = 5000;
const DEFAULT_BATCH_SIZE = 10;
const DEFAULT_MAX_RETRIES = 5;
const DEFAULT_MIN_IDLE_MS = 30_000;
const RECLAIM_INTERVAL_MS = 10_000;

function parseStreamMessage(fields: string[]): InboundEvent | null {
  for (let i = 0; i < fields.length - 1; i += 2) {
    if (fields[i] === "data") {
      try {
        return JSON.parse(fields[i + 1]) as InboundEvent;
      } catch {
        return null;
      }
    }
  }
  return null;
}

async function ensureConsumerGroup(
  redis: Redis,
  streamKey: string,
  group: string,
  log: (msg: string) => void,
): Promise<void> {
  try {
    await redis.xgroup("CREATE", streamKey, group, "0", "MKSTREAM");
    log(`awada: consumer group created: ${group} on ${streamKey}`);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    if (!msg.includes("BUSYGROUP")) {
      throw err;
    }
  }
}

async function reclaimPendingMessages(params: {
  redis: Redis;
  streamKey: string;
  group: string;
  consumer: string;
  minIdleMs: number;
  maxRetries: number;
  batchSize: number;
  dlqKey: string;
  log: (msg: string) => void;
  onMessage: (event: InboundEvent) => Promise<void>;
}): Promise<void> {
  const { redis, streamKey, group, consumer, minIdleMs, maxRetries, batchSize, dlqKey, log, onMessage } = params;
  try {
    const result = (await redis.call(
      "XAUTOCLAIM",
      streamKey,
      group,
      consumer,
      minIdleMs,
      "0-0",
      "COUNT",
      batchSize,
    )) as [string, [string, string[]][], string[]];

    if (!result?.[1]?.length) return;

    for (const [id, fields] of result[1]) {
      const event = parseStreamMessage(fields);
      if (!event) {
        await redis.xack(streamKey, group, id);
        continue;
      }

      // Check delivery count
      const pending = await redis.xpending(streamKey, group, id, id, 1) as [string, string, number, number][];
      const deliveryCount = pending?.[0]?.[3] ?? 0;

      if (deliveryCount >= maxRetries) {
        // Move to DLQ
        await redis.xadd(dlqKey, "*", "data", JSON.stringify({
          originalEvent: event,
          originalStreamId: id,
          lastError: `Exceeded max retries (${maxRetries})`,
          movedToDlqAt: Math.floor(Date.now() / 1000),
          deliveryCount,
        }));
        await redis.xack(streamKey, group, id);
        log(`awada: message ${id} moved to DLQ after ${deliveryCount} retries`);
        continue;
      }

      try {
        await onMessage(event);
        await redis.xack(streamKey, group, id);
      } catch (err) {
        log(`awada: reclaim processing failed for ${id}: ${String(err)}`);
      }
    }
  } catch (err) {
    log(`awada: reclaim loop error: ${String(err)}`);
  }
}

/**
 * Monitor a single awada lane (Redis stream) for inbound events.
 * Returns a Promise that resolves when aborted.
 */
async function monitorLane(params: {
  cfg: ClawdbotConfig;
  redisUrl: string;
  streamKey: string;
  dlqKey: string;
  group: string;
  consumer: string;
  blockMs: number;
  batchSize: number;
  maxRetries: number;
  minIdleMs: number;
  runtime?: RuntimeEnv;
  abortSignal?: AbortSignal;
  accountId: string;
}): Promise<void> {
  const { cfg, redisUrl, streamKey, dlqKey, group, consumer, blockMs, batchSize, maxRetries, minIdleMs, runtime, abortSignal, accountId } = params;
  const log = runtime?.log ?? console.log;
  const error = runtime?.error ?? console.error;

  const redis = createConsumerClient(redisUrl);

  await ensureConsumerGroup(redis, streamKey, group, log);

  log(`awada[${accountId}]: monitoring ${streamKey} (group=${group}, consumer=${consumer})`);

  let reclaimTimer: ReturnType<typeof setInterval> | null = null;

  const cleanup = async () => {
    if (reclaimTimer) {
      clearInterval(reclaimTimer);
      reclaimTimer = null;
    }
    try {
      await redis.quit();
    } catch {
      // ignore
    }
  };

  abortSignal?.addEventListener("abort", () => {
    void cleanup();
  });

  // Start reclaim loop
  reclaimTimer = setInterval(() => {
    void reclaimPendingMessages({
      redis,
      streamKey,
      dlqKey,
      group,
      consumer,
      minIdleMs,
      maxRetries,
      batchSize,
      log,
      onMessage: async (event) => {
        await handleAwadaMessage({ cfg, event, runtime, accountId });
      },
    });
  }, RECLAIM_INTERVAL_MS);

  // Main consume loop
  while (!abortSignal?.aborted) {
    try {
      const result = await redis.xreadgroup(
        "GROUP",
        group,
        consumer,
        "COUNT",
        batchSize,
        "BLOCK",
        blockMs,
        "STREAMS",
        streamKey,
        ">",
      );

      if (!result?.length) continue;

      const [, messages] = result[0] as [string, [string, string[]][]];
      for (const [id, fields] of messages) {
        const event = parseStreamMessage(fields);
        if (!event) {
          await redis.xack(streamKey, group, id);
          continue;
        }
        try {
          await handleAwadaMessage({ cfg, event, runtime, accountId });
          await redis.xack(streamKey, group, id);
        } catch (err) {
          error(`awada[${accountId}]: message processing failed ${id}: ${String(err)}`);
          // Leave in pending for reclaim
        }
      }
    } catch (err) {
      if (abortSignal?.aborted) break;
      error(`awada[${accountId}]: consume loop error: ${String(err)}`);
      // Brief pause to avoid tight error loop
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
  }

  await cleanup();
}

export type MonitorAwadaOpts = {
  config?: ClawdbotConfig;
  runtime?: RuntimeEnv;
  abortSignal?: AbortSignal;
  accountId?: string;
};

export async function monitorAwadaProvider(opts: MonitorAwadaOpts = {}): Promise<void> {
  const { config: cfg, runtime, abortSignal, accountId } = opts;
  if (!cfg) throw new Error("Config is required for awada monitor");

  const account = resolveAwadaAccount({ cfg, accountId });
  if (!account.enabled || !account.configured || !account.redisUrl) {
    throw new Error("Awada channel not enabled or configured (missing redisUrl)");
  }

  const { redisUrl, lane, consumerGroup, consumerName, config: awadaCfg } = account;
  const blockMs = awadaCfg?.blockTimeMs ?? DEFAULT_BLOCK_MS;
  const batchSize = awadaCfg?.batchSize ?? DEFAULT_BATCH_SIZE;
  const maxRetries = awadaCfg?.maxRetries ?? DEFAULT_MAX_RETRIES;

  const resolvedAccountId = account.accountId;

  await monitorLane({
    cfg,
    redisUrl,
    streamKey: `awada:events:inbound:${lane}`,
    dlqKey: "awada:events:inbound:dlq",
    group: consumerGroup ?? DEFAULT_CONSUMER_GROUP,
    consumer: consumerName ?? DEFAULT_CONSUMER_NAME,
    blockMs,
    batchSize,
    maxRetries,
    minIdleMs: DEFAULT_MIN_IDLE_MS,
    runtime,
    abortSignal,
    accountId: resolvedAccountId,
  });
}
