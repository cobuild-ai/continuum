# 📱 Continuum Mobile Client (Android)

> **Kotlin + Jetpack Compose 기반의 린(Lean) 네이티브 모바일 코딩 뷰어**  
> *PC 앞을 벗어나 손안에서 AI 개발 상태를 확인하고, 인라인 카드 터치로 Diff를 검토하여 원터치로 최종 머지를 승인하는 경량 클라이언트*

---

## 🏛️ 아키텍처 개요

```
[ 📱 Android Client ]
  ├── ui/
  │    ├── chat/ (채팅 뷰어 & 프롬프트 입력)
  │    ├── cards/ (4-Lens 요약 카드 & Diff 요약 카드)
  │    └── diff/ (풀스크린 인터랙티브 Diff 뷰어)
  ├── network/
  │    ├── ContinuumApiService.kt (Retrofit / Ktor REST)
  │    └── SseStreamClient.kt (OkHttp SSE 실시간 로그 수신)
  └── fcm/
       └── ContinuumFirebaseMessagingService.kt (백그라운드 푸시 & 딥링크)
```

---

## 💡 화면 및 UX 컴포넌트 규격

### 1. 💬 Chat Screen (`ui/chat/ChatScreen.kt`)
- 대화형 린(Lean) 뷰어로 사용자 요청(프롬프트) 전송
- 서버로부터 수신한 상태 업데이트를 인라인 카드로 렌더링

### 2. 🎴 Inline Action Cards (`ui/cards/`)
- **`LensEvaluationCard`**:
  - 4개 렌즈 점수 배지(Arch, Eng, Sec, Hardcode) 표시
  - 점수 70점 이상 시 녹색 배지, 미달 시 경고 배지 및 권고안 펼치기
  - [승인하고 샌드박스 시작] / [수정 요청] 원터치 버튼
- **`DiffSummaryCard`**:
  - 변경 파일 개수, `+추가 / -삭제` 라인 요약
  - 카드 탭 시 `DiffViewerScreen`으로 풀스크린 전환

### 3. 📑 Fullscreen Diff Viewer (`ui/diff/DiffViewerScreen.kt`)
- 모바일 화면에 최적화된 구문 강조(Syntax Highlighting) 및 좌우/상하 스크롤 뷰어
- 상단 고정 바: `ai/<task-id>` ➔ `main` 브랜치 타깃 표시
- 하단 플로팅 액션 바: **[🚀 원터치 Squash Merge 승인]** / **[❌ 거절 및 브랜치 폐기]**

---

## 🔔 FCM 푸시 알림 및 딥링크 규격

| 액션 타입 (`action_type`) | 알림 제목 | 본문 내용 | 딥링크 목적지 |
| :--- | :--- | :--- | :--- |
| `DESIGN_APPROVAL` | 🔍 4-Lens 사전 검토 완료 | 4대 렌즈 평가 점수: N/100점. 설계안 검토 요청 | `continuum://tasks/{task_id}/design` |
| `MERGE_APPROVAL` | ✨ 샌드박스 빌드/테스트 완료 | N개 파일 변경 (+A, -D). 머지 승인 대기 | `continuum://tasks/{task_id}/diff` |
| `VIEW_ERROR` | ❌ 작업 실행 실패 | 오류 원인 및 로그 확인 | `continuum://tasks/{task_id}/error` |

---

## 🚀 통신 규격 (Vibe Server 연동)
- **Base URL**: `http://<HOST_IP>:8080/api/v1`
- **인증**: Local Bearer Token / Tailscale 사설망 지원
