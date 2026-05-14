#!/bin/bash
# install.sh - 一键安装 / 升级 wiseflow
#
# 适用场景：
#   - 新用户首次安装（已下载并解压缩全部源码文件）
#   - 老用户升级（拉取最新代码 + 同步 openclaw 引擎）
#
# 执行流程：
#   1. 验证 wiseflow 项目目录合法性
#   2. 初始化 git remote（如未初始化）或验证 remote URL
#   3. git fetch + reset --hard 拉取最新 wiseflow 代码
#   4. 读取 openclaw.version，按锚定版本检出 openclaw 子目录
#      - 若已是目标 commit，跳过耗时的 install
#   5. 首次初始化内置全局 Crew workspace + openclaw.json
#   6. apply-addons.sh（patches + skills + crew 模板，内含 setup-crew.sh）
#   7. pnpm build（编译 openclaw dist）
#   8. 安装 daemon + 环境变量注入 + 重启
#
# ⚠️  升级前请确保系统空闲（无 agent 会话正在处理任务）
set -e

OFB_REPO="https://github.com/TeamWiseFlow/wiseflow.git"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OPENCLAW_DIR="$PROJECT_ROOT/openclaw"
VERSION_FILE="$PROJECT_ROOT/openclaw.version"
OPENCLAW_HOME="$HOME/.openclaw"
OPENCLAW_CONFIG_PATH="${OPENCLAW_CONFIG_PATH:-$OPENCLAW_HOME/openclaw.json}"
SYSTEMD_ENV_FILE="$OPENCLAW_HOME/daemon.env"
MACOS_GATEWAY_ENV="$OPENCLAW_HOME/service-env/ai.openclaw.gateway.env"
BUILTIN_CREWS="main hrbp it-engineer"
FORCE=false
SKIP_CREW=false

while [ $# -gt 0 ]; do
  case "$1" in
    --force)
      FORCE=true
      shift
      ;;
    --skip-crew)
      SKIP_CREW=true
      shift
      ;;
    *)
      echo "❌ Unknown option: $1"
      echo "Usage: $0 [--force] [--skip-crew]"
      echo "  --force       Overwrite existing workspace files (including MEMORY.md)"
      echo "  --skip-crew   Skip setup-crew.sh (only sync addons, no workspace updates)"
      exit 1
      ;;
  esac
done

cd "$PROJECT_ROOT"

echo "🔧 wiseflow — Install / Upgrade"
echo "   Project root: $PROJECT_ROOT"
echo ""

# ─── 1. 验证当前目录是 wiseflow 项目 ──────────────────────────────────
if [ ! -f "$PROJECT_ROOT/scripts/apply-addons.sh" ] || [ ! -d "$OPENCLAW_DIR" ]; then
  echo "❌ This does not look like a wiseflow project directory."
  echo "   Expected: scripts/apply-addons.sh and openclaw/ subdirectory"
  exit 1
fi

ensure_openclaw_config() {
  if [ ! -f "$OPENCLAW_CONFIG_PATH" ]; then
    mkdir -p "$(dirname "$OPENCLAW_CONFIG_PATH")"
    echo "📝 Creating default config from template..."
    if [ -f "$PROJECT_ROOT/config-templates/openclaw.json" ]; then
      cp "$PROJECT_ROOT/config-templates/openclaw.json" "$OPENCLAW_CONFIG_PATH"
    else
      echo "{}" > "$OPENCLAW_CONFIG_PATH"
    fi
  fi

  # WSL2 环境：注入 noSandbox = true
  if grep -qi microsoft /proc/version 2>/dev/null; then
    node -e '
      const fs = require("fs");
      const p = process.argv[1];
      const c = JSON.parse(fs.readFileSync(p, "utf8"));
      if (!c.browser) c.browser = {};
      if (!c.browser.noSandbox) {
        c.browser.noSandbox = true;
        fs.writeFileSync(p, JSON.stringify(c, null, 2) + "\n");
        console.log("  WSL2 detected: browser.noSandbox = true");
      }
    ' "$OPENCLAW_CONFIG_PATH"
  fi
}

# ─── 2. 配置 git remote ────────────────────────────────────────
if [ ! -d "$PROJECT_ROOT/.git" ]; then
  echo "📦 Initializing git repository..."
  git init
  git remote add origin "$OFB_REPO"
  echo "  ✅ git initialized, remote set to $OFB_REPO"
else
  CURRENT_REMOTE="$(git remote get-url origin 2>/dev/null || echo "")"
  if [ -z "$CURRENT_REMOTE" ]; then
    git remote add origin "$OFB_REPO"
    echo "  ✅ Remote 'origin' added: $OFB_REPO"
  elif [ "$CURRENT_REMOTE" != "$OFB_REPO" ]; then
    echo "  ℹ️  Current remote: $CURRENT_REMOTE"
    echo "  ℹ️  Official wiseflow repo: $OFB_REPO"
    echo ""
    echo "  Remote is not the official wiseflow repo. Continue anyway? [y/N]"
    read -r reply
    case "$reply" in
      y|Y) echo "  Continuing with existing remote..." ;;
      *) echo "  Aborted."; exit 0 ;;
    esac
  fi
fi

# ─── 3. 拉取最新 wiseflow 代码 ────────────────────────────────────────
echo "📥 Fetching latest wiseflow code..."
if git fetch origin master; then
  COMMITS_BEHIND="$(git rev-list HEAD..origin/master --count 2>/dev/null || echo "?")"
  if [ "$COMMITS_BEHIND" = "0" ]; then
    echo "  ✅ wiseflow code is already up to date."
  elif [ "$COMMITS_BEHIND" = "?" ]; then
    echo "  ⚠️  Unable to compare with origin/master, continuing with local wiseflow code."
  else
    echo "  📊 $COMMITS_BEHIND new commit(s) available"
    if git reset --hard origin/master; then
      echo "  ✅ wiseflow code updated"
    else
      echo "  ⚠️  Failed to reset to origin/master, continuing with local wiseflow code."
    fi
  fi
else
  echo "  ⚠️  Failed to fetch latest wiseflow code from origin/master."
  echo "  ⚠️  Continuing with local wiseflow code."
fi
echo ""

# ─── 4. 按锚定版本更新 openclaw 引擎 ────────────────────────────
if [ ! -f "$VERSION_FILE" ]; then
  echo "❌ openclaw.version not found at $VERSION_FILE"
  exit 1
fi

# shellcheck source=../openclaw.version
. "$VERSION_FILE"

if [ -z "$OPENCLAW_COMMIT" ]; then
  echo "❌ OPENCLAW_COMMIT not set in openclaw.version"
  exit 1
fi

echo "🔍 openclaw target: $OPENCLAW_VERSION ($OPENCLAW_COMMIT)"

CURRENT_COMMIT="$(git -C "$OPENCLAW_DIR" rev-parse HEAD 2>/dev/null || echo "")"
if [ "$CURRENT_COMMIT" = "$OPENCLAW_COMMIT" ]; then
  echo "  ✅ openclaw is already at target commit."
  OPENCLAW_UPDATED=false
else
  echo "  Current commit: ${CURRENT_COMMIT:-"(unknown)"}"
  echo "  Checking out target commit..."
  git -C "$OPENCLAW_DIR" reset --hard HEAD 2>/dev/null || true
  if ! git -C "$OPENCLAW_DIR" cat-file -e "${OPENCLAW_COMMIT}^{tree}" 2>/dev/null; then
    echo "  📥 Fetching openclaw target commit..."
    git -C "$OPENCLAW_DIR" fetch origin --tags || \
      echo "  ⚠️  Failed to fetch openclaw tags from origin."
  fi
  if ! git -C "$OPENCLAW_DIR" cat-file -e "${OPENCLAW_COMMIT}^{tree}" 2>/dev/null; then
    echo "  ⚠️  Target commit not found locally; trying shallow-clone recovery..."
    git -C "$OPENCLAW_DIR" fetch --unshallow origin 2>/dev/null || \
      git -C "$OPENCLAW_DIR" fetch --deepen=200 origin || \
      echo "  ⚠️  Failed to deepen openclaw history from origin."
  fi
  if ! git -C "$OPENCLAW_DIR" cat-file -e "${OPENCLAW_COMMIT}^{tree}" 2>/dev/null; then
    echo "❌ Local openclaw commit (${CURRENT_COMMIT:-unknown}) does not match required openclaw.version ($OPENCLAW_COMMIT)."
    echo "   Network update failed or target commit is not available locally; aborting install."
    exit 1
  fi
  if ! git -C "$OPENCLAW_DIR" checkout "$OPENCLAW_COMMIT"; then
    echo "❌ Unable to checkout required openclaw commit from openclaw.version: $OPENCLAW_COMMIT"
    exit 1
  fi
  echo "  ✅ openclaw checked out at $OPENCLAW_VERSION"

  echo "  📦 Installing dependencies..."
  (cd "$OPENCLAW_DIR" && pnpm install)
  OPENCLAW_UPDATED=true
fi
echo ""

# ─── 5. 初始化内置 Crew workspace + 配置文件 ───────────────────
# shellcheck source=scripts/lib/crew-workspaces.sh
source "$PROJECT_ROOT/scripts/lib/crew-workspaces.sh"

if [ "$SKIP_CREW" = "true" ]; then
  echo "⏭️  Skipping built-in crew workspace bootstrap (--skip-crew)"
else
  echo "📦 Bootstrapping built-in crew workspaces..."
  seed_builtin_crew_workspaces "$PROJECT_ROOT/crews" "$OPENCLAW_HOME" "$BUILTIN_CREWS"
fi
ensure_openclaw_config
echo ""

# ─── 6. 应用 addons（patches + skills + crew 模板）──────────────
# apply-addons 不 build、不 restart（由本脚本统一处理）
echo "🔄 Applying addons..."
ADDON_ARGS=(--no-build --no-restart)
[ "$FORCE" = "true" ] && ADDON_ARGS+=(--force)
[ "$SKIP_CREW" = "true" ] && ADDON_ARGS+=(--skip-crew)
"$PROJECT_ROOT/scripts/apply-addons.sh" "${ADDON_ARGS[@]}"
echo ""

# ─── 7. 编译 openclaw dist ──────────────────────────────────────
echo "🔨 Building openclaw..."
(cd "$OPENCLAW_DIR" && pnpm build)
echo "  ✅ Build complete"

echo "🎨 Building Control UI assets..."
(cd "$OPENCLAW_DIR" && pnpm ui:build)
echo "  ✅ UI build complete"
echo ""

# ─── 8. 环境变量收集 + daemon 安装 ─────────────────────────

# --- 8a. 收集 openclaw.json 中引用的环境变量（Linux + macOS 共享）---
_env_scan_config="$OPENCLAW_CONFIG_PATH"
if [ ! -f "$_env_scan_config" ] && [ -f "$PROJECT_ROOT/config-templates/openclaw.json" ]; then
  _env_scan_config="$PROJECT_ROOT/config-templates/openclaw.json"
fi

collect_env_refs_from_config() {
  local config_path="$1"
  node - "$config_path" <<'NODE'
const fs = require("node:fs");
const configPath = process.argv[2];
if (!configPath) process.exit(1);
let raw = "";
try { raw = fs.readFileSync(configPath, "utf8"); } catch { process.exit(1); }
let cfg;
try { cfg = JSON.parse(raw); } catch { process.exit(2); }
const refs = new Set();
const envPattern = /\$\{([A-Z][A-Z0-9_]*)\}/g;
const envIdPattern = /^[A-Z][A-Z0-9_]*$/;
function walk(value) {
  if (typeof value === "string") { for (const m of value.matchAll(envPattern)) { if (m[1]) refs.add(m[1]); } return; }
  if (Array.isArray(value)) { for (const item of value) walk(item); return; }
  if (!value || typeof value !== "object") return;
  if (value.source === "env" && typeof value.id === "string" && envIdPattern.test(value.id)) refs.add(value.id);
  for (const child of Object.values(value)) walk(child);
}
walk(cfg);
process.stdout.write([...refs].sort().join("\n"));
NODE
}

get_env_file_value() {
  local env_file="$1" key="$2" line=""
  [ -f "$env_file" ] || return 1
  # Try KEY=value format first (systemd)
  line="$(grep -E "^${key}=" "$env_file" | tail -n 1 || true)"
  if [ -z "$line" ]; then
    # Try export KEY= format (shell / launchd)
    line="$(grep -E "^export ${key}=" "$env_file" | tail -n 1 || true)"
  fi
  [ -n "$line" ] || return 1
  # Extract value: remove leading KEY= or export KEY=, strip single quotes
  _value="${line#*=}"
  _value="${_value#\'}"; _value="${_value%\'}"
  printf "%s" "$_value"
}

prompt_env_value() {
  local key="$1" default_value="$2" default_source="$3" value="" reuse="" skip_empty=""
  if [ -n "$default_value" ]; then
    read -r -p "Use existing ${default_source} value for ${key}? [Y/n] " reuse
    if [[ ! "$reuse" =~ ^[Nn]$ ]]; then printf "%s" "$default_value"; return 0; fi
  fi
  while true; do
    read -r -s -p "Enter value for ${key}: " value; echo ""
    value="${value//$'\r'/}"; value="${value//$'\n'/}"
    if [ -n "$value" ]; then printf "%s" "$value"; return 0; fi
    read -r -p "Value is empty, skip ${key}? [y/N] " skip_empty
    if [[ "$skip_empty" =~ ^[Yy]$ ]]; then printf ""; return 0; fi
  done
}

env_refs="$(collect_env_refs_from_config "$_env_scan_config" 2>/dev/null || true)"
if [ -n "$env_refs" ]; then
  echo "🔐 Detected env vars from config:"
  while IFS= read -r var_name; do
    [ -n "$var_name" ] || continue
    echo "   - ${var_name}"
  done <<< "$env_refs"
  echo ""
fi

# --- 8b. Linux: 写入 daemon.env（在 daemon install 之前）---
if [ "$(uname -s)" = "Linux" ] && [ -n "$env_refs" ]; then
  mkdir -p "$(dirname "$SYSTEMD_ENV_FILE")"
  temp_env_file="$(mktemp "${SYSTEMD_ENV_FILE}.tmp.XXXXXX")"
  chmod 600 "$temp_env_file"

  # 保留现有 daemon.env 中不属于 env_refs 管理的行（用户自定义变量）
  if [ -f "$SYSTEMD_ENV_FILE" ]; then
    while IFS= read -r existing_line; do
      [[ "$existing_line" =~ ^[[:space:]]*# ]] && continue
      [ -z "$existing_line" ] && continue
      existing_key="${existing_line%%=*}"
      if ! grep -qxF "$existing_key" <<< "$env_refs"; then
        printf "%s\n" "$existing_line" >> "$temp_env_file"
      fi
    done < "$SYSTEMD_ENV_FILE"
  fi

  while IFS= read -r var_name; do
    [ -n "$var_name" ] || continue
    default_value="" default_source=""
    shell_value="${!var_name-}"
    if [ -n "$shell_value" ]; then
      default_value="$shell_value"; default_source="shell"
    else
      existing_file_value="$(get_env_file_value "$SYSTEMD_ENV_FILE" "$var_name" || true)"
      if [ -n "$existing_file_value" ]; then
        default_value="$existing_file_value"; default_source="existing env file"
      fi
    fi
    if [ -t 0 ]; then
      resolved_value="$(prompt_env_value "$var_name" "$default_value" "$default_source")"
    else
      resolved_value="$default_value"
      [ -z "$resolved_value" ] && echo "⚠️  Missing ${var_name} in non-interactive mode; leaving it unset."
    fi
    [ -n "$resolved_value" ] && printf "%s=%s\n" "$var_name" "$resolved_value" >> "$temp_env_file"
  done <<< "$env_refs"

  mv "$temp_env_file" "$SYSTEMD_ENV_FILE"
  chmod 600 "$SYSTEMD_ENV_FILE"
  echo "✅ Merged env file: $SYSTEMD_ENV_FILE"

  # --- 注入 node 路径到 daemon.env ---
  _node_bin="$(command -v node 2>/dev/null || true)"
  if [ -n "$_node_bin" ]; then
    _node_dir="$(dirname "$_node_bin")"
    mkdir -p "$(dirname "$SYSTEMD_ENV_FILE")"
    {
      [ -f "$SYSTEMD_ENV_FILE" ] && grep -v "^PATH=" "$SYSTEMD_ENV_FILE" || true
      printf 'PATH=%s:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n' "$_node_dir"
    } > "${SYSTEMD_ENV_FILE}.new"
    mv "${SYSTEMD_ENV_FILE}.new" "$SYSTEMD_ENV_FILE"
    chmod 600 "$SYSTEMD_ENV_FILE"
  fi

  # --- WSL2 环境：注入 GUI 显示变量 ---
  if grep -qi microsoft /proc/version 2>/dev/null; then
    {
      [ -f "$SYSTEMD_ENV_FILE" ] && grep -vE "^(DISPLAY|WAYLAND_DISPLAY|XDG_RUNTIME_DIR)=" "$SYSTEMD_ENV_FILE" || true
      printf 'DISPLAY=:0\nWAYLAND_DISPLAY=wayland-0\nXDG_RUNTIME_DIR=/mnt/wslg/runtime-dir\n'
    } > "${SYSTEMD_ENV_FILE}.new"
    mv "${SYSTEMD_ENV_FILE}.new" "$SYSTEMD_ENV_FILE"
    chmod 600 "$SYSTEMD_ENV_FILE"
  fi
fi

# ─── 9. 安装 daemon ──────────────────────────────────────
cd "$OPENCLAW_DIR"
pnpm openclaw daemon uninstall 2>/dev/null || true
pnpm openclaw daemon install

# ─── 10. 平台特定的 post-install ─────────────────────────
if [ "$(uname -s)" = "Linux" ] && command -v systemctl >/dev/null 2>&1; then
  # --- systemd drop-in 引用 daemon.env ---
  if systemctl --user show-environment >/dev/null 2>&1; then
    SERVICE_NAME="openclaw-gateway"
    user_systemd_dir="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
    dropin_dir="${user_systemd_dir}/${SERVICE_NAME}.service.d"
    mkdir -p "$dropin_dir"
    cat > "${dropin_dir}/10-env-file.conf" <<EOF
[Service]
EnvironmentFile=-${SYSTEMD_ENV_FILE}
EOF
    systemctl --user daemon-reload
    systemctl --user restart "${SERVICE_NAME}.service"
    echo "✅ Installed systemd drop-in and restarted gateway"
  fi
elif [ "$(uname -s)" = "Darwin" ] && [ -n "$env_refs" ]; then
  # --- 追加 env 到 launchd gateway.env（在 daemon install 之后）---
  if [ -f "$MACOS_GATEWAY_ENV" ]; then
    temp_env_file="$(mktemp "${MACOS_GATEWAY_ENV}.tmp.XXXXXX")"
    chmod 600 "$temp_env_file"

    # 保留 daemon install 写入的内容
    cat "$MACOS_GATEWAY_ENV" > "$temp_env_file"

    while IFS= read -r var_name; do
      [ -n "$var_name" ] || continue
      # 跳过 daemon install 已写入的变量
      if grep -qE "^export ${var_name}=" "$MACOS_GATEWAY_ENV" 2>/dev/null; then
        continue
      fi
      default_value="" default_source=""
      shell_value="${!var_name-}"
      if [ -n "$shell_value" ]; then
        default_value="$shell_value"; default_source="shell"
      fi
      if [ -t 0 ]; then
        resolved_value="$(prompt_env_value "$var_name" "$default_value" "$default_source")"
      else
        resolved_value="$default_value"
        [ -z "$resolved_value" ] && echo "⚠️  Missing ${var_name} in non-interactive mode; leaving it unset."
      fi
      if [ -n "$resolved_value" ]; then
        # shell export 格式，单引号转义
        printf "export %s='%s'\n" "$var_name" "${resolved_value//\'/\'\\\'\'}" >> "$temp_env_file"
      fi
    done <<< "$env_refs"

    mv "$temp_env_file" "$MACOS_GATEWAY_ENV"
    chmod 600 "$MACOS_GATEWAY_ENV"
    echo "✅ Merged env file: $MACOS_GATEWAY_ENV"

    # 重启 gateway 使新环境变量生效
    cd "$OPENCLAW_DIR"
    pnpm openclaw gateway restart 2>/dev/null || true
  else
    echo "⚠️  macOS gateway env file not found at $MACOS_GATEWAY_ENV"
    echo "   Skipping env injection. Ensure gateway is installed: openclaw daemon install"
  fi
fi

echo ""
echo "✅ Installation complete!"
echo "   Access: http://127.0.0.1:18789"
