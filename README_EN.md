# Chief Intelligence Officer (Wiseflow)

**[简体中文](README.md) | [日本語](README_JP.md) | [한국어](README_KR.md)**

🚀 **Chief Intelligence Officer** (Wiseflow) is an agile information mining tool that can extract information from various sources such as websites, WeChat official accounts, and social platforms based on preset focus points, automatically tag and categorize the information, and upload it to the database.

**What we lack is not information, but the ability to filter out noise from massive information, thereby revealing valuable information.**

🌱 See how Chief Intelligence Officer helps you save time, filter irrelevant information, and organize key points of interest! 🌱

https://github.com/user-attachments/assets/f6fec29f-2b4b-40f8-8676-8433abb086a7

## 🔥 Introducing Version V0.3.5

Based on extensive community feedback, we have refined the product positioning of wiseflow, making it more focused. Version V0.3.5 is the new architecture version under this positioning:

- Introduced [Crawlee](https://github.com/apify/crawlee-python) as the basic crawler and task management framework, significantly enhancing page acquisition capabilities. Pages that were previously unobtainable (including those obtained as garbled text) can now be acquired well. If you encounter pages that cannot be acquired well, please provide feedback in [issue #136](https://github.com/TeamWiseFlow/wiseflow/issues/136);
- New information extraction strategy under the new product positioning—"crawling and checking integration," abandoning detailed article extraction. During the crawling process, LLM directly extracts user-interested information (infos), and automatically judges links worth following up on. **What you focus on is what you need**;
- Adapted to the latest version (v0.23.4) of Pocketbase, updated form configuration. Additionally, the new architecture no longer requires modules like GNE, reducing the number of requirement dependencies to 8;
- The new architecture deployment scheme is also more convenient, with Docker mode supporting hot updates of the code repository. This means that subsequent upgrades no longer require repeated Docker builds.
- For more details, refer to [CHANGELOG](CHANGELOG.md)

🌟 **Future Plans for V0.3.x**

- Introduce [SeeAct](https://github.com/OSU-NLP-Group/SeeAct) solution, guiding complex page operations through visual large models, such as scrolling, clicking to reveal information (V0.3.6);
- Attempt to support WeChat official account subscription without wxbot (V0.3.7);
- Introduce support for RSS information sources (V0.3.8);
- Attempt to introduce a lightweight knowledge graph driven by LLM to help users build insights from infos (V0.3.9).

## ✋ How is wiseflow Different from Traditional Crawler Tools, AI Search, and Knowledge Base (RAG) Projects?

Since the release of version V0.3.0 in late June 2024, wiseflow has received widespread attention from the open-source community, attracting even some self-media reports. First of all, we would like to express our gratitude!

However, we have also noticed some misunderstandings about the functional positioning of wiseflow among some followers. The following table, through comparison with traditional crawler tools, AI search, and knowledge base (RAG) projects, represents our current thinking on the latest product positioning of wiseflow.

|          | Comparison with **Chief Intelligence Officer (Wiseflow)** | 
|-------------|-----------------|
| **Crawler Tools** | First, wiseflow is a project based on crawler tools (in the current version, we use the crawler framework Crawlee). However, traditional crawler tools require manual intervention in information extraction, providing explicit Xpath, etc. This not only blocks ordinary users but also lacks generality. For different websites (including upgraded websites), manual reanalysis and updating of extraction code are required. Wiseflow is committed to automating web analysis and extraction using LLM. Users only need to tell the program their focus points. From this perspective, wiseflow can be simply understood as an "AI agent that can automatically use crawler tools." |
| **AI Search** | AI search is mainly used for **instant question-and-answer** scenarios, such as "Who is the founder of XX company?" or "Where can I buy the xx product under the xx brand?" Users want **a single answer**; wiseflow is mainly used for **continuous information collection** in certain areas, such as tracking related information of XX company, continuously tracking market behavior of XX brand, etc. In these scenarios, users can provide focus points (a company, a brand) or even information sources (site URLs, etc.), but cannot pose specific search questions. Users want **a series of related information**.| 
| **Knowledge Base (RAG) Projects** | Knowledge base (RAG) projects are generally based on downstream tasks of existing information and usually face private knowledge (such as operation manuals, product manuals, government documents within enterprises, etc.); wiseflow currently does not integrate downstream tasks and faces public information on the internet. From the perspective of "agents," the two belong to agents built for different purposes. RAG projects are "internal knowledge assistant agents," while wiseflow is an "external information collection agent."|

## 📥 Installation and Usage

### 1. Clone the Code Repository

🌹 Starring and forking are good habits 🌹

```bash
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

### 2. Refer to env_sample to Configure the .env File and Place it in the Core Directory

🌟 **This is different from previous versions**, starting from V0.3.5, the .env file needs to be placed in the core folder.

Additionally, the env configuration has been greatly simplified from V0.3.5, with only three required configuration items, as follows:

- LLM_API_KEY=""

    Large model service key, this is mandatory

- LLM_API_BASE="https://api.siliconflow.cn/v1" 

    Service interface address, any service provider supporting openai sdk can be used. If you directly use openai services, this item can also be left blank

- PB_API_AUTH="test@example.com|1234567890" 

  Pocketbase database superuser username and password, remember to separate with |

The following are optional configurations:
- #VERBOSE="true" 

   Whether to enable observation mode. If enabled, not only will debug log information be recorded in the logger file (default is only output to the console), but the playwright browser window will also be opened to facilitate observation of the crawling process;

- #PRIMARY_MODEL="Qwen/Qwen2.5-7B-Instruct"

    Main model selection. When using siliconflow services, this item left blank will default to Qwen2.5-7B-Instruct, which is practically sufficient, but I **recommend Qwen2.5-14B-Instruct** more

- #SECONDARY_MODEL="THUDM/glm-4-9b-chat" 

    Secondary model selection. When using siliconflow services, this item left blank will default to glm-4-9b-chat.

- #PROJECT_DIR="work_dir" 

    Project runtime data directory. If not configured, the default is `core/work_dir`. Note: The entire core directory is mounted under the container, meaning you can directly access it.

- #PB_API_BASE="" 

   Only required when your pocketbase is not running on the default IP or port. Ignored by default.

### 3.1 Run Using Docker

✋ The V0.3.5 version architecture and dependencies are significantly different from previous versions. Please make sure to re-pull the code, delete the old version image (including the mounted pb_data folder), and rebuild!

```bash
cd wiseflow
docker compose up
```

**Note:**

The first time you run the Docker container, the program may report an error, which is normal. Please follow the screen prompts to create a super user account (must use an email), then fill in the created username and password into the .env file, and restart the container.

🌟 The Docker solution defaults to running task.py, which will periodically execute crawling-extraction tasks (immediately executes once at startup, then every hour thereafter)

### 3.2 Run Using Python Environment

✋ The V0.3.5 version architecture and dependencies are significantly different from previous versions. Please make sure to re-pull the code, delete (or rebuild) pb_data

It is recommended to use conda to build a virtual environment

```bash
cd wiseflow
conda create -n wiseflow python=3.10
conda activate wiseflow
cd core
pip install -r requirements.txt
```

Then go here [Download](https://pocketbase.io/docs/) the corresponding pocketbase client and place it in the [/pb](/pb) directory. Then

```bash
chmod +x run.sh
./run_task.sh # if you just want to scan sites one-time (no loop), use ./run.sh
```

This script will automatically determine if pocketbase is already running. If not, it will automatically start. However, please note that when you terminate the process with ctrl+c or ctrl+z, the pocketbase process will not be terminated until you close the terminal.

Similarly to Docker deployment, the first run may result in an error. Please follow the screen prompts to create a super user account (must use an email), then fill in the created username and password into the .env file and run again.

Of course, you can also run and set up pocketbase in another terminal in advance (this will avoid the first error). For details, please refer to [pb/README.md](/pb/README.md)

### 4. Model Recommendations [2024-12-09]

Although larger models generally mean better performance, practical tests show that **using Qwen2.5-7b-Instruct and glm-4-9b-chat models can achieve basic effects**. However, considering cost, speed, and effect, I **recommend using Qwen2.5-14B-Instruct as the main model (PRIMARY_MODEL)**.

Here, I still strongly recommend using siliconflow's MaaS service, which provides services for multiple mainstream open-source models, with ample supply. Qwen2.5-7b-Instruct and glm-4-9b-chat currently offer free services. (When using Qwen2.5-14B-Instruct as the main model, crawling 374 web pages, effectively extracting 43 infos, total cost ￥3.07)
      
😄 If you are willing, you can use my [siliconflow invitation link](https://cloud.siliconflow.cn?referrer=clx6wrtca00045766ahvexw92), so I can also get more token rewards 🌹

**If your information sources are mostly non-Chinese pages and you do not require the extracted infos to be in Chinese, it is more recommended to use models from overseas manufacturers such as openai or claude.**
   
You can try the third-party proxy **AiHubMix**, seamlessly access a wide range of leading AI models like OpenAI, Claude, Google, Llama, and more with just one API.

😄 Welcome to use the following invitation link [AiHubMix invitation link](https://aihubmix.com?aff=Gp54) to register 🌹

🌟 **Please note that wiseflow itself does not limit any model services, as long as the service is compatible with the openAI SDK, including locally deployed services like ollama, Xinference, etc.**


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

For commercial and custom cooperation, please contact **Email: 35252986@qq.com**

- Commercial customers, please contact us for registration. The product promises to be forever free.


## 📬 Contact

If you have any questions or suggestions, please feel free to leave a message via [issue](https://github.com/TeamWiseFlow/wiseflow/issues).


## 🤝 This Project is Based on the Following Excellent Open-Source Projects:

- crawlee-python (A web scraping and browser automation library for Python to build reliable crawlers. Works with BeautifulSoup, Playwright, and raw HTTP. Both headful and headless mode. With proxy rotation.) https://github.com/apify/crawlee-python
- json_repair (Repair invalid JSON documents) https://github.com/josdejong/jsonrepair/tree/main 
- python-pocketbase (pocketBase client SDK for python) https://github.com/vaphes/pocketbase
- SeeAct (a system for generalist web agents that autonomously carry out tasks on any given website, with a focus on large multimodal models (LMMs) such as GPT-4Vision.) https://github.com/OSU-NLP-Group/SeeAct

Also inspired by [GNE](https://github.com/GeneralNewsExtractor/GeneralNewsExtractor) and [AutoCrawler](https://github.com/kingname/AutoCrawler).

## Citation

If you reference or cite part or all of this project in your related work, please specify the following information:

```
Author: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```