# AI 수석 정보 책임자 (Wiseflow)

**[English](README_EN.md) | [日本語](README_JP.md) | [简体中文](README.md)**

🚀 **AI 수석 정보 책임자** (Wiseflow)는 대규모 언어 모델의 사고 및 분석 능력을 활용하여 다양한 정보원에서 특정 정보를 정확하게 추출할 수 있는 민첩한 정보 마이닝 도구입니다. 전체 과정에서 인간의 개입이 필요하지 않습니다.

**우리가 부족한 것은 정보가 아니라, 방대한 정보 속에서 노이즈를 필터링하여 가치 있는 정보를 드러내는 것입니다.**

🌱 수석 정보 책임자가 어떻게 시간을 절약하고, 관련 없는 정보를 필터링하며, 관심 사항을 정리하는지 살펴보세요! 🌱

https://github.com/user-attachments/assets/fc328977-2366-4271-9909-a89d9e34a07b


🌟 알림: 최근 DeepSeek R1과 같은 reasoning 모델이 뛰어나다는 이야기를 많이 들었을 수도 있습니다(저도 이를 부정하지 않습니다). 하지만 WiseFlow의 정보 추출 및 요약 작업에는 복잡한 논리적 추론이 필요하지 않으며, reasoning 모델을 사용하면 오히려 처리 시간이 크게 증가하고 비용도 상승하게 됩니다! 이 결론에 대해 더 자세히 알고 싶다면, 아래 테스트 보고서를 참고하세요: [wiseflow V0.38 with deepseek series report](./test/reports/wiseflow_report_v038_dp_bigbrother666/README.md).

현재 우리는 일반적인 대형 언어 모델을 계속 사용하는 것을 추천합니다. 또한 기존 프롬프트를 개선하여 7B 및 14B 모델의 출력 품질을 향상시켰습니다. 생성 속도와 비용이 중요한 경우, `PRIMARY_MODEL`과 `SECONDARY_MODEL`을 `Qwen2.5-14B-Instruct`로 설정하는 것을 권장합니다.


## 🔥 V0.3.8 공식 출시

- V0.3.8 버전에서는 RSS 및 검색 엔진에 대한 지원이 도입되어, 이제 wiseflow는 _웹사이트_, _rss_, _검색 엔진_, _WeChat 공식 계정_의 네 가지 정보원을 지원합니다!

- 제품 전략이 관심 지점에 따라 정보원을 지정하는 방식으로 변경되어, 서로 다른 정보원에 대해 서로 다른 관심 지점을 지정할 수 있게 되었습니다. 동일한 모델에서 정보 추출의 정확성을 더욱 향상시킬 수 있음을 실험을 통해 확인했습니다.

- MacOS&Linux와 Windows 사용자 각각에게 단일 시작 스크립트를 제공하여, 시작 프로그램을 최적화하고 사용 편의성을 높였습니다.

이번 업그레이드에 대한 자세한 내용은 [CHANGELOG.md](./CHANGELOG.md)를 참조하세요.

**V0.3.8 버전의 검색 엔진은 Zhipu bigmodel 오픈 플랫폼에서 제공하는 서비스를 사용하며, .env 파일에 ZHIPU_API_KEY를 추가해야 합니다**

**V0.3.8 버전에서는 pocketbase의 폼 구조가 조정되었으므로, 기존 사용자는 ./pocketbase migrate를 한 번 실행해야 합니다 (pb 폴더 내)**

V0.3.8은 안정적인 버전입니다. 원래 계획된 V0.3.9는 커뮤니티의 피드백을 더 많이 수집하여 업그레이드 방향을 결정해야 하므로 출시까지 시간이 더 걸릴 것입니다.

다음 커뮤니티 멤버들이 V0.3.5~V0.3.8 버전에서 PR을 기여해 주셨습니다:

  - @ourines는 install_pocketbase.sh 자동 설치 스크립트를 기여했습니다
  - @ibaoger는 Windows용 pocketbase 자동 설치 스크립트를 기여했습니다
  - @tusik는 비동기 llm wrapper를 기여하고 AsyncWebCrawler의 수명 주기 문제를 발견했습니다
  - @c469591는 Windows 버전 시작 스크립트를 기여했습니다
  
### 🌟 테스트 보고서

최신 추출 전략에서, 7b와 같은 규모의 모델도 링크 분석 및 추출 작업을 잘 수행할 수 있다는 것을 발견했습니다. 테스트 결과는 [report](./test/reports/wiseflow_report_v037_bigbrother666/README.md)를 참조하세요.

하지만 정보 요약 작업의 경우 여전히 32b 이상 규모의 모델을 사용하는 것을 권장합니다. 자세한 권장 사항은 최신 [env_sample](./env_sample)을 참조하세요.

계속해서 더 많은 테스트 결과를 제출해 주시기를 환영합니다. 다양한 정보 소스에서 wiseflow의 최적 사용 방안을 함께 탐구해 봅시다.

현재 단계에서는 **테스트 결과 제출이 프로젝트 코드 제출과 동등하게 취급**되며, contributor로 인정받을 수 있고, 심지어 상업화 프로젝트에 초대될 수도 있습니다! 자세한 내용은 [test/README.md](./test/README.md)를 참조하세요.

## ✋ wiseflow는 전통적인 크롤러 도구, AI 검색, 지식 베이스(RAG) 프로젝트와 어떻게 다를까요?

wiseflow는 2024년 6월 말 V0.3.0 버전 출시 이후 오픈소스 커뮤니티의 광범위한 관심을 받았으며, 심지어 많은 자체 미디어의 자발적인 보도까지 이끌어냈습니다. 이에 먼저 감사의 말씀을 전합니다!

그러나 우리는 일부 관심 있는 분들이 wiseflow의 기능 위치에 대해 일부 이해 오류가 있음을 알게 되었습니다. 아래 표는 전통적인 크롤러 도구, AI 검색, 지식 베이스(RAG) 프로젝트와의 비교를 통해 wiseflow 제품의 최신 위치에 대한 우리의 생각을 나타냅니다.

|          | **수석 정보 책임자 (Wiseflow)**와의 비교 설명 | 
|-------------|--------------------------------------------------------------------------|
| **크롤러 도구** | 먼저, wiseflow는 크롤러 도구를 기반으로 한 프로젝트이지만, 전통적인 크롤러 도구는 정보 추출을 위해 명시적인 Xpath 등의 정보를 수동으로 제공해야 합니다... 이는 일반 사용자를 막을 뿐만 아니라 범용성도 없습니다. 다양한 웹사이트(기존 웹사이트 업그레이드 후 포함)에 대해 수동으로 재분석하고 프로그램을 업데이트해야 합니다. wiseflow는 LLM을 사용하여 웹 페이지의 분석과 추출을 자동화하는 데 주력하고 있으며, 사용자는 프로그램에 자신의 관심사를 알리기만 하면 됩니다. Crawl4ai를 예로 들어 비교하자면, Crawl4ai는 LLM을 사용하여 정보를 추출하는 크롤러이고, wiseflow는 크롤러 도구를 사용하는 LLM 정보 추출기입니다.  |
| **AI 검색** | AI 검색의 주요 응용 시나리오는 **구체적인 문제의 즉각적인 질문 및 답변**입니다. 예: "XX 회사의 창립자는 누구인가", "xx 브랜드의 xx 제품은 어디서 구매할 수 있는가". 사용자는 **하나의 답변**을 원합니다. wiseflow의 주요 응용 시나리오는 **특정 측면의 정보 지속적 수집**입니다. 예: XX 회사의 관련 정보 추적, XX 브랜드의 시장 행동 지속 추적 등. 이러한 시나리오에서 사용자는 관심사 (특정 회사, 특정 브랜드) 및 신뢰할 수 있는 소스 (사이트 URL 등)를 제공할 수 있지만, 구체적인 검색 질문을 제시할 수 없습니다. 사용자는 **일련의 관련 정보**를 원합니다.                                  |
| **지식 베이스 (RAG) 프로젝트** | 지식 베이스 (RAG) 프로젝트는 일반적으로 기존 정보를 기반으로 한 하류 작업을 기반으로 하며, 일반적으로 개인 지식 (예: 기업 내 운영 매뉴얼, 제품 매뉴얼, 정부 부서의 문서 등)을 대상으로 합니다. wiseflow는 현재 하류 작업을 통합하지 않으며, 인터넷상의 공개 정보를 대상으로 합니다. "에이전트"의 관점에서 볼 때, 둘은 서로 다른 목적으로 구축된 에이전트입니다. RAG 프로젝트는 "내부 지식 보조 에이전트"이며, wiseflow는 "외부 정보 수집 에이전트"입니다.                                                                                                      |

**wiseflow 0.4.x 버전은 다운스트림 작업의 통합에 초점을 맞추고, LLM 기반의 경량 지식 그래프를 도입하여 사용자가 infos에서 통찰력을 얻을 수 있도록 돕습니다.**

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

Wiseflow 0.3.x는 데이터베이스로 pocketbase를 사용합니다. pocketbase 클라이언트를 수동으로 다운로드할 수도 있습니다(버전 0.23.4를 다운로드하여 [pb](./pb) 디렉토리에 배치하는 것을 잊지 마세요). 그리고 수퍼유저를 수동으로 생성할 수 있습니다(.env 파일에 저장하는 것을 잊지 마세요).

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
PRIMARY_MODEL="Qwen/Qwen2.5-32B-Instruct"
SECONDARY_MODEL="Qwen/Qwen2.5-14B-Instruct"
VL_MODEL="OpenGVLab/InternVL2-26B"
```
      
😄 원하신다면 제 [siliconflow 추천 링크](https://cloud.siliconflow.cn?referrer=clx6wrtca00045766ahvexw92)를 사용하실 수 있습니다. 이를 통해 제가 더 많은 토큰 보상을 받을 수 있습니다 🌹

#### 추천 2: OpenAI, Claude, Gemini와 같은 폐쇄형 상용 모델에는 AiHubMix 프록시 사용

정보 소스가 대부분 비한국어 페이지이고 추출된 정보가 한국어일 필요가 없다면, OpenAI, Claude, Gemini와 같은 폐쇄형 상용 모델을 사용하는 것이 좋습니다. 서드파티 프록시인 **AiHubMix**를 시도해볼 수 있습니다. 하나의 API로 OpenAI, Claude, Google, Llama 등 주요 AI 모델에 원활하게 접근할 수 있습니다.

AiHubMix 모델을 사용할 때 .env 구성은 다음을 참조할 수 있습니다:

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://aihubmix.com/v1" # refer https://doc.aihubmix.com/
PRIMARY_MODEL="gpt-4o"
SECONDARY_MODEL="gpt-4o-mini"
VL_MODEL="gpt-4o"
```

😄 Welcome to register using the [AiHubMix referral link](https://aihubmix.com?aff=Gp54) 🌹

#### 로컬 대규모 언어 모델 서비스 배포

Xinference를 예로 들면, .env 구성은 다음을 참조할 수 있습니다:

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

여기서 pocketbase 데이터베이스의 슈퍼유저 사용자 이름과 비밀번호를 설정합니다. |로 구분하는 것을 잊지 마세요 (install_pocketbase.sh 스크립트가 성공적으로 실행되었다면 이미 존재할 것입니다)

#### 3.3 智谱（bigmodel）플랫폼 키 설정（검색 엔진 서비스에 사용）

```
ZHIPU_API_KEY=Your_API_KEY
```

（신청 주소：https://bigmodel.cn/ 현재 무료로 제공 중입니다）


#### 3.4 기타 선택적 구성

다음은 모두 선택적 구성입니다:
- #VERBOSE="true" 

  관찰 모드를 활성화할지 여부. 활성화되면 디버그 정보가 로거 파일에 기록됩니다(기본적으로 콘솔에만 출력);

- #PROJECT_DIR="work_dir" 

    프로젝트 런타임 데이터 디렉토리. 구성하지 않으면 기본값은 `core/work_dir`입니다. 참고: 현재 전체 core 디렉토리가 컨테이너에 마운트되어 있어 직접 접근할 수 있습니다.

- #PB_API_BASE="" 

  pocketbase가 기본 IP 또는 포트에서 실행되지 않는 경우에만 구성이 필요합니다. 기본 상황에서는 이를 무시할 수 있습니다.
  
- #LLM_CONCURRENT_NUMBER=8 

  llm 동시 요청 수를 제어하는 데 사용됩니다. 설정하지 않으면 기본값은 1입니다(활성화하기 전에 llm 제공자가 설정된 동시성을 지원하는지 확인하세요. 로컬 대규모 모델은 하드웨어 기반에 자신이 있지 않는 한 신중하게 사용하세요)

### 4. 프로그램 실행

✋ V0.3.5 버전의 아키텍처와 종속성은 이전 버전과 크게 다릅니다. 코드를 다시 가져오고, pb_data를 삭제(또는 재구축)하도록 하세요

가상 환경을 구축하기 위해 conda를 사용하는 것을 권장합니다(물론 이 단계를 건너뛰거나 다른 Python 가상 환경 솔루션을 사용할 수 있습니다)

```bash
conda create -n wiseflow python=3.10
conda activate wiseflow
```

그런 다음

```bash
cd wiseflow
cd core
pip install -r requirements.txt
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


## 📚 wiseflow가 크롤링한 데이터를 귀하의 프로그램에서 사용하는 방법

1. [dashbord](dashboard) 부분 소스 코드를 참조하여 2차 개발을 수행하세요.

wiseflow의 core 부분은 dashboard를 필요로 하지 않으며, 현재 제품은 dashboard를 통합하지 않았습니다. dashboard가 필요한 경우, [V0.2.1 버전](https://github.com/TeamWiseFlow/wiseflow/releases/tag/V0.2.1)을 다운로드하세요.

2. pocketbase에서 직접 데이터를 가져오세요.

wiseflow가 크롤링한 모든 데이터는 즉시 pocketbase에 저장되므로, pocketbase 데이터베이스를 직접 조작하여 데이터를 가져올 수 있습니다.

PocketBase는 인기 있는 경량 데이터베이스로, 현재 Go/Javascript/Python 등 언어의 SDK를 제공합니다.
   - Go : https://pocketbase.io/docs/go-overview/
   - Javascript : https://pocketbase.io/docs/js-overview/
   - python : https://github.com/vaphes/pocketbase

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