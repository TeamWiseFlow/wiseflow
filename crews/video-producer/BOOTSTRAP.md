# Bootstrap

This is a pre-configured crew workspace. Your role, responsibilities, and behavioral guidelines are fully defined in the following files — please review them at startup:

- **SOUL.md** — Role definition, core responsibilities, and autonomy level
- **AGENTS.md** — Workflows and operating procedures
- **MEMORY.md** — Background context and ongoing task state
- **IDENTITY.md** — Name and persona
- **USER.md** — Assumptions about who you are serving
- **TOOLS.md** — Available tools and usage guidelines

## First-Run Checklist

On first startup, check and report to user:
1. `SILICONFLOW_API_KEY` is set → required for LLM + TTS + image/video generation (all skills)
2. `moviepy` is installed: `python3 -c "import moviepy; print('ok')"` → required for video composition
3. `requests` is installed: `python3 -c "import requests; print('ok')"` → required for t2video
4. `edge-tts` is installed: `python3 -c "import edge_tts; print('ok')"` → required for shorts-compose only
5. Output directories exist: `mkdir -p output_videos video_assets`

Optional (for footage modes):
- `PEXELS_API_KEY` is set → enables `pexels-footage` skill
- `PIXABAY_API_KEY` is set → enables `pixabay-footage` skill

If SILICONFLOW_API_KEY or moviepy check fails, report clearly and spawn IT Engineer to resolve.
