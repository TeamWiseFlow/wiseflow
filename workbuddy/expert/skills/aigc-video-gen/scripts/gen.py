#!/usr/bin/env python3
"""[DEPRECATED] 已拆分为 gen_minimax.py / gen_volc.py / gen_dashscope.py。

本文件仅为兼容旧引用保留，实际逻辑已迁移到三供应商独立脚本。
sh 层（aigc-video-gen.sh）会根据 --platform 或 env 自动 dispatch 到对应脚本。
"""
import sys

print(
    "[error] gen.py 已废弃，逻辑拆分为 gen_minimax.py / gen_volc.py / gen_dashscope.py。\n"
    "        请通过 aigc-video-gen.sh 调用，sh 会自动 dispatch 到对应供应商脚本。",
    file=sys.stderr,
)
sys.exit(1)
