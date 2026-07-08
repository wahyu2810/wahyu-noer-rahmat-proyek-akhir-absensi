# 🖥️ Sistem Absensi Mahasiswa berbasis Face Recognition & PostgreSQL

Aplikasi Desktop Sistem Absensi Mahasiswa adalah platform manajemen kehadiran berbasis GUI (Tkinter) yang mengintegrasikan pengenalan wajah menggunakan OpenCV (Haar Cascade & LBPH Face Recognizer) dan penentuan lokasi geografis berbasis IP Geolocation (atau simulasi koordinat) dengan penyimpanan basis data **PostgreSQL**.

Sistem ini didesain dengan pembagian peran (*role-based*):
1. **Dosen**: Mengelola absensi mahasiswa, melakukan registrasi & pelatihan sampel wajah baru, memantau rekap absensi lengkap dengan koordinat lokasi presensi mahasiswa, dan mengekspor laporan absensi (CSV).
2. **Mahasiswa**: Melakukan absensi masuk/keluar dengan verifikasi wajah via Webcam dan validasi radius lokasi kampus.

---

## 🛠️ Fitur Utama

- **Login Multi-Role**: Pemisahan hak akses antara Dosen dan Mahasiswa.
- **Deteksi & Pengenalan Wajah**: Pendaftaran sampel wajah (20 foto) dan pelatihan model LBPH untuk pencocokan wajah secara *real-time* saat absensi.
- **Validasi Geografis (Radius Lokasi)**: Membatasi absensi hanya bisa dilakukan jika mahasiswa berada dalam radius aman (100 meter) dari titik koordinat kampus (UNU Indonesia Kampus B).
- **Auto-Update Status Kehadiran**: Penentuan status otomatis berdasarkan jam kehadiran (Hadir, Terlambat, Alfa).
- **Ekspor Laporan**: Memungkinkan dosen mengunduh data kehadiran dalam format `.csv`.
- **Integrasi PostgreSQL**: Penyimpanan data yang andal dan terpusat menggunakan server PostgreSQL (dikonfigurasi via variabel lingkungan).

---

## 📂 Struktur Direktori Proyek

```text
├── controllers/
│   └── controller_face.py        # Logika registrasi, pelatihan model, dan verifikasi wajah
├── models/
│   ├── model_absensi.py          # Entitas absensi, koneksi PostgreSQL, dan kalkulasi jarak lokasi
│   ├── model_users.py            # Entitas pengguna (Dosen & Mahasiswa)
│   └── simulation_state.py       # Pengaturan waktu & koordinat simulasi untuk testing
├── views/
│   ├── theme.py                  # Konfigurasi skema warna dan gaya UI (Modern Dark Mode)
│   ├── view_dosen_dashboard.py   # Tampilan menu & manajemen dosen
│   ├── view_login.py             # Tampilan halaman login
│   └── view_mahasiswa_dashboard.py # Tampilan menu & verifikasi absensi mahasiswa (Dua Baris Dinamis)
├── database.py                   # Inisialisasi awal skema basis data PostgreSQL & default data
├── main.py                       # Titik masuk utama aplikasi (Entrypoint)
├── test_app.py                   # Script check kesiapan environment dasar
├── haarcascade_frontalface_default.xml # Dataset deteksi wajah OpenCV
├── .env.example                  # Template konfigurasi variabel lingkungan basis data
└── .env                          # Konfigurasi basis data aktif (tidak disertakan di git)
```

---

## 🚀 Cara Menjalankan Project (Local Development)

### Prasyarat
* Python 3.10 atau versi terbaru.
* Server PostgreSQL aktif.
* Koneksi internet aktif (untuk IP Geolocation dan download Haar Cascade jika file hilang).

### Langkah-langkah Setup
1. **Buka Terminal / PowerShell** di direktori proyek ini.
2. **Aktifkan Virtual Environment (venv)**:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
   .\.venv\Scripts\Activate.ps1
   ```
3. **Instal Dependensi**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Konfigurasi Database (.env)**:
   * Salin file `.env.example` menjadi `.env`:
     ```powershell
     Copy-Item .env.example .env
     ```
   * Buka file `.env` dan isi sesuai kredensial server PostgreSQL Anda:
     ```env
     DB_HOST=localhost
     DB_PORT=5432
     DB_NAME=wahyu_absensi
     DB_USER=postgres
     DB_PASSWORD=password_anda
     ```
5. **Inisialisasi Database**:
   Jalankan perintah berikut untuk membuat tabel dan memasukkan data default:
   ```bash
   python database.py
   ```
6. **Jalankan Aplikasi Utama**:
   ```bash
   python main.py
   ```

*Gunakan kredensial default berikut untuk login:*
* **Dosen**: Username: `dosen1` | Password: `123456`
* **Mahasiswa 1**: Username: `mahasiswa1` | Password: `123456` (Nama: Wahyu Noer Rahmat)
* **Mahasiswa 2**: Username: `mahasiswa2` | Password: `123456` (Nama: Siti Nurhaliza)

---

## 📦 Cara Mem-build Project Menjadi File `.exe`

Gunakan **PyInstaller** untuk mengemas aplikasi menjadi file executable mandiri agar siap dijalankan tanpa perlu menginstal Python di komputer target.

### Langkah-langkah Build:
1. Pastikan virtual environment aktif.
2. Jalankan perintah PyInstaller menggunakan spec file yang telah disediakan:
   ```powershell
   python -m PyInstaller Sistem_Absensi.spec --noconfirm
   ```
3. Tunggu hingga proses selesai. Hasil build executable akan berada di folder **`dist/Sistem_Absensi.exe`**.

---

## 🏃‍♂️ Cara Menjalankan File `.exe` yang Sudah Dibuat

1. Masuk ke direktori **`dist/`** yang berada di dalam folder proyek Anda.
2. Salin berkas **`.env`** (konfigurasi database) dan **`haarcascade_frontalface_default.xml`** ke dalam folder **`dist/`** (sejajar dengan file `Sistem_Absensi.exe`).
3. Klik ganda (double-click) pada file **`Sistem_Absensi.exe`** untuk meluncurkan aplikasi.
4. Folder `faces/` (untuk menyimpan sampel foto pendaftaran wajah) akan dibuat otomatis secara portabel di folder yang sama saat pertama kali pendaftaran dilakukan.
