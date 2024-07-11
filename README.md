# WiseFlow

**[中文](README_CN.md) | [日本語](README_JP.md) | [Français](README_FR.md) | [Deutsch](README_DE.md)**

**Wiseflow** is an agile information extraction tool that can refine information from various sources such as websites, WeChat Public Accounts, and social media platforms based on predefined focus points, automatically categorize tags, and upload to the database.

---

SiliconFlow has officially announced that several LLM online inference services, such as Qwen2-7B-Instruct and glm-4-9b-chat, will be free starting from June 25, 2024. This means you can perform information mining with wiseflow at “zero cost”!

---

We are not short of information; what we need is to filter out the noise from the vast amount of information so that valuable information stands out! 

See how WiseFlow helps you save time, filter out irrelevant information, and organize key points of interest!

https://github.com/TeamWiseFlow/wiseflow/assets/96130569/bd4b2091-c02d-4457-9ec6-c072d8ddfb16

<img alt="sample.png" src="asset/sample.png" width="1024"/>

## 🔥 Major Update V0.3.0

- ✅ Completely rewritten general web content parser, using a combination of statistical learning (relying on the open-source project GNE) and LLM, adapted to over 90% of news pages;


- ✅ Brand new asynchronous task architecture;


- ✅ New information extraction and labeling strategy, more accurate, more refined, and can perform tasks perfectly with only a 9B LLM!

## 🌟 Key Features

- 🚀 **Native LLM Application**  
  We carefully selected the most suitable 7B~9B open-source models to minimize usage costs and allow data-sensitive users to switch to local deployment at any time.


- 🌱 **Lightweight Design**  
  Without using any vector models, the system has minimal overhead and does not require a GPU, making it suitable for any hardware environment.


- 🗃️ **Intelligent Information Extraction and Classification**  
  Automatically extracts information from various sources and tags and classifies it according to user interests.

  😄 **Wiseflow is particularly good at extracting information from WeChat official account articles**; for this, we have configured a dedicated mp article parser!


- 🌍 **Can be Integrated into Any Agent Project**  
  Can serve as a dynamic knowledge base for any Agent project, without needing to understand the code of Wiseflow, just operate through database reads!


- 📦 **Popular Pocketbase Database**  
  The database and interface use PocketBase. Besides the web interface, SDK for Go/Javascript/Python languages are available.
    
    - Go: https://pocketbase.io/docs/go-overview/
    - Javascript: https://pocketbase.io/docs/js-overview/
    - Python: https://github.com/vaphes/pocketbase

## 🔄 What are the Differences and Connections between Wiseflow and Common Crawlers, LLM-Agent Projects?

| Feature         | Wiseflow | Crawler / Scraper                        | LLM-Agent                                          |
|-----------------|--------------------------------------|------------------------------------------|----------------------------------------------------|
| **Main Problem Solved** | Data processing (filtering, extraction, labeling) | Raw data acquisition                      | Downstream applications                            |
| **Connection**  |                                      | Can be integrated into Wiseflow for more powerful raw data acquisition | Can integrate Wiseflow as a dynamic knowledge base |

## 📥 Installation and Usage

WiseFlow has virtually no hardware requirements, with minimal system overhead, and does not need GPU or CUDA (when using online LLM services).

1. **Clone the Repository**

     😄 Starring and forking are good habits

    ```bash
    git clone https://github.com/TeamWiseFlow/wiseflow.git
    cd wiseflow
    ```

2. **Highly Recommended: Use Docker**

    **For users in China, please configure your network properly or specify a Docker Hub mirror**

    ```bash
    docker compose up
    ```
   You may modify `compose.yaml` as needed.

    **Note:**
    - Run the above command in the root directory of the wiseflow repository.
    - Before running, create and edit a `.env` file in the same directory as the Dockerfile (root directory of the wiseflow repository). Refer to `env_sample` for the `.env` file.
    - The first time you run the Docker container, an error might occur because you haven't created an admin account for the pb repository.

    At this point, keep the container running, open `http://127.0.0.1:8090/_/` in your browser, and follow the instructions to create an admin account (make sure to use an email). Then enter the created admin email (again, make sure it's an email) and password into the `.env` file, and restart the container.

    _If you want to change the container's timezone and language [which will determine the prompt language, but has little effect on the results], run the image with the following command_

    ```bash
    docker run -e LANG=zh_CN.UTF-8 -e LC_CTYPE=zh_CN.UTF-8 your_image
    ```

3. **[Alternative] Run Directly with Python**

    ```bash
    conda create -n wiseflow python=3.10
    conda activate wiseflow
    cd core
    pip install -r requirements.txt
    ```

    You can then start pb, task, and backend individually using the scripts in core/scripts (move the script files to the core directory).

    Note:
    - Start pb first; task and backend are independent processes, and the order doesn't matter. You can start any one of them as needed.
    - Download the pocketbase client suitable for your device from https://pocketbase.io/docs/ and place it in the /core/pb directory.
    - For issues with pb (including first-run errors), refer to [core/pb/README.md](/core/pb/README.md).
    - Before use, create and edit a `.env` file and place it in the root directory of the wiseflow repository (the directory above core). Refer to `env_sample` for the `.env` file, and see below for detailed configuration.


    📚 For developers, see [/core/README.md](/core/README.md) for more information.

    Access data via pocketbase:
    - http://127.0.0.1:8090/_/ - Admin dashboard UI
    - http://127.0.0.1:8090/api/ - REST API


4. **Configuration**

    Copy `env_sample` from the directory and rename it to `.env`, then fill in your configuration information (such as LLM service tokens) as follows:

   - LLM_API_KEY # API key for large language model inference services
   - LLM_API_BASE # This project relies on the OpenAI SDK. Configure this if your model service supports OpenAI's API. If using OpenAI's service, you can omit this.
   - WS_LOG="verbose"  # Set to enable debug observation. Delete if not needed.
   - GET_INFO_MODEL # Model for information extraction and tag matching tasks, default is gpt-3.5-turbo
   - REWRITE_MODEL # Model for approximate information merging and rewriting tasks, default is gpt-3.5-turbo
   - HTML_PARSE_MODEL # Model for web page parsing (intelligently enabled if the GNE algorithm performs poorly), default is gpt-3.5-turbo
   - PROJECT_DIR # Storage location for data, cache, and log files, relative to the repository. Default is within the repository.
   - PB_API_AUTH='email|password' # Email and password for the pb database admin (must be an email, can be a fictitious one)
   - PB_API_BASE  # Typically unnecessary. Only configure if you're not using the default local pocketbase interface (8090).


5. **Model Recommendations**

    Based on extensive testing (for both Chinese and English tasks), we recommend **"zhipuai/glm4-9B-chat"** for **GET_INFO_MODEL**, **"alibaba/Qwen2-7B-Instruct"** for **REWRITE_MODEL**, and **"alibaba/Qwen2-7B-Instruct"** for **HTML_PARSE_MODEL**.

    These models are well-suited for this project, with stable adherence to instructions and excellent generation quality. The project's prompts have been optimized for these three models. (**HTML_PARSE_MODEL** can also use **"01-ai/Yi-1.5-9B-Chat"**, which has been tested to perform excellently.)


    ⚠️ We highly recommend using **SiliconFlow**'s online inference service for lower costs, faster speeds, and higher free quotas! ⚠️

    SiliconFlow's online inference service is compatible with the OpenAI SDK and provides open-source services for the above three models. Simply configure `LLM_API_BASE` to "https://api.siliconflow.cn/v1" and set `LLM_API_KEY` to use it.

    😄 Alternatively, you can use my [invitation link](https://cloud.siliconflow.cn?referrer=clx6wrtca00045766ahvexw92), which also rewards me with more tokens 😄


6. **Focus Points and Scheduled Source Scanning**

    After starting the program, open the pocketbase Admin dashboard UI (http://127.0.0.1:8090/_/)

        6.1 Open the **tags form**

        Use this form to specify your focus points. The LLM will extract, filter, and classify information based on these.

        Tags field description:

        - name, Description of the focus point. **Note: Be specific.** Good example: `Trends in US-China competition`. Bad example: `International situation`.
        - activated, Whether activated. If deactivated, the focus point will be ignored. It can be reactivated later. Activation and deactivation don't require a Docker container restart and will update in the next scheduled task.

        6.2 Open the **sites form**

        Use this form to specify custom sources. The system will start background tasks to scan, parse, and analyze these sources locally.

        Sites field description:

        - url, URL of the source. Provide a URL to the list page rather than a specific article page.
        - per_hours, Scan frequency in hours, as an integer (range 1-24; we recommend no more than once a day, i.e., set to 24).
        - activated, Whether activated. If deactivated, the source will be ignored. It can be reactivated later. Activation and deactivation don't require a Docker container restart and will update in the next scheduled task.


7. **Local Deployment**

    As you can see, this project uses 7B/9B LLMs and does not require any vector models, which means you only need a single RTX 3090 (24GB VRAM) to fully deploy this project locally.

    Ensure your local LLM service is compatible with the OpenAI SDK and configure `LLM_API_BASE` accordingly.


## 🛡️ License

This project is open-source under the [Apache 2.0](LICENSE) license.

For commercial use and customization cooperation, please contact **Email: 35252986@qq.com**.

- Commercial customers, please register with us. The product promises to be free forever.
- For customized customers, we provide the following services according to your sources and business needs:
  - Dedicated crawler and parser for customer business scenario sources
  - Customized information extraction and classification strategies
  - Targeted LLM recommendations or even fine-tuning services
  - Private deployment services
  - UI interface customization

## 📬 Contact Information

If you have any questions or suggestions, feel free to contact us through [issue](https://github.com/TeamWiseFlow/wiseflow/issues).

## 🤝 This Project is Based on the Following Excellent Open-source Projects:

- GeneralNewsExtractor (General Extractor of News Web Page Body Based on Statistical Learning) https://github.com/GeneralNewsExtractor/GeneralNewsExtractor
- json_repair (Repair invalid JSON documents) https://github.com/josdejong/jsonrepair/tree/main 
- python-pocketbase (PocketBase client SDK for Python) https://github.com/vaphes/pocketbase

# Citation

If you refer to or cite part or all of this project in related work, please indicate the following information:

```
Author: Wiseflow Team
https://openi.pcl.ac.cn/wiseflow/wiseflow
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```