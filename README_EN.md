# AI Chief Intelligence Officer (Wiseflow)

**[简体中文](README.md) | [English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/TeamWiseFlow/wiseflow)

🚀 **Use large language models to track the information you care about most daily from various sources!**

Wiseflow intelligently monitors and tracks various network sources, including mainstream social media, websites, RSS, and search engines, and intelligently extracts the information you are most concerned about.

## 🎉 WiseFlow Pro Version Now Available!

Stronger crawling capabilities, more comprehensive social media support, includes a Web UI, and a one-click installation package!

https://github.com/user-attachments/assets/880af7a3-7b28-44ff-86b6-aaedecd22761

🔥🔥 **Pro version is now available worldwide**: https://shouxiqingbaoguan.com/ 

🌹 From today, contributors who submit PRs to the Wiseflow open-source version (code, documentation, and success case sharing are all welcome) will receive a one-year subscription to Wiseflow Pro upon acceptance!

## Wiseflow 4.30 Open Source Version

The Wiseflow open-source version has been upgraded to the same architecture as the Pro version, featuring the same API, and can seamlessly share the [wiseflow+](https://github.com/TeamWiseFlow/wiseflow-plus) ecosystem!

## Sponsors

Powered By <a href="https://www.baotianqi.cn" target="_blank"><img src="./docs/logos/tianqibao.png" alt="Tianqibao" height="40"/></a>

[Thordata](https://www.thordata.com/products/serp-api?ls=github&lk=wiseflow): Get Reliable Global Proxies at an Unbeatable Value. One-click data collection with enterprise-grade stability and compliance. Join thousands of developers using ThorData for high-scale operations. 

🎁 Exclusive Offer: Sign up for a free Residential Proxy trial and 2,000 FREE SERP API calls!

<a href="https://www.thordata.com/products/serp-api?ls=github&lk=wiseflow" target="_blank"><img src="./docs/logos/thordata_en.png" alt="Thordata" height="120"/></a>

## Comparison between Wiseflow Open Source and Pro Versions

| Feature | Open Source | Pro Version |
| :--- | :---: | :---: |
| **Monitored Sources** | web, rss | web, rss, plus 7 major Chinese self-media platforms |
| **Search Sources** | bing, github, arxiv | bing, github, arxiv, plus 6 major Chinese self-media platforms |
| **Installation** | Manual environment setup and deployment | No installation needed, one-click run |
| **User Interface** | No UI | Chinese web UI |
| **LLM Cost** | User-provided LLM service or local LLM | Subscription includes LLM costs (no config needed) |
| **Technical Support** | GitHub Issues | WeChat group for paid users |
| **Price** | Free | ￥488/year |
| **Target Audience** | Community exploration and learning | Daily use (Individual or Enterprise) |

## 🧐 Wiseflow Positioning

Wiseflow is not a general-purpose agent like ChatGPT or Manus; it focuses on information monitoring and extraction, supporting user-specified sources with scheduled tasks to ensure the latest information is always obtained (supports up to 4 times a day, i.e., every 6 hours). Wiseflow also supports comprehensive information searching across specified platforms (e.g., "finding people").

However, do not equate Wiseflow with traditional crawlers or RPA! Wiseflow's acquisition behavior is entirely driven by LLM, using real browsers (instead of headless or virtual browsers), and its acquisition and extraction actions are performed simultaneously:

- Innovative HTML intelligent parsing mechanism: Automatically identifies key information and links worth exploring further.
- "Crawl-and-Search-in-One" strategy: Real-time LLM judgment and extraction during crawling, capturing only relevant information, significantly reducing risk control risks.
- Truly ready to use: No need for Xpath, scripts, or manual configuration. Ordinary users can easily use it.

    ……

For more, please refer to: https://shouxiqingbaoguan.com/

## 🌟 Quick Start

**Get started in just three steps!**

**From version 4.2 onwards, Google Chrome must be installed (using the default installation path).**

**Windows users, please download the Git Bash tool in advance and execute the following commands in bash. [Bash Download Link](https://git-scm.com/downloads/win)**

### 📋 Install environment management tool uv and download Wiseflow source code

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

The above operation will complete the installation of uv and download the Wiseflow source code.

### 📥 Configure .env file based on env_sample

In the wiseflow folder (project root directory), create a .env file based on env_sample and fill in the relevant settings (mainly LLM service configuration).

**The Wiseflow open-source version requires users to configure their own LLM service.**

Wiseflow does not limit model service providers, as long as the service is compatible with the OpenAI SDK request interface format. You can choose existing MaaS services or locally deployed model services like Ollama.

For users in Mainland China, we recommend using the Siliconflow model service.

😄 Feel free to use my [referral link](https://cloud.siliconflow.cn/i/WNLYbBpi) to apply—both you and I will receive a ￥14 platform reward.

If you prefer to use overseas closed-source models such as OpenAI, you can use the AiHubMix model service, which works smoothly in Mainland China:

😄 You are welcome to register with my [AiHubMix invitation link](https://aihubmix.com?aff=Gp54).

Overseas users can use the international version of Siliconflow: https://www.siliconflow.com/

### 🚀 Take Off!

```bash
cd wiseflow
uv venv # only needed the first time
source .venv/bin/activate  # Linux/macOS
# or on Windows:
# .venv\Scripts\activate
uv sync # only needed the first time
python core/entry.py
```

## 📚 How to use data crawled by Wiseflow in your own programs

Refer to [wiseflow backend api](./core/backend/README.md)

Whether based on Wiseflow or Wiseflow Pro, we welcome you to share and promote your application cases in the following repo!

- https://github.com/TeamWiseFlow/wiseflow-plus

(Contributing PRs to this repo will also grant a one-year subscription to Wiseflow Pro upon acceptance)

**The architecture of version 4.2x is not fully compatible with 4.30. The final version of 4.2x (v4.29) is no longer maintained. For code reference, you can switch to the "2025" branch.**

## 🛡️ License

Since version 4.2, we have updated the open-source license agreement. Please check: [LICENSE](LICENSE) 

For commercial cooperation, please contact **Email: zm.zhao@foxmail.com**

## 📬 Contact

For any questions or suggestions, welcome to leave a message through [issue](https://github.com/TeamWiseFlow/wiseflow/issues).

For Pro version requirements or cooperation feedback, please contact the "Manager" of AI Chief Intelligence Officer via WeChat:

<img src="docs/wechat.jpg" alt="wechat" width="360">

## 🤝 This Project is Based on the Following Excellent Open Source Projects:

- Crawl4ai (Open-source LLM Friendly Web Crawler & Scraper) https://github.com/unclecode/crawl4ai
- Patchright (Undetected Python version of the Playwright testing and automation library) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- MediaCrawler (xhs/dy/wb/ks/bilibili/zhihu crawler) https://github.com/NanmiCoder/MediaCrawler
- NoDriver (Providing a blazing fast framework for web automation, webscraping, bots and any other creative ideas...) https://github.com/ultrafunkamsterdam/nodriver
- Feedparser (Parse feeds in Python) https://github.com/kurtmckee/feedparser
- SearXNG (A free internet metasearch engine which aggregates results from various search services and databases) https://github.com/searxng/searxng

## Citation

If you reference or cite part or all of this project in related work, please note the following information:

```
Author: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## Friendly Links

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)
