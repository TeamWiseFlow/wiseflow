# AI Chief Intelligence Officer (Wiseflow)

**[简体中文](README.md) | [English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

🚀 **Use large language models to mine information you're truly interested in from massive data and various sources daily!**

What we lack is not information, but the ability to filter out noise from massive information to reveal valuable insights.

https://github.com/user-attachments/assets/48998353-6c6c-4f8f-acae-dc5c45e2e0e6

## 🔥🔥🔥 Wiseflow 4.1 Version Officially Released!

Version 4.1 brings many exciting new features on top of version 4.0!

### 🔍 Custom Search Sources

Version 4.1 supports precise configuration of search sources for focus points. It currently supports four search sources: bing, github, arxiv, and ebay, all using native platform interfaces without requiring additional third-party services.

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
- LLM_API_BASE="https://api.siliconflow.com/v1" # LLM service interface address
- PRIMARY_MODEL=Qwen/Qwen3-14B # Recommended Qwen3-14B or equivalent thinking model
- VL_MODEL=Pro/Qwen/Qwen2.5-VL-7B-Instruct # better to have

### 🚀 Take Off!

```bash
cd wiseflow
uv venv # only needed the first time
source .venv/bin/activate  # Linux/macOS
# or Windows:
# .venv\Scripts\activate
uv sync # only needed the first time
python -m playwright install --with-deps chromium # only needed the first time
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

This project is open source under [Apache2.0](LICENSE).

For commercial cooperation, please contact **Email: zm.zhao@foxmail.com**

- Commercial customers please contact us for registration, open source version promises to be free forever.

## 📬 Contact

For any questions or suggestions, welcome to leave a message through [issue](https://github.com/TeamWiseFlow/wiseflow/issues).

## 🤝 This Project is Based on the Following Excellent Open Source Projects:

- Crawl4ai (Open-source LLM Friendly Web Crawler & Scraper) https://github.com/unclecode/crawl4ai
- MediaCrawler (xhs/dy/wb/ks/bilibili/zhihu crawler) https://github.com/NanmiCoder/MediaCrawler
- NoDriver (Providing a blazing fast framework for web automation, webscraping, bots and any other creative ideas...) https://github.com/ultrafunkamsterdam/nodriver
- Pocketbase (Open Source realtime backend in 1 file) https://github.com/pocketbase/pocketbase
- Feedparser (Parse feeds in Python) https://github.com/kurtmckee/feedparser
- SearXNG（a free internet metasearch engine which aggregates results from various search services and databases） https://github.com/searxng/searxng

## Citation

If you reference or cite part or all of this project in related work, please note the following information:

```
Author: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```

## Friendly Links

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)