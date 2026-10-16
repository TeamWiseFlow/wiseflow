#!/usr/bin/env bash
# content-calibrator.sh — content-calibrator 顶层 wrapper（子命令分发）
# 让 agent 用 `content-calibrator <子命令> [参数...]` 走 PATH，零路径拼接。
# 每个子命令 exec 转发到 scripts/ 下对应脚本，不改语义。
set -euo pipefail
SELF="${BASH_SOURCE[0]}"
# 只解析 ~/.xiaobei-workbuddy/bin 软链一层（bin/<skill> -> <workspace>/skills/<skill>/<skill>.sh），
# 不 readlink -f 继续展开 workspace 内 skills/<skill> 指向仓库模板的软链。
# 子脚本用 dirname $0/../../.. 推导 workspace 根（ROOT/db/…），readlink -f 会把
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
  eval)          exec bash "$SCRIPT_DIR/scripts/dna-eval.sh" "$@" ;;
  query-metrics) exec bash "$SCRIPT_DIR/scripts/query-metrics.sh" "$@" ;;
  init)          exec bash "$SCRIPT_DIR/scripts/init.sh" "$@" ;;
  *)
    cat >&2 <<'USAGE'
用法: content-calibrator <子命令> [参数...]

子命令:
  eval           DNA 表现评估聚合引擎（须从 workspace 根调用）
                   eval --platform <p> --check                       廉价阈值检查
                   eval --platform <p>                               聚合触发 DNA 的证据
                   eval --platform <p> --dna-id <id> --force         手动触发（不达阈值也评估）
                   eval --platform <p> --mark-evaluated --ids 3,4,5  评估完成后标记
  query-metrics  查询单篇内容的互动指标（--platform --source-folder）
  init           初始化平台校准数据目录（--platform <p>，幂等）
USAGE
    exit 1
    ;;
esac
