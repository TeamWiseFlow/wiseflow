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

더욱 놀라운 것은, 초기 실험과 탐색을 통해 wiseflow의 데이터 수집 능력을 "플러그인" 형태로 openclaw에 통합하면 위에서 언급한 두 가지 한계를 완벽하게 해결할 수 있다는 것을 발견했습니다. 앞으로 흥미진진한 실제 데모 영상을 순차적으로 공개하고, 이 "플러그인"들을 오픈소스로 릴리스할 예정입니다.

다만, openclaw의 플러그인 시스템은 우리가 전통적으로 이해하는 "플러그인"(Claude Code의 플러그인과 유사한 것)과는 다르기 때문에, "add-on"이라는 개념을 별도로 도입해야 했습니다. 정확히 말하면, wiseflow 5.x는 openclaw add-on 형태로 제공됩니다. 원래 openclaw에는 "add-on" 아키텍처가 없지만, 실제로는 몇 가지 간단한 셸 명령어만으로 이 "개조"를 완료할 수 있습니다. 또한 실제 비즈니스 시나리오를 위한 프리셋 설정이 포함된 즉시 사용 가능한 openclaw 강화 버전인 [openclaw_for_business](https://github.com/TeamWiseFlow/openclaw_for_business)도 준비했습니다. 클론한 후 wiseflow 릴리스를 openclaw_for_business의 add-on 폴더에 배치하면 됩니다.

## 🌟 빠른 시작

이 디렉토리를 openclaw_for_business의 `addons/` 디렉토리에 복사하세요:

```bash
# 방법 1: wiseflow 저장소에서 클론
git clone https://github.com/TeamWiseFlow/wiseflow.git /tmp/wiseflow
cp -r /tmp/wiseflow/addon <openclaw_for_business>/addons/wiseflow

# 방법 2: 이미 wiseflow 저장소가 있는 경우
https://github.com/TeamWiseFlow/wiseflow/releases 에서 최신 릴리스를 다운로드
압축 해제 후 <openclaw_for_business>/addons 에 배치
```

설치 후 openclaw를 재시작하면 적용됩니다.

## 디렉토리 구조

```
addon/
├── addon.json                    # 메타데이터
├── overrides.sh                  # pnpm overrides: playwright-core → patchright-core
├── patches/
│   └── 001-browser-tab-recovery.patch  # 탭 복구 패치
├── skills/
│   └── browser-guide/SKILL.md    # 브라우저 사용 모범 사례
├── docs/                         # 기술 문서
│   ├── anti-detection-research.md
│   └── openclaw-extension-architecture.md
└── tests/                        # 테스트 케이스 및 스크립트
    ├── README.md
    └── run-managed-tests.mjs
```

## WiseFlow Pro 버전 출시!

더 강력한 스크래핑 능력, 더 포괄적인 소셜 미디어 지원, UI 인터페이스 및 원클릭 설치 패키지 — 배포 불필요!

https://github.com/user-attachments/assets/57f8569c-e20a-4564-a669-1200d56c5725

🔥 **Pro 버전 판매 중**: https://shouxiqingbaoguan.com/

🌹 오늘부터 wiseflow 오픈소스 버전에 PR 기여(코드, 문서, 성공 사례 공유 모두 환영)가 채택되면, 기여자에게 wiseflow Pro 버전 1년 사용권이 증정됩니다!

📥 🎉 📚

## 🛡️ 라이선스

버전 4.2부터 오픈소스 라이선스를 업데이트했습니다. 자세한 내용은: [LICENSE](LICENSE)

상업적 협력 문의: **Email: zm.zhao@foxmail.com**

## 📬 연락처

질문이나 제안이 있으시면 [issue](https://github.com/TeamWiseFlow/wiseflow/issues)를 통해 메시지를 남겨주세요.

Pro 버전 관련 요구사항이나 협력 피드백은 WeChat으로 연락해 주세요:

<img src="docs/wechat.jpg" alt="wechat" width="360">

## 🤝 wiseflow 5.x는 다음의 우수한 오픈소스 프로젝트를 기반으로 합니다:

- Patchright (Playwright 테스트 및 자동화 라이브러리의 탐지 우회 Python 버전) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- Feedparser (Python으로 피드 파싱) https://github.com/kurtmckee/feedparser
- SearXNG (다양한 검색 서비스와 데이터베이스에서 결과를 집계하는 무료 인터넷 메타 검색 엔진) https://github.com/searxng/searxng

## Citation

본 프로젝트의 일부 또는 전체를 참조하거나 인용하는 경우, 다음 정보를 명시해 주세요:

```
Author: Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## 파트너

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)
