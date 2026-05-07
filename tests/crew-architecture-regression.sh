#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP_HOME="$(mktemp -d)"
LOG_DIR="$(mktemp -d)"

cleanup() {
  local status=$?
  rm -rf "$TMP_HOME" "$LOG_DIR"
  if [ -n "${BOOT_HOME:-}" ]; then
    rm -rf "$BOOT_HOME"
  fi
  exit "$status"
}
trap cleanup EXIT

assert_true() {
  local condition="$1"
  local message="$2"
  if ! eval "$condition"; then
    echo "ASSERT FAILED: $message"
    exit 1
  fi
}

assert_command_fails() {
  local cmd="$1"
  local message="$2"
  if eval "$cmd"; then
    echo "ASSERT FAILED: $message"
    exit 1
  fi
}

OPENCLAW_HOME="$TMP_HOME/.openclaw"
CONFIG_PATH="$OPENCLAW_HOME/openclaw.json"
mkdir -p "$OPENCLAW_HOME"
cp "$PROJECT_ROOT/config-templates/openclaw.json" "$CONFIG_PATH"

echo "[TEST] installer bootstrap should seed missing built-in workspaces only"
BOOT_HOME="$(mktemp -d)"
BOOT_OPENCLAW_HOME="$BOOT_HOME/.openclaw"
mkdir -p "$BOOT_OPENCLAW_HOME/workspace-main"
cat > "$BOOT_OPENCLAW_HOME/workspace-main/SOUL.md" <<'EOF'
# User customized Main
crew-type: internal
EOF
# shellcheck source=../scripts/lib/crew-workspaces.sh
if [ ! -f "$PROJECT_ROOT/scripts/lib/crew-workspaces.sh" ]; then
  echo "ASSERT FAILED: scripts/lib/crew-workspaces.sh is missing"
  exit 1
fi
source "$PROJECT_ROOT/scripts/lib/crew-workspaces.sh"
seed_builtin_crew_workspaces "$PROJECT_ROOT/crews" "$BOOT_OPENCLAW_HOME" "main hrbp it-engineer" >"$LOG_DIR/bootstrap.log" 2>&1
assert_true "grep -q 'User customized Main' '$BOOT_OPENCLAW_HOME/workspace-main/SOUL.md'" "existing workspace-main was overwritten"
for id in hrbp it-engineer; do
  assert_true "[ -f '$BOOT_OPENCLAW_HOME/workspace-$id/openclaw_setting_sample.json' ]" "workspace-$id was not seeded as a full template copy"
  assert_true "[ -f '$BOOT_OPENCLAW_HOME/workspace-$id/SOUL.md' ]" "workspace-$id missing SOUL.md after bootstrap"
done
install_seed_line="$(grep -n 'seed_builtin_crew_workspaces' "$PROJECT_ROOT/scripts/install.sh" | head -1 | cut -d: -f1)"
install_apply_line="$(grep -n 'scripts/apply-addons.sh' "$PROJECT_ROOT/scripts/install.sh" | tail -1 | cut -d: -f1)"
assert_true "[ '$install_seed_line' -lt '$install_apply_line' ]" "install.sh must seed built-in workspaces before apply-addons"

echo "[TEST] setup-crew baseline"
HOME="$TMP_HOME" "$PROJECT_ROOT/scripts/setup-crew.sh" >"$LOG_DIR/setup.log" 2>&1

echo "[TEST] built-in workspaces should be full template copies"
for id in main hrbp it-engineer; do
  assert_true "[ -f '$OPENCLAW_HOME/workspace-$id/openclaw_setting_sample.json' ]" "workspace-$id missing openclaw_setting_sample.json"
done

echo "[TEST] addon crew templates should sync directly to runtime template directories"
assert_true "[ -d '$OPENCLAW_HOME/crew_templates/business-developer' ]" "business-developer internal addon template missing from crew_templates"
assert_true "[ -d '$OPENCLAW_HOME/crew_templates/designer' ]" "designer internal addon template missing from crew_templates"
assert_true "[ -d '$OPENCLAW_HOME/crew_templates/selfmedia-operator' ]" "selfmedia-operator internal addon template missing from crew_templates"
assert_true "[ -d '$OPENCLAW_HOME/hrbp_templates/sales-cs' ]" "sales-cs external addon template missing from hrbp_templates"
assert_true "grep -qi '^crew-type:[[:space:]]*internal' '$OPENCLAW_HOME/crew_templates/business-developer/SOUL.md'" "internal addon runtime template missing crew-type"
assert_true "grep -qi '^crew-type:[[:space:]]*external' '$OPENCLAW_HOME/hrbp_templates/sales-cs/SOUL.md'" "external addon runtime template missing crew-type"

echo "[TEST] apply-addons must not write addon crew templates into repo crews/"
if grep -q 'template_dest="\$CREWS_DIR/\$template_id"' "$PROJECT_ROOT/scripts/apply-addons.sh"; then
  echo "ASSERT FAILED: apply-addons still stages addon crew templates in repo crews/"
  exit 1
fi

echo "[TEST] default agents should only include built-in internal crews"
HOME="$TMP_HOME" node -e '
const fs = require("fs");
const cfg = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
const ids = (cfg.agents?.list || []).map((a) => a.id).sort();
const expected = ["hrbp", "it-engineer", "main"];
if (JSON.stringify(ids) !== JSON.stringify(expected)) {
  console.error("expected built-in internal agents only:", expected, "got:", ids);
  process.exit(1);
}
' "$CONFIG_PATH"

echo "[TEST] baseline config should enforce dmScope and internal exec tiers"
HOME="$TMP_HOME" node -e '
const fs = require("fs");
const cfg = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
if (cfg?.session?.dmScope !== "per-channel-peer") {
  console.error("expected session.dmScope=per-channel-peer, got:", cfg?.session?.dmScope);
  process.exit(1);
}
const byId = new Map((cfg.agents?.list || []).map((a) => [a.id, a]));
if (byId.get("hrbp")?.tools?.exec?.security !== "allowlist") {
  console.error("expected hrbp tools.exec.security=allowlist");
  process.exit(1);
}
if (byId.get("it-engineer")?.tools?.exec?.security !== "full") {
  console.error("expected it-engineer tools.exec.security=full");
  process.exit(1);
}
for (const id of ["main", "hrbp", "it-engineer"]) {
  const skills = byId.get(id)?.skills || [];
  if (skills.includes("alipay-mcp-config")) {
    console.error("global project skill should not be auto-inherited:", id);
    process.exit(1);
  }
}
' "$CONFIG_PATH"

echo "[TEST] external recruit must require DECLARED_SKILLS"
mkdir -p "$OPENCLAW_HOME/workspace-ext-bad"
cat > "$OPENCLAW_HOME/workspace-ext-bad/SOUL.md" <<'EOF'
# Ext Bad
crew-type: external
command-tier: T0
EOF
assert_command_fails \
  "HOME='$TMP_HOME' bash '$PROJECT_ROOT/crews/hrbp/skills/hrbp-recruit/scripts/add-agent.sh' ext-bad --crew-type external >'$LOG_DIR/ext-bad.log' 2>&1" \
  "external recruit unexpectedly succeeded without DECLARED_SKILLS"

echo "[TEST] external crew should default to T0 deny when no ALLOWED_COMMANDS"
mkdir -p "$OPENCLAW_HOME/workspace-ext-default"
cat > "$OPENCLAW_HOME/workspace-ext-default/SOUL.md" <<'EOF'
# Ext Default
crew-type: external
command-tier: T0
EOF
cat > "$OPENCLAW_HOME/workspace-ext-default/DECLARED_SKILLS" <<'EOF'
# keep empty for this test
EOF
HOME="$TMP_HOME" bash "$PROJECT_ROOT/crews/hrbp/skills/hrbp-recruit/scripts/add-agent.sh" ext-default --crew-type external --note "test-external-default" >"$LOG_DIR/ext-default-add.log" 2>&1
HOME="$TMP_HOME" "$PROJECT_ROOT/scripts/setup-crew.sh" >"$LOG_DIR/setup-after-ext-default.log" 2>&1
HOME="$TMP_HOME" node -e '
const fs = require("fs");
const cfg = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
const agent = (cfg.agents?.list || []).find((a) => a.id === "ext-default");
if (!agent) {
  console.error("ext-default missing from openclaw.json");
  process.exit(1);
}
const sec = agent?.tools?.exec?.security;
if (sec !== "deny") {
  console.error("expected ext-default tools.exec.security=deny, got:", sec);
  process.exit(1);
}
const hasBlocked = (agent.skills || []).some((s) => s === "self-improving" || s === "self-improve");
if (hasBlocked) {
  console.error("external crew must not include self-improving skills");
  process.exit(1);
}
const main = (cfg.agents?.list || []).find((a) => a.id === "main");
if ((main?.subagents?.allowAgents || []).includes("ext-default")) {
  console.error("external crew should not be in main.subagents.allowAgents");
  process.exit(1);
}
' "$CONFIG_PATH"
assert_true "[ -d '$OPENCLAW_HOME/workspace-ext-default/feedback' ]" "external crew feedback directory missing"

echo "[TEST] external T0 should support explicit ALLOWED_COMMANDS whitelist"
mkdir -p "$OPENCLAW_HOME/workspace-ext-whitelist"
cat > "$OPENCLAW_HOME/workspace-ext-whitelist/SOUL.md" <<'EOF'
# Ext Whitelist
crew-type: external
command-tier: T0
EOF
cat > "$OPENCLAW_HOME/workspace-ext-whitelist/DECLARED_SKILLS" <<'EOF'
# keep empty for this test
EOF
cat > "$OPENCLAW_HOME/workspace-ext-whitelist/ALLOWED_COMMANDS" <<'EOF'
+echo
EOF
HOME="$TMP_HOME" bash "$PROJECT_ROOT/crews/hrbp/skills/hrbp-recruit/scripts/add-agent.sh" ext-whitelist --crew-type external --note "test-external-whitelist" >"$LOG_DIR/ext-whitelist-add.log" 2>&1
HOME="$TMP_HOME" "$PROJECT_ROOT/scripts/setup-crew.sh" >"$LOG_DIR/setup-after-ext.log" 2>&1
HOME="$TMP_HOME" node -e '
const fs = require("fs");
const cfg = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
const approvals = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const agent = (cfg.agents?.list || []).find((a) => a.id === "ext-whitelist");
if (!agent) {
  console.error("ext-whitelist missing from openclaw.json");
  process.exit(1);
}
const sec = agent?.tools?.exec?.security;
if (sec !== "allowlist") {
  console.error("expected ext-whitelist tools.exec.security=allowlist, got:", sec);
  process.exit(1);
}
const allowlist = approvals?.agents?.["ext-whitelist"]?.allowlist || [];
if (!Array.isArray(allowlist) || allowlist.length === 0) {
  console.error("expected ext-whitelist allowlist entries in exec-approvals");
  process.exit(1);
}
' "$CONFIG_PATH" "$OPENCLAW_HOME/exec-approvals.json"

echo "[TEST] main should be able to dismiss internal crew"
mkdir -p "$OPENCLAW_HOME/workspace-int-demo"
cat > "$OPENCLAW_HOME/workspace-int-demo/SOUL.md" <<'EOF'
# Int Demo
crew-type: internal
command-tier: T1
EOF
touch "$OPENCLAW_HOME/workspace-int-demo/IDENTITY.md"

HOME="$TMP_HOME" bash "$PROJECT_ROOT/crews/hrbp/skills/hrbp-recruit/scripts/add-agent.sh" int-demo --crew-type internal --note "test-internal" >"$LOG_DIR/int-add.log" 2>&1
HOME="$TMP_HOME" node -e '
const fs = require("fs");
const cfg = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
const a = (cfg.agents?.list || []).find((x) => x.id === "int-demo");
if (!a) {
  console.error("int-demo missing after recruit");
  process.exit(1);
}
const skills = a.skills || [];
if (skills.includes("alipay-mcp-config")) {
  console.error("internal recruit should not auto-include project global skills");
  process.exit(1);
}
' "$CONFIG_PATH"
HOME="$TMP_HOME" bash "$PROJECT_ROOT/crews/main/skills/crew-dismiss/scripts/dismiss-internal-crew.sh" int-demo >"$LOG_DIR/int-dismiss.log" 2>&1

assert_true \
  "! HOME='$TMP_HOME' node -e \"const fs=require('fs');const c=JSON.parse(fs.readFileSync('$CONFIG_PATH','utf8'));process.exit((c.agents?.list||[]).some(a=>a.id==='int-demo')?0:1)\"" \
  "internal crew int-demo still exists in openclaw.json after dismiss"

assert_true \
  "ls '$OPENCLAW_HOME/archived' | grep -q '^workspace-int-demo-'" \
  "archived workspace for int-demo not found"

echo "ALL TESTS PASSED"
