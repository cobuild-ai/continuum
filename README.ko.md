# 🌌 Continuum: 모바일 퍼스트 Vibe Coding & 호스트 샌드박스 오케스트레이션 엔진

<div align="center">

<p align="center">
  <a href="README.md">English</a> |
  <b>한국어</b> |
  <a href="README.id.md">Bahasa Indonesia</a>
</p>

[![라이선스: Apache 2.0](https://img.shields.io/badge/라이선스-Apache%202.0-blue.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/프레임워크-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Android Client](https://img.shields.io/badge/클라이언트-Kotlin%20Compose-3DDC84.svg)](mobile/README.md)
[![Quality: 5--Lens Guard](https://img.shields.io/badge/품질-5대%20렌즈%20가드레일-success)](#-5대-렌즈-품질-가드레일)
[![Isolation: Docker Sandbox](https://img.shields.io/badge/격리-Docker%20샌드박스-2496ED.svg)](docker/)

**Continuum**은 개발자가 데스크톱 책상에 묶여 있지 않고 어디서나 자율 AI 코딩을 지휘할 수 있도록 설계된 엔터프라이즈급 **모바일 퍼스트 Vibe Coding 및 호스트 샌드박스 오케스트레이션 플랫폼**입니다.

Android 스마트폰에서 실시간 대화로 AI 기능 구현을 지시하고, 파일별/라인별 인라인 Diff를 검토하며, 5대 렌즈 정적 분석 리포트를 확인한 후 원클릭으로 안전하게 머지 승인할 수 있습니다.

[Why Continuum?](#-why-continuum-5대-아키텍처-핵심-장점) • [릴리즈 상태](#-릴리즈-상태) • [핵심 기능](#-핵심-플랫폼-기능) • [시스템 아키텍처](#-시스템-아키텍처) • [빠른 시작](#-빠른-시작-quick-start) • [거버넌스](00-governance/)

</div>

---

## 💡 Why Continuum? (5대 아키텍처 핵심 장점)

> **"언제 어디서나 코딩하세요. AI 에이전트가 기능을 작성하고 테스트를 돌리는 동안 자리를 비우고, 모바일에서 원클릭으로 검토 및 머지를 승인하세요."**

| 핵심 장점 | 아키텍처 세부 메커니즘 | 비즈니스 및 엔지니어링 임팩트 |
| :--- | :--- | :--- |
| 📱 **탈-데스크톱 모바일 Vibe Coding** | 네이티브 Android Jetpack Compose 클라이언트로 대화형 UI, 접이식 인라인 Diff 검사, 원터치 `[Accept all]` 스쿼시 머지 승인 제공 | 데스크톱 IDE에 종속되지 않고 이동 중이나 휴식 중에도 스마트폰으로 온전한 코드 리뷰 및 배포 완결 |
| 🛡️ **5대 렌즈 품질 가드레일** | 사전 및 사후 5대 렌즈(`CleanCode`, `Architecture`, `Security`, `Performance`, `AIConduct`) 정적 분석; 70점 미만 또는 취약점 검출 시 머지 자동 차단 | AI 할루시네이션, 보안 결함, 조잡한 보일러플레이트 코드가 `main` 브랜치에 유입되는 것을 물리적으로 원천 차단 |
| 🌿 **원자적 `ai/*` Git 브랜치 격리** | 관리 대상 저장소에 전용 작업 브랜치(`ai/{task_id}`)를 자동 생성하고 샌드박스 내에서 커밋 후 모바일 승인 시에만 스쿼시 머지 | 작업 트리 및 로컬 워킹 디렉토리 무오염 보장; 모든 AI 코드 생성 단위로 완벽한 롤백(Revert) 추적성 확보 |
| ⚡ **가짜 응답 절대 금지 (Zero Fake Protocol)** | 실제 테스트 러너(`pytest`, `./gradlew test`)와 컴파일러 피드백을 수반하는 다회차 자율 에이전트 루프 및 실측 파일 변경(0개 정직 보고) 준수 | 가짜 모의 성공 응답을 완전 배제하고, 실제 테스트를 통과한 검증된 코드만 프로덕션에 안전하게 통합 |
| 🧠 **하이브리드 클라우드 + 온디바이스 SLM 페일오버** | 고성능 Antigravity / Gemini 3.7 Flash를 1순위로 사용하며, 네트워크 지연 시 로컬 SkyBrain (Qwen 3.8 on Apple Metal)으로 100ms 서킷 브레이커 자동 전환 | 네트워크 혼잡 시 $0 로컬 토큰 오프로딩을 실현하고, 오프라인 환경에서도 무중단 코드 어시스턴스 보장 |

---

## 📊 릴리즈 상태

| 컴포넌트 | 버전 | 아키텍처 | 상태 | 주요 핵심 내용 |
| :--- | :---: | :---: | :---: | :--- |
| 📱 **모바일 앱 (Android)** | `v0.1.0` | **Kotlin + Jetpack Compose** | **상용 안정 (Stable)** | 대화형 UI, 라인별 가감 뱃지(+/-) Diff Summary Card, 5대 렌즈 품질 뱃지, 원클릭 스쿼시 머지 |
| ⚡ **호스트 Vibe 서버** | `v0.1.0` | **Python 3.11+ / FastAPI** | **상용 안정 (Stable)** | 다회차 ReAct 자율 에이전트 루프, Git Workspace 매니저, 5대 렌즈 진단 엔진, SkyBrain 서킷 브레이커 |
| 🛡️ **5대 렌즈 가드레일** | `v0.1.0` | **정적 및 AST 분석** | **상용 안정 (Stable)** | 70점 기준 품질 게이트키퍼, 위반 사유 분석 보고, 모바일 Amber 경고 배너 |
| 🐳 **실행 샌드박스** | `v0.1.0` | **Docker / Host 격리** | **상용 안정 (Stable)** | 볼륨 마운트 컨테이너 실행, 자동화 테스트 검증, 프로세스 라이프사이클 보호 |

---

## 🌟 핵심 플랫폼 기능

### 📱 1. 모바일 퍼스트 Vibe Coding 인터페이스
- **대화형 페어 프로그래밍**: 자연어로 새로운 기능, 리팩토링 목표, 버그 수정을 요청합니다.
- **인터랙티브 Diff 카드 (`DiffSummaryCard`)**: 수정된 파일 목록, 추가 라인 수(`+N`), 삭제 라인 수(`-N`), 언어별 색상 뱃지를 실시간으로 확인합니다.
- **원터치 머지 게이트**: 에이전트의 자동화 테스트 검증 결과를 확인하고 `[Accept all]` 버튼을 눌러 `main` 브랜치에 스쿼시 머지하거나, `[Reject]` 버튼으로 즉시 폐기할 수 있습니다.

### 🛡️ 2. 5대 렌즈 품질 임계치 가드레일 (`check_quality_threshold`)
- 생성된 모든 패치는 아래의 5대 전문 렌즈를 통해 엄격히 정적 진단됩니다:
  1. **Clean Code**: 코드 가독성, 명명 규칙, 독스트링 및 함수 크기.
  2. **Architecture**: 도메인 경계 분리, 단일 책임 원칙, 계층 간 의존성 격리.
  3. **Security**: 시크릿 유출 방지, 입력값 세니타이징, 권한 검증.
  4. **Performance**: 시간 복잡도, 메모리 누수 방지, 불필요한 입출력.
  5. **AI Conduct**: 가짜 모의 하드코딩 검출, 날조된 API 사용 방지, 침묵하는 예외 억제 감지.
- **자동 거부 및 Amber 경고 배너**: 종합 점수가 70.0점 미만이거나 주요 점검 항목이 탈락한 경우, 모바일 화면 상단에 `🛡️ Quality Guardrail Alert` 배너를 띄우고 위험한 머지를 사전에 방지합니다.

### 🌿 3. 원자적 Git 작업 격리
- 호스트의 작업 중인 워킹 트리나 `main` 브랜치에 절대 직접 쓰지 않습니다.
- 자동으로 `ai/{task_id}` 브랜치로 분기하여 격리된 환경에서 테스트를 거친 후 정석 커밋을 생성합니다.

### 🧠 4. 하이브리드 클라우드 및 온디바이스 SLM 라우팅
- Google Gemini (`gemini-3.7-flash`, `gemini-2.5-flash`) 및 Apple Silicon Metal GPU 가속 기반의 로컬 온디바이스 **SkyBrain** (Qwen 3.8)과 매끄럽게 상호 운용됩니다.
- 클라우드 할당량 초과(HTTP 429) 시 100ms 이내에 로컬 SkyBrain으로 자동 전환되어 과금 없이 오프로딩 처리됩니다.

---

## 🏛️ 시스템 아키텍처

```
[ 📱 모바일 클라이언트 (Android Jetpack Compose) ]
             ▲
             │ REST API & WebSocket / FCM 푸시 알림
             ▼
[ ⚡ 호스트 Vibe 서버 (포트 8080 FastAPI) ]
   ├── 🧠 하이브리드 AI 라우터 (Gemini 3.7 Flash ⇄ Local SkyBrain SLM)
   ├── 🤖 자율 에이전트 루프 (다회차 ReAct 도구 디스패치)
   ├── 🛡️ 5대 렌즈 품질 진단 (70점 임계치 품질 게이트키퍼)
   ├── 🌿 Git 워크스페이스 매니저 (ai/* 브랜치 격리 및 스쿼시 머지)
   └── 🐳 Docker 컨테이너 샌드박스 (볼륨 마운트 빌드 & 테스트)
             │
             ▼
[ 📁 관리 대상 저장소 / 워크스페이스 ]
   ├── 태스크 브랜치: ai/{task_id} (격리 실행 및 테스트 검증)
   └── 메인 브랜치: main (보호 브랜치, 모바일 승인 시에만 머지)
```

---

## 🚀 빠른 시작 (Quick Start)

### 1. 사전 요구사항
- **호스트 OS**: macOS (Apple Silicon 권장) 또는 Linux
- **Python**: 3.11+ 및 [`uv`](https://github.com/astral-sh/uv)
- **Docker Engine**: Docker Desktop 또는 Podman (호스트 모드 실행 시 선택사항)
- **Android 디바이스 / 에뮬레이터**: Android 10+ (API 29+)

### 2. 호스트 서버 셋업 및 기동
```bash
# 저장소 클론
git clone https://github.com/cobuild-ai/continuum.git
cd Continuum

# 가상환경 생성 및 패키지 설치
uv venv
source .venv/bin/activate
uv pip install -e .

# Continuum Vibe 서버 실행
uvicorn vibe_server.main:app --host 0.0.0.0 --port 8080 --reload
```
서버는 `http://0.0.0.0:8080`에서 시작되며, `http://localhost:8080/docs`에서 Swagger API 문서를 확인할 수 있습니다.

### 3. 단위 테스트 및 보안 감사
```bash
# 백엔드 Pytest 테스트 스위트 실행 (39개 테스트)
pytest -q

# 사전 보안 및 시크릿 감사
python3 scripts/audit_secrets.py --target . --opensource
```

### 4. 모바일 클라이언트 빌드 및 설치
```bash
cd mobile
./gradlew assembleDebug

# ADB를 통해 연결된 Android 실기기에 설치
adb install -r app/build/outputs/apk/debug/app-debug.apk
```
스마트폰에서 **Continuum** 앱을 열고 호스트 IP(예: `192.168.1.xxx:8080`)를 설정한 후 바이브 코딩을 시작하세요!

---

## 📜 라이선스 및 오픈소스 거버넌스

Continuum은 **Apache License 2.0** 하에 배포되는 오픈소스 소프트웨어입니다. [cobuild-ai](https://github.com/cobuild-ai)의 엔터프라이즈 거버넌스 표준에 따라 투명하게 관리됩니다.
