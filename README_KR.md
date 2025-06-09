# AI 최고 정보 책임자 (Wiseflow)

**[English](README_EN.md) | [日本語](README_JP.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md) | [简体中文](README.md)**

🚀 **대규모 언어 모델을 사용하여 매일 방대한 정보와 다양한 소스에서 당신이 진정으로 관심 있는 정보를 발굴하세요!**

우리에게 부족한 것은 정보가 아니라, 방대한 정보에서 노이즈를 필터링하여 가치 있는 정보를 끌어내는 능력입니다.

## 🔥🔥🔥 Wiseflow 4.0 버전 정식 출시!

https://github.com/user-attachments/assets/2c52c010-6ae7-47f4-bc1c-5880c4bd76f3

(온라인 서비스는 현재 기술적인 이유로 4.0 코어로 전환되지 않았으며, 업그레이드를 가속화하고 있습니다)

3개월의 기다림 끝에 마침내 wiseflow 4.0 버전이 정식 출시되었습니다! 이번 버전은 완전히 새로운 4.x 아키텍처를 도입하여 소셜 미디어 소스 지원과 다양한 새로운 기능을 제공합니다.

4.x는 WIS Crawler(크롤4ai, 미디어크롤러, 노드라이버를 깊이 있게 재구성하여 통합)를 내장하고 있으며, 웹페이지 외에도 소셜 미디어 소스를 지원합니다. 4.0 버전에서는 먼저 웨이보와 쿠아이쇼우 플랫폼을 지원하며, 향후 계획에 따라 추가될 플랫폼은 다음과 같습니다:
웨이신 공식 계정, 샤오홍슈, 틱톡, Bilibili, 지후...

4.x 아키텍처가 가져오는 다른 새로운 기능들:

- 새로운 아키텍처, 비동기와 스레드 풀의 하이브리드 사용으로 처리 효율성 대폭 향상(메모리 소비도 감소)
- Crawl4ai 0.6.3 버전의 디스패처 기능을 상속하여 더 세련된 메모리 관리 제공
- 버전 3.9의 Pre-Process와 Crawl4ai의 Markdown Generation 프로세스를 깊이 통합하여 중복 처리 방지
- RSS 소스 지원 최적화
- 저장소 파일 구조 최적화, 더 명확하고 현대적인 Python 프로젝트 표준 준수
- uv를 사용한 의존성 관리로 전환하고 requirement.txt 파일 최적화
- 시작 스크립트 최적화(Windows 버전 제공), 진정한 "원클릭 시작" 구현
- 설정 및 배포 프로세스 최적화, 백엔드 프로그램이 pocketbase 서비스에 의존하지 않게 되어 .env에서 pocketbase 자격 증명을 제공할 필요가 없으며 pocketbase 버전 제한도 없음

## 🧐 '딥 서치' VS '와이드 서치'

저는 Wiseflow를 "와이드 서치"로 포지셔닝하고 있습니다. 이는 현재 인기 있는 "딥 서치"와 대비되는 것입니다.

구체적으로, "딥 서치"는 특정 질문에 대해 LLM이 자율적으로 검색 경로를 계획하고, 다른 페이지를 지속적으로 탐색하며, 충분한 정보를 수집하여 답변이나 보고서를 생성하는 것입니다. 그러나 때로는 특정 질문 없이 검색하고, 깊은 탐색도 필요하지 않으며, 광범위한 정보 수집(산업 정보 수집, 배경 정보 수집, 고객 정보 수집 등)만 필요한 경우가 있습니다. 이러한 경우에는 폭이 분명히 더 의미가 있습니다. "딥 서치"로도 이 작업을 달성할 수 있지만, 그것은 대포로 모기를 잡는 것과 같아 비효율적이고 비용이 많이 듭니다. Wiseflow는 바로 이러한 "와이드 서치" 시나리오를 위해 특별히 설계된 도구입니다.

## ✋ Wiseflow가 다른 AI 기반 크롤러와 다른 점은?

- 웹 페이지, 소셜 미디어(현재 Weibo와 Kuaishou 플랫폼 지원), RSS 소스, 검색 엔진 등을 포함한 전체 플랫폼 수집 능력
- 단순한 크롤링뿐만 아니라 자동 분석과 필터링을 수행하며, 14b 파라미터의 LLM으로도 잘 작동
- 사용자 친화적(개발자뿐만 아니라), 코딩 불필요, "즉시 사용 가능"
- 지속적인 반복을 통한 높은 안정성과 가용성, 시스템 리소스와 속도의 균형을 고려한 처리 효율성
- (향후) insight 모듈을 통해 획득한 정보 아래에 숨겨진 "어두운 정보"를 발굴하는 능력

……… 또한 관심 있는 개발자들의 참여를 기대하며, 모두가 사용할 수 있는 AI 최고 정보 책임자를 함께 구축해 나가겠습니다!

## 🌟 빠른 시작

**단 3단계로 시작하세요!**

**Windows 사용자는 사전에 Git Bash 도구를 다운로드하고 bash에서 다음 명령을 실행하세요 [Bash 다운로드 링크](https://git-scm.com/downloads/win)**

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
- LLM_API_BASE="https://api.siliconflow.cn/v1" # LLM 서비스 인터페이스 주소
- JINA_API_KEY="" # 검색 도구 서비스의 키 (Jina 추천, 개인 사용 시 등록 없이 신청 가능)
- PRIMARY_MODEL="Qwen3-14B" # 추천 Qwen3-14B 또는 동일 수준의 사고 모델

### 🚀 시작!

```bash
cd wiseflow
uv venv # 처음 실행할 때만 필요
source .venv/bin/activate  # Linux/macOS
# 또는 Windows에서:
# .venv\Scripts\activate
uv sync # 처음 실행할 때만 필요
python -m playwright install --with-deps chromium # 처음 실행할 때만 필요
chmod +x run.sh # 처음 실행할 때만 필요
./run.sh
```

자세한 사용 방법은 [docs/manual/manual_ko.md](./docs/manual/manual_ko.md)를 참조하세요

## 📚 Wiseflow로 크롤링한 데이터를 자신의 프로그램에서 사용하는 방법

Wiseflow로 크롤링한 모든 데이터는 즉시 pocketbase에 저장되므로 pocketbase 데이터베이스를 직접 조작하여 데이터를 얻을 수 있습니다.

인기 있는 경량 데이터베이스로서 PocketBase는 현재 Go/Javascript/Python 등의 언어 SDK를 제공하고 있습니다.

온라인 서비스는 곧 sync API를 출시하여 온라인 크롤링 결과를 로컬에 동기화하여 "동적 지식 베이스" 등을 구축하는 것을 지원할 예정입니다. 기대해 주세요:

  - 온라인 체험 주소: https://www.aiqingbaoguan.com/
  - 온라인 서비스 API 사용 예제: https://github.com/TeamWiseFlow/wiseflow_plus

## 🛡️ 라이선스

이 프로젝트는 [Apache2.0](LICENSE) 하에 오픈소스입니다.

상업적 협력에 대해서는 **Email: zm.zhao@foxmail.com**로 연락해 주세요

- 상업 고객은 등록을 위해 연락해 주세요. 오픈소스 버전은 영구 무료임을 약속합니다.

## 📬 연락처

질문이나 제안이 있으시면 [issue](https://github.com/TeamWiseFlow/wiseflow/issues)를 통해 메시지를 남겨주세요.

## 🤝 이 프로젝트는 다음과 같은 훌륭한 오픈소스 프로젝트를 기반으로 합니다:

- Crawl4ai(오픈소스 LLM 친화적 웹 크롤러 & 스크래퍼) https://github.com/unclecode/crawl4ai
- MediaCrawler(xhs/dy/wb/ks/bilibili/zhihu 크롤러) https://github.com/NanmiCoder/MediaCrawler
- NoDriver(웹 자동화, 웹 스크래핑, 봇 및 기타 창의적인 아이디어를 위한 빠른 프레임워크 제공) https://github.com/ultrafunkamsterdam/nodriver
- Pocketbase(1개의 파일로 된 오픈소스 실시간 백엔드) https://github.com/pocketbase/pocketbase
- Feedparser(Python에서 피드 파싱) https://github.com/kurtmckee/feedparser

이 프로젝트의 개발은 [GNE](https://github.com/GeneralNewsExtractor/GeneralNewsExtractor), [AutoCrawler](https://github.com/kingname/AutoCrawler), [SeeAct](https://github.com/OSU-NLP-Group/SeeAct)에서 영감을 받았습니다.

## 인용

관련 작업에서 이 프로젝트의 일부 또는 전체를 참조하거나 인용하는 경우 다음 정보를 기재해 주세요:

```
저자: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Apache2.0 라이선스
``` 