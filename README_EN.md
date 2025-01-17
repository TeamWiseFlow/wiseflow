# Chief Intelligence Officer (Wiseflow)

**[简体中文](README.md) | [日本語](README_JP.md) | [한국어](README_KR.md)**

🚀 **Chief Intelligence Officer** (Wiseflow) is an agile information mining tool that can precisely extract specific information from various given sources by leveraging the thinking and analytical capabilities of large models, requiring no human intervention throughout the process.

**What we lack is not information, but the ability to filter out noise from massive information, thereby revealing valuable information.**

🌱 See how AI Intelligence Officer helps you save time, filter irrelevant information, and organize key points of interest! 🌱

https://github.com/user-attachments/assets/fc328977-2366-4271-9909-a89d9e34a07b

## 🔥 V0.3.6 is Here

V0.3.6 is an enhanced version of V0.3.5, incorporating numerous improvements based on community feedback. We recommend all users to upgrade.

- Switched to Crawl4ai as the underlying web crawling framework. Although Crawl4ai and Crawlee both rely on Playwright with similar fetching results, Crawl4ai's html2markdown feature is quite practical for LLM information extraction. Additionally, Crawl4ai's architecture better aligns with my design philosophy.
- Built upon Crawl4ai's html2markdown, we added a deep scraper to further differentiate standalone links from the main content, facilitating more precise LLM extraction. The preprocessing done by html2markdown and deep scraper significantly cleans up raw web data, minimizing interference and misleading information for LLMs, ensuring higher quality outcomes while reducing unnecessary token consumption.

  *Distinguishing between list pages and article pages is a common challenge in web scraping projects, especially when modern webpages often include extensive recommended readings in sidebars and footers of articles, making it difficult to differentiate them through text statistics.*
  *Initially, I considered using large visual models for layout analysis, but found that obtaining undistorted webpage screenshots greatly increases program complexity and reduces processing efficiency...*

- Restructured extraction strategies and LLM prompts;

  *Regarding prompts, I believe that a good prompt serves as clear workflow guidance, with each step being explicit enough to minimize errors. However, I am skeptical about the value of overly complex prompts, which are hard to evaluate. If you have better solutions, feel free to submit a PR.*

- Introduced large visual models to automatically recognize high-weight images (currently evaluated by Crawl4ai) before extraction and append relevant information to the page text;
- Continued to reduce dependencies in requirement.txt; json_repair is no longer needed (in practice, having LLMs generate JSON format still noticeably increases processing time and failure rates, so I now adopt a simpler approach with additional post-processing of results)
- Made minor adjustments to the pb info form structure, adding web_title and reference fields.
- @ourines contributed the install_pocketbase.sh script (the Docker running solution has been temporarily removed as it wasn't very convenient for users...)
- @ibaoger contributed the install_pocketbase.ps1 script for windows users
- @tusik contributed the asynchronous llm wrapper

**Upgrading to V0.3.6 requires restructuring the PocketBase database. Please delete the pb/pb_data folder and re-run the setup**

**In V0.3.6, replace SECONDARY_MODEL with VL_MODEL in the .env file. Refer to the latest [env_sample](./env_sample)**

### V0.3.6 Test Report

We conducted horizontal tests across four real-world tasks and six real web samples using deepseekV2.5, Qwen2.5-32B-Instruct, Qwen2.5-14B-Instruct, and Qwen2.5-72B-Instruct models provided by siliconflow. For detailed test results, please refer to [report](./test/reports/wiseflow_report_v036_bigbrother666/README.md).

We have also open-sourced our testing scripts. We welcome everyone to submit more test results. Wiseflow is an open-source project aiming to create an "information retrieval tool accessible to everyone"!

Refer to [test/README.md](./test/README.md)

At this stage, **submitting test results is equivalent to contributing code**, and contributors may even be invited to participate in commercial projects!


🌟**V0.3.x Roadmap**

- Attempt to support WeChat Official Account subscription without wxbot (V0.3.7);
- Introduce support for RSS feeds and search engines (V0.3.8);
- Attempt partial support for social platforms (V0.3.9).

Throughout these versions, I will continuously improve the deep scraper and LLM extraction strategies. We welcome continuous feedback on application scenarios and sources where extraction performance is unsatisfactory. Please provide feedback in [issue #136](https://github.com/TeamWiseFlow/wiseflow/issues/136).


## ✋ How is wiseflow Different from Traditional Crawler Tools, AI Search, and Knowledge Base (RAG) Projects?

Since the release of version V0.3.0 in late June 2024, wiseflow has received widespread attention from the open-source community, attracting even some self-media reports. First of all, we would like to express our gratitude!

However, we have also noticed some misunderstandings about the functional positioning of wiseflow among some followers. The following table, through comparison with traditional crawler tools, AI search, and knowledge base (RAG) projects, represents our current thinking on the latest product positioning of wiseflow.

|          | Comparison with **Chief Intelligence Officer (Wiseflow)** | 
|-------------|-----------------|
| **Crawler Tools** | First of all, wiseflow is a project based on a web crawler tool, but traditional crawler tools require manual provision of explicit Xpath information for data extraction... This not only blocks ordinary users but also lacks universality. For different websites (including existing websites after upgrades), manual re-analysis and program updates are required. wiseflow is committed to using LLM to automate the analysis and extraction of web pages. Users only need to tell the program their focus points. Taking Crawl4ai as an example for comparison, Crawl4ai is a crawler that uses LLM for information extraction, while wiseflow is an LLM information extractor that uses crawler tools. |
| **AI Search** | AI search is mainly used for **instant question-and-answer** scenarios, such as "Who is the founder of XX company?" or "Where can I buy the xx product under the xx brand?" Users want **a single answer**; wiseflow is mainly used for **continuous information collection** in certain areas, such as tracking related information of XX company, continuously tracking market behavior of XX brand, etc. In these scenarios, users can provide focus points (a company, a brand) or even information sources (site URLs, etc.), but cannot pose specific search questions. Users want **a series of related information**.| 
| **Knowledge Base (RAG) Projects** | Knowledge base (RAG) projects are generally based on downstream tasks of existing information and usually face private knowledge (such as operation manuals, product manuals, government documents within enterprises, etc.); wiseflow currently does not integrate downstream tasks and faces public information on the internet. From the perspective of "agents," the two belong to agents built for different purposes. RAG projects are "internal knowledge assistant agents," while wiseflow is an "external information collection agent."|

**The wiseflow 0.4.x version will focus on the integration of downstream tasks, introducing an LLM-driven lightweight knowledge graph to help users gain insights from infos.**

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

```bash
export LLM_API_KEY=Your_API_KEY
export LLM_API_BASE="https://api.siliconflow.cn/v1"
export PRIMARY_MODEL="Qwen/Qwen2.5-32B-Instruct"
export SECONDARY_MODEL="Qwen/Qwen2.5-7B-Instruct"
export VL_MODEL="OpenGVLab/InternVL2-26B"
```
      
😄 If you'd like, you can use my [siliconflow referral link](https://cloud.siliconflow.cn?referrer=clx6wrtca00045766ahvexw92), which will help me earn more token rewards 🌹

#### Recommendation 2: Use AiHubMix Proxy for Closed-Source Commercial Models like OpenAI, Claude, Gemini

If your information sources are mostly non-Chinese pages and you don't require the extracted info to be in Chinese, then it's recommended to use closed-source commercial models like OpenAI, Claude, Gemini. You can try the third-party proxy **AiHubMix**, seamlessly access a wide range of leading AI models like OpenAI, Claude, Google, Llama, and more with just one API.

When using AiHubMix models, the .env configuration can refer to the following:

```bash
export LLM_API_KEY=Your_API_KEY
export LLM_API_BASE="https://aihubmix.com/v1" # refer to https://doc.aihubmix.com/
export PRIMARY_MODEL="gpt-4o"
export SECONDARY_MODEL="gpt-4o-mini"
export VL_MODEL="gpt-4o"
```

😄 Welcome to register using the [AiHubMix referral link](https://aihubmix.com?aff=Gp54) 🌹

#### Use Local Large Language Model Service

Taking Xinference as an example, the .env configuration can refer to the following:

```bash
# LLM_API_KEY='' no need for local service, please comment out or delete
export LLM_API_BASE='http://127.0.0.1:9997'
export PRIMARY_MODEL=launched_model_id
export VL_MODEL=launched_model_id
```

#### 3.2 Pocketbase Account and Password Configuration

```bash
export PB_API_AUTH="test@example.com|1234567890" 
```

This is where you set the superuser username and password for the pocketbase database, remember to separate them with | (if the install_pocketbase.sh script executed successfully, this should already exist)

#### 3.3 Other Optional Configurations

The following are all optional configurations:
- #VERBOSE="true" 

  Whether to enable observation mode. When enabled, debug information will be recorded in the logger file (by default only output to console);

- #PROJECT_DIR="work_dir" 

    Project runtime data directory. If not configured, defaults to `core/work_dir`. Note: Currently the entire core directory is mounted under the container, meaning you can access it directly.

- #PB_API_BASE="" 

  Only needs to be configured if your pocketbase is not running on the default IP or port. Under default circumstances, you can ignore this.

- #LLM_CONCURRENT_NUMBER=8 

 Used to control the number of concurrent LLM requests. Default is 1 if not set (before enabling, please ensure your LLM provider supports the configured concurrency. Use local large models with caution unless you are confident in your hardware capabilities)
  
  Thanks to @tusik for contributing the asynchronous LLM wrapper

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
chmod +x run.sh
./run_task.sh # if you just want to scan sites one-time (no loop), use ./run.sh
```

🌟 This script will automatically determine if pocketbase is already running. If not, it will automatically start. However, please note that when you terminate the process with ctrl+c or ctrl+z, the pocketbase process will not be terminated until you close the terminal.

run_task.sh will periodically execute crawling-extraction tasks (it will execute immediately at startup, then every hour after that). If you only need to execute once, you can use the run.sh script.

### 5. **Adding Focus Points and Scheduled Scanning of Information Sources**
    
After starting the program, open the pocketbase Admin dashboard UI (http://127.0.0.1:8090/_/)
    
#### 5.1 Open the focus_point Form

Through this form, you can specify your focus points, and LLM will refine, filter, and categorize information accordingly.
    
Field description:
- focuspoint, focus point description (required), such as "Shanghai elementary to junior high school information," "cryptocurrency prices"
- explanation, detailed explanation or specific conventions of the focus point, such as "Only official junior high school admission information released by Shanghai" or "Current price, price change data of BTC, ETH"
- activated, whether to activate. If closed, this focus point will be ignored, and it can be re-enabled later.

Note: After updating the focus_point settings (including activated adjustments), **the program needs to be restarted for the changes to take effect.**

#### 5.2 Open the sites Form

Through this form, you can specify custom information sources. The system will start background scheduled tasks to scan, parse, and analyze the information sources locally.

sites field description:
- url, the URL of the information source. The information source does not need to be given a specific article page, just the article list page.
- per_hours, scanning frequency, in hours, integer type (1~24 range, we recommend not exceeding once a day, i.e., set to 24)
- activated, whether to activate. If closed, this information source will be ignored, and it can be re-enabled later.

**Adjustments to sites settings do not require restarting the program.**


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
- python-pocketbase (pocketBase client SDK for python) https://github.com/vaphes/pocketbase

Also inspired by [GNE](https://github.com/GeneralNewsExtractor/GeneralNewsExtractor)  [AutoCrawler](https://github.com/kingname/AutoCrawler)  [SeeAct](https://github.com/OSU-NLP-Group/SeeAct) .

## Citation

If you reference or cite part or all of this project in your related work, please specify the following information:

```
Author: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```