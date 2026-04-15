#!/bin/bash
# upgrade_without_git.sh - 升级 openclaw 引擎 + 配置同步（跳过 wiseflow 和 openclaw 的 git 同步）
#
# 适用场景：
#   - 通过 release 包安装的用户（手动解压新版 tarball 后运行，不依赖 git 拉取）
#
# 执行流程：
#   1. 验证 wiseflow 项目目录合法性
#   2. 读取 openclaw.version，安装依赖并构建（跳过 git fetch/checkout）
#   3. 调用 apply-addons.sh（内含 setup-crew.sh，只需调一次）
#
# ⚠️  升级前请确保系统空闲（无 agent 会话正在处理任务）
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OPENCLAW_DIR="$PROJECT_ROOT/openclaw"
VERSION_FILE="$PROJECT_ROOT/openclaw.version"
FORCE=false
SKIP_ADDONS=false
SKIP_CREW=false

while [ $# -gt 0 ]; do
  case "$1" in
    --force)
      FORCE=true
      shift
      ;;
    --skip-addons)
      SKIP_ADDONS=true
      shift
      ;;
    --skip-crew)
      SKIP_CREW=true
      shift
      ;;
    *)
      echo "❌ Unknown option: $1"
      echo "Usage: $0 [--force] [--skip-addons] [--skip-crew]"
      echo "  --force        Overwrite existing workspace files (including MEMORY.md)"
      echo "  --skip-addons  Skip apply-addons.sh and setup-crew.sh entirely"
      echo "  --skip-crew    Run apply-addons.sh but skip setup-crew.sh"
      exit 1
      ;;
  esac
done

cd "$PROJECT_ROOT"

echo "🔄 wiseflow — Upgrade"
echo "   Project root: $PROJECT_ROOT"
echo ""

# ─── 1. 验证当前目录是 wiseflow 项目 ──────────────────────────────────
if [ ! -f "$PROJECT_ROOT/scripts/apply-addons.sh" ] || [ ! -d "$OPENCLAW_DIR" ]; then
  echo "❌ This does not look like a wiseflow project directory."
  echo "   Expected: scripts/apply-addons.sh and openclaw/ subdirectory"
  echo "   Please run this script from within your wiseflow project folder."
  exit 1
fi

# ─── 2. 按锚定版本更新 openclaw 引擎（跳过 git 同步）────────────────
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

echo "  📦 Installing dependencies..."
(cd "$OPENCLAW_DIR" && pnpm install)

echo "  🔨 Building..."
(cd "$OPENCLAW_DIR" && pnpm build)

echo "  🎨 Building Control UI assets..."
(cd "$OPENCLAW_DIR" && pnpm ui:build)

echo "  ✅ openclaw engine ready"
OPENCLAW_UPDATED=false
echo ""

# ─── 3. 重新应用 addons + 同步配置（apply-addons.sh 末尾会调 setup-crew.sh）
if [ "$SKIP_ADDONS" = "true" ]; then
  echo "⏭️  Skipping apply-addons and setup-crew (--skip-addons)"
else
  echo "🔄 Applying addons and syncing config..."
  ADDON_ARGS=()
  [ "$FORCE" = "true" ] && ADDON_ARGS+=(--force)
  [ "$SKIP_CREW" = "true" ] && ADDON_ARGS+=(--skip-crew)
  "$PROJECT_ROOT/scripts/apply-addons.sh" "${ADDON_ARGS[@]}"
fi

echo ""
echo "✅ Upgrade complete!"
if [ "$OPENCLAW_UPDATED" = "true" ]; then
  echo "Next steps — openclaw engine was updated; reinstall daemon to refresh service unit:"
  echo "  Production: cd $PROJECT_ROOT && ./scripts/reinstall-daemon.sh --skip-addons"
  echo "  Dev mode:   cd $PROJECT_ROOT && ./scripts/dev.sh gateway"
else
  echo "Next steps — only wiseflow config updated; a simple service restart is enough:"
  echo "  Production: systemctl --user restart openclaw-gateway.service"
  echo "  Dev mode:   cd $PROJECT_ROOT && ./scripts/dev.sh gateway"
fi
