#!/usr/bin/env -S node --experimental-strip-types
/**
 * link_parser.ts — Parse Douyin / Bilibili / Kuaishou video URLs
 *
 * Ported from ContentRemixAgent/backend/services/link_parser.py (XHS removed).
 * Short-links are resolved by following HTTP redirects.
 */

export type Platform = "douyin" | "bilibili" | "kuaishou"

export interface ParsedLink {
  platform: Platform
  contentId: string
  originalUrl: string
  isShortLink: boolean
}

// Short-link domains
const SHORT_LINK_DOMAINS = new Set([
  "v.douyin.com",
  "b23.tv",
  "v.kuaishou.com",
])

// Domain → platform mapping
const DOMAIN_TO_PLATFORM: Record<string, Platform> = {
  "v.douyin.com": "douyin",
  "douyin.com": "douyin",
  "www.douyin.com": "douyin",
  "b23.tv": "bilibili",
  "bilibili.com": "bilibili",
  "www.bilibili.com": "bilibili",
  "v.kuaishou.com": "kuaishou",
  "kuaishou.com": "kuaishou",
  "www.kuaishou.com": "kuaishou",
}

// Platform content-id extraction patterns
const CONTENT_ID_PATTERNS: Record<Platform, RegExp[]> = {
  douyin: [
    /\/video\/(\d+)/,
    /\/note\/(\d+)/,
  ],
  bilibili: [
    /\/(BV[a-zA-Z0-9]+)/,
    /\/video\/(BV[a-zA-Z0-9]+)/,
    /\/video\/av(\d+)/,
  ],
  kuaishou: [
    /\/short-video\/([a-zA-Z0-9_-]+)/,
    /\/photo\/([a-zA-Z0-9_-]+)/,
  ],
}

async function expandShortLink(url: string): Promise<string> {
  try {
    const resp = await fetch(url, {
      method: "HEAD",
      redirect: "follow",
      signal: AbortSignal.timeout(10_000),
    })
    return resp.url
  } catch {
    // Try GET if HEAD fails
    try {
      const resp = await fetch(url, {
        method: "GET",
        redirect: "follow",
        signal: AbortSignal.timeout(10_000),
      })
      return resp.url
    } catch {
      return url
    }
  }
}

function extractContentId(platform: Platform, url: string): string | null {
  for (const pattern of CONTENT_ID_PATTERNS[platform]) {
    const match = url.match(pattern)
    if (match) return match[1]
  }
  return null
}

export async function parseLink(rawUrl: string): Promise<ParsedLink> {
  let url = rawUrl.trim()
  // Extract URL from mixed text (e.g. "https://v.douyin.com/xxx 复制此链接…")
  const urlMatch = url.match(/https?:\/\/[^\s]+/)
  if (urlMatch) url = urlMatch[0]

  let parsed: URL
  try {
    parsed = new URL(url)
  } catch {
    throw new Error(`无法解析 URL: ${url}`)
  }

  const hostname = parsed.hostname.replace(/^www\./, "")
  const isShortLink = SHORT_LINK_DOMAINS.has(parsed.hostname) || SHORT_LINK_DOMAINS.has(hostname)

  // Resolve short links
  let resolvedUrl = url
  if (isShortLink) {
    resolvedUrl = await expandShortLink(url)
    try {
      parsed = new URL(resolvedUrl)
    } catch {
      throw new Error(`短链展开失败: ${url}`)
    }
  }

  const resolvedHostname = parsed.hostname.replace(/^www\./, "")
  const platform = DOMAIN_TO_PLATFORM[parsed.hostname] ?? DOMAIN_TO_PLATFORM[resolvedHostname]
  if (!platform) {
    throw new Error(`不支持的平台域名: ${parsed.hostname}（支持：抖音、B站、快手）`)
  }

  const contentId = extractContentId(platform, resolvedUrl)
  if (!contentId) {
    throw new Error(`无法从 URL 提取内容 ID: ${resolvedUrl}`)
  }

  return { platform, contentId, originalUrl: url, isShortLink }
}
