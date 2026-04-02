import Redis from "ioredis";
import type { AwadaProbeResult } from "./types.js";

const PROBE_TIMEOUT_MS = 5000;
const REDIS_PROTOCOLS = new Set(["redis:", "rediss:"]);

export function validateAwadaRedisUrl(redisUrl: string): string | null {
  const value = redisUrl.trim();
  if (!value) {
    return "missing redisUrl";
  }

  let parsed: URL;
  try {
    parsed = new URL(value);
  } catch {
    return "invalid redisUrl format";
  }

  if (!REDIS_PROTOCOLS.has(parsed.protocol)) {
    return "invalid redisUrl protocol (expected redis:// or rediss://)";
  }

  if (!parsed.hostname) {
    return "invalid redisUrl host";
  }

  if (parsed.hash) {
    return "invalid redisUrl: found unescaped # fragment; URL-encode password special characters (for example @, #, !, %)";
  }

  return null;
}

/**
 * Probe Redis connectivity for an awada account.
 * Returns ok=true if PING succeeds within timeout.
 */
export async function probeAwada(params: {
  redisUrl?: string;
  accountId?: string;
}): Promise<AwadaProbeResult> {
  const { redisUrl, accountId } = params;

  if (!redisUrl) {
    return { ok: false, error: "missing redisUrl" };
  }

  const normalizedRedisUrl = redisUrl.trim();
  const validationError = validateAwadaRedisUrl(normalizedRedisUrl);
  if (validationError) {
    return { ok: false, redisUrl: normalizedRedisUrl, error: validationError };
  }

  let client: Redis | null = null;
  const timeoutHandle = setTimeout(() => {
    client?.disconnect();
  }, PROBE_TIMEOUT_MS);

  try {
    client = new Redis(normalizedRedisUrl, {
      maxRetriesPerRequest: 1,
      enableOfflineQueue: false,
      connectTimeout: PROBE_TIMEOUT_MS,
      lazyConnect: true,
    });
    client.on("error", () => {
      // Probe already returns structured failure; suppress unhandled event noise from ioredis.
    });

    await client.connect();
    const pong = await client.ping();

    if (pong !== "PONG") {
      return {
        ok: false,
        redisUrl: normalizedRedisUrl,
        error: `unexpected PING response: ${pong}`,
      };
    }

    return { ok: true, redisUrl: normalizedRedisUrl };
  } catch (err) {
    return {
      ok: false,
      redisUrl: normalizedRedisUrl,
      error: err instanceof Error ? err.message : String(err),
    };
  } finally {
    clearTimeout(timeoutHandle);
    try {
      await client?.quit();
    } catch {
      // ignore
    }
  }
}
