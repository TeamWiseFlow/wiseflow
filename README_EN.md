# AI Chief Intelligence Officer (Wiseflow)

**[简体中文](README.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

🚀 **Use large language models to mine information you're truly interested in from massive data and various sources daily!**

What we lack is not information, but the ability to filter out noise from massive information to reveal valuable insights.

## 🔥🔥🔥 Wiseflow 4.0 Version Officially Released!

https://github.com/user-attachments/assets/2c52c010-6ae7-47f4-bc1c-5880c4bd76f3

(Online service is currently not switched to 4.0 core due to technical reasons, we are accelerating the upgrade)

After three months of waiting, we are finally pleased to announce the official release of the wiseflow 4.0 version! This version introduces a completely new 4.x architecture, introduces support for social media sources, and brings many new features.

4.x includes WIS Crawler (deeply reconstructed and integrated based on Crawl4ai, MediaCrawler, and Nodriver), which now provides complete support for web pages and social media sources. The 4.0 version initially provides support for the Weibo and Kuaishou platforms, with plans to add other platforms gradually, including:
WeChat official accounts, Xiaohongshu, Douyin, Bilibili, Zhihu...

Other new features brought by the 4.x architecture include:

- New architecture, hybrid use of async and thread pools, greatly improving processing efficiency (while reducing memory consumption);
- Inherited Crawl4ai 0.6.3 version's dispatcher capabilities, providing more refined memory management;
- Deep integration of Pre-Process from version 3.9 and Crawl4ai's Markdown Generation process, avoiding duplicate processing;
- Optimized support for RSS sources;
- Optimized repository file structure, clearer and more compliant with contemporary Python project standards;
- Switched to using uv for dependency management and optimized requirement.txt file;
- Optimized startup scripts (providing Windows version), truly achieving "one-click startup";
- Optimized configuration and deployment process, backend program no longer depends on pocketbase service, therefore no need to provide pocketbase credentials in .env, and no version restrictions for pocketbase.

## 🧐 'Deep Search' VS 'Wide Search'

I position Wiseflow as "wide search", which is relative to the currently popular "deep search".

Specifically, "deep search" is where LLM autonomously plans search paths for specific questions, continuously exploring different pages, collecting sufficient information to provide answers or generate reports. However, sometimes we don't search with specific questions and don't need in-depth exploration, just broad information collection (such as industry intelligence gathering, background information collection, customer information collection, etc.). In these cases, breadth is clearly more meaningful. While "deep search" can also accomplish this task, it's like using a cannon to kill a mosquito - inefficient and costly. Wiseflow is specifically designed for these "wide search" scenarios.

## ✋ What Makes Wiseflow Different from Other AI-Powered Crawlers?

- Full platform acquisition capabilities, including web pages, social media (currently supporting Weibo and Kuaishou platforms), RSS sources, search engines, etc.;
- Not just crawling, but automatic analysis and filtering, working well with just a 14b parameter LLM;
- User-friendly (not just for developers), no coding required, "ready to use";
- High stability and availability through continuous iteration, and processing efficiency that balances system resources and speed;
- (Future) Ability to mine "hidden information" beneath acquired information through the insight module

……… We also look forward to interested developers joining us to build an AI Chief Intelligence Officer accessible to everyone!

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
- LLM_API_BASE="https://api.siliconflow.cn/v1" # LLM service interface address
- JINA_API_KEY="" # Search engine service key (Jina recommended, even available without registration for personal use)
- PRIMARY_MODEL="Qwen3-14B" # Recommended Qwen3-14B or equivalent thinking model

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

Online service will soon launch sync API, supporting synchronization of online crawling results to local, for building "dynamic knowledge bases" and more, stay tuned:

  - Online experience address: https://www.aiqingbaoguan.com/
  - Online service API usage examples: https://github.com/TeamWiseFlow/wiseflow_plus

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

This project's development was inspired by [GNE](https://github.com/GeneralNewsExtractor/GeneralNewsExtractor), [AutoCrawler](https://github.com/kingname/AutoCrawler), and [SeeAct](https://github.com/OSU-NLP-Group/SeeAct).

## Citation

If you reference or cite part or all of this project in related work, please note the following information:

```
Author: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
``` 