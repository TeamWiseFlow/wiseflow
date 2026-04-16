#!/usr/bin/env -S node --experimental-strip-types
/**
 * transcriber.ts — ASR transcription via SiliconFlow API
 *
 * API reference provided by user:
 *   POST https://api.siliconflow.cn/v1/audio/transcriptions
 *   model via env: ASR_MODEL (default: FunAudioLLM/SenseVoiceSmall)
 */

import { readFileSync, existsSync } from "fs"
import { basename } from "path"

export interface TranscriptSegment {
  start: number
  end: number
  text: string
}

export interface TranscriptResult {
  text: string
  segments: TranscriptSegment[]
}

const ASR_URL = "https://api.siliconflow.cn/v1/audio/transcriptions"

export async function transcribeAudio(audioPath: string): Promise<TranscriptResult> {
  const apiKey = process.env.SILICONFLOW_API_KEY
  if (!apiKey) {
    throw new Error("环境变量 SILICONFLOW_API_KEY 未设置")
  }

  if (!existsSync(audioPath)) {
    throw new Error(`音频文件不存在: ${audioPath}`)
  }

  const model = process.env.ASR_MODEL ?? "FunAudioLLM/SenseVoiceSmall"
  const audioBuffer = readFileSync(audioPath)
  const fileName = basename(audioPath)

  const formData = new FormData()
  formData.append("file", new Blob([audioBuffer], { type: "audio/wav" }), fileName)
  formData.append("model", model)

  const resp = await fetch(ASR_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
    },
    body: formData,
    signal: AbortSignal.timeout(120_000),
  })

  if (!resp.ok) {
    const errText = await resp.text()
    throw new Error(`ASR API 失败 (${resp.status}): ${errText}`)
  }

  const data = await resp.json() as {
    text: string
    segments?: Array<{ start: number; end: number; text: string }>
  }

  return {
    text: data.text ?? "",
    segments: (data.segments ?? []).map(s => ({
      start: s.start,
      end: s.end,
      text: s.text,
    })),
  }
}
