#!/bin/bash
# wiseflow addon - overrides.sh
# 通过 pnpm overrides 将 playwright-core 替换为 patchright-core（反检测）
# 由 apply-addons.sh 调用，接收环境变量：ADDON_DIR, OPENCLAW_DIR
set -e

PATCHRIGHT_VERSION="${PATCHRIGHT_VERSION:-1.57.0}"

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
