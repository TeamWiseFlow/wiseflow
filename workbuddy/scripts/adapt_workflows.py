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
    text = text.replace('、微信公众号 `wx-mp-hunter`', '；公众号内容与账号资料由用户提供')
    text = text.replace(' / `wx-mp-hunter`', '')
    text = text.replace(' 或 `wx-mp-hunter`', '')
    text = text.replace('微信公众号评论不可得。', '公众号评论同样以用户提供的材料为准，不自动读取。')
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
        if path == 'expert-wx-mp/SKILL.md':
            text = text.replace('只想抓个数据', '只想整理用户数据')
            text = re.sub(r'^description:.*$', 'description: 基于用户提供的文章、封面和后台数据，完成微信公众号账号诊断、内容 DNA、选题写作、排版与 API 草稿上传。', text, flags=re.M)
            text = text.replace('| 账号对标 |', '| 账号诊断 | Account Diagnosis | 诊断自己的公众号定位、内容与获客问题，读取 workflows/account-diagnosis.md |\n| 账号对标 |')
            text = text.replace('跨领域通用技能：`wx-mp-hunter`（公众号文章与发布列表采集）、', '公众号正文、封面、截图和后台数据由用户提供。跨领域通用技能：')
        elif path == 'expert-wx-mp/workflows/style-dna.md':
            text = text.replace('调用 `wx-mp-hunter` 获取材料', '整理用户提供的正文和封面')
            text = section(text, '## 样本获取', '''## 样本获取

本版不自动读取公众号链接、账号或合集。文章链接只作出处；只有名称或链接时，请用户补充正文与封面。

| 用户材料 | 处理 |
| --- | --- |
| 本地 Markdown / 文本或粘贴正文 | 读取或保存为 .md / .txt，作为 profiler 输入 |
| Word / PDF / HTML | 用当前实际可用的文件读取能力整理正文，保留标题与原文证据 |
| 文章封面或截图 | 使用用户提供的本地图片，封面通过 --cover-image 传入 |
| 公众号名、文章链接、合集目录 | 记录出处，请用户提供需要分析的实际内容 |

1. 剔除重复或正文缺失样本；截图只能支持其中实际可读的内容，缺失部分请用户补充。
2. 保留用户提供的账号、标题、出处 URL、发布时间，以及本地文件路径；缺失元数据不编造。
3. 一个样本生成单篇 report，多个样本聚合统计。账号级初始化和对标的样本要求按对应 workflow 执行；不足时先交付已有样本的观察并注明覆盖范围。
4. 阅读、转发、评论等数据只使用用户提供的截图或导出文件。
5. 封面必须由用户提供；缺少时记录未提供，不以正文图片或想象补齐。
''', '## 建立或重建 DNA')
            text = text.replace('它不要求重新抓取或重新提取原文。', '已有 DNA 的局部融合不要求用户再次提供完整原文。')
        elif path == 'expert-wx-mp/workflows/account-benchmark.md':
            text = text.replace('只抓文章不提炼 DNA -> 直接走 `wx-mp-hunter`', '仅要求下载公众号文章 -> 请用户提供内容；能力不足时按专家入口引导完整版')
            text = section(text, '### Step 1 - 获取样本', '''### Step 1 - 整理用户样本

请用户提供对标文章的正文、封面及必要截图，可粘贴文本或提供本地文档。账号名、链接、合集目录只记录为出处，不自动抓取。

1. 用户有阅读、转发、评论数据时，可优先选有代表性的文章；数据缺失时按选题和表达取样，不伪造高转发样本。
2. 账号级对标建议至少 10 篇；已有样本不足时先分析并标明覆盖范围，用户愿意时再补充。
3. 保留账号、标题、出处或文件路径，以及用户提供的数据线索，运营效果不等同于内容质量。
4. 正文整理为 .md / .txt 输入 profiler；封面通过 --cover-image 传入，未提供时保留缺口。
5. 单篇只形成单篇观察，不当作账号级稳定 DNA；多个样本才分析共性与覆盖率。
''', '### Step 2 - 建立对标 DNA')
            text = text.replace('不需要重新抓取参考文章', '不需要用户再次提供参考文章')
        elif path == 'expert-wx-mp/workflows/account-setup.md':
            text = text.replace('老号样本采集', '整理用户的老号样本')
            text = text.replace('   - 文章链接：`wx-mp-hunter fetch --download-cover`', '   - 正文、文档和封面：读取用户提供的材料，整理为 profiler 输入')
            text = text.replace('   - 公众号名：先 `wx-mp-hunter posts-list`，再逐篇 `fetch --download-cover`', '   - 公众号名或文章链接：只作出处，请用户补充实际正文和封面')
            text = text.replace('4. `wx-mp-hunter` 不支持微信搜索和互动指标；用户找到账号或文章链接后，Agent 再负责抓取和提炼。', '4. 本版不提供公众号自动采集。用户找到参考后提供正文、封面和数据线索，Agent 基于这些材料提炼。')
            text = text.replace('用户补回账号名或文章链接后，回到路径A。', '用户补充文章内容后，回到路径 A；账号名和链接不能代替正文。')
            text = section(text, '### Step 1 - 获取老号样本', '''### Step 1 - 整理老号样本

1. 请用户提供近期代表文章的正文、封面和必要截图；支持粘贴或本地文档，建议以 30 篇为分析上限。
2. 只有公众号名或链接时补问内容；建议 10 篇，不足时先分析已提供的样本并注明限制。
3. 按 style-dna.md 整理正文与封面，去重、标记材料缺口；不自动抓取，不将样本当作完整发布历史。
''', '### Step 2A')
            text = text.replace('有账号名且 `wx-mp-hunter posts-list` 可用时，先抓最近可获取文章并自行分析，再向用户补问缺失信息。可分析内容支柱、质量、调性、选题、标题、发布频率和时间。', '先分析用户已提供的正文、封面和数据，再补问缺失信息。可判断内容支柱、质量、调性、选题和标题；发布时间和频率只依据用户提供的真实记录。')
        elif path == 'expert-wx-mp/workflows/content-production.md':
            text = text.replace('### 3. 采集生产要求', '### 3. 整理生产要求')
            text = text.replace('参考文章（链接或文本）', '参考文章（用户提供正文及出处）')
            text = text.replace('用户给公众号文章链接时，先判断意图：', '用户提供公众号文章内容时，先判断意图；仅有链接时请补充正文，链接只作出处，不自动抓取：')
            text = text.replace('   - `mp.weixin.qq.com` 链接 -> 调 `wx-mp-hunter fetch` 获取正文（需要封面时加 `--download-cover`）。', '   - 公众号内容 -> 使用用户提供的正文、封面或本地文档；链接只记出处，不自动读取。')
            text = text.replace('提取参考文章排版风格生成主题', '分析用户提供的 HTML 或截图生成主题')
        elif path == 'expert-wx-mp/workflows/editing.md':
            text = text.replace('2. **用户给了微信文章链接**（`mp.weixin.qq.com` 开头）-> 调 `generate-wenyan-theme` 提取参考文章的排版风格，生成自定义主题', '2. **用户提供参考 HTML 或排版截图** -> 调 `generate-wenyan-theme` 分析实际样本，生成自定义主题；只有公众号文章链接时请补充 HTML 或截图，不自动读取链接')
            text = text.replace('4. **对标某个账号的排版** -> 先抓几篇那个号的文章 -> 调 `generate-wenyan-theme` 提取，并登记到 `wx_mp/wenyan-theme/index.json`', '4. **对标某个账号的排版** -> 使用用户提供的多篇 HTML 或截图 -> 调 `generate-wenyan-theme` 分析并生成主题，登记到 `wx_mp/wenyan-theme/index.json`')
        elif path == 'expert-wx-mp/tools/wechat-style-profiler/references/style-17d-framework.md':
            text = text.replace('- `wx-mp-hunter fetch <url> --download-cover` 下载文章分享封面。\n', '')
        elif path == 'expert-wx-mp/tools/generate-wenyan-theme/SKILL.md':
            text = text.replace('从自然语言描述或对标公众号文章生成', '从自然语言描述或用户提供的排版样本生成')
            text = text.replace('- **微信文章仿样式生成**：当用户提供 `https://mp.weixin.qq.com` 文章链接时，调用 `wx-mp-hunter fetch <url> --html` 获取正文 HTML，分析原文排版特征后生成 wenyan CSS', '- **样式参考生成**：分析用户提供的本地 HTML、封面或排版截图，生成 wenyan CSS；只有链接时请补充材料')
            text = text.replace('- **公众号近期文章归纳生成**：当用户提供公众号账号时，调用 `wx-mp-hunter search` + `account-posts` + `fetch --html` 采集近期文章 HTML，抽取共性后生成模板', '- **多篇排版归纳**：读取用户提供的多篇 HTML 或截图，提炼真实出现的排版共性；不自动按账号采集')
            text = section(text, '## 输入模式识别', '''## 输入模式识别

1. 用户提供本地 HTML：运行本地整理入口，将内容保存为样本 JSON 后分析。
2. 用户提供多篇 HTML 或排版截图：逐篇分析，提炼共性；截图不能证明未显示的字号或 CSS 实现。
3. 用户只描述视觉需求：按自然语言模式生成。
4. 只有公众号名或文章链接：先请用户提供 HTML 或截图；链接只记出处。

## 用户 HTML 整理脚本

通过 xiaobei-runtime 调用逻辑命令 generate-wenyan-theme；脚本只读用户本地文件，不访问网络。

```bash
generate-wenyan-theme --input-html wx_mp/ref/article.html --output wx_mp/wenyan-theme/sources.json
generate-wenyan-theme --input-html wx_mp/ref/one.html --input-html wx_mp/ref/two.html --output wx_mp/wenyan-theme/sources.json
```

输入路径可为用户授权的绝对路径或工作空间相对路径；输出必须是工作空间内的相对 .json 路径。结果 articles[].content_html 为实际文件内容，source_file 标明出处。工具不支持 URL 或账号采集参数。用户仅提供截图时直接使用当前可用的视觉能力分析，不伪造 HTML。

''', '## HTML 样式分析要点')
            text = text.replace('采集 JSON', '用户样本 JSON').replace('采集输出 JSON', '样本输出 JSON')
            text = section(text, '### B. 单篇文章 URL 模式', '''### B. 用户提供单篇样本

1. 读取用户提供的 HTML 或排版截图；只有链接时请补充材料。
2. HTML 运行 generate-wenyan-theme --input-html <本地文件> --output wx_mp/wenyan-theme/sources.json，读取真实样本 JSON。
3. 分析实际可见的标题、段落、引用、分割线、强调与图片布局；截图不支持的细节明确标注。
4. 按 #wenyan 命名空间把可迁移特征生成 CSS，不复制无效 class。
5. 按原主题规则保存、注册，再交 wx-mp-publisher 使用。

### C. 用户提供多篇样本

1. 核对用户提供的样本、账号标识和筛选要求；多个 HTML 以重复 --input-html 参数整理。
2. 逐篇阅读真实内容，列出实际参考的标题或文件路径；不宣称读取了未提供的账号文章。
3. 用户已指定样本并要求生成时直接执行；需要自行取舍样本或有风格冲突时，先展示拟采用的样本与取舍。
4. 优先抽取多篇共同的视觉规则，单篇偶发特征作可选细节。
5. 生成 CSS，保存并注册主题。

## 生成前确认要求

仅在需要用户选择样本或解决冲突时补问；说明样本数量、标题或文件名、筛选依据和主题方向。用户已明确提供样本与生成要求时沿用授权，不重复索取确认。

''', '## 生成主题注册规则')
        if 'wx-mp-hunter' in text or 'posts-list' in text:
            raise ValueError('Removed WeChat collection route remains: ' + path)
    return text
