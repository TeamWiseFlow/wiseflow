# 수석 정보 책임자 (Wiseflow)

**[English](README_EN.md) | [日本語](README_JP.md) | [中文](README.md)**

🚀 **수석 정보 책임자** (Wiseflow)는 웹사이트, 위챗 공식 계정, 소셜 플랫폼 등 다양한 정보원에서 설정된 관심사를 기반으로 정보를 추출하고, 자동으로 라벨링하여 데이터베이스에 업로드하는 민첩한 정보 마이닝 도구입니다.

**우리가 부족한 것은 정보가 아니라, 방대한 정보에서 노이즈를 필터링하여 가치 있는 정보를 드러내는 능력입니다.**

🌱 수석 정보 책임자가 어떻게 당신의 시간을 절약하고, 관련 없는 정보를 필터링하며, 주목할 만한 요점을 정리하는지 살펴보세요! 🌱

- ✅ 범용 웹 콘텐츠 파서, 통계 학습(오픈 소스 프로젝트 GNE에 의존)과 LLM을 포괄적으로 사용하여 90% 이상의 뉴스 페이지에 적합;
  (**Wiseflow는 위챗 공식 계정 기사에서 정보를 추출하는 데 특히 뛰어나며**, 이를 위해 전용 mp 기사 파서를 구성했습니다!)
- ✅ 비동기 작업 아키텍처;
- ✅ LLM을 사용한 정보 추출 및 라벨 분류 (9B 크기의 LLM으로 작업을 완벽하게 수행할 수 있습니다)!

https://github.com/TeamWiseFlow/wiseflow/assets/96130569/bd4b2091-c02d-4457-9ec6-c072d8ddfb16

<img alt="sample.png" src="asset/sample.png" width="1024"/>

## 🔥 V0.3.1 업데이트

👏 일부 9B 크기의 LLM(THUDM/glm-4-9b-chat)은 이미 안정적인 정보 추출 출력을 달성할 수 있지만, 복잡한 의미의 태그(예: "당 건설") 또는 특정 수집이 필요한 태그(예: "커뮤니티 활동"만 수집하고 콘서트와 같은 대규모 이벤트 정보는 포함하지 않음)에 대해서는
현재 프롬프트로는 정확한 추출을 수행할 수 없습니다. 따라서 이 버전에서는 각 태그에 설명 필드를 추가하여 입력을 통해 더 명확한 태그 지정이 가능하도록 했습니다.

   _참고: 복잡한 설명에는 더 큰 규모의 모델이 필요합니다. 자세한 내용은 [모델 추천 2024-09-03](###-4. 모델 추천 [2024-09-03])을 참조하십시오_

👏 또한, 이전 버전의 프롬프트 언어 선택 문제(출력 결과에는 영향을 주지 않음)에 대응하여, 현재 버전에서는 솔루션을 더욱 간소화했습니다. 사용자는 더 이상 시스템 언어를 지정할 필요가 없으며(Docker에서는 그다지 직관적이지 않습니다), 시스템은 태그와 그 설명을 기반으로 프롬프트 언어(즉, 정보의 출력 언어)를 판단하여 wiseflow의 배포 및 사용을 더욱 간소화합니다. **하지만 현재 wiseflow는 간체 중국어와 영어만 지원하며, 다른 언어의 요구 사항은 core/insights/get_info.py의 프롬프트를 변경하여 구현할 수 있습니다**

🌹 또한, 이번 업데이트에서는 지난 2개월 동안의 PR을 병합하고, 다음과 같은 새로운 기여자를 추가했습니다:

@wwz223 @madizm @GuanYixuan @xnp2020 @JimmyMa99

🌹 여러분의 기여에 감사드립니다!

## 🌟 애플리케이션에 wiseflow를 통합하는 방법

wiseflow는 네이티브 LLM 애플리케이션으로, 7B~9B 크기의 LLM만으로 정보 마이닝, 필터링 및 분류 작업을 잘 수행할 수 있으며, 벡터 모델이 필요하지 않아 다양한 하드웨어 환경에서의 로컬 및 프라이빗 배포에 적합합니다.

wiseflow는 마이닝된 정보를 내장된 Pocketbase 데이터베이스에 저장하므로, wiseflow의 코드를 깊이 이해할 필요 없이 데이터베이스 읽기 작업만으로 통합이 가능합니다!

PocketBase는 인기 있는 경량 데이터베이스로, 현재 Go/Javascript/Python 등의 언어 SDK가 있습니다.
   - Go : https://pocketbase.io/docs/go-overview/
   - Javascript : https://pocketbase.io/docs/js-overview/
   - python : https://github.com/vaphes/pocketbase

## 🔄 wiseflow와 일반적인 크롤러 도구, LLM-Agent 프로젝트의 차이점과 연관성

| 특징 | 수석 정보 책임자 (Wiseflow) | 크롤러 / 스크래퍼 | LLM-Agent |
|----------------|--------------------------------------|-------------------|-----------|
| **주요 해결 문제** | 데이터 처리 (필터링, 정제, 라벨링) | 원시 데이터 획득 | 하류 애플리케이션 |
| **연관성** | | WiseFlow에 통합 가능, wiseflow에 더 강력한 원시 데이터 획득 능력을 부여 | WiseFlow를 동적 지식 기반으로 통합 가능 |

## 📥 설치 및 사용 방법

### 1. 저장소 복제

🌹 스타링과 포크는 좋은 습관입니다 🌹

```bash
git clone https://github.com/TeamWiseFlow/wiseflow.git
cd wiseflow
```

### 2. Docker를 사용하여 실행하는 것을 권장

```bash
docker compose up
```

주의:

- wiseflow 코드 저장소의 루트 디렉토리에서 위의 명령을 실행하십시오;

- 실행 전에 .env 파일을 생성하고, Dockerfile과 동일한 디렉토리(wiseflow 코드 저장소의 루트 디렉토리)에 배치하십시오. .env 파일은 env_sample을 참조할 수 있습니다;

- 처음 docker 컨테이너를 실행할 때 오류가 발생할 수 있습니다. 이는 pb 저장소의 관리자 계정이 아직 생성되지 않았기 때문입니다.

- 이 시점에서 컨테이너를 실행한 상태로 두고, 브라우저를 열어 http://127.0.0.1:8090/_/에 접속하여 프롬프트에 따라 관리자 계정을 생성하십시오(반드시 이메일을 사용해야 합니다). 그런 다음, 생성한 관리자의 이메일 주소(다시 말하지만, 이메일을 사용해야 합니다)와 비밀번호를 .env 파일에 입력하고, 컨테이너를 다시 시작하십시오.

_컨테이너의 시간대와 언어를 변경하려면 다음 명령으로 이미지를 실행하십시오_

```bash
docker run -e LANG=zh_CN.UTF-8 -e LC_CTYPE=zh_CN.UTF-8 your_image
```

### 2. [대안] Python을 직접 사용하여 실행

```bash
conda create -n wiseflow python=3.10
conda activate wiseflow
cd core
pip install -r requirements.txt
```

이후 core/scripts 폴더에 있는 스크립트를 참조하여 각각 pb, task, backend를 시작할 수 있습니다 (스크립트 파일을 core 디렉토리로 이동하십시오).

**주의:**
   - 반드시 pb를 먼저 시작해야 하며, task와 backend는 독립적인 프로세스이므로 순서는 상관없고, 필요에 따라 하나만 시작해도 됩니다.
   - 먼저 여기를 방문하여 https://pocketbase.io/docs/ 본인의 장치에 맞는 pocketbase 클라이언트를 다운로드하고 /core/pb 디렉토리에 배치해야 합니다.
   - pb 실행 문제(처음 실행 시 오류 포함)에 대해서는 [core/pb/README.md](/core/pb/README.md)를 참조하십시오.
   - 사용 전에 .env 파일을 생성하고 편집하여 wiseflow 코드 저장소의 루트 디렉토리(core 디렉토리의 상위)에 배치하십시오. .env 파일은 env_sample을 참고하고, 자세한 설정 설명은 아래를 참조하십시오.

📚 개발자를 위한 더 많은 정보는 [/core/README.md](/core/README.md)를 참조하십시오.

pocketbase를 통해 액세스한 데이터:
   - http://127.0.0.1:8090/_/ - 관리자 대시보드 UI
   - http://127.0.0.1:8090/api/ - REST API

### 3. 설정

env_sample 파일을 복사하여 .env로 이름을 변경하고, 아래 내용을 참고하여 본인의 설정 정보를 입력하십시오 (예: LLM 서비스 토큰 등).

**윈도우 사용자가 Python 프로그램을 직접 실행하려면, “시작 - 설정 - 시스템 - 정보 - 고급 시스템 설정 - 환경 변수”에서 아래 항목을 설정하십시오. 설정 후에는 터미널을 재시작해야 합니다.**

   - LLM_API_KEY # 대형 모델 추론 서비스 API 키
   - LLM_API_BASE # 이 프로젝트는 OpenAI SDK를 사용하며, 모델 서비스가 OpenAI 인터페이스를 지원하면 해당 항목을 설정하여 정상적으로 사용할 수 있습니다. OpenAI 서비스를 사용할 경우 이 항목을 삭제하면 됩니다.
   - WS_LOG="verbose"  # 디버그 모드를 시작할지 여부를 설정합니다. 필요 없으면 삭제하십시오.
   - GET_INFO_MODEL # 정보 추출 및 태그 매칭 작업 모델, 기본값은 gpt-4o-mini-2024-07-18
   - REWRITE_MODEL # 유사 정보 병합 및 재작성 작업 모델, 기본값은 gpt-4o-mini-2024-07-18
   - HTML_PARSE_MODEL # 웹 페이지 파싱 모델 (GNE 알고리즘의 성능이 부족할 때 자동으로 활성화됨), 기본값은 gpt-4o-mini-2024-07-18
   - PROJECT_DIR # 데이터, 캐시 및 로그 파일의 저장 위치. 코드 저장소의 상대 경로로 설정되며, 기본값은 코드 저장소입니다.
   - PB_API_AUTH='email|password' # pb 데이터베이스 관리자의 이메일과 비밀번호 (반드시 이메일이어야 하며, 가상의 이메일일 수도 있습니다).
   - PB_API_BASE  # 기본적으로 필요하지 않지만, 기본 pocketbase 로컬 인터페이스(8090)를 사용하지 않는 경우에만 설정해야 합니다.

### 4. 모델 추천 [2024-09-03]

반복적인 테스트(영어 및 중국어 작업)를 통해 **GET_INFO_MODEL**, **REWRITE_MODEL**, **HTML_PARSE_MODEL**의 최소 사용 가능한 모델은 각각 **"THUDM/glm-4-9b-chat"**, **"Qwen/Qwen2-7B-Instruct"**, **"Qwen/Qwen2-7B-Instruct"**입니다.

현재, SiliconFlow는 Qwen2-7B-Instruct, glm-4-9b-chat 온라인 추론 서비스를 무료로 제공한다고 발표했습니다. 이로 인해 여러분은 wiseflow를 "제로 비용"으로 사용할 수 있습니다!

😄 원하시면 저의 [siliconflow 초대 링크](https://cloud.siliconflow.cn?referrer=clx6wrtca00045766ahvexw92)를 사용하셔도 좋습니다. 이렇게 하면 저도 더 많은 토큰 보상을 받을 수 있습니다 😄

⚠️ **V0.3.1 업데이트**

설명이 포함된 복잡한 태그를 사용하는 경우, glm-4-9b-chat 크기의 모델로는 정확한 이해를 보장할 수 없습니다. 현재 테스트 결과, 이 유형의 작업에 적합한 모델은 **Qwen/Qwen2-72B-Instruct**와 **gpt-4o-mini-2024-07-18**입니다.

`gpt-4o-mini-2024-07-18` 모델 사용을 원하는 사용자들은 제3자 대리 서비스 **AiHubMix**를 시도해 볼 수 있습니다. 국내 네트워크 환경에서 직접 연결을 지원하며, 알리페이로 충전이 가능합니다 (실제 요율은 공식 웹사이트 요율의 약 14% 할인).

🌹 다음 초대 링크 [AiHubMix 초대 링크](https://aihubmix.com?aff=Gp54)를 사용하여 등록하십시오 🌹

🌍 위 두 플랫폼의 온라인 추론 서비스는 모두 OpenAI SDK와 호환되며, `.env` 파일의 `LLM_API_BASE`와 `LLM_API_KEY`를 설정한 후 사용할 수 있습니다.

### 5. **관심사와 정기 스캔 소스 추가**

프로그램을 시작한 후 pocketbase 관리자 대시보드 UI(http://127.0.0.1:8090/_)를 엽니다.

#### 5.1 tags 폼 열기

이 폼을 통해 관심사를 지정할 수 있으며, LLM은 이를 기준으로 정보를 추출하고 필터링하여 분류합니다.

tags 필드 설명:
   - name: 관심사 이름
   - explaination: 관심사의 상세 설명 또는 구체적인 정의, 예를 들어 "상하이시 공식 발표 중학교 진학 정보에 한정" (tag 이름: 상하이 중학교 진학 정보)
   - activated: 활성화 여부. 비활성화하면 해당 관심사는 무시되며, 비활성화 후 다시 활성화할 수 있습니다. 활성화 및 비활성화는 Docker 컨테이너를 재시작하지 않고도 가능하며, 다음 정기 작업 시 업데이트됩니다.

#### 5.2 sites 폼 열기

이 폼을 통해 사용자 정의 소스를 지정할 수 있으며, 시스템은 백그라운드에서 정기 작업을 시작하여 로컬에서 소스 스캔, 파싱 및 분석을 수행합니다.

sites 필드 설명:
   - url: 소스의 URL, 소스는 특정 기사 페이지가 아닌 기사 목록 페이지만 제공하면 됩니다.
   - per_hours: 스캔 주기, 시간 단위, 정수 타입 (1~24 범위, 하루 한 번 이상 스캔하지 않는 것이 좋습니다. 즉, 24로 설정).
   - activated: 활성화 여부. 비활성화하면 해당 소스는 무시되며, 비활성화 후 다시 활성화할 수 있습니다. 활성화 및 비활성화는 Docker 컨테이너를 재시작하지 않고도 가능하며, 다음 정기 작업 시 업데이트됩니다.

### 6. 로컬 배포

보시다시피, 이 프로젝트는 최소한 7b\9b 크기의 LLM만 필요하며, 어떤 벡터 모델도 필요하지 않습니다. 이는 3090RTX (24G VRAM) 한 개만 있으면 이 프로젝트를 완전히 로컬에 배포할 수 있음을 의미합니다.

로컬 배포 LLM 서비스가 OpenAI SDK와 호환되는지 확인하고, LLM_API_BASE를 설정하십시오.

참고: 태그 설명에 대한 7b~9b 크기의 LLM이 정확히 이해하도록 하려면, 프롬프트 최적화를 위해 dspy를 사용하는 것이 좋지만, 이를 위해서는 약 50개의 수동 레이블 데이터가 필요합니다. 자세한 내용은 [DSPy](https://dspy-docs.vercel.app/)를 참조하십시오.

## 🛡️ 라이선스

이 프로젝트는 [Apache2.0](LICENSE) 오픈소스로 제공됩니다.

상업적 사용 및 맞춤형 협력을 원하시면 **Email: 35252986@qq.com**으로 연락해 주세요.

   - 상업적 고객은 저희에게 연락하여 등록해 주세요. 제품은 영원히 무료로 제공할 것을 약속합니다.

## 📬 연락처

궁금한 점이나 제안 사항이 있으시면 [issue](https://github.com/TeamWiseFlow/wiseflow/issues)를 통해 연락해 주세요.

## 🤝 이 프로젝트는 다음과 같은 훌륭한 오픈 소스 프로젝트를 기반으로 합니다:

- GeneralNewsExtractor （ General Extractor of News Web Page Body Based on Statistical Learning） https://github.com/GeneralNewsExtractor/GeneralNewsExtractor
- json_repair（Repair invalid JSON documents ） https://github.com/josdejong/jsonrepair/tree/main 
- python-pocketbase (pocketBase client SDK for python) https://github.com/vaphes/pocketbase

## Citation

본 프로젝트의 일부 또는 전체를 참조하거나 인용한 경우, 다음 정보를 명시해 주세요：

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```
