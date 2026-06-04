#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DB="$ROOT/db/published_track.db"

mkdir -p "$ROOT/db"

sqlite3 "$DB" <<'SQL'

-- 微信公众号
CREATE TABLE IF NOT EXISTS pub_wx_mp (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content_type TEXT NOT NULL CHECK(content_type IN ('article','video','post')),
  source_folder TEXT NOT NULL UNIQUE,
  publish_url TEXT,
  publish_date TEXT NOT NULL,
  reads INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  favorites INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  top_comment TEXT,
  notes TEXT,
  created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime'))
);

-- 知乎
CREATE TABLE IF NOT EXISTS pub_zhihu (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content_type TEXT NOT NULL CHECK(content_type IN ('article','video','post')),
  source_folder TEXT NOT NULL UNIQUE,
  publish_url TEXT,
  publish_date TEXT NOT NULL,
  views INTEGER DEFAULT 0,
  upvotes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  favorites INTEGER DEFAULT 0,
  top_comment TEXT,
  notes TEXT,
  created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime'))
);

-- B站
CREATE TABLE IF NOT EXISTS pub_bilibili (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content_type TEXT NOT NULL CHECK(content_type IN ('article','video','post')),
  source_folder TEXT NOT NULL UNIQUE,
  publish_url TEXT,
  publish_date TEXT NOT NULL,
  plays INTEGER DEFAULT 0,
  danmaku INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  coins INTEGER DEFAULT 0,
  favorites INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  top_comment TEXT,
  notes TEXT,
  created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime'))
);

-- 抖音
CREATE TABLE IF NOT EXISTS pub_douyin (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content_type TEXT NOT NULL CHECK(content_type IN ('article','video','post')),
  source_folder TEXT NOT NULL UNIQUE,
  publish_url TEXT,
  publish_date TEXT NOT NULL,
  plays INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  favorites INTEGER DEFAULT 0,
  top_comment TEXT,
  notes TEXT,
  created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime'))
);

-- 快手
CREATE TABLE IF NOT EXISTS pub_kuaishou (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content_type TEXT NOT NULL CHECK(content_type IN ('article','video','post')),
  source_folder TEXT NOT NULL UNIQUE,
  publish_url TEXT,
  publish_date TEXT NOT NULL,
  plays INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  top_comment TEXT,
  notes TEXT,
  created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime'))
);

-- 小红书
CREATE TABLE IF NOT EXISTS pub_xhs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content_type TEXT NOT NULL CHECK(content_type IN ('article','video','post')),
  source_folder TEXT NOT NULL UNIQUE,
  publish_url TEXT,
  publish_date TEXT NOT NULL,
  views INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  favorites INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  top_comment TEXT,
  notes TEXT,
  created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime'))
);

-- 今日头条
CREATE TABLE IF NOT EXISTS pub_toutiao (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content_type TEXT NOT NULL CHECK(content_type IN ('article','video','post')),
  source_folder TEXT NOT NULL UNIQUE,
  publish_url TEXT,
  publish_date TEXT NOT NULL,
  impressions INTEGER DEFAULT 0,
  reads INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  top_comment TEXT,
  notes TEXT,
  created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime'))
);

-- 掘金
CREATE TABLE IF NOT EXISTS pub_juejin (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content_type TEXT NOT NULL CHECK(content_type IN ('article','video','post')),
  source_folder TEXT NOT NULL UNIQUE,
  publish_url TEXT,
  publish_date TEXT NOT NULL,
  views INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  favorites INTEGER DEFAULT 0,
  top_comment TEXT,
  notes TEXT,
  created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime'))
);

-- Twitter/X
CREATE TABLE IF NOT EXISTS pub_twitter (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content_type TEXT NOT NULL CHECK(content_type IN ('article','video','post')),
  source_folder TEXT NOT NULL UNIQUE,
  publish_url TEXT,
  publish_date TEXT NOT NULL,
  views INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  retweets INTEGER DEFAULT 0,
  replies INTEGER DEFAULT 0,
  bookmarks INTEGER DEFAULT 0,
  notes TEXT,
  created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime'))
);

-- Facebook
CREATE TABLE IF NOT EXISTS pub_facebook (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content_type TEXT NOT NULL CHECK(content_type IN ('article','video','post')),
  source_folder TEXT NOT NULL UNIQUE,
  publish_url TEXT,
  publish_date TEXT NOT NULL,
  reach INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  notes TEXT,
  created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime'))
);

-- Instagram
CREATE TABLE IF NOT EXISTS pub_instagram (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content_type TEXT NOT NULL CHECK(content_type IN ('article','video','post')),
  source_folder TEXT NOT NULL UNIQUE,
  publish_url TEXT,
  publish_date TEXT NOT NULL,
  reach INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  saves INTEGER DEFAULT 0,
  notes TEXT,
  created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime'))
);

-- TikTok
CREATE TABLE IF NOT EXISTS pub_tiktok (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content_type TEXT NOT NULL CHECK(content_type IN ('article','video','post')),
  source_folder TEXT NOT NULL UNIQUE,
  publish_url TEXT,
  publish_date TEXT NOT NULL,
  plays INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  favorites INTEGER DEFAULT 0,
  top_comment TEXT,
  notes TEXT,
  created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime'))
);

-- YouTube
CREATE TABLE IF NOT EXISTS pub_youtube (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content_type TEXT NOT NULL CHECK(content_type IN ('article','video','post')),
  source_folder TEXT NOT NULL UNIQUE,
  publish_url TEXT,
  publish_date TEXT NOT NULL,
  views INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  notes TEXT,
  created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime'))
);

-- Pinterest
CREATE TABLE IF NOT EXISTS pub_pinterest (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content_type TEXT NOT NULL CHECK(content_type IN ('article','video','post')),
  source_folder TEXT NOT NULL UNIQUE,
  publish_url TEXT,
  publish_date TEXT NOT NULL,
  impressions INTEGER DEFAULT 0,
  saves INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  notes TEXT,
  created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime'))
);

-- Threads
CREATE TABLE IF NOT EXISTS pub_threads (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content_type TEXT NOT NULL CHECK(content_type IN ('article','video','post')),
  source_folder TEXT NOT NULL UNIQUE,
  publish_url TEXT,
  publish_date TEXT NOT NULL,
  views INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  reposts INTEGER DEFAULT 0,
  replies INTEGER DEFAULT 0,
  notes TEXT,
  created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime'))
);

-- 企业微信朋友圈
CREATE TABLE IF NOT EXISTS pub_wxwork_moments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content_type TEXT NOT NULL CHECK(content_type IN ('article','video','post')),
  source_folder TEXT NOT NULL UNIQUE,
  publish_url TEXT,
  publish_date TEXT NOT NULL,
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  top_comment TEXT,
  notes TEXT,
  created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime'))
);

SQL

echo '{"ok":true,"message":"published_track.db initialized"}'
