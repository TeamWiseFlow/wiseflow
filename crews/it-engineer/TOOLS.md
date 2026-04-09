# IT Engineer Agent — Tools

## 可用工具

### 通用工具
- 文件读写：读取日志、配置文件，修改 workspace 文件
- Shell 执行：运行系统命令、检查状态、查看日志

### wiseflow 内置脚本（需先 cd 到项目目录再执行）

> wiseflow 项目路径见同目录的 `OFB_ENV.md`（每次 `setup-crew.sh` 自动更新，里面有完整命令）。

```bash
# 开发模式前台启动（含日志输出）
cd <PROJECT_ROOT> && ./scripts/dev.sh gateway

# 生产模式重新安装后台服务
cd <PROJECT_ROOT> && ./scripts/reinstall-daemon.sh

# 重新同步 crew 配置（幂等，安全执行）
cd <PROJECT_ROOT> && ./scripts/setup-crew.sh

# 重新应用 addons
cd <PROJECT_ROOT> && ./scripts/apply-addons.sh

# 升级 wiseflow 系统（执行前必须确认系统空闲）
cd <PROJECT_ROOT> && ./scripts/upgrade.sh
```

> ⚠️ **禁止直接运行 `openclaw` 命令**（`openclaw` 不在系统 PATH 中）。
> 如需直接调用上游 CLI，必须在 `openclaw/` 子目录内通过 `pnpm openclaw` 执行：
> ```bash
> cd <PROJECT_ROOT>/openclaw && pnpm openclaw <subcommand>
> ```

### 检查系统运行状态

```bash
# 检查 openclaw 进程是否存活
ps aux | grep openclaw.mjs | grep -v grep

# 查看 pm2 管理的进程（生产模式）
pm2 list
pm2 logs openclaw --lines 50

# 检查配置文件完整性
node -e "require('fs').readFileSync(process.env.HOME + '/.openclaw/openclaw.json', 'utf8'); console.log('✅ Config OK')"
```

### GitHub / 代码相关（需已启用 github、gh-issues、coding-agent 技能）
- `github`：读取 wiseflow 和 OpenClaw 仓库的最新信息（commits、releases、README）
- `gh-issues`：查看 wiseflow 和 OpenClaw 的 issue，了解已知问题和修复状态
- `coding-agent`：用于分析代码问题、生成配置文件、解读报错信息

### 查阅其他 Agent 的 Session 历史

> ⚠️ **禁止使用 `sessions_send`/`sessions_list`/`sessions_history`/`sessions_status` 等技能命令查询其他 agent 的 session**——这些命令仅限当前自身 agent 使用。

如需查阅其他 agent 的对话历史（例如用于持续改进分析），直接读取本地文件：

```bash
# 查看某 agent 的 session 索引（含所有 session 的元数据）
cat ~/.openclaw/agents/<agentId>/sessions/sessions.json

# 查看某条 session 的完整对话记录（JSONL 格式，每行一条消息）
cat ~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl
```

- `sessions.json`：JSON 对象，key = session key（如 `agent:cs-001:awada:direct:user123`），value = session 元数据
- `<sessionId>.jsonl`：完整对话内容，逐条 JSON 行，包含 role/content/timestamp 等字段
- 归档的 session transcript：`~/.openclaw/agents/<agentId>/sessions/` 下的 `.archived/` 目录

## 工具使用规则

1. **备份重要文件**：修改 `~/.openclaw/openclaw.json` 前，先备份
2. **脚本优先**：优先使用 wiseflow 内置脚本，不要直接操作 `openclaw/` 目录下的代码
3. **日志是第一线索**：遇到问题先查日志，再猜原因
4. **验证结果**：每次操作后确认效果（如重启后检查服务是否正常运行）

### SEO 技术工具

```bash
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
| `xurl` | 直接访问 GSC API、PageSpeed API、结构化数据测试 API |
| `coding-agent` | 生成 sitemap.xml、JSON-LD Schema、robots.txt 内容 |
