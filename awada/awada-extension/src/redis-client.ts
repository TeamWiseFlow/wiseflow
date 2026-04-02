import Redis from "ioredis";

// Per-redisUrl connection pool (reuse connections for publisher)
const publisherPool = new Map<string, Redis>();

/**
 * Get or create a shared Redis client for publishing outbound events.
 * Separate from consumer connections (XREADGROUP BLOCK requires dedicated connections).
 */
export function getPublisherClient(redisUrl: string): Redis {
  const existing = publisherPool.get(redisUrl);
  if (existing && existing.status !== "end" && existing.status !== "close") {
    return existing;
  }
  const client = new Redis(redisUrl, {
    maxRetriesPerRequest: 3,
    enableOfflineQueue: true,
  });
  client.on("error", (err) => {
    console.error(`[awada] Redis publisher error (${redisUrl}):`, err.message);
  });
  publisherPool.set(redisUrl, client);
  return client;
}

/**
 * Create a dedicated Redis client for consuming (blocking XREADGROUP).
 * Callers are responsible for closing this connection.
 */
export function createConsumerClient(redisUrl: string): Redis {
  const client = new Redis(redisUrl, {
    maxRetriesPerRequest: null, // Infinite retries for long-running consumer
    enableOfflineQueue: true,
  });
  client.on("error", (err) => {
    console.error(`[awada] Redis consumer error:`, err.message);
  });
  return client;
}

export async function closeAllPublishers(): Promise<void> {
  const promises = Array.from(publisherPool.values()).map((c) => c.quit().catch(() => {}));
  await Promise.all(promises);
  publisherPool.clear();
}
