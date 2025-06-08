# WiseFlow Installation and User Manual

**3.x users need to completely delete the original code repository and pb folder, and re-clone the 4.x code repository, otherwise it cannot start normally.**

## 📋 System Requirements

- **Python**: 3.10 - 3.12 (3.12 recommended)
- **Operating System**: macOS, Linux, or Windows
- **Hardware Requirements**: 8GB RAM or more (when using online LLM services)

## 📥 Usage Instructions

WiseFlow 4.x user interface uses PocketBase (though not ideal, it's the current best solution)

### 1. Access Interface

🌐 After successful startup, open your browser and visit: **http://127.0.0.1:8090/_/**

### 2. Configure Information Sources and Focus Points

Switch to the focus_point form

Through this form, you can specify your focus points. The LLM will refine, filter, and categorize information accordingly.

Field descriptions:
- focuspoint (required): Description of the focus point, telling the LLM what information you want, such as "Shanghai primary to secondary school information" or "Tender notices"
- restrictions (optional): Focus point filtering constraints, telling the LLM what information to exclude, such as "Only official Shanghai middle school admission information" or "Published after January 1, 2025, with amounts over 1 million"
- explanation (optional): Explanations for special concepts or technical terms to avoid LLM misunderstandings, such as "primary to secondary school refers to the transition from elementary to middle school"
- activated: Whether to activate. If turned off, this focus point will be ignored, can be turned on again later
- freq: Crawling frequency in hours, integer type (we recommend not exceeding once per day, i.e., set to 24, minimum value is 2, i.e., crawl every 2 hours)
- search: Whether to enable search engine for each crawl, and whether to search through configured social media
- sources: Select corresponding information sources

**Focus point configuration adjustments take effect automatically on the next execution without requiring program restart.**

You can add information sources in either the sources page or the focus_points binding page. Information source addition field descriptions:

- type: Type, currently supports: web, rss, wb (Weibo), ks (Kuaishou), mp (WeChat Official Account (4.0 temporarily not supported, waiting for 4.1))
- creators: Creator IDs to crawl (multiple separated by ','), only valid for ks, wb, and mp, where ks and mp support entering 'homefeed' (represents getting system-pushed content each time). This field can also be left empty, then the source is only used for searching

  *Note: IDs should use the platform's corresponding web version homepage link, for example, if Weibo's ID is https://m.weibo.cn/profile/2656274875, then the ID is 2656274875*

- url: Link corresponding to the information source, only valid for rss and web types.

### 3. View Results

- infos page: Stores the final extracted useful information
- crawled_data page: Stores the original crawled data
- ks_cache page: Stores Kuaishou cache data
- wb_cache page: Stores Weibo cache data

## 🌟 Deployment Installation

**Deployment installation only takes three steps!**

### 📋 Download Project Source Code and Install uv and PocketBase

- for MacOS/Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

- for Windows:

**Windows users please download Git Bash tool in advance and execute the following commands in bash [Bash download link](https://git-scm.com/downloads/win)**

```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

The above operations will complete the installation of uv. For PocketBase installation, please refer to [PocketBase docs](https://pocketbase.io/docs/)

You can also try using install_pocketbase.sh (for MacOS/Linux) or install_pocketbase.ps1 (for Windows) to install.

### 📥 Configure .env File Based on env_sample

In the wiseflow folder (project root directory), create a .env file based on env_sample and fill in the relevant settings.

Version 4.x does not require users to provide PocketBase account credentials in .env, nor does it limit the PocketBase version. We have also temporarily removed the Secondary Model setting. Therefore, you actually only need four parameters to complete the configuration:

- LLM_API_KEY="" # LLM service key (any model service provider that provides OpenAI format API is acceptable, no need to set if using locally deployed ollama)
- LLM_API_BASE="https://api.siliconflow.com/v1" # LLM service interface address
- JINA_API_KEY="" # Search engine service key (Jina recommended, even personal use can apply without registration)
- PRIMARY_MODEL="Qwen3-14B" # Qwen3-14B or similar thinking model recommended
- VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct" # Visual model, optional but recommended. Used for analyzing necessary page images (program will determine if analysis is necessary based on context, won't extract every image), minimum Qwen2.5-VL-7B-Instruct is sufficient

### 🚀 Let's Go!

- for MacOS/Linux:

```bash
cd wiseflow
uv venv # Only needed for first execution
uv sync # Only needed for first execution
python -m playwright install --with-deps chromium # Only needed for first execution
chmod +x run.sh # Only needed for first execution
./run.sh
```

- for Windows:

```bash
cd wiseflow
uv venv # Only needed for first execution
uv sync # Only needed for first execution
python -m playwright install --with-deps chromium # Only needed for first execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser # Only needed for first execution
.\run.ps1
```

✨ **It's that simple!** The startup script will automatically complete the following tasks:
- ✅ Check environment configuration
- ✅ Synchronize project dependencies
- ✅ Activate virtual environment
- ✅ Start PocketBase database
- ✅ Run WiseFlow application

The program will first perform a crawling task for all activated sources (activated set to true), then execute periodically according to the set frequency in hours.

⚠️ **Note:** When you use `Ctrl+C` to terminate the process, the PocketBase process may not terminate automatically and may need to be closed manually or the terminal restarted.

### 📝 Manual Installation (Optional)

If you want to manually control each step, you can follow these steps:

#### 1. Execute the install_pocketbase script in the root directory

Linux/macOS users please execute:

```bash
chmod +x install_pocketbase.sh
./install_pocketbase.sh
```

**Windows users please execute:**
```powershell
.\install_pocketbase.ps1
```

#### 2. Create and Activate Virtual Environment

```bash
uv venv
source .venv/bin/activate  # Linux/macOS
# Or on Windows:
# .venv\Scripts\activate
```

##### 4.2 Install Dependencies

```bash
uv sync
```

This will install WiseFlow and all its dependencies, ensuring dependency version consistency. uv sync reads the project's dependency declarations and synchronizes the virtual environment.

Then install browser dependencies:

```bash
python -m playwright install --with-deps chromium
```

Finally, start the main service:

```bash
python core/run_task.py
# Or on Windows:
# python core\run_task.py
```

When you need to use the PocketBase user interface, start the PocketBase service:

```bash
cd wiseflow/pb
./pocketbase serve
```

Or on Windows:

```powershell
cd wiseflow\pb
.\pocketbase.exe serve
```

### 🔧 Configure Environment Variables

Whether using quick start or manual installation, you need to create a .env file based on env_sample:

#### 1. LLM Related Configuration

WiseFlow is an LLM-native application, please ensure stable LLM service is provided to the program.

🌟 **WiseFlow does not limit the model service provider, as long as the service is compatible with OpenAI SDK, including locally deployed ollama, Xinference, and other services**

##### Recommendation 1: Use SiliconFlow's MaaS Service

SiliconFlow provides online MaaS services for most mainstream open-source models. With their acceleration inference technology, their service has advantages in both speed and price. When using SiliconFlow's service, .env configuration can refer to:

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://api.siliconflow.com/v1"
PRIMARY_MODEL="Qwen3-14B"
VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct"
CONCURRENT_NUMBER=8
```

😄 If you'd like, you can use my [SiliconFlow invitation link](https://cloud.siliconflow.com/i/WNLYbBpi), so I can get more token rewards 🌹

##### Recommendation 2: Use AiHubMix's proxied overseas closed-source commercial model services like OpenAI, Claude, Gemini

If your information sources are mostly non-Chinese pages and you don't require the extracted info to be in Chinese, then overseas closed-source commercial models like OpenAI, Claude, Gemini are more recommended. You can try third-party proxy **AiHubMix**, which supports direct connection in Chinese network environment, convenient Alipay payment, and eliminates account blocking risks.
When using AiHubMix's models, .env configuration can refer to:

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://aihubmix.com/v1" # For details, refer to https://doc.aihubmix.com/
PRIMARY_MODEL="gpt-4o-mini"
VL_MODEL="gpt-4o"
CONCURRENT_NUMBER=8
```

😄 Welcome to register using [AiHubMix invitation link](https://aihubmix.com?aff=Gp54) 🌹

##### Local LLM Service Deployment

Taking Xinference as an example, .env configuration can refer to:

```
# LLM_API_KEY='' Not needed for local service, please comment out or delete
LLM_API_BASE='http://127.0.0.1:9997' # 'http://127.0.0.1:11434/v1' for ollama
PRIMARY_MODEL=Started model ID
VL_MODEL=Started model ID
CONCURRENT_NUMBER=1 # Determine based on actual hardware resources
```

#### 3. JINA_API_KEY Setting (for Search Engine Service)

Get it at https://jina.ai/, currently available without registration. (Please recharge for high concurrency or commercial use)

```
JINA_API_KEY=Your_API_KEY
```

#### 4. Other Optional Configurations

The following are optional configurations:
- #VERBOSE="true" 

  Whether to enable observation mode, if enabled, debug information will be recorded in the logger file (default only outputs to console)

- #CONCURRENT_NUMBER=8 

  Used to control the number of concurrent LLM requests, default is 1 if not set (please ensure the LLM provider supports the set concurrency before enabling, use with caution for local large models unless you're confident in your hardware foundation)

## 🐳 Docker Deployment

Docker deployment solution for version 4.x please wait for follow-up, and we also hope interested developers can contribute PRs~

## 🌹 Paid Services

Open source is not easy ☺️ Documentation writing and consultation Q&A are even more time-consuming. If you're willing to provide support, we'll offer better quality services~

- Detailed tutorial video + 3 email Q&A sessions: $1.99
- Detailed tutorial video + 3 email Q&A sessions + Join paid user WeChat group: $2.99

*Note: The paid user group does not provide Q&A services, it's only for exchanging product requirements and usage experiences. Future iterations will prioritize high-frequency requirements from the paid user group, and system optimization will mainly target cases from the paid user group*

Payment method: Scan the payment code below, fill in your email in the remarks when paying, and we will contact you within 24 hours to provide service.

<img src="alipay.png" alt="Alipay Payment Code" width="300">      <img src="weixinpay.jpg" alt="WeChat Payment Code" width="300"> 