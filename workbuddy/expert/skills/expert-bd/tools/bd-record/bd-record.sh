#!/usr/bin/env bash
# bd-record.sh — bd-record 工具 wrapper（子命令分发）
# 让 agent 用 `bd-record <子命令> [参数...]` 走 PATH，零路径拼接。
# 每个子命令 exec 转发到 scripts/ 下对应脚本，不改语义。
set -euo pipefail
SELF="${BASH_SOURCE[0]}"
# 只解析 ~/.xiaobei-workbuddy/bin 软链一层（bin/<tool> -> <workspace>/skills/expert-bd/tools/bd-record/bd-record.sh），
# 不 readlink -f 继续展开 workspace 内 skills/expert-bd 指向仓库模板的软链。
# 子脚本用 dirname $0 向上推导 workspace 根（db/…），readlink -f 会把
# workspace 折叠成仓库模板路径，导致 ROOT 解析到模板目录（无 db → 空结果）。
# 保留字面 workspace 路径，ROOT 才能命中真实运行数据目录。
if [ -L "$SELF" ]; then
  _target="$(readlink "$SELF")"
  case "$_target" in
    /*) SELF="$_target" ;;
    *)  SELF="$(cd "$(dirname "$SELF")" && pwd)/$_target" ;;
  esac
fi
SCRIPT_DIR="$(cd "$(dirname "$SELF")" && pwd)"

cmd="${1:-}"
if [ $# -gt 0 ]; then shift; fi

case "$cmd" in
  init-db)          exec bash "$SCRIPT_DIR/scripts/init-db.sh" "$@" ;;
  check-creator)    exec bash "$SCRIPT_DIR/scripts/check-creator.sh" "$@" ;;
  record-creator)   exec bash "$SCRIPT_DIR/scripts/record-creator.sh" "$@" ;;
  check-post)       exec bash "$SCRIPT_DIR/scripts/check-post.sh" "$@" ;;
  record-post)      exec bash "$SCRIPT_DIR/scripts/record-post.sh" "$@" ;;
  *)
    cat >&2 <<'USAGE'
用法: bd-record <子命令> [参数...]

子命令:
  init-db            初始化 db/bd_record.db（幂等）
  check-creator      创作者去重检查（--platform --creator-id）
  record-creator     记录创作者（--platform --creator-id --nickname --homepage-url --qualified --notes）
  check-post         帖子互动去重检查（--platform --post-url）
  record-post        记录互动（--platform --post-title --post-url --strategy --reply-content [--reply-target-id]）
USAGE
    exit 1
    ;;
esac
