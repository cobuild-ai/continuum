# 🌌 Continuum: Mesin Orkestrasi Vibe Coding Mobile-First & Sandbox Host

<div align="center">

<p align="center">
  <a href="README.md">English</a> |
  <a href="README.ko.md">한국어</a> |
  <b>Bahasa Indonesia</b>
</p>

[![Lisensi: MIT](https://img.shields.io/badge/Lisensi-MIT-blue.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Android Client](https://img.shields.io/badge/Klien-Kotlin%20Compose-3DDC84.svg)](mobile/README.md)
[![Kualitas: 5--Lens Guard](https://img.shields.io/badge/Kualitas-5--Lens%20Guardrail-success)](#-5-lensa-kualitas-guardrail)
[![Isolasi: Docker Sandbox](https://img.shields.io/badge/Isolasi-Docker%20Sandbox-2496ED.svg)](docker/)

**Continuum** adalah platform orkestrasi Vibe Coding dan sandbox host kelas enterprise berbasis mobile-first yang membebaskan pengembang dari keterikatan pada meja kerja.

Perintahkan pengembangan perangkat lunak AI, periksa perubahan kode baris demi baris (inline diff), evaluasi laporan kualitas 5 Lensa, dan setujui penggabungan kode (merge) langsung dari ponsel Android Anda dengan perlindungan sistem host terkontainerisasi.

[Mengapa Continuum?](#-mengapa-continuum-5-keunggulan-arsitektur-utama) • [Status Rilis](#-status-rilis) • [Fitur Utama](#-fitur-utama-platform) • [Arsitektur Sistem](#-arsitektur-sistem) • [Panduan Cepat](#-panduan-cepat-quick-start) • [Tata Kelola](00-governance/)

</div>

---

## 💡 Mengapa Continuum? (5 Keunggulan Arsitektur Utama)

> **"Koding di mana saja, kapan saja. Tinggalkan meja kerja Anda saat agen AI otonom mengimplementasikan fitur, menjalankan pengujian, dan menunggu persetujuan penggabungan satu sentuhan di ponsel Anda."**

| Keunggulan Utama | Detail & Mekanisme Arsitektur | Dampak Bisnis & Rekayasa |
| :--- | :--- | :--- |
| 📱 **Vibe Coding Mobile Bebas Meja** | Klien native Android Jetpack Compose dengan antarmuka percakapan, inspeksi diff yang dapat diciutkan, dan persetujuan penggabungan squash `[Accept all]` sekali sentuh | Membebaskan pengembang dari ketergantungan desktop; tinjau dan gabungkan kode di perjalanan tanpa hambatan |
| 🛡️ **Guardrail Kualitas 5 Lensa** | Evaluasi statis pra dan pasca eksekusi melalui 5 lensa (`CleanCode`, `Architecture`, `Security`, `Performance`, `AIConduct`); memblokir penggabungan jika skor < 70 atau pengujian gagal | Mencegah halusinasi AI, kerentanan keamanan, dan kode boilerplate berantakan masuk ke cabang `main` |
| 🌿 **Isolasi Cabang Git Atomik `ai/*`** | Menyediakan cabang tugas khusus (`ai/{task_id}`) pada repositori proyek yang dikelola; melakukan komit dalam sandbox dan melakukan squash-merge hanya setelah persetujuan ponsel | Menjamin pohon kerja (working tree) bersih dari polusi; kemampuan rollback atomik untuk setiap generasi AI |
| ⚡ **Protokol Tanpa Kepalsuan (Zero-Fake)** | Siklus agen ReAct otonom yang mengeksekusi runner pengujian nyata (`pytest`, `./gradlew test`) dengan umpan balik kesalahan kompilasi dan pelaporan jujur 0-perubahan | Menghilangkan respons tiruan palsu; menjamin bahwa kode benar-benar dibuat dan diverifikasi terhadap suite uji nyata |
| 🧠 **Failover Hibrida Cloud + SLM Lokal** | Antigravity / Gemini 3.7 Flash sebagai mesin utama berkinerja tinggi, didukung oleh SkyBrain lokal (Qwen 3.8 pada Apple Metal) melalui circuit breaker 100ms | Memastikan waktu operasional 100%, pengalihan beban token $0 saat jaringan padat, dan keandalan fallback offline |

---

## 📊 Status Rilis

| Komponen | Versi | Arsitektur | Status | Sorotan Utama |
| :--- | :---: | :---: | :---: | :--- |
| 📱 **Aplikasi Mobile (Android)** | `v0.1.0` | **Kotlin + Jetpack Compose** | **Stabil Produksi** | UI Percakapan, Kartu Ringkasan Diff (+/- baris), Lencana Kualitas 5 Lensa, Squash Merge Satu Ketukan |
| ⚡ **Server Host Vibe** | `v0.1.0` | **Python 3.11+ / FastAPI** | **Stabil Produksi** | Siklus Agen ReAct Multi-Putaran, Manajer Git Workspace, Diagnostik 5 Lensa, Circuit Breaker SkyBrain |
| 🛡️ **Guardrail 5 Lensa** | `v0.1.0` | **Analisis Statis & AST** | **Stabil Produksi** | Gatekeeper Ambang Batas 70 Poin, Penjelasan Pelanggaran, Spanduk Peringatan Amber di Ponsel |
| 🐳 **Sandbox Eksekusi** | `v0.1.0` | **Docker / Host Terisolasi** | **Stabil Produksi** | Kontainer terisolasi dengan volume mount, eksekusi pengujian otomatis, pelindung siklus proses |

---

## 🌟 Fitur Utama Platform

### 📱 1. Antarmuka Vibe Coding Mobile-First
- **Pair Programming Percakapan**: Jelaskan fitur baru, perbaikan bug, atau refaktor menggunakan bahasa alami.
- **Kartu Diff Interaktif (`DiffSummaryCard`)**: Periksa file yang diubah, penambahan baris (`+N`), pengurangan baris (`-N`), dan lencana jenis file secara real time.
- **Pintu Persetujuan Satu Sentuhan**: Tinjau ringkasan verifikasi pengujian agen dan ketuk `[Accept all]` untuk melakukan squash-merge ke `main`, atau `[Reject]` untuk membuang cabang tugas.

### 🛡️ 2. Guardrail Ambang Kualitas 5 Lensa
- Setiap patch yang dibuat AI diaudit secara ketat melalui 5 dimensi spesialisasi:
  1. **Clean Code**: Keterbacaan kode, konvensi penamaan, docstring, dan ukuran fungsi.
  2. **Architecture**: Pemisahan batas domain, tanggung jawab tunggal, dan isolasi dependensi.
  3. **Security**: Pencegahan kebocoran rahasia, sanitasi input, dan pemeriksaan izin.
  4. **Performance**: Kompleksitas waktu, pencegahan kebocoran memori, dan I/O yang tidak perlu.
  5. **AI Conduct**: Deteksi tiruan hardcoded palsu, penggunaan API palsu, dan penekanan pengecualian diam-diam.
- **Penolakan Otomatis & Peringatan Amber**: Jika skor rata-rata di bawah 70.0 atau pemeriksaan penting gagal, spanduk visual `🛡️ Quality Guardrail Alert` akan muncul di ponsel dan menolak penggabungan otomatis.

### 🌿 3. Isolasi Tugas Git Atomik
- Tidak pernah menulis langsung ke cabang `main` atau ruang kerja aktif Anda.
- Secara otomatis mencabangkan ke `ai/{task_id}`, menjalankan pengujian dalam lingkungan terisolasi, dan membuat komit konvensional yang bersih.

### 🧠 4. Perutean Hibrida Cloud & SLM On-Device
- Beroperasi mulus dengan Google Gemini (`gemini-3.7-flash`, `gemini-2.5-flash`) dan **SkyBrain** lokal (Qwen 3.8 berbasis akselerasi GPU Metal Apple Silicon).
- Jika batas kuota cloud tercapai (HTTP 429), permintaan secara otomatis dialihkan ke SkyBrain dalam 100ms tanpa biaya token cloud.

---

## 🏛️ Arsitektur Sistem

```
[ 📱 Klien Mobile (Android Jetpack Compose) ]
             ▲
             │ REST API & WebSocket / FCM Push
             ▼
[ ⚡ Server Host Vibe (FastAPI pada Port 8080) ]
   ├── 🧠 Perute AI Hibrida (Gemini 3.7 Flash ⇄ SLM SkyBrain Lokal)
   ├── 🤖 Siklus Agen Otonom (Multi-Turn ReAct dengan Tool Dispatch)
   ├── 🛡️ Diagnostik Kualitas 5 Lensa (Gatekeeper Ambang Batas 70 Poin)
   ├── 🌿 Manajer Git Workspace (Cabang Tugas ai/* & Squash Merge)
   └── 🐳 Sandbox Kontainer Docker (Build & Uji Terisolasi)
             │
             ▼
[ 📁 Repositori Target / Ruang Kerja yang Dikelola ]
   ├── Cabang Tugas: ai/{task_id} (Eksekusi Terisolasi & Verifikasi Uji)
   └── Cabang Utama: main (Terlindungi, Gabungkan hanya setelah Persetujuan)
```

---

## 🚀 Panduan Cepat (Quick Start)

### 1. Prasyarat
- **Sistem Operasi Host**: macOS (direkomendasikan Apple Silicon) atau Linux
- **Python**: 3.11+ dengan [`uv`](https://github.com/astral-sh/uv) terinstal
- **Mesin Docker**: Docker Desktop atau Podman (opsional untuk mode sandbox host murni)
- **Perangkat / Emulator Android**: Android 10+ (API 29+)

### 2. Penyiapan & Menjalankan Server Host
```bash
# Kloning repositori
git clone https://github.com/cobuild-ai/Continuum.git
cd Continuum

# Buat virtual environment dan pasang dependensi
uv venv
source .venv/bin/activate
uv pip install -e .

# Jalankan Server Vibe Continuum
uvicorn vibe_server.main:app --host 0.0.0.0 --port 8080 --reload
```
Server akan berjalan di `http://0.0.0.0:8080` dengan dokumentasi Swagger di `http://localhost:8080/docs`.

### 3. Menjalankan Pengujian Unit & Verifikasi
```bash
# Jalankan rangkaian pengujian pytest backend (39 tes)
pytest -q

# Jalankan audit keamanan dan deteksi kebocoran rahasia
python3 scripts/audit_secrets.py --target . --opensource
```

### 4. Memasang Klien Mobile
```bash
cd mobile
./gradlew assembleDebug

# Pasang ke perangkat Android fisik via ADB
adb install -r app/build/outputs/apk/debug/app-debug.apk
```
Buka aplikasi **Continuum** di ponsel Anda, atur IP Host (misalnya `192.168.1.xxx:8080`), dan mulailah vibe coding!

---

## 📜 Lisensi & Tata Kelola Sumber Terbuka

Continuum adalah perangkat lunak sumber terbuka di bawah lisensi **MIT License**. Dikelola secara transparan di bawah standar tata kelola enterprise [cobuild-ai](https://github.com/cobuild-ai).
