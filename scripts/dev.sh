#!/bin/bash
# dev.sh - 开发环境启动脚本（前台运行 gateway）
#
# 执行流程：
#   1. 初始化配置文件（如不存在，从模板创建）
#   2. apply-addons.sh（patches + skills + crew 模板，不 build、不 restart）
#   3. 前台运行 openclaw gateway（需要用户自行先 pnpm build）
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_PATH="$HOME/.openclaw/openclaw.json"

# 如果配置文件不存在，从模板创建
if [ ! -f "$CONFIG_PATH" ]; then
  mkdir -p "$HOME/.openclaw"
  echo "📝 Creating default config from template..."
  if [ -f "$PROJECT_ROOT/config-templates/openclaw.json" ]; then
    cp "$PROJECT_ROOT/config-templates/openclaw.json" "$CONFIG_PATH"
  else
    echo "{}" > "$CONFIG_PATH"
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
  ' "$CONFIG_PATH"
fi

# Apply addons（不 build、不 restart — 开发模式下用户自行 pnpm build）
"$PROJECT_ROOT/scripts/apply-addons.sh" --no-build --no-restart

ACCESS_URL="http://127.0.0.1:18789"

echo "🚀 Starting gateway in dev mode..."
echo "   Data: ~/.openclaw"
echo "   Config: $CONFIG_PATH"
echo "   Access: $ACCESS_URL"
echo ""

cd "$PROJECT_ROOT/openclaw"

# 根据参数决定运行模式
case "${1:-gateway}" in
  gateway)
    shift 2>/dev/null || true
    pnpm openclaw gateway "$@"
    ;;
  cli)
    shift
    pnpm openclaw "$@"
    ;;
  *)
    pnpm openclaw "$@"
    ;;
esac
