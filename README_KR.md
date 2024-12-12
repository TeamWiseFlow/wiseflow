# 수석 정보 책임자 (Wiseflow)

**[English](README_EN.md) | [日本語](README_JP.md) | [简体中文](README.md)**

🚀 **수석 정보 책임자** (Wiseflow)는 웹사이트, 위챗 공중 계정, 소셜 플랫폼 등 다양한 정보 소스에서 설정된 관심사에 따라 정보를 추출하고, 자동으로 태그를 분류하여 데이터베이스에 업로드하는 민첩한 정보 마이닝 도구입니다.

**우리가 부족한 것은 정보가 아니라, 방대한 정보 속에서 노이즈를 필터링하여 가치 있는 정보를 드러내는 것입니다.**

🌱 수석 정보 책임자가 어떻게 시간을 절약하고, 관련 없는 정보를 필터링하며, 관심 사항을 정리하는지 살펴보세요! 🌱

https://github.com/user-attachments/assets/f6fec29f-2b4b-40f8-8676-8433abb086a7

## 🔥 V0.3.5 버전 소개

커뮤니티 피드백을 충분히 수렴한 후, 우리는 wiseflow의 제품 위치를 재정립하였으며, 새로운 위치는 더욱 집중되어 있습니다. V0.3.5 버전은 이 새로운 위치에 기반한 완전히 새로운 아키텍처 버전입니다.

- [Crawlee](https://github.com/apify/crawlee-python)를 기본 크롤러 및 작업 관리 프레임워크로 도입하여 페이지 획득 능력을 크게 향상시켰습니다. 이전에 획득할 수 없었던 (또는 코드가 깨진) 페이지를 현재는 잘 획득할 수 있습니다. 향후 획득이 잘 되지 않는 페이지가 있다면, [issue #136](https://github.com/TeamWiseFlow/wiseflow/issues/136)에 피드백을 주시기 바랍니다.
- 새로운 제품 위치에 따른 새로운 정보 추출 전략 — "크롤링과 조사 통합"을 도입하였습니다. 기사 상세 추출을 포기하고, 크롤링 과정에서 llm을 사용하여 사용자가 관심 있는 정보(infos)를 직접 추출하며, 추가로 크롤링할 가치가 있는 링크를 자동으로 판단합니다. **당신이 관심 있는 것이 당신이 필요한 것입니다.**
- 최신 버전(v0.23.4)의 Pocketbase에 적합하며, 폼 구성을 업데이트하였습니다. 또한 새로운 아키텍처는 GNE 등의 모듈이 더 이상 필요하지 않으며, requirement 종속 항목이 8개로 줄었습니다.
- 새로운 아키텍처의 배포 방식도 더욱 간편해졌으며, docker 모드는 코드 저장소 핫 업데이트를 지원합니다. 이는 향후 업그레이드 시 docker build를 다시 수행할 필요가 없음을 의미합니다.
- 더 많은 세부 사항은 [CHANGELOG](CHANGELOG.md)를 참조하세요.

🌟 **V0.3.x 향후 계획**

- [SeeAct](https://github.com/OSU-NLP-Group/SeeAct) 방식을 도입하여, 시각 대형 모델을 통해 복잡한 페이지의 작업을 지원합니다. 예를 들어, 스크롤, 클릭 후 정보 표시 등 (V0.3.6).
- 위챗 공중 계정 무료 구독 지원 시도 (V0.3.7).
- RSS 정보 소스 지원 도입 (V0.3.8).
- LLM 기반의 경량 지식 그래프 도입 시도, 사용자가 infos에서 통찰력을 구축하는 데 도움을 줍니다 (V0.3.9).

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

```bash
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

### 2. env_sample 참조하여 .env 파일 구성하고 core 디렉토리에 배치

🌟 **이전 버전과 다릅니다** V0.3.5부터 .env 파일을 core 폴더에 배치해야 합니다.

또한 V0.3.5부터 env 구성이 크게 단순화되었으며, 필수 구성 항목은 세 가지뿐입니다. 구체적인 내용은 다음과 같습니다:

- LLM_API_KEY=""

    대형 모델 서비스 키, 이는 필수입니다.

- LLM_API_BASE="https://api.siliconflow.cn/v1" 

    서비스 인터페이스 주소, openai sdk를 지원하는 모든 서비스 제공자를 사용할 수 있습니다. openai 서비스를 직접 사용하는 경우, 이 항목은 비워둘 수 있습니다.

- PB_API_AUTH="test@example.com|1234567890" 

  pocketbase 데이터베이스의 superuser 사용자 이름 및 비밀번호, |로 구분하세요.

아래는 선택적 구성입니다:
- #VERBOSE="true" 

  관찰 모드 활성화 여부, 활성화하면 debug log 정보가 logger 파일에 기록됩니다 (기본적으로 console에만 출력됨). 또한 playwright 브라우저 창이 열리므로 크롤링 과정을 관찰하기 쉽습니다.

- #PRIMARY_MODEL="Qwen/Qwen2.5-7B-Instruct"

    주 모델 선택, siliconflow 서비스를 사용하는 경우, 이 항목을 비워두면 기본적으로 Qwen2.5-7B-Instruct가 호출됩니다. 실제로 충분히 사용 가능하지만, 저는 **Qwen2.5-14B-Instruct**를 더 추천합니다.

- #SECONDARY_MODEL="THUDM/glm-4-9b-chat" 

    보조 모델 선택, siliconflow 서비스를 사용하는 경우, 이 항목을 비워두면 기본적으로 glm-4-9b-chat가 호출됩니다.

- #PROJECT_DIR="work_dir" 

    프로젝트 실행 데이터 디렉토리, 구성하지 않으면 기본적으로 `core/work_dir`에 저장됩니다. 주의: 현재 전체 core 디렉토리는 container에 마운트되어 있으므로, 여기에 직접 접근할 수 있습니다.

- #PB_API_BASE="" 

  pocketbase가 기본 IP 또는 포트에서 실행되지 않는 경우에만 구성해야 합니다. 기본적으로 무시하면 됩니다.

### 3.1 docker를 사용하여 실행

✋ V0.3.5 버전의 아키텍처 및 종속성은 이전 버전과 크게 다릅니다. 반드시 코드를 다시 가져와 이전 버전 이미지 (pb_data 폴더 포함)를 삭제하고 다시 build하세요!

> ⚠️ 대신 루트 디렉토리의 install_pocketbase.sh 스크립트를 실행하십시오. 이 스크립트는 자동으로 pocketbase를 다운로드하고 구성합니다.
> ```bash
> chmod +x install_pocketbase.sh
> ./install_pocketbase.sh
> ```

```bash
cd wiseflow
docker compose up
```

**주의:**

처음 docker container를 실행할 때 프로그램이 오류를 보고할 수 있습니다. 이는 정상적인 현상입니다. 화면의 프롬프트에 따라 superuser 계정을 생성하세요 (반드시 이메일 주소를 사용하세요). 그런 다음 생성된 사용자 이름과 비밀번호를 .env 파일에 입력하고 container를 다시 시작하세요.

🌟 docker 솔루션은 기본적으로 task.py를 실행하며, 이는 주기적으로 크롤링-추출 작업을 실행합니다 (시작 시 즉시 한 번 실행된 후, 매 시간마다 한 번씩 실행됩니다).

### 3.2 python 환경에서 실행

✋ V0.3.5 버전의 아키텍처 및 종속성은 이전 버전과 크게 다릅니다. 반드시 코드를 다시 가져와 pb_data를 삭제 (또는 재구축)하세요.

conda를 사용하여 가상 환경을 구축하는 것을 추천합니다.

```bash
cd wiseflow
conda create -n wiseflow python=3.10
conda activate wiseflow
cd core
pip install -r requirements.txt
```

그 후 [다운로드](https://pocketbase.io/docs/) 해당 pocketbase 클라이언트를 [/pb](/pb) 디렉토리에 배치하세요. 그리고

```bash
chmod +x run.sh
./run_task.sh # 사이트를 한 번만 스캔하려면 (루프 없이), ./run.sh를 사용하세요
```

이 스크립트는 pocketbase가 이미 실행 중인지 자동으로 판단하며, 실행 중이 아니면 자동으로 시작합니다. 그러나 ctrl+c 또는 ctrl+z로 프로세스를 종료할 때 pocketbase 프로세스는 종료되지 않으며, terminal을 닫을 때까지 계속 실행됩니다.

또한 docker 배포와 마찬가지로, 처음 실행할 때 오류가 발생할 수 있습니다. 화면의 프롬프트에 따라 superuser 계정을 생성하세요 (반드시 이메일 주소를 사용하세요). 그런 다음 생성된 사용자 이름과 비밀번호를 .env 파일에 입력하고 다시 실행하세요.

물론 다른 terminal에서 미리 pocketbase를 실행하고 설정할 수도 있습니다 (이렇게 하면 첫 번째 오류를 방지할 수 있습니다). 구체적인 내용은 [pb/README.md](/pb/README.md)를 참조하세요.

### 4. 모델 추천 [2024-12-09]

모델의 매개변수 수가 많을수록 더 나은 성능을 의미하지만, 실제 테스트를 통해 **Qwen2.5-7b-Instruct 및 glm-4-9b-chat 모델을 사용하면 기본적인 효과를 얻을 수 있음**이 확인되었습니다. 그러나 비용, 속도 및 효과를 종합적으로 고려할 때, 저는 주 모델 **(PRIMARY_MODEL)로 Qwen2.5-14B-Instruct를 더 추천합니다**.

여기에서 siliconflow (규소 흐름)의 MaaS 서비스를 강력히 추천합니다. 여러 주요 오픈소스 모델의 서비스를 제공하며, 대량 서비스를 제공합니다. Qwen2.5-7b-Instruct 및 glm-4-9b-chat는 현재 무료 서비스를 제공합니다. (주 모델로 Qwen2.5-14B-Instruct를 사용하는 경우, 374개의 웹페이지를 크롤링하고 43개의 유효한 info를 추출하여 총 비용은 ￥3.07입니다).

😄 원한다면 제 [siliconflow 초대 링크](https://cloud.siliconflow.cn?referrer=clx6wrtca00045766ahvexw92)를 사용하여 등록할 수 있으며, 이 경우 저도 더 많은 token 보상을 받을 수 있습니다 🌹

**만약 귀하의 정보 소스가 주로 중국어가 아닌 페이지이고, 추출된 info가 중국어일 필요가 없다면, openai 또는 claude와 같은 해외 제조사의 모델을 사용하는 것을 더 추천합니다.**

타사 프록시 **AiHubMix**를 사용하여 단 하나의 API로 OpenAI, Claude, Google, Llama 등과 같은 다양한 주요 AI 모델에 원활하게 액세스할 수 있습니다.

😄 다음 초대 링크 [AiHubMix 초대 링크](https://aihubmix.com?aff=Gp54)를 사용하여 등록하세요 🌹

🌟 **wiseflow 자체는 어떤 모델 서비스에도 제한을 두지 않으며, openAI SDK와 호환되는 서비스라면 모두 사용 가능합니다. 로컬에 배포된 ollama, Xinference 등의 서비스도 포함됩니다.**

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

상업적 및 맞춤형 협력은 **Email: 35252986@qq.com**으로 문의하세요.

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