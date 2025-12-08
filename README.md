# Visualisasi ABD 8

Project visualisasi data warehouse untuk kebutuhan analisis bisnis dan pelaporan World Happiness Report.

## 🌐 Live Demo

Dashboard sudah di-deploy di Streamlit Cloud dan dapat diakses di:
**[https://visualisasi-abd-8-5n8fkqxmjxha2p45cgz78x.streamlit.app/](https://visualisasi-abd-8-5n8fkqxmjxha2p45cgz78x.streamlit.app/)**

## Deskripsi

Project ini merupakan implementasi data warehouse dengan SQL dan visualisasi menggunakan Python. Sistem ini dirancang untuk mengumpulkan, menyimpan, dan menganalisis data **World Happiness Report** dari 175+ negara tahun 2015-2024 secara terpusat dengan dashboard interaktif.

### Fitur Utama Dashboard:
- 🌐 **Region** - Analisis data regional dengan peta interaktif
- 🗺️ **Country** - Choropleth map dan statistik per negara
- 😊 **Happiness Report** - Ranking dan distribusi skor kebahagiaan
- 💰 **Economic Indicator** - Analisis GDP dan hubungannya dengan kebahagiaan
- 👥 **Social Indicator** - Indikator sosial (dukungan sosial, harapan hidup, kebebasan)
- 🤝 **Perception Indicator** - Analisis generosity dan persepsi korupsi

## Struktur File

- **app_whr.py** - Aplikasi utama Streamlit untuk visualisasi dan analisis data
- **config_whr.py** - Konfigurasi koneksi Supabase dan database queries
- **DDL_whr_v2.sql** - Data Definition Language (CREATE TABLE, schema definition)
- **DML_whr_v2.sql** - Data Manipulation Language (INSERT, sample data)
- **requirements.txt** - Daftar dependencies Python yang diperlukan
- **supabase.toml** - Konfigurasi Supabase
- **.env.example** - Template file environment variables

## Persyaratan

- Python 3.8+
- Supabase PostgreSQL Database (cloud-based)
- Library yang terdaftar di requirements.txt

## Instalasi Lokal

### 1. Clone Repository
```bash
git clone https://github.com/RayhanIIqbal13/visualisasi-abd-8.git
cd visualisasi-abd-8
```

### 2. Setup Environment Variables
```bash
# Copy .env.example ke .env
cp .env.example .env

# Edit .env dengan credential Supabase Anda
# SUPABASE_HOST=your_host
# SUPABASE_PORT=5432
# SUPABASE_DB=postgres
# SUPABASE_USER=postgres.your_project_id
# SUPABASE_PASSWORD=your_password
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Jalankan Dashboard Lokal
```bash
streamlit run app_whr.py
```

Dashboard akan terbuka di `http://localhost:8501`

## Deployment ke Streamlit Cloud

### 1. Push ke GitHub
```bash
git add .
git commit -m "Update untuk deployment"
git push origin main
```

### 2. Deploy ke Streamlit Cloud
1. Buka https://streamlit.io/cloud
2. Sign in dengan GitHub account
3. Click "New app"
4. Pilih repository: `visualisasi-abd-8`
5. Main file path: `app_whr.py`
6. Click "Deploy"

### 3. Setup Secrets di Streamlit Cloud
Di Streamlit Cloud dashboard:
1. Buka app settings
2. Klik "Secrets"
3. Paste environment variables:
```
SUPABASE_HOST=your_host
SUPABASE_PORT=5432
SUPABASE_DB=postgres
SUPABASE_USER=postgres.your_project_id
SUPABASE_PASSWORD=your_password
SUPABASE_URL=your_url
SUPABASE_API_KEY=your_api_key
```

## Tech Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Supabase PostgreSQL
- **Visualisasi**: Plotly Express, Plotly Graph Objects
- **Maps**: Folium, Streamlit-folium
- **Data Processing**: Pandas, NumPy

## Database Schema

### Dimension Tables:
- `region` - Wilayah geografis dunia
- `country` - Negara-negara dunia

### Fact Tables:
- `happiness_report` - Skor dan ranking kebahagiaan per tahun
- `economic_indicator` - GDP per capita
- `social_indicator` - Social support, life expectancy, freedom
- `perception_indicator` - Generosity, perception of corruption

## API Endpoints / Database Functions

Semua queries didefinisikan di `config_whr.py`. Contoh:
- `get_happiness_report_by_year(year)` - Data happiness per tahun
- `get_economic_indicators_by_year(year)` - Economic data per tahun
- `get_global_happiness_statistics()` - Statistik global
- `get_countries_by_region(region_id)` - Countries di region tertentu

## Troubleshooting

### Error: "Database connection failed"
- Pastikan credential Supabase di `.env` sudah benar
- Check apakah Supabase database sudah aktif
- Verify password dan format user: `postgres.PROJECT_ID`

### Error: "Module not found"
```bash
pip install -r requirements.txt
```

### Port sudah terpakai
```bash
streamlit run app_whr.py --server.port 8502
```

## Kontribusi

Untuk kontribusi:
1. Fork repository
2. Buat branch feature: `git checkout -b feature/nama-fitur`
3. Commit changes: `git commit -m "Add: deskripsi fitur"`
4. Push ke branch: `git push origin feature/nama-fitur`
5. Buat Pull Request

## Lisensi

Project ini dilisensikan di bawah **MIT License**.

## Penulis

**Rayhan IIqbal**
- GitHub: [@RayhanIIqbal13](https://github.com/RayhanIIqbal13)

## Changelog

### Version 2.0 (Current)
- ✅ Migrated dari local PostgreSQL ke Supabase Cloud
- ✅ Added 8 interactive dashboard pages
- ✅ Implemented Streamlit Cloud deployment
- ✅ Added Folium choropleth maps
- ✅ Complete data visualization with Plotly

### Version 1.0
- Initial release dengan basic dashboard

---

**Last Updated:** December 8, 2025  
**Status:** ✅ Live on Streamlit Cloud
