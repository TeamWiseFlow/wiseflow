"""Host-specific workflow edits; preserve creative methods, remove unavailable execution routes."""
import re


def section(text, heading, replacement, next_heading=None):
    if text.count(heading) != 1:
        raise ValueError('Workflow structure changed; review ' + heading)
    start = text.index(heading)
    end = text.index(next_heading, start + len(heading)) if next_heading else len(text)
    return text[:start] + replacement.rstrip() + '\n\n' + text[end:]


DOUYIN_HANDOFF = '''## Step 6 - 发布材料交付

本版不提供抖音发布命令。将已确认的视频或有序图组、标题、纯正文 body.txt、话题、双封面和所需 AIGC 声明说明放在作品目录，交付用户在抖音原平台发布。

用户本次明确连接了其他 WorkBuddy 抖音发布能力时，先读取它的实际说明再按已有授权调用；不猜工具名或参数，不使用宿主 OpenClaw 的发布脚本。发布结果未知先查原操作，不重新提交。

## Step 7 - 真实发布后记录

材料准备完成的状态是“待发布”，不先写成已发布。收到用户提供的真实发布链接，或实际发布工具的作品回执后，再写 dna-meta.json 并运行 published-track record：平台 douyin，图文 content-type 为 post，视频为 video，传作品目录、真实链接、标题和账号。

本人后台数据由用户导出提供，使用 published-track update-metrics 入库后走 review.md；不能把公开互动数当作后台播放、完播或转化指标。
'''


def adapt_workflow(path, text):
    if not path.endswith('.md'):
        return text
    text = text.replace('`smart-search`', '本次 WorkBuddy 实际可用的检索工具')
    text = text.replace('`ui-demo`', '用户录屏或本次实际可用的录屏能力')
    text = text.replace('`expert-wx-channel/workflows/native-ui-cards.md`', '用户提供的视频号资料')
    if path == 'expert-douyin/workflows/content-production.md':
        text = section(text, '## Step 6 - 发布', DOUYIN_HANDOFF)
        text = text.replace('从选题到发布的完整内容生产。', '从选题到制作、发布材料交付和真实发布后记录的内容生产。')
        text = text.replace('完成抖音图文制作、发布与记录', '完成抖音图文制作、材料交付与真实发布后记录')
        text = re.sub(r'^\| workflow \|.*$', '| workflow | 仅在外部制作能力的实际说明中存在对应流程时指定，否则只交付 Brief 和验收要求 |', text, flags=re.M)
        text = text.replace('发布传 `--cover-vertical` / `--cover-horizontal`。', '把两个方向的封面文件随发布材料一同交付。')
    elif path == 'expert-douyin/workflows/native-ui-cards.md':
        text = section(text, '## 4. 抖音发布与记录', '''## 4. 材料交付与记录

本版在抖音侧交付卡片图片、标题、body.txt 和话题，由用户在原平台发布；本次存在真实 WorkBuddy 发布入口时按该入口说明和已有授权操作。图片生成不等于发布成功，不调用本包没有的浏览器工具。

只有收到真实作品链接或发布回执才使用 published-track record，平台 douyin、content-type post，带作品目录和账号。同步发小红书时走 expert-xhs 的 native-ui-cards workflow，使用本包保留的 xhs-publish API 单独发布与记录。''')
    elif path == 'expert-douyin/workflows/editing.md':
        text = section(text, '## Step 4 - 交付、发布与记录', '''## Step 4 - 交付、发布与记录

保留修改后的成片或图组、封面、标题与正文。用户只要求改片时直接交付；要求上线时按 content-production.md Step 6–7 交付发布材料，或调用本次实际存在的 WorkBuddy 发布能力。收到真实回执后才入库，结果未知不重发。已发布作品删除或下架由用户决定。

风格偏好按 style-dna.md 回流；单次修改不默认改变长期 DNA。''')
    elif path == 'expert-douyin/references/api-capabilities.md':
        text = '''# 抖音能力路由

| 业务 | 入口 |
| --- | --- |
| 内容 DNA、定位、创作、对标、图文分析 | 本包对应 workflow 与 douyin-style-profiler |
| 账号、作品、评论、搜索、媒体下载 | douyin-hunter |
| 视频转写与关键帧 | 先 douyin-hunter 下载，再 viral-chaser 分析本地视频 |
| 已有视频素材加工 | video-edit / talking-head-cut / video-review |
| 已实现的互动、私信、直播写操作 | expert-bd 的对应工具 |
| 发布 | 交付完整材料，由用户原平台发布；本次有真实 WorkBuddy 发布能力时按其说明执行 |
| 本人后台数据与复盘 | 用户导出数据 → published-track update-metrics → content-calibrator 与 review workflow |

采集和 BD 使用 douyin-login 的独立 API 会话。没有发布或本人后台取数的本地入口，不借用宿主浏览器 profile。
'''
    elif path == 'expert-douyin/workflows/review.md':
        text = re.sub(r'^- `douyin-engagement`.*$', '- 本版使用用户提供的本人后台数据，或用户本次明确连接的真实取数能力。保存采集时间与来源，缺项不补零；douyin-hunter 的公开互动计数不能替代后台播放、完播、跳出和转化数据。', text, flags=re.M)
        text = re.sub(r'^- 复盘不取数：.*$', '- 先检查 published-track 中的数据来源和新鲜度；用户需要更新数据时接收新的导出文件并入库，再进行评估。本版没有后台自动采集或 HEARTBEAT 服务。', text, flags=re.M)
    elif path == 'expert-douyin/SKILL.md':
        text = re.sub(r'^description:.*$', 'description: 抖音内容定位、DNA 提取、对标、图文创作、已有视频加工与用户数据复盘。发布交付材料，账号采集走 douyin-hunter。', text, flags=re.M)
        text = text.replace('抖音图文发布', '抖音图文制作与材料交付')
        text = text.replace('群聊误发式单图、问答式连续讨论流三图的制作与抖音图文制作与材料交付', '群聊误发式单图、问答式连续讨论流三图制作与发布材料交付')
        text = re.sub(r'发布走 Camoufox.*?(?=\n\n)', '本版不提供抖音自动发布或本人后台取数。采集与互动使用 douyin-login 的独立 API 会话。', text, flags=re.S)
        text = re.sub(r'^- \*\*串行发布\*\*.*\n', '', text, flags=re.M)
        text = re.sub(r'^- \*\*登录态\*\*.*$', '- **登录态**：仅管理独立采集/互动 API 会话；不读取浏览器发布 profile。', text, flags=re.M)
    elif path == 'expert-xhs/workflows/native-ui-cards.md':
        text = re.sub(r'双平台分发时抖音走.*$', '需要同步抖音时交付材料，由用户原平台发布；小红书继续使用本包 xhs-publish API。', text, flags=re.M)
    elif path == 'douyin-hunter/tools/douyin-login/SKILL.md':
        text = text.replace('和 `douyin-engagement check`', '')
        text = re.sub(r'^`douyin-publish`.*$', '本版只处理采集与互动 API 的登录及平台验证，不为创作者浏览器发布准备会话。', text, flags=re.M)
    elif path == 'douyin-hunter/SKILL.md':
        text = re.sub(r'本人已发作品使用 expert-douyin 的 `douyin-engagement`.*?；', '本人后台数据本版由用户导出提供，再经 published-track 入库复盘；', text)
    elif path == 'native-ui-card/SKILL.md':
        text = text.replace('抖音用 `douyin-publish note --caption @/绝对路径/body.txt` 由脚本读取', '抖音侧交付该文件由用户在原平台发布')
    elif path == 'published-track/SKILL.md':
        text = re.sub(r'^> \*\*视频号.*?(?=\n\n)', '', text, flags=re.S | re.M)
        text = re.sub(r'^统一管理所有平台.*$', '统一管理真实发布事实与指标。平台自动化能力以本包实际技能清单为准；数据库历史兼容表不代表对应平台在本版可采集或发布。', text, flags=re.M)
        text = text.replace('如 `wx_mp`、`wx_channel`、`xhs`、`bilibili`', '如 `wx_mp`、`xhs`、`douyin`、`tiktok`')
        text = '\n'.join(line for line in text.split('\n') if not (line.startswith('|') and '微信视频号' in line))
        text = re.sub(r'本技能只负责发布记录、查询和 `update-metrics` 写库。按平台使用.*?(?=\n\n)', '本技能只负责发布记录、查询和 update-metrics 写库。自动取数使用已保留的 xhs-engagement、tiktok-engagement、kuaishou-engagement、twitter-engagement；抖音和公众号由用户提供后台数据。缺项不补零，失败保留旧值。', text, flags=re.S)
        text = section(text, '## 与发布技能的配合', '''## 与发布技能的配合

保留的 wx-mp-publisher、xhs-publish、tiktok-publish、kuaishou-publish、twitter-post、weibo-publish 在真实发布后记录，带账号、作品链接与 source-folder。DNA 经 dna-meta.json 关联。抖音仅收到用户真实发布事实后补录。

## 平台状态与定时取数

platform-status 只读取工作空间对应平台的校准启用状态，不负责平台连接。只有本次真实可用的 WorkBuddy 调度能力才能安排定时任务；本人后台取数只调用已保留的 engagement 工具。数据库中的历史兼容表不代表本版支持对应平台。''')
    elif path == 'published-track/references/platform-constraints.md':
        text = '\n'.join(line for line in text.split('\n') if '微信视频号' not in line)
        text = text.replace('微信公众号/视频号/头条/掘金/知乎', '微信公众号/头条/掘金/知乎')
    if path.startswith('expert-wx-mp/'):
        replacements = {
            '| 公众号名 | `wx-mp-hunter posts-list` -> `fetch --download-cover` |': '| 公众号名 | 用户提供该账号近期文章链接，再逐篇 wx-mp-hunter fetch --download-cover |',
            '| 公众号名称 | 调 `wx-mp-hunter posts-list` 获取可访问列表，再逐篇 `fetch --download-cover`；抓不到时请用户提供链接 |': '| 公众号名称 | 用户提供近期文章链接，再逐篇 wx-mp-hunter fetch --download-cover |',
            '5. `posts-list` 不可用、账号不在已关注列表或抓取失败时，请用户手动提供对标账号最近文章链接；原则上至少 10 篇，不足 10 篇给全部。': '5. 本版从用户提供的近期文章链接取得样本；原则上至少 10 篇，账号文章不足 10 篇时提供全部并说明。',
            '   - 公众号名：先 `wx-mp-hunter posts-list`，再逐篇 `fetch --download-cover`': '   - 公众号名：请用户提供近期文章链接，再逐篇 wx-mp-hunter fetch --download-cover',
            '1. 用户提供账号名且 `wx-mp-hunter posts-list` 可用时，Agent 直接抓最近可获取文章；建议以最近 30 篇为分析上限，不足 30 篇取全部。': '1. 根据用户提供的近期文章链接取样；建议以最近 30 篇为分析上限，不足 30 篇取全部。',
            '2. `posts-list` 不可用、账号不在已关注列表、列表缺失或抓取失败时，请用户手动提供老号最近文章链接；原则上至少 10 篇，账号文章不足 10 篇时提供全部并说明。': '2. 用户只给公众号名时，请补充近期文章链接；原则上至少 10 篇，账号文章不足 10 篇时提供全部并说明。',
            '有账号名且 `wx-mp-hunter posts-list` 可用时，先抓最近可获取文章并自行分析，再向用户补问缺失信息。可分析内容支柱、质量、调性、选题、标题、发布频率和时间。': '根据用户提供的近期文章链接先抓全文并分析，再补问缺失信息。依据真实样本分析内容支柱、质量、调性、选题、标题与已有样本的发布时间，不将样本当作完整发布历史。',
            '公众号文章与发布列表采集': '用户文章链接的正文、图片与封面获取',
        }
        for before, after in replacements.items():
            text = text.replace(before, after)
        if 'posts-list' in text:
            raise ValueError('Removed WeChat list route remains: ' + path)
        text = re.sub(r'^\| 专题页 / 合集页 \|.*$', '| 专题页 / 合集页 | 用户提供目录中的文章链接，再逐篇 wx-mp-hunter fetch --download-cover |', text, flags=re.M)
        if path.endswith('/SKILL.md') and path.count('/') == 1:
            text = re.sub(r'^description:.*$', 'description: 微信公众号账号诊断、内容 DNA、选题写作、排版与 API 草稿上传。后台指标由用户导出后复盘。', text, flags=re.M)
            text = text.replace('| 账号对标 |', '| 账号诊断 | Account Diagnosis | 诊断自己的公众号定位、内容与获客问题，读取 workflows/account-diagnosis.md |\n| 账号对标 |')
    return text
