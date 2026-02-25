# Wiseflow

**[中文](README.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

🚀 **STEP INTO 5.x**

> 📌 **Looking for 4.x?** The original v4.30 and earlier code is available on the [`4.x` branch](https://github.com/TeamWiseFlow/wiseflow/tree/4.x).

```
"My life has a limit, but knowledge has none. To pursue the limitless with the limited — that is perilous!" — Zhuangzi, Inner Chapters, Nourishing the Lord of Life
```

Wiseflow 4.x (and earlier versions) achieved powerful data acquisition capabilities in specific scenarios through a series of precisely engineered workflows, but still had significant limitations:

- 1. Unable to acquire interactive content (content that only appears after clicking, especially in dynamically loaded scenarios)
- 2. Limited to information filtering and extraction, with virtually no downstream task capabilities
- ……

Although we have been dedicated to improving its functionality and expanding its boundaries, the real world is complex, and so is the real internet. Rules can never be exhaustive, so a fixed workflow can never adapt to all scenarios. This is not a problem with wiseflow — it's a problem with traditional software!

However, the rapid advancement of Agents over the past year has shown us the technical possibility of fully simulating human internet behavior driven by large language models. The emergence of [openclaw](https://github.com/openclaw/openclaw) has further strengthened this belief.

What's even more remarkable is that through our early experiments and exploration, we discovered that integrating wiseflow's acquisition capabilities into openclaw as "plugins" perfectly solves the two limitations mentioned above. We will be releasing exciting real demo videos soon, along with open-sourcing these "plugins".

It should be noted, however, that openclaw's plugin system is quite different from what we traditionally understand as "plugins" (similar to Claude Code's plugins). Therefore, we had to introduce the concept of "add-on". To be precise, wiseflow 5.x will appear in the form of an openclaw add-on. The original openclaw does not have an "add-on" architecture, but in practice, you only need a few simple shell commands to complete this "transformation". We have also prepared a ready-to-use enhanced version of openclaw with a series of preset configurations for real business scenarios: [openclaw_for_business](https://github.com/TeamWiseFlow/openclaw_for_business). You can simply clone it and extract the wiseflow release into the add-on folder of openclaw_for_business.

## 🌟 Quick Start

Copy this directory to the `addons/` directory of openclaw_for_business:

```bash
# Option 1: Clone from the wiseflow repository
git clone https://github.com/TeamWiseFlow/wiseflow.git /tmp/wiseflow
cp -r /tmp/wiseflow/addon <openclaw_for_business>/addons/wiseflow

# Option 2: If you already have the wiseflow repository
Download the latest release from https://github.com/TeamWiseFlow/wiseflow/releases
Extract and place it in <openclaw_for_business>/addons
```

Restart openclaw after installation to take effect.

## Directory Structure

```
addon/
├── addon.json                    # Metadata
├── overrides.sh                  # pnpm overrides: playwright-core → patchright-core
├── patches/
│   └── 001-browser-tab-recovery.patch  # Tab recovery patch
├── skills/
│   └── browser-guide/SKILL.md    # Browser usage best practices
├── docs/                         # Technical documentation
│   ├── anti-detection-research.md
│   └── openclaw-extension-architecture.md
└── tests/                        # Test cases and scripts
    ├── README.md
    └── run-managed-tests.mjs
```

## WiseFlow Pro is Now Available!

Stronger scraping capabilities, more comprehensive social media support, with UI interface and one-click installation package — no deployment needed!

https://github.com/user-attachments/assets/57f8569c-e20a-4564-a669-1200d56c5725

🔥 **Pro version is now on sale**: https://shouxiqingbaoguan.com/

🌹 Starting today, contribute PRs to the wiseflow open-source version (code, documentation, and successful case studies are all welcome). Once accepted, contributors will receive a one-year license for wiseflow Pro!

📥 🎉 📚

## 🛡️ License

Since version 4.2, we have updated our open-source license. Please refer to: [LICENSE](LICENSE)

For commercial cooperation, please contact **Email: zm.zhao@foxmail.com**

## 📬 Contact

For any questions or suggestions, feel free to leave a message via [issue](https://github.com/TeamWiseFlow/wiseflow/issues).

For Pro version requirements or cooperation feedback, please contact the "AI Chief Intelligence Officer" via WeChat:

<img src="docs/wechat.jpg" alt="wechat" width="360">

## 🤝 wiseflow 5.x is built on the following excellent open-source projects:

- Patchright (Undetected Python version of the Playwright testing and automation library) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- Feedparser (Parse feeds in Python) https://github.com/kurtmckee/feedparser
- SearXNG (a free internet metasearch engine which aggregates results from various search services and databases) https://github.com/searxng/searxng

## Citation

If you reference or cite part or all of this project in your work, please include the following information:

```
Author: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## Partners

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)
