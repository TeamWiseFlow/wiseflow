"""runtime_root.py — 把 Path(__file__).resolve() 算出的 ROOT 映射回 OpenClaw 运行时工作区。

背景：部署到 ``~/.xiaobei-workbuddy/workspace-<crew>/skills/<name>`` 的 skill 是指向源仓
``~/wiseflow/crews/<crew>/skills/<name>`` 的 symlink。脚本的 ``Path(__file__).resolve()``
会跟随 symlink 跳进源仓，导致 ROOT 指向源仓而非运行时工作区——DB / dna-meta.json /
DNA 评估报告等运行时数据都在工作区下，源仓里没有，于是全部 ``exists()=False``。

本 helper 按 marker 文件是否存在判定，把 ROOT 映射回 ``~/.xiaobei-workbuddy/workspace-<crew>``。
"""
from __future__ import annotations

import os
from pathlib import Path


def resolve_runtime_root(
    naive_root: Path,
    marker: str = "db/published_track.db",
    env_var: str = "PUBLISHED_TRACK_ROOT",
) -> Path:
    """返回运行时 ROOT（marker 文件所在的工作区）。

    判定顺序：
      1. ``env_var`` 显式指定 → 直接用（最高优先级，供部署/调试覆盖）。
      2. ``naive_root`` 下 marker 存在 → 未 symlink / 源仓内直跑，用 naive_root。
      3. 从 ``naive_root`` 路径里解析 ``crews/<crew>`` → ``~/.xiaobei-workbuddy/workspace-<crew>``，
         该目录下 marker 存在则用之（symlink 部署的常规情况）。
      4. 都不命中 → 原样返回 naive_root（让调用方以清晰的 missing-DB 报错）。
    """
    env = os.environ.get(env_var)
    if env:
        return Path(env).expanduser()

    if (naive_root / marker).exists():
        return naive_root

    parts = naive_root.parts
    for i, part in enumerate(parts):
        if part == "crews" and i + 1 < len(parts):
            crew = parts[i + 1]
            cand = (Path(os.environ.get("XIAOBEI_WORKBUDDY_HOME", Path.home() / ".xiaobei-workbuddy"))) / f"workspace-{crew}"
            if (cand / marker).exists():
                return cand
            break

    return naive_root
