# Wiseflow Addon for OpenClaw

浏览器反检测 + Tab Recovery + 互联网能力增强。

本目录是 [wiseflow](https://github.com/TeamWiseFlow/wiseflow) 提供给 [openclaw-for-business](https://github.com/TeamWiseFlow/openclaw_for_business) 的标准 addon 包。

## 功能

- **Patchright 反检测** — 通过 pnpm overrides 将 `playwright-core` 替换为 `patchright-core`，无需修改上游源码
- **Tab Recovery 补丁** — 浏览器标签页恢复能力
- **Browser Guide 技能** — 教会 agent 处理登录墙、验证码、懒加载、付费墙等场景的最佳实践

## 安装

将本目录复制到 openclaw_for_business 的 `addons/` 目录：

```bash
# 方式一：从 wiseflow 仓库复制
git clone https://github.com/TeamWiseFlow/wiseflow.git /tmp/wiseflow
cp -r /tmp/wiseflow/addon <openclaw_for_business>/addons/wiseflow

# 方式二：如果已有 wiseflow 仓库
cp -r /path/to/wiseflow/addon <openclaw_for_business>/addons/wiseflow
```

安装后重启 openclaw 即可生效（`dev.sh` 会自动扫描并应用）。

## 目录结构

```
addon/
├── addon.json                    # 元数据
├── overrides.sh                  # pnpm overrides: playwright-core → patchright-core
├── patches/
│   └── 001-browser-tab-recovery.patch  # 标签页恢复补丁
├── skills/
│   └── browser-guide/SKILL.md    # 浏览器使用最佳实践
├── docs/                         # 技术文档
│   ├── anti-detection-research.md
│   └── openclaw-extension-architecture.md
└── tests/                        # 测试用例和脚本
    ├── README.md
    └── run-managed-tests.mjs
```

## 三层加载机制

addon 被 `apply-addons.sh` 加载时按以下顺序执行：

1. **overrides.sh** — 运行 pnpm overrides 替换 playwright-core 为 patchright-core（最稳健，不依赖行号）
2. **patches/*.patch** — 应用 git patch（精确代码改动，上游更新时可能需调整）
3. **skills/*/SKILL.md** — 安装自定义技能到 openclaw

## 要求

- OpenClaw >= 2026.2
- pnpm（由 openclaw_for_business 提供）

## 测试

参见 [tests/README.md](tests/README.md) 了解浏览器反检测测试用例。
