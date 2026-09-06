# 🌌 Continuum

> **Mesin Orkestrasi Vibe Coding Mobile-First & Sandbox Host**  
> *Bebas dari meja kerja: Kendalikan pengembangan AI, periksa perbedaan kode (diff) inline, dan setujui perubahan langsung dari perangkat seluler Anda dengan perlindungan lingkungan host berbasis kontainer secara penuh.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Android](https://img.shields.io/badge/Client-Kotlin%20Compose-3DDC84.svg)](mobile/README.md)
[![Docker Sandbox](https://img.shields.io/badge/Isolation-Docker%20Sandbox-2496ED.svg)](docker/)

---

## 🌐 Bahasa yang Didukung
- [English (Master)](README.md)
- [한국어 (Korean)](README.ko.md)
- [Bahasa Indonesia](README.id.md)

---

## 🌟 Visi & Filosofi Utama

Alur kerja pengkodean AI tradisional mengharuskan pengembang tetap berada di depan layar desktop, terus-menerus mengetik perintah dan meninjau ribuan baris kode dengan risiko merusak lingkungan host lokal.

**Continuum** memecahkan batasan ini dengan memperkenalkan **Arsitektur Vibe Coding Mobile-First Bebas Meja**:
1. **📱 Klien Seluler Ringan (Kotlin + Jetpack Compose)**: Antarmuka obrolan native yang dioptimalkan untuk pengambilan keputusan cepat dan persetujuan satu sentuhan.
2. **🔔 Mesin Notifikasi FCM Asinkron**: Mengirimkan notifikasi push seketika ke ponsel cerdas saat tugas memerlukan peninjauan atau kompilasi selesai.
3. **🔍 Tinjauan Kelayakan Pra-Eksekusi 5-Lensa Selaras SkyBrain**: Menganalisis persyaratan sebelum pembuatan kode melalui 5 lensa ketat (`CleanCode`, `Architecture`, `Security`, `Performance`, `AIConduct`).
4. **🌿 Isolasi Cabang Git Atomik `ai/*` pada Proyek Target**: Tidak pernah mengotori cabang kerja yang ada; secara otomatis membuat cabang tugas sementara pada repositori target dan melakukan Squash Merge setelah disetujui.
5. **🐳 Sandbox Host Kontainer Docker**: Menjalankan build dan pengujian dalam kontainer yang diisolasi dengan volume mount, menjaga sistem operasi host tetap bersih.

---

## 🏛️ Arsitektur Sistem

```
[ 📱 Klien Seluler (Jetpack Compose) ]
             ▲
             │ Notifikasi Push FCM & REST/WebSocket
             ▼
[ ⚡ Host Vibe Server (FastAPI) ]
  ├── 🔍 Peninjau 5-Lensa (CleanCode / Arch / Sec / Perf / AIConduct)
  ├── 🌿 Pengelola Git Proyek Target (Cabang ai/* & Squash Merge)
  ├── 🐳 Mesin Sandbox Docker (Eksekusi Terisolasi Volume Mount)
  └── 📑 Pemeriksa Diff & Pemformat Kartu Interaktif
```

---

## 🚀 Panduan Memulai Cepat

### 1. Persyaratan
- Python 3.11+ & [`uv`](https://github.com/astral-sh/uv)
- Docker Desktop atau mesin Podman
- Android Studio (untuk pengembangan klien seluler)

### 2. Pemasangan & Menjalankan Server
```bash
cd 01-production/continuum
make install
make run
```
Server akan berjalan di `http://0.0.0.0:8080` dengan dokumentasi API interaktif di `/docs`.

### 3. Menjalankan Pengujian Verifikasi
```bash
make test
```

---

## 📜 Lisensi
Lisensi MIT. Didistribusikan di bawah standar Tata Kelola Sumber Terbuka (Open Source Governance).
