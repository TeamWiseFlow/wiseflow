#!/usr/bin/env python3
"""Export main/public skills with scripts and explicit WorkBuddy adaptations."""
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

from adapt_workflows import adapt_workflow

ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / 'workbuddy'
EXPERT = PRODUCT / 'expert'
SKILLS = EXPERT / 'skills'
SPEC = json.loads((PRODUCT / 'native-skills.json').read_text())
VERSION = SPEC['version']
RELAY_SETUP_MESSAGE = '当前功能需要 relay 服务，OFB_KEY 尚未配置。请到 https://openclaw-for-business.com/ 查看接入说明，再通过 xiaobei-runtime 的私有配置流程继续。'


def remove_functions(text, names):
    tree = ast.parse(text)
    ranges = [(n.lineno - 1, n.end_lineno) for n in tree.body
              if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in names]
    lines = text.splitlines(keepends=True)
    for start, end in sorted(ranges, reverse=True):
        del lines[start:end]
    return ''.join(lines)


def replace_once(text, before, after):
    if text.count(before) != 1:
        raise ValueError(f'Native adaptation needs review: {before[:80]}')
    return text.replace(before, after)


def adapt(path, text):
    changes = []
    if path.endswith('.py'):
        original = text
        for node in ast.walk(ast.parse(original)):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and 'OFB_KEY 未配置。OFB_KEY 是 VIP Club' in node.value:
                text = text.replace(ast.get_source_segment(original, node), json.dumps(RELAY_SETUP_MESSAGE, ensure_ascii=False))
                changes.append('relay-setup-on-demand')
    elif path.endswith(('.ts', '.js', '.mjs')):
        old = 'OFB_KEY 未配置。OFB_KEY 是 VIP Club 会员凭证，由 ofb 掌柜签发——请向 ofb 掌柜索取该 key，交由 IT engineer 写入 daemon.env 后重启实例。'
        if old in text:
            text = text.replace(old, RELAY_SETUP_MESSAGE)
            changes.append('relay-setup-on-demand')
    text = text.replace('默认指向官方中转 relay（VIP Club 会员默认走我们中转，零配置起手）。', '默认指向现有官方 relay，接入凭证由运行层配置。')
    text, changed = re.subn(r'(?<![A-Za-z0-9_.-])\.openclaw(?![A-Za-z0-9_-])', '.xiaobei-workbuddy', text)
    if changed:
        changes.append('isolated-state-home')
    if path.endswith('.py'):
        pattern = r'''Path\.home\(\)\s*/\s*(["'])(\.xiaobei-workbuddy(?:/[^"']*)?)\1'''
        def state_path(match):
            suffix = match.group(2)[len('.xiaobei-workbuddy'):].lstrip('/')
            base = 'Path(os.environ.get("XIAOBEI_WORKBUDDY_HOME", Path.home() / ".xiaobei-workbuddy"))'
            return '(' + base + (' / ' + json.dumps(suffix) if suffix else '') + ')'
        text, count = re.subn(pattern, state_path, text)
        if count:
            tree = ast.parse(text)
            if not any(isinstance(n, ast.Import) and any(a.name == 'os' for a in n.names) for n in tree.body):
                first = next(n for n in tree.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)) and not (isinstance(n, ast.ImportFrom) and n.module == '__future__'))
                lines = text.splitlines(keepends=True)
                lines.insert(first.lineno - 1, 'import os\n')
                text = ''.join(lines)
            changes.append('configurable-private-state')
    if path == 'expert-wx-mp/tools/wx-mp-publisher/scripts/publish_wx_mp.py':
        node = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == '_detect_crew_workspace')
        lines = text.splitlines(keepends=True)
        lines[node.lineno - 1:node.end_lineno] = ['def _detect_crew_workspace() -> Path:\n', '    return Path(os.environ["XIAOBEI_WORKSPACE"])\n']
        text = ''.join(lines)
        changes.append('publisher-theme-workspace')
    if path in ('pitch-deck/scripts/html_to_longimage.py', 'pitch-deck/scripts/html_to_pptx.py'):
        text = replace_once(text, 'pw.chromium.launch(headless=True)', 'pw.chromium.launch(headless=True, executable_path=os.environ.get("CHROME_BIN") or None)')
        changes.append('runtime-chromium-path')
    if path == '_shared/volc_asr.py':
        text = replace_once(text, 'os.path.expanduser("~/.xiaobei-workbuddy/.env")', 'os.path.join(os.environ.get("XIAOBEI_WORKBUDDY_HOME", os.path.expanduser("~/.xiaobei-workbuddy")), ".env")')
        changes.append('configurable-private-env-file')
    if path.endswith('.sh') and any(path.startswith(p) for p in
        ('published-track/scripts/', 'content-calibrator/scripts/', 'expert-bd/tools/bd-record/scripts/', 'expert-ir/tools/ir-record/scripts/')):
        text, count = re.subn(r'^(ROOT|WORKSPACE|WORKSPACE_DIR)=.*$',
                             r'\1="${XIAOBEI_WORKSPACE:?WorkBuddy workspace required}"', text, flags=re.M)
        if count:
            changes.append('workspace-environment')
    if path == 'published-track/scripts/platform-status.py':
        text = replace_once(text, "workspace = Path(os.path.abspath(Path(__file__).parent / '../../..'))",
                            "workspace = Path(os.environ['XIAOBEI_WORKSPACE'])")
        changes.append('workspace-environment')
    if path == 'talking-head-cut/scripts/cut_plan.py':
        text = replace_once(text, 'Path(__file__).resolve().parents[5] / "skills" / "_shared"',
                            'Path(__file__).resolve().parents[2] / "_shared"')
        changes.append('packaged-shared-asr')
    if path == 'viral-chaser/scripts/transcriber.ts':
        text = replace_once(text, '../../../../../skills/_shared/asr.py', '../../_shared/asr.py')
        changes.append('packaged-shared-asr')
    if path == 'aigc-video-gen/aigc-video-gen.sh':
        text = replace_once(text, "mapfile -d '' -t CLEAN_ARGS < <(strip_platform \"$@\")",
                            "CLEAN_ARGS=()\nwhile IFS= read -r -d '' arg; do CLEAN_ARGS+=(\"$arg\"); done < <(strip_platform \"$@\")")
        changes.append('bash-3-compatible-argv')
    if path == 'native-ui-card/scripts/render.py':
        text = remove_functions(text, {'camoufox_call', 'camoufox_render', 'find_chrome'})
        start = text.index('    chrome = find_chrome(')
        end = text.index('    output.parent.mkdir', start)
        text = text[:start] + "    chrome = os.environ.get('CHROME_BIN') or shutil.which('google-chrome') or shutil.which('chromium') or shutil.which('chromium-browser')\n    if not chrome:\n        raise RuntimeError('Chromium 未准备好；通过 xiaobei-runtime setup 安装本地渲染依赖')\n" + text[end:]
        text = replace_once(text, '                    camoufox_render(session, path, stage / f"{name}.png")',
                            "                    raise RuntimeError('Chromium unavailable')")
        text = replace_once(text, '        if session:\n            subprocess.run(["camoufox-cli", "--session", session, "--json", "close"], capture_output=True, timeout=15)',
                            '        pass')
        changes.append('chromium-only-rendering')
    if path == 'platform-runtime/scripts/backend.mjs':
        start = text.index('  else if (platforms[platform].session) {')
        end = text.index('  if (!value)', start)
        text = text[:start] + '  else value = process.env.HTTPS_PROXY || process.env.HTTP_PROXY;\n' + text[end:]
        changes.append('explicit-api-proxy-only')
    if path == 'platform-runtime/scripts/cli.mjs':
        text = replace_once(text, "'call', 'login', 'login-confirm',", "'call', ...(platform === 'kuaishou' ? ['login', 'login-confirm'] : []),")
        text = replace_once(text, ", ...(platform === 'kuaishou' ? [] : ['login-status', 'export', ...(platform === 'tiktok' ? ['prepare-write'] : [])])", '')
        text = replace_once(text, "    const { main: login } = await import('./login.mjs');\n    return login([action === 'login-confirm' ? 'export' : action, '--platform', platform, ...args]);",
                            "    throw new PlatformError('UNSUPPORTED', '本版不包含浏览器登录/导出。通过 xiaobei-runtime import-session 导入已授权 API 会话；快手保留 HTTP 扫码/短信登录。', 4);")
        changes.append('no-browser-login')
    if path == 'expert-wx-mp/tools/generate-wenyan-theme/generate-wenyan-theme.sh':
        text = text.replace('collect-theme-sources.js', 'collect-theme-sources.mjs')
        changes.append('user-provided-local-html-only')
    if path in ('xhs-hunter/xhs-hunter.sh', 'expert-bd/tools/xhs-live/xhs-live.sh'):
        text = replace_once(text, 'SELF="$(readlink -f "${BASH_SOURCE[0]}")"', 'SELF="${BASH_SOURCE[0]}"')
        changes.append('staged-regular-wrapper-path')
    if path.endswith('.md'):
        # Native production methods remain intact; only host-specific routing changes.
        text = text.replace('`content-producer`', '当前实际可用的 WorkBuddy 视频制作专家')
        text = text.replace('content-producer', '当前实际可用的 WorkBuddy 视频制作专家')
        text = text.replace('Content Producer', 'WorkBuddy 视频制作专家')
        text = re.sub(r'\bCP\b', '制作方', text)
        text = text.replace('spawn 当前实际可用的 WorkBuddy 视频制作专家', '有真实调用工具时调用当前实际可用的 WorkBuddy 视频制作专家')
        text = re.sub(r'spawn IT (?:engineer|Engineer)(?: subagent)?', '使用当前真实可用的 WorkBuddy 工具', text)
        text = text.replace('应该 使用当前真实可用的 WorkBuddy 工具 配置环境变量，**不要自己写环境变量文件**。', '使用 `xiaobei-runtime configure --env-file` 导入用户授权的私有配置文件，不在命令行、文档或专家包中写凭据。')
        text = text.replace('应该 使用当前真实可用的 WorkBuddy 工具 写入实例环境变量，**不要自己写环境变量文件**。', '使用 `xiaobei-runtime configure --env-file` 导入用户授权的私有配置文件。')
        text = text.replace('OpenClaw 内置 TTS 工具', 'WorkBuddy 本次实际可用的 TTS 工具')
        if path == 'pitch-deck/SKILL.md':
            for script, command in [('html_to_longimage.py', 'pitch-deck-longimage'), ('html_to_pptx.py', 'pitch-deck-pptx'), ('extract_pptx.py', 'pitch-deck-extract')]:
                text = text.replace('python3 ./scripts/' + script, command)
            text = text.replace('执行时按本技能实际安装路径拼接。', '执行时通过 xiaobei-runtime 的逻辑命令，不自行拼接路径。')
        text = text.replace('`expert-osbi` 的 Market Research workflow', '当前实际可用的公开资料检索能力')
        text = text.replace('expert-osbi', '当前实际可用的公开资料检索能力')
        if path in ('tiktok-hunter/SKILL.md', 'x-hunter/SKILL.md', 'weibo-hunter/SKILL.md'):
            start = text.index('**登录必须在 Camoufox')
            end = text.index('```bash', start)
            text = text[:start] + '会话导入与检查见 [运行库登录说明](../platform-runtime/references/login.md)。发布与 BD 复用对应账号的 API 会话，多账号显式传 `--account`。\n\n' + text[end:]
        if path == 'platform-runtime/references/login.md':
            text = '''# API 会话导入与管理

X、TikTok、微博通过 `xiaobei-runtime import-session --platform <x|tiktok|weibo> --account <alias> --file <用户授权私有文件>` 导入。文件可以是 Cookie 数组或平台原生会话对象，权限仅当前用户可读写；不从 OpenClaw 或浏览器 profile 取凭据。快手仍使用 `kuaishou-hunter login/login-confirm` 的 HTTP QR/SMS 流程。

导入在临时私有目录执行 auth login 和 auth status，核对新会话与在线用户 ID 一致后才原子写入私有平台状态目录。失败不覆盖旧会话，同一账号别名不允许更换用户；导入新账号用新 alias，不自动改变已有默认账号。多账号业务操作显式传 `--account`。成功后执行对应 hunter check；有 Cookie 不等于通过在线校验。

TikTok 写操作仍要求 ticket_guard_private_key、ticket_guard_encrypt_ticket、ticket_guard_ts_sign 等同次材料；缺项返回只读状态，写工具请求前再次检查。不要补造材料或拼接其他设备的票据。

代理使用明确 PLATFORM_API_<平台大写ID>_PROXY、PLATFORM_API_PROXY 或宿主 HTTPS_PROXY/HTTP_PROXY。凭据与代理值不输出日志。明确会话失效、网络/风控故障、依赖缺失分别报告；不自动重登或重发未知写操作。
'''
        text = text.replace('spawn subagent', '调用当前环境提供的专家或子任务工具')
        text = text.replace('sessions_yield', '当前环境的子任务等待工具')
        text = text.replace('`expert-osbi`', 'WorkBuddy 当前可用的公开资料检索能力')
        text = adapt_workflow(path, text)
        changes.append('workbuddy-routing')
    if path.endswith('.py'):
        ast.parse(text)
    return text, changes


def skill_manual(text):
    header, _, body = text[4:].partition('\n---\n')
    name = re.search(r'^name:\s*(.+)$', header, re.M).group(1).strip().strip('"\'')
    match = re.search(r'^description:\s*(.+)$', header, re.M)
    description = match.group(1).strip().strip('"\'') if match else name
    english = f'{name}: native Xiaobei workflows, tools and reusable resources.'
    fields = {'name': name, 'description': description, 'description_zh': description,
              'description_en': english, 'version': VERSION, 'author': 'TeamWiseFlow'}
    invocation = re.findall(r'^(?:user-invocable|disable-model-invocation):\s*(?:true|false)$', header, re.M)
    front = '\n'.join(f'{key}: {json.dumps(value, ensure_ascii=False)}' for key, value in fields.items())
    if invocation:
        front += '\n' + '\n'.join(invocation)
    prelude = '\n## WorkBuddy 执行入口\n\n本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。\n'
    if name == 'council':
        prelude += '\n保留战略家、质疑者、务实者、风控者四个声音。当前 WorkBuddy 有专家/子任务调用工具时，给三个独立声音只传必要上下文；没有此工具时按三个角色分别完成论证并注明同会话分析，不能调用 OpenClaw self-spawn 或编造子任务结果。\n'
        body = body.replace('三个外部声音以**独立子 agent** 身份启动(self-spawn)', '工具可用时，三个外部声音以**独立子任务** 身份启动')
        body = body.replace('### 4. 并行启动三个独立声音', '### 4. 分别完成三个声音的论证')
        body = body.replace('每个子 agent 只获得：', '有子任务工具时，每个子任务只获得以下信息；否则按以下角色模板在同会话分别分析，并明确标注：')
    if name == 'native-ui-card':
        body = body.replace('；小红书卡片找不到 Chromium 时可使用已安装的 `camoufox-cli`', '；两种平台都仅使用 Chromium')
    if name in ('tiktok-hunter', 'x-hunter', 'weibo-hunter', 'platform-runtime'):
        prelude += '\n本版保留 API 业务，不包含浏览器 login/export/prepare-write。通过 `xiaobei-runtime import-session` 导入用户明确授权的 API 会话文件，再执行 hunter check；快手仍可用 HTTP 扫码/短信登录。TikTok 写操作仍需完整会话材料，不绕过原门槛。\n'
    if name == 'platform-runtime':
        body = '''平台任务使用对应技能 wrapper，由 xiaobei-runtime 调度。本目录提供四平台共享 API 传输、能力检查、发布回执与会话管理，不作为业务入口。会话导入及快手 HTTP 登录见 [登录说明](references/login.md)。

状态由运行层设置 PLATFORM_API_HOME，默认使用独立 ~/.xiaobei-workbuddy/logins/platform-api。依赖按 package.json 和固定四平台 profile 由运行层安装；保留原上游版本、校验值、裁剪和探测逻辑。不要绕过固定版本安装器手工安装 catbus-cli。

平台代理按 PLATFORM_API_<平台大写ID>_PROXY、PLATFORM_API_PROXY、HTTPS_PROXY/HTTP_PROXY 选择，空的显式平台代理值表示直连。不读取浏览器配置，代理和凭据不输出日志。
'''
    if name in ('expert-douyin', 'expert-wx-mp'):
        unavailable = {'expert-douyin': ('douyin-publish', 'douyin-engagement'), 'expert-wx-mp': ('wx-mp-engagement',)}[name]
        if name == 'expert-douyin':
            prelude += '\n本版不提供抖音自动发布与本人后台取数。按已适配的工作流交付发布材料、接收用户后台数据，再做记录与 DNA 复盘。\n'
        else:
            prelude += '\n本版使用用户提供的文章正文、封面、排版样本和后台数据，完成账号诊断、DNA、写作排版与 API 草稿上传；不提供公众号自动采集或后台取数。\n'
        body = '\n'.join(line for line in body.split('\n') if not (line.startswith('|') and any(f'`{item}`' in line for item in unavailable)))
    return '---\n' + front + '\n---\n' + prelude + '\n' + body


def sync_persona():
    agent = EXPERT / 'agents/xiaobei-growth.md'
    sources = [ROOT / 'crews/main/SOUL.md', ROOT / 'crews/main/IDENTITY.md']
    soul, identity = [file.read_text() for file in sources]
    soul = soul.split('## 权限级别')[0].strip()
    soul = soul.replace('- 委派 it-engineer 做系统运维与渠道配置', '- 渠道凭据按 xiaobei-runtime 配置；专业视频制作仅交给本次实际可调用的 WorkBuddy 能力')
    soul = soul.replace('（参考 it-engineer 的"升级前自主检查"原则，但 main 的角色是"发现要做的事 → 委派 it-engineer"）', '')
    persona = '<!-- native-persona:start -->\n' + identity.strip() + '\n\n' + soul + '\n<!-- native-persona:end -->'
    text = agent.read_text()
    if text.count('<!-- native-persona:start -->') != 1 or text.count('<!-- native-persona:end -->') != 1:
        raise ValueError('Agent persona markers required')
    text = re.sub(r'<!-- native-persona:start -->.*?<!-- native-persona:end -->', lambda _: persona, text, flags=re.S)
    agent.write_text(text)
    return {'target': 'agents/xiaobei-growth.md', 'sha256': hashlib.sha256(text.encode()).hexdigest(),
            'sources': [{'source': str(file.relative_to(ROOT)), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()} for file in sources]}


def excluded(path):
    return any(path == prefix or path.startswith(prefix + '/') for prefix in SPEC['exclude_paths'])


def sync():
    index_path = EXPERT / '.codebuddy-plugin/native-index.json'
    previous = json.loads(index_path.read_text()) if index_path.is_file() else {'files': []}
    tracked = subprocess.check_output(['git', 'ls-files', '-z', 'skills', 'crews/main/skills'], cwd=ROOT).decode().split('\0')
    records, roots, commands = [], set(), {}
    for source in tracked:
        if not source:
            continue
        prefix = 'crews/main/skills/' if source.startswith('crews/') else 'skills/'
        relative = source[len(prefix):]
        name = relative.split('/')[0]
        if name in SPEC['exclude_skills'] or excluded(relative) or '/' not in relative:
            continue
        file = ROOT / source
        if file.is_symlink():
            continue
        if not file.is_file() or any(part.startswith('.') for part in Path(relative).parts) or file.name in {'README.md', 'package-lock.json'}:
            continue
        destination = SKILLS / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        original = file.read_bytes()
        changes = []
        if file.suffix in {'.md', '.py', '.sh', '.mjs', '.js', '.ts', '.json'}:
            text, changes = adapt(relative, original.decode())
            if file.name == 'SKILL.md':
                text = skill_manual(text)
                changes.append('workbuddy-frontmatter-and-entry')
                if destination.parent.parent == SKILLS:
                    roots.add(name)
            if file.suffix == '.md' and text.endswith('\n\n'):
                text = text.rstrip('\n') + '\n'
                changes.append('single-final-newline')
            data = text.encode()
        else:
            data = original
        destination.write_bytes(data)
        destination.chmod(0o755 if file.suffix == '.sh' else 0o644)
        if file.suffix == '.sh' and file.parent.name != 'scripts':
            command = file.stem
            if command in commands and commands[command] != relative:
                raise ValueError(f'duplicate command: {command}')
            commands[command] = relative
        records.append({'source': source, 'target': relative, 'source_sha256': hashlib.sha256(original).hexdigest(),
                        'sha256': hashlib.sha256(data).hexdigest(), 'adaptations': changes})
    missing = set(SPEC['required_skills']) - roots
    if missing:
        raise ValueError(f'Missing required skills: {sorted(missing)}')
    extensions = PRODUCT / 'extensions'
    for source in sorted(extensions.rglob('*')):
        if not source.is_file():
            continue
        relative = source.relative_to(extensions).as_posix()
        if relative.split('/')[0] not in roots:
            raise ValueError('Extension targets excluded skill: ' + relative)
        original = source.read_bytes()
        data = original
        destination = SKILLS / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        records.append({'source': str(source.relative_to(ROOT)), 'target': relative,
                        'source_sha256': hashlib.sha256(original).hexdigest(), 'sha256': hashlib.sha256(data).hexdigest(),
                        'adaptations': ['workbuddy-task-workflow']})
    for command, script in [('pitch-deck-longimage', 'html_to_longimage.py'), ('pitch-deck-pptx', 'html_to_pptx.py'), ('pitch-deck-extract', 'extract_pptx.py')]:
        commands[command] = 'pitch-deck/scripts/' + script
    retained = {record['target'] for record in records}
    for record in previous['files']:
        if record['target'] not in retained:
            stale = SKILLS / record['target']
            if stale.resolve().is_relative_to(SKILLS.resolve()):
                stale.unlink(missing_ok=True)
    for name in set(previous.get('skills', [])) - roots:
        shutil.rmtree(SKILLS / name, ignore_errors=True)
    (EXPERT / 'avatars/ofb_contact.png').unlink(missing_ok=True)
    assets = []
    persona = sync_persona()
    index_path.write_text(json.dumps(
        {'version': VERSION, 'skills': sorted(roots), 'commands': commands, 'files': records,
         'assets': assets, 'persona': persona, 'relay_base_url': SPEC['relay_base_url'],
         'excluded_skills': SPEC['exclude_skills'], 'excluded_paths': SPEC['exclude_paths']}, ensure_ascii=False, indent=2) + '\n')
    requirements = SKILLS / 'xiaobei-runtime/references/python-requirements.txt'
    requirements.parent.mkdir(parents=True, exist_ok=True)
    requirements.write_bytes((PRODUCT / 'requirements.txt').read_bytes())
    (EXPERT / 'LICENSE').write_bytes((ROOT / 'LICENSE').read_bytes())
    manifest_path = EXPERT / '.codebuddy-plugin/plugin.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['version'] = VERSION
    custom = ['xiaobei-runtime', 'xiaobei-video-handoff']
    manifest['skills'] = ['./skills/' + name for name in [*custom, *sorted(roots)]]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    for name in custom:
        manual = SKILLS / name / 'SKILL.md'
        manual.write_text(re.sub(r'^version: .*$', 'version: ' + VERSION, manual.read_text(), flags=re.M))
    inventory = ['# 技能保留与裁剪范围', '', f'原生技能 {len(roots)} 个，WorkBuddy 适配技能 {len(custom)} 个；原生资源与扩展流程 {len(records)} 个、逻辑命令 {len(commands)} 个。由 sync_native.py 生成。', '',
                 '保留 main 与公共技能的原工作流、脚本、模板、素材和共享运行库。操作只走 xiaobei-runtime 统一入口；下表没有 wrapper 的技能按其手册执行内容工作。脚本存在不等于平台账号已连接或实号验收通过。', '',
                 '| 原生技能 | 包内命令入口 |', '| --- | --- |']
    for name in sorted(roots):
        wrappers = sorted(command for command, path in commands.items() if path.split('/')[0] == name)
        inventory.append('| `' + name + '` | ' + (' / '.join('`' + command + '`' for command in wrappers) or '内容方法与工作流，无独立 wrapper') + ' |')
    inventory += ['', '## 删除的技能', '', '| 技能 | 原因 |', '| --- | --- |']
    inventory += [f'| `{name}` | {reason} |' for name, reason in SPEC['exclude_skills'].items()]
    inventory += ['', '## 混合技能中删除的工具与资源', '', '| 路径 | 原因 |', '| --- | --- |']
    inventory += [f'| `{name}` | {reason} |' for name, reason in SPEC['exclude_paths'].items()]
    inventory += ['', '## 保留但改变入口的能力', '', '- native-ui-card 保留渲染、模板、头像及样式，仅用 Chromium，不包含 Camoufox 回退。',
                  '- 公众号文章正文、封面、排版参考和后台数据由用户提供；主题工具仅整理用户本地 HTML，不采集链接或账号。',
                  '- X/TikTok/微博保留 API 与原写操作检查，通过私有文件 import-session 在线核验后导入；不含浏览器登录/导出。快手 HTTP 登录保留。',
                  '- Council 保留四声分析。有实际子任务工具才并行委托；没有时明确标注同会话角色分析。',
                  '- 完整视频制作不打包 content-producer，已有素材加工由 video-edit、talking-head-cut、video-review 执行。',
                  '- HTTP/API 与已有 relay 客户端保留，不预置凭据。Camoufox 发布与取数缺失步骤接受用户资料或 WorkBuddy 当前真实可用的工具。', '']
    inventory += ['## 官方服务与角色', '', f'- 默认 relay：{SPEC["relay_base_url"]}，沿用现有官方服务，不另建 WorkBuddy relay。',
                  '- 小贝 SOUL.md / IDENTITY.md 嵌入 agents/xiaobei-growth.md 系统提示词；不依赖平台自动加载这些文件。',
                  '- 接入未配置时仅针对当前确实需要 relay 的步骤提示官网说明；不包含联系图片、服务价格或任务完成后的推广。',
                  '- 已删除 xiaobei-operations 的泛化重复指导，入口直接路由原生专家与具体任务 workflow。', '']
    (PRODUCT / 'docs/skill-inventory.md').write_text('\n'.join(inventory))
    print(json.dumps({'native_skills': len(roots), 'files': len(records), 'commands': len(commands)}, ensure_ascii=False))


if __name__ == '__main__':
    sync()
