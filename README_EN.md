# AI Chief Intelligence Officer (Wiseflow)

**[简体中文](README.md) | [日本語](README_JP.md) | [한국어](README_KR.md)**

🚀 **Use large models to mine the information you are truly interested in from massive information and various sources every day!**

What we lack is not information, but the ability to filter out noise from massive information, thereby revealing valuable information.

🌱 See how AI Intelligence Officer helps you save time, filter irrelevant information, and organize key points of interest! 🌱

https://github.com/user-attachments/assets/fc328977-2366-4271-9909-a89d9e34a07b

## 🔥🔥🔥 Qwen3 Series Compatibility Report

On April 30th, the highly anticipated Qwen3 series was released, and we conducted tests immediately during the holiday.

We primarily tested Qwen3-14B and Qwen3-30B-A3B, comparing them with GLM-4-32B-0414 and DeepSeek-R1-Distill-Qwen-14B. We chose models with parameters not exceeding 32b because Wiseflow tasks are relatively simple - larger models don't bring significant improvements but would greatly increase usage costs. (Wiseflow tasks are characterized by low difficulty but require frequent calls).

The final conclusion: **Qwen3-14B and Qwen3-30B-A3B are highly recommended when think mode is enabled!** For detailed test reports, please see [test/reports/wiseflow_report_v40_web/Qwen3_report_0502.md](./test/reports/wiseflow_report_v40_web/Qwen3_report_0502.md)

Based on these tests (considering both generation speed and cost factors), for Wiseflow usage, we currently recommend using Qwen3-30B-A3B as the primary model and Qwen3-14B as the secondary model.

For local deployment with limited GPU memory, we recommend using only Qwen3-14B, and you can choose the 8bit quantized version.

Of course, you can also continue to use free models for "zero-cost" operation. For this, we strongly recommend the glm-4-flash-250414 from the Zhipu platform.

### If you don't want to bother with setup, you're also welcome to use the **Wiseflow** online service

which requires no deployment or setup, no need to apply for various keys, just register to use!

Online experience address: https://www.aiqingbaoguan.com/ 

Currently, registration gives you 15 computing points (each focus point consumes 1 point per day, regardless of the number of information sources).

*The online server is built on Alibaba Cloud, and access to websites outside mainland China is restricted. Additionally, the online service currently does not support WeChat official accounts. If your sources primarily consist of these two types, we recommend using the open-source version to deploy yourself.*

## 🌟 New contributors in the past two weeks

  - @zhudongwork PR #360 [replace re with regex library for better performance]
  - @beat4ocean PR #361 [update docker base image to improve for playwright]


## 🧐 'Deep Search' VS 'Wide Search'

I position Wiseflow's product as a "wide search," in contrast to the currently popular "deep search."

Specifically, "deep search" is oriented towards a specific question, where the LLM autonomously and dynamically plans the search path, continuously explores different pages, and collects enough information to give an answer or produce a report. However, sometimes we don't have a specific question and don't need in-depth exploration. We only need broad information collection (such as industry intelligence collection, background information collection on a subject, customer information collection, etc.). In these cases, breadth is clearly more meaningful. Although "deep search" can also accomplish this task, it's like using a cannon to kill a mosquito – inefficient and costly. Wiseflow is a powerful tool specifically designed for this "wide search" scenario.

## ✋ What makes Wiseflow different from other AI-powered crawlers?

The biggest difference is in the scraper stage, where we propose a pipeline different from existing crawlers: the "crawl-and-check integration" strategy. Specifically, we abandon the traditional filter-extractor process (of course, this process can also be integrated with LLM, as in Crawl4ai), and we no longer treat a single page as the minimum processing unit. Instead, building upon Crawl4ai's html2markdown, we further divide the page into blocks and, based on a series of characteristic algorithms, classify them into "content blocks" and "outbound link blocks." Different LLM extraction strategies are used based on the classification (each block is still analyzed by the LLM only once, but the analysis strategies differ to avoid token waste). This approach can handle list pages, content pages, and mixed pages.

  - For "content blocks," summaries are extracted directly according to the focus points, avoiding information scattering and even completing tasks like translation in the process.
  - For "outbound link blocks," information such as page layout is considered to determine which links are worth further exploration and which can be ignored. Therefore, users do not need to manually configure depth or maximum crawl quantity.

This approach is actually very similar to AI Search.

In addition, we have also written specialized parsing modules for specific types of pages, such as WeChat official account articles (which surprisingly have nine formats...). For this type of content, Wiseflow currently provides the best parsing results among similar products.

## ✋ What's Next (4.x plan)?

### Enhancements to the Crawler Fetching Stage

The 3.x architecture uses Crawl4ai entirely for the crawler fetching part. In 4.x, we will continue to use this approach for regular page acquisition, but we will gradually add fetching solutions for social media platforms.

### Insight Module

The truly valuable information may not be the "information that can be crawled," but the "hidden information" beneath it. The ability to intelligently correlate crawled information and analyze and extract the "hidden information" beneath it is what the 4.x Insight module will focus on.


## 📥 Installation and Usage

### 1. Clone the Code Repository

🌹 Starring and forking are good habits 🌹

**windows users please download git bash tool first** [link](https://git-scm.com/downloads/win)

```bash
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

### 2. Execute the install_pocketbase script in the root directory

linux/macos users please execute 

```bash
chmod +x install_pocketbase
./install_pocketbase
```

**windows users please execute [install_pocketbase.ps1](./install_pocketbase.ps1) script**

Wiseflow 3.x uses pocketbase as its database. You can also manually download the pocketbase client (remember to download version 0.23.4 and place it in the [pb](./pb) directory) and manually create the superuser (remember to save it in the .env file).

For details, please refer to [pb/README.md](/pb/README.md)

### 3. Continue Configuring the core/.env File

🌟 **This is different from previous versions** - starting from V3.5, the .env file needs to be placed in the [core](./core) folder.

#### 3.1 Large Language Model Configuration

Wiseflow is a LLM native application, so please ensure you provide stable LLM service for the program.

🌟 **Wiseflow does not restrict the source of model services - as long as the service is compatible with the openAI SDK, including locally deployed services like ollama, Xinference, etc.**

#### Recommendation 1: Use MaaS Service Provided by Siliconflow

Siliconflow provides online MaaS services for most mainstream open-source models. With its accumulated acceleration inference technology, its service has great advantages in both speed and price. When using siliconflow's service, the .env configuration can refer to the following:

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://api.siliconflow.cn/v1"
PRIMARY_MODEL="Qwen3-30B-A3B"
SECONDARY_MODEL="Qwen3-14B"
VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct"
PROJECT_DIR="work_dir"
```
      
😄 If you'd like, you can use my [siliconflow referral link](https://cloud.siliconflow.cn/i/WNLYbBpi), which will help me earn more token rewards 🌹

#### Recommendation 2: Use AiHubMix Proxy for Closed-Source Commercial Models like OpenAI, Claude, Gemini

If your information sources are mostly non-Chinese pages and you don't require the extracted info to be in Chinese, then it's recommended to use closed-source commercial models like OpenAI, Claude, Gemini. You can try the third-party proxy **AiHubMix**, seamlessly access a wide range of leading AI models like OpenAI, Claude, Google, Llama, and more with just one API.

When using AiHubMix models, the .env configuration can refer to the following:

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://aihubmix.com/v1" # refer to https://doc.aihubmix.com/
PRIMARY_MODEL="gpt-4o"
SECONDARY_MODEL="gpt-4o-mini"
VL_MODEL="gpt-4o"
PROJECT_DIR="work_dir"
```

😄 Welcome to register using the [AiHubMix referral link](https://aihubmix.com?aff=Gp54) 🌹

#### Use Local Large Language Model Service

Taking Xinference as an example, the .env configuration can refer to the following:

```
# LLM_API_KEY='' no need for local service, please comment out or delete
LLM_API_BASE='http://127.0.0.1:9997' # 'http://127.0.0.1:11434/v1' for ollama
PRIMARY_MODEL=launched_model_id
VL_MODEL=launched_model_id
PROJECT_DIR="work_dir"
```

#### 3.2 Pocketbase Account and Password Configuration

```
PB_API_AUTH="test@example.com|1234567890" 
```

This is where you set the superuser username and password for the pocketbase database, remember to separate them with | (if the install_pocketbase.sh script executed successfully, this should already exist)

#### 3.3 JINA_API_KEY Setting (for Search Engine Service)

Obtain from https://jina.ai/, currently no registration is required. (If you have high concurrency or commercial needs, please use after recharging)

```
JINA_API_KEY=Your_API_KEY
```

#### 3.4 Other Optional Configurations

The following are all optional configurations:
- #VERBOSE="true" 

  Whether to enable observation mode. When enabled, debug information will be recorded in the logger file (by default only output to console);

- #PB_API_BASE="" 

  Only needs to be configured if your pocketbase is not running on the default IP or port. Under default circumstances, you can ignore this.

- #LLM_CONCURRENT_NUMBER=8 

 Used to control the number of concurrent LLM requests. Default is 1 if not set (before enabling, please ensure your LLM provider supports the configured concurrency. Use local large models with caution unless you are confident in your hardware capabilities)

### 4. Running the Program

It is recommended to use conda to build a virtual environment (of course you can skip this step, or use other Python virtual environment solutions)

```bash
conda create -n wiseflow python=3.12
conda activate wiseflow
```

then

```bash
cd wiseflow
cd core
pip install -r requirements.txt
python -m playwright install --with-deps chromium
```

Afterwards, MacOS&Linux users execute

```bash
chmod +x run.sh
./run.sh
```

Windows users execute

```bash
python windows_run.py
```

- This script will automatically determine if pocketbase is already running, and if not, it will automatically start it. However, please note that when you terminate the process with ctrl+c or ctrl+z, the pocketbase process will not be terminated until you close the terminal.

- run.sh will first execute a crawling task for all sources that have been activated (set to true), and then execute periodically at the set frequency in hours.

### 5. Focus Points and Source Addition
    
After starting the program, open the pocketbase Admin dashboard UI (http://127.0.0.1:8090/_/)

#### 5.1 Opening the Sites Form

This form allows you to configure sources, noting that sources must be selected in the subsequent focus_point form.

Sites field explanations:
- url, the URL of the source, the source does not need to provide specific article pages, just the article list pages.
- type, the type, either web or rss.
    
#### 5.2 Opening the Focus Point Form

This form allows you to specify your focus points, and LLM will refine, filter, and categorize information based on this.
    
Field explanations:
- focuspoint, focus point description (required), such as "Christmas holiday discount information" or "bid announcement"
- explanation, detailed explanation or specific convention of the focus point, such as "xx series products" or "published after January 1, 2025, and with an amount over 10 million" etc.
- activated, whether to activate. If closed, this focus point will be ignored, and can be reopened after closing.
- per_hour, crawl frequency, in hours, integer type (1-24 range, we recommend not to exceed once a day, i.e., set to 24)
- search_engine, whether to enable the search engine for each crawl
- sites, select the corresponding source

**Note: After version V3.8, adjustments to configurations do not require restarting the program, and will automatically take effect at the next execution.**

## 🐳 Docker Deployment

If you want to deploy Wiseflow using Docker, we provide complete containerization support.

### 1. Prerequisites

Make sure Docker is installed on your system.

### 2. Configure Environment Variables

Copy the `env_docker` file as `.env` in the root directory:

```bash
cp env_docker .env
```

### 3. Modify the `.env` File According to the《[Installation and Usage](#-installation-and-usage)》Section

The following environment variables must be modified as needed:

```bash
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://api.siliconflow.cn/v1"
PRIMARY_MODEL="Qwen3-30B-A3B"
SECONDARY_MODEL="Qwen3-14B"
VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct"
PB_SUPERUSER_EMAIL="test@example.com"
PB_SUPERUSER_PASSWORD="1234567890" #no '&' in the password and at least 10 characters
```

### 4. Start the Service

Execute in the project root directory:

```bash
docker compose up -d
```

After the service starts:

- PocketBase Admin Interface: http://localhost:8090/_/
- Wiseflow service will automatically run and connect to PocketBase

### 5. Stop the Service

```bash
docker compose down
```

### 6. Important Notes

- The `./pb/pb_data` directory is used to store PocketBase related files
- The `./docker/pip_cache` directory is used to store Python dependency package cache to avoid repeated downloads
- The `./core/work_dir` directory is used to store Wiseflow runtime logs, you can modify `PROJECT_DIR` in the `.env` file

## 📚 How to Use the Data Crawled by wiseflow in Your Own Program

1. Refer to the [dashboard](dashboard) part of the source code for secondary development.

Note that the core part of wiseflow does not require a dashboard, and the current product does not integrate a dashboard. If you need a dashboard, please download [V0.2.1 version](https://github.com/TeamWiseFlow/wiseflow/releases/tag/V0.2.1)

2. Directly obtain data from Pocketbase

All crawled data by wiseflow will be instantly stored in pocketbase, so you can directly operate the pocketbase database to obtain data.

PocketBase, as a popular lightweight database, currently has SDKs for Go/Javascript/Python and other languages.
   - Go : https://pocketbase.io/docs/go-overview/
   - Javascript : https://pocketbase.io/docs/js-overview/
   - python : https://github.com/vaphes/pocketbase

3.  The online service will also launch a sync API soon, supporting the synchronization of online crawling results to the local, which can be used to build a "dynamic knowledge base", etc. Please stay tuned:

   - Online experience address: https://www.aiqingbaoguan.com/
   - Online service API use case: https://github.com/TeamWiseFlow/wiseflow_plus


## 🛡️ License

This project is open-source under the [Apache2.0](LICENSE) license.

For cooperation, please contact **Email: zm.zhao@foxmail.com**

- Commercial customers, please contact us for registration. The product promises to be forever free.


## 📬 Contact

If you have any questions or suggestions, please feel free to leave a message via [issue](https://github.com/TeamWiseFlow/wiseflow/issues).


## 🤝 This Project is Based on the Following Excellent Open-Source Projects:

- crawl4ai（Open-source LLM Friendly Web Crawler & Scraper） https://github.com/unclecode/crawl4ai
- pocketbase (Open Source realtime backend in 1 file) https://github.com/pocketbase/pocketbase
- python-pocketbase (pocketBase client SDK for python) https://github.com/vaphes/pocketbase
- feedparser (Parse feeds in Python) https://github.com/kurtmckee/feedparser

Also inspired by [GNE](https://github.com/GeneralNewsExtractor/GeneralNewsExtractor)  [AutoCrawler](https://github.com/kingname/AutoCrawler)  [SeeAct](https://github.com/OSU-NLP-Group/SeeAct) .

## Citation

If you reference or cite part or all of this project in your related work, please specify the following information:

```
Author: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```
