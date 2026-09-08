# 🌌 Continuum: Mobile-First Vibe Coding & Host Sandbox Engine

<div align="center">

<p align="center">
  <b>English</b> |
  <a href="README.ko.md">한국어</a> |
  <a href="README.id.md">Bahasa Indonesia</a>
</p>

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Android Client](https://img.shields.io/badge/Client-Kotlin%20Compose-3DDC84.svg)](mobile/README.md)
[![Quality: 5--Lens Guard](https://img.shields.io/badge/Quality-5--Lens%20Guardrail-success)](#-5-lens-quality-guardrail)
[![Isolation: Docker Sandbox](https://img.shields.io/badge/Isolation-Docker%20Sandbox-2496ED.svg)](docker/)

**Continuum** is an enterprise-grade, mobile-first Vibe Coding and host sandbox orchestration platform that untethers developers from their desks.

Command AI software development, inspect inline line-by-line diffs, evaluate 5-Lens quality reports, and approve code merges directly from your Android phone with containerized host OS protection.

[Why Continuum?](#-why-continuum-5-key-architectural-advantages) • [Release Status](#-release-status) • [Key Features](#-key-platform-features) • [System Architecture](#-system-architecture) • [Quick Start](#-quick-start) • [Governance](00-governance/)

</div>

---

## 💡 Why Continuum? (5 Key Architectural Advantages)

> **"Code anywhere, anytime. Walk away from your desk while autonomous AI agents implement features, run tests, and await your mobile one-click merge approval."**

| Key Advantage | Architectural Detail & Mechanism | Business & Engineering Impact |
| :--- | :--- | :--- |
| 📱 **Deskless Mobile Vibe Coding** | Native Android Jetpack Compose client with conversational chat UI, collapsible diff inspection, and single-touch `[Accept all]` squash merge approvals | Frees engineers from desktop confinement; review and merge code on the go with zero desktop dependency |
| 🛡️ **5-Lens Quality Guardrail** | Pre-flight and post-execution static evaluation across 5 lenses (`CleanCode`, `Architecture`, `Security`, `Performance`, `AIConduct`); blocks merge if score < 70 or checks fail | Automatically intercepts AI hallucinations, security vulnerabilities, and messy boilerplate before hitting `main` |
| 🌿 **Atomic `ai/*` Git Branch Sandbox** | Provisions dedicated task branches (`ai/{task_id}`) on managed project repositories; commits changes in sandbox and squash-merges only upon mobile approval | Zero working tree pollution; full reversibility and atomic rollback capability for every AI generation |
| ⚡ **Zero-Fake Multi-Turn Self-Healing** | Autonomous ReAct agent loop executing real test runners (`pytest`, `./gradlew test`) with compiler error feedback and honest 0-change reporting | Eliminates fabricated mock responses; guarantees that code is genuinely generated and verified against real suites |
| 🧠 **Hybrid Cloud + Local SLM Failover** | Antigravity / Gemini 3.7 Flash as high-performance primary engine, backed by on-device SkyBrain (Qwen 3.8 on Apple Metal) via 100ms circuit breaker | Ensures 100% operational uptime, $0 token offloading during network congestion, and air-gapped fallback reliability |

---

## 📊 Release Status

| Component | Version | Architecture | Status | Primary Highlights |
| :--- | :---: | :---: | :---: | :--- |
| 📱 **Mobile App (Android)** | `v0.1.0` | **Kotlin + Jetpack Compose** | **Production Stable** | Conversational UI, Diff Summary Card with +/- line counts, 5-Lens Quality Badges, One-Click Squash Merge |
| ⚡ **Host Vibe Server** | `v0.1.0` | **Python 3.11+ / FastAPI** | **Production Stable** | Multi-Turn ReAct Agent Loop, Git Workspace Manager, 5-Lens Diagnostics, SkyBrain Circuit Breaker |
| 🛡️ **5-Lens Guardrail** | `v0.1.0` | **Static & AST Analysis** | **Production Stable** | 70-Point Threshold Gatekeeper, Violation Explanations, Amber Warning Banners on Mobile |
| 🐳 **Execution Sandbox** | `v0.1.0` | **Docker / Host Isolated** | **Production Stable** | Volume-mounted isolated containers, automated test execution, process lifecycle guard |

---

## 🌟 Key Platform Features

### 📱 1. Mobile-First Vibe Coding Interface
- **Conversational Pair Programming**: Describe features, refactoring goals, or bug fixes in natural language.
- **Interactive Diff Card (`DiffSummaryCard`)**: Inspect modified files, line additions (`+N`), line deletions (`-N`), and file-type badges in real time.
- **Single-Touch Merge Gate**: Review the autonomous agent's test verification summary and tap `[Accept all]` to squash-merge into `main`, or `[Reject]` to discard the task branch.

### 🛡️ 2. 5-Lens Quality Threshold Guardrail
- Every AI-generated patch is rigorously audited across 5 specialized dimensions:
  1. **Clean Code**: Code readability, naming conventions, docstrings, and function size.
  2. **Architecture**: Domain boundary separation, single responsibility, and layer isolation.
  3. **Security**: Secret leakage prevention, input sanitization, and permission checks.
  4. **Performance**: Computational complexity, memory leaks, and redundant I/O.
  5. **AI Conduct**: Detection of fabricated mocks, hallucinated APIs, and silent exception swallowing.
- **Automated Rejection & Amber Warning**: If the composite score falls below 70.0 or any critical check fails, Continuum displays a visual `🛡️ Quality Guardrail Alert` banner and rejects automatic merging.

### 🌿 3. Atomic Git Task Isolation
- Never writes directly to `main` or your active working tree.
- Automatically branches to `ai/{task_id}`, executes inside an isolated sandbox, runs automated tests, and creates clean conventional commits.

### 🧠 4. Hybrid Cloud & On-Device SLM Routing
- Seamlessly interoperates with Google Gemini (`gemini-3.7-flash`, `gemini-2.5-flash`) and local on-device **SkyBrain** (Qwen 3.8 running on Apple Silicon Metal GPU).
- In the event of cloud rate limits (HTTP 429) or offline environments, requests automatically route to SkyBrain with zero cloud token consumption.

---

## 🏛️ System Architecture

```
[ 📱 Mobile Client (Android Jetpack Compose) ]
             ▲
             │ REST API & WebSocket / FCM Push
             ▼
[ ⚡ Host Vibe Server (FastAPI on Port 8080) ]
   ├── 🧠 Hybrid AI Router (Gemini 3.7 Flash ⇄ Local SkyBrain SLM)
   ├── 🤖 Autonomous Agent Loop (Multi-Turn ReAct with Tool Dispatch)
   ├── 🛡️ 5-Lens Quality Diagnostics (70-pt Threshold Gatekeeper)
   ├── 🌿 Git Workspace Manager (ai/* Task Branches & Squash Merge)
   └── 🐳 Docker Container Sandbox (Volume-Mounted Build & Test)
             │
             ▼
[ 📁 Target Repository / Managed Workspaces ]
   ├── Task Branch: ai/{task_id} (Isolated Execution & Test Verification)
   └── Main Branch: main (Protected, Merge upon Mobile Approval)
```

---

## 🚀 Quick Start

### 1. Prerequisites
- **Host OS**: macOS (Apple Silicon recommended) or Linux
- **Python**: 3.11+ with [`uv`](https://github.com/astral-sh/uv) installed
- **Docker Engine**: Docker Desktop or Podman (optional for pure host sandbox mode)
- **Android Device / Emulator**: Android 10+ (API 29+) for the mobile app

### 2. Host Server Setup & Launch
```bash
# Clone the repository
git clone https://github.com/cobuild-ai/Continuum.git
cd Continuum

# Install dependencies in isolated virtual environment
uv venv
source .venv/bin/activate
uv pip install -e .

# Launch Continuum Vibe Server
uvicorn vibe_server.main:app --host 0.0.0.0 --port 8080 --reload
```
The server will start at `http://0.0.0.0:8080` with Swagger documentation available at `http://localhost:8080/docs`.

### 3. Running Unit Tests & Verification
```bash
# Run backend pytest test suite (39 tests)
pytest -q

# Run preflight security and secret audit
python3 scripts/audit_secrets.py --target . --opensource
```

### 4. Mobile Client Installation
```bash
cd mobile
./gradlew assembleDebug

# Install on connected Android device via ADB
adb install -r app/build/outputs/apk/debug/app-debug.apk
```
Open the **Continuum** app on your phone, configure the Host IP (e.g. `192.168.1.xxx:8080`), and start vibe coding!

---

## 📁 Repository Structure

```
Continuum/
├── vibe_server/                 # Backend FastAPI Vibe Server
│   ├── agent/                   # Autonomous ReAct agent loop & workspace tools
│   ├── core/                    # AI engine client, config, models & 5-lens diagnostics
│   ├── notify/                  # FCM push notification dispatcher
│   └── sandbox/                 # Git workspace manager, test executor & synthesizer
├── mobile/                      # Android Client Application
│   └── app/src/main/java/.../
│       ├── data/                # Retrofit API services, models & preferences
│       └── ui/                  # Jetpack Compose screens (Chat, Diff, Settings)
├── tests/                       # Pytest unit & integration test suites
├── docker/                      # Sandbox container definitions
├── scripts/                     # Security linter & 3-tier governance automation
├── Makefile                     # Standard developer commands
├── README.md                    # English Master Documentation
├── README.ko.md                 # 한국어 가이드
└── README.id.md                 # Panduan Bahasa Indonesia
```

---

## 📜 License & Open Source Governance

Continuum is open-source software licensed under the **Apache License 2.0**. Distributed under the enterprise governance standards of [cobuild-ai](https://github.com/cobuild-ai).
