# AI Chief Intelligence Officer (Wiseflow)

**[English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md)**

🚀 **Use large language models to mine information you're truly interested in from massive data and various sources daily!**

What we lack is not information, but the ability to filter out noise from massive information to reveal valuable insights.

🌱 See how AI Intelligence Officer helps you save time, filter out irrelevant information, and organize key points! 🌱

https://github.com/user-attachments/assets/fc328977-2366-4271-9909-a89d9e34a07b

## 🔥🔥🔥 Wiseflow 4.0 Version Officially Released!

(Online service is currently not switched to 4.0 core due to technical reasons, we are accelerating the upgrade)

After a three-month wait, we finally welcome the official release of Wiseflow 4.0!

This version brings a brand new 4.x architecture, introduces support for social media sources, and brings many new features.

🌟 4.x includes WIS Crawler (deeply restructured and integrated based on Crawl4ai, MediaCrawler, and Nodriver), which now perfectly supports web pages and social media. Version 4.0 initially provides support for Weibo and Kuaishou platforms, with plans to add more platforms including:
WeChat Official Accounts, Xiaohongshu, Douyin, Bilibili, Zhihu...

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

## 🚀 Quick Start

**Just three steps to get started!**

### 📋 Download Project Source Code and Install uv and pocketbase

- for MacOS/Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

- for Windows:

**Windows users please download Git Bash tool in advance and execute the following commands in bash [Bash Download Link](https://git-scm.com/downloads/win)**

```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

🌟 The above operations will complete the installation of uv. For pocketbase installation, please refer to [pocketbase docs](https://pocketbase.io/docs/)

You can also try using install_pocketbase.sh (for MacOS/Linux) or install_pocketbase.ps1 (for Windows) to install.

### 📥 Configure .env File Based on env_sample

In the wiseflow folder (project root directory), create a .env file based on env_sample and fill in the relevant settings

### 🚀 Take Off!

- for MacOS/Linux:

```bash
cd wiseflow
./run.sh
```

(Note: You may need to execute `chmod +x run.sh` first to grant execution permission)

- for Windows:

```bash
cd wiseflow
.\run.ps1
```

(Note: You may need to execute `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` first to grant execution permission)

If you encounter issues starting the virtual browser, you can execute the following command:

```bash
python -m playwright install --with-deps chromium
```

For detailed usage instructions, please refer to [docs/manual.md](./docs/manual.md)

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