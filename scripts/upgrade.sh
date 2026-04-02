#!/bin/bash
# upgrade.sh - 一键升级 wiseflow（自身代码 + openclaw 引擎 + 配置同步）
#
# 适用场景：
#   - 通过 release 包安装的用户（首次运行会自动 git init）
#   - git clone 安装的用户（直接拉取最新代码）
#
# 执行流程：
#   1. 验证 wiseflow 项目目录合法性
#   2. 初始化 git remote（如未初始化）或验证 remote URL
#   3. git fetch + reset --hard 拉取最新 wiseflow 代码
#      - addons/ 在 .gitignore 中，不受影响
#      - ~/.openclaw/ 在 wiseflow 项目目录外，不受影响
#   4. 读取 openclaw.version，按锚定版本检出 openclaw 子目录
#      - 若已是目标 commit，跳过耗时的 install/build
#   5. 调用 apply-addons.sh（内含 setup-crew.sh，只需调一次）
#
# ⚠️  升级前请确保系统空闲（无 agent 会话正在处理任务）
set -e

OFB_REPO="https://github.com/TeamWiseFlow/wiseflow.git"
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
      *) echo "  Aborted. To use the official repo:"; echo "    git remote set-url origin $OFB_REPO"; exit 0 ;;
    esac
  fi
fi

# ─── 3. 拉取最新 wiseflow 代码 ────────────────────────────────────────
echo "📥 Fetching latest wiseflow code..."
git fetch origin master

COMMITS_BEHIND="$(git rev-list HEAD..origin/master --count 2>/dev/null || echo "?")"
if [ "$COMMITS_BEHIND" = "0" ]; then
  echo "  ✅ wiseflow code is already up to date."
  OFB_UPDATED=false
else
  echo "  📊 $COMMITS_BEHIND new commit(s) available"
  git reset --hard origin/master
  echo "  ✅ wiseflow code updated"
  OFB_UPDATED=true
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
  echo "  ✅ openclaw is already at target commit, skipping install/build."
  OPENCLAW_UPDATED=false
else
  echo "  Current commit: ${CURRENT_COMMIT:-"(unknown)"}"
  echo "  Checking out target commit..."
  git -C "$OPENCLAW_DIR" reset --hard HEAD 2>/dev/null || true
  # 对于 shallow clone，需要带 --tags 确保 target commit 的 tree 对象被下载
  git -C "$OPENCLAW_DIR" fetch origin --tags
  # 若仍无法读取 tree（blobless/treeless clone），进一步 unshallow
  if ! git -C "$OPENCLAW_DIR" cat-file -e "${OPENCLAW_COMMIT}^{tree}" 2>/dev/null; then
    echo "  ⚠️  Shallow clone detected, unshallowing to fetch full objects..."
    git -C "$OPENCLAW_DIR" fetch --unshallow origin 2>/dev/null || \
      git -C "$OPENCLAW_DIR" fetch --deepen=200 origin
  fi
  git -C "$OPENCLAW_DIR" checkout "$OPENCLAW_COMMIT"
  echo "  ✅ openclaw checked out at $OPENCLAW_VERSION"

  echo "  📦 Installing dependencies..."
  (cd "$OPENCLAW_DIR" && pnpm install)

  echo "  🔨 Building..."
  (cd "$OPENCLAW_DIR" && pnpm build)

  echo "  ✅ openclaw engine ready"
  OPENCLAW_UPDATED=true
fi
echo ""

# ─── 5. 重新应用 addons + 同步配置（apply-addons.sh 末尾会调 setup-crew.sh）
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
