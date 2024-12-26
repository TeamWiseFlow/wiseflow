# 수석 정보 책임자 (Wiseflow)

**[English](README_EN.md) | [日本語](README_JP.md) | [简体中文](README.md)**

🚀 **수석 정보 책임자** (Wiseflow)는 대규모 언어 모델의 사고 및 분석 능력을 활용하여 다양한 정보원에서 특정 정보를 정확하게 추출할 수 있는 민첩한 정보 마이닝 도구입니다. 전체 과정에서 인간의 개입이 필요하지 않습니다.

**우리가 부족한 것은 정보가 아니라, 방대한 정보 속에서 노이즈를 필터링하여 가치 있는 정보를 드러내는 것입니다.**

🌱 수석 정보 책임자가 어떻게 시간을 절약하고, 관련 없는 정보를 필터링하며, 관심 사항을 정리하는지 살펴보세요! 🌱

https://github.com/user-attachments/assets/fc328977-2366-4271-9909-a89d9e34a07b

## 🔥 테스트 스크립트 및 테스트 보고서 발표

siliconflow에서 제공하는 deepseekV2.5, Qwen2.5-32B-Instruct, Qwen2.5-14B-Instruct, Qwen2.5-coder-7B-Instruct 모델의 성능을 4개의 실제 사례 작업과 총 10개의 실제 웹페이지 샘플에서 수평적으로 테스트하고 비교했습니다.
테스트 결과는 [report](./test/reports/wiseflow_report_20241223_bigbrother666/README.md)를 참조하세요.

또한 테스트 스크립트도 오픈소스로 공개했으니, 더 많은 테스트 결과를 적극적으로 제출해 주시기 바랍니다. wiseflow는 오픈소스 프로젝트이며, 모두의 공동 기여를 통해 "누구나 사용할 수 있는 정보 수집 도구"를 만들고자 합니다!

자세한 내용은 [test/README_EN.md](./test/README_EN.md)를 참조하세요.

현 단계에서는 **테스트 결과 제출이 프로젝트 코드 제출과 동일하게 취급**되며, contributor로 인정받을 수 있고, 심지어 상업화 프로젝트에 초대될 수도 있습니다!

또한 pocketbase의 다운로드 및 사용자 이름/비밀번호 구성 방안을 개선했으며, @ourines가 기여한 install_pocketbase.sh 스크립트에 감사드립니다.

(docker 실행 방안은 일시적으로 제거되었습니다. 사용하기에 그다지 편리하지 않다고 느껴져서...)

🌟 **V0.3.6 버전 예고**

V0.3.6 버전은 2024년 12월 30일 이전에 출시될 예정이며, 이 버전은 v0.3.5의 성능 최적화 버전입니다. 정보 추출 품질이 크게 향상될 것이며, 시각적 대형 모델도 도입하여 웹페이지 정보가 부족할 때 페이지 이미지 정보를 보완 자료로 추출할 예정입니다.

**V0.3.x 계획**

- 위챗 공중 계정 wxbot 없이 구독 지원 시도 (V0.3.7)
- RSS 정보 소스 지원 도입 (V0.3.8)
- LLM 기반의 경량 지식 그래프 도입 시도, 사용자가 infos에서 통찰력을 구축하도록 지원 (V0.3.9)

V0.3.5 버전부터 wiseflow는 완전히 새로운 아키텍처를 사용하며, [Crawlee](https://github.com/apify/crawlee-python)를 기본 크롤러 및 작업 관리 프레임워크로 도입하여 페이지 획득 능력을 크게 향상시켰습니다. 앞으로도 wiseflow의 페이지 획득 능력을 지속적으로 향상시킬 예정이며, 잘 획득되지 않는 페이지가 있다면 [issue #136](https://github.com/TeamWiseFlow/wiseflow/issues/136)에서 피드백을 주시기 바랍니다.

## ✋ wiseflow는 전통적인 크롤러 도구, AI 검색, 지식 베이스(RAG) 프로젝트와 어떻게 다를까요?

wiseflow는 2024년 6월 말 V0.3.0 버전 출시 이후 오픈소스 커뮤니티의 광범위한 관심을 받았으며, 심지어 많은 자체 미디어의 자발적인 보도까지 이끌어냈습니다. 이에 먼저 감사의 말씀을 전합니다!

그러나 우리는 일부 관심 있는 분들이 wiseflow의 기능 위치에 대해 일부 이해 오류가 있음을 알게 되었습니다. 아래 표는 전통적인 크롤러 도구, AI 검색, 지식 베이스(RAG) 프로젝트와의 비교를 통해 wiseflow 제품의 최신 위치에 대한 우리의 생각을 나타냅니다.

|          | **수석 정보 책임자 (Wiseflow)**와의 비교 설명 | 
|-------------|-----------------|
| **크롤러 도구** | 먼저 wiseflow는 크롤러 도구 기반 프로젝트입니다 (현재 버전 기준으로, 우리는 크롤러 프레임워크 Crawlee를 기반으로 합니다). 그러나 전통적인 크롤러 도구는 정보 추출 측면에서 인간의 개입이 필요하며, 명확한 Xpath 등을 제공해야 합니다. 이는 일반 사용자를 막을 뿐만 아니라 일반성이 전혀 없으며, 다른 웹사이트 (기존 웹사이트 업그레이드 포함)에 대해서는 인간이 다시 분석을 수행하고 추출 코드를 업데이트해야 합니다. wiseflow는 LLM을 사용하여 웹페이지의 자동 분석 및 추출 작업을 추구하며, 사용자는 프로그램에 그의 관심사만 알려주면 됩니다. 이 관점에서 wiseflow를 "자동으로 크롤러 도구를 사용할 수 있는 AI 에이전트"로 간단히 이해할 수 있습니다. |
| **AI 검색** | AI 검색의 주요 응용 시나리오는 **구체적인 문제의 즉각적인 질문 및 답변**입니다. 예: "XX 회사의 창립자는 누구인가", "xx 브랜드의 xx 제품은 어디서 구매할 수 있는가". 사용자는 **하나의 답변**을 원합니다. wiseflow의 주요 응용 시나리오는 **특정 측면의 정보 지속적 수집**입니다. 예: XX 회사의 관련 정보 추적, XX 브랜드의 시장 행동 지속 추적 등. 이러한 시나리오에서 사용자는 관심사 (특정 회사, 특정 브랜드) 및 신뢰할 수 있는 소스 (사이트 URL 등)를 제공할 수 있지만, 구체적인 검색 질문을 제시할 수 없습니다. 사용자는 **일련의 관련 정보**를 원합니다. |
| **지식 베이스 (RAG) 프로젝트** | 지식 베이스 (RAG) 프로젝트는 일반적으로 기존 정보를 기반으로 한 하류 작업을 기반으로 하며, 일반적으로 개인 지식 (예: 기업 내 운영 매뉴얼, 제품 매뉴얼, 정부 부서의 문서 등)을 대상으로 합니다. wiseflow는 현재 하류 작업을 통합하지 않으며, 인터넷상의 공개 정보를 대상으로 합니다. "에이전트"의 관점에서 볼 때, 둘은 서로 다른 목적으로 구축된 에이전트입니다. RAG 프로젝트는 "내부 지식 보조 에이전트"이며, wiseflow는 "외부 정보 수집 에이전트"입니다. |

## 📥 설치 및 사용

### 1. 코드 저장소 복제

🌹 좋아요, fork는 좋은 습관입니다 🌹

**windows 사용자는 먼저 git bash 도구를 다운로드해야 합니다** [링크](https://git-scm.com/downloads/win)

```bash
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

### 2. 루트 디렉토리에서 install_pocketbase.sh 스크립트 실행

이 스크립트는 pocketbase(버전 0.23.4)의 다운로드 및 구성을 안내하고 core 디렉토리 아래에 .env 파일을 생성합니다.

```bash
chmod +x install_pocketbase.sh
./install_pocketbase.sh
```

Wiseflow 0.3.x는 데이터베이스로 pocketbase를 사용합니다. pocketbase 클라이언트를 수동으로 다운로드할 수도 있습니다(버전 0.23.4를 다운로드하여 [pb](./pb) 디렉토리에 배치하는 것을 잊지 마세요). 그리고 수퍼유저를 수동으로 생성할 수 있습니다(.env 파일에 저장하는 것을 잊지 마세요).

자세한 내용은 [pb/README.md](/pb/README.md)를 참조하세요.

### 3. core/.env 파일 구성 계속하기

🌟 **이전 버전과 다릅니다** - V0.3.5부터 .env 파일은 [core](./core) 폴더에 위치해야 합니다.

#### 3.1 대규모 언어 모델 구성

Wiseflow는 LLM 네이티브 애플리케이션이므로 프로그램에 안정적인 LLM 서비스를 제공하도록 해주세요.

🌟 **Wiseflow는 모델 서비스의 출처를 제한하지 않습니다 - ollama, Xinference 등 로컬에 배포된 서비스를 포함하여 openAI SDK와 호환되는 서비스라면 모두 사용할 수 있습니다**

#### 추천 1: Siliconflow가 제공하는 MaaS 서비스 사용

Siliconflow는 대부분의 주류 오픈소스 모델에 대한 온라인 MaaS 서비스를 제공합니다. 축적된 추론 가속화 기술로 속도와 가격 모두에서 큰 장점이 있습니다. siliconflow의 서비스를 사용할 때 .env 구성은 다음을 참조할 수 있습니다:

```bash
export LLM_API_KEY=Your_API_KEY
export LLM_API_BASE="https://api.siliconflow.cn/v1"
export PRIMARY_MODEL="Qwen/Qwen2.5-32B-Instruct"
export SECONDARY_MODEL="Qwen/Qwen2.5-7B-Instruct"
export VL_MODEL="OpenGVLab/InternVL2-26B"
```
      
😄 원하신다면 제 [siliconflow 추천 링크](https://cloud.siliconflow.cn?referrer=clx6wrtca00045766ahvexw92)를 사용하실 수 있습니다. 이를 통해 제가 더 많은 토큰 보상을 받을 수 있습니다 🌹

#### 추천 2: OpenAI, Claude, Gemini와 같은 폐쇄형 상용 모델에는 AiHubMix 프록시 사용

정보 소스가 대부분 비한국어 페이지이고 추출된 정보가 한국어일 필요가 없다면, OpenAI, Claude, Gemini와 같은 폐쇄형 상용 모델을 사용하는 것이 좋습니다. 서드파티 프록시인 **AiHubMix**를 시도해볼 수 있습니다. 하나의 API로 OpenAI, Claude, Google, Llama 등 주요 AI 모델에 원활하게 접근할 수 있습니다.

AiHubMix 모델을 사용할 때 .env 구성은 다음을 참조할 수 있습니다:

```bash
export LLM_API_KEY=Your_API_KEY
export LLM_API_BASE="https://aihubmix.com/v1" # refer https://doc.aihubmix.com/
export PRIMARY_MODEL="gpt-4o"
export SECONDARY_MODEL="gpt-4o-mini"
export VL_MODEL="gpt-4o"
```

😄 Welcome to register using the [AiHubMix referral link](https://aihubmix.com?aff=Gp54) 🌹

#### 로컬 대규모 언어 모델 서비스 배포

Xinference를 예로 들면, .env 구성은 다음을 참조할 수 있습니다:

```bash
# LLM_API_KEY='' no need for local service, please comment out or delete
export LLM_API_BASE='http://127.0.0.1:9997'
export PRIMARY_MODEL=launched_model_id
export SECONDARY_MODEL=launched_model_id
export VL_MODEL=launched_model_id
```

#### 3.2 Pocketbase Account and Password Configuration

```bash
export PB_API_AUTH="test@example.com|1234567890" 
```

여기서 pocketbase 데이터베이스의 슈퍼유저 사용자 이름과 비밀번호를 설정합니다. |로 구분하는 것을 잊지 마세요 (install_pocketbase.sh 스크립트가 성공적으로 실행되었다면 이미 존재할 것입니다)

#### 3.3 기타 선택적 구성

다음은 모두 선택적 구성입니다:
- #VERBOSE="true" 

  관찰 모드를 활성화할지 여부. 활성화되면 디버그 정보가 로거 파일에 기록됩니다(기본적으로 콘솔에만 출력);

- #PROJECT_DIR="work_dir" 

    프로젝트 런타임 데이터 디렉토리. 구성하지 않으면 기본값은 `core/work_dir`입니다. 참고: 현재 전체 core 디렉토리가 컨테이너에 마운트되어 있어 직접 접근할 수 있습니다.

- #PB_API_BASE="" 

  pocketbase가 기본 IP 또는 포트에서 실행되지 않는 경우에만 구성이 필요합니다. 기본 상황에서는 이를 무시할 수 있습니다.

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
chmod +x run.sh
./run_task.sh # if you just want to scan sites one-time (no loop), use ./run.sh
```

🌟 이 스크립트는 pocketbase가 이미 실행 중인지 자동으로 확인합니다. 실행 중이 아닌 경우 자동으로 시작됩니다. 단, ctrl+c 또는 ctrl+z로 프로세스를 종료할 때 터미널을 닫을 때까지 pocketbase 프로세스는 종료되지 않는다는 점에 유의하세요.

run_task.sh는 주기적으로 크롤링-추출 작업을 실행합니다(시작 시 즉시 실행되고 그 후 매시간마다 실행됨). 한 번만 실행하면 되는 경우 run.sh 스크립트를 사용할 수 있습니다.

### 5. **관심사 및 정기 스캔 정보 소스 추가**

프로그램을 시작한 후, pocketbase Admin dashboard UI (http://127.0.0.1:8090/_/)를 여세요.

#### 5.1 focus_point 폼 열기

이 폼을 통해 귀하의 관심사를 지정할 수 있으며, LLM은 이를 기반으로 정보를 추출, 필터링 및 분류합니다.

필드 설명:
- focuspoint, 관심사 설명 (필수), 예: "상하이 초등학교 졸업 정보", "암호화폐 가격"
- explanation, 관심사의 상세 설명 또는 구체적인 약속, 예: "상하이 공식 발표 중학교 입학 정보만 포함", "BTC, ETH의 현재 가격, 등락률 데이터" 등
- activated, 활성화 여부. 비활성화되면 해당 관심사는 무시되며, 비활성화 후 다시 활성화할 수 있습니다.

주의: focus_point 업데이트 설정 (activated 조정 포함) 후, **프로그램을 다시 시작해야 적용됩니다.**

#### 5.2 sites 폼 열기

이 폼을 통해 사용자 정의 정보 소스를 지정할 수 있으며, 시스템은 백그라운드 정기 작업을 시작하여 로컬에서 정보 소스를 스캔, 구문 분석 및 분석합니다.

sites 필드 설명:
- url, 정보 소스의 URL, 정보 소스는 구체적인 기사 페이지를 제공할 필요가 없으며, 기사 목록 페이지만 제공하면 됩니다.
- per_hours, 스캔 빈도, 단위는 시간, 정수 형식 (1~24 범위, 스캔 빈도를 하루에 한 번 이상으로 설정하지 않는 것을 권장합니다. 즉, 24로 설정).
- activated, 활성화 여부. 비활성화되면 해당 정보 소스는 무시되며, 비활성화 후 다시 활성화할 수 있습니다.

**sites 설정 조정은 프로그램을 다시 시작할 필요가 없습니다.**

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

- crawlee-python (Python용 웹 스크래핑 및 브라우저 자동화 라이브러리로, 신뢰할 수 있는 크롤러를 구축합니다. BeautifulSoup, Playwright 및 원시 HTTP와 함께 작동합니다. headful 및 headless 모드 모두 지원. 프록시 회전 기능 포함.) https://github.com/apify/crawlee-python
- json_repair (유효하지 않은 JSON 문서 복구) https://github.com/josdejong/jsonrepair/tree/main 
- python-pocketbase (pocketBase 클라이언트 SDK for python) https://github.com/vaphes/pocketbase
- SeeAct (모든 주어진 웹사이트에서 자율적으로 작업을 수행하는 일반 웹 에이전트 시스템, 특히 GPT-4Vision과 같은 대형 멀티모달 모델 (LMMs)에 중점을 둡니다.) https://github.com/OSU-NLP-Group/SeeAct

또한 [GNE](https://github.com/GeneralNewsExtractor/GeneralNewsExtractor), [AutoCrawler](https://github.com/kingname/AutoCrawler)에서 영감을 받았습니다.

## Citation

이 프로젝트의 일부 또는 전체를 관련 작업에서 참조하거나 인용하는 경우, 다음 정보를 명시하세요:

```
Author: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```