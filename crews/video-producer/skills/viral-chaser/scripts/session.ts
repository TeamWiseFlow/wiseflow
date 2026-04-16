#!/usr/bin/env -S node --experimental-strip-types
/**
 * session.ts — Read/write platform session files
 *
 * Session files stored at: ~/.openclaw/logins/{platform}.json
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "fs"
import { homedir } from "os"
import { join, dirname } from "path"

export type Platform = "douyin" | "bilibili" | "kuaishou"

export interface SessionData {
  platform: Platform
  cookies: string
  user_agent: string
  updated_at: string // ISO 8601
}

const SESSIONS_DIR = join(homedir(), ".openclaw", "logins")

function sessionPath(platform: Platform): string {
  return join(SESSIONS_DIR, `${platform}.json`)
}

export function readSession(platform: Platform): SessionData | null {
  const path = sessionPath(platform)
  if (!existsSync(path)) return null
  try {
    const raw = readFileSync(path, "utf-8")
    return JSON.parse(raw) as SessionData
  } catch {
    return null
  }
}

export function writeSession(data: SessionData): void {
  mkdirSync(SESSIONS_DIR, { recursive: true })
  writeFileSync(sessionPath(data.platform), JSON.stringify(data, null, 2), "utf-8")
}

/**
 * Read session or exit with code 2 (cookie invalid / not logged in).
 * The calling skill is expected to trigger login-manager on exit code 2.
 */
export function requireSession(platform: Platform): SessionData {
  const data = readSession(platform)
  if (!data || !data.cookies) {
    process.stderr.write(
      JSON.stringify({ ok: false, error: "SESSION_EXPIRED", platform }) + "\n"
    )
    process.exit(2)
  }
  return data
}
