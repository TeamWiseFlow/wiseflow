#!/usr/bin/env node
/**
 * OpenClaw Managed Browser — Automated Test Suite
 *
 * Opens each test URL with the openclaw-managed browser, extracts AI snapshot
 * content via native `snapshot --format ai --mode detailed`, saves it to disk,
 * and analyses the snapshot text for
 * anti-bot / login-wall signals.
 *
 * Commands used:
 *   openclaw browser --browser-profile openclaw status
 *   openclaw browser --browser-profile openclaw start
 *   openclaw browser --browser-profile openclaw open <url>
 *   openclaw browser --browser-profile openclaw snapshot --format ai --mode detailed
 *
 * Usage:
 *   node browser_test/run-managed-tests.mjs [options]
 *
 * Options:
 *   --mode <smoke|full|social>   scope (default: smoke)
 *   --profile <name>             browser profile (default: openclaw)
 *   --stabilizeMs <ms>           wait after open before extracting HTML (default: 4000)
 *   --timeoutMs <ms>             CLI timeout per command (default: 60000)
 *   --outputDir <dir>            results root (default: browser_test/results)
 *
 * Modes:
 *   smoke  — 8 representative cases, no login prompts  (~5 min)
 *   full   — all README section-1/2/3 cases + pre-login interactive  (~25 min)
 *   social — full + social media  (multiple interactive login prompts)
 */

import { spawnSync }                from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join, dirname, resolve }   from 'node:path';
import { fileURLToPath }            from 'node:url';
import { createInterface }          from 'node:readline';

const __dirname    = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(__dirname, '..');
const OPENCLAW_DIR = join(PROJECT_ROOT, 'openclaw');

// ── Argument parsing ──────────────────────────────────────────────────────────
const argv    = process.argv.slice(2);
const getArg  = (k, d) => { const i = argv.indexOf(`--${k}`); return i >= 0 && argv[i+1] !== undefined ? argv[i+1] : d; };

const MODE         = getArg('mode',        'smoke');
const PROFILE      = getArg('profile',     'openclaw');
const STABILIZE_MS = parseInt(getArg('stabilizeMs', '4000'),  10);
const TIMEOUT_MS   = parseInt(getArg('timeoutMs',   '60000'), 10);
const OUTPUT_DIR   = getArg('outputDir',   join(PROJECT_ROOT, 'browser_test', 'results'));

// ── Run directory ─────────────────────────────────────────────────────────────
const RUN_ID  = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19) + '_managed';
const RUN_DIR = join(OUTPUT_DIR, RUN_ID);
const CASES   = join(RUN_DIR, 'cases');
const SNAPSHOTS = join(RUN_DIR, 'snapshots');

mkdirSync(CASES, { recursive: true });
mkdirSync(SNAPSHOTS,  { recursive: true });

// ── Environment for openclaw processes (uses default ~/.openclaw) ────────────
const OC_ENV = { ...process.env };

// ── openclaw CLI wrapper ──────────────────────────────────────────────────────
function oc(args, { ms = TIMEOUT_MS, safe = false } = {}) {
  const res = spawnSync('pnpm', ['openclaw', ...args], {
    cwd:       OPENCLAW_DIR,
    env:       OC_ENV,
    timeout:   ms,
    encoding:  'utf8',
    maxBuffer: 30 * 1024 * 1024,
  });
  const out = (res.stdout ?? '').trim();
  const err = (res.stderr ?? '').trim();
  if (!safe && res.status !== 0) {
    throw new Error(err || out || `openclaw exited ${res.status}`);
  }
  return { ok: res.status === 0, out, err };
}

/** Extract first valid JSON object from CLI output (skips logo / header lines). */
function extractJson(text) {
  if (!text) return null;
  const raw = text.trim();

  try { return JSON.parse(raw); } catch { /* continue */ }

  // Try parsing from first JSON opener to each possible closing index.
  const firstObj = raw.indexOf('{');
  const firstArr = raw.indexOf('[');
  const starts = [firstObj, firstArr].filter(i => i >= 0).sort((a, b) => a - b);
  for (const start of starts) {
    for (let end = raw.length; end > start; end--) {
      const ch = raw[end - 1];
      if (ch !== '}' && ch !== ']') continue;
      const candidate = raw.slice(start, end).trim();
      try { return JSON.parse(candidate); } catch { /* try shorter tail */ }
    }
  }

  // Last fallback: parse any single JSON line (for compact outputs).
  for (const line of raw.split('\n').reverse()) {
    const t = line.trim();
    if (!t) continue;
    if (t.startsWith('{') || t.startsWith('[') || t.startsWith('"')) {
      try { return JSON.parse(t); } catch { /* try next line */ }
    }
  }

  return null;
}

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

function waitForEnter(msg) {
  return new Promise(resolve => {
    const rl = createInterface({ input: process.stdin, output: process.stdout });
    rl.question(msg, () => { rl.close(); resolve(); });
  });
}

// ── Snapshot-based content analysis ───────────────────────────────────────────
// Pick a best-effort title from an AI snapshot line like:
// - heading "Some Title" [level=1] [ref=e1]
function extractTitle(snapshot) {
  const lines = String(snapshot ?? '').split('\n');
  for (const line of lines) {
    if (!line.includes('heading')) continue;
    const m = line.match(/"([^"]{1,200})"/);
    if (m && m[1]) return m[1].trim();
  }
  return '';
}

// Convert snapshot tree text to plain text for keyword matching.
function snapshotToText(snapshot) {
  return String(snapshot ?? '')
    .replace(/\[[^\]]+\]/g, ' ')
    .replace(/-\s+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

const BOT_PATTERNS = [
  /captcha/i,
  /are you (a )?human/i,
  /verify you(\'re| are)/i,
  /robot check/i,
  /security check/i,
  /ddos.{0,20}protection/i,
  /cloudflare ray id/i,
  /just a moment/i,
  /checking your browser/i,
  /access denied/i,
  /403 forbidden/i,
  /request blocked/i,
  /you('ve| have) been blocked/i,
  /请完成安全验证/,
  /人机验证/,
  /请证明您不是机器人/,
];

const LOGIN_PATTERNS = [
  /sign in to continue/i,
  /log in to continue/i,
  /subscribe to (read|continue|access)/i,
  /create (an? )?account/i,
  /登录后(才能|可以|方可)/,
  /请先登录/,
  /立即登录/,
  /(注册|登录)享受更多/,
];

function analyzeSnapshot(snapshot) {
  const title = extractTitle(snapshot);
  const text  = snapshotToText(snapshot);
  const lower = text.toLowerCase();

  const botBlocked = BOT_PATTERNS.some(re => re.test(lower));
  // Login wall: softer signal — only flag if bot not triggered
  const loginWall  = !botBlocked && LOGIN_PATTERNS.some(re => re.test(text));

  return {
    title,
    snapshotChars: String(snapshot ?? '').length,
    textChars:  text.length,
    rich:       text.length >= 300,  // meaningful snapshot content
    botBlocked,
    loginWall,
  };
}

// ── Test case definitions ─────────────────────────────────────────────────────
// Fields:
//   id         — unique id used in filenames
//   sec        — display section
//   url        — target URL
//   login      — true: login wall is expected/normal (not a failure)
//   loginTest  — pause for manual login then re-extract HTML (pre-login scenario)
//   socialOnly — only run in 'social' mode
const ALL_CASES = [

  // ── 企业官网 ──────────────────────────────────────────────────────────────
  { id: '1.01_komatsu',     sec: '企业官网', url: 'https://www.komatsu.com/en-us' },
  { id: '1.02_putzmeister', sec: '企业官网', url: 'https://www.putzmeister.com/web/european-union' },
  { id: '1.03_liebherr',    sec: '企业官网', url: 'https://www.liebherr.com/en-hk/group/start-page-5221008' },
  { id: '1.04_cat',         sec: '企业官网', url: 'https://www.cat.com/global-selector.html' },

  // ── 新闻媒体 ──────────────────────────────────────────────────────────────
  { id: '2.01_wsj',         sec: '新闻媒体', url: 'https://www.wsj.com/',          login: true },
  { id: '2.02_bloomberg',   sec: '新闻媒体', url: 'https://www.bloomberg.com' },

  // ── 政府网站（美国）──────────────────────────────────────────────────────
  { id: '3.01_justice',     sec: '政府网站', url: 'https://www.justice.gov/' },

  // ── 政府网站（中国）──────────────────────────────────────────────────────
  { id: '3.02_china_cer',   sec: '政府网站', url: 'http://www.china-cer.com.cn/policy_base/' },
  { id: '3.03_zjw_sh',      sec: '政府网站', url: 'https://zjw.sh.gov.cn/zwgk/index.html#tab2-a' },
  { id: '3.04_fgj_sh',      sec: '政府网站', url: 'https://fgj.sh.gov.cn/gfxwj/index.html' },
  { id: '3.05_rsj_sh',      sec: '政府网站', url: 'https://rsj.sh.gov.cn/tgwgfx_17726/index.html' },
  { id: '3.06_ybj_sh',      sec: '政府网站', url: 'https://ybj.sh.gov.cn/dybz3/index.html' },
  { id: '3.07_mohurd',      sec: '政府网站', url: 'https://www.mohurd.gov.cn/gongkai/fdzdgknr/zgzygwywj/index.html' },
  { id: '3.08_sh_nw39221',  sec: '政府网站', url: 'https://www.shanghai.gov.cn/nw39221/index.html' },
  { id: '3.09_sh_nw39220',  sec: '政府网站', url: 'https://www.shanghai.gov.cn/nw39220/index.html' },
  { id: '3.10_sh_nw11408',  sec: '政府网站', url: 'https://www.shanghai.gov.cn/nw11408/index.html' },
  { id: '3.11_sh_nw11407',  sec: '政府网站', url: 'https://www.shanghai.gov.cn/nw11407/index.html' },
  { id: '3.12_sh_nw2407',   sec: '政府网站', url: 'https://www.shanghai.gov.cn/nw2407/index.html' },
  { id: '3.13_sh_nw42850',  sec: '政府网站', url: 'https://www.shanghai.gov.cn/nw42850/index.html' },
  { id: '3.14_sh_nw42944',  sec: '政府网站', url: 'https://www.shanghai.gov.cn/nw42944/index.html' },
  { id: '3.15_gov_cn',      sec: '政府网站', url: 'https://www.gov.cn/zhengce/index.htm' },

  // ── 搜索引擎压力测试 ──────────────────────────────────────────────────────
  { id: '4.01_bing_wsj',    sec: '搜索引擎', url: 'https://www.bing.com/search?q=%E5%8D%8E%E5%B0%94%E8%A1%97%E6%97%A5%E6%8A%A5' },
  { id: '4.02_bing_cat',    sec: '搜索引擎', url: 'https://www.bing.com/search?q=caterpillar+heavy+equipment' },
  { id: '4.03_bing_policy', sec: '搜索引擎', url: 'https://www.bing.com/search?q=%E4%B8%8A%E6%B5%B7+%E5%BB%BA%E8%AE%BE%E5%B7%A5%E7%A8%8B+%E6%94%BF%E7%AD%96' },

  // ── 预登录功能测试（full+ 模式，交互）───────────────────────────────────
  { id: '5.01_wsj_article', sec: '预登录测试', login: true, loginTest: true,
    url: 'https://www.wsj.com/opinion/donald-trump-tariffs-ieepa-supreme-court-john-roberts-opinion-e2610d81' },

  // ── 社交媒体 — 主页（social 模式）────────────────────────────────────────
  { id: '6.01_x',           sec: '社交媒体', login: true,  socialOnly: true, url: 'https://x.com/valormental' },
  { id: '6.02_facebook',    sec: '社交媒体', login: true,  socialOnly: true, url: 'https://www.facebook.com/andrea.sow.31' },
  { id: '6.03_linkedin',    sec: '社交媒体', login: true,  socialOnly: true, url: 'https://www.linkedin.com/in/baoqiangliu/' },
  { id: '6.04_instagram',   sec: '社交媒体', login: true,  socialOnly: true, url: 'https://www.instagram.com/elisameliani/' },
  { id: '6.05_bilibili',    sec: '社交媒体', socialOnly: true, url: 'https://space.bilibili.com/3546603057056627' },
  { id: '6.06_weixin',      sec: '社交媒体', socialOnly: true, url: 'https://mp.weixin.qq.com/s/Duij3Z2vrImLuOzanqbgbA' },
  { id: '6.07_douyin',      sec: '社交媒体', login: true,  socialOnly: true, url: 'https://www.douyin.com/user/MS4wLjABAAAAXUpP_zAelVixv3zv_sWINae86Dt0FMPRZyuozH8MmhbBjvgoDg_xq3Lqnwlacelc' },
  { id: '6.08_kuaishou',    sec: '社交媒体', socialOnly: true, url: 'https://www.kuaishou.com/profile/3xvwve5yerjsvvg' },
  { id: '6.09_weibo',       sec: '社交媒体', socialOnly: true, url: 'https://m.weibo.cn/profile/2194035935' },
  { id: '6.10_xiaohongshu', sec: '社交媒体', socialOnly: true, url: 'https://www.xiaohongshu.com/user/profile/5f035b1c0000000001002389?xsec_token=ABti9cMRn3S9ARpTWxqiy-5oHI9_QXq50-5qjiSm8emMk=&xsec_source=pc_feed' },
  { id: '6.11_zhihu',       sec: '社交媒体', socialOnly: true, url: 'https://www.zhihu.com/people/lingzezhao' },
  { id: '6.12_discord',     sec: '社交媒体', login: true,  socialOnly: true, url: 'https://discord.com/servers/midjourney-662267976984297473' },

  // ── 社交媒体 — 搜索（social 模式）────────────────────────────────────────
  { id: '7.01_x_search',        sec: '社交媒体搜索', login: true, socialOnly: true, url: 'https://x.com/search?q=OpenClaw' },
  { id: '7.02_fb_search',       sec: '社交媒体搜索', login: true, socialOnly: true, url: 'https://www.facebook.com/search/posts/?q=OpenClaw' },
  { id: '7.03_linkedin_search', sec: '社交媒体搜索', login: true, socialOnly: true, url: 'https://www.linkedin.com/search/results/all/?keywords=openclaw' },
  { id: '7.04_instagram_tag',   sec: '社交媒体搜索', login: true, socialOnly: true, url: 'https://www.instagram.com/explore/tags/OpenClaw/' },
  { id: '7.05_bilibili_search', sec: '社交媒体搜索', socialOnly: true, url: 'https://search.bilibili.com/all?keyword=openclaw' },
  { id: '7.06_douyin_user',     sec: '社交媒体搜索', socialOnly: true, url: 'https://www.douyin.com/search/OpenClaw?type=user' },
  { id: '7.07_douyin_video',    sec: '社交媒体搜索', socialOnly: true, url: 'https://www.douyin.com/search/OpenClaw?type=video' },
  { id: '7.08_kuaishou_search', sec: '社交媒体搜索', socialOnly: true, url: 'https://www.kuaishou.com/search/video?searchKey=openclaw' },
  { id: '7.09_weibo_search',    sec: '社交媒体搜索', socialOnly: true, url: 'https://m.weibo.cn/search?containerid=100103type%3D1%26q%3Dopenclaw' },
  { id: '7.10_xhs_search',      sec: '社交媒体搜索', socialOnly: true, url: 'https://www.xiaohongshu.com/search_result?keyword=openclaw' },
  { id: '7.11_zhihu_content',   sec: '社交媒体搜索', socialOnly: true, url: 'https://www.zhihu.com/search?q=openclaw&type=content' },
  { id: '7.12_zhihu_people',    sec: '社交媒体搜索', socialOnly: true, url: 'https://www.zhihu.com/search?q=openclaw&type=people' },
  { id: '7.13_zhihu_video',     sec: '社交媒体搜索', socialOnly: true, url: 'https://www.zhihu.com/search?q=openclaw&type=zvideo' },
];

// Smoke: one or two cases from each key category
const SMOKE_IDS = new Set([
  '1.01_komatsu', '1.03_liebherr',
  '2.02_bloomberg',
  '3.01_justice', '3.02_china_cer',
  '4.01_bing_wsj', '4.02_bing_cat',
  '3.08_sh_nw39221',
]);

function buildRunList() {
  switch (MODE) {
    case 'smoke':  return ALL_CASES.filter(c => SMOKE_IDS.has(c.id));
    case 'full':   return ALL_CASES.filter(c => !c.socialOnly);
    case 'social': return ALL_CASES;
    default:
      console.error(`Unknown --mode "${MODE}". Use: smoke | full | social`);
      process.exit(1);
  }
}

const RUN_LIST = buildRunList();
const PARALLEL_SECTIONS = new Set(['企业官网', '政府网站', '搜索引擎']);
const PARALLEL_LIMIT = 6;

// ── Snapshot extraction helper ────────────────────────────────────────────────
function extractSnapshotFromOutput(out) {
  if (!out) return null;
  const raw = out.trim();
  if (!raw) return null;

  // Some builds return JSON; others print snapshot text directly.
  try {
    const parsed = JSON.parse(raw);
    if (typeof parsed === 'string') return extractSnapshotFromOutput(parsed);
    const candidates = [
      parsed?.snapshot,
      parsed?.value,
      parsed?.result,
      parsed?.data,
      parsed?.result?.snapshot,
      parsed?.result?.value,
      parsed?.result?.result?.value,
    ];
    for (const c of candidates) {
      if (typeof c === 'string') {
        const v = extractSnapshotFromOutput(c);
        if (v) return v;
      }
    }
  } catch {
    // ignore: non-JSON output
  }

  const lineJson = extractJson(raw);
  if (lineJson && typeof lineJson === 'object') {
    const nested = [
      lineJson.snapshot,
      lineJson.value,
      lineJson.result?.snapshot,
      lineJson.result?.value,
    ];
    for (const c of nested) {
      if (typeof c === 'string') {
        const v = extractSnapshotFromOutput(c);
        if (v) return v;
      }
    }
  }

  // Fallback: keep only the snapshot tree part and drop build/log noise.
  const lines = raw.split('\n');
  const start = lines.findIndex(l => /^\s*-\s+/.test(l));
  if (start >= 0) {
    return lines.slice(start).join('\n').trim();
  }

  return null;
}

async function fetchSnapshotAI({ ms = TIMEOUT_MS, targetId = null } = {}) {
  const args = ['browser', '--browser-profile', PROFILE, 'snapshot', '--format', 'ai', '--mode', 'detailed'];
  if (targetId) args.push('--target-id', targetId);
  const cliRes = oc(args, { ms, safe: true });
  if (!cliRes.ok) return null;
  return extractSnapshotFromOutput(cliRes.out);
}

function parseOpenedTargetId(text) {
  const raw = String(text ?? '');
  const fromJson = extractJson(raw);
  const maybeJsonId = fromJson?.id ?? fromJson?.targetId ?? fromJson?.result?.id;
  if (typeof maybeJsonId === 'string' && maybeJsonId.trim()) {
    return maybeJsonId.trim();
  }
  const m = raw.match(/\bid:\s*([A-F0-9]{16,})\b/i);
  return m?.[1] ?? null;
}

/**
 * Query the current tab list to obtain a best-effort active tab.
 */
function fetchCurrentTab() {
  const { out, ok } = oc(
    ['browser', '--browser-profile', PROFILE, 'tabs', '--json'],
    { ms: 8000, safe: true },
  );
  if (!ok || !out) return null;
  const json = extractJson(out);
  const tabs = Array.isArray(json?.tabs) ? json.tabs : [];
  if (!tabs.length) return null;

  const preferred = tabs.find(t => t?.url && t.url !== 'about:blank' && t?.type === 'page') ?? tabs[0];
  return {
    targetId: preferred?.targetId ?? null,
    wsUrl: preferred?.wsUrl ?? null,
    url: preferred?.url ?? null,
    title: preferred?.title ?? null,
  };
}

// ── Per-case test runner ──────────────────────────────────────────────────────
async function runCase(tc) {
  const { id, url, sec, login, loginTest } = tc;

  process.stdout.write(`\n[${''.padEnd(0)}${id}]`.padEnd(28) + ` ${url}\n`);

  const meta = {
    id, url, sec,
    status:          'pending',
    startedAt:       new Date().toISOString(),
    elapsedMs:       0,
    targetId:        null,
    title:           '',
    snapshotChars:   0,
    snapshotAfterChars:  0,
    loginExpected:   !!login,
    loginTestRan:    false,
    loginSuccess:    null,
    analysis:        {},
    error:           null,
  };

  const t0 = Date.now();
  try {
    // ── 1. open ───────────────────────────────────────────────────────────────
    const opened = oc(['browser', '--browser-profile', PROFILE, 'open', url], { ms: 30000, safe: true });
    meta.targetId = parseOpenedTargetId(opened.out);
    let currentTab = null;
    if (!meta.targetId) {
      // Fallback only when open output does not include id.
      currentTab = fetchCurrentTab();
      meta.targetId = currentTab?.targetId ?? null;
    }
    process.stdout.write(`     ↳ opened  targetId=${meta.targetId ?? '?'}\n`);

    // ── 2. wait for page to settle ────────────────────────────────────────────
    await sleep(STABILIZE_MS);
    oc(
      ['browser', '--browser-profile', PROFILE, 'wait',
       '--load', 'networkidle', '--timeout-ms', '10000'],
      { ms: 14000, safe: true },
    );

    // ── 3. extract AI snapshot via native browser tool ────────────────────────
    const snapshot = await fetchSnapshotAI({
      ms: 25000,
      targetId: meta.targetId,
    });
    if (!snapshot) {
      throw new Error('snapshot returned no content — page may not have loaded');
    }

    meta.snapshotChars = snapshot.length;
    writeFileSync(join(SNAPSHOTS, `${id}.txt`), snapshot, 'utf8');
    process.stdout.write(`     ↳ snapshot ${meta.snapshotChars.toLocaleString()} chars\n`);

    // ── 4. analyse snapshot ───────────────────────────────────────────────────
    const analysis  = analyzeSnapshot(snapshot);
    meta.analysis   = analysis;
    meta.title      = analysis.title;

    // ── 5. pre-login test (interactive) ──────────────────────────────────────
    if (loginTest && analysis.loginWall) {
      meta.loginTestRan = true;
      await waitForEnter(
        `\n  🔑 Login wall detected on ${url}\n` +
        `     Log in manually in the browser window, then press ENTER to re-extract HTML...\n  > `,
      );

      await sleep(STABILIZE_MS);
      currentTab = fetchCurrentTab() ?? currentTab;
      const snapshotAfter = await fetchSnapshotAI({
        ms: 25000,
        targetId: currentTab?.targetId ?? meta.targetId,
      });
      if (snapshotAfter) {
        meta.snapshotAfterChars = snapshotAfter.length;
        writeFileSync(join(SNAPSHOTS, `${id}_after.txt`), snapshotAfter, 'utf8');
        const ratio = snapshotAfter.length / Math.max(snapshot.length, 1);
        meta.loginSuccess = ratio > 1.2 && snapshotAfter.length > snapshot.length + 500;
        process.stdout.write(
          `     ↳ after-login snapshot ${meta.snapshotAfterChars.toLocaleString()} chars` +
          ` (${ratio.toFixed(2)}x)  login=${meta.loginSuccess ? '✅' : '❌'}\n`,
        );
      }
    }

    // ── 6. determine status ───────────────────────────────────────────────────
    if (analysis.botBlocked) {
      meta.status = 'blocked';
      process.stdout.write(`     🚫 BLOCKED — bot/captcha signal in HTML\n`);
    } else if (!analysis.rich) {
      meta.status = 'partial';
      process.stdout.write(`     ⚠️  PARTIAL — snapshot thin (text ${analysis.textChars} chars)\n`);
    } else {
      meta.status = 'success';
      const note = analysis.loginWall
        ? ` [login wall${login ? ', expected' : ''}]`
        : '';
      process.stdout.write(`     ✅ SUCCESS — title: "${meta.title}"${note}\n`);
    }

    // ── 7. close tab ──────────────────────────────────────────────────────────
    const tidToClose = meta.targetId ?? fetchCurrentTab()?.targetId ?? null;
    if (tidToClose) {
      oc(['browser', '--browser-profile', PROFILE, 'close', tidToClose],
         { ms: 5000, safe: true });
    }

  } catch (err) {
    meta.status = 'error';
    meta.error  = String(err?.message ?? err).slice(0, 600);
    process.stdout.write(`     ❌ ERROR — ${meta.error}\n`);
    // Best-effort close even on error
    const tidOnError = meta.targetId ?? fetchCurrentTab()?.targetId ?? null;
    if (tidOnError) {
      oc(['browser', '--browser-profile', PROFILE, 'close', tidOnError],
         { ms: 5000, safe: true });
    }
  }

  meta.elapsedMs = Date.now() - t0;
  writeFileSync(join(CASES, `${id}.json`), JSON.stringify(meta, null, 2), 'utf8');
  return meta;
}

// ── Report generator ──────────────────────────────────────────────────────────
function writeReport(results) {
  const ICON = { success: '✅', blocked: '🚫', partial: '⚠️', error: '❌' };

  const sections = new Map();
  for (const r of results) {
    if (!sections.has(r.sec)) sections.set(r.sec, []);
    sections.get(r.sec).push(r);
  }

  let md = `# Test Report — OpenClaw Managed Browser\n\n`;
  md += `**Run ID**: \`${RUN_ID}\`  \n`;
  md += `**Date**: ${new Date().toISOString()}  \n`;
  md += `**Mode**: ${MODE}  |  **Profile**: \`${PROFILE}\`  |  **Cases**: ${results.length}  \n\n`;

  md += `## Summary\n\n`;
  md += `| Section | Total | ✅ | 🚫 | ⚠️ | ❌ |\n`;
  md += `|---------|------:|----:|----:|----:|----:|\n`;

  let T=0, Ok=0, Bl=0, Pa=0, Er=0;
  for (const [sec, rows] of sections) {
    const ok = rows.filter(r => r.status==='success').length;
    const bl = rows.filter(r => r.status==='blocked').length;
    const pa = rows.filter(r => r.status==='partial').length;
    const er = rows.filter(r => r.status==='error'  ).length;
    md += `| ${sec} | ${rows.length} | ${ok} | ${bl} | ${pa} | ${er} |\n`;
    T+=rows.length; Ok+=ok; Bl+=bl; Pa+=pa; Er+=er;
  }
  md += `| **合计** | **${T}** | **${Ok}** | **${Bl}** | **${Pa}** | **${Er}** |\n\n`;

  md += `## Case Details\n\n`;
  for (const [sec, rows] of sections) {
    md += `### ${sec}\n\n`;
    for (const r of rows) {
      const icon = ICON[r.status] ?? '?';
      md += `#### ${icon} \`${r.id}\`\n\n`;
      md += `- **URL**: ${r.url}\n`;
      md += `- **Status**: \`${r.status}\`  (${(r.elapsedMs/1000).toFixed(1)} s)\n`;
      if (r.title)    md += `- **Title**: ${r.title}\n`;
      if (r.snapshotChars) {
        md += `- **Snapshot**: ${r.snapshotChars.toLocaleString()} chars\n`;
      }
      const { botBlocked, loginWall, rich, textChars } = r.analysis ?? {};
      if (botBlocked)       md += `- 🚫 **Bot / CAPTCHA signal detected**\n`;
      if (loginWall)        md += `- 🔑 **Login wall** (${r.loginExpected ? 'expected' : '⚠️ unexpected'})\n`;
      if (rich === false)   md += `- ⚠️ **Thin content** — extracted text ${textChars ?? 0} chars\n`;
      if (r.loginTestRan) {
        const badge = r.loginSuccess ? '✅ 内容明显增加，登录成功' : '❌ 内容未见明显变化';
        md += `- 🔑 **Pre-login test**: ${badge}`;
        if (r.snapshotAfterChars) md += ` (${r.snapshotChars.toLocaleString()} → ${r.snapshotAfterChars.toLocaleString()} chars)`;
        md += '\n';
      }
      if (r.error)          md += `- **Error**: \`${r.error}\`\n`;
      md += '\n';
    }
  }

  writeFileSync(join(RUN_DIR, 'report.md'), md, 'utf8');
  return { T, Ok, Bl, Pa, Er };
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  const LINE = '═'.repeat(66);
  console.log(`\n${LINE}`);
  console.log(`  OpenClaw Managed Browser — Automated Test Suite`);
  console.log(`  Mode: ${MODE.toUpperCase()}  |  Profile: ${PROFILE}  |  Cases: ${RUN_LIST.length}`);
  console.log(`  Run ID: ${RUN_ID}`);
  console.log(`  Output: ${RUN_DIR}`);
  console.log(`${LINE}`);

  // ── Phase 1: status ───────────────────────────────────────────────────────
  console.log('\n■ [1/4] Checking browser status...');
  const { out: statusOut } = oc(
    ['browser', '--browser-profile', PROFILE, 'status', '--json'],
    { safe: true },
  );
  const running = extractJson(statusOut)?.running === true;
  console.log(`       ${running ? '✓ running' : '✗ stopped'}`);

  // ── Phase 2: start if needed ──────────────────────────────────────────────
  if (!running) {
    console.log('\n■ [2/4] Starting browser...');
    oc(['browser', '--browser-profile', PROFILE, 'start'], { ms: 30000 });
    await sleep(3000);
    console.log('       ✓ browser started');
  } else {
    console.log('\n■ [2/4] Browser already running — skipping start.');
  }

  // ── Phase 3: test cases ───────────────────────────────────────────────────
  console.log(`\n■ [3/4] Running ${RUN_LIST.length} cases...\n`);
  const results = [];
  const parallelCases = RUN_LIST.filter(tc => PARALLEL_SECTIONS.has(tc.sec));
  const sequentialCases = RUN_LIST.filter(tc => !PARALLEL_SECTIONS.has(tc.sec));

  if (parallelCases.length) {
    for (let i = 0; i < parallelCases.length; i += PARALLEL_LIMIT) {
      const chunk = parallelCases.slice(i, i + PARALLEL_LIMIT);
      console.log(`\n   ↳ parallel batch (${chunk.length}) for 企业/政府/搜索...`);
      const chunkResults = await Promise.all(chunk.map(tc => runCase(tc)));
      results.push(...chunkResults);
      await sleep(800);
    }
  }

  for (const tc of sequentialCases) {
    results.push(await runCase(tc));
    await sleep(800);
  }

  // ── Phase 4: report ───────────────────────────────────────────────────────
  console.log('\n■ [4/4] Writing report...');
  const { T, Ok, Bl, Pa, Er } = writeReport(results);

  const DASH = '─'.repeat(66);
  console.log(`\n${DASH}`);
  console.log(`  ${Ok} success  /  ${Bl} blocked  /  ${Pa} partial  /  ${Er} error  (total ${T})`);
  console.log(`  report : ${join(RUN_DIR, 'report.md')}`);
  console.log(`  snapshots: ${SNAPSHOTS}`);
  console.log(`${DASH}\n`);
}

main().catch(err => {
  console.error('\nFatal error:', err?.message ?? err);
  process.exit(1);
});
