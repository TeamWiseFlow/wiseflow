# Wiseflow

**[English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

🚀 **STEP INTO 5.x**

> 📌 **寻找 4.x 版本？** 原版 v4.30 及之前版本的代码在 [`4.x` 分支](https://github.com/TeamWiseFlow/wiseflow/tree/4.x)中。

```
“吾生也有涯，而知也无涯。以有涯随无涯，殆已！“ —— 《庄子·内篇·养生主第三》
```

wiseflow 4.x(包括之前的版本) 通过一系列精密的 workflow 实现了在特定场景下的强大的获取能力，但依然存在诸多局限性：

- 1. 无法获取交互式内容（需要经过点选才能出现的内容，尤其是动态加载的情况）
- 2. 只能进行信息过滤与提取，几乎没有任何下游任务能力
- ……

虽然我们一直致力于完善它的功能、扩增它的边界，但真实世界是复杂的，真实的互联网也一样，规则永无可能穷尽，因此固定的 workflow 永远做不到适配所有场景，这不是 wiseflow 的问题，这是传统软件的问题！

然而过去一年 Agent 的突飞猛进，让我们看到了由大模型驱动完全模拟人类互联网行为在技术上的可能，[openclaw](https://github.com/openclaw/openclaw) 的出现更让我们坚定了此信念。

更奇妙的是，通过前期的实验和探索，我们发现将 wiseflow 的获取能力以”插件“形式融入 openclaw，即可以完美解决上面提到的两个局限性。我们接下来会陆续放出激动人心的真实 demo 视频，同时开源发布这些”插件“。

不过需要说明的是，openclaw 的 plugin 系统与传统上我们理解的“插件”（类似 claude code 的 plugin）并不相同，因此我们不得不额外提出了“add-on"的概念，所以确切的说，wiseflow5.x 将以 openclaw add-on 的形态出现。原版的 openclaw 并不具有”add-on“架构，不过实际上，你只需要几条简单的 shell 命令即可完成这个”改造“。我们也准备了开箱即用、同时包含一系列针对真实商用场景预设配置的 openclaw 强化版本，即 [openclaw_for_business](https://github.com/TeamWiseFlow/openclaw_for_business), 你可以直接 clone ，并将 wiseflow release 解压缩放置于 openclaw_for_business 的 add-on 文件夹内即可。

## 🌟 快速开始

将本目录复制到 openclaw_for_business 的 `addons/` 目录：

```bash
# 方式一：从 wiseflow 仓库复制
git clone https://github.com/TeamWiseFlow/wiseflow.git /tmp/wiseflow
cp -r /tmp/wiseflow/addon <openclaw_for_business>/addons/wiseflow

# 方式二：如果已有 wiseflow 仓库
从 https://github.com/TeamWiseFlow/wiseflow/releases 下载最新的发布
解压缩后放入 <openclaw_for_business>/addons
```

安装后重启 openclaw 即可生效。

## 目录结构

```
addon/
├── addon.json                    # 元数据
├── overrides.sh                  # pnpm overrides: playwright-core → patchright-core
├── patches/
│   └── 001-browser-tab-recovery.patch  # 标签页恢复补丁
├── skills/
│   └── browser-guide/SKILL.md    # 浏览器使用最佳实践
├── docs/                         # 技术文档
│   ├── anti-detection-research.md
│   └── openclaw-extension-architecture.md
└── tests/                        # 测试用例和脚本
    ├── README.md
    └── run-managed-tests.mjs
```

##  WiseFlow Pro 版本现已发布！

更强的抓取能力、更全面的社交媒体支持、含 UI 界面和免部署一键安装包！

https://github.com/user-attachments/assets/57f8569c-e20a-4564-a669-1200d56c5725

🔥 **Pro 版本现已面向全网发售**：https://shouxiqingbaoguan.com/ 

🌹 即日起为 wiseflow 开源版本贡献 PR（代码、文档、成功案例分享均欢迎），一经采纳，贡献者将获赠 wiseflow pro版本一年使用权！

📥 🎉 📚

## 🛡️ 许可协议

自4.2版本起，我们更新了开源许可协议，敬请查阅： [LICENSE](LICENSE) 

商用合作，请联系 **Email：zm.zhao@foxmail.com**

## 📬 联系方式

有任何问题或建议，欢迎通过 [issue](https://github.com/TeamWiseFlow/wiseflow/issues) 留言。

有关 pro 版本的需求或合作反馈，欢迎联系 AI首席情报官“掌柜”企业微信：

<img src="docs/wechat.jpg" alt="wechat" width="360">

## 🤝 wiseflow5.x 基于如下优秀的开源项目：

- Patchright(Undetected Python version of the Playwright testing and automation library) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- Feedparser（Parse feeds in Python） https://github.com/kurtmckee/feedparser
- SearXNG（a free internet metasearch engine which aggregates results from various search services and databases） https://github.com/searxng/searxng

## Citation

如果您在相关工作中参考或引用了本项目的部分或全部，请注明如下信息：

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## 友情链接

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)
