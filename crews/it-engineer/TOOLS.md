# IT Engineer Agent — Tools

## 可用工具

### 通用工具
- 文件读写：读取日志、配置文件，修改 workspace 文件
- Shell 执行：运行系统命令、检查状态、查看日志

### WiseFlow 内置脚本（需先 cd 到 WiseFlow 项目目录再执行）

> WiseFlow 项目路径见同目录的 `OFB_ENV.md`（历史命名保留，每次 `setup-crew.sh` 自动更新，里面有完整命令）。

```bash
# 开发模式前台启动（含日志输出）
cd <WISEFLOW_PROJECT_ROOT> && ./scripts/dev.sh gateway

# 生产模式重新安装后台服务
cd <WISEFLOW_PROJECT_ROOT> && ./scripts/reinstall-daemon.sh

# 重新同步 crew 配置（幂等，安全执行）
cd <WISEFLOW_PROJECT_ROOT> && ./scripts/setup-crew.sh

# 重新应用 addons
cd <WISEFLOW_PROJECT_ROOT> && ./scripts/apply-addons.sh
```

> ⚠️ **禁止直接运行 `openclaw` 命令**（`openclaw` 不在系统 PATH 中）。
> 如需直接调用上游 CLI，必须在 `openclaw/` 子目录内通过 `pnpm openclaw` 执行：
> ```bash
> cd <WISEFLOW_PROJECT_ROOT>/openclaw && pnpm openclaw <subcommand>
> ```

### 检查系统运行状态

```bash
# 检查 openclaw 进程是否存活
ps aux | grep 'dist/index.js gateway' | grep -v grep

# 查看 pm2 管理的进程（生产模式）
pm2 list
pm2 logs openclaw --lines 50

# 检查配置文件完整性
node -e "require('fs').readFileSync(process.env.HOME + '/.openclaw/openclaw.json', 'utf8'); console.log('✅ Config OK')"
```

### GitHub / 代码相关（需已启用 github、gh-issues、coding-agent 技能）
- `github`：读取 WiseFlow 和 OpenClaw 仓库的最新信息（commits、releases、README）
- `gh-issues`：查看 WiseFlow 和 OpenClaw 的 issue，了解已知问题和修复状态
- `coding-agent`：用于分析代码问题、生成配置文件、解读报错信息


## 工具使用规则

1. **备份重要文件**：修改 `~/.openclaw/openclaw.json` 前，先备份
2. **脚本优先**：优先使用 WiseFlow 内置脚本，不要直接操作 `openclaw/` 目录下的代码
3. **日志是第一线索**：遇到问题先查日志，再猜原因
4. **验证结果**：每次操作后确认效果（如重启后检查服务是否正常运行）

## SEO 技术工具

```
# Lighthouse 性能/SEO 评分（需要 Chrome）
npx lighthouse https://yoursite.com --only-categories=performance,seo --output json

# sitemap 验证（检查格式和可访问性）
curl -sf https://yoursite.com/sitemap.xml | python3 -c "import sys; import xml.etree.ElementTree as ET; ET.parse(sys.stdin); print('✅ sitemap valid')"

# robots.txt 检查
curl -sf https://yoursite.com/robots.txt

# 内链/外链状态检测（使用 xurl 技能或 curl 批量检查）
curl -o /dev/null -s -w "%{http_code}" https://yoursite.com/some-page

# Google Search Console（通过浏览器访问，或使用 GSC API）
# API 文档：https://developers.google.com/webmaster-tools/v1/api_reference_index
```

| 工具 | 用途 |
|------|------|
| `smart-search` | 搜索 SEO 最佳实践、查找竞品技术方案 |
| `coding-agent` | 生成 sitemap.xml、JSON-LD Schema、robots.txt 内容 |