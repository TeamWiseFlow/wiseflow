# Wiseflow

**[中文](README.md) | [English](README_EN.md) | [日本語](README_JP.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

🚀 **STEP INTO 5.x**

> 📌 **4.x를 찾고 계신가요?** 원래 v4.30 이전 버전의 코드는 [`4.x` 브랜치](https://github.com/TeamWiseFlow/wiseflow/tree/4.x)에서 확인할 수 있습니다.

```
"내 삶에는 한계가 있지만, 지식에는 한계가 없다. 유한한 것으로 무한한 것을 쫓으니, 위태로울 뿐이다!" —— 『장자·내편·양생주제삼』
```

wiseflow 4.x(이전 버전 포함)는 일련의 정밀한 워크플로우를 통해 특정 시나리오에서 강력한 데이터 수집 능력을 구현했지만, 여전히 많은 한계가 존재했습니다:

- 1. 인터랙티브 콘텐츠를 수집할 수 없음 (클릭해야만 나타나는 콘텐츠, 특히 동적 로딩의 경우)
- 2. 정보 필터링과 추출만 가능하며, 다운스트림 작업 처리 능력이 거의 없음
- ……

기능 개선과 범위 확장에 꾸준히 노력해 왔지만, 현실 세계는 복잡하고 인터넷도 마찬가지입니다. 규칙을 완전히 망라하는 것은 불가능하므로, 고정된 워크플로우로는 모든 시나리오에 대응할 수 없습니다. 이것은 wiseflow의 문제가 아니라 전통적인 소프트웨어의 문제입니다!

그러나 지난 1년간 Agent 기술의 비약적인 발전은 대규모 언어 모델로 인간의 인터넷 행동을 완전히 시뮬레이션하는 것이 기술적으로 가능하다는 것을 보여주었습니다. [openclaw](https://github.com/openclaw/openclaw)의 등장은 이러한 확신을 더욱 굳건히 했습니다.

더욱 놀라운 것은, 초기 실험과 탐색을 통해 wiseflow의 데이터 수집 능력을 "플러그인" 형태로 openclaw에 통합하면 위에서 언급한 두 가지 한계를 완벽하게 해결할 수 있다는 것을 발견했습니다.

https://github.com/user-attachments/assets/8d097b3b-f9ab-42eb-98bb-88af5d28b089

다만, openclaw의 플러그인 시스템은 우리가 전통적으로 이해하는 "플러그인"(Claude Code의 플러그인과 유사한 것)과는 다르기 때문에, "add-on"이라는 개념을 별도로 도입해야 했습니다. 정확히 말하면, wiseflow 5.x는 openclaw add-on 형태로 제공됩니다. 원래 openclaw에는 "add-on" 아키텍처가 없지만, 실제로는 몇 가지 간단한 셸 명령어만으로 이 "개조"를 완료할 수 있습니다. 또한 실제 비즈니스 시나리오를 위한 프리셋 설정이 포함된 즉시 사용 가능한 openclaw 강화 버전인 [openclaw_for_business](https://github.com/TeamWiseFlow/openclaw_for_business)도 준비했습니다. 클론한 후 wiseflow 릴리스를 openclaw_for_business의 add-on 폴더에 배치하면 됩니다.

## ✨ wiseflow를 설치하면 무엇을 얻을 수 있나요（원본 openclaw보다 우수한 점）？

### 1. 탐지 방지 브라우저, 브라우저 확장 프로그램 설치 불필요

wiseflow의 patch-001은 openclaw 내장 Playwright를 [Patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright)(Playwright의 탐지 방지 포크)로 교체하여, 자동화 브라우저가 대상 웹사이트에 감지·차단될 가능성을 크게 줄입니다. 이를 통해 Chrome Relay Extension 설치 없이, 관리형 브라우저만으로도 Relay와 동등하거나 더 뛰어난 웹 수집 및 조작 능력을 달성할 수 있습니다.

📥 *저희는 nodriver, browser-use, Vercel의 agent-browser 등 현재 시장에서 인기 있는 모든 브라우저 자동화 프레임워크를 종합적으로 평가했습니다. 모두 CDP를 통해 동작하고 openclaw 전용 지속적 프로필을 제공한다는 기본 원리는 같지만, CDP 프로브를 완전히 제거하는 것은 Patchright뿐입니다. 즉, 가장 순수한 CDP 직접 연결 방식을 사용하더라도 여전히 검출 가능한 특징이 남아 있습니다. 다른 프레임워크는 데이터 수집이 아닌 자동화 테스트를 목적으로 설계되었지만, Patchright는 처음부터 데이터 수집을 목적으로 설계되었습니다. 본질적으로 Playwright의 패치이기 때문에 거의 모든 Playwright 상위 API를 그대로 계승하며, 이로 인해 openclaw와 기본적으로 호환되어 추가 플러그인이나 MCP를 설치할 필요가 없습니다.*

### 2. 자동 탭 복구 메커니즘

Agent 작업 중 대상 탭이 예기치 않게 닫히거나 사라질 경우, 스냅샷 기반 탭 복구를 자동으로 수행하여 탭 소실로 인한 작업 중단을 방지합니다.

### 3. 스마트 검색 Skill

openclaw 내장 `web_search`를 더욱 강력한 검색 기능으로 대체합니다. 원버전 내장 web search tool 대비 스마트 검색의 세 가지 핵심 강점:

- **완전 무료, API 키 불필요**: 서드파티 검색 API에 의존하지 않아 비용 제로
- **실시간 검색, 최고의 시의성**: 브라우저를 직접 대상 페이지나 주요 소셜 미디어 플랫폼(Weibo, Twitter/X, Facebook 등)으로 ��동하여 최신 게시물을 즉시 검색
- **검색 출처 사용자 정의 가능**: 사용자가 검색 출처를 자유롭게 지정하여 필요한 정보를 정확하게 취득

### 4. 새 미디어 편집자 Crew（사전 설정 AI 에이전트）

즉시 사용 가능한 중국어 소셜 미디어 콘텐츠 제작 AI 에이전트로, 웨이보, 샤오홍슈, 즈후, 빌리빌리, 더우인 등 중국 주요 플랫폼에 특화되어 있습니다.

**주요 기능：**

- 주제 리서치 + 트렌드 분석（Mode A）
- 초안 확장 + 온라인 근거 추가（Mode B）
- 기사 완성 후 [文颜（Wenyan）](https://github.com/caol64/wenyan)을 자동으로 호출하여 위챗 공식 계정 스타일 HTML로 렌더링（내장 테마 7개 지원）
- 위챗 공식 계정 임시 보관함에 직접 발행（Mode C, `WECHAT_APP_ID`/`WECHAT_APP_SECRET` 설정 필요）
- AI 이미지/영상 생성 지원（[SiliconFlow](https://www.siliconflow.com/) 이미지/영상 생성, `SILICONFLOW_API_KEY` 설정 필요）

## 🌟 빠른 시작

> **💡 API 비용 안내**
>
> wiseflow 5.x는 openclaw의 Agent 워크플로우를 기반으로 하며, LLM API 접근이 필요합니다. 사전에 API 자격 증명을 준비하시기 바랍니다:
>
> - **해외 사용자（권장）**：[SiliconFlow](https://www.siliconflow.com/) — 등록 후 무료 크레딧 지급, 초기 사용 비용 충당 가능
> - **OpenAI / Anthropic 및 기타 제공업체**：호환 가능한 모든 API 사용 가능

본 저장소의 [Releases](https://github.com/TeamWiseFlow/wiseflow/releases)에서 openclaw_for_business와 wiseflow addon이 포함된 통합 패키지를 다운로드하세요.

1. 압축 파일을 다운로드하고 압축을 해제합니다
2. 압축 해제된 폴더로 이동합니다
3. 시작 방식을 선택합니다:

   **디버그 모드**（단회 실행, 테스트 및 개발용）:
   ```bash
   ./scripts/dev.sh gateway
   ```

   **프로덕션 모드**（시스템 서비��로 설치, 장기 운영용）:
   ```bash
   ./scripts/reinstall-daemon.sh
   ```

> **시스템 요구사항**
> - **Ubuntu 22.04** 권장
> - **Windows WSL2** 환경 지원
> - **macOS** 지원
> - **Windows 네이티브** 환경에서의 직접 실행은 **지원하지 않음**

### 【대안】수동 설치

> 주의: 먼저 openclaw_for_business를 다운로드하여 배포해야 합니다. 다운로드 주소: https://github.com/TeamWiseFlow/openclaw_for_business/releases

저장소 내의 `wiseflow` 폴더(저장소 전체가 아님)를 openclaw_for_business의 `addons/` 디렉토리에 복사하세요:

```bash
# 방법 1: wiseflow 저장소에서 클론
git clone https://github.com/TeamWiseFlow/wiseflow.git /tmp/wiseflow
cp -r /tmp/wiseflow/wiseflow <openclaw_for_business>/addons/wiseflow
```

설치 후 openclaw_for_business를 재시작하면 적용됩니다.

## 디렉토리 구조

```
wiseflow/                         # addon 패키지（addons/ 디렉토리에 복사）
├── addon.json                    # 메타데이터
├── overrides.sh                  # pnpm overrides + 내장 web_search 비활성화
├── patches/
│   ├── 001-browser-tab-recovery.patch        # 탭 복구 패치
│   ├── 002-disable-web-search-env-var.patch  # 내장 web_search 비활성화 (env var)
│   └── 003-act-field-validation.patch        # ACT 필드 유효성 검사 패치
├── skills/                       # 글로벌 스킬（모든 에이전트 사용 가능）
│   ├── browser-guide/SKILL.md    # 브라우저 모범 사례 (로그인/캡차/지연 로딩 등)
│   ├── smart-search/SKILL.md     # 다중 플랫폼 검색 URL 빌더 (내장 web_search 대체)
│   └── rss-reader/               # RSS/Atom 피드 리더
│       ├── SKILL.md
│       ├── package.json
│       └── scripts/fetch-rss.mjs
└── crew/                         # 사전 설정 AI 에이전트（Crew 템플릿）
    └── new-media-editor/         # 새 미디어 편집자（중국어 소셜 미디어 콘텐츠 제작）
        ├── IDENTITY.md / SOUL.md / AGENTS.md / TOOLS.md / ...
        └── skills/               # Crew 전용 스킬
            ├── siliconflow-img-gen/   # AI 이미지 생성（SiliconFlow API）
            ├── siliconflow-video-gen/ # AI 영상 생성（SiliconFlow API）
            └── wenyan-formatter/      # Markdown → 위챗 HTML / 임시 보관함 발행

docs/                             # 기술 문서（저장소 루트）
├── anti-detection-research.md
└── more_powerful_search_skill/

scripts/                          # 유틸리티 스크립트（저장소 루트）
└── generate-patch.sh

tests/                            # 테스트 케이스 및 스크립트（저장소 루트）
├── README.md
└── run-managed-tests.mjs
```

## WiseFlow Pro 버전 출시!

더 강력한 스크래핑 능력, 더 포괄적인 소셜 미디어 지원, UI 인터페이스 및 원클릭 설치 패키지 — 배포 불필요!

https://github.com/user-attachments/assets/57f8569c-e20a-4564-a669-1200d56c5725

🔥 **Pro 버전 판매 중**: https://shouxiqingbaoguan.com/

🌹 오늘부터 wiseflow 오픈소스 버전에 PR 기여(코드, 문서, 성공 사례 공유 모두 환영)가 채택되면, 기여자에게 wiseflow Pro 버전 1년 사용권이 증정됩니다!

## 🛡️ 라이선스

버전 4.2부터 오픈소스 라이선스를 업데이트했습니다. 자세한 내용은: [LICENSE](LICENSE)

상업적 협력 문의: **Email: zm.zhao@foxmail.com**

## 📬 연락처

질문이나 제안이 있으시면 [issue](https://github.com/TeamWiseFlow/wiseflow/issues)를 통해 메시지를 남겨주세요.

🎉 wiseflow && OFB에서 현재 **유료 지식 베이스**를 제공하고 있습니다. 내용에는 단계별 설치 튜토리얼, 각종 독점 활용 팁, **VIP 위챗 그룹**이 포함됩니다：

"掌柜的" 기업 위챗을 추가하여 문의하세요：

<img width="360" height="360" alt="wiseflow掌柜" src="https://github.com/user-attachments/assets/b013b3fd-546e-4176-b418-57bee419e761" />

🌹 오픈소스 유지에 응원해 주셔서 감사합니다!

## 🤝 wiseflow 5.x는 다음의 우수한 오픈소스 프로젝트를 기반으로 합니다:

- Patchright (Playwright 테스트 및 자동화 라이브러리의 탐지 우회 Python 버전) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- Feedparser (Python으로 피드 파싱) https://github.com/kurtmckee/feedparser
- SearXNG (다양한 검색 서비스와 데이터베이스에서 결과를 집계하는 무료 인터넷 메타 검색 엔진) https://github.com/searxng/searxng
- Wenyan (다중 플랫폼 Markdown 서식 및 게시 도구, 새 미디어 편집자 Crew가 wenyan-formatter 스킬을 통해 사용) https://github.com/caol64/wenyan

## Citation

본 프로젝트의 일부 또는 전체를 참조하거나 인용하는 경우, 다음 정보를 명시해 주세요:

```
Author: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## 파트너

[<img src="https://github.com/TeamWiseFlow/wiseflow/raw/4.x/docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)
