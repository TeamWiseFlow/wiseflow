#!/usr/bin/env node
/**
 * fetch-rss.mjs — Fetch and parse an RSS/Atom feed
 *
 * Usage:
 *   node fetch-rss.mjs <url> [options]
 *
 * Options:
 *   --limit <n>        Max number of entries to return (default: 20)
 *   --skip <urls>      Comma-separated list of URLs to skip (deduplication)
 *   --content-only     Only return entries that have full content (skip link-only entries)
 *   --json             Output as JSON (default)
 *   --summary          Output a brief markdown summary instead of full JSON
 */

import { createRequire } from "node:module";
import { URL } from "node:url";

const require = createRequire(import.meta.url);

// Attempt to load rss-parser; guide user if missing
let Parser;
try {
  Parser = require("rss-parser");
} catch {
  console.error(
    "Error: 'rss-parser' package not found.\n" +
    "Install it with: npm install -g rss-parser\n" +
    "Or locally: npm install rss-parser"
  );
  process.exit(1);
}

// --- Argument parsing ---
const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "--help" || args[0] === "-h") {
  console.log(`Usage: node fetch-rss.mjs <url> [options]

Options:
  --limit <n>       Max entries to return (default: 20)
  --skip <urls>     Comma-separated article URLs to skip (deduplication)
  --content-only    Skip entries with no content (link-only items)
  --summary         Print a short markdown summary instead of JSON
  --help            Show this message
`);
  process.exit(0);
}

const feedUrl = args[0];
let limit = 20;
let skipUrls = new Set();
let contentOnly = false;
let summary = false;

for (let i = 1; i < args.length; i++) {
  if (args[i] === "--limit" && args[i + 1]) {
    limit = parseInt(args[++i], 10) || 20;
  } else if (args[i] === "--skip" && args[i + 1]) {
    skipUrls = new Set(args[++i].split(",").map((u) => u.trim()).filter(Boolean));
  } else if (args[i] === "--content-only") {
    contentOnly = true;
  } else if (args[i] === "--summary") {
    summary = true;
  }
}

// Validate URL
try {
  new URL(feedUrl);
} catch {
  console.error(`Error: "${feedUrl}" is not a valid URL.`);
  process.exit(1);
}

// --- Fetch and parse ---
const parser = new Parser({
  customFields: {
    item: [
      ["content:encoded", "contentEncoded"],
      ["dc:creator", "dcCreator"],
    ],
  },
  timeout: 15000,
  headers: { "User-Agent": "rss-reader-skill/1.0" },
});

let feed;
try {
  feed = await parser.parseURL(feedUrl);
} catch (err) {
  const msg = err.message || String(err);
  if (msg.includes("401") || msg.includes("403") || msg.includes("login")) {
    console.error(`Error: Feed requires authentication — ${feedUrl}`);
  } else if (msg.includes("404")) {
    console.error(`Error: Feed not found (404) — ${feedUrl}`);
  } else if (msg.includes("ENOTFOUND") || msg.includes("ETIMEDOUT")) {
    console.error(`Error: Network error — ${msg}`);
  } else {
    console.error(`Error: Failed to parse feed — ${msg}`);
  }
  process.exit(1);
}

// --- Build result ---
const feedMeta = {
  title: feed.title || "",
  description: feed.description || feed.subtitle || "",
  siteUrl: feed.link || "",
  feedUrl,
  lastUpdated: feed.lastBuildDate || feed.updated || "",
  totalItems: feed.items.length,
};

const entries = [];
for (const item of feed.items) {
  if (entries.length >= limit) break;

  const url = item.link || item.guid || "";
  if (skipUrls.has(url)) continue;

  // Content priority: content:encoded > content > summary > description
  const rawContent =
    item.contentEncoded ||
    item.content ||
    item.summary ||
    item.description ||
    "";

  if (contentOnly && rawContent.length < 50) continue;

  entries.push({
    title: item.title || "",
    url,
    content: rawContent,
    hasFullContent: rawContent.length > 200,
    author: item.dcCreator || item.creator || item.author || "",
    publishDate:
      item.isoDate ||
      item.pubDate ||
      item.published ||
      "",
  });
}

const result = { feed: feedMeta, entries, returned: entries.length };

if (summary) {
  // Brief markdown summary
  console.log(`## Feed: ${feedMeta.title}`);
  if (feedMeta.description) console.log(`> ${feedMeta.description}\n`);
  console.log(`**URL:** ${feedUrl}`);
  console.log(`**Items returned:** ${entries.length} / ${feedMeta.totalItems}\n`);
  for (const e of entries) {
    const date = e.publishDate ? ` (${e.publishDate.slice(0, 10)})` : "";
    const author = e.author ? ` — ${e.author}` : "";
    const full = e.hasFullContent ? " ✓full" : " ·summary";
    console.log(`- [${e.title || "(no title)"}](${e.url})${date}${author}${full}`);
  }
} else {
  console.log(JSON.stringify(result, null, 2));
}
