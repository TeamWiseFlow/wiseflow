#!/usr/bin/env bash
# ir-record.sh — ir-record 工具 wrapper（子命令分发）
# 让 agent 用 `ir-record <子命令> [参数...]` 走 PATH，零路径拼接。
# 每个子命令 exec 转发到 scripts/ 下对应脚本，不改语义。
set -euo pipefail
SELF="${BASH_SOURCE[0]}"
# 只解析 ~/.xiaobei-workbuddy/bin 软链一层（bin/<tool> -> <workspace>/skills/expert-ir/tools/ir-record/ir-record.sh），
# 不 readlink -f 继续展开 workspace 内 skills/expert-ir 指向仓库模板的软链。
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
  init-db)            exec bash "$SCRIPT_DIR/scripts/init-db.sh" "$@" ;;
  check-investor)     exec bash "$SCRIPT_DIR/scripts/check-investor.sh" "$@" ;;
  record-investor)    exec bash "$SCRIPT_DIR/scripts/record-investor.sh" "$@" ;;
  update-status)      exec bash "$SCRIPT_DIR/scripts/update-status.sh" "$@" ;;
  check-contact)      exec bash "$SCRIPT_DIR/scripts/check-contact.sh" "$@" ;;
  record-contact)     exec bash "$SCRIPT_DIR/scripts/record-contact.sh" "$@" ;;
  query-progress)     exec bash "$SCRIPT_DIR/scripts/query-progress.sh" "$@" ;;
  query-stale)        exec bash "$SCRIPT_DIR/scripts/query-stale.sh" "$@" ;;
  check-application)  exec bash "$SCRIPT_DIR/scripts/check-application.sh" "$@" ;;
  record-application) exec bash "$SCRIPT_DIR/scripts/record-application.sh" "$@" ;;
  update-application) exec bash "$SCRIPT_DIR/scripts/update-application.sh" "$@" ;;
  query-applications) exec bash "$SCRIPT_DIR/scripts/query-applications.sh" "$@" ;;
  *)
    cat >&2 <<'USAGE'
用法: ir-record <子命令> [参数...]

子命令:
  init-db              初始化 db/ir_record.db（幂等）
  check-investor       投资人去重检查（--name --firm）
  record-investor      记录投资人（--name --type --firm 必填，其余可选）
  update-status        更新投资人状态（--id --status [--notes]）
  check-contact        检查近期接触（--investor-id --days）
  record-contact       记录接触（--investor-id --contact-type --direction --summary --contact-date 必填）
  query-progress       Pipeline 摘要
  query-stale          超期未跟进投资人（--days <N>）
  check-application    申报去重检查（--name [--organizer]）
  record-application   记录申报（--name --type 必填）
  update-application   更新申报状态（--id --status [--notes] [--result]）
  query-applications   查询申报（[--status] [--upcoming <天数>]）

各子命令完整参数见 ir-record 工具说明（SKILL.md）。
USAGE
    exit 1
    ;;
esac
