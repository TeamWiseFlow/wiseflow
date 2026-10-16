#!/usr/bin/env python3
"""dna-eval.py — DNA 表现评估聚合引擎（published-track 数据 → 结构化证据）

设计原则：脚本只提供聚合证据（绝对值 + 同账号相对比值 + 趋势走向），
不做定性判断；好坏归因由 Agent 回读 DNA 文档与作品原文完成。

三种模式：
  1. --check            廉价阈值检查（heartbeat 每日跑）：各 DNA 待评估计数与是否触发
  2. （默认）聚合模式    对触发的 DNA 输出逐篇证据 + 每指标趋势
  3. --mark-evaluated   评估报告写完后标记 perf_evaluated=1

关键语义：
  - 待评估记录 = publish_date ≤ 今日-mature_days 且 perf_evaluated=0 且 dna_id 非空
  - 触发条件   = 某（平台, DNA）待评估记录 ≥ min_samples
  - 基线       = 同账号「此前」最多 baseline_window 篇的指标均值（避免后视）；
                 此前 <3 篇 → baseline_insufficient，只给绝对观察不给比值/趋势
  - account 为空 → 归入 __unknown__ 组，不参与其他账号基线
  - 趋势       = 按发布时间序对比值做最小二乘斜率：>+0.02 up / <-0.02 down / 否则 flat；
                 有效点 <3 → insufficient
"""
import argparse
import json
import os
import sqlite3
import sys
from datetime import date, datetime, timedelta

NON_METRIC_COLS = {
    "id", "title", "content_type", "source_folder", "publish_url", "publish_date",
    "distribute_status", "top_comment", "notes", "dna_id", "account", "perf_evaluated",
    "created_at", "updated_at",
    "cal_enabled", "cal_score_er", "cal_score_hp", "cal_score_sr", "cal_score_ql",
    "cal_score_na", "cal_score_ab", "cal_score_pv", "cal_composite",
    "cal_rubric_version", "cal_scored_at", "cal_bias_signals", "cal_bump_evaluated",
}
SLOPE_EPSILON = 0.02
MIN_BASELINE_PRIORS = 3
MIN_TREND_POINTS = 3
UNKNOWN_ACCOUNT = "__unknown__"


def die(msg):
    print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False))
    sys.exit(1)


def metric_columns(conn, table):
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    cols = []
    for _, name, ctype, *_ in rows:
        if name in NON_METRIC_COLS:
            continue
        if (ctype or "").upper().startswith(("TEXT", "BLOB")):
            continue
        cols.append(name)
    return cols


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", default=os.environ.get("PUBLISHED_TRACK_ROOT", os.getcwd()))
    ap.add_argument("--platform", required=True)
    ap.add_argument("--check", action="store_true", help="只做阈值检查，不聚合")
    ap.add_argument("--mark-evaluated", action="store_true", help="标记 perf_evaluated=1")
    ap.add_argument("--ids", default="", help="--mark-evaluated 用，逗号分隔的记录 id")
    ap.add_argument("--dna-id", default="", help="只处理指定 DNA（聚合模式）")
    ap.add_argument("--force", action="store_true", help="忽略 min_samples 阈值强制评估（用户手动触发兜底）")
    ap.add_argument("--min-samples", type=int, default=5)
    ap.add_argument("--mature-days", type=int, default=3)
    ap.add_argument("--baseline-window", type=int, default=10)
    return ap.parse_args()


def main():
    args = parse_args()
    db_path = os.path.join(args.workspace, "db", "published_track.db")
    if not os.path.isfile(db_path):
        die(f"published_track.db not found at {db_path}（先跑 published-track init-db；agent 须从 workspace 根调用）")
    table = f"pub_{args.platform}"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    exists = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()
    if not exists:
        die(f"unknown platform: {args.platform} (table {table} not found)")
    cols = {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if "dna_id" not in cols or "perf_evaluated" not in cols:
        die(f"{table} 缺少 v3 列（dna_id/perf_evaluated），先跑 published-track migrate-v3")

    metrics = metric_columns(conn, table)
    today = date.today()
    cutoff = (today - timedelta(days=args.mature_days)).isoformat()

    # ── 模式 3：标记已评估 ──
    if args.mark_evaluated:
        ids = [x.strip() for x in args.ids.split(",") if x.strip()]
        if not ids:
            die("--mark-evaluated 需要 --ids 1,2,3")
        bad = [i for i in ids if not i.isdigit()]
        if bad:
            die(f"非法 id: {bad}")
        marks = ",".join(ids)
        cur = conn.execute(f"UPDATE {table} SET perf_evaluated=1 WHERE id IN ({marks})")
        conn.commit()
        print(json.dumps({"ok": True, "mode": "mark_evaluated", "platform": args.platform,
                          "marked": cur.rowcount, "ids": [int(i) for i in ids]}, ensure_ascii=False))
        return

    pending_where = "dna_id IS NOT NULL AND dna_id != '' AND perf_evaluated=0 AND publish_date <= ?"

    # ── 模式 1：廉价阈值检查 ──
    if args.check:
        rows = conn.execute(
            f"SELECT dna_id, COUNT(*) AS n FROM {table} WHERE {pending_where} GROUP BY dna_id ORDER BY n DESC",
            (cutoff,),
        ).fetchall()
        dnas = []
        for r in rows:
            dnas.append({"dna_id": r["dna_id"], "pending": r["n"],
                         "triggered": r["n"] >= args.min_samples})
        print(json.dumps({"ok": True, "mode": "check", "platform": args.platform,
                          "mature_cutoff": cutoff, "min_samples": args.min_samples,
                          "dnas": dnas}, ensure_ascii=False))
        return

    # ── 模式 2：聚合 ──
    if args.dna_id:
        target_dnas = [args.dna_id]
    else:
        rows = conn.execute(
            f"SELECT dna_id, COUNT(*) AS n FROM {table} WHERE {pending_where} GROUP BY dna_id",
            (cutoff,),
        ).fetchall()
        target_dnas = [r["dna_id"] for r in rows if args.force or r["n"] >= args.min_samples]

    if not target_dnas:
        print(json.dumps({"ok": True, "mode": "aggregate", "platform": args.platform,
                          "mature_cutoff": cutoff, "min_samples": args.min_samples,
                          "dnas": [], "note": "无触发 DNA（未达阈值或无待评估记录）"}, ensure_ascii=False))
        return

    out_dnas = []
    for dna_id in target_dnas:
        batch = conn.execute(
            f"SELECT * FROM {table} WHERE dna_id=? AND {pending_where} ORDER BY publish_date ASC, id ASC",
            (dna_id, cutoff),
        ).fetchall()
        if not batch:
            continue
        total_published = conn.execute(
            f"SELECT COUNT(*) AS n FROM {table} WHERE dna_id=?", (dna_id,)
        ).fetchone()["n"]

        records_out = []
        for rec in batch:
            acct = rec["account"] or UNKNOWN_ACCOUNT
            # 同账号「此前」的作品（发布日更早；同日按 id 更早），最多 baseline_window 篇
            priors = conn.execute(
                f"""SELECT {",".join(metrics)} FROM {table}
                    WHERE COALESCE(account,'') = COALESCE(?, '')
                      AND (publish_date < ? OR (publish_date = ? AND id < ?))
                    ORDER BY publish_date DESC, id DESC LIMIT ?""",
                (rec["account"], rec["publish_date"], rec["publish_date"], rec["id"],
                 args.baseline_window),
            ).fetchall()
            acct_ctx = conn.execute(
                f"""SELECT COUNT(*) AS n, MIN(publish_date) AS first_date FROM {table}
                    WHERE COALESCE(account,'') = COALESCE(?, '')""",
                (rec["account"],),
            ).fetchone()
            entry = {
                "id": rec["id"], "title": rec["title"], "source_folder": rec["source_folder"],
                "publish_date": rec["publish_date"],
                "account": acct if acct != UNKNOWN_ACCOUNT else None,
                "account_total_published": acct_ctx["n"],
                "account_first_publish": acct_ctx["first_date"],
                "metrics": {m: (rec[m] or 0) for m in metrics},
            }
            if len(priors) < MIN_BASELINE_PRIORS:
                entry["baseline_insufficient"] = True
                entry["baseline"] = None
                entry["ratios"] = None
                entry["prior_count"] = len(priors)
            else:
                entry["baseline_insufficient"] = False
                entry["prior_count"] = len(priors)
                baseline, ratios = {}, {}
                for m in metrics:
                    vals = [(p[m] or 0) for p in priors]
                    base = sum(vals) / len(vals)
                    baseline[m] = round(base, 2)
                    ratios[m] = round((rec[m] or 0) / base, 3) if base > 0 else None
                entry["baseline"] = baseline
                entry["ratios"] = ratios
            records_out.append(entry)

        # 趋势：仅用基线充足的记录，按时间序对比值做最小二乘斜率
        trends, trend_insufficient = {}, []
        enough = [r for r in records_out if not r.get("baseline_insufficient")]
        for m in metrics:
            pts = [r["ratios"][m] for r in enough if r["ratios"] and r["ratios"][m] is not None]
            if len(pts) < MIN_TREND_POINTS:
                trend_insufficient.append(m)
                continue
            n = len(pts)
            xs = list(range(n))
            mx, my = sum(xs) / n, sum(pts) / n
            denom = sum((x - mx) ** 2 for x in xs)
            slope = sum((x - mx) * (y - my) for x, y in zip(xs, pts)) / denom if denom else 0.0
            direction = "up" if slope > SLOPE_EPSILON else ("down" if slope < -SLOPE_EPSILON else "flat")
            trends[m] = {"direction": direction, "slope": round(slope, 4),
                         "points": n, "mean_ratio": round(my, 3)}

        out_dnas.append({
            "dna_id": dna_id,
            "pending_count": len(records_out),
            "total_published": total_published,
            "records": records_out,
            "trends": trends,
            "trend_insufficient": trend_insufficient,
        })

    print(json.dumps({
        "ok": True, "mode": "aggregate", "platform": args.platform,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "params": {"min_samples": args.min_samples, "mature_days": args.mature_days,
                   "baseline_window": args.baseline_window, "mature_cutoff": cutoff,
                   "forced": args.force},
        "metrics": metrics,
        "dnas": out_dnas,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
