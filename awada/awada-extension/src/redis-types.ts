/**
 * Minimal subset of the awada Redis protocol types needed by this extension.
 * Mirrors awada-server/src/infrastructure/redis/types.ts without importing from it.
 */

export type InboundEventType = "MESSAGE_NEW" | "PAYMENT_SUCCESS" | "BUTTON_CLICK";
export type OutboundEventType = "REPLY_MESSAGE" | "COMMAND_EXECUTE";

export interface TextObject {
  type: "text";
  text: string;
}

export interface ImageObject {
  type: "image";
  file_name: string;
  file_url?: string;
  file_id?: string;
}

export interface AudioObject {
  type: "audio";
  file_path?: string;
  file_url?: string;
  file_id?: string;
}

export interface FileObject {
  type: "file";
  file_name: string;
  file_url?: string;
  file_id?: string;
}

export type ContentObject = TextObject | ImageObject | AudioObject | FileObject;
export type Payload = ContentObject[];

export interface InboundMeta {
  platform: string;
  tenant_id: string;
  channel_id: string;
  lane: string;
  actor_type: string;
  user_id_external: string;
  session_id: string;
  session_seq: number;
  source_message_id: string;
  raw_ref?: string;
  conversation_id?: string;
}

export interface InboundEvent {
  schema_version: number;
  event_id: string;
  type: InboundEventType;
  timestamp: number;
  correlation_id: string;
  trace_id: string;
  meta: InboundMeta;
  payload: Payload;
}

export interface OutboundTarget {
  platform: string;
  tenant_id: string;
  lane: string;
  user_id_external: string;
  channel_id: string;
  reply_token?: string;
  conversation_id?: string;
  action_ask?: [number, string[]];
}

export interface OutboundEvent {
  schema_version: number;
  event_id: string;
  reply_to_event_id: string;
  type: OutboundEventType;
  timestamp: number;
  correlation_id: string;
  trace_id: string;
  target: OutboundTarget;
  payload: Payload;
}
