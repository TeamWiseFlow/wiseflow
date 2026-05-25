#!/bin/bash
# scan-feedback.sh - 扫描对外 Crew 实例的 feedback 目录，输出结构化摘要
# 用法:
#   bash ./scan-feedback.sh <instance-id>          扫描单个实例
#   bash ./scan-feedback.sh --all                  扫描所有外部 crew 实例
set -e

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
HRBP_WORKSPACE="$OPENCLAW_HOME/workspace-hrbp"
EXTERNAL_REGISTRY="$HRBP_WORKSPACE/EXTERNAL_CREW_REGISTRY.md"

scan_instance() {
  local instance_id="$1"
  local feedback_dir="$OPENCLAW_HOME/workspace-$instance_id/feedback"

  echo "## Feedback Scan: $instance_id"
  echo ""

  if [ ! -d "$feedback_dir" ]; then
    echo "  ⚠️  No feedback directory found: $feedback_dir"
    echo ""
    return
  fi

  local feedback_files
  feedback_files="$(find "$feedback_dir" -name "*.md" -not -name ".gitkeep" 2>/dev/null | sort)"

  if [ -z "$feedback_files" ]; then
    echo "  ✅ No feedback entries recorded."
    echo ""
    return
  fi

  local total=0 resolved=0 unresolved=0 escalated=0
  local dissatisfied=0

  while IFS= read -r file; do
    [ -f "$file" ] || continue
    local entries
    entries="$(grep -c '^## Feedback:' "$file" 2>/dev/null || echo 0)"
    total=$((total + entries))
    resolved=$((resolved + $(grep -c '已解决' "$file" 2>/dev/null || echo 0)))
    unresolved=$((unresolved + $(grep -c '未解决' "$file" 2>/dev/null || echo 0)))
    escalated=$((escalated + $(grep -c '已升级' "$file" 2>/dev/null || echo 0)))
    dissatisfied=$((dissatisfied + $(grep -c '不满' "$file" 2>/dev/null || echo 0)))
  done <<< "$feedback_files"

  echo "  总反馈条目: $total"
  echo "    - 已解决: $resolved"
  echo "    - 未解决: $unresolved"
  echo "    - 已升级: $escalated"
  echo "    - 用户不满: $dissatisfied"
  echo ""
  echo "  反馈文件:"
  while IFS= read -r file; do
    [ -f "$file" ] || continue
    echo "    - $(basename "$file")"
  done <<< "$feedback_files"
  echo ""
}

if [ "$1" = "--all" ]; then
  if [ ! -f "$EXTERNAL_REGISTRY" ]; then
    echo "❌ External crew registry not found: $EXTERNAL_REGISTRY"
    echo "   Run HRBP recruit to create external crew instances first."
    exit 1
  fi
  echo "# External Crew Feedback Summary"
  echo ""
  # 从注册表中提取实例 ID（假设表格格式：| instance-id | ...）
  grep '^\| [a-z]' "$EXTERNAL_REGISTRY" 2>/dev/null | while IFS='|' read -r _ id _rest; do
    id="$(echo "$id" | tr -d ' ')"
    [ -n "$id" ] && [ "$id" != "Instance ID" ] && scan_instance "$id"
  done || echo "  ⚠️  No instances found in registry."
elif [ -n "$1" ]; then
  scan_instance "$1"
else
  echo "Usage: $0 <instance-id> | --all"
  exit 1
fi
