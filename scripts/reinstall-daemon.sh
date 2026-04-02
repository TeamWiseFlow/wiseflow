#!/bin/bash
# 重新安装 Gateway Daemon
# 支持 macOS (LaunchAgent)、Linux (systemd)、Windows (Task Scheduler)
# 使用默认存储位置 ~/.openclaw

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OPENCLAW_CONFIG_PATH_DEFAULT="${OPENCLAW_CONFIG_PATH:-$HOME/.openclaw/openclaw.json}"
OPENCLAW_STATE_DIR_DEFAULT="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
SYSTEMD_ENV_FILE="${OPENCLAW_STATE_DIR_DEFAULT}/daemon.env"
SKIP_ADDONS=false

while [ $# -gt 0 ]; do
  case "$1" in
    --skip-addons)
      SKIP_ADDONS=true
      shift
      ;;
    *)
      echo "❌ Unknown option: $1"
      echo "Usage: $0 [--skip-addons]"
      echo "  --skip-addons  Skip apply-addons.sh (use when upgrade.sh already ran it)"
      exit 1
      ;;
  esac
done

collect_env_refs_from_config() {
  local config_path="$1"
  node - "$config_path" <<'NODE'
const fs = require("node:fs");

const configPath = process.argv[2];
if (!configPath) {
  process.exit(1);
}

let raw = "";
try {
  raw = fs.readFileSync(configPath, "utf8");
} catch {
  process.exit(1);
}

let cfg;
try {
  cfg = JSON.parse(raw);
} catch {
  process.exit(2);
}

const refs = new Set();
const envPattern = /\$\{([A-Z][A-Z0-9_]*)\}/g;
const envIdPattern = /^[A-Z][A-Z0-9_]*$/;

function walk(value) {
  if (typeof value === "string") {
    for (const match of value.matchAll(envPattern)) {
      if (match[1]) {
        refs.add(match[1]);
      }
    }
    return;
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      walk(item);
    }
    return;
  }

  if (!value || typeof value !== "object") {
    return;
  }

  if (
    value.source === "env" &&
    typeof value.id === "string" &&
    envIdPattern.test(value.id)
  ) {
    refs.add(value.id);
  }

  for (const child of Object.values(value)) {
    walk(child);
  }
}

walk(cfg);
process.stdout.write([...refs].sort().join("\n"));
NODE
}

get_env_file_value() {
  local env_file="$1"
  local key="$2"
  local line=""

  if [ ! -f "$env_file" ]; then
    return 1
  fi

  line="$(grep -E "^${key}=" "$env_file" | tail -n 1 || true)"
  if [ -z "$line" ]; then
    return 1
  fi

  printf "%s" "${line#*=}"
}

prompt_env_value() {
  local key="$1"
  local default_value="$2"
  local default_source="$3"
  local value=""
  local reuse=""
  local skip_empty=""

  if [ -n "$default_value" ]; then
    read -r -p "Use existing ${default_source} value for ${key}? [Y/n] " reuse
    if [[ ! "$reuse" =~ ^[Nn]$ ]]; then
      printf "%s" "$default_value"
      return 0
    fi
  fi

  while true; do
    read -r -s -p "Enter value for ${key}: " value
    echo ""
    value="${value//$'\r'/}"
    value="${value//$'\n'/}"

    if [ -n "$value" ]; then
      printf "%s" "$value"
      return 0
    fi

    read -r -p "Value is empty, skip ${key}? [y/N] " skip_empty
    if [[ "$skip_empty" =~ ^[Yy]$ ]]; then
      printf ""
      return 0
    fi
  done
}

prepare_systemd_env_file() {
  local config_path="$1"
  local env_file="$2"
  local env_refs=""
  local var_name=""
  local shell_value=""
  local existing_file_value=""
  local default_value=""
  local default_source=""
  local resolved_value=""
  local temp_env_file=""

  if [ ! -f "$config_path" ]; then
    echo "ℹ️  Config not found at ${config_path}; skip systemd env bootstrap."
    return 0
  fi

  if ! env_refs="$(collect_env_refs_from_config "$config_path")"; then
    echo "⚠️  Failed to parse ${config_path}; skip systemd env bootstrap."
    return 0
  fi

  if [ -z "$env_refs" ]; then
    echo "ℹ️  No env-var references found in ${config_path}; skip systemd env bootstrap."
    return 0
  fi

  echo ""
  echo "🔐 Detected env vars from ${config_path}:"
  while IFS= read -r var_name; do
    [ -n "$var_name" ] || continue
    echo "   - ${var_name}"
  done <<< "$env_refs"
  echo ""

  mkdir -p "$(dirname "$env_file")"
  temp_env_file="$(mktemp "${env_file}.tmp.XXXXXX")"
  chmod 600 "$temp_env_file"

  while IFS= read -r var_name; do
    [ -n "$var_name" ] || continue
    default_value=""
    default_source=""
    shell_value="${!var_name-}"
    existing_file_value=""

    if [ -n "$shell_value" ]; then
      default_value="$shell_value"
      default_source="shell"
    else
      existing_file_value="$(get_env_file_value "$env_file" "$var_name" || true)"
      if [ -n "$existing_file_value" ]; then
        default_value="$existing_file_value"
        default_source="existing env file"
      fi
    fi

    if [ -t 0 ]; then
      resolved_value="$(prompt_env_value "$var_name" "$default_value" "$default_source")"
    else
      resolved_value="$default_value"
      if [ -z "$resolved_value" ]; then
        echo "⚠️  Missing ${var_name} in non-interactive mode; leaving it unset."
      fi
    fi

    if [ -n "$resolved_value" ]; then
      printf "%s=%s\n" "$var_name" "$resolved_value" >> "$temp_env_file"
    fi
  done <<< "$env_refs"

  mv "$temp_env_file" "$env_file"
  chmod 600 "$env_file"
  echo "✅ Wrote systemd env file: ${env_file}"
}

resolve_gateway_systemd_service_name() {
  local profile="${OPENCLAW_PROFILE:-}"
  local profile_trimmed=""
  local profile_lower=""

  profile_trimmed="$(printf "%s" "$profile" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
  profile_lower="$(printf "%s" "$profile_trimmed" | tr '[:upper:]' '[:lower:]')"

  if [ -z "$profile_trimmed" ] || [ "$profile_lower" = "default" ]; then
    printf "%s" "openclaw-gateway"
    return 0
  fi

  printf "%s" "openclaw-gateway-${profile_trimmed}"
}

install_systemd_env_dropin() {
  local env_file="$1"
  local user_systemd_dir=""
  local service_name=""
  local dropin_dir=""
  local dropin_file=""

  if [ "$(uname -s)" != "Linux" ]; then
    return 0
  fi

  if [ ! -f "$env_file" ]; then
    echo "ℹ️  Env file ${env_file} not found; skip systemd drop-in."
    return 0
  fi

  if ! command -v systemctl >/dev/null 2>&1; then
    echo "ℹ️  systemctl unavailable; skip systemd drop-in."
    return 0
  fi

  if ! systemctl --user show-environment >/dev/null 2>&1; then
    echo "⚠️  systemctl --user unavailable in current session; skip systemd drop-in."
    return 0
  fi

  service_name="$(resolve_gateway_systemd_service_name)"
  user_systemd_dir="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
  dropin_dir="${user_systemd_dir}/${service_name}.service.d"
  dropin_file="${dropin_dir}/10-env-file.conf"

  mkdir -p "$dropin_dir"
  cat > "$dropin_file" <<EOF
[Service]
EnvironmentFile=-${env_file}
EOF

  systemctl --user daemon-reload
  systemctl --user restart "${service_name}.service"

  echo "✅ Installed systemd drop-in: ${dropin_file}"
}

echo "🔧 Reinstalling Gateway Daemon..."
echo "   Data: ~/.openclaw"

# 如果配置文件不存在，从模板创建（与 dev.sh 保持一致）
if [ ! -f "$OPENCLAW_CONFIG_PATH_DEFAULT" ]; then
  mkdir -p "$(dirname "$OPENCLAW_CONFIG_PATH_DEFAULT")"
  echo "📝 Creating default config from template..."
  if [ -f "$PROJECT_ROOT/config-templates/openclaw.json" ]; then
    cp "$PROJECT_ROOT/config-templates/openclaw.json" "$OPENCLAW_CONFIG_PATH_DEFAULT"
  else
    echo "{}" > "$OPENCLAW_CONFIG_PATH_DEFAULT"
  fi
fi

# WSL2 环境：注入 noSandbox = true（Chrome 在 WSL2 中需要此选项）
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
  ' "$OPENCLAW_CONFIG_PATH_DEFAULT"
fi

# 安装 addon + 同步 Agent 系统（apply-addons.sh 末尾会自动调 setup-crew.sh）
if [ "$SKIP_ADDONS" = "true" ]; then
  echo "⏭️  Skipping apply-addons (--skip-addons)"
else
  "$PROJECT_ROOT/scripts/apply-addons.sh"
fi

if [ "$(uname -s)" = "Linux" ]; then
  # config fallback：running config 不存在时从 config-templates 扫描 env refs
  _env_scan_config="$OPENCLAW_CONFIG_PATH_DEFAULT"
  if [ ! -f "$_env_scan_config" ] && [ -f "$PROJECT_ROOT/config-templates/openclaw.json" ]; then
    _env_scan_config="$PROJECT_ROOT/config-templates/openclaw.json"
    echo "  ℹ️  Running config not found; scanning config-templates/openclaw.json for env vars..."
  fi
  prepare_systemd_env_file "$_env_scan_config" "$SYSTEMD_ENV_FILE"

  # 将 node 路径注入 daemon.env，解决 systemd 最小 PATH 不含 node 的问题
  _node_bin="$(command -v node 2>/dev/null || true)"
  if [ -n "$_node_bin" ]; then
    _node_dir="$(dirname "$_node_bin")"
    mkdir -p "$(dirname "$SYSTEMD_ENV_FILE")"
    # 幂等：移除旧 PATH 行后重写（防止重复运行产生重复行）
    {
      [ -f "$SYSTEMD_ENV_FILE" ] && grep -v "^PATH=" "$SYSTEMD_ENV_FILE" || true
      printf 'PATH=%s:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n' "$_node_dir"
    } > "${SYSTEMD_ENV_FILE}.new"
    mv "${SYSTEMD_ENV_FILE}.new" "$SYSTEMD_ENV_FILE"
    chmod 600 "$SYSTEMD_ENV_FILE"
    echo "  ✅ Node.js path written to daemon.env: $_node_dir"
  fi

  # WSL2 环境：幂等注入 GUI 显示相关环境变量（WSLg 需要）
  if grep -qi microsoft /proc/version 2>/dev/null; then
    mkdir -p "$(dirname "$SYSTEMD_ENV_FILE")"
    {
      [ -f "$SYSTEMD_ENV_FILE" ] && grep -vE "^(DISPLAY|WAYLAND_DISPLAY|XDG_RUNTIME_DIR)=" "$SYSTEMD_ENV_FILE" || true
      printf 'DISPLAY=:0\n'
      printf 'WAYLAND_DISPLAY=wayland-0\n'
      printf 'XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir\n'
    } > "${SYSTEMD_ENV_FILE}.new"
    mv "${SYSTEMD_ENV_FILE}.new" "$SYSTEMD_ENV_FILE"
    chmod 600 "$SYSTEMD_ENV_FILE"
    echo "  ✅ WSL2 display env written to daemon.env (DISPLAY, WAYLAND_DISPLAY, XDG_RUNTIME_DIR)"
  fi
fi

cd "$PROJECT_ROOT/openclaw"

# 卸载现有的 daemon
pnpm openclaw daemon uninstall 2>/dev/null || true

# 重新安装（会使用当前环境变量，自动检测操作系统）
pnpm openclaw daemon install

if [ "$(uname -s)" = "Linux" ]; then
  install_systemd_env_dropin "$SYSTEMD_ENV_FILE"
fi

ACCESS_URL="http://127.0.0.1:18789"
ENV_NOTE=""

echo ""
echo "✅ Daemon reinstalled"
echo ""
echo "Now open $ACCESS_URL to use $ENV_NOTE"
