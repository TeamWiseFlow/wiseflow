import { randomUUID } from "crypto";
import { mkdirSync } from "fs";
import { writeFile } from "fs/promises";
import { join } from "path";
import type { ClawdbotConfig, RuntimeEnv } from "openclaw/plugin-sdk/feishu";
import { DEFAULT_ACCOUNT_ID } from "openclaw/plugin-sdk/feishu";
import { resolveAwadaAccount } from "./accounts.js";
import { fetchAudioBuffer, transcribeAudio } from "./audio-transcribe.js";
import type { AudioObject, FileObject, ImageObject, InboundEvent } from "./redis-types.js";
import { createAwadaReplyDispatcher } from "./reply-dispatcher.js";
import { cacheOutboundTarget } from "./target-cache.js";
import { getAwadaRuntime } from "./runtime.js";
import { buildOutboundTarget, encodeAwadaTo, sendTextToAwada } from "./send.js";

/**
 * Extract text from a payload array. Returns the concatenated text of all text objects.
 */
function extractTextFromPayload(payload: InboundEvent["payload"]): string {
  return payload
    .filter((item) => item.type === "text")
    .map((item) => (item as { type: "text"; text: string }).text)
    .join("\n")
    .trim();
}

/**
 * Sanitize a peer ID for use in session keys (stored in DB).
 * Allows Unicode letters/numbers (Chinese names, etc.) while replacing
 * control characters and shell-unsafe chars with underscores.
 * Does NOT modify the original user_id_external — only call this for peer/session routing.
 */
function sanitizePeerId(id: string): string {
  if (!id || !id.trim()) {
    return "_anonymous_";
  }
  return id.replace(/[^\p{L}\p{N}_\-.@+:]/gu, "_");
}

/**
 * Guess a MIME type from a URL or file name.
 */
function guessMimeType(urlOrName: string): string {
  const lower = urlOrName.toLowerCase();
  if (/\.jpe?g$/.test(lower)) return "image/jpeg";
  if (lower.endsWith(".png")) return "image/png";
  if (lower.endsWith(".gif")) return "image/gif";
  if (lower.endsWith(".webp")) return "image/webp";
  if (lower.endsWith(".bmp")) return "image/bmp";
  if (lower.endsWith(".svg")) return "image/svg+xml";
  if (lower.endsWith(".pdf")) return "application/pdf";
  if (lower.endsWith(".txt")) return "text/plain";
  if (lower.endsWith(".md")) return "text/markdown";
  if (lower.endsWith(".json")) return "application/json";
  if (lower.endsWith(".csv")) return "text/csv";
  return "application/octet-stream";
}

/**
 * Guess image extension from base64 magic bytes.
 */
function guessImageExt(base64: string): string {
  if (base64.startsWith("/9j/")) return ".jpg";
  if (base64.startsWith("iVBOR")) return ".png";
  if (base64.startsWith("R0lGO")) return ".gif";
  if (base64.startsWith("UklGR")) return ".webp";
  return ".png";
}

/**
 * Resolve the openclaw-approved temp directory for media files.
 * Agent sandbox only allows paths under /tmp/openclaw/ (not bare /tmp/).
 */
const OPENCLAW_TMP_DIR = "/tmp/openclaw";
function ensureMediaTmpDir(): string {
  mkdirSync(OPENCLAW_TMP_DIR, { recursive: true, mode: 0o700 });
  return OPENCLAW_TMP_DIR;
}

/**
 * Download a URL to a temp file. Returns the local path.
 */
async function downloadToTemp(url: string, ext: string): Promise<string> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`fetch ${url}: ${res.status}`);
  const buffer = Buffer.from(await res.arrayBuffer());
  const filePath = join(ensureMediaTmpDir(), `awada-${randomUUID()}${ext}`);
  await writeFile(filePath, buffer);
  return filePath;
}

/**
 * Save a base64 string to a temp file. Returns the local path.
 */
async function saveBase64ToTemp(data: string, ext: string): Promise<string> {
  const buffer = Buffer.from(data, "base64");
  const filePath = join(ensureMediaTmpDir(), `awada-${randomUUID()}${ext}`);
  await writeFile(filePath, buffer);
  return filePath;
}

// ---- Audio failure reply ----
const AUDIO_FAIL_MESSAGE = "对不起，我暂时不方便听语音，您能打字给我吗？";

/**
 * Process image payload items: download/decode to local temp files.
 * Returns arrays of (path, mimeType) for successfully processed images.
 */
async function processImages(
  images: ImageObject[],
  log: (...args: unknown[]) => void,
): Promise<{ paths: string[]; types: string[] }> {
  const paths: string[] = [];
  const types: string[] = [];
  for (const img of images) {
    try {
      if (img.file_url) {
        const url = img.file_url;
        const ext = url.includes(".") ? `.${url.split(".").pop()!.split("?")[0]}` : ".png";
        const localPath = await downloadToTemp(url, ext);
        paths.push(localPath);
        types.push(guessMimeType(url));
      } else if (img.base64) {
        const ext = guessImageExt(img.base64);
        const localPath = await saveBase64ToTemp(img.base64, ext);
        paths.push(localPath);
        types.push(ext === ".jpg" ? "image/jpeg" : `image/${ext.slice(1)}`);
      }
    } catch (err) {
      log(`awada: failed to process image: ${String(err)}`);
    }
  }
  return { paths, types };
}

/**
 * Process file payload items: download to local temp files.
 */
async function processFiles(
  files: FileObject[],
  log: (...args: unknown[]) => void,
): Promise<{ paths: string[]; types: string[] }> {
  const paths: string[] = [];
  const types: string[] = [];
  for (const file of files) {
    try {
      if (file.file_url) {
        const name = file.file_name ?? file.file_url;
        const ext = name.includes(".") ? `.${name.split(".").pop()!.split("?")[0]}` : "";
        const localPath = await downloadToTemp(file.file_url, ext);
        paths.push(localPath);
        types.push(guessMimeType(name));
      }
    } catch (err) {
      log(`awada: failed to process file: ${String(err)}`);
    }
  }
  return { paths, types };
}

/**
 * Handle a single inbound awada event, dispatching to the OpenClaw agent.
 */
export async function handleAwadaMessage(params: {
  cfg: ClawdbotConfig;
  event: InboundEvent;
  runtime?: RuntimeEnv;
  accountId?: string;
}): Promise<void> {
  const { cfg, event, runtime, accountId = DEFAULT_ACCOUNT_ID } = params;
  const log = runtime?.log ?? console.log;
  const error = runtime?.error ?? console.error;

  const account = resolveAwadaAccount({ cfg, accountId });
  if (!account.enabled || !account.configured) {
    log(`awada[${accountId}]: account not enabled or configured, skipping`);
    return;
  }

  const { meta, payload, event_id, correlation_id, trace_id } = event;

  // ---- Classify payload items ----
  const textContent = extractTextFromPayload(payload);
  const images = payload.filter((item): item is ImageObject => item.type === "image");
  const files = payload.filter((item): item is FileObject => item.type === "file");
  const audios = payload.filter((item): item is AudioObject => item.type === "audio");

  // ---- Build reply target early (needed for audio failure reply) ----
  const target = buildOutboundTarget({
    lane: meta.lane,
    tenant_id: meta.tenant_id,
    channel_id: meta.channel_id,
    user_id_external: meta.user_id_external,
    platform: meta.platform,
    conversation_id: meta.conversation_id,
  });

  // Cache outbound target so handleAction can reach this peer later
  cacheOutboundTarget(meta.user_id_external, target);

  // ---- Handle audio: transcribe via SiliconFlow, then treat as text ----
  let audioTranscript = "";
  for (const audio of audios) {
    const audioUrl = audio.file_url;
    if (!audioUrl) continue;
    try {
      const buffer = await fetchAudioBuffer(audioUrl);
      const fileName = audioUrl.split("/").pop() ?? "audio.ogg";
      const result = await transcribeAudio(buffer, fileName);
      if (result.ok) {
        audioTranscript += (audioTranscript ? "\n" : "") + result.text;
      } else {
        error(`awada[${accountId}]: audio transcription failed: ${result.error}`);
        // Send polite decline and return — do not dispatch to agent
        await sendTextToAwada({
          redisUrl: account.redisUrl!,
          target,
          text: AUDIO_FAIL_MESSAGE,
          replyToEventId: event_id,
          correlationId: correlation_id,
          traceId: trace_id,
        });
        return;
      }
    } catch (err) {
      error(`awada[${accountId}]: audio fetch/transcribe error: ${String(err)}`);
      await sendTextToAwada({
        redisUrl: account.redisUrl!,
        target,
        text: AUDIO_FAIL_MESSAGE,
        replyToEventId: event_id,
        correlationId: correlation_id,
        traceId: trace_id,
      });
      return;
    }
  }

  // ---- Combine text sources ----
  const effectiveText = [textContent, audioTranscript].filter(Boolean).join("\n").trim();

  // Skip if no processable content at all
  if (!effectiveText && images.length === 0 && files.length === 0) {
    log(`awada[${accountId}]: no processable content for event ${event_id}, skipping`);
    return;
  }

  // ---- Process images and files for openclaw MediaPaths ----
  const mediaPaths: string[] = [];
  const mediaTypes: string[] = [];

  if (images.length > 0) {
    const imgResult = await processImages(images, log);
    mediaPaths.push(...imgResult.paths);
    mediaTypes.push(...imgResult.types);
  }
  if (files.length > 0) {
    const fileResult = await processFiles(files, log);
    mediaPaths.push(...fileResult.paths);
    mediaTypes.push(...fileResult.types);
  }

  // Use text or a media placeholder if text is empty but media is present
  const displayText = effectiveText || (mediaPaths.length > 0 ? "<media>" : "");

  log(
    `awada[${accountId}]: received from ${meta.user_id_external} in lane ${meta.lane}: ${displayText.slice(0, 80)}` +
      (mediaPaths.length > 0 ? ` (+${mediaPaths.length} media)` : ""),
  );

  const core = getAwadaRuntime();

  const awadaTo = encodeAwadaTo(target);
  const awadaFrom = `awada:${meta.user_id_external}`;

  // Resolve agent route
  const route = core.channel.routing.resolveAgentRoute({
    cfg,
    channel: "awada",
    accountId,
    peer: { kind: "direct", id: sanitizePeerId(meta.user_id_external) },
  });

  // Build agent envelope
  const envelopeOptions = core.channel.reply.resolveEnvelopeFormatOptions(cfg);
  const messageBody = displayText;
  const body = core.channel.reply.formatAgentEnvelope({
    channel: "Awada",
    from: awadaFrom,
    timestamp: new Date(event.timestamp * 1000),
    envelope: envelopeOptions,
    body: messageBody,
  });

  const ctxPayload = core.channel.reply.finalizeInboundContext({
    Body: body,
    BodyForAgent: messageBody,
    RawBody: displayText,
    CommandBody: displayText,
    From: awadaFrom,
    To: awadaTo,
    SessionKey: route.sessionKey,
    AccountId: route.accountId,
    ChatType: "direct",
    SenderId: meta.user_id_external,
    SenderName: meta.user_id_external,
    Provider: "awada" as const,
    Surface: "awada" as const,
    MessageSid: event_id,
    Timestamp: event.timestamp * 1000,
    OriginatingChannel: "awada" as const,
    OriginatingTo: awadaTo,
    // Expose customer identity to the agent via UntrustedContext.
    UntrustedContext: [
      `awada_customer_id: ${meta.platform}:${meta.channel_id}:${meta.user_id_external}:${meta.lane}`,
    ],
    // Media attachments — openclaw generates [media attached: ...] notes automatically
    ...(mediaPaths.length > 0
      ? { MediaPaths: mediaPaths, MediaTypes: mediaTypes }
      : {}),
  });

  const { dispatcher, markDispatchIdle } = createAwadaReplyDispatcher({
    cfg,
    agentId: route.agentId,
    runtime: runtime as RuntimeEnv,
    redisUrl: account.redisUrl!,
    target,
    inboundEventId: event_id,
    correlationId: correlation_id,
    traceId: trace_id,
    accountId,
  });

  try {
    log(`awada[${accountId}]: dispatching to agent (session=${route.sessionKey})`);
    await core.channel.reply.withReplyDispatcher({
      dispatcher,
      onSettled: () => markDispatchIdle(),
      run: () =>
        core.channel.reply.dispatchReplyFromConfig({
          ctx: ctxPayload,
          cfg,
          dispatcher,
        }),
    });
  } catch (err) {
    error(`awada[${accountId}]: dispatch failed: ${String(err)}`);
  }
}
