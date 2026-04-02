import { randomUUID } from "crypto";
import { getPublisherClient } from "./redis-client.js";
import type {
  ContentObject,
  FileObject,
  ImageObject,
  OutboundEvent,
  OutboundTarget,
} from "./redis-types.js";

const OUTBOUND_STREAM_PREFIX = "awada:events:outbound:";

export function encodeAwadaTo(target: OutboundTarget): string {
  return `awada:${Buffer.from(JSON.stringify(target)).toString("base64")}`;
}

export function decodeAwadaTo(to: string): OutboundTarget | null {
  if (!to.startsWith("awada:")) return null;
  try {
    return JSON.parse(Buffer.from(to.slice(6), "base64").toString("utf8")) as OutboundTarget;
  } catch {
    return null;
  }
}

export function buildOutboundTarget(meta: {
  lane: string;
  tenant_id: string;
  channel_id: string;
  user_id_external: string;
  platform: string;
  conversation_id?: string;
}): OutboundTarget {
  const target: OutboundTarget = {
    platform: meta.platform,
    tenant_id: meta.tenant_id,
    lane: meta.lane,
    user_id_external: meta.user_id_external,
    channel_id: meta.channel_id,
  };
  if (meta.conversation_id) {
    target.conversation_id = meta.conversation_id;
  }
  return target;
}

export async function publishOutboundEvent(
  redisUrl: string,
  event: OutboundEvent,
): Promise<string> {
  const client = getPublisherClient(redisUrl);
  const streamKey = `${OUTBOUND_STREAM_PREFIX}${event.target.lane}`;
  const messageId = await client.xadd(streamKey, "*", "data", JSON.stringify(event));
  if (!messageId) {
    throw new Error(`[awada] Failed to publish to ${streamKey}`);
  }
  return messageId;
}

export async function sendTextToAwada(params: {
  redisUrl: string;
  target: OutboundTarget;
  text: string;
  replyToEventId: string;
  correlationId: string;
  traceId: string;
}): Promise<string> {
  const { redisUrl, target, text, replyToEventId, correlationId, traceId } = params;
  const event: OutboundEvent = {
    schema_version: 1,
    event_id: randomUUID(),
    reply_to_event_id: replyToEventId || randomUUID(),
    type: "REPLY_MESSAGE",
    timestamp: Math.floor(Date.now() / 1000),
    correlation_id: correlationId || randomUUID(),
    trace_id: traceId || randomUUID(),
    target,
    payload: [{ type: "text", text }],
  };
  return publishOutboundEvent(redisUrl, event);
}

/**
 * Send a media item (file, image, or audio) to the awada outbound stream.
 */
export async function sendMediaToAwada(params: {
  redisUrl: string;
  target: OutboundTarget;
  media: ContentObject;
  replyToEventId: string;
  correlationId: string;
  traceId: string;
}): Promise<string> {
  const { redisUrl, target, media, replyToEventId, correlationId, traceId } = params;
  const event: OutboundEvent = {
    schema_version: 1,
    event_id: randomUUID(),
    reply_to_event_id: replyToEventId || randomUUID(),
    type: "REPLY_MESSAGE",
    timestamp: Math.floor(Date.now() / 1000),
    correlation_id: correlationId || randomUUID(),
    trace_id: traceId || randomUUID(),
    target,
    payload: [media],
  };
  return publishOutboundEvent(redisUrl, event);
}

const IMAGE_EXTENSIONS = new Set([
  ".jpg",
  ".jpeg",
  ".png",
  ".gif",
  ".webp",
  ".bmp",
  ".svg",
]);

/**
 * Build a ContentObject from a file_name (and optional file_id), for pre-stored
 * WeChat cloud files. Type is determined by extension: image extensions → ImageObject,
 * everything else → FileObject.
 */
export function buildMediaContentFromName(params: {
  file_name: string;
  file_id?: string;
}): ImageObject | FileObject {
  const { file_name, file_id } = params;
  const ext = file_name.slice(file_name.lastIndexOf(".")).toLowerCase();
  if (IMAGE_EXTENSIONS.has(ext)) {
    return {
      type: "image",
      file_name,
      ...(file_id ? { file_id } : {}),
    };
  }
  return {
    type: "file",
    file_name,
    ...(file_id ? { file_id } : {}),
  };
}

/**
 * Build a ContentObject from a URL.
 * file_name is extracted from the URL path; file_url is set to the URL.
 * Type is determined by extension: image extensions → ImageObject, everything else → FileObject.
 */
export function buildMediaContentFromUrl(url: string): ImageObject | FileObject {
  const pathname = new URL(url).pathname;
  const raw = pathname.split("/").pop() ?? "";
  const file_name = raw || "file";
  const ext = file_name.slice(file_name.lastIndexOf(".")).toLowerCase();
  if (IMAGE_EXTENSIONS.has(ext)) {
    return { type: "image", file_name, file_url: url };
  }
  return { type: "file", file_name, file_url: url };
}
