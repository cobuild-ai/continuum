# 🌌 Continuum

> **모바일 퍼스트 바이브 코딩 & 호스트 샌드박스 오케스트레이션 엔진**  
> *책상을 벗어나 스마트폰으로 AI 개발을 지휘하고, 인라인 Diff 검토와 원터치 승인으로 안전하게 코드를 완성하는 무결점 개발 환경*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Android](https://img.shields.io/badge/Client-Kotlin%20Compose-3DDC84.svg)](mobile/README.md)
[![Docker Sandbox](https://img.shields.io/badge/Isolation-Docker%20Sandbox-2496ED.svg)](docker/)

---

## 🌐 지원 언어
- [English (Master)](README.md)
- [한국어 (Korean)](README.ko.md)
- [Bahasa Indonesia](README.id.md)

---

## 🌟 비전 및 핵심 철학

기존의 AI 코딩 워크플로는 개발자가 책상 앞 모니터에 얽매여 계속 프롬프트를 입력하고 수천 줄의 코드 변경을 감시해야 하며, 로컬 호스트 환경이 오염될 위험을 감수해야 했습니다.

**Continuum**은 **\"탈(脫) 데스크 & 손안의 바이브 코딩(Deskless Vibe Coding)\"** 아키텍처를 통해 이 한계를 혁신합니다:
1. **📱 린(Lean) 모바일 클라이언트 (Kotlin + Jetpack Compose)**: 복잡한 입력 없이 빠른 의사결정과 원터치 승인에 최적화된 경량 네이티브 채팅 뷰어.
2. **🔔 비동기 FCM 푸시 엔진**: 샌드박스 빌드가 완료되거나 검토가 필요할 때 스마트폰으로 즉시 푸시 알림을 전송하여 자유로운 이동 보장.
3. **🔍 SkyBrain 연계 5대 렌즈(5-Lens) 사전 타당성 검토**: 코드 생성 전 클린코드(`CleanCode`), 클린아키텍처(`Architecture`), 보안(`Security`), 성능(`Performance`), AI 수행규범(`AIConduct`) 관점에서 요구사항을 정밀 사전 검토.
4. **🌿 관리 대상 프로젝트의 원자적 `ai/*` Git 임시 브랜치 격리**: 개발자가 작업 중인 대상 프로젝트의 브랜치를 오염시키지 않고 임시 격리 분기 후, 승인 완료 시에만 깔끔하게 Squash Merge 적용.
5. **🐳 Docker 컨테이너 격리 샌드박스**: 프로젝트 디렉토리 볼륨 마운트 기반으로 빌드와 테스트를 격리 수행하여 호스트 OS 환경을 완벽하게 보호.

---

## 🏛️ 시스템 아키텍처

```
[ 📱 모바일 클라이언트 (Jetpack Compose) ]
             ▲
             │ FCM 푸시 알림 & REST/WebSocket
             ▼
[ ⚡ 호스트 Vibe Server (FastAPI) ]
  ├── 🔍 5대 렌즈 사전 분석기 (CleanCode / Arch / Sec / Perf / AIConduct)
  ├── 🌿 대상 프로젝트 Git 관리자 (ai/* 브랜치 격리 & Squash Merge)
  ├── 🐳 Docker 샌드박스 엔진 (볼륨 마운트 격리 빌드/테스트)
  └── 📑 Diff 검사기 및 대화형 카드 포맷터
```

---

## 🚀 빠른 시작 가이드

### 1. 사전 요구사항
- Python 3.11+ 및 [`uv`](https://github.com/astral-sh/uv)
- Docker Desktop 또는 Podman 엔진
- Android Studio (모바일 클라이언트 빌드 시)

### 2. Vibe Server 설치 및 실행
```bash
cd 01-production/continuum
make install
make run
```
서버는 기본적으로 `http://0.0.0.0:8080`에서 실행되며, `/docs`를 통해 OpenAPI 스펙 및 인터랙티브 테스트가 가능합니다.

### 3. 검증 테스트 실행
```bash
make test
```

---

## 📜 라이선스
MIT License. 오픈소스 거버넌스 표준에 따라 배포됩니다.
