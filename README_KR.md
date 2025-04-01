# AI 수석 정보 책임자 (Wiseflow)

**[English](README_EN.md) | [日本語](README_JP.md) | [简体中文](README.md)**

🚀 **대규모 모델을 사용하여 방대한 정보와 다양한 소스에서 매일 당신이 সত্যিই 관심 있는 정보를 찾아보세요!**

우리가 부족한 것은 정보가 아니라, 방대한 정보 속에서 노이즈를 필터링하여 가치 있는 정보를 드러내는 것입니다.

🌱 수석 정보 책임자가 어떻게 시간을 절약하고, 관련 없는 정보를 필터링하며, 관심 사항을 정리하는지 살펴보세요! 🌱

https://github.com/user-attachments/assets/fc328977-2366-4271-9909-a89d9e34a07b


## 🔥🔥🔥 AI 수석 정보 책임자 온라인 체험 서비스가 공개 베타 테스트를 시작했습니다. 배포 및 설정이 필요 없고, 각종 키를 추가로 신청할 필요 없이, 가입만으로 사용 가능합니다!

온라인 체험 주소: https://www.aiqingbaoguan.com/

공개 베타 기간 동안, 가입 시 10 포인트의 연산 능력을 증정합니다 (각 관심 지점은 매일 1 포인트를 소모하며, 정보 출처 수는 계산하지 않습니다).

*온라인 서버는 알리바바 클라우드에 구축되어 있으며, 중국 대륙 외부 사이트 접속이 제한되어 있으며, 온라인 서비스는 현재 WeChat 공식 계정을 지원하지 않습니다. 만약 당신의 정보원이 이러한 유형이라면, 오픈소스 버전을 자체 배포하는 것을 권장합니다.*

## 🌟 V3.9-patch3 버전 출시

이번 업그레이드에 대한 자세한 내용은 [CHANGELOG.md](./CHANGELOG.md)를 참조하십시오.

이 버전부터 버전 번호 명명 규칙을 업데이트합니다. V0.3.9 -> V3.9, V0.3.8 -> V3.8, V0.3.7 -> V3.7, V0.3.6 -> V3.6, V0.3.5 -> V3.5 ...

현재 온라인 서비스 코어는 V3.9-patch3 버전을 기반으로 합니다.

**V0.3.8 및 이전 버전 사용자는 업그레이드 후 Python 환경에서 Crawl4ai를 삭제하는 것이 좋습니다 (`pip uninstall crawl4ai`).**

**V0.3.7 및 이전 버전 사용자는 업그레이드 후 pb 폴더에서 ./pocketbase migrate를 한 번 실행하십시오.**

다음 커뮤니티 멤버들이 V0.3.5~V0.3.9 버전에서 PR을 기여해 주셨습니다:

  - @ourines는 install_pocketbase.sh 자동 설치 스크립트를 기여했습니다
  - @ibaoger는 Windows용 pocketbase 자동 설치 스크립트를 기여했습니다
  - @tusik는 비동기 llm wrapper를 기여하고 AsyncWebCrawler의 수명 주기 문제를 발견했습니다
  - @c469591는 Windows 버전 시작 스크립트를 기여했습니다
  - @braumye는 Docker 실행 방안을 기여했습니다
  - @YikaJ는 install_pocketbase.sh 최적화를 제공했습니다
  - @xxxiaogangg는 내보내기 스크립트 참조를 기여했습니다
  

## 🧐 '딥 서치(deep search)' VS '와이드 서치(wide search)'

저는 wiseflow의 제품 포지셔닝을 "와이드 서치"라고 부릅니다. 이는 현재 뜨겁게 떠오르고 있는 "딥 서치"와는 상대적인 개념입니다.

구체적으로 "딥 서치"는 특정 문제에 대해 LLM이 자체적으로 동적 계획 검색 경로를 설정하고, 지속적으로 다양한 페이지를 탐색하며, 충분한 정보를 수집한 후 답변을 제공하거나 보고서를 생성하는 방식입니다. 하지만 때로는 구체적인 문제가 없고, 깊이 있는 탐색도 필요하지 않으며, 광범위한 정보 수집(예: 산업 정보 수집, 대상 배경 정보 수집, 고객 정보 수집 등)만 필요한 경우가 있습니다. 이럴 때는 넓은 범위가 훨씬 더 의미가 있습니다. "딥 서치"를 사용하여 이러한 작업을 수행할 수도 있지만, 이는 모기를 잡는 데 대포를 쏘는 격으로, 효율성은 낮고 비용은 높습니다. 반면 wiseflow는 이러한 "와이드 서치" 시나리오를 위해 특별히 제작된 도구입니다.

## ✋ 다른 AI 기반 크롤러와 wiseflow의 차이점은 무엇인가요?

가장 큰 차이점은 스크레이퍼 단계에서 기존 크롤러와는 다른 파이프라인, 즉 "크롤링과 검사를 통합"하는 전략을 제안한다는 것입니다. 구체적으로, 우리는 전통적인 필터-추출기 프로세스(물론 이 프로세스도 crawl4ai처럼 LLM을 통합할 수 있습니다)를 포기하고, 단일 페이지를 최소 처리 단위로 취급하지 않습니다. 대신 crawl4ai의 html2markdown을 기반으로 페이지를 더 세분화하고, 일련의 특징 알고리즘에 따라 블록을 "본문 블록"과 "외부 링크 블록"으로 나눕니다. 분류에 따라 다른 LLM 추출 전략을 사용합니다(여전히 각 블록은 LLM으로 한 번만 분석하지만, 분석 전략이 다르므로 토큰 낭비를 방지합니다). 이 방식은 목록 페이지, 콘텐츠 페이지 및 혼합 페이지 등 다양한 상황에 모두 적용할 수 있습니다.

  - "본문 블록"의 경우, 관심 지점에 따라 직접 요약 및 추출을 수행하여 정보 분산을 방지하고, 심지어 이 과정에서 직접 번역 등을 완료합니다.
  - "외부 링크 블록"의 경우, 페이지 레이아웃 등의 정보를 종합하여 어떤 링크를 더 탐색할 가치가 있는지, 어떤 링크를 무시할지 판단합니다. 따라서 사용자가 수동으로 깊이, 최대 크롤링 수 등을 구성할 필요가 없습니다.

이 방식은 실제로 AI 검색과 매우 유사합니다.

또한 특정 유형의 페이지(예: 위챗 공식 계정 게시글(무려 9가지 형식이 있습니다...))를 위해 특별히 작성된 파싱 모듈도 있습니다. 이러한 콘텐츠의 경우, wiseflow는 현재 동종 제품 중 최고의 파싱 효과를 제공할 수 있습니다.

## ✋ 다음 계획(4.x 계획)은 무엇인가요?

### 크롤러 페칭(fetching) 단계 강화

3.x 아키텍처에서 크롤러 페칭 부분은 Crawl4ai를 완전히 사용합니다. 4.x에서도 일반 페이지를 가져오는 데는 이 방식을 계속 사용하겠지만, 소셜 플랫폼 페칭 방식을 점진적으로 추가할 예정입니다.

### 인사이트(Insight) 모듈

사실 진정으로 가치 있는 것은 "수집할 수 있는 정보"가 아니라, 이러한 정보 아래 숨겨진 "숨겨진 정보"일 수 있습니다. 수집된 정보를 지능적으로 연결하고, 그 아래 숨겨진 "숨겨진 정보"를 분석하고 추출하는 것이 4.x에서 중점적으로 구축할 인사이트 모듈입니다.


## 📥 설치 및 사용

### 1. 코드 저장소 복제

🌹 좋아요, fork는 좋은 습관입니다 🌹

**windows 사용자는 먼저 git bash 도구를 다운로드해야 합니다** [링크](https://git-scm.com/downloads/win)

```bash
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

### 2. 루트 디렉토리에서 install_pocketbase 스크립트 실행

for linux/macos users:

```bash
chmod +x install_pocketbase
./install_pocketbase
```

**윈도우 사용자는 [install_pocketbase.ps1](./install_pocketbase.ps1) 스크립트를 실행하세요**

Wiseflow 3.x는 데이터베이스로 pocketbase를 사용합니다. pocketbase 클라이언트를 수동으로 다운로드할 수도 있습니다(버전 0.23.4를 다운로드하여 [pb](./pb) 디렉토리에 배치하는 것을 잊지 마세요). 그리고 수퍼유저를 수동으로 생성할 수 있습니다(.env 파일에 저장하는 것을 잊지 마세요).

자세한 내용은 [pb/README.md](/pb/README.md)를 참조하세요.

### 3. core/.env 파일 구성 계속하기

🌟 **이전 버전과 다릅니다** - V0.3.5부터 .env 파일은 [core](./core) 폴더에 위치해야 합니다.

#### 3.1 대규모 언어 모델 구성

Wiseflow는 LLM 네이티브 애플리케이션이므로 프로그램에 안정적인 LLM 서비스를 제공하도록 해주세요.

🌟 **Wiseflow는 모델 서비스의 출처를 제한하지 않습니다 - ollama, Xinference 등 로컬에 배포된 서비스를 포함하여 openAI SDK와 호환되는 서비스라면 모두 사용할 수 있습니다**

#### 추천 1: Siliconflow가 제공하는 MaaS 서비스 사용

Siliconflow는 대부분의 주류 오픈소스 모델에 대한 온라인 MaaS 서비스를 제공합니다. 축적된 추론 가속화 기술로 속도와 가격 모두에서 큰 장점이 있습니다. siliconflow의 서비스를 사용할 때 .env 구성은 다음을 참조할 수 있습니다:

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://api.siliconflow.cn/v1"
PRIMARY_MODEL="deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"
SECONDARY_MODEL="Qwen/Qwen2.5-14B-Instruct"
VL_MODEL="deepseek-ai/deepseek-vl2"
PROJECT_DIR="work_dir"
```
      
😄 원하신다면 제 [siliconflow 추천 링크](https://cloud.siliconflow.cn/i/WNLYbBpi)를 사용하실 수 있습니다. 이를 통해 제가 더 많은 토큰 보상을 받을 수 있습니다 🌹

#### 추천 2: OpenAI, Claude, Gemini와 같은 폐쇄형 상용 모델에는 AiHubMix 프록시 사용

정보 소스가 대부분 비한국어 페이지이고 추출된 정보가 한국어일 필요가 없다면, OpenAI, Claude, Gemini와 같은 폐쇄형 상용 모델을 사용하는 것이 좋습니다. 서드파티 프록시인 **AiHubMix**를 시도해볼 수 있습니다. 하나의 API로 OpenAI, Claude, Google, Llama 등 주요 AI 모델에 원활하게 접근할 수 있습니다.

AiHubMix 모델을 사용할 때 .env 구성은 다음을 참조할 수 있습니다:

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://aihubmix.com/v1" # refer https://doc.aihubmix.com/
PRIMARY_MODEL="gpt-4o"
SECONDARY_MODEL="gpt-4o-mini"
VL_MODEL="gpt-4o"
PROJECT_DIR="work_dir"
```

😄 Welcome to register using the [AiHubMix referral link](https://aihubmix.com?aff=Gp54) 🌹

#### 로컬 대규모 언어 모델 서비스 배포

Xinference를 예로 들면, .env 구성은 다음을 참조할 수 있습니다:

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

여기서 pocketbase 데이터베이스의 슈퍼유저 사용자 이름과 비밀번호를 설정합니다. |로 구분하는 것을 잊지 마세요 (install_pocketbase.sh 스크립트가 성공적으로 실행되었다면 이미 존재할 것입니다)

#### 3.3 智谱（bigmodel）플랫폼 키 설정（검색 엔진 서비스에 사용）

알림: **즈푸 플랫폼은 2025년 3월 14일 0시부터 web_search_pro 인터페이스에 대한 과금을 정식으로 시작합니다. 검색 기능을 사용하려면 계정 잔액을 확인하시기 바랍니다.**
[즈푸 플랫폼 공지](https://bigmodel.cn/dev/api/search-tool/web-search-pro)

```
ZHIPU_API_KEY=Your_API_KEY
```

（신청 주소: https://bigmodel.cn/ ~~현재 무료~~ 0.03 원/회, 계정 잔액을 유지하십시오）

#### 3.4 기타 선택적 구성

다음은 모두 선택적 구성입니다:
- #VERBOSE="true" 

  관찰 모드를 활성화할지 여부. 활성화되면 디버그 정보가 로거 파일에 기록됩니다(기본적으로 콘솔에만 출력);

- #PB_API_BASE="" 

  pocketbase가 기본 IP 또는 포트에서 실행되지 않는 경우에만 구성이 필요합니다. 기본 상황에서는 이를 무시할 수 있습니다.
  
- #LLM_CONCURRENT_NUMBER=8 

  llm 동시 요청 수를 제어하는 데 사용됩니다. 설정하지 않으면 기본값은 1입니다(활성화하기 전에 llm 제공자가 설정된 동시성을 지원하는지 확인하세요. 로컬 대규모 모델은 하드웨어 기반에 자신이 있지 않는 한 신중하게 사용하세요)

### 4. 프로그램 실행

✋ V0.3.5 버전의 아키텍처와 종속성은 이전 버전과 크게 다릅니다. 코드를 다시 가져오고, pb_data를 삭제(또는 재구축)하도록 하세요

가상 환경을 구축하기 위해 conda를 사용하는 것을 권장합니다(물론 이 단계를 건너뛰거나 다른 Python 가상 환경 솔루션을 사용할 수 있습니다)

```bash
conda create -n wiseflow python=3.12
conda activate wiseflow
```

그런 다음

```bash
cd wiseflow
cd core
pip install -r requirements.txt
python -m playwright install --with-deps chromium
```

이후 MacOS&Linux 사용자는 실행합니다

```bash
chmod +x run.sh
./run.sh
```

Windows 사용자는 실행합니다

```bash
python windows_run.py
```

- 이 스크립트는 pocketbase가 이미 실행 중인지 자동으로 판단하고, 실행 중이 아니면 자동으로 시작합니다. 그러나 주의해주세요, ctrl+c 또는 ctrl+z로 프로세스를 종료하더라도, pocketbase 프로세스는 종료되지 않습니다. 터미널을 닫을 때까지입니다.

- run.sh는 먼저 활성화된 (activated가 true로 설정된) 모든 정보원에 대해 한 번의 크롤링 작업을 실행한 후, 설정된 빈도로 시간 단위로 주기적으로 실행합니다.

### 5. 관심사 및 정보원 추가
    
프로그램을 시작한 후, pocketbase Admin dashboard UI (http://127.0.0.1:8090/_/)를 엽니다.

#### 5.1 sites 폼 열기

이 폼을 통해 정보원을 구성할 수 있습니다. 注意：정보원은 다음 단계의 focus_point 폼에서 선택해야 합니다.

sites 필드 설명：
- url, 정보원의 url, 정보원은 특정 기사 페이지를 지정할 필요가 없습니다. 기사 목록 페이지를 지정하면 됩니다.
- type, 유형, web 또는 rss입니다.
    
#### 5.2 focus_point 폼 열기

이 폼을 통해 당신의 관심사를 지정할 수 있습니다. LLM은 이를 기반으로 정보를 추출, 필터링, 분류합니다.
    
필드 설명：
- focuspoint, 관심사 설명（필수），예를 들어 "새해 할인" 또는 "입찰 공고"
- explanation, 관심사의 상세 설명 또는 구체적 약정, 예를 들어 "어떤 브랜드" 또는 "2025년 1월 1일 이후에 발행된 날짜, 100만원 이상의 금액" 등
- activated, 활성화 여부. 활성화하지 않으면 해당 관심사는 무시됩니다. 활성화하지 않으면 나중에 다시 활성화할 수 있습니다.
- per_hour, 크롤링 빈도, 시간 단위, 정수 형식（1~24 범위, 우리는 하루에 한 번씩 스캔하는 것을 추천합니다, 즉 24로 설정합니다）
- search_engine, 각 크롤링 시 검색 엔진을 활성화할지 여부
- sites, 해당 정보원을 선택

**참고：V0.3.8 버전 이후, 설정의 변경은 프로그램을 재시작하지 않아도 다음 실행 시 자동으로 적용됩니다.**

## 🐳 Docker 배포

Docker를 사용하여 Wiseflow를 배포하려는 경우, 완벽한 컨테이너화 지원을 제공합니다.

### 1. 전제 조건

시스템에 Docker가 설치되어 있는지 확인하십시오.

### 2. 환경 변수 구성

루트 디렉토리에서 `env_docker` 파일을 `.env`로 복사하십시오:

```bash
cp env_docker .env
```

### 3. 《[설치 및 사용](#-설치-및-사용)》섹션에 따라 `.env` 파일 수정

다음 환경 변수는 필요에 따라 수정해야 합니다:

```bash
LLM_API_KEY=""
LLM_API_BASE="https://api.siliconflow.cn/v1"
PB_SUPERUSER_EMAIL="test@example.com"
PB_SUPERUSER_PASSWORD="1234567890" #no '&' in the password and at least 10 characters
```

### 4. 서비스 시작

프로젝트 루트 디렉토리에서 실행:

```bash
docker compose up -d
```

서비스 시작 후:

- PocketBase 관리자 인터페이스: http://localhost:8090/_/
- Wiseflow 서비스가 자동으로 실행되고 PocketBase에 연결됩니다

### 5. 서비스 중지

```bash
docker compose down
```

### 6. 중요 참고 사항

- `./pb/pb_data` 디렉토리는 PocketBase 관련 파일을 저장하는 데 사용됩니다
- `./docker/pip_cache` 디렉토리는 Python 종속성 패키지 캐시를 저장하여 반복 다운로드를 방지하는 데 사용됩니다
- `./core/work_dir` 디렉토리는 Wiseflow 런타임 로그를 저장하는 데 사용됩니다. `.env` 파일에서 `PROJECT_DIR`을 수정할 수 있습니다

## 📚 wiseflow가 크롤링한 데이터를 귀하의 프로그램에서 사용하는 방법

1. [dashbord](dashboard) 부분 소스 코드를 참조하여 2차 개발을 수행하세요.

wiseflow의 core 부분은 dashboard를 필요로 하지 않으며, 현재 제품은 dashboard를 통합하지 않았습니다. dashboard가 필요한 경우, [V0.2.1 버전](https://github.com/TeamWiseFlow/wiseflow/releases/tag/V0.2.1)을 다운로드하세요.

2. pocketbase에서 직접 데이터를 가져오세요.

wiseflow가 크롤링한 모든 데이터는 즉시 pocketbase에 저장되므로, pocketbase 데이터베이스를 직접 조작하여 데이터를 가져올 수 있습니다.

PocketBase는 인기 있는 경량 데이터베이스로, 현재 Go/Javascript/Python 등 언어의 SDK를 제공합니다.
   - Go : https://pocketbase.io/docs/go-overview/
   - Javascript : https://pocketbase.io/docs/js-overview/
   - python : https://github.com/vaphes/pocketbase


3. 온라인 서비스도 곧 sync api를 출시하여 온라인 크롤링 결과를 로컬에 동기화하여 "동적 지식 베이스" 등을 구축할 수 있도록 지원할 예정입니다. 많은 관심 부탁드립니다:

  - 온라인 체험 주소: https://www.aiqingbaoguan.com/
  - 온라인 서비스 API 사용 사례: https://github.com/TeamWiseFlow/wiseflow_plus


## 🛡️ 라이선스 계약

이 프로젝트는 [Apache2.0](LICENSE) 오픈소스 라이선스를 기반으로 합니다.

상업적 및 맞춤형 협력은 **Email: zm.zhao@foxmail.com**으로 문의하세요.

- 상업용 고객은 등록을 위해 연락해 주세요. 제품은 영원히 무료로 제공됩니다.

## 📬 연락처

문의 사항이나 제안이 있으면 [issue](https://github.com/TeamWiseFlow/wiseflow/issues)를 통해 문의하세요.

## 🤝 이 프로젝트는 다음과 같은 우수한 오픈소스 프로젝트를 기반으로 합니다:

- crawl4ai（Open-source LLM Friendly Web Crawler & Scraper） https://github.com/unclecode/crawl4ai
- pocketbase (Open Source realtime backend in 1 file) https://github.com/pocketbase/pocketbase
- python-pocketbase (pocketBase 클라이언트 SDK for python) https://github.com/vaphes/pocketbase
- feedparser (Parse feeds in Python) https://github.com/kurtmckee/feedparser

또한 [GNE](https://github.com/GeneralNewsExtractor/GeneralNewsExtractor), [AutoCrawler](https://github.com/kingname/AutoCrawler), [SeeAct](https://github.com/OSU-NLP-Group/SeeAct) 에서 영감을 받았습니다.

## Citation

이 프로젝트의 일부 또는 전체를 관련 작업에서 참조하거나 인용하는 경우, 다음 정보를 명시하세요:

```
Author: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```
