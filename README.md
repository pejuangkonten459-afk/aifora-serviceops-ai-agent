# AIFORA ServiceOps AI Agent

**Project Code:** 01.AIFORA.10.26  
**Organization:** AIFORA AI ENGINEERING

ServiceOps AI Agent adalah asisten operasional berbasis FastAPI yang mencari panduan dari dokumen SOP lokal menggunakan retrieval-augmented generation (RAG).

## Fitur

- REST API untuk permintaan operasional.
- Penyimpanan data menggunakan SQLite.
- Pencarian dokumen SOP menggunakan ChromaDB lokal.
- Jawaban berdasarkan dokumen SOP beserta sumbernya.
- Fallback ketika informasi yang relevan tidak ditemukan.
- Dashboard web sederhana.
- Pengujian otomatis dengan pytest.

## Persyaratan

- Python yang kompatibel dengan dependensi proyek.
- Virtual environment `.venv`.
- Dependensi dalam `requirements.txt`.

## Menjalankan aplikasi

Aktifkan virtual environment jika belum aktif:

```powershell
.\.venv\Scripts\Activate.ps1
```

Pasang dependensi jika diperlukan:

```powershell
python -m pip install -r requirements.txt
```

Jalankan server dari direktori utama proyek:

```powershell
python -m uvicorn app.main:app --reload
```

Buka dashboard:

http://127.0.0.1:8000/dashboard

Dokumentasi API:

http://127.0.0.1:8000/docs

Health check:

http://127.0.0.1:8000/health

## Menjalankan pengujian

```powershell
python -m pytest -q
```

Baseline pengujian terakhir: **24 passed, 0 failed**.

## Struktur proyek

- `app/` — aplikasi FastAPI, layanan, database, dan RAG.
- `dashboard/` — antarmuka web.
- `data/` — database dan dokumen operasional lokal.
- `docs/` — dokumentasi tambahan.
- `scripts/` — skrip pendukung.
- `tests/` — pengujian otomatis.
- `requirements.txt` — dependensi Python.
- `.env.example` — contoh konfigurasi lingkungan.

## Batasan MVP

- Kualitas jawaban bergantung pada cakupan dan relevansi dokumen SOP.
- Fallback bukan jaminan bahwa semua pertanyaan di luar cakupan akan selalu terdeteksi.
- Pengujian lulus menunjukkan skenario yang diuji berhasil, bukan sertifikasi kesiapan produksi.
- Keamanan, autentikasi, observabilitas, dan deployment produksi perlu dievaluasi terpisah sebelum penggunaan enterprise.

---
AIFORA AI ENGINEERING
