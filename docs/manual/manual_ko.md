# WiseFlow 설치 및 사용자 매뉴얼

**3.x 사용자는 원본 코드 저장소와 pb 폴더를 완전히 삭제하고 4.x 코드 저장소를 다시 클론해야 합니다. 그렇지 않으면 정상적으로 시작할 수 없습니다.**

**4.0 사용자가 버전 4.1로 업그레이드하는 경우, 최신 코드를 가져온 후 먼저 ./pb/pocketbase migrate 명령을 실행해야 합니다. 그렇지 않으면 정상적으로 시작할 수 없습니다.**

**4.2버전부터 먼저 google chrome 브라우저를 다운로드하고 기본 경로로 설치하세요**

## 📋 시스템 요구사항

- **Python**: 3.10 - 3.12（3.12 권장）
- **운영체제**: macOS, Linux 또는 Windows
- **하드웨어 요구사항**: 8GB 이상의 RAM（온라인 LLM 서비스 사용 시）

## 📥 사용 방법

WiseFlow 4.x 사용자 인터페이스는 PocketBase를 사용합니다（이상적이지는 않지만 현재 최적의 솔루션입니다）

### 1. 인터페이스 접근

🌐 시작 성공 후, 브라우저를 열고 다음 주소로 접속하세요：**http://127.0.0.1:8090/_/**

### 2. 정보 소스 및 포커스 포인트 설정

focus_point 폼으로 전환하세요

이 폼을 통해 포커스 포인트를 지정할 수 있습니다. LLM은 이를 기반으로 정보를 정제, 필터링 및 분류합니다.

필드 설명：
- focuspoint（필수）：포커스 포인트 설명. LLM에게 어떤 정보가 필요한지 알려줍니다. 예: "상하이 초중등학교 정보" 또는 "입찰 공고"
- restrictions（선택사항）：포커스 포인트 필터링 제약조건. LLM에게 어떤 정보를 제외해야 하는지 알려줍니다. 예: "상하이시 공식 발표 중학교 입학 정보만" 또는 "2025년 1월 1일 이후 발표되고 금액이 100만 이상인 것"
- explanation（선택사항）：특수 개념이나 전문 용어에 대한 설명. LLM의 오해를 방지하기 위함. 예: "초중등학교는 초등학교에서 중학교로의 전환을 의미합니다"
- activated：활성화 여부. 끄면 이 포커스 포인트는 무시되며, 나중에 다시 켤 수 있습니다
- freq：크롤링 빈도（시간 단위）, 정수형（하루에 한 번을 초과하지 않는 것을 권장, 즉 24로 설정, 최소값은 2, 즉 2시간마다 크롤링）
- search：상세 검색 소스를 설정합니다. 현재 bing, github, arxiv, ebay를 지원합니다
- sources：해당하는 정보 소스 선택

#### 💡 초점 포인트 작성 방식은 정보 추출이 요구 사항을 충족하는지 여부를 직접적으로 결정하므로 매우 중요합니다. 특히:

  - 사용 사례가 산업 정보, 학술 정보, 정책 정보 등 추적이고 정보 소스에 광범위한 검색이 포함된 경우 초점 포인트는 검색 엔진과 유사한 키워드 모델을 사용해야 합니다. 동시에 제약 조건과 설명을 추가하고 필요한 경우 역할과 목표를 정의해야 합니다.

  - 사용 사례가 경쟁사 추적, 배경 조사 등과 같이 정보 출처가 경쟁사 홈페이지, 공식 계정 등 매우 구체적인 경우, "가격 인하 정보", "신제품 정보" 등 관심 있는 관점을 초점 포인트로 입력하기만 하면 됩니다.

**포커스 포인트 설정 변경은 프로그램 재시작 없이 다음 실행 시 자동으로 적용됩니다.**

정보 소스는 sources 페이지 또는 focus_points 바인딩 페이지에서 추가할 수 있습니다. 정보 소스 추가 필드 설명：

- type：유형, 현재 지원：web, rss, wb（웨이보）, ks（쿠아이쇼우）, mp（위챗 공식 계정（4.0에서는 일시적으로 지원되지 않음, 4.1을 기다리고 있습니다））
- creators：크롤링할 크리에이터 ID（여러 개는 ','로 구분）, ks, wb, mp에서만 유효. ks와 mp는 'homefeed' 입력을 지원합니다（시스템 푸시 콘텐츠를 매번 가져오는 것을 의미）. 이 필드는 비워둘 수도 있으며, 그 경우 정보 소스는 검색에만 사용됩니다

  *참고：ID는 플랫폼의 해당 웹 버전 홈페이지 링크를 사용하세요. 예를 들어, 웨이보의 ID가 https://m.weibo.cn/profile/2656274875인 경우, ID는 2656274875입니다*

- url：정보 소스에 해당하는 링크, rss와 web 유형에서만 유효

### 3. 결과 보기

- infos 페이지：최종적으로 추출된 유용한 정보 저장
- crawled_data 페이지：크롤링된 원본 데이터 저장
- ks_cache 페이지：쿠아이쇼우 캐시 데이터 저장
- wb_cache 페이지：웨이보 캐시 데이터 저장

## 🌟 배포 설치

**배포 설치는 3단계만으로 완료됩니다！**

**Windows 사용자는 사전에 Git Bash 도구를 다운로드하고 bash에서 다음 명령을 실행하세요 [Bash 다운로드 링크](https://git-scm.com/downloads/win)**

### 📋 프로젝트 소스 코드 다운로드 및 uv와 pocketbase 설치

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

위 작업으로 uv 설치가 완료됩니다.

다음으로 [pocketbase docs](https://pocketbase.io/docs/) 에서 자신의 운영체제에 맞는 pocketbase 프로그램을 다운로드하여 [.pb](./pb/) 폴더에 위치시키세요.

install_pocketbase.sh(MacOS/Linux용) 또는 install_pocketbase.ps1(Windows용)을 사용하여 설치할 수도 있습니다.

### 📥 env_sample을 기반으로 .env 파일 설정

wiseflow 폴더（프로젝트 루트 디렉토리）에서 env_sample을 기반으로 .env 파일을 생성하고 관련 설정을 입력하세요.

버전 4.x에서는 사용자가 .env에서 PocketBase 계정 인증 정보를 제공할 필요가 없으며, PocketBase 버전도 제한되지 않습니다. 또한 Secondary Model 설정도 일시적으로 제거되었습니다. 따라서 실제로는 4개의 매개변수만으로 설정을 완료할 수 있습니다：

- LLM_API_KEY="" # LLM 서비스 키（OpenAI 형식 API를 제공하는 모델 서비스 제공업체라면 어느 것이든 가능, 로컬에서 배포된 ollama를 사용하는 경우 설정 불필요）
- LLM_API_BASE="" # LLM 서비스 기본 URL (있는 경우. OpenAI 사용자의 경우 비워두세요)
- PRIMARY_MODEL=ByteDance-Seed/Seed-OSS-36B-Instruct # 가격에 민감하고 추출이 복잡하지 않은 시나리오에서는 Qwen3-14B를 사용할 수 있습니다
- VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct" # 시각 모델, 선택사항이지만 권장. 필요한 페이지 이미지 분석에 사용（프로그램은 컨텍스트에 따라 분석이 필요한지 여부를 판단하며, 모든 이미지를 추출하지는 않음）, 최소 Qwen2.5-VL-7B-Instruct로 충분합니다

### 🚀 시작해 보세요！

```bash
cd wiseflow
uv venv # 처음 실행할 때만 필요
source .venv/bin/activate  # Linux/macOS
# 또는 Windows에서:
# .venv\Scripts\activate
uv sync # 처음 실행할 때만 필요
chmod +x run.sh # 처음 실행할 때만 필요
./run.sh
```

✨ **이렇게 간단합니다！** 시작 스크립트는 자동으로 다음 작업을 완료합니다：
- ✅ 환경 설정 확인
- ✅ 프로젝트 종속성 동기화
- ✅ 가상 환경 활성화
- ✅ PocketBase 데이터베이스 시작
- ✅ WiseFlow 애플리케이션 실행

프로그램은 먼저 모든 활성화된 소스（activated가 true로 설정된 것）에 대해 크롤링 작업을 수행한 다음, 설정된 빈도로 시간 단위로 주기적으로 실행합니다.

⚠️ **참고：** `Ctrl+C`로 프로세스를 종료할 때, PocketBase 프로세스는 자동으로 종료되지 않을 수 있으며, 수동으로 닫거나 터미널을 재시작해야 할 수 있습니다.

### 📝 수동 설치（선택사항）

각 단계를 수동으로 제어하려면 다음 단계를 따르세요：

#### 1. 루트 디렉토리의 install_pocketbase 스크립트 실행

Linux/macOS 사용자는 다음을 실행하세요：

```bash
chmod +x install_pocketbase.sh
./install_pocketbase.sh
```

**Windows 사용자는 다음을 실행하세요：**
```powershell
.\install_pocketbase.ps1
```

#### 2. 가상 환경 생성 및 활성화

```bash
uv venv
source .venv/bin/activate  # Linux/macOS
# Windows의 경우：
# .venv\Scripts\activate
```

##### 4.2 종속성 설치

```bash
uv sync
```

이렇게 하면 WiseFlow와 모든 종속성이 설치되며, 종속성 버전의 일관성이 보장됩니다. uv sync는 프로젝트의 종속성 선언을 읽고 가상 환경을 동기화합니다.

마지막으로 메인 서비스를 시작합니다：

```bash
python core/run_task.py
# Windows의 경우：
# python core\run_task.py
```

PocketBase 사용자 인터페이스를 사용해야 하는 경우, PocketBase 서비스를 시작합니다：

```bash
cd wiseflow/pb
./pocketbase serve
```

또는 Windows의 경우：

```powershell
cd wiseflow\pb
.\pocketbase.exe serve
```

### 🔧 환경 변수 설정

빠른 시작 또는 수동 설치 모두 env_sample을 기반으로 .env 파일을 생성해야 합니다：

#### 1. LLM 관련 설정

WiseFlow는 LLM 네이티브 애플리케이션입니다. 프로그램에 안정적인 LLM 서비스를 제공하세요.

🌟 **WiseFlow는 모델 서비스 제공업체를 제한하지 않습니다. OpenAI SDK와 호환되는 서비스라면 로컬에서 배포된 ollama, Xinference, 기타 서비스도 포함하여 사용할 수 있습니다**

##### 추천 1：SiliconFlow의 MaaS 서비스 사용

SiliconFlow는 대부분의 주류 오픈 소스 모델에 대한 온라인 MaaS 서비스를 제공합니다. 그들의 가속 추론 기술로 인해 서비스는 속도와 가격 모두에서 우위를 가집니다. SiliconFlow의 서비스를 사용할 때 .env 설정은 다음과 같습니다：

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE=""
PRIMARY_MODEL=ByteDance-Seed/Seed-OSS-36B-Instruct # 가격에 민감하고 추출이 복잡하지 않은 시나리오에서는 Qwen3-14B를 사용할 수 있습니다
VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct"
CONCURRENT_NUMBER=6
```

[Siliconflow](https://www.siliconflow.com/)의 모델 서비스 사용을 권장합니다.

##### 추천 2：AiHubMix의 프록시된 해외 클로즈드 소스 상용 모델 서비스（OpenAI, Claude, Gemini 등）사용

AiHubMix의 모델을 사용할 때 .env 설정은 다음과 같습니다：

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://aihubmix.com/v1" # 자세한 내용은 https://doc.aihubmix.com/ 참조
PRIMARY_MODEL="o3-mini" #or openai/gpt-oss-20b
VL_MODEL="gpt-4o-mini"
CONCURRENT_NUMBER=6
```

😄 [AiHubMix 초대 링크](https://aihubmix.com?aff=Gp54)를 사용하여 등록해 주세요 🌹

##### 로컬 LLM 서비스 배포

Xinference를 예로 들면, .env 설정은 다음과 같습니다：

```
# LLM_API_KEY='' 로컬 서비스에서는 불필요, 주석 처리하거나 삭제하세요
LLM_API_BASE='http://127.0.0.1:9997' # ollama의 경우 'http://127.0.0.1:11434/v1'
PRIMARY_MODEL=시작된 모델 ID
VL_MODEL=시작된 모델 ID
CONCURRENT_NUMBER=1 # 실제 하드웨어 리소스에 따라 결정
```

#### 3. 기타 선택적 설정

다음은 선택적 설정입니다：
- #VERBOSE="true" 

  관찰 모드를 활성화할지 여부. 활성화하면 디버그 정보가 로거 파일에 기록됩니다（기본적으로는 콘솔에만 출력）

- #CONCURRENT_NUMBER=8 

  LLM 요청의 동시 실행 수를 제어하는 데 사용. 설정하지 않으면 기본값은 1（활성화하기 전에 LLM 제공업체가 설정된 동시성을 지원하는지 확인하세요. 로컬 대형 모델은 하드웨어 기반에 자신이 있는 경우를 제외하고는 신중하게 사용하세요）

## 🐳 Docker 배포

버전 4.x의 Docker 배포 솔루션은 추후 업데이트를 기다려 주세요. 또한 관심 있는 개발자의 PR 기여도 기다리고 있습니다~

## 🌹 유료 서비스

오픈 소스는 쉽지 않습니다 ☺️ 문서 작성과 상담 Q&A는 더욱 시간이 많이 걸립니다. 지원을 제공해 주시면 더 나은 품질의 서비스를 제공하겠습니다~

- 상세 튜토리얼 영상 + 이메일 질의응답 3회 + 유료 사용자 위챗 그룹 가입: ￥36.88

구매 방법: 아래 결제 코드를 스캔한 후 위챗(WeChat) ID: bigbrother666sh 를 추가하고 결제 스크린샷을 보내주세요.

(친구 추가 후 최대 8시간 이내에 수락됩니다. 35252986@qq.com 이메일로도 연락 가능합니다.)

<img src="alipay.png" alt="알리페이 결제 코드" width="300">      <img src="weixinpay.jpg" alt="위챗페이 결제 코드" width="300"> 