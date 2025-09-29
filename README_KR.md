# AI 최고 정보 책임자 (Wiseflow)

**[简体中文](README.md) | [English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/TeamWiseFlow/wiseflow)

🚀 **대규모 언어 모델을 사용하여 매일 방대한 정보와 다양한 소스에서 당신이 진정으로 관심 있는 정보를 발굴하세요!**

우리에게 부족한 것은 정보가 아니라, 방대한 정보에서 노이즈를 필터링하여 가치 있는 정보를 끌어내는 능력입니다.

https://github.com/user-attachments/assets/48998353-6c6c-4f8f-acae-dc5c45e2e0e6


## 🔥🔥🔥 Wiseflow 4.2 버전 정식 출시!

버전 4.2는 버전 4.0과 4.1을 기반으로 웹 크롤링 기능을 크게 강화하였습니다. 프로그램이 이제 당신의 로컬 "진짜" Chrome 브라우저를 직접 호출하여 가져오기를 할 수 있습니다. 이는 대상 사이트에 의한 "위험 제어" 확률을 최대한 줄이는 것은 물론, 영구적인 사용자 데이터와 페이지 조작 스크립트 지원과 같은 새로운 기능도 가져다줍니다! (예를 들어, 일부 웹사이트에서는 사용자 로그인 후에 전체 콘텐츠를 표시하기 때문에, 이제 미리 로그인하고 wiseflow를 사용하여 완전한 콘텐츠를 얻을 수 있습니다).

버전 4.2는 로컬 Chrome 브라우저를 직접 사용하기 때문에 배포 시 `python -m playwright install --with-deps chromium`을 실행할 필요가 없어졌지만, **기본 설치 경로로 Google Chrome 브라우저를 설치해야 합니다**.

또한 검색 엔진 솔루션을 리팩토링하고 완전한 프록시 솔루션도 제공했습니다. 자세한 내용은 **[CHANGELOG](CHANGELOG.md)**를 참조하세요.

### 🔍 사용자 정의 검색 소스

4.1 버전은 포커스 포인트에 대한 검색 소스를 정밀하게 구성하는 것을 지원합니다. 현재 bing, github, arxiv 검색 소스를 지원하며, 모두 플랫폼 네이티브 인터페이스를 사용하므로 추가적인 타사 서비스 신청이 필요 없습니다.

<img src="docs/select_search_source.gif" alt="search_source" width="360">


### 🧠 AI가 당신의 입장에서 생각하게 하세요!

4.1 버전은 포커스 포인트에 역할과 목적을 설정하여 LLM이 특정 관점이나 목적으로 정보를 분석하고 추출하도록 안내하는 것을 지원합니다. 하지만 사용 시 다음 사항에 유의하십시오:

    - 포커스 포인트 자체가 매우 구체적인 경우, 역할과 목적 설정이 결과에 미치는 영향은 크지 않습니다.
    - 최종 결과의 품질에 가장 큰 영향을 미치는 요소는 항상 정보 소스입니다. 포커스 포인트와 매우 관련성이 높은 소스를 제공해야 합니다.

역할과 목적 설정이 추출 결과에 미치는 영향에 대한 테스트 사례는 [task1](test/reports/report_v4x_llm/task1)을 참조하십시오.


### ⚙️ 사용자 정의 추출 모드

이제 pb 인터페이스에서 자신만의 양식을 만들고 특정 포커스 포인트에 구성할 수 있습니다. LLM은 양식 필드에 따라 정확하게 정보를 추출합니다.


### 👥 소셜 미디어 소스를 위한 크리에이터 검색 모드

이제 포커스 포인트를 기반으로 소셜 미디어 플랫폼에서 관련 콘텐츠를 찾고, 콘텐츠 크리에이터의 홈페이지 정보를 추가로 찾도록 프로그램을 지정할 수 있습니다. "사용자 정의 추출 모드"와 결합하여 wiseflow는 전체 네트워크에서 잠재 고객, 파트너 또는 투자자의 연락처 정보를 검색하는 데 도움을 줄 수 있습니다.

<img src="docs/find_person_by_wiseflow.png" alt="find_person_by_wiseflow" width="720">


**4.1 버전에 대한 자세한 업데이트 정보는 [CHANGELOG](CHANGELOG.md)를 참조하십시오.**

## 🌹 최적의 LLM 조합 가이드

"LLM 시대에 우수한 개발자는 적어도 시간의 60%를 적절한 LLM 모델 선택에 사용해야 합니다" ☺️

우리는 실제 프로젝트에서 7개의 테스트 샘플을 선별하고, 출력 가격이 ¥4/M 토큰을 초과하지 않는 주류 모델을 광범위하게 선택하여 상세한 wiseflow 정보 추출 작업 테스트를 수행하여 다음과 같은 사용 권장 사항에 도달했습니다:

    - 성능 우선 시나리오에서는 다음을 추천합니다: ByteDance-Seed/Seed-OSS-36B-Instruct

    - 비용 우선 시나리오에서는 여전히 다음을 추천합니다: Qwen/Qwen3-14B

시각 보조 분석 모델의 경우 여전히 다음을 사용할 수 있습니다: Qwen/Qwen2.5-VL-7B-Instruct (wiseflow 작업은 현재 이에 대한 의존성이 낮습니다)

자세한 테스트 보고서는 [LLM USE TEST](./test/reports/README_EN.md)를 참조하세요

위의 테스트 결과는 wiseflow 정보 추출 작업에서의 모델 성능만을 나타내며 모델의 종합적 능력을 나타내지는 않습니다. Wiseflow 정보 추출 작업은 다른 유형의 작업(계획, 작성 등)과 현저히 다를 수 있습니다. 또한 wiseflow 작업은 많은 모델 사용량을 소모하기 때문에, 특히 다중 소스, 다중 포커스 시나리오에서 비용이 주요 고려 사항 중 하나입니다.

Wiseflow는 모델 서비스 제공업체를 제한하지 않으며, openaiSDK 요청 인터페이스 형식과 호환되는 한 기존 MaaS 서비스나 Ollama와 같은 로컬 배포 모델 서비스를 선택할 수 있습니다.

[Siliconflow](https://www.siliconflow.com/)의 모델 서비스 사용을 권장합니다.

또는 openai 시리즈 모델을 선호하는 경우 'o3-mini'와 'openai/gpt-oss-20b'도 좋은 선택이며, 시각 보조 분석은 gpt-4o-mini와 짝을 이룰 수 있습니다.

💰 현재 wiseflow 애플리케이션 내에서 AiHubMix가 전달하는 OpenAI 시리즈 모델 공식 인터페이스를 공식 가격의 90%로 사용할 수 있습니다.

**주의:** 할인 혜택을 받으려면 aihubmix 브랜치로 전환해야 합니다. 자세한 내용은 [README](https://github.com/TeamWiseFlow/wiseflow/blob/aihubmix/README.md)를 참조하세요

## 🧐 '딥 서치' VS '와이드 서치'

저는 Wiseflow를 "와이드 서치"로 포지셔닝하고 있습니다. 이는 현재 인기 있는 "딥 서치"와 대비되는 것입니다.

구체적으로, "딥 서치"는 특정 질문에 대해 LLM이 자율적으로 검색 경로를 계획하고, 다른 페이지를 지속적으로 탐색하며, 충분한 정보를 수집하여 답변이나 보고서를 생성하는 것입니다. 그러나 때로는 특정 질문 없이 검색하고, 깊은 탐색도 필요하지 않으며, 광범위한 정보 수집(산업 정보 수집, 배경 정보 수집, 고객 정보 수집 등)만 필요한 경우가 있습니다. 이러한 경우에는 폭이 분명히 더 의미가 있습니다. "딥 서치"로도 이 작업을 달성할 수 있지만, 그것은 대포로 모기를 잡는 것과 같아 비효율적이고 비용이 많이 듭니다. Wiseflow는 바로 이러한 "와이드 서치" 시나리오를 위해 특별히 설계된 도구입니다.

## ✋ Wiseflow가 다른 AI 기반 크롤러와 다른 점은?

- 웹 페이지, 소셜 미디어(현재 Weibo와 Kuaishou 플랫폼 지원), RSS 소스, 그리고 Bing, GitHub, arXiv, eBay 등 검색 소스를 포함한 전체 플랫폼 수집 능력
- 독특한 HTML 처리 워크플로우로 관심사에 따라 정보를 자동 추출하고 추가 탐색이 가치 있는 링크를 발견하며, 14b 파라미터의 LLM으로도 잘 작동
- 사용자 친화적(개발자뿐만 아니라), Xpath 등의 수동 설정 불필요, "즉시 사용 가능"
- 지속적인 반복을 통한 높은 안정성과 가용성, 시스템 리소스와 속도의 균형을 고려한 처리 효율성
- 단순한 "크롤러" 이상이 될 것입니다...

<img src="docs/wiseflow4.xscope.png" alt="4.x full scope" width="720">

(4.x 아키텍처 전체 범위. 점선 상자는 미완성된 부분을 나타냅니다. 능력 있는 커뮤니티 개발자들이 참여하여 PR을 제공해주시기를 바랍니다. 모든 기여자에게는 pro 버전 무료 이용권이 제공됩니다!)

## 🌟 빠른 시작

**단 3단계로 시작하세요!**

**Windows 사용자는 사전에 Git Bash 도구를 다운로드하고 bash에서 다음 명령을 실행하세요 [Bash 다운로드 링크](https://git-scm.com/downloads/win)**

**4.2 버전부터 먼저 Google Chrome 브라우저를 설치해야 합니다(기본 설치 경로 사용)**

### 📋 프로젝트 소스 코드 다운로드 및 uv와 pocketbase 설치

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

위 작업으로 uv 설치가 완료됩니다.

다음으로 [pocketbase docs](https://pocketbase.io/docs/) 에서 자신의 운영체제에 맞는 pocketbase 프로그램을 다운로드하여 [.pb](./pb/) 폴더에 위치시키세요.

install_pocketbase.sh(MacOS/Linux용) 또는 install_pocketbase.ps1(Windows용)을 사용하여 설치할 수도 있습니다.

### 📥 env_sample을 참조하여 .env 파일 설정

wiseflow 폴더(프로젝트 루트 디렉토리)에서 env_sample을 참조하여 .env 파일을 생성하고 관련 설정 정보를 입력하세요

4.x 버전에서는 사용자가 .env 파일에 pocketbase 계정 정보를 제공할 필요가 없으며, pocketbase 버전에 대한 제한도 없습니다. 또한 보조 모델 설정도 임시로 제거되었으므로, 사실상 최소 4개의 매개변수만으로 설정을 완료할 수 있습니다:

- LLM_API_KEY="" # LLM 서비스의 키 (모든 OpenAI 형식 API를 제공하는 모델 서비스를 사용할 수 있으며, 로컬에서 ollama를 사용하여 배포하는 경우 설정할 필요가 없음)
- LLM_API_BASE=""
- PRIMARY_MODEL=ByteDance-Seed/Seed-OSS-36B-Instruct # 가격에 민감하고 덜 복잡한 추출 시나리오에서는 Qwen3-14B를 사용할 수 있습니다
- VL_MODEL=Pro/Qwen/Qwen2.5-VL-7B-Instruct # 가지고 있는 것이 좋음

### 🚀 시작!

```bash
cd wiseflow
uv venv # 처음 실행할 때만 필요
source .venv/bin/activate  # Linux/macOS
# 또는 Windows에서:
# .venv\Scripts\activate
uv sync # 처음 실행할 때만 필요
chmod +x run.sh # 처음 실행할 때만 필요
./run.sh  # Linux/macOS
.\run.bat  # Windows
```

자세한 사용 방법은 [docs/manual/manual_ko.md](./docs/manual/manual_ko.md)를 참조하세요

## 📚 Wiseflow로 크롤링한 데이터를 자신의 프로그램에서 사용하는 방법

Wiseflow로 크롤링한 모든 데이터는 즉시 pocketbase에 저장되므로 pocketbase 데이터베이스를 직접 조작하여 데이터를 얻을 수 있습니다.

인기 있는 경량 데이터베이스로서 PocketBase는 현재 Go/Javascript/Python 등의 언어 SDK를 제공하고 있습니다.

다음 repo에서 여러분의 2차 개발 애플리케이션 사례를 공유하고 홍보하는 것을 환영합니다!

- https://github.com/TeamWiseFlow/wiseflow_plus

## 🛡️ 라이선스

4.2 버전부터 오픈소스 라이선스 계약을 업데이트했습니다. 자세한 내용은 [LICENSE](LICENSE)를 확인하세요.

상업적 협력에 대해서는 **Email: zm.zhao@foxmail.com**로 연락해 주세요

## 📬 연락처

질문이나 제안이 있으시면 [issue](https://github.com/TeamWiseFlow/wiseflow/issues)를 통해 메시지를 남겨주세요.

## 🤝 이 프로젝트는 다음과 같은 훌륭한 오픈소스 프로젝트를 기반으로 합니다:

- Crawl4ai(오픈소스 LLM 친화적 웹 크롤러 & 스크래퍼) https://github.com/unclecode/crawl4ai
- MediaCrawler(xhs/dy/wb/ks/bilibili/zhihu 크롤러) https://github.com/NanmiCoder/MediaCrawler
- Patchright(Undetected Python version of the Playwright testing and automation library) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- NoDriver(웹 자동화, 웹 스크래핑, 봇 및 기타 창의적인 아이디어를 위한 빠른 프레임워크 제공) https://github.com/ultrafunkamsterdam/nodriver
- Pocketbase(1개의 파일로 된 오픈소스 실시간 백엔드) https://github.com/pocketbase/pocketbase
- Feedparser(Python에서 피드 파싱) https://github.com/kurtmckee/feedparser
- SearXNG(다양한 검색 서비스와 데이터베이스에서 결과를 집계하는 무료 인터넷 메타검색 엔진) https://github.com/searxng/searxng

## 인용

관련 작업에서 이 프로젝트의 일부 또는 전체를 참조하거나 인용하는 경우 다음 정보를 기재해 주세요:

```
저자: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## 우호 링크

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)