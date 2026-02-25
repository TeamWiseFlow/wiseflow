以下测试均要求：

- 在 test 下创建一个 md 文件，记录每次的测试结果（success/fail)，并最终整理为一个列表；
- 每次测试获取的快照需要额外保存为本地文件，备查。


# 企业官网与政府网站

分别打开如下页面，**每批并发 6 个页面**，看是否可以正常打开页面，不触发反检测，并可以获取有效快照内容

## 测试用例

```
https://www.komatsu.com/en-us
https://www.putzmeister.com/web/european-union
https://www.liebherr.com/en-hk/group/start-page-5221008
https://www.cat.com/global-selector.html
https://www.bing.com/search?q=%E5%8D%8E%E5%B0%94%E8%A1%97%E6%97%A5%E6%8A%A5
https://www.wsj.com/
https://www.bloomberg.com
https://www.justice.gov/
http://www.china-cer.com.cn/policy_base/
https://zjw.sh.gov.cn/zwgk/index.html#tab2-a
https://fgj.sh.gov.cn/gfxwj/index.html
https://rsj.sh.gov.cn/tgwgfx_17726/index.html
https://ybj.sh.gov.cn/dybz3/index.html
https://www.mohurd.gov.cn/gongkai/fdzdgknr/zgzygwywj/index.html
https://www.shanghai.gov.cn/nw39221/index.html
https://www.shanghai.gov.cn/nw39220/index.html
https://www.shanghai.gov.cn/nw11408/index.html
https://www.shanghai.gov.cn/nw11407/index.html
https://www.shanghai.gov.cn/nw2407/index.html
https://www.shanghai.gov.cn/nw42850/index.html
https://www.shanghai.gov.cn/nw42944/index.html
https://www.gov.cn/zhengce/index.htm
```

# 搜索引擎压力测试

打开搜索页并做压力测试，**每批并发 6 个页面**，看是否能够正常返回并成功获取快照内容

# 网站预登录功能模拟测试

打开 https://www.wsj.com/opinion/donald-trump-tariffs-ieepa-supreme-court-john-roberts-opinion-e2610d81

能够侦测到页面存在登录元素，提醒用户完成登录，之后再次访问该页面，能够正常访问，并成功获取内容（正文长度出现变化，大于第一次获取的）

# 社交媒体获取

## 1. 非登录指定主页获取

1.1 打开下面第一个站点，看是否触发了反侦测，以及是否可以获取页面内容。（这些内容都是可以不登录进行获取的）

1.2 在打开的页面里面随便选一个帖子，点进入，看是否可以获取详情，包括评论，如果触发了登录验证，则提示用户完成登录，之后再次访问该页面，能够正常访问，并成功获取内容（正文长度出现变化，大于第一次获取的）

1.3 重复以上步骤逐个测试每个站点

```
https://x.com/valormental
https://www.facebook.com/andrea.sow.31
https://www.linkedin.com/in/baoqiangliu/
https://www.instagram.com/elisameliani/
https://space.bilibili.com/3546603057056627
https://mp.weixin.qq.com/s/Duij3Z2vrImLuOzanqbgbA
https://www.douyin.com/user/MS4wLjABAAAAXUpP_zAelVixv3zv_sWINae86Dt0FMPRZyuozH8MmhbBjvgoDg_xq3Lqnwlacelc
https://www.kuaishou.com/profile/3xvwve5yerjsvvg
https://m.weibo.cn/profile/2194035935
https://www.xiaohongshu.com/user/profile/5f035b1c0000000001002389?xsec_token=ABti9cMRn3S9ARpTWxqiy-5oHI9_QXq50-5qjiSm8emMk=&xsec_source=pc_feed
https://www.zhihu.com/people/lingzezhao
https://discord.com/servers/midjourney-662267976984297473
```

## 2. 搜索

2.1 依次打开如下站点，看是否触发了反侦测，以及是否可以获取页面内容，如果检测到需要登录，则提示用户完成登录，之后再次访问该页面，能够正常访问，并成功获取内容（正文长度出现变化，大于第一次获取的）；

2.2 在打开的页面里面随便选一个帖子，点进入，看是否可以获取详情，包括评论，如果触发了登录验证，则提示用户完成登录，之后再次访问该页面，能够正常访问，并成功获取内容（正文长度出现变化，大于第一次获取的）

2.3 重复以上步骤逐个测试每个站点

```
https://x.com/search?q=OpenClaw
https://www.facebook.com/search/posts/?q=OpenClaw
https://www.linkedin.com/search/results/all/?keywords=openclaw
https://www.instagram.com/explore/tags/OpenClaw/
https://search.bilibili.com/all?keyword=openclaw
https://www.douyin.com/search/OpenClaw?type=user
https://www.douyin.com/search/OpenClaw?type=video
https://www.kuaishou.com/search/video?searchKey=openclaw
https://m.weibo.cn/search?containerid=100103type%3D1%26q%3Dopenclaw
https://www.xiaohongshu.com/search_result?keyword=openclaw
https://www.zhihu.com/search?q=openclaw&type=content
https://www.zhihu.com/search?q=openclaw&type=people
https://www.zhihu.com/search?q=openclaw&type=zvideo
```

## 输出结果

每次运行会生成目录：`browser_test/results/<runId>/`

- `report.md`：汇总报告（success/fail/blocked）
- `cases/<caseId>.json`：单用例详情（耗时、错误、登录校验结果）
- `snapshots/<caseId>.txt`：登录前 AI 快照
- `snapshots/<caseId>_after.txt`：登录后 AI 快照（仅登录流程触发时）

---

# Managed Browser 自动化测试（推荐）

脚本路径：`browser_test/run-managed-tests.mjs`

使用 **openclaw-managed browser**，通过以下四个 CLI 命令驱动测试，无需 Chrome 扩展：

```
openclaw browser --browser-profile openclaw status
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open <url>
openclaw browser --browser-profile openclaw snapshot
```

## 运行命令

```bash
# 快速验证（8 个代表性用例，~5 分钟）
node browser_test/run-managed-tests.mjs --mode smoke

# 完整测试（企业/政府/搜索/新闻，含预登录交互，~25 分钟）
node browser_test/run-managed-tests.mjs --mode full

# 全量测试（包含社交媒体，含多处交互登录提示）
node browser_test/run-managed-tests.mjs --mode social
```

## 可选参数

| 参数 | 说明 | 默认值 |
|------|------|-------|
| `--mode <smoke\|full\|social>` | 测试范围 | `smoke` |
| `--profile <name>` | browser profile | `openclaw` |
| `--stabilizeMs <ms>` | 打开页面后等待稳定的时间 | `4000` |
| `--timeoutMs <ms>` | 单条命令超时 | `60000` |
| `--outputDir <dir>` | 结果根目录 | `browser_test/results` |

## 运行前准备

先启动 openclaw gateway（保持运行）：

```bash
./scripts/dev.sh gateway
```

无需 Chrome 扩展，managed browser 由 openclaw 自动管理。

## 输出结构

```
browser_test/results/<RUN_ID>_managed/
  report.md              汇总报告（success/blocked/partial/error）
  cases/<id>.json        单用例详情（耗时、快照字节数、内容分析结果）
  snapshots/<id>.txt     页面 AI 快照（snapshot --format ai --mode efficient）
  snapshots/<id>_after.txt 登录后 AI 快照（仅预登录测试触发时）
```

所有判断（是否触发反爬、是否存在登录墙、内容是否充足）均基于提取到的 AI 快照文本。

## 并发策略

- 企业官网、政府网站、搜索引擎：每批并发 6 个页面
- 新闻媒体、预登录、社交媒体：串行逐个测试（避免登录/状态互相干扰）

## 登录测试行为

`full` / `social` 模式下，遇到预登录测试用例（如 WSJ 文章）：

1. 先抓取一次内容（before）；
2. 若检测到登录墙，命令行暂停等待手动登录；
3. 回车后再次抓取（after）；
4. 内容增长 > 20% 且 > 200 chars 则判定登录成功。
