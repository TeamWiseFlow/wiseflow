# video-producer — Tools

## Environment Variables Required

| 变量 | 用途 | 必填 |
|------|------|------|
| `SILICONFLOW_API_KEY` | 图片/视频生成 + LLM + TTS（同一个 Key） | **是** |
| `LLM_API_BASE` | 如需切换其他 LLM 提供商，设置其 API 地址 | 否 |
| `LLM_API_KEY` | 切换其他 LLM 时填写，否则默认复用 SILICONFLOW_API_KEY | 否 |
| `LLM_MODEL` | 模型名称（默认 `Qwen/Qwen2.5-7B-Instruct`） | 否 |
| `PEXELS_API_KEY` | pexels-footage 素材下载 | 否（footage 模式必填） |
| `PIXABAY_API_KEY` | pixabay-footage 素材下载 | 否（Pexels 无结果时用） |
