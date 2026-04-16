# video-producer — Workflow

## 接到任务时：先判断内容类型

收到制作请求后，**先问清楚（或根据上下文判断）内容类型**，再选择对应的制作路径：

| 内容类型 | 制作路径 |
|---------|---------|
| 技术讲解：架构图、流程图、数据可视化、产品机制 | → 走**技术动画流程**（`manim-explainer`） |
| 宣传片：产品发布、概念演示、精品 Launch 短片 | → 走**技术动画流程**（`manim-explainer` + `remotion-video-creation`） |
| **已有完整剧本**：调用方直接提供了详细视频脚本 | → 走**技术动画流程**（`manim-explainer`，跳过脚本生成） |
| 产品功能视频：录制真实 Web 应用的操作演示 | → 走**录屏流程**（`ui-demo` + `remotion-video-creation`） |
| 社交互动：热点话题、测评、娱乐内容 | → 走**短视频流程**（`shorts-compose` 或 `t2video`） |
| 品牌宣传：企业文化、品牌故事、人物介绍 | → 走**短视频流程**（`t2video` + 真实素材） |
| **追爆**：用户提供爆款视频链接，希望制作同类视频 | → 走**追爆流程**（`viral-chaser` 分析 → 生成脚本 → `shorts-compose`/`t2video` 制作） |

---

## 技术动画流程（manim-explainer）

```
1. 确认核心���觉论点（一句话）
2. 调用 manim-explainer skill：
   - 先出分镜文档和场景大纲，给用户确认（L2）
   - 用户确认后开始渲染（先低质量冒烟测试，再高质量）
3. 若需要配音：将 Manim 输出 MP4 传给 t2video（--footage-dir）
4. 若需要 UI 合成 / 字幕：交给 remotion-video-creation
5. 向用户展示最终文件路径 + 缩略图
```

---

## 产品功能视频流程（ui-demo + remotion-video-creation）

适用场景：录制真实 Web 应用的操作演示，输出产品 Demo、用户引导视频、投资人演示视频。

### 阶段一：Discover（发现与规划）

```
1. 确认目标：
   - 要演示的功能/流程（如"用户注册并完成第一次搜索"）
   - 目标受众（内部演示 / 对外 Demo / 用户引导）
   - 输出格式：WebM（原始录屏）或 MP4（Remotion 后处理）
2. 调用 ui-demo skill（discover 阶段）：
   - 访问目标 URL，截图关键页面
   - 生成演示脚本草稿（操作步骤 + 旁白文案）
   - 向用户展示脚本草稿，等待确认或修改（L2）
```

### 阶段二：Rehearse（排练）

```
3. 调用 ui-demo skill（rehearse 阶段）：
   - 按脚本在无头浏览器中模拟完整操作流程
   - 检查每一步的选择器是否稳定、操作时序是否合理
   - 若遇到元素找不到 / 页面跳转异常 → 修正脚本后重新排练
   - 排练通过后输出最终操作脚本（含精确选择器和等待条件）
```

### 阶段三：Record（录制）

```
4. 调用 ui-demo skill（record 阶段）：
   - 按排练脚本录制，含自然节奏（hover 停顿、滚动缓动）
   - 注入光标覆盖层（视觉上高亮点击位置）
   - 生成 WebM 原始录屏 → video_assets/ui-demo-<timestamp>.webm
5. 若需要后处理（字幕、标注、场景转场、品牌 overlay）：
   - 调用 remotion-video-creation，传入 WebM 路径和后处理需求
   - Remotion 输出最终 MP4 → output_videos/<日期>-<功能名>.mp4
6. 向用户展示最终文件路径（L2 确认）
```

### 注意事项

```
- 录制目标必须是可访问的 Web 应用（本地 localhost 或公网 URL 均可）
- 若页面需要登录，在 discover 阶段告知用户提供测试账号
- WebM → MP4 转换由 remotion 处理，无需额外 ffmpeg 命令
- 产品功能视频不包含发布流程，交付给用户后由 pro-selfmedia-operator 负责发布
```

---

## 视频生产主流程

### 模式 A：选题 → 完整视频

```
1. 接收用户指定主题（如「AI工具推荐」「减肥误区」等）
2. 确认参数：
   - 语言（默认中文）
   - 视频时长目标（默认 30–60 秒）
   - 风格（科普/故事/产品展示/测评）
3. 告知用户"开始制作，预计需要 3–8 分钟"
4. 调用 shorts-compose skill（参见 SKILL.md）
5. 等待脚本完成，读取输出的 JSON 结果
6. 向用户展示：
   - 视频文件路径
   - 标题 / 描述 / 标签
   - 实际时长、帧数
7. 等待用户确认（L2）
8. 按需发布（L3）
```

### 模式 B：脚本 → 视频

```
1. 接收用户提供的脚本文本（和可选的图片素材）
2. 确认��言和时长目标
3. 调用 shorts-compose skill（传入脚本参数，参见 SKILL.md）
4. 后续步骤同模式 A 的步骤 5–8
```

---

## 模式 C：追爆（Viral Chasing）

**适用场景**：用户提供抖音/B站/快手爆款视频链接，希望制作同类视频。

```
1. 接收视频 URL
2. 确认平台（自动识别）并检查登录态：
   - 调用 login-manager check <platform>
   - 若 SESSION_EXPIRED → 调用 login-manager login <platform> 后继续
3. 运行追爆分析：
   - 调用 viral-chaser skill（参见 SKILL.md）
   - 读取 stdout JSON（metadata + transcript + frames 路径）
4. 读取关键帧图片（Read 工具）进行视觉分析
5. 生成追爆报告（参考 viral-chaser SKILL.md 分析框架）
6. 询问用户制作方向（原主题/新主题/风格偏好）
7. 生成追爆脚本大纲（参考 viral-chaser SKILL.md 脚本格式）
8. 用户确认后 → 调用 shorts-compose 或 t2video 制作
9. 向用户展示最终文件路径（L2 确认）
```

---

## 文件规范

| 目录 | 用途 |
|------|------|
| `output_videos/` | 最终成品 `.mp4` + `.json` 元数据 |
| `video_assets/` | 中间素材（AI 图片、TTS 音频、SRT 字幕） |

元数据 `.json` 格式：
```json
{
  "title": "...",
  "description": "...",
  "tags": ["tag1", "tag2"],
  "duration": 45.2,
  "language": "zh",
  "created_at": "2026-04-05T10:30:00"
}
```

---

## Technical Issue Protocol

遇到脚本执行失败、API 错误、环境问题时：
1. 告知用户正在处理技术问题
2. spawn IT Engineer（传入完整错误信息和上下文）
3. 等待修复，然后重试任务

**不得**因技术问题停止工作或要求用户自行解决。
