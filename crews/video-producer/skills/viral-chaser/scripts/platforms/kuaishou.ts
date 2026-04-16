#!/usr/bin/env -S node --experimental-strip-types
/**
 * kuaishou.ts — Kuaishou (快手) API client
 *
 * Uses GraphQL API directly (no signing required).
 * GraphQL queries ported from MediaCrawlerPro-Downloader/DownloadServer/pkg/media_platform_api/kuaishou/
 */

import type { SessionData } from "../session.ts"

const KS_GRAPHQL = "https://www.kuaishou.com/graphql"
const KS_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

export interface VideoInfo {
  contentId: string
  title: string
  desc: string
  videoUrl: string
  coverUrl: string
  durationMs: number
  author: string
  stats: { viewCount: number; likeCount: number; commentCount: number }
}

// GraphQL query for video detail (from kuaishou/graphql/video_detail.graphql)
const VIDEO_DETAIL_QUERY = `
  query visionVideoDetail($photoId: String, $type: String, $page: String, $webPageArea: String) {
    visionVideoDetail(photoId: $photoId, type: $type, page: $page, webPageArea: $webPageArea) {
      status
      author {
        id
        name
        headerUrl
      }
      photo {
        id
        duration
        caption
        likeCount
        viewCount
        coverUrl
        photoUrl
        timestamp
        manifest {
          adaptationSet {
            representation {
              id
              url
              height
              width
              avgBitrate
              qualityType
              qualityLabel
            }
          }
        }
      }
      tags {
        type
        name
      }
    }
  }
`

// Probe query to check cookie validity
const PROBE_QUERY = `
  query visionProfileUserList($ftype: Int) {
    visionProfileUserList(ftype: $ftype) {
      result
    }
  }
`

async function ksPost(
  query: string,
  variables: Record<string, unknown>,
  operationName: string,
  session: SessionData,
): Promise<Record<string, any>> {
  const ua = session.user_agent || KS_UA
  const resp = await fetch(KS_GRAPHQL, {
    method: "POST",
    headers: {
      "Cookie": session.cookies ?? "",
      "User-Agent": ua,
      "Content-Type": "application/json;charset=UTF-8",
      "Origin": "https://www.kuaishou.com",
      "Referer": "https://www.kuaishou.com/",
      "Accept": "application/json, text/plain, */*",
    },
    body: JSON.stringify({ operationName, variables, query }),
    signal: AbortSignal.timeout(20_000),
  })

  if (!resp.ok) throw new Error(`快手 API ${resp.status}: ${resp.statusText}`)

  const data = await resp.json() as { data?: Record<string, any>; errors?: unknown[] }
  if (data.errors) throw new Error(`快手 GraphQL 错误: ${JSON.stringify(data.errors)}`)
  return data.data ?? {}
}

// Pick lowest quality video URL from manifest (to save bandwidth)
function pickVideoUrl(photo: Record<string, any>): string {
  // Try direct photoUrl first (usually no-watermark or medium quality)
  const directUrl: string = photo.photoUrl ?? ""

  const adaptationSets = photo.manifest?.adaptationSet ?? []
  if (!adaptationSets.length) return directUrl

  const allReps: Array<Record<string, any>> = adaptationSets.flatMap(
    (s: Record<string, any>) => s.representation ?? []
  )
  if (!allReps.length) return directUrl

  // Sort by avgBitrate ascending, pick lowest
  allReps.sort((a, b) => (a.avgBitrate ?? 0) - (b.avgBitrate ?? 0))
  return allReps[0].url ?? directUrl
}

export async function getKuaishouVideo(photoId: string, session: SessionData): Promise<VideoInfo> {
  const data = await ksPost(
    VIDEO_DETAIL_QUERY,
    { photoId, type: "0", page: "search", webPageArea: "topline" },
    "visionVideoDetail",
    session,
  )

  const detail = data.visionVideoDetail
  if (!detail || detail.status !== 1) {
    throw new Error(`快手视频获取失败 (status=${detail?.status})，可能 cookie 已失效`)
  }

  const photo = detail.photo ?? {}
  const author = detail.author ?? {}

  return {
    contentId: photoId,
    title: photo.caption ?? "",
    desc: photo.caption ?? "",
    videoUrl: pickVideoUrl(photo),
    coverUrl: photo.coverUrl ?? "",
    durationMs: photo.duration ?? 0,
    author: author.name ?? "",
    stats: {
      viewCount: photo.viewCount ?? 0,
      likeCount: photo.likeCount ?? 0,
      commentCount: 0,
    },
  }
}
