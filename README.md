# Visualisasi ABD 8

Project visualisasi data warehouse untuk kebutuhan analisis bisnis dan pelaporan.

## Deskripsi

Project ini merupakan implementasi data warehouse dengan SQL dan visualisasi menggunakan Python. Sistem ini dirancang untuk mengumpulkan, menyimpan, dan menganalisis data bisnis secara terpusat.

## Struktur File

- **app_whr.py** - Aplikasi utama untuk visualisasi dan analisis data
- **config_whr.py** - Konfigurasi koneksi database dan pengaturan aplikasi
- **DDL_whr_v2.sql** - Data Definition Language (CREATE TABLE, schema definition)
- **DML_whr_v2.sql** - Data Manipulation Language (INSERT, UPDATE, sample data)
- **requirements.txt** - Daftar dependencies Python yang diperlukan

## Persyaratan

- Python 3.8+
- Database (sesuai konfigurasi di config_whr.py)
- Library yang terdaftar di requirements.txt

## Instalasi

1. Clone repository ini:
```bash
git clone https://github.com/RayhanIIqbal13/visualisasi-abd-8.git
cd visualisasi-abd-8
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Konfigurasi database:
   - Edit file `config_whr.py` sesuai dengan pengaturan database Anda

4. Buat schema dan tabel:
   - Jalankan script `DDL_whr_v2.sql` di database Anda

5. Masukkan data sample:
   - Jalankan script `DML_whr_v2.sql` di database Anda

## Penggunaan

Jalankan aplikasi dengan perintah:
```bash
python app_whr.py
```

## Fitur

- Koneksi database yang terpusat
- Visualisasi data interaktif
- Query dan analisis data warehouse
- Reporting dan dashboard

## Kontribusi

Untuk kontribusi, silakan buat pull request atau hubungi maintainer.

## Lisensi

Project ini dilisensikan di bawah MIT License.

## Penulis

Rayhan IIqbal

---

Last Updated: December 8, 2025
