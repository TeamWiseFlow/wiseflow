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

What's even more remarkable is that through our early experiments and exploration, we discovered that integrating wiseflow's acquisition capabilities into openclaw as "plugins" perfectly solves the two limitations mentioned above.

https://github.com/user-attachments/assets/8d097b3b-f9ab-42eb-98bb-88af5d28b089

It should be noted that openclaw's plugin system is quite different from what we traditionally understand as "plugins" (similar to Claude Code's plugins). Therefore, we had to introduce the concept of "add-on". To be precise, wiseflow 5.x will appear in the form of an openclaw add-on. The original openclaw does not have an "add-on" architecture, but in practice, you only need a few simple shell commands to complete this "transformation". We have also prepared a ready-to-use enhanced version of openclaw with a series of preset configurations for real business scenarios: [openclaw_for_business](https://github.com/TeamWiseFlow/openclaw_for_business). You can simply clone it and extract the wiseflow release into the add-on folder of openclaw_for_business.

## ✨ What Do You Gain by Installing wiseflow (Superior to Vanilla openclaw)?

### 1. Anti-Detection Browser, No Browser Extensions Required

wiseflow's patch-001 replaces openclaw's built-in Playwright with [Patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright) (an undetected fork of Playwright), significantly reducing the likelihood of automated browsers being identified and blocked by target websites. This means that without installing the Chrome relay extension, a managed browser alone can achieve the same — or even better — web acquisition and operation capabilities as a relay setup.

📥 *We evaluated all major browser automation frameworks currently available, including nodriver, browser-use, and Vercel's agent-browser. We can confirm that while they all operate through CDP and provide persistent openclaw-specific profiles, only Patchright delivers complete removal of CDP fingerprints. In other words, even the most direct CDP connection approach still carries detectable signatures. Other frameworks are designed for automated testing, not for data acquisition, whereas Patchright was specifically built for acquisition. Since it is essentially a patch on top of Playwright, it inherits nearly all of Playwright's high-level APIs — making it natively compatible with openclaw without requiring any additional extensions or MCP.*

### 2. Automatic Tab Recovery Mechanism

When a target browser tab is unexpectedly closed or lost during an Agent operation, the system automatically performs snapshot-based tab recovery, ensuring tasks are not interrupted by tab loss.

### 3. Smart Search Skill

Replaces openclaw's built-in `web_search` with more powerful search capabilities. Compared to the original built-in web search tool, Smart Search has three core advantages:

- **Completely free, no API key required**: Does not rely on any third-party search APIs — zero cost
- **Real-time search for maximum timeliness**: Directly drives the browser to target pages or major social media platforms (Weibo, Twitter/X, Facebook, etc.) to search for the latest published content
- **User-configurable search sources**: Users can freely specify their search sources for precise, targeted information retrieval

### 4. New Media Editor Crew (Preset AI Agent)

A ready-to-use Chinese social media content creation AI Agent, focused on major Chinese platforms including Weibo, Xiaohongshu, Zhihu, Bilibili, and Douyin.

**Key capabilities:**

- Topic research + trending analysis (Mode A)
- Draft expansion + online fact support (Mode B)
- After article finalization, automatically invokes [Wenyan](https://github.com/caol64/wenyan) to render WeChat public account-style HTML with 7 built-in themes
- Direct push to WeChat public account draft box (Mode C, requires `WECHAT_APP_ID`/`WECHAT_APP_SECRET`)
- AI image/video generation support ([SiliconFlow](https://www.siliconflow.com/) image/video generation, requires `SILICONFLOW_API_KEY`)

## 🌟 Quick Start

> **💡 API Cost Note**
>
> wiseflow 5.x is powered by openclaw's Agent workflow, which requires LLM API access. We recommend preparing your API credentials first:
>
> - **International users (recommended)**: [SiliconFlow](https://www.siliconflow.com/) — free credits available after registration, covering initial usage costs
> - **OpenAI / Anthropic and other providers**: Any compatible API works

Download the integrated package (which includes openclaw_for_business and the wiseflow addon) directly from this repository's [Releases](https://github.com/TeamWiseFlow/wiseflow/releases).

1. Download and extract the archive
2. Enter the extracted directory
3. Choose your startup mode:

   **Debug mode** (single startup, for testing and development):
   ```bash
   ./scripts/dev.sh gateway
   ```

   **Production mode** (install as a system service for long-term operation):
   ```bash
   ./scripts/reinstall-daemon.sh
   ```

> **System Requirements**
> - **Ubuntu 22.04** is recommended
> - **Windows WSL2** environment is supported
> - **macOS** is supported
> - Running directly on **native Windows** is **not supported**

### [Alternative] Manual Installation

> Note: You need to first download and deploy openclaw_for_business from: https://github.com/TeamWiseFlow/openclaw_for_business/releases

Copy the `wiseflow` folder from this repository (not the repository itself) to the `addons/` directory of openclaw_for_business:

```bash
# Option 1: Clone from the wiseflow repository
git clone https://github.com/TeamWiseFlow/wiseflow.git /tmp/wiseflow
cp -r /tmp/wiseflow/wiseflow <openclaw_for_business>/addons/wiseflow
```

Restart openclaw_for_business after installation to take effect.

## Directory Structure

```
wiseflow/                         # addon package (copy to addons/ directory)
├── addon.json                    # Metadata
├── overrides.sh                  # pnpm overrides + disable built-in web_search
├── patches/
│   ├── 001-browser-tab-recovery.patch        # Tab recovery patch
│   ├── 002-disable-web-search-env-var.patch  # Disable built-in web_search (env var)
│   └── 003-act-field-validation.patch        # ACT field validation patch
├── skills/                       # Global skills (available to all Agents)
│   ├── browser-guide/SKILL.md    # Browser best practices (login/captcha/lazy-loading, etc.)
│   ├── smart-search/SKILL.md     # Multi-platform search URL builder (replaces built-in web_search)
│   └── rss-reader/               # RSS/Atom Feed reader
│       ├── SKILL.md
│       ├── package.json
│       └── scripts/fetch-rss.mjs
└── crew/                         # Preset AI Agents (Crew templates)
    └── new-media-editor/         # New Media Editor (Chinese social media content creation)
        ├── IDENTITY.md / SOUL.md / AGENTS.md / TOOLS.md / ...
        └── skills/               # Crew-specific skills
            ├── siliconflow-img-gen/   # AI image generation (SiliconFlow API)
            ├── siliconflow-video-gen/ # AI video generation (SiliconFlow API)
            └── wenyan-formatter/      # Markdown → WeChat HTML / push draft

docs/                             # Technical documentation (repo root)
├── anti-detection-research.md
└── more_powerful_search_skill/

scripts/                          # Utility scripts (repo root)
└── generate-patch.sh

tests/                            # Test cases and scripts (repo root)
├── README.md
└── run-managed-tests.mjs
```

## WiseFlow Pro is Now Available!

Stronger scraping capabilities, more comprehensive social media support, with UI interface and one-click installation package — no deployment needed!

https://github.com/user-attachments/assets/57f8569c-e20a-4564-a669-1200d56c5725

🔥 **Pro version is now on sale**: https://shouxiqingbaoguan.com/

🌹 Starting today, contribute PRs to the wiseflow open-source version (code, documentation, and successful case studies are all welcome). Once accepted, contributors will receive a one-year license for wiseflow Pro!

## 🛡️ License

Since version 4.2, we have updated our open-source license. Please refer to: [LICENSE](LICENSE)

For commercial cooperation, please contact **Email: zm.zhao@foxmail.com**

## 📬 Contact

For any questions or suggestions, feel free to leave a message via [issue](https://github.com/TeamWiseFlow/wiseflow/issues).

🎉 wiseflow & OFB now offer a **paid knowledge base**, including step-by-step installation tutorials, exclusive application tips, and a **VIP WeChat group**:

Feel free to add "Keeper" on WeChat Enterprise for inquiries:

<img width="360" height="360" alt="wiseflow掌柜" src="https://github.com/user-attachments/assets/b013b3fd-546e-4176-b418-57bee419e761" />

🌹 Open source takes effort — thank you for your support!

## 🤝 wiseflow 5.x is built on the following excellent open-source projects:

- Patchright (Undetected Python version of the Playwright testing and automation library) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- Feedparser (Parse feeds in Python) https://github.com/kurtmckee/feedparser
- SearXNG (a free internet metasearch engine which aggregates results from various search services and databases) https://github.com/searxng/searxng
- Wenyan (multi-platform Markdown formatting and publishing tool, used by the New Media Editor Crew via the wenyan-formatter skill) https://github.com/caol64/wenyan

## Citation

If you reference or cite part or all of this project in your work, please include the following information:

```
Author: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## Partners

[<img src="https://github.com/TeamWiseFlow/wiseflow/raw/4.x/docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)
