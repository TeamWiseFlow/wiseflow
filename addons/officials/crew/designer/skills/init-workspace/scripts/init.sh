#!/usr/bin/env bash
# init-workspace — 为 designer 单项任务创建标准目录结构
# 用法: bash ./skills/init-workspace/scripts/init.sh <任务名>
# 示例: bash ./skills/init-workspace/scripts/init.sh wiseflow-5-launch-poster

set -euo pipefail

TASK_NAME="${1:?用法: init.sh <任务名>}"

# 任务目录命名: design_assets/YYYY-MM-DD-<任务名>
TODAY="$(date +%Y-%m-%d)"
TASK_DIR="design_assets/${TODAY}-${TASK_NAME}"

# 确保设计资产根目录存在
mkdir -p design_assets/references design_assets/brand

# 创建任务目录（含子目录）
mkdir -p "${TASK_DIR}/source" "${TASK_DIR}/output"

# 初始化 brief.md 模板
if [ ! -f "${TASK_DIR}/brief.md" ]; then
  cat > "${TASK_DIR}/brief.md" <<'BRIEF'
# 设计 Brief

## 需求摘要
<!-- 简述本次设计任务 -->

## 主题文案
<!-- 活动名、核心 slogan、时间地点等关键信息 -->

## 目标平台与尺寸
<!-- 线上/印刷/朋友圈/展架... 及具体尺寸 -->

## 风格方向
<!-- 1–3 个参考词，如"科技感+深色系" -->

## 品牌约束
<!-- 品牌色、字体、LOGO 等（从 MEMORY.md 获取） -->

## 参考素材
<!-- 灵感参考、竞品截图等，附来源 -->
BRIEF
fi

# 初始化 prompts.json
if [ ! -f "${TASK_DIR}/prompts.json" ]; then
  echo '[]' > "${TASK_DIR}/prompts.json"
fi

echo "✅ 任务目录已创建: ${TASK_DIR}/"
echo "   brief.md 模板已就绪，请填写后发送确认"
