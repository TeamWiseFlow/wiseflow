---
name: manim-explainer
description: Build reusable Manim explainers for technical concepts, graphs, system diagrams, and product walkthroughs, then hand off to the wider video stack if needed. Use when the user wants a clean animated explainer rather than a generic talking-head script.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎬",
        "always": false,
        "requires": { "bins": ["python3", "manim", "ffmpeg"] },
      },
  }
---

# Manim Explainer

Use Manim for technical explainers where motion, structure, and clarity matter more than photorealism.

## When to Activate

- the user wants a technical explainer animation
- the concept is a graph, workflow, architecture, metric progression, or system diagram
- the user wants a short product or launch explainer for X or a landing page
- the visual should feel precise instead of generically cinematic

## Tool Requirements

- `manim` CLI for scene rendering
- `ffmpeg` for post-processing if needed
- `video-editing` for final assembly or polish
- `remotion-video-creation` when the final package needs composited UI, captions, or additional motion layers

## 先决条件安装

```bash
pip install manim
# macOS
brew install cairo pango ffmpeg
# Linux
apt-get install libcairo2-dev libpango1.0-dev ffmpeg
```

## Default Output

- short 16:9 MP4
- one thumbnail or poster frame
- storyboard plus scene plan

## Workflow

1. Define the core visual thesis in one sentence.
2. Break the concept into 3 to 6 scenes.
3. Decide what each scene proves.
4. Write the scene outline before writing Manim code.
5. Render the smallest working version first.
6. Tighten typography, spacing, color, and pacing after the render works.
7. Hand off to the wider video stack only if it adds value.

## Scene Planning Rules

- each scene should prove one thing
- avoid overstuffed diagrams
- prefer progressive reveal over full-screen clutter
- use motion to explain state change, not just to keep the screen busy
- title cards should be short and loaded with meaning

## Network Graph Default

For social-graph and network-optimization explainers:

- show the current graph before showing the optimized graph
- distinguish low-signal follow clutter from high-signal bridges
- highlight warm-path nodes and target clusters
- if useful, add a final scene showing the self-improvement lineage that informed the skill

## Render Conventions

- default to 16:9 landscape unless the user asks for vertical
- start with a low-quality smoke test render
- only push to higher quality after composition and timing are stable
- export one clean thumbnail frame that reads at social size

```bash
# 冒烟测试（低质量）
manim -ql <scene_file>.py <ClassName>

# 中等质量预览
manim -qm <scene_file>.py <ClassName>

# 正式输出
manim -qh <scene_file>.py <ClassName>

# 导出封面帧
ffmpeg -i output.mp4 -ss 2 -frames:v 1 thumbnail.png
```

## Reusable Starter

Use [assets/network_graph_scene.py](assets/network_graph_scene.py) as a starting point for network-graph explainers.

Example smoke test:

```bash
manim -ql assets/network_graph_scene.py NetworkGraphExplainer
```

## Output Format

Return:

- core visual thesis
- storyboard
- scene outline
- render plan
- any follow-on polish recommendations

## Related Skills

- `t2video` with `--footage-dir` when the rendered MP4 needs narration and composition into a short
- `remotion-video-creation` for motion-heavy post-processing, UI compositing, or captions
- `shorts-compose` when the animation is one segment inside a longer short-form piece
