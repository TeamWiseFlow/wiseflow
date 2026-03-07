# 1、按 README.md 更新其他语种 readme

# 2、更新 .github/workflows/ 的 release 流程

## 触发机制：

**upstream**（TeamWiseflow 正式仓库）每次合并 PR 后通过 github actions 自动更新版本号并触发 release 打包发布

## 具体工作机制

分别从 https://github.com/openclaw/openclaw 和 https://github.com/TeamWiseFlow/openclaw_for_business 拉取最新代码，拉取后按如下结构放置：

```
openclaw_for_business/
├── addons/
│   └── wiseflow/   # 本项目代码仓内的 wiseflow/ 注意：不是整个项目目录
└── openclaw/
    └── 
```

使用 github action 分别在最新的 ubuntu24.04、macos-latest 两个系统上进行端到端完整测试，保证执行`openclaw_for_business/scripts/reinstall-daemon.sh`脚本没问题后，直接连同 openclaw_for_business 和 openclaw 代码，保持上面的放置结构，打包为一个 zip 压缩包，发布到本代码仓的 release