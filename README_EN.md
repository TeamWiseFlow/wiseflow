# AI Chief Intelligence Officer (Wiseflow)

**[简体中文](README.md) | [日本語](README_JP.md) | [한국어](README_KR.md)**

🚀 **AI Chief Intelligence Officer** (Wiseflow) is an agile information mining tool that can precisely extract specific information from various given sources by leveraging the thinking and analytical capabilities of large models, requiring no human intervention throughout the process.

**What we lack is not information, but the ability to filter out noise from massive information, thereby revealing valuable information.**

🌱 See how AI Intelligence Officer helps you save time, filter irrelevant information, and organize key points of interest! 🌱

https://github.com/user-attachments/assets/fc328977-2366-4271-9909-a89d9e34a07b

🌟 Reminder: Although you may have recently heard many people praise reasoning models like DeepSeek R1 (which I do not deny), tasks like information extraction and summarization in WiseFlow do not require complex logical reasoning. Using reasoning models will instead significantly increase inference time and costs! If you are interested in understanding this conclusion further, you can refer to the following test report: [wiseflow V0.38 with deepseek series report](./test/reports/wiseflow_report_v038_dp_bigbrother666/README.md).

:anger: **Starting from March 14, 2025, the Wiseflow platform will officially charge for the web_search_pro interface. Please be aware of your account balance if you need to use the search function.** :anger:
[Wiseflow Platform Announcement](https://bigmodel.cn/dev/api/search-tool/web-search-pro)

## 🔥 V0.3.9_patch2 Released

For more details about this upgrade, please see [CHANGELOG.md](./CHANGELOG.md)

**Users upgrading from V0.3.7 or earlier versions should first execute `./pocketbase migrate` in the `pb` folder.**

Thanks to the following community members for their PRs in versions V0.3.5~V0.3.9:

  - @ourines contributed the install_pocketbase.sh automated installation script
  - @ibaoger contributed the PocketBase automated installation script for Windows
  - @tusik contributed the asynchronous llm wrapper and discovered the AsyncWebCrawler lifecycle issue
  - @c469591 contributed the Windows version startup script
  - @braumye contributed the Docker deployment solution
  - @YikaJ provided optimizations for install_pocketbase.sh

0.3.9 is the last version of the 0.3.x series  **The next open-source version of wiseflow is expected to take at least 2 months, and we will launch a completely new 0.4.x architecture.**

Regarding 0.4.x, I have been thinking about the specific product roadmap. Currently, I need more real user feedback. I hope everyone can submit more usage requirements in the [issue](https://github.com/TeamWiseFlow/wiseflow/issues) section.
  
### 🌟 Test Report

Under the latest extraction strategy, we found that models of 7b scale can also perform link analysis and extraction tasks well. For test results, please refer to [report](./test/reports/wiseflow_report_v037_bigbrother666/README.md)

However, for information summarization tasks, we still recommend using models no smaller than 32b scale. For specific recommendations, please refer to the latest [env_sample](./env_sample)

We continue to welcome more test results to jointly explore the best usage solutions for wiseflow under various information sources.

At this stage, **submitting test results is equivalent to submitting project code**, and will similarly be accepted as a contributor, and may even be invited to participate in commercialization projects! For details, please refer to [test/README.md](./test/README.md)

## 🧐  Comparison between wiseflow and various "deep search" applications including Manus:

In simple terms, question and answer tasks are more suitable for "deep search" applications, and for information collection tasks, you can try it out and you will know the advantages of wiseflow in this aspect..


## ✋ How is wiseflow Different from Traditional Crawler Tools, AI Search, and Knowledge Base (RAG) Projects?

Since the release of version V0.3.0 in late June 2024, wiseflow has received widespread attention from the open-source community, attracting even some self-media reports. First of all, we would like to express our gratitude!

However, we have also noticed some misunderstandings about the functional positioning of wiseflow among some followers. The following table, through comparison with traditional crawler tools, AI search, and knowledge base (RAG) projects, represents our current thinking on the latest product positioning of wiseflow.

|          | Comparison with **Chief Intelligence Officer (Wiseflow)** | 
|-------------|-----------------|
| **Crawler Tools** | First of all, wiseflow is a project based on a web crawler tool, but traditional crawler tools require manual provision of explicit Xpath information for data extraction... This not only blocks ordinary users but also lacks universality. For different websites (including existing websites after upgrades), manual re-analysis and program updates are required. wiseflow is committed to using LLM to automate the analysis and extraction of web pages. Users only need to tell the program their focus points. Taking Crawl4ai as an example for comparison, Crawl4ai is a crawler that uses LLM for information extraction, while wiseflow is an LLM information extractor that uses crawler tools. |
| **AI Search（inclue all ‘deep search’）** | AI search is mainly used for **instant question-and-answer** scenarios, such as "Who is the founder of XX company?" or "Where can I buy the xx product under the xx brand?" Users want **a single answer**; wiseflow is mainly used for **continuous information collection** in certain areas, such as tracking related information of XX company, continuously tracking market behavior of XX brand, etc. In these scenarios, users can provide focus points (a company, a brand) or even information sources (site URLs, etc.), but cannot pose specific search questions. Users want **a series of related information**.| 
| **Knowledge Base (RAG) Projects** | Knowledge base (RAG) projects are generally based on downstream tasks of existing information and usually face private knowledge (such as operation manuals, product manuals, government documents within enterprises, etc.); wiseflow currently does not integrate downstream tasks and faces public information on the internet. From the perspective of "agents," the two belong to agents built for different purposes. RAG projects are "internal knowledge assistant agents," while wiseflow is an "external information collection agent."|


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

Wiseflow 0.3.x uses pocketbase as its database. You can also manually download the pocketbase client (remember to download version 0.23.4 and place it in the [pb](./pb) directory) and manually create the superuser (remember to save it in the .env file).

For details, please refer to [pb/README.md](/pb/README.md)

### 3. Continue Configuring the core/.env File

🌟 **This is different from previous versions** - starting from V0.3.5, the .env file needs to be placed in the [core](./core) folder.

#### 3.1 Large Language Model Configuration

Wiseflow is a LLM native application, so please ensure you provide stable LLM service for the program.

🌟 **Wiseflow does not restrict the source of model services - as long as the service is compatible with the openAI SDK, including locally deployed services like ollama, Xinference, etc.**

#### Recommendation 1: Use MaaS Service Provided by Siliconflow

Siliconflow provides online MaaS services for most mainstream open-source models. With its accumulated acceleration inference technology, its service has great advantages in both speed and price. When using siliconflow's service, the .env configuration can refer to the following:

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://api.siliconflow.cn/v1"
PRIMARY_MODEL="Qwen/Qwen2.5-32B-Instruct"
SECONDARY_MODEL="Qwen/Qwen2.5-14B-Instruct"
VL_MODEL="deepseek-ai/deepseek-vl2"
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
```

😄 Welcome to register using the [AiHubMix referral link](https://aihubmix.com?aff=Gp54) 🌹

#### Use Local Large Language Model Service

Taking Xinference as an example, the .env configuration can refer to the following:

```
# LLM_API_KEY='' no need for local service, please comment out or delete
LLM_API_BASE='http://127.0.0.1:9997'
PRIMARY_MODEL=launched_model_id
VL_MODEL=launched_model_id
```

#### 3.2 Pocketbase Account and Password Configuration

```
PB_API_AUTH="test@example.com|1234567890" 
```

This is where you set the superuser username and password for the pocketbase database, remember to separate them with | (if the install_pocketbase.sh script executed successfully, this should already exist)


#### 3.3 Zhipu (bigmodel) Platform Key Configuration (for Search Engine Services)

```
ZHIPU_API_KEY=Your_API_KEY
```

(Application here: https://bigmodel.cn/ ~~currently free~~ 0.03 CNY/query, please ensure your account balance)

#### 3.4 Other Optional Configurations

The following are all optional configurations:
- #VERBOSE="true" 

  Whether to enable observation mode. When enabled, debug information will be recorded in the logger file (by default only output to console);

- #PROJECT_DIR="work_dir" 

    Project runtime data directory. If not configured, defaults to `core/work_dir`. Note: Currently the entire core directory is mounted under the container, meaning you can access it directly.

- #PB_API_BASE="" 

  Only needs to be configured if your pocketbase is not running on the default IP or port. Under default circumstances, you can ignore this.

- #LLM_CONCURRENT_NUMBER=8 

 Used to control the number of concurrent LLM requests. Default is 1 if not set (before enabling, please ensure your LLM provider supports the configured concurrency. Use local large models with caution unless you are confident in your hardware capabilities)

### 4. Running the Program

✋ The V0.3.5 version architecture and dependencies are significantly different from previous versions. Please make sure to re-pull the code, delete (or rebuild) pb_data

It is recommended to use conda to build a virtual environment (of course you can skip this step, or use other Python virtual environment solutions)

```bash
conda create -n wiseflow python=3.10
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

**Note: After version V0.3.8, adjustments to configurations do not require restarting the program, and will automatically take effect at the next execution.**

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
LLM_API_KEY=""
LLM_API_BASE="https://api.siliconflow.cn/v1"
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
