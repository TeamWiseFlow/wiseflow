#!/usr/bin/env -S node --experimental-strip-types
/**
 * downloader.ts — HTTP streaming video download
 *
 * Ported from ContentRemixAgent/backend/services/video_downloader.py
 * Downloads the video URL returned by platform API clients.
 */

import { createWriteStream, mkdirSync } from "fs"
import { join } from "path"
import { pipeline } from "stream/promises"
import { Readable } from "stream"

export interface DownloadResult {
  filePath: string
  fileSize: number
}

const CHUNK_SIZE = 65536 // 64 KB
const MAX_RETRIES = 3
const RETRY_DELAY_MS = 2000

// Platform-specific headers for CDN anti-hotlinking
function getPlatformHeaders(videoUrl: string, userAgent: string): Record<string, string> {
  const headers: Record<string, string> = {
    "User-Agent": userAgent,
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Range": "bytes=0-",
  }

  if (videoUrl.includes("douyinvod") || videoUrl.includes("bytedance") || videoUrl.includes("toutiao")) {
    headers["Referer"] = "https://www.douyin.com/"
    headers["Origin"] = "https://www.douyin.com"
  } else if (videoUrl.includes("bilivideo") || videoUrl.includes("bili") || videoUrl.includes("hdslb")) {
    headers["Referer"] = "https://www.bilibili.com/"
    headers["Origin"] = "https://www.bilibili.com"
  } else if (videoUrl.includes("kuaishou") || videoUrl.includes("gifshow")) {
    headers["Referer"] = "https://www.kuaishou.com/"
    headers["Origin"] = "https://www.kuaishou.com"
  }

  return headers
}

async function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export async function downloadVideo(
  videoUrl: string,
  outputDir: string,
  filename: string,
  userAgent: string,
): Promise<DownloadResult> {
  mkdirSync(outputDir, { recursive: true })
  const filePath = join(outputDir, filename)
  const headers = getPlatformHeaders(videoUrl, userAgent)

  let lastError: Error | null = null

  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      const resp = await fetch(videoUrl, {
        headers,
        signal: AbortSignal.timeout(120_000),
      })

      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}: ${resp.statusText}`)
      }

      if (!resp.body) {
        throw new Error("响应体为空")
      }

      const fileStream = createWriteStream(filePath)
      const nodeReadable = Readable.fromWeb(resp.body as any)
      await pipeline(nodeReadable, fileStream)

      const { size } = await import("fs").then(m => m.promises.stat(filePath))
      return { filePath, fileSize: size }

    } catch (err) {
      lastError = err instanceof Error ? err : new Error(String(err))
      process.stderr.write(
        `[downloader] 下载失败 (attempt ${attempt}/${MAX_RETRIES}): ${lastError.message}\n`
      )
      if (attempt < MAX_RETRIES) {
        await sleep(RETRY_DELAY_MS)
      }
    }
  }

  throw new Error(`视频下载失败（重试 ${MAX_RETRIES} 次）: ${lastError?.message}`)
}
