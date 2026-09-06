# 🌌 Continuum

> **Mobile-First Vibe Coding & Host Sandbox Orchestration Engine**  
> *Untether from your desk: Command AI development, inspect inline diffs, and approve changes seamlessly from your mobile device with full containerized host protection.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Android](https://img.shields.io/badge/Client-Kotlin%20Compose-3DDC84.svg)](mobile/README.md)
[![Docker Sandbox](https://img.shields.io/badge/Isolation-Docker%20Sandbox-2496ED.svg)](docker/)

---

## 🌐 Languages
- [English (Master)](README.md)
- [한국어 (Korean)](README.ko.md)
- [Bahasa Indonesia](README.id.md)

---

## 🌟 Vision & Core Philosophy

Traditional AI coding workflows require developers to stay glued to desktop IDEs, constantly typing prompts and reviewing thousands of lines of changes while risking host environment corruption.

**Continuum** breaks this limitation by introducing a **Deskless, Mobile-First Vibe Coding Architecture**:
1. **📱 Lean Mobile Client (Kotlin + Jetpack Compose)**: A lightweight, responsive chat interface designed for quick reviews and single-touch approvals.
2. **🔔 Asynchronous FCM Push Engine**: Triggers instant notifications when tasks require review or builds complete, allowing you to walk away from your desk.
3. **🔍 SkyBrain-Aligned 5-Lens Pre-Execution Review**: Analyzes user requests before code generation through 5 rigorous lenses (`CleanCode`, `Architecture`, `Security`, `Performance`, `AIConduct`).
4. **🌿 Atomic `ai/*` Git Branch Isolation on Managed Projects**: Never pollutes working branches; automatically spins up temporary task branches on the target repository and squash-merges upon approval.
5. **🐳 Docker Containerized Host Sandbox**: Executes builds, tests, and code modifications strictly within volume-mounted containers, keeping your host OS pristine.

---

## 🏛️ System Architecture

```
[ 📱 Mobile Client (Jetpack Compose) ]
             ▲
             │ FCM Push & REST/WebSocket
             ▼
[ ⚡ Host Vibe Server (FastAPI) ]
  ├── 🔍 5-Lens Reviewer (CleanCode / Arch / Sec / Perf / AIConduct)
  ├── 🌿 Target Repo Git Manager (ai/* branches & Squash Merge)
  ├── 🐳 Docker Sandbox Engine (Volume Mount Execution)
  └── 📑 Diff Inspector & Interactive Card Formatter
```

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.11+ & [`uv`](https://github.com/astral-sh/uv)
- Docker Desktop or Podman engine
- Android Studio (for mobile client development)

### 2. Server Installation & Execution
```bash
cd 01-production/continuum
make install
make run
```
The Vibe Server will start at `http://0.0.0.0:8080` with interactive API docs at `/docs`.

### 3. Running Verification Tests
```bash
make test
```

---

## 📜 License
MIT License. Distributed under the Open Source Governance standard.
