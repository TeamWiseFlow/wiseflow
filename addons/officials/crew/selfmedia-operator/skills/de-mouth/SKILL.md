---
name: de-mouth
description: 口播视频去口误。自动识别并删除静音、语气词、卡顿词、重复句、残句等，输出干净视频+字幕+剪映草稿。触发词：去口误、剪口播、de-mouth、去除口误
metadata:
  openclaw:
    emoji: ✂️
    primaryEnv: VOLCENGINE_API_KEY
    requires:
      bin:
        - python3
        - ffmpeg
---

# de-mouth — 口播视频去口误

> 全自动口播精修：转录 → 口误检测 → 剪辑 → 输出

## 快速使用

```
用户: 帮我把这个视频的口误剪掉
用户: 去口误 video.mp4
用户: 处理一下这个口播视频
```

## 输出目录

```
output_videos/<video-name>/
├── subtitles_words.json    # 字级别字幕（含静音标记）
├── readable.txt            # 易读格式（供 AI 分析）
├── sentences.txt           # 分句列表（供 AI 分析）
├── auto_selected.json      # 删除索引列表
├── analysis.json           # 分析统计
├── <name>_clean.mp4        # 去口误视频
├── <name>_clean_hd.mp4    # 高清化视频（--hd 时）
├── <name>.srt              # SRT 字幕（--srt 时）
└── jianying_draft/         # 剪映草稿目录（--draft 时）
    ├── draft_content.json
    └── draft_info.json
```

## 流程

```
0. 确认视频路径 + 输出目录
    ↓
1. 运行去口误脚本（脚本完成步骤 1-6）
    ↓
2. AI 语义分析口误（agent 执行步骤 7）
    ↓
3. 合并 AI 结果，重新剪辑
    ↓
4. 输出最终视频 + 字幕 + 剪映草稿
```

## 执行步骤

### 步骤 0: 确认参数

从用户消息中提取视频路径。确认输出目录：

```bash
VIDEO_PATH="<用户提供的视频路径>"
VIDEO_NAME=$(basename "$VIDEO_PATH" | sed 's/\.[^.]*$//')
OUT_DIR="output_videos/${VIDEO_NAME}"
```

### 步骤 1: 运行去口误脚本

```bash
python3 ./skills/de-mouth/scripts/de_mouth.py "$VIDEO_PATH" \
  --out-dir "$OUT_DIR" \
  --srt --draft
```

**参数说明**：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--silence-threshold` | 0.3 | 静音阈值（秒） |
| `--keep-fillers` | 空 | 保留的语气词（逗号分隔，如 `嗯,啊`） |
| `--no-ai` | 关 | 跳过 AI 语义分析（只做脚本检测） |
| `--hd` | 关 | 2-pass 高清化输出 |
| `--hd-multiplier` | 1.2 | 高清化码率倍率 |
| `--srt` | 关 | 生成 SRT 字幕 |
| `--draft` | 关 | 生成剪映草稿目录 |
| `--dict` | 无 | 热词词典文件路径 |

脚本会自动完成：
- 音频提取 → ASR 转录 → 脚本确定性检测 → 剪辑 → 输出

脚本完成后，读取 `analysis.json` 确认结果。

### 步骤 2: AI 语义分析口误

> 🚨 **核心原则：删前保后。所有重复/口误，删前面的，保后面的。**

读取 `readable.txt` 和 `sentences.txt`，按以下 4 类规则分析。

#### 2.1 句间重复

**规则**：相邻句子（被静音≥0.5s 分隔）开头≥5字相同 → 删**前句整句**。

隔一句也要比对（中间可能是残句）。多次重复（≥3次）保留最后完整的，前面全删。

**输出格式**：
```
| 句号 | idx范围 | 内容摘要 | 处理 |
|------|---------|----------|------|
| 5 | 212-233 | 与句6重复，句6更完整 | 删前句 |
```

#### 2.2 句内重复

**规则**：同一句内短语 A 出现两次（中间夹杂 1-3 字），即 A+中间+A 模式。

**只删前面的重复片段，不删整句。**

```
"于是很把于是很容易把它理解成一种不够友好但很高效的界面"
 ↑删这4字↑ ↑保留后面完整内容↑
```

**不是口误的情况**：列举（任务1任务2任务3）、强调（一个一个地）

#### 2.3 残句

**规则**：话说到一半突然停住，后面接了静音或重新开始。

**整句删除**（从句首到句尾），不只是删结尾几个字。

判断标准：
1. 句子不完整：缺少宾语、谓语或结尾不自然
2. 后接静音：残句后通常有明显停顿
3. 后有重说：重新开始说类似内容

#### 2.4 重说纠正

**规则**：说错后立即纠正，删前面错误的部分。

| 类型 | 原文 | 删除 |
|------|------|------|
| 部分重复 | 你再关你关掉 | "你再关" |
| 否定纠正 | 它是它不是 | "它是" |
| 词被打断 | 依赖[静]依赖关系 | "依赖[静]" |

#### 2.5 合并 AI 结果

将 AI 分析返回的所有删除 idx 追加到 `auto_selected.json`，去重排序。

**⚠️ 关键警告：行号 ≠ idx**

```
readable.txt 格式: idx|内容|时间
                   ↑ 用这个值

行号1500 → "1568|[静1.02s]|..."  ← idx是1568，不是1500！
```

**范围整段删除规则**：标记口误时，从 startIdx 到 endIdx 之间的**所有元素**（含中间的 gap）全部加入删除列表。

### 步骤 3: 重新剪辑（合并 AI 结果后）

如果 AI 分析新增了删除项，需要重新剪辑：

```bash
# 读取合并后的 auto_selected.json，转换为 delete_segments.json
# 然后调用脚本重新剪辑
python3 ./skills/de-mouth/scripts/de_mouth.py "$VIDEO_PATH" \
  --out-dir "$OUT_DIR" \
  --apply-ai \
  --srt --draft
```

> 注：`--apply-ai` 模式下，脚本读取已有的 `auto_selected.json`（含 AI 追加的 idx），
> 跳过转录和检测，直接执行剪辑。

### 步骤 4: 输出结果

向用户报告：

```
✅ 去口误完成！

📹 视频: output_videos/<name>/<name>_clean.mp4
   原时长: 19:02 → 新时长: 15:47（删除 3:15，17.1%）

📊 检测统计:
   - 静音: 114 处
   - 语气词: 89 处
   - 卡顿词: 23 处
   - 句间重复: 15 处
   - 句内重复: 8 处
   - 残句: 6 处
   - 重说纠正: 4 处

📄 SRT 字幕: output_videos/<name>/<name>.srt
🎬 剪映草稿: output_videos/<name>/jianying_draft/
   （复制到 ~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft/ 并重启剪映即可导入）
```

## ASR 说明

| 模式 | 条件 | 时间戳精度 |
|------|------|-----------|
| 火山引擎 | `VOLCENGINE_API_KEY` 已设置 | 字级别（毫秒精度） |
| SiliconFlow | 仅 `SILICONFLOW_API_KEY` 已设置 | 粗估（字符均匀分布） |

火山引擎为推荐方案，提供字级别精确时间戳 + 热词词典支持。

## 剪映草稿说明

输出的 `jianying_draft/` 目录包含 `draft_content.json` + `draft_info.json`，是剪映工程的逆向格式。

**导入方法**：
1. 复制整个目录到 `~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft/`
2. 退出剪映（Cmd+Q）
3. 重新打开剪映
4. 首页即可看到新草稿

**不依赖剪映安装** — 纯文件输出，剪映未安装也不影响去口误功能。

## 配置

### 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `VOLCENGINE_API_KEY` | 推荐 | 火山引擎 ASR API Key |
| `SILICONFLOW_API_KEY` | 降级 | SiliconFlow ASR API Key |

### 热词词典

可选的 `词典.txt` 文件，每行一个词，用于 ASR 转录时纠错专业术语：

```
Claude Code
MCP
API
openclaw
```
