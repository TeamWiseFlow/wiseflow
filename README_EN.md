# AI Chief Intelligence Officer (Wiseflow)

**[简体中文](README.md) | [English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/TeamWiseFlow/wiseflow)

🚀 **Use large language models to mine information you're truly interested in from massive data and various sources daily!**

What we lack is not information, but the ability to filter out noise from massive information to reveal valuable insights.

https://github.com/user-attachments/assets/48998353-6c6c-4f8f-acae-dc5c45e2e0e6


## 🔥🔥🔥 Wiseflow 4.2 Version Officially Released!

Version 4.2 significantly enhances web crawling capabilities based on versions 4.0 and 4.1. The program can now directly call your local "real" Chrome browser for fetching. This not only maximizes the reduction of being "risk-controlled" by target sites, but also brings new features such as persistent user data and support for page operation scripts! (For example, some websites require user login to display complete content, you can now pre-login and then use wiseflow to get complete content).

Since version 4.2 directly uses your local Chrome browser for crawling, you no longer need to execute `python -m playwright install --with-deps chromium` during deployment, but you need to **install Google Chrome browser using the default installation path**.

In addition, we have also refactored the search engine solution and provided a complete proxy solution. For details, see **[CHANGELOG](CHANGELOG.md)**

### 🔍 Custom Search Sources

Version 4.1 supports precise configuration of search sources for focus points. It currently supports bing, github, and arxiv search sources, all using native platform interfaces without requiring additional third-party services.

<img src="docs/select_search_source.gif" alt="search_source" width="360">


### 🧠 Let the AI Think from Your Perspective!

Version 4.1 supports setting roles and objectives for focus points to guide the LLM in analyzing and extracting information from a specific perspective or for a specific purpose. However, please note:

    - If the focus point itself is very specific, setting roles and objectives will have little impact on the results.
    - The most important factor affecting the quality of the final results is always the source of information. Be sure to provide sources that are highly relevant to the focus point.

For test cases on how setting roles and objectives affects extraction results, please refer to [task1](test/reports/report_v4x_llm/task1).


### ⚙️ Custom Extraction Mode

You can now create your own forms in the pb interface and configure them for specific focus points. The LLM will then extract information accurately according to the form fields.


### 👥 Creator Search Mode for Social Media Sources

You can now specify the program to find relevant content on social media platforms based on focus points, and further find the homepage information of the content creators. Combined with the "Custom Extraction Mode", wiseflow can help you search for potential customers, partners, or investors' contact information across the entire network.

<img src="docs/find_person_by_wiseflow.png" alt="find_person_by_wiseflow" width="720">


**For more update information on version 4.1, please see the [CHANGELOG](CHANGELOG.md)**

## 🌹 Best LLM Combination Guide

"In the LLM era, excellent developers should spend at least 60% of their time choosing the right LLM model" ☺️

We selected 7 test samples from real projects and extensively chose mainstream models with output prices not exceeding $0.6/M tokens, conducting detailed wiseflow info extracting task tests, and arrived at the following usage recommendations:

    - For performance-priority scenarios, we recommend: ByteDance-Seed/Seed-OSS-36B-Instruct

    - For cost-priority scenarios, we still recommend: Qwen/Qwen3-14B

For visual auxiliary analysis models, you can still use: Qwen/Qwen2.5-VL-7B-Instruct (wiseflow tasks currently have low dependency on this)

For detailed test reports, see [LLM USE TEST](./test/reports/README.md)

It should be noted that the above test results only represent the performance of models in wiseflow information extraction tasks and cannot represent the comprehensive capabilities of the models. Wiseflow information extraction tasks may be significantly different from other types of tasks (such as planning, writing, etc.). Additionally, cost is one of our key considerations because wiseflow tasks consume a large amount of model usage, especially in multi-source, multi-focus scenarios.

Wiseflow does not limit model service providers, as long as the service is compatible with openaiSDK request interface format. You can choose existing MaaS services or locally deployed model services like Ollama.

we recommend using [Siliconflow](https://www.siliconflow.com/) 's model service.

Alternatively, if you prefer openai series models, 'o3-mini' and 'openai/gpt-oss-20b' are also good choices, and visual auxiliary analysis can be paired with gpt-4o-mini.

💰 Currently, you can use OpenAI series model official interfaces forwarded by AiHubMix at 10% off the official price within the wiseflow application.

**Note:** To enjoy the discount, you need to switch to the aihubmix branch, see [README](https://github.com/TeamWiseFlow/wiseflow/blob/aihubmix/README.md) for details

## 🧐 'Deep Search' VS 'Wide Search'

I position Wiseflow as "wide search", which is relative to the currently popular "deep search".

Specifically, "deep search" is where LLM autonomously plans search paths for specific questions, continuously exploring different pages, collecting sufficient information to provide answers or generate reports. However, sometimes we don't search with specific questions and don't need in-depth exploration, just broad information collection (such as industry intelligence gathering, background information collection, customer information collection, etc.). In these cases, breadth is clearly more meaningful. While "deep search" can also accomplish this task, it's like using a cannon to kill a mosquito - inefficient and costly. Wiseflow is specifically designed for these "wide search" scenarios.

## ✋ What Makes Wiseflow Different from Other AI-Powered Crawlers?

- Full platform acquisition capabilities, including web pages, social media (currently supporting Weibo and Kuaishou platforms), RSS feeds, and search sources such as Bing, GitHub, arXiv, and eBay, etc.;
- Unique HTML processing workflow that automatically extracts information based on focus points and discovers links worth further exploration, working well with just a 14b parameter LLM;
- User-friendly (not just for developers), no need for manual Xpath configuration, "ready to use";
- High stability and availability through continuous iteration, and processing efficiency that balances system resources and speed;
- It will be more than just a "crawler"...

<img src="docs/wiseflow4.xscope.png" alt="4.x full scope" width="720">

(4.x architecture overall scope. The dashed box indicates the unfinished parts. We hope capable community developers will join us and contribute PRs. All contributors will receive free access to the pro version!)

## 🌟 Quick Start

**Just three steps to get started!**

**Starting from version 4.2, you must first install Google Chrome browser (using the default installation path)**

**Windows users please download Git Bash tool in advance and execute the following commands in bash [Bash Download Link](https://git-scm.com/downloads/win)**

### 📋 Download Project Source Code and Install uv and pocketbase

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

The above operations will complete the installation of uv. 

Next, go to [pocketbase docs](https://pocketbase.io/docs/) to download the corresponding pocketbase program for your system and place it in the [.pb](./pb/) folder.

You can also try using install_pocketbase.sh (for MacOS/Linux) or install_pocketbase.ps1 (for Windows) to install.

### 📥 Configure .env File Based on env_sample

In the wiseflow folder (project root directory), create a .env file based on env_sample and fill in the relevant settings

Version 4.x does not require users to provide pocketbase credentials in .env, nor does it restrict pocketbase version. Additionally, we have temporarily removed the Secondary Model setting. Therefore, you only need a minimum of four parameters to complete the configuration:

- LLM_API_KEY="" # LLM service key (any model provider offering OpenAI format API, not required if using ollama locally)
- LLM_API_BASE="" 
- PRIMARY_MODEL=ByteDance-Seed/Seed-OSS-36B-Instruct #model you used
- VL_MODEL=Pro/Qwen/Qwen2.5-VL-7B-Instruct # better to have

### 🚀 Take Off!

```bash
cd wiseflow
uv venv # only needed the first time
source .venv/bin/activate  # Linux/macOS
# or Windows:
# .venv\Scripts\activate
uv sync # only needed the first time
chmod +x run.sh # only needed the first time
./run.sh
```

For detailed usage instructions, please refer to [docs/manual/manual_en.md](./docs/manual/manual_en.md)

## 📚 How to Use Data Crawled by Wiseflow in Your Own Programs

All data crawled by Wiseflow will be instantly stored in pocketbase, so you can directly operate the pocketbase database to obtain data.

As a popular lightweight database, PocketBase currently has SDKs for Go/Javascript/Python and other languages.

Welcome to share and promote your secondary development application examples in the following repo!

- https://github.com/TeamWiseFlow/wiseflow_plus

## 🛡️ License

Starting from version 4.2, we have updated the open source license agreement, please check: [LICENSE](LICENSE)

For commercial cooperation, please contact **Email: zm.zhao@foxmail.com**

## 📬 Contact

For any questions or suggestions, welcome to leave a message through [issue](https://github.com/TeamWiseFlow/wiseflow/issues).

## 🤝 This Project is Based on the Following Excellent Open Source Projects:

- Crawl4ai (Open-source LLM Friendly Web Crawler & Scraper) https://github.com/unclecode/crawl4ai
- MediaCrawler (xhs/dy/wb/ks/bilibili/zhihu crawler) https://github.com/NanmiCoder/MediaCrawler
- Patchright(Undetected Python version of the Playwright testing and automation library) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- NoDriver (Providing a blazing fast framework for web automation, webscraping, bots and any other creative ideas...) https://github.com/ultrafunkamsterdam/nodriver
- Pocketbase (Open Source realtime backend in 1 file) https://github.com/pocketbase/pocketbase
- Feedparser (Parse feeds in Python) https://github.com/kurtmckee/feedparser
- SearXNG（a free internet metasearch engine which aggregates results from various search services and databases） https://github.com/searxng/searxng

## Citation

If you reference or cite part or all of this project in related work, please note the following information:

```
Author: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## Friendly Links

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)