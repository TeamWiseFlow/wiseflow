#!/bin/bash
# agent-usage.sh - 查询 Agent 模型使用量和成本
#
# 用法:
#   bash ./skills/hrbp-usage/scripts/agent-usage.sh                    # 所有 Agent 累计
#   bash ./skills/hrbp-usage/scripts/agent-usage.sh --agent hrbp       # 指定 Agent
#   bash ./skills/hrbp-usage/scripts/agent-usage.sh --period daily     # 按日统计（默认 7 天）
#   bash ./skills/hrbp-usage/scripts/agent-usage.sh --period weekly    # 按周统计
#   bash ./skills/hrbp-usage/scripts/agent-usage.sh --period monthly   # 按月统计
#   bash ./skills/hrbp-usage/scripts/agent-usage.sh --days 30          # 指定天数
#   bash ./skills/hrbp-usage/scripts/agent-usage.sh --agent all --period daily --days 14
set -e

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
AGENTS_DIR="$OPENCLAW_HOME/agents"
CONFIG_PATH="$OPENCLAW_HOME/openclaw.json"

# 默认参数
AGENT_FILTER=""
PERIOD="cumulative"
DAYS=7

# 解析参数
while [ $# -gt 0 ]; do
  case "$1" in
    --agent) AGENT_FILTER="$2"; shift 2 ;;
    --period) PERIOD="$2"; shift 2 ;;
    --days) DAYS="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: $0 [--agent <id|all>] [--period <daily|weekly|monthly|cumulative>] [--days <N>]"
      echo ""
      echo "Options:"
      echo "  --agent <id>    Filter by agent ID (default: all)"
      echo "  --period <p>    Aggregation period: daily, weekly, monthly, cumulative (default: cumulative)"
      echo "  --days <N>      Number of days to look back (default: 7, ignored for cumulative)"
      echo ""
      echo "Examples:"
      echo "  $0                                    # All agents, cumulative"
      echo "  $0 --agent hrbp                       # HRBP only, cumulative"
      echo "  $0 --period daily --days 14           # All agents, daily for 14 days"
      echo "  $0 --agent developer --period monthly # Developer, monthly"
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

if [ ! -d "$AGENTS_DIR" ]; then
  echo "⚠️  No agent session data found at $AGENTS_DIR"
  echo "   Agents start recording usage after their first interaction."
  exit 0
fi

# 获取已注册的 agent 列表（用于显示名称）
AGENT_NAMES="{}"
if [ -f "$CONFIG_PATH" ]; then
  AGENT_NAMES=$(node -e "
    const c = JSON.parse(require('fs').readFileSync('$CONFIG_PATH','utf8'));
    const m = {};
    for (const a of (c.agents?.list || [])) { m[a.id] = a.name || a.id; }
    console.log(JSON.stringify(m));
  " 2>/dev/null || echo "{}")
fi

# 主查询逻辑
node -e "
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const agentsDir = '$AGENTS_DIR';
const agentFilter = '$AGENT_FILTER';
const period = '$PERIOD';
const lookbackDays = parseInt('$DAYS', 10);
const agentNames = $AGENT_NAMES;

const now = new Date();
const cutoffMs = period === 'cumulative' ? 0 : now.getTime() - lookbackDays * 86400000;

// 规范化 usage 字段
function normalizeUsage(raw) {
  if (!raw) return null;
  const input = raw.input ?? raw.inputTokens ?? raw.input_tokens ?? raw.promptTokens ?? raw.prompt_tokens ?? 0;
  const output = raw.output ?? raw.outputTokens ?? raw.output_tokens ?? raw.completionTokens ?? raw.completion_tokens ?? 0;
  const cacheRead = raw.cacheRead ?? raw.cache_read_input_tokens ?? 0;
  const cacheWrite = raw.cacheWrite ?? raw.cache_creation_input_tokens ?? 0;
  const total = raw.total ?? raw.totalTokens ?? raw.total_tokens ?? (input + output + cacheRead + cacheWrite);
  return { input, output, cacheRead, cacheWrite, total };
}

// 提取 cost
function extractCost(entry) {
  const u = entry.usage || entry.message?.usage;
  if (!u) return 0;
  if (u.cost && typeof u.cost === 'object') return u.cost.total || 0;
  if (typeof u.cost === 'number') return u.cost;
  if (entry.costTotal) return entry.costTotal;
  return 0;
}

// 提取 timestamp
function extractTimestamp(entry) {
  if (entry.timestamp) {
    const d = new Date(entry.timestamp);
    if (!isNaN(d.getTime())) return d;
  }
  if (entry.message?.timestamp) {
    const t = entry.message.timestamp;
    const d = new Date(typeof t === 'number' ? (t > 1e12 ? t : t * 1000) : t);
    if (!isNaN(d.getTime())) return d;
  }
  return null;
}

// 日期 key 生成
function dateKey(d, p) {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  switch (p) {
    case 'daily': return yyyy + '-' + mm + '-' + dd;
    case 'weekly': {
      const jan1 = new Date(yyyy, 0, 1);
      const week = Math.ceil(((d - jan1) / 86400000 + jan1.getDay() + 1) / 7);
      return yyyy + '-W' + String(week).padStart(2, '0');
    }
    case 'monthly': return yyyy + '-' + mm;
    default: return 'cumulative';
  }
}

// 空 bucket
function emptyBucket() {
  return {
    calls: 0,
    input: 0,
    output: 0,
    cacheRead: 0,
    cacheWrite: 0,
    totalTokens: 0,
    cost: 0,
    zeroTokenCalls: 0,
    missingUsageCalls: 0,
    errorCalls: 0
  };
}

function mergeBucket(dst, usage, cost, flags = {}) {
  dst.calls++;
  dst.input += usage.input;
  dst.output += usage.output;
  dst.cacheRead += usage.cacheRead;
  dst.cacheWrite += usage.cacheWrite;
  dst.totalTokens += usage.total;
  dst.cost += cost;
  if (flags.zeroToken) dst.zeroTokenCalls++;
  if (flags.missingUsage) dst.missingUsageCalls++;
  if (flags.errorCall) dst.errorCalls++;
}

async function scanAgentSessions(agentId) {
  const sessDir = path.join(agentsDir, agentId, 'sessions');
  if (!fs.existsSync(sessDir)) return [];

  const files = fs.readdirSync(sessDir).filter(f => f.endsWith('.jsonl'));
  const entries = [];

  for (const file of files) {
    const filePath = path.join(sessDir, file);
    const stat = fs.statSync(filePath);
    if (cutoffMs > 0 && stat.mtimeMs < cutoffMs) continue;

    const content = fs.readFileSync(filePath, 'utf8');
    for (const line of content.split('\\n')) {
      if (!line.trim()) continue;
      try {
        const entry = JSON.parse(line);
        if (!entry.message || !entry.message.role) continue;
        if (entry.message.role !== 'assistant') continue;

        const rawUsage = entry.usage || entry.message?.usage;
        const usage = normalizeUsage(rawUsage) || { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 };

        const ts = extractTimestamp(entry);
        if (!ts) continue;
        if (cutoffMs > 0 && ts.getTime() < cutoffMs) continue;

        const cost = extractCost(entry);
        const stopReason = entry.stopReason || entry.message?.stopReason;
        const hasError = Boolean(entry.errorMessage || entry.message?.errorMessage || stopReason === 'error');
        const zeroToken = usage.total === 0;
        const missingUsage = !rawUsage;
        entries.push({
          ts,
          usage,
          cost,
          model: entry.model || entry.message?.model || 'unknown',
          flags: { zeroToken, missingUsage, errorCall: hasError }
        });
      } catch (e) { /* skip malformed lines */ }
    }
  }
  return entries;
}

async function main() {
  // 确定要扫描的 agent 列表
  let agentIds;
  if (agentFilter && agentFilter !== 'all') {
    agentIds = [agentFilter];
  } else {
    agentIds = fs.readdirSync(agentsDir).filter(d => {
      return fs.statSync(path.join(agentsDir, d)).isDirectory();
    });
  }

  if (agentIds.length === 0) {
    console.log('⚠️  No agent session data found.');
    return;
  }

  // 按 agent 和时间段聚合
  const results = new Map(); // agentId -> Map<periodKey, bucket>
  const globalTotals = new Map(); // periodKey -> bucket

  for (const agentId of agentIds) {
    const entries = await scanAgentSessions(agentId);
    if (entries.length === 0) continue;

    const agentBuckets = new Map();
    for (const e of entries) {
      const key = dateKey(e.ts, period);
      if (!agentBuckets.has(key)) agentBuckets.set(key, emptyBucket());
      mergeBucket(agentBuckets.get(key), e.usage, e.cost, e.flags);

      if (!globalTotals.has(key)) globalTotals.set(key, emptyBucket());
      mergeBucket(globalTotals.get(key), e.usage, e.cost, e.flags);
    }
    results.set(agentId, agentBuckets);
  }

  if (results.size === 0) {
    console.log('⚠️  No usage data found' + (agentFilter ? ' for agent: ' + agentFilter : '') + '.');
    console.log('   Agents start recording usage after their first interaction.');
    return;
  }

  // 输出报告
  const sep = '─'.repeat(95);
  const periodLabel = period === 'cumulative' ? 'Cumulative' :
    period === 'daily' ? 'Daily (' + lookbackDays + ' days)' :
    period === 'weekly' ? 'Weekly' : 'Monthly';

  console.log('');
  console.log('📊 Agent Usage Report — ' + periodLabel);
  console.log(sep);

  // 按 agent 输出
  for (const [agentId, buckets] of [...results.entries()].sort()) {
    const name = agentNames[agentId] || agentId;
    console.log('');
    console.log('🤖 ' + name + ' (' + agentId + ')');

    const sortedKeys = [...buckets.keys()].sort();
    console.log('  ' + 'Period'.padEnd(14) + 'Calls'.padStart(8) + 'Input'.padStart(12) + 'Output'.padStart(12) + 'Cache R'.padStart(12) + 'Total Tk'.padStart(12) + 'Cost'.padStart(10));
    console.log('  ' + '─'.repeat(80));

    for (const key of sortedKeys) {
      const b = buckets.get(key);
      const costStr = b.cost > 0 ? '$' + b.cost.toFixed(4) : '—';
      console.log('  ' +
        key.padEnd(14) +
        String(b.calls).padStart(8) +
        b.input.toLocaleString().padStart(12) +
        b.output.toLocaleString().padStart(12) +
        b.cacheRead.toLocaleString().padStart(12) +
        b.totalTokens.toLocaleString().padStart(12) +
        costStr.padStart(10)
      );
    }

    // Agent 小计
    if (sortedKeys.length > 1) {
      const total = emptyBucket();
      for (const b of buckets.values()) {
        mergeBucket(
          total,
          { input: b.input, output: b.output, cacheRead: b.cacheRead, cacheWrite: b.cacheWrite, total: b.totalTokens },
          b.cost,
          { zeroToken: false, missingUsage: false, errorCall: false }
        );
      }
      total.calls = [...buckets.values()].reduce((s, b) => s + b.calls, 0);
      total.zeroTokenCalls = [...buckets.values()].reduce((s, b) => s + b.zeroTokenCalls, 0);
      total.missingUsageCalls = [...buckets.values()].reduce((s, b) => s + b.missingUsageCalls, 0);
      total.errorCalls = [...buckets.values()].reduce((s, b) => s + b.errorCalls, 0);
      const costStr = total.cost > 0 ? '$' + total.cost.toFixed(4) : '—';
      console.log('  ' + '─'.repeat(80));
      console.log('  ' +
        'SUBTOTAL'.padEnd(14) +
        String(total.calls).padStart(8) +
        total.input.toLocaleString().padStart(12) +
        total.output.toLocaleString().padStart(12) +
        total.cacheRead.toLocaleString().padStart(12) +
        total.totalTokens.toLocaleString().padStart(12) +
        costStr.padStart(10)
      );
      if (total.calls > 0 && total.totalTokens === 0) {
        console.log('  ℹ️  Active sessions detected, but provider returned zero usage metrics.');
      }
      if (total.errorCalls > 0) {
        console.log('  ⚠️  Error responses: ' + total.errorCalls);
      }
    } else {
      const only = buckets.get(sortedKeys[0]);
      if (only && only.calls > 0 && only.totalTokens === 0) {
        console.log('  ℹ️  Active sessions detected, but provider returned zero usage metrics.');
      }
      if (only && only.errorCalls > 0) {
        console.log('  ⚠️  Error responses: ' + only.errorCalls);
      }
    }
  }

  // 全局汇总（多 agent 时）
  if (results.size > 1) {
    console.log('');
    console.log(sep);
    console.log('📋 GRAND TOTAL');
    const grandTotal = emptyBucket();
    for (const b of globalTotals.values()) {
      grandTotal.calls += b.calls;
      grandTotal.input += b.input;
      grandTotal.output += b.output;
      grandTotal.cacheRead += b.cacheRead;
      grandTotal.cacheWrite += b.cacheWrite;
      grandTotal.totalTokens += b.totalTokens;
      grandTotal.cost += b.cost;
    }
    const costStr = grandTotal.cost > 0 ? '$' + grandTotal.cost.toFixed(4) : '—';
    console.log('  Calls: ' + grandTotal.calls);
    console.log('  Tokens: ' + grandTotal.totalTokens.toLocaleString() + ' (in: ' + grandTotal.input.toLocaleString() + ', out: ' + grandTotal.output.toLocaleString() + ', cache: ' + grandTotal.cacheRead.toLocaleString() + ')');
    console.log('  Cost: ' + costStr);
    if (grandTotal.calls > 0 && grandTotal.totalTokens === 0) {
      console.log('  Note: sessions are active, but provider returned zero usage metrics.');
    }
  }

  console.log('');
  console.log(sep);
  console.log('Data source: ' + agentsDir);
  console.log('');
}

main().catch(e => { console.error('Error:', e.message); process.exit(1); });
"
