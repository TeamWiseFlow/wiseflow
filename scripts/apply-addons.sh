#!/bin/bash
# apply-addons.sh - wiseflow 基础能力安装 + addon 加载器
#
# 技能两级体系：
#   - 默认全局 skills: skills/ (项目根目录) → 安装到 ~/.openclaw/skills/ (managed dir)
#   - Addon 额外全局 skills: addons/<name>/skills/ → 安装到 ~/.openclaw/skills/ (managed dir)
#   - Agent 专属 skills: crews/<template>/skills/ → 已由 setup-crew.sh 安装到 workspace
#
# 每次运行时：
#   1. 恢复 openclaw/ 到干净状态
#   2. 应用基础补丁（patches/*.patch）+ 依赖覆盖（patches/overrides.sh）
#   3. 安装默认全局 skills（项目根目录 skills/）
#   4. 扫描 addons/*/ 目录，对每个 addon 依次执行：
#      a. skills/*/SKILL.md — 额外全局 skill 安装
#      b. crew/*/  — Crew 模板安装 + 可选自动实例化
#
# addon 目录结构：
#   addons/<name>/
#   ├── addon.json          # 元数据（名称、版本、描述）
#   ├── skills/*/SKILL.md   # 可选：额外全局技能（所有 Agent 可见）
#   └── crew/               # 可选：Crew 模板
#       └── <template-id>/
#           ├── SOUL.md ... HEARTBEAT.md  # 模板 workspace 文件
#           ├── DENIED_SKILLS             # 可选：屏蔽特定内置 skill
#           └── skills/*/SKILL.md         # 模板专属技能
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CREWS_DIR="$PROJECT_ROOT/crews"
ADDONS_DIR="$PROJECT_ROOT/addons"
OPENCLAW_DIR="$PROJECT_ROOT/openclaw"
OPENCLAW_HOME="$HOME/.openclaw"
CONFIG_PATH="$OPENCLAW_HOME/openclaw.json"
HRBP_ADD_AGENT_SCRIPT="$PROJECT_ROOT/crews/hrbp/skills/hrbp-recruit/scripts/add-agent.sh"
GLOBAL_SHARED_SKILLS_FILE="$OPENCLAW_HOME/GLOBAL_SHARED_SKILLS"
FORCE=false
SKIP_CREW=false
NO_BUILD=false
NO_RESTART=false

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
    --no-build)
      NO_BUILD=true
      shift
      ;;
    --no-restart)
      NO_RESTART=true
      shift
      ;;
    *)
      echo "❌ Unknown option: $1"
      echo "Usage: $0 [--force] [--skip-crew] [--no-build] [--no-restart]"
      exit 1
      ;;
  esac
done

GLOBAL_SHARED_SKILLS_RAW=""
append_global_shared_skill() {
  local skill_name="$1"
  [ -n "$skill_name" ] || return 0
  GLOBAL_SHARED_SKILLS_RAW="${GLOBAL_SHARED_SKILLS_RAW}
$skill_name"
}

NEEDS_INSTALL=false

# ─── 恢复上游到干净状态 ──────────────────────────────────────────
cd "$OPENCLAW_DIR"
git reset --hard HEAD 2>/dev/null || true
# 清理 patches 创建的新文件（reset --hard 不删除 untracked 文件）
git clean -fd -- src/ extensions/ 2>/dev/null || true
cd "$PROJECT_ROOT"

# ─── 应用基础依赖覆盖（patches/overrides.sh） ─────────────────────
if [ -f "$PROJECT_ROOT/patches/overrides.sh" ]; then
  echo "🔧 Applying base overrides..."
  ADDON_DIR="$PROJECT_ROOT/patches" OPENCLAW_DIR="$OPENCLAW_DIR" bash "$PROJECT_ROOT/patches/overrides.sh"
  NEEDS_INSTALL=true
fi

# ─── 应用基础补丁（patches/*.patch，按序号顺序） ─────────────────
PATCHES_DIR="$PROJECT_ROOT/patches"
if ls "$PATCHES_DIR"/*.patch 1>/dev/null 2>&1; then
  echo "🩹 Applying base patches..."
  cd "$OPENCLAW_DIR"
  for patch in $(ls "$PATCHES_DIR"/*.patch | sort); do
    echo "  → $(basename "$patch")"
    git apply --3way --ignore-whitespace --whitespace=fix "$patch" || {
      echo "  ❌ Failed to apply $(basename "$patch")"
      echo "     Hint: 上游代码可能已变更，需重新生成此补丁"
      exit 1
    }
  done
  cd "$PROJECT_ROOT"
  NEEDS_INSTALL=true
fi

# ─── 同步 skills 禁用配置（从 config-templates 到运行配置）──────
if [ -f "$CONFIG_PATH" ] && [ -f "$PROJECT_ROOT/config-templates/openclaw.json" ]; then
  node -e "
    const fs = require('fs');
    const running = JSON.parse(fs.readFileSync('$CONFIG_PATH', 'utf8'));
    const template = JSON.parse(fs.readFileSync('$PROJECT_ROOT/config-templates/openclaw.json', 'utf8'));
    const clone = (value) => {
      if (value && typeof value === 'object') return JSON.parse(JSON.stringify(value));
      return value;
    };
    let changed = false;

    // 同步 skills.entries：
    //   enabled: true  → 强制覆写（wiseflow 功能依赖，必须保证开启）
    //   enabled: false → 仅在运行配置中尚无该条目时写��（首次初始化语义，
    //                    保留用户已主动开启的配置，不回退）
    if (template.skills?.entries) {
      if (!running.skills) running.skills = {};
      if (!running.skills.entries) running.skills.entries = {};
      for (const [name, entry] of Object.entries(template.skills.entries)) {
        if (entry && entry.enabled === true) {
          // 强制写入：确保 wiseflow 依赖的技能始终开启
          running.skills.entries[name] = entry;
          changed = true;
        } else if (!(name in running.skills.entries)) {
          // 首次写入：用户从未配置过此条目才写默认值
          running.skills.entries[name] = entry;
          changed = true;
        }
      }
    }

    // 同步 tools.exec 配置（避免 WSL/Linux 下 sandbox 默认导致 exec 失败）
    if (template.tools?.exec) {
      if (!running.tools) running.tools = {};
      if (!running.tools.exec) running.tools.exec = {};
      for (const [key, value] of Object.entries(template.tools.exec)) {
        running.tools.exec[key] = value;
        changed = true;
      }
    }

    // 同步 session.dmScope 默认值（外部 crew 需要 per-channel-peer 隔离）
    if (template.session?.dmScope) {
      if (!running.session) running.session = {};
      if (running.session.dmScope !== template.session.dmScope) {
        running.session.dmScope = template.session.dmScope;
        changed = true;
      }
    }

    // 同步 hooks.internal.entries 配置（确保 boot-md 等 hook 开关与模板一致）
    if (template.hooks?.internal?.entries) {
      if (!running.hooks) running.hooks = {};
      if (!running.hooks.internal) running.hooks.internal = {};
      if (!running.hooks.internal.entries) running.hooks.internal.entries = {};
      for (const [name, entry] of Object.entries(template.hooks.internal.entries)) {
        running.hooks.internal.entries[name] = entry;
        changed = true;
      }
    }

    // 规范 Feishu 多账号配置：将顶层 single-account 字段下沉到 accounts.*
    // 避免启动时触发 Doctor 迁移提示：
    // \"Moved channels.feishu single-account top-level values into channels.feishu.accounts.default.\"
    const feishu = running.channels?.feishu;
    if (feishu && typeof feishu === 'object' && !Array.isArray(feishu)) {
      const accounts = feishu.accounts;
      if (accounts && typeof accounts === 'object' && !Array.isArray(accounts)) {
        const accountEntries = Object.entries(accounts);
        if (accountEntries.length > 0) {
          const keysToMove = ['dmPolicy', 'allowFrom', 'groupPolicy', 'groupAllowFrom', 'defaultTo'];
          const topLevelValues = {};
          for (const key of keysToMove) {
            if (feishu[key] !== undefined) topLevelValues[key] = feishu[key];
          }
          if (Object.keys(topLevelValues).length > 0) {
            const nextAccounts = {};
            for (const [accountId, rawAccount] of accountEntries) {
              const account =
                rawAccount && typeof rawAccount === 'object' && !Array.isArray(rawAccount)
                  ? { ...rawAccount }
                  : {};
              for (const [key, value] of Object.entries(topLevelValues)) {
                if (account[key] === undefined) account[key] = clone(value);
              }
              nextAccounts[accountId] = account;
            }
            for (const key of Object.keys(topLevelValues)) {
              delete feishu[key];
            }
            feishu.accounts = nextAccounts;
            changed = true;
          }
        }
      }
    }

    if (changed) {
      fs.writeFileSync('$CONFIG_PATH', JSON.stringify(running, null, 2) + '\n');
    }
  "
  echo "📝 Skills configuration synchronized"
fi

# ─── 注入 awada 扩展路径（绝对路径，避免 CWD 依赖）──────────────
AWADA_EXT="$PROJECT_ROOT/awada/awada-extension"
if [ -d "$AWADA_EXT" ] && [ -f "$AWADA_EXT/openclaw.plugin.json" ]; then
  if [ -f "$CONFIG_PATH" ]; then
    node -e "
      const fs = require('fs');
      const config = JSON.parse(fs.readFileSync('$CONFIG_PATH', 'utf8'));
      if (!config.plugins) config.plugins = {};
      if (!config.plugins.load) config.plugins.load = {};
      if (!Array.isArray(config.plugins.load.paths)) config.plugins.load.paths = [];
      const awadaPath = '$AWADA_EXT';
      // 先移除所有结尾匹配 awada/awada-extension 的旧路径（跨机器迁移时清理残留）
      config.plugins.load.paths = config.plugins.load.paths.filter(
        p => !p.endsWith('awada/awada-extension')
      );
      config.plugins.load.paths.push(awadaPath);
      if (!config.plugins.entries) config.plugins.entries = {};
      if (!config.plugins.entries.awada) {
        config.plugins.entries.awada = { enabled: false };
      }
      fs.writeFileSync('$CONFIG_PATH', JSON.stringify(config, null, 2) + '\n');
    "
    echo "📝 Awada extension path injected"
  fi
fi


# ─── 安装全局共享技能（项目根目录 skills/） ──────────────────────
GLOBAL_SKILL_COUNT=0
if [ -d "$PROJECT_ROOT/skills" ]; then
  mkdir -p "$OPENCLAW_HOME/skills"
  for skill_dir in "$PROJECT_ROOT"/skills/*/; do
    if [ -f "${skill_dir}SKILL.md" ]; then
      skill_name="$(basename "$skill_dir")"
      rm -rf "$OPENCLAW_HOME/skills/$skill_name"
      cp -r "${skill_dir%/}" "$OPENCLAW_HOME/skills/$skill_name"
      GLOBAL_SKILL_COUNT=$((GLOBAL_SKILL_COUNT + 1))
      append_global_shared_skill "$skill_name"
    fi
  done
fi
if [ "$GLOBAL_SKILL_COUNT" -gt 0 ]; then
  echo "📦 Global skills installed ($GLOBAL_SKILL_COUNT)"
fi

# ─── 扫描并加载 addons ──────────────────────────────────────────
if [ ! -d "$ADDONS_DIR" ]; then
  mkdir -p "$ADDONS_DIR"
fi

ADDON_COUNT=0

for addon_dir in "$ADDONS_DIR"/*/; do
  [ -d "$addon_dir" ] || continue

  addon_name="$(basename "$addon_dir")"

  # 跳过没有 addon.json 的目录
  if [ ! -f "$addon_dir/addon.json" ]; then
    echo "⚠️  Skipping $addon_name (no addon.json)"
    continue
  fi

  echo "📦 Loading addon: $addon_name"
  ADDON_COUNT=$((ADDON_COUNT + 1))

  # ─── 第一层：全局 skills 安装 ──────────────────────────────────
  if [ -d "$addon_dir/skills" ]; then
    echo "  📚 Installing global skills..."
    mkdir -p "$OPENCLAW_HOME/skills"
    for skill_dir in "$addon_dir"/skills/*/; do
      if [ -f "${skill_dir}SKILL.md" ]; then
        skill_name="$(basename "$skill_dir")"
        echo "    → $skill_name (global)"
        rm -rf "$OPENCLAW_HOME/skills/$skill_name"
        cp -r "${skill_dir%/}" "$OPENCLAW_HOME/skills/$skill_name"
        append_global_shared_skill "$skill_name"
      fi
    done
  fi

  # ─── 第二层：Crew 模板安装（crew/ → crews/） ─────────────────
  if [ -d "$addon_dir/crew" ]; then
    echo "  🤖 Installing crew templates..."

    # 从 addon.json 读取 internal_crews / external_crews 数组（crew-type 的唯一权威来源）
    # addon 模板的 SOUL.md 不要求包含 crew-type 字段；若包含则被此声明覆盖
    addon_crew_lists="$(node -e "
      try {
        const a = JSON.parse(require('fs').readFileSync('${addon_dir}addon.json','utf8'));
        const i = Array.isArray(a.internal_crews) ? a.internal_crews : [];
        const e = Array.isArray(a.external_crews) ? a.external_crews : [];
        console.log(JSON.stringify({ internal: i, external: e }));
      } catch(err) { console.log(JSON.stringify({ internal: [], external: [] })); }
    " 2>/dev/null || echo '{"internal":[],"external":[]}')"

    for template_ws in "$addon_dir"/crew/*/; do
      [ -d "$template_ws" ] || continue
      # 需要至少有 SOUL.md 才算有效的模板
      [ -f "${template_ws}SOUL.md" ] || continue

      template_id="$(basename "$template_ws")"

      # 从 addon.json 的 internal_crews / external_crews 数组确定 crew-type
      addon_crew_type="$(ADDON_CREW_LISTS="$addon_crew_lists" node -e "
        const { internal, external } = JSON.parse(process.env.ADDON_CREW_LISTS);
        const id = '$template_id';
        if (internal.includes(id) && external.includes(id)) console.log('CONFLICT');
        else if (internal.includes(id)) console.log('internal');
        else if (external.includes(id)) console.log('external');
        else console.log('');
      " 2>/dev/null || echo "")"

      if [ "$addon_crew_type" = "CONFLICT" ]; then
        echo "    ❌ template $template_id listed in both internal_crews and external_crews"
        exit 1
      elif [ -z "$addon_crew_type" ]; then
        echo "    ⚠️  template $template_id not in internal_crews or external_crews, defaulting to external"
        addon_crew_type="external"
      fi

      echo "    → $template_id (crew-type: $addon_crew_type)"

      # 安装/更新模板到 crews/（每次覆盖，确保升级时同步最新内容）
      template_dest="$CREWS_DIR/$template_id"
      rm -rf "$template_dest"
      cp -r "${template_ws%/}" "$template_dest"
      echo "    ✅ template $template_id synced to crews/"

      # 在 crews/ 中的 SOUL.md 上覆盖或注入 crew-type（addon.json 声明为权威来源）
      # 确保 setup-crew.sh 重扫 crews/ 时能正确路由到 crew_templates/ 或 hrbp_templates/
      if [ -f "$template_dest/SOUL.md" ]; then
        if grep -q '^crew-type:' "$template_dest/SOUL.md" 2>/dev/null; then
          sed -i.bak "s/^crew-type:.*$/crew-type: $addon_crew_type/" "$template_dest/SOUL.md" && rm -f "$template_dest/SOUL.md.bak"
        else
          printf '\ncrew-type: %s\n' "$addon_crew_type" >> "$template_dest/SOUL.md"
        fi
      fi

      # 同步到运行时模板目录（按 crew-type 分路由）
      if [ "$addon_crew_type" = "internal" ]; then
        # 对内 Crew → crew_templates/（Main Agent 访问）
        mkdir -p "$OPENCLAW_HOME/crew_templates"
        runtime_template_dir="$OPENCLAW_HOME/crew_templates/$template_id"
        rm -rf "$runtime_template_dir"
        cp -r "$template_ws" "$runtime_template_dir"
        echo "    ✅ synced to crew_templates/ (internal)"
      else
        # 对外 Crew → hrbp_templates/（HRBP 访问）
        mkdir -p "$OPENCLAW_HOME/hrbp_templates"
        runtime_template_dir="$OPENCLAW_HOME/hrbp_templates/$template_id"
        rm -rf "$runtime_template_dir"
        cp -r "$template_ws" "$runtime_template_dir"
        echo "    ✅ synced to hrbp_templates/ (external)"
      fi

      # 可选自动实例化（addon.json 中 auto-activate: true）
      auto_activate="$(node -e "
        const a = JSON.parse(require('fs').readFileSync('$addon_dir/addon.json','utf8'));
        console.log(a['auto-activate'] === true ? 'true' : 'false');
      " 2>/dev/null || echo "false")"

      if [ "$auto_activate" = "true" ]; then
        agent_id="$template_id"
        dest="$OPENCLAW_HOME/workspace-$agent_id"

        if [ -d "$dest" ]; then
          echo "    ⚠️  workspace-$agent_id already exists, skipping auto-activate"
          # 对外 Crew：幂等同步 DECLARED_SKILLS（仅追加模板中有但 workspace 缺失的技能）
          if [ "$addon_crew_type" = "external" ] \
              && [ -f "${template_ws}DECLARED_SKILLS" ] \
              && [ -f "$dest/DECLARED_SKILLS" ]; then
            _added=0
            while IFS= read -r _skill; do
              [ -n "$_skill" ] || continue
              grep -qxF "$_skill" "$dest/DECLARED_SKILLS" 2>/dev/null || {
                echo "$_skill" >> "$dest/DECLARED_SKILLS"
                _added=$((_added + 1))
              }
            done < <(
              sed 's/#.*$//' "${template_ws}DECLARED_SKILLS" \
                | tr ',' '\n' \
                | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' \
                | awk 'NF'
            )
            [ "$_added" -gt 0 ] && echo "    📝 DECLARED_SKILLS: synced $_added new skill(s) from template"
          fi
        else
          mkdir -p "$dest"
          cp "${template_ws}"*.md "$dest/"
          # 同步 crew-type 到 workspace 的 SOUL.md（addon.json 声明为准）
          if [ -f "$dest/SOUL.md" ]; then
            if grep -q '^crew-type:' "$dest/SOUL.md" 2>/dev/null; then
              sed -i.bak "s/^crew-type:.*$/crew-type: $addon_crew_type/" "$dest/SOUL.md" && rm -f "$dest/SOUL.md.bak"
            else
              printf '\ncrew-type: %s\n' "$addon_crew_type" >> "$dest/SOUL.md"
            fi
          fi
          if [ -f "${template_ws}ALLOWED_COMMANDS" ]; then
            if [ ! -f "$dest/ALLOWED_COMMANDS" ]; then
              cp "${template_ws}ALLOWED_COMMANDS" "$dest/"
            else
              while IFS= read -r line; do
                [[ "$line" =~ ^\+ ]] || continue
                grep -qxF "$line" "$dest/ALLOWED_COMMANDS" || echo "$line" >> "$dest/ALLOWED_COMMANDS"
              done < "${template_ws}ALLOWED_COMMANDS"
            fi
          fi
          if [ -f "${template_ws}DENIED_SKILLS" ]; then
            cp "${template_ws}DENIED_SKILLS" "$dest/"
          fi
          # 对外 Crew：复制 DECLARED_SKILLS 和创建 feedback/ 目录
          if [ "$addon_crew_type" = "external" ]; then
            if [ -f "${template_ws}DECLARED_SKILLS" ]; then
              cp "${template_ws}DECLARED_SKILLS" "$dest/"
            fi
            mkdir -p "$dest/feedback"
          fi
          # 复制共享协议
          if [ -d "$CREWS_DIR/shared" ]; then
            cp "$CREWS_DIR/shared/"*.md "$dest/"
          fi
          # 复制模板专属 skills（如有）
          if [ -d "${template_ws}skills" ]; then
            cp -r "${template_ws}skills" "$dest/"
          fi
          echo "    ✅ workspace-$agent_id auto-activated"

          # 注册 agent（如果尚未注册）
          if [ -f "$CONFIG_PATH" ]; then
            if ! node -e "
              const c = JSON.parse(require('fs').readFileSync('$CONFIG_PATH','utf8'));
              process.exit((c.agents?.list || []).some(a => a.id === '$agent_id') ? 0 : 1);
            " 2>/dev/null; then
              if [ ! -f "$HRBP_ADD_AGENT_SCRIPT" ]; then
                echo "    ❌ HRBP add-agent script not found: $HRBP_ADD_AGENT_SCRIPT"
                exit 1
              fi
              # 根据 crew-type 传入对应参数
              "$HRBP_ADD_AGENT_SCRIPT" "$agent_id" --crew-type "$addon_crew_type"
              echo "    ✅ agent $agent_id registered (crew-type: $addon_crew_type)"
            fi
          fi
        fi
      else
        echo "    📋 template $template_id ready (use HRBP/Main Agent to instantiate)"
      fi
    done
  fi
  echo "  ✅ $addon_name loaded"
done

# 有 overrides 或 patches 时才需要同步依赖
if [ "$NEEDS_INSTALL" = "true" ]; then
  echo "📦 Syncing dependencies..."
  cd "$OPENCLAW_DIR"
  pnpm install --frozen-lockfile=false
  cd "$PROJECT_ROOT"
fi

if [ "$ADDON_COUNT" -gt 0 ]; then
  echo "✅ All addons applied ($ADDON_COUNT loaded)"
else
  echo "📦 No addons found"
fi

# ─── 写入全局共享 skills 清单（供 skills allowlist 计算使用） ──────
mkdir -p "$OPENCLAW_HOME"
printf '%s\n' "$GLOBAL_SHARED_SKILLS_RAW" \
  | awk 'NF && !seen[$0]++' \
  | sort > "$GLOBAL_SHARED_SKILLS_FILE"
GLOBAL_SHARED_COUNT="$(wc -l < "$GLOBAL_SHARED_SKILLS_FILE" | tr -d ' ')"
echo "🧾 Global shared skills catalog updated ($GLOBAL_SHARED_COUNT)"

# ─── 重新同步 agents.list[].skills（纳入最新全局 skills）──────────
if [ "$SKIP_CREW" = "true" ]; then
  echo "⏭️  Skipping setup-crew.sh (--skip-crew)"
elif [ -f "$CONFIG_PATH" ] && [ -x "$PROJECT_ROOT/scripts/setup-crew.sh" ]; then
  if [ "$FORCE" = "true" ]; then
    CALLED_FROM_APPLY_ADDONS=true "$PROJECT_ROOT/scripts/setup-crew.sh" --force
  else
    CALLED_FROM_APPLY_ADDONS=true "$PROJECT_ROOT/scripts/setup-crew.sh"
  fi
fi

# ─── 编译 dist（patches 改的是源码，需要 build 才能生效） ──────────
if [ "$NO_BUILD" = "true" ]; then
  echo "⏭️  Skipping pnpm build (--no-build)"
elif [ "$NEEDS_INSTALL" = "true" ]; then
  echo "🔨 Building openclaw (patches applied, dist needs refresh)..."
  cd "$OPENCLAW_DIR"
  pnpm build
  cd "$PROJECT_ROOT"
  echo "✅ Build complete"
fi

# ─── 重启 gateway service（如果正在运行） ─────────────────────────
if [ "$NO_RESTART" = "true" ]; then
  echo "⏭️  Skipping gateway restart (--no-restart)"
elif [ "$(uname -s)" = "Linux" ] && command -v systemctl >/dev/null 2>&1; then
  SERVICE_NAME="openclaw-gateway"
  if systemctl --user is-active "$SERVICE_NAME.service" >/dev/null 2>&1; then
    echo "🔄 Restarting $SERVICE_NAME.service..."
    systemctl --user restart "$SERVICE_NAME.service"
    echo "✅ Gateway restarted"
  fi
fi
