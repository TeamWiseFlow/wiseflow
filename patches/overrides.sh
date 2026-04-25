#!/bin/bash
# wiseflow addon - overrides.sh
# 通过 pnpm overrides 将 playwright-core 替换为 patchright-core（反检测）
# 由 apply-addons.sh 调用，接收环境变量：ADDON_DIR, OPENCLAW_DIR
set -e

PATCHRIGHT_VERSION="${PATCHRIGHT_VERSION:-1.59.4}"

# ─── pnpm overrides（核心，不修改源码） ─────────────────────────
echo "    → pnpm override: playwright-core → patchright-core@${PATCHRIGHT_VERSION}"

cd "$OPENCLAW_DIR"
node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
pkg.pnpm = pkg.pnpm || {};
pkg.pnpm.overrides = pkg.pnpm.overrides || {};
pkg.pnpm.overrides['playwright-core'] = 'npm:patchright-core@${PATCHRIGHT_VERSION}';
fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
"

# ─── 文档文本替换（可选，仅影响文档准确性） ────────────────────
DOC_FILES=(
  "Dockerfile"
  "docs/help/faq.md"
  "docs/install/docker.md"
  "docs/tools/browser.md"
  "docs/zh-CN/install/docker.md"
  "docs/zh-CN/tools/browser.md"
  "src/browser/pw-tools-core.snapshot.ts"
  "src/browser/routes/agent.shared.ts"
  "src/dockerfile.test.ts"
)

for file in "${DOC_FILES[@]}"; do
  if [ -f "$file" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
      sed -i '' 's/playwright-core/patchright-core/g' "$file"
    else
      sed -i 's/playwright-core/patchright-core/g' "$file"
    fi
  fi
done

# ─── 禁用内置 web_search 工具（由 smart-search skill 通过浏览器替代） ──────────
# openclaw 加载顺序：CWD/.env → OPENCLAW_STATE_DIR/.env（不覆盖已有值）
# 这里写入 OPENCLAW_STATE_DIR/.env（默认 ~/.openclaw/.env）
OPENCLAW_STATE_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
ENV_FILE="$OPENCLAW_STATE_DIR/.env"
mkdir -p "$OPENCLAW_STATE_DIR"
if ! grep -q "OPENCLAW_DISABLE_WEB_SEARCH" "$ENV_FILE" 2>/dev/null; then
  echo "OPENCLAW_DISABLE_WEB_SEARCH=1" >> "$ENV_FILE"
  echo "    → injected OPENCLAW_DISABLE_WEB_SEARCH=1 into $ENV_FILE"
else
  echo "    → OPENCLAW_DISABLE_WEB_SEARCH already set in $ENV_FILE"
fi
