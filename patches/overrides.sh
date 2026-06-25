#!/bin/bash
# wiseflow addon - overrides.sh
# 通过 pnpm overrides 将 playwright-core 替换为 patchright-core（反检测）
# 由 apply-addons.sh 调用，接收环境变量：ADDON_DIR, OPENCLAW_DIR
set -e

PATCHRIGHT_VERSION="${PATCHRIGHT_VERSION:-1.60.2}"

# ─── pnpm overrides（核心，不修改源码） ─────────────────────────
# pnpm v11+ 不再从 package.json 的 pnpm.overrides 读取覆盖设置，
# 改为写入 pnpm-workspace.yaml 的 overrides 字段。
echo "    → pnpm override: playwright-core → patchright-core@${PATCHRIGHT_VERSION}"

cd "$OPENCLAW_DIR"
WORKSPACE_YAML="pnpm-workspace.yaml"
if [ -f "$WORKSPACE_YAML" ]; then
  # pnpm v11+: 写入 pnpm-workspace.yaml overrides
  node -e "
    const fs = require('fs');
    const yaml = fs.readFileSync('$WORKSPACE_YAML', 'utf8');
    const overrideLine = '  playwright-core: \"npm:patchright-core@${PATCHRIGHT_VERSION}\"';
    // 移除旧的 playwright-core override（如有）
    const cleaned = yaml.replace(/  playwright-core:.*\n?/, '');
    // 在 overrides: 行后插入
    const patched = cleaned.replace(/^(overrides:\n)/, \"\$1\" + overrideLine + '\n');
    fs.writeFileSync('$WORKSPACE_YAML', patched);
  "
  echo "    → written to $WORKSPACE_YAML"
else
  # 兜底：旧版 pnpm 写入 package.json
  node -e "
    const fs = require('fs');
    const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    pkg.pnpm = pkg.pnpm || {};
    pkg.pnpm.overrides = pkg.pnpm.overrides || {};
    pkg.pnpm.overrides['playwright-core'] = 'npm:patchright-core@${PATCHRIGHT_VERSION}';
    fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
  "
  echo "    → written to package.json (legacy pnpm)"
fi

# 清理 package.json 中可能残留的旧 pnpm.overrides（pnpm v11 会发出 WARN）
node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
if (pkg.pnpm && pkg.pnpm.overrides) {
  delete pkg.pnpm.overrides;
  if (Object.keys(pkg.pnpm).length === 0) delete pkg.pnpm;
  fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
  console.log('    → cleaned stale pnpm.overrides from package.json');
}
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
