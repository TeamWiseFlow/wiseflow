# 수석 정보 책임자 (Wiseflow)

**[English](README_EN.md) | [日本語](README_JP.md) | [简体中文](README.md)**

🚀 **수석 정보 책임자** (Wiseflow)는 대규모 언어 모델의 사고 및 분석 능력을 활용하여 다양한 정보원에서 특정 정보를 정확하게 추출할 수 있는 민첩한 정보 마이닝 도구입니다. 전체 과정에서 인간의 개입이 필요하지 않습니다.

**우리가 부족한 것은 정보가 아니라, 방대한 정보 속에서 노이즈를 필터링하여 가치 있는 정보를 드러내는 것입니다.**

🌱 수석 정보 책임자가 어떻게 시간을 절약하고, 관련 없는 정보를 필터링하며, 관심 사항을 정리하는지 살펴보세요! 🌱

https://github.com/user-attachments/assets/fc328977-2366-4271-9909-a89d9e34a07b

## 🔥 늦었지만 도착했습니다, V0.3.6가 출시되었습니다

V0.3.6은 V0.3.5의 개선 버전으로, 많은 커뮤니티 피드백을 반영하여 업그레이드를 권장드립니다.

  - Crawl4ai를 기본 크롤링 프레임워크로 변경하였습니다. 사실 Crawl4ai와 Crawlee는 Playwright 기반이며 얻는 결과가 비슷하지만, Crawl4ai의 html2markdown 기능이 매우 유용하며 이는 llm 정보 추출에 큰 도움이 됩니다. 또한 Crawl4ai의 아키텍처가 저의 생각과 더 잘 맞습니다.
  - Crawl4ai의 html2markdown 기능을 바탕으로 deep scraper를 추가하여 페이지의 독립 링크와 본문을 구분함으로써 llm의 정확한 추출을 용이하게 하였습니다. html2markdown과 deep scraper가 원본 웹 페이지 데이터를 잘 정리하여 llm이 받는 간섭과 오도를 크게 줄이고 최종 결과의 품질을 보장하며 불필요한 token 소비도 줄였습니다.

     *리스트 페이지와 문서 페이지의 구분은 모든 크롤링 프로젝트에서 어려운 문제입니다. 특히 현대 웹 페이지는 종종 문서 페이지의 사이드바와 하단에 많은 추천 읽기 항목을 추가하여 두 가지가 텍스트 통계적 특징 차이 없이 혼동됩니다.*
     *이 부분에서는 시각 대형 모델을 사용하여 레이아웃 분석을 고려했으나, 간섭받지 않는 웹 페이지 스크린샷을 얻는 것이 프로그램 복잡성을 크게 증가시키고 처리 효율성을 낮추는 것으로 나타났습니다.*

  - 추출 전략과 llm의 prompt를 재구성하였습니다.

    *좋은 prompt는 명확한 작업 지침이며 각 단계가 충분히 명확해야 실수를 하기 어렵습니다. 하지만 너무 복잡한 prompt의 가치는 평가하기 어렵습니다. 더 나은 방법이 있으시다면 PR을 환영합니다.*

  - 시각 대형 모델을 도입하여 Crawl4ai가 높은 가중치(현재 Crawl4ai가 평가)를 부여한 이미지를 자동으로 인식하고 관련 정보를 페이지 텍스트에 추가합니다.
  - requirement.txt 의 의존성 항목을 계속 줄였으며, 이제 json_repair가 필요하지 않습니다. (실제로 llm이 JSON 형식으로 생성하는 것은 처리 시간을 증가시키고 실패율을 높이므로 더 간단한 방식을 채택하고 처리 결과 후처리를 강화하였습니다.)
  - pb info 양식 구조를 약간 조정하여 web_title과 reference 항목을 추가했습니다.
  - @ourines 님이 install_pocketbase.sh 스크립트를 기여하셨습니다. (Docker 실행 방안은 일시적으로 제거되었으며 사용이 편리하지 않아서……)
  - @ibaoger 님이 install_pocketbase.ps1 스크립트를 기여하셨습니다.
  - @tusik 님이 비동기 llm wrapper를 기여하셨습니다.
**V0.3.6 버전으로 업그레이드하려면 pocketbase 데이터베이스를 다시 구성해야 합니다. pb/pb_data 폴더를 삭제한 후 다시 실행해 주세요.**

**V0.3.6 버전에서는 .env에서 SECONDARY_MODEL을 VL_MODEL로 변경해야 합니다. 최신 [env_sample](./env_sample)을 참고해 주세요.**
  
### V0.3.6 테스트 보고서

siliconflow의 deepseekV2.5, Qwen2.5-32B-Instruct, Qwen2.5-14B-Instruct, Qwen2.5-72B-Instruct 모델의 성능을 네 가지 실제 사례 및 여섯 개의 실제 웹 페이지 샘플에서 횡断적으로 테스트하고 비교하였습니다.
테스트 결과는 [report](./test/reports/wiseflow_report_v036_bigbrother666/README.md)를 참조해 주세요.

또한 테스트 스크립트도 오픈소스로 제공되며 더 많은 테스트 결과를 제출해 주시길 바랍니다. wiseflow는 오픈소스 프로젝트로서 모두의 공헌으로 "누구나 사용할 수 있는 정보 수집 도구"를 만들고자 합니다!

참고: [test/README.md](./test/README.md)

현재, **테스트 결과 제출은 프로젝트 코드 제출과 동일하며** 기여자로 인정되며 상업 프로젝트 참여 초청까지 받을 수도 있습니다!


🌟**V0.3.x 계획**

- WeChat 공개 계정 wxbot 없이 구독 지원 (V0.3.7);
- RSS 정보 소스 및 검색 엔진 지원 도입 (V0.3.8);
- 일부 사회적 플랫폼 지원 시도 (V0.3.9).

이 세 가지 버전 동안 deep scraper 및 llm 추출 전략을 지속적으로 개선할 예정입니다. 또한 적용 장면과 추출 효과가 이상적인 정보 원본 주소를 지속적으로 피드백해 주시길 바랍니다. [issue #136](https://github.com/TeamWiseFlow/wiseflow/issues/136)에서 피드백을 남겨주세요.


## ✋ wiseflow는 전통적인 크롤러 도구, AI 검색, 지식 베이스(RAG) 프로젝트와 어떻게 다를까요?

wiseflow는 2024년 6월 말 V0.3.0 버전 출시 이후 오픈소스 커뮤니티의 광범위한 관심을 받았으며, 심지어 많은 자체 미디어의 자발적인 보도까지 이끌어냈습니다. 이에 먼저 감사의 말씀을 전합니다!

그러나 우리는 일부 관심 있는 분들이 wiseflow의 기능 위치에 대해 일부 이해 오류가 있음을 알게 되었습니다. 아래 표는 전통적인 크롤러 도구, AI 검색, 지식 베이스(RAG) 프로젝트와의 비교를 통해 wiseflow 제품의 최신 위치에 대한 우리의 생각을 나타냅니다.

|          | **수석 정보 책임자 (Wiseflow)**와의 비교 설명                                                                                                                                                                                                                                                                                                                                                      | 
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
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

**windows users please execute [install_pocketbase.ps1](./install_pocketbase.ps1) script**

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
export VL_MODEL="gpt-4o"
```

😄 Welcome to register using the [AiHubMix referral link](https://aihubmix.com?aff=Gp54) 🌹

#### 로컬 대규모 언어 모델 서비스 배포

Xinference를 예로 들면, .env 구성은 다음을 참조할 수 있습니다:

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

여기서 pocketbase 데이터베이스의 슈퍼유저 사용자 이름과 비밀번호를 설정합니다. |로 구분하는 것을 잊지 마세요 (install_pocketbase.sh 스크립트가 성공적으로 실행되었다면 이미 존재할 것입니다)

#### 3.3 기타 선택적 구성

다음은 모두 선택적 구성입니다:
- #VERBOSE="true" 

  관찰 모드를 활성화할지 여부. 활성화되면 디버그 정보가 로거 파일에 기록됩니다(기본적으로 콘솔에만 출력);

- #PROJECT_DIR="work_dir" 

    프로젝트 런타임 데이터 디렉토리. 구성하지 않으면 기본값은 `core/work_dir`입니다. 참고: 현재 전체 core 디렉토리가 컨테이너에 마운트되어 있어 직접 접근할 수 있습니다.

- #PB_API_BASE="" 

  pocketbase가 기본 IP 또는 포트에서 실행되지 않는 경우에만 구성이 필요합니다. 기본 상황에서는 이를 무시할 수 있습니다.
  
- #LLM_CONCURRENT_NUMBER=8 

  llm 동시 요청 수를 제어하는 데 사용됩니다. 설정하지 않으면 기본값은 1입니다(활성화하기 전에 llm 제공자가 설정된 동시성을 지원하는지 확인하세요. 로컬 대규모 모델은 하드웨어 기반에 자신이 있지 않는 한 신중하게 사용하세요)
  
  @tusik이 기여한 비동기 llm wrapper에 감사드립니다

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

- crawl4ai（Open-source LLM Friendly Web Crawler & Scraper） https://github.com/unclecode/crawl4ai
- python-pocketbase (pocketBase 클라이언트 SDK for python) https://github.com/vaphes/pocketbase

또한 [GNE](https://github.com/GeneralNewsExtractor/GeneralNewsExtractor), [AutoCrawler](https://github.com/kingname/AutoCrawler), [SeeAct](https://github.com/OSU-NLP-Group/SeeAct) 에서 영감을 받았습니다.

## Citation

이 프로젝트의 일부 또는 전체를 관련 작업에서 참조하거나 인용하는 경우, 다음 정보를 명시하세요:

```
Author: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```