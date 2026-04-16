#!/usr/bin/env -S node --experimental-strip-types
/**
 * bilibili.ts — Bilibili (B站) API client with WBI signing
 *
 * WBI signing ported from MediaCrawlerPro-SignSrv/logic/bilibili/help.py
 * API reference: MediaCrawlerPro-Downloader DownloadServer/pkg/media_platform_api/bilibili/
 */

import { createHash } from "crypto"
import type { SessionData } from "../session.ts"

const BILI_API = "https://api.bilibili.com"
const BILI_INDEX = "https://www.bilibili.com"
const BILI_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

export interface VideoInfo {
  contentId: string
  title: string
  desc: string
  videoUrl: string
  audioUrl: string          // separate audio stream (DASH), may be empty for durl
  coverUrl: string
  durationSeconds: number
  author: string
  bvid: string
  aid: number
  cid: number
  mediaFormat: "DASH" | "MP4"
  stats: { viewCount: number; likeCount: number; coinCount: number }
}

// ── WBI signing ────────────────────────────────────────────────────────────

const MAP_TABLE = [
  46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,
  33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,
  61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52,
]

function getMixinKey(imgKey: string, subKey: string): string {
  const raw = imgKey + subKey
  return MAP_TABLE.map(i => raw[i]).join("").slice(0, 32)
}

function wbiSign(
  params: Record<string, string | number>,
  imgKey: string,
  subKey: string,
): Record<string, string> {
  const wts = Math.floor(Date.now() / 1000)
  const allParams = { ...params, wts }
  const sorted = Object.fromEntries(
    Object.entries(allParams)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([k, v]) => [k, String(v).replace(/[!'()*]/g, "")])
  )
  const query = new URLSearchParams(sorted).toString()
  const salt = getMixinKey(imgKey, subKey)
  const w_rid = createHash("md5").update(query + salt).digest("hex")
  return { ...sorted, w_rid }
}

// Cache WBI keys for 10 minutes
let wbiKeyCache: { imgKey: string; subKey: string; ts: number } | null = null

async function getWbiKeys(session: SessionData): Promise<{ imgKey: string; subKey: string }> {
  if (wbiKeyCache && Date.now() - wbiKeyCache.ts < 10 * 60 * 1000) {
    return { imgKey: wbiKeyCache.imgKey, subKey: wbiKeyCache.subKey }
  }

  const resp = await fetch(`${BILI_API}/x/web-interface/nav`, {
    headers: biliHeaders(session),
    signal: AbortSignal.timeout(10_000),
  })

  if (!resp.ok) throw new Error(`获取 WBI 密钥失败: ${resp.status}`)
  const data = await resp.json() as Record<string, any>
  const wbiImg = data?.data?.wbi_img
  if (!wbiImg) throw new Error("WBI 密钥字段不存在")

  // Extract filename without extension from URL
  function keyFromUrl(url: string): string {
    return url.split("/").pop()?.replace(/\.[^.]+$/, "") ?? ""
  }

  const imgKey = keyFromUrl(wbiImg.img_url)
  const subKey = keyFromUrl(wbiImg.sub_url)
  wbiKeyCache = { imgKey, subKey, ts: Date.now() }
  return { imgKey, subKey }
}

// ── HTTP helpers ───────────────────────────────────────────────────────────

function biliHeaders(session: SessionData): Record<string, string> {
  return {
    "Cookie": session.cookies ?? "",
    "User-Agent": session.user_agent || BILI_UA,
    "Referer": BILI_INDEX,
    "Origin": BILI_INDEX,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
  }
}

async function biliGet(
  path: string,
  params: Record<string, string | number>,
  session: SessionData,
  sign = false,
): Promise<Record<string, any>> {
  let finalParams = params

  if (sign) {
    const { imgKey, subKey } = await getWbiKeys(session)
    finalParams = wbiSign(params, imgKey, subKey)
  }

  const url = `${BILI_API}${path}?${new URLSearchParams(
    Object.fromEntries(Object.entries(finalParams).map(([k, v]) => [k, String(v)]))
  ).toString()}`

  const resp = await fetch(url, {
    headers: biliHeaders(session),
    signal: AbortSignal.timeout(20_000),
  })

  if (!resp.ok) throw new Error(`Bilibili API ${resp.status}: ${resp.statusText}`)
  const data = await resp.json() as Record<string, any>

  if (data.code !== 0) {
    if (data.code === -101) throw new Error("B站 cookie 已失效，请重新登录")
    if (data.code === -404) return {}
    throw new Error(`Bilibili API 错误 ${data.code}: ${data.message}`)
  }

  return data.data ?? {}
}

// ── Video detail ───────────────────────────────────────────────────────────

export async function getBilibiliVideo(bvid: string, session: SessionData): Promise<VideoInfo> {
  // Step 1: Get video info (no WBI sign required)
  const videoInfo = await biliGet("/x/web-interface/wbi/view", { bvid }, session, false)

  if (!videoInfo.bvid) {
    throw new Error(`B站视频不存在或 cookie 已失效: ${bvid}`)
  }

  const aid: number = videoInfo.aid
  const cid: number = videoInfo.cid
  const title: string = videoInfo.title ?? ""
  const desc: string = videoInfo.desc ?? ""
  const coverUrl: string = videoInfo.pic ?? ""
  const durationSeconds: number = videoInfo.duration ?? 0
  const author: string = videoInfo.owner?.name ?? ""
  const stats = videoInfo.stat ?? {}

  // Step 2: Get play URL (WBI sign required), request 480P MP4 format
  const playData = await biliGet("/x/player/wbi/playurl", {
    avid: aid,
    cid,
    qn: 32,      // 480P (falls back to available quality)
    fnval: 1,    // Legacy MP4 (durl format, single file)
    fnver: 0,
    fourk: 0,
    platform: "pc",
  }, session, true)

  let videoUrl = ""
  let audioUrl = ""
  let mediaFormat: "DASH" | "MP4" = "MP4"

  const durl = playData.durl as Array<Record<string, any>> | undefined
  const dash = playData.dash as Record<string, any> | undefined

  if (durl && durl.length > 0) {
    // Legacy MP4 format
    videoUrl = durl[0].url ?? ""
    mediaFormat = "MP4"
  } else if (dash) {
    // DASH format — pick lowest quality video + best audio
    mediaFormat = "DASH"
    const videoStreams = (dash.video as Array<Record<string, any>> | undefined) ?? []
    const audioStreams = (dash.audio as Array<Record<string, any>> | undefined) ?? []

    if (videoStreams.length > 0) {
      videoStreams.sort((a, b) => (a.id ?? 0) - (b.id ?? 0))  // lowest quality first
      videoUrl = videoStreams[0].baseUrl ?? videoStreams[0].base_url ?? ""
    }
    if (audioStreams.length > 0) {
      audioStreams.sort((a, b) => (b.id ?? 0) - (a.id ?? 0))  // highest quality first
      audioUrl = audioStreams[0].baseUrl ?? audioStreams[0].base_url ?? ""
    }
  }

  return {
    contentId: bvid,
    title, desc, videoUrl, audioUrl, coverUrl,
    durationSeconds, author, bvid, aid, cid, mediaFormat,
    stats: {
      viewCount: stats.view ?? 0,
      likeCount: stats.like ?? 0,
      coinCount: stats.coin ?? 0,
    },
  }
}
