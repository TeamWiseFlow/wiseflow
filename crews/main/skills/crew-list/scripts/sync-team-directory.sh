#!/bin/bash
# sync-team-directory.sh - 生成对内 Crew 通讯录
# 写入 ~/.openclaw/crew_templates/TEAM_DIRECTORY.md（仅对内 crew，所有对内 crew 可读）
# 对外 Crew 记录在 ~/.openclaw/workspace-hrbp/EXTERNAL_CREW_REGISTRY.md（由 HRBP 维护）
set -e

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
CONFIG_PATH="${CONFIG_PATH:-$OPENCLAW_HOME/openclaw.json}"
CREW_TEMPLATES_DIR="$OPENCLAW_HOME/crew_templates"
TEAM_DIRECTORY_PATH="${TEAM_DIRECTORY_PATH:-$CREW_TEMPLATES_DIR/TEAM_DIRECTORY.md}"

# 确保 crew_templates 目录存在
mkdir -p "$CREW_TEMPLATES_DIR"

if [ ! -f "$CONFIG_PATH" ]; then
  echo "⚠️  Config not found: $CONFIG_PATH"
  exit 0
fi

CONFIG_PATH="$CONFIG_PATH" TEAM_DIRECTORY_PATH="$TEAM_DIRECTORY_PATH" node -e '
const fs = require("fs");
const path = require("path");

const configPath = process.env.CONFIG_PATH;
const teamDirectoryPath = process.env.TEAM_DIRECTORY_PATH;
const home = process.env.HOME || "";

let config;
try {
  config = JSON.parse(fs.readFileSync(configPath, "utf8"));
} catch (err) {
  console.error("❌ Failed to parse " + configPath + ": " + err.message);
  process.exit(1);
}

const agents = Array.isArray(config?.agents?.list) ? config.agents.list : [];
const bindings = Array.isArray(config?.bindings) ? config.bindings : [];
const main = agents.find((agent) => agent.id === "main");
const allowSet = new Set(
  Array.isArray(main?.subagents?.allowAgents) ? main.subagents.allowAgents : []
);

// 对内 Crew：main 本身 + 在 allowAgents 中的 crew
// 对外 Crew（不在 allowAgents 中）不包含在本文件中
const internalAgentIds = new Set(["main", "hrbp", "it-engineer"]);
// 扩展：任何在 allowAgents 中的也视为内部（Main Agent 可 spawn）
for (const id of allowSet) { internalAgentIds.add(id); }

function resolveWorkspace(rawWorkspace, agentId) {
  const fallback = home + "/.openclaw/workspace-" + agentId;
  const value = typeof rawWorkspace === "string" && rawWorkspace.trim()
    ? rawWorkspace.trim()
    : fallback;
  return value.replace(/^~(?=\/|$)/, home);
}

function parseRole(workspacePath) {
  const identityPath = path.join(workspacePath, "IDENTITY.md");
  if (!fs.existsSync(identityPath)) return "—";
  const content = fs.readFileSync(identityPath, "utf8");
  const roleMatch = content.match(/##\s*Role\s*\n([\s\S]*?)(?:\n##\s|\n#\s|$)/);
  if (!roleMatch) return "—";
  const summary = roleMatch[1]
    .split(/\r?\n/).map((line) => line.trim()).filter(Boolean).join(" ");
  if (!summary) return "—";
  return summary.replace(/\|/g, "/").slice(0, 160);
}

function routeMode(agentId, hasBinding, isSpawnable) {
  if (agentId === "main") return "entry";
  if (hasBinding && isSpawnable) return "both";
  if (hasBinding) return "binding";
  if (isSpawnable) return "spawn";
  return "none";
}

// 只处理对内 crew
const internalAgents = agents.filter(a => internalAgentIds.has(a.id));

const lines = [];
lines.push("# Internal Crew Directory");
lines.push("");
lines.push("_Generated from `" + configPath + "` at " + new Date().toISOString() + "._");
lines.push("_This file lists internal crews only. External crews are managed by HRBP._");
lines.push("");
lines.push("| ID | Name | Role | Type | Route | Bindings | Status |");
lines.push("|----|------|------|------|-------|----------|--------|");

for (const agent of internalAgents) {
  const id = agent.id || "unknown";
  const name = agent.name || id;
  const workspacePath = resolveWorkspace(agent.workspace, id);
  const agentBindings = bindings.filter((entry) => entry.agentId === id);
  const hasBinding = agentBindings.length > 0;
  const isSpawnable = id === "main" || allowSet.has(id);
  const route = routeMode(id, hasBinding, isSpawnable);
  const bindingsLabel = hasBinding
    ? agentBindings.map((entry) => `${entry?.match?.channel || "unknown"}:${entry?.match?.accountId || "*"}`).join(", ")
    : "—";
  const status = fs.existsSync(workspacePath) ? "active" : "registered";
  const role = parseRole(workspacePath);
  lines.push(
    `| ${id} | ${name.replace(/\|/g, "/")} | ${role} | internal | ${route} | ${bindingsLabel.replace(/\|/g, "/")} | ${status} |`
  );
}

lines.push("");
const content = lines.join("\n");

// Atomic write
const tmpPath = teamDirectoryPath + ".tmp." + process.pid;
try {
  fs.writeFileSync(tmpPath, content);
  fs.renameSync(tmpPath, teamDirectoryPath);
} catch (err) {
  try { fs.unlinkSync(tmpPath); } catch (_) {}
  throw err;
}
'

echo "✅ Internal crew directory synchronized: $TEAM_DIRECTORY_PATH"
