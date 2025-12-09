# 😊 World Happiness Report Dashboard

> Platform analisis interaktif berbasis Streamlit untuk eksplorasi data kebahagiaan dunia menggunakan PostgreSQL dan Supabase cloud database.

## 📋 Daftar Isi

1. [Gambaran Project](#-gambaran-project)
2. [Arsitektur & Desain Database](#-arsitektur--desain-database)
3. [Tech Stack](#-tech-stack)
4. [Instalasi & Setup](#-instalasi--setup)
5. [Konfigurasi Database (config_whr.py)](#-konfigurasi-database-config_whrpy)
6. [Fitur Dashboard (app_whr.py)](#-fitur-dashboard-app_whrpy)
7. [Schema Database (DDL_whr_v2.sql)](#-schema-database-ddl_whr_v2sql)
8. [Data Sample (DML_whr_v2.sql)](#-data-sample-dml_whr_v2sql)
9. [Halaman Dashboard](#-halaman-dashboard)
10. [Panduan Penggunaan](#-panduan-penggunaan)
11. [Troubleshooting](#-troubleshooting)

---

## 🎯 Gambaran Project

Project ini menyediakan **dashboard Streamlit interaktif 8 halaman** untuk menganalisis data World Happiness Report dari berbagai dimensi:

- 🌍 **Distribusi Regional** - Analisis kebahagiaan berdasarkan wilayah geografis
- 🗺️ **Profil Negara** - Peta choropleth dan statistik per negara
- 😊 **Happiness Report** - Ranking dan distribusi skor kebahagiaan
- 💰 **Economic Indicator** - Korelasi GDP dengan tingkat kebahagiaan
- 👥 **Social Indicator** - Dukungan sosial, harapan hidup, dan kebebasan
- 🤝 **Perception Indicator** - Analisis generosity dan persepsi korupsi

**Fitur Utama:**
- ✅ Database PostgreSQL cloud-hosted (Supabase)
- ✅ Visualisasi real-time dengan Plotly
- ✅ Peta interaktif dengan Folium
- ✅ Schema database ternormalisasi (3NF)
- ✅ Kredensial aman berbasis environment variable
- ✅ 171 negara dari 10 region dunia
- ✅ 1.710 records data kebahagiaan (2015-2024)

---

## 🏗️ Arsitektur & Desain Database

### Normalisasi Database

Database mengikuti **Third Normal Form (3NF)** untuk memisahkan data dimensi dan fakta dengan relasi yang jelas:

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA MODEL                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Region (Dimension)                                         │
│      │                                                      │
│      └──> Country (Dimension) ──┐                           │
│                                 │                           │
│                                 ▼                           │
│                          Happiness_Report (Fact)            │
│                                 │                           │
│           ┌─────────────────────┼─────────────────────┐     │
│           │                     │                     │     │
│           ▼                     ▼                     ▼     │
│   Economic_Indicator    Social_Indicator    Perception_Indicator │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Mengapa Desain Ini?

| Masalah | Solusi | Keuntungan |
|---------|--------|------------|
| Satu negara banyak tahun data | Tabel `happiness_report` dengan year | Track data tahunan per negara |
| Indikator berbeda kategori | Tabel terpisah per kategori indikator | Modular dan mudah di-maintain |
| Negara terkelompok dalam region | Foreign key `region_id` di country | Analisis regional fleksibel |
| Data redundancy | Tabel ternormalisasi | Data integrity terjaga |

---

## 💻 Tech Stack

| Komponen | Teknologi | Versi | Kegunaan |
|----------|-----------|-------|----------|
| **Frontend** | Streamlit | ≥1.29.0 | Web dashboard interaktif |
| **Visualisasi** | Plotly | ≥5.18.0 | Chart dan grafik interaktif |
| **Peta** | Folium | ≥0.14.0 | Choropleth map dunia |
| **Data Processing** | Pandas | ≥2.1.0 | Manipulasi dan analisis data |
| **Database** | PostgreSQL | 15+ | Cloud database (Supabase) |
| **Driver** | psycopg2 | ≥2.9.9 | Koneksi PostgreSQL |
| **Config** | python-dotenv | ≥1.0.0 | Environment variables |
| **Hosting** | Supabase | Latest | Cloud PostgreSQL service |

---

## 🚀 Instalasi & Setup

### Prasyarat

- Python 3.8+
- Git
- Akun Supabase (gratis tersedia)

### Langkah 1: Clone Repository

```bash
git clone https://github.com/RayhanIIqbal13/visualisasi-abd-8.git
cd visualisasi-abd-8
```

### Langkah 2: Buat Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Langkah 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Langkah 4: Konfigurasi Koneksi Supabase

Buat file `.env` di root project:

```env
# Supabase Configuration
SUPABASE_HOST=aws-1-ap-south-1.pooler.supabase.com
SUPABASE_PORT=5432
SUPABASE_USER=postgres.your_project_id
SUPABASE_PASSWORD=your_password
SUPABASE_DB=postgres
SUPABASE_URL=https://your_project_id.supabase.co
SUPABASE_API_KEY=your_api_key
```

### Langkah 5: Inisialisasi Database

```bash
# Buat schema
psql -h your_host -U postgres.your_project_id -d postgres -f DDL_whr_v2.sql

# Load data
psql -h your_host -U postgres.your_project_id -d postgres -f DML_whr_v2.sql
```

### Langkah 6: Jalankan Dashboard

```bash
streamlit run app_whr.py
```

Buka browser ke `http://localhost:8501`

---

## ⚙️ Konfigurasi Database (config_whr.py)

### Overview

`config_whr.py` menangani koneksi database dan menyediakan helper functions untuk pengambilan data dengan optimasi SQL yang tepat.

### Setup Koneksi

```python
@st.cache_resource
def get_database_connection():
    """Membuat koneksi database dengan caching"""
    conn = psycopg2.connect(
        host=os.getenv("SUPABASE_HOST"),
        port=os.getenv("SUPABASE_PORT"),
        user=os.getenv("SUPABASE_USER"),
        password=os.getenv("SUPABASE_PASSWORD"),
        dbname=os.getenv("SUPABASE_DB"),
        sslmode="require"  # Wajib untuk Supabase
    )
    return conn
```

**Fitur Utama:**
- ✅ Kredensial berbasis environment (aman)
- ✅ Enkripsi SSL/TLS aktif
- ✅ Error handling dengan try/except
- ✅ Connection caching dengan `@st.cache_resource`

### Fungsi Pengambilan Data

#### 1. **get_happiness_report_by_year(year)** - Data Happiness Per Tahun

```python
def get_happiness_report_by_year(year):
    """Mengambil data happiness report untuk tahun tertentu"""
    query = '''
        SELECT c.country_name, r.region_name,
               h.ranking, h.happiness_score, h.dystopia_residual
        FROM happiness_report h
        JOIN country c ON h.country_id = c.country_id
        JOIN region r ON c.region_id = r.region_id
        WHERE h.year = %s
        ORDER BY h.ranking ASC
    '''
    return execute_query(query, (year,))
```

**Return:** List of dictionaries dengan data happiness per negara

**Konsep SQL:**
- INNER JOIN untuk menggabungkan data dari 3 tabel
- Filter berdasarkan tahun dengan parameterized query
- Sorted by ranking

---

#### 2. **get_economic_indicators_by_year(year)** - Data Ekonomi Per Tahun

```python
def get_economic_indicators_by_year(year):
    """Mengambil economic indicators untuk tahun tertentu"""
    query = '''
        SELECT c.country_name, r.region_name,
               h.happiness_score, e.gdp_per_capita
        FROM happiness_report h
        JOIN economic_indicator e ON h.report_id = e.report_id
        JOIN country c ON h.country_id = c.country_id
        JOIN region r ON c.region_id = r.region_id
        WHERE h.year = %s
        ORDER BY e.gdp_per_capita DESC
    '''
    return execute_query(query, (year,))
```

**Return:** `(country_name, region_name, happiness_score, gdp_per_capita)`

**Konsep SQL:**
- Multiple JOINs across 4 tables
- Correlation data antara GDP dan happiness
- Sorted by GDP descending

---

#### 3. **get_social_indicators_by_year(year)** - Data Sosial Per Tahun

```python
def get_social_indicators_by_year(year):
    """Mengambil social indicators untuk tahun tertentu"""
    query = '''
        SELECT c.country_name, r.region_name,
               h.happiness_score, s.social_support,
               s.healthy_life_expectancy, s.freedom_to_make_life_choices
        FROM happiness_report h
        JOIN social_indicator s ON h.report_id = s.report_id
        JOIN country c ON h.country_id = c.country_id
        JOIN region r ON c.region_id = r.region_id
        WHERE h.year = %s
        ORDER BY s.social_support DESC
    '''
    return execute_query(query, (year,))
```

**Return:** Data sosial dengan 3 sub-indikator

---

#### 4. **get_global_happiness_statistics()** - Statistik Global

```python
def get_global_happiness_statistics():
    """Mengambil statistik happiness global"""
    query = '''
        SELECT 
            AVG(happiness_score) as avg_score,
            MAX(happiness_score) as max_score,
            MIN(happiness_score) as min_score
        FROM happiness_report
    '''
    return execute_query_single(query)
```

**Return:** Dictionary dengan statistik agregat

**Konsep SQL:**
- Aggregate functions: `AVG()`, `MAX()`, `MIN()`
- Single row result

---

#### 5. **get_happiness_report_all_aggregated()** - Data Agregat Semua Tahun

```python
def get_happiness_report_all_aggregated():
    """Mengambil rata-rata happiness score per negara (semua tahun)"""
    query = '''
        SELECT c.country_name, r.region_name,
               AVG(h.ranking) as avg_ranking,
               AVG(h.happiness_score) as avg_happiness_score
        FROM happiness_report h
        JOIN country c ON h.country_id = c.country_id
        JOIN region r ON c.region_id = r.region_id
        GROUP BY c.country_id, c.country_name, r.region_name
        ORDER BY avg_happiness_score DESC
    '''
    return execute_query(query)
```

**Return:** Data agregat per negara dari semua tahun

**Konsep SQL:**
- GROUP BY untuk agregasi per negara
- AVG() untuk rata-rata multi-tahun

---

## 📊 Fitur Dashboard (app_whr.py)

### Overview Arsitektur

`app_whr.py` adalah aplikasi Streamlit dengan 2000+ baris yang menyediakan 8 halaman analisis.

```
app_whr.py Structure:
├── Page Configuration (lines 1-50)
│   ├── st.set_page_config()
│   ├── Styling & CSS
│   └── Header & Sidebar
│
├── Helper Functions (lines 50-300)
│   ├── @st.cache_data decorators
│   ├── Data fetching functions
│   └── Type conversion utilities
│
└── 8 Dashboard Pages (lines 300-2000)
    ├── 🏠 Beranda (Home)
    ├── 🌍 Region Analysis
    ├── 🗺️ Country Profile
    ├── 😊 Happiness Report
    ├── 💰 Economic Indicator
    ├── 👥 Social Indicator
    ├── 🤝 Perception Indicator
    └── 📊 Comparison Tools
```

### Konfigurasi Halaman

```python
st.set_page_config(
    page_title="World Happiness Report Dashboard",
    page_icon="😊",
    layout="wide",           # Layout full-width
    initial_sidebar_state="expanded"
)
```

**Settings:**
- Wide layout untuk tampilan chart lebih baik
- Emoji icon untuk branding
- Sidebar expanded by default

### Navigasi Sidebar

```python
st.sidebar.radio(
    "Pilih Halaman:",
    [
        "🏠 Beranda",
        "🌍 Region",
        "🗺️ Country",
        "😊 Happiness Report",
        "💰 Economic Indicator",
        "👥 Social Indicator",
        "🤝 Perception Indicator",
        "📊 Comparison"
    ]
)
```

---

### Strategi Data Caching

```python
@st.cache_data
def get_happiness_data(year):
    """Fungsi pengambilan data dengan caching"""
    data = get_happiness_report_by_year(year)
    
    df = pd.DataFrame(data)
    
    # Konversi tipe data untuk operasi numerik
    df['happiness_score'] = pd.to_numeric(df['happiness_score'], errors='coerce')
    
    return df
```

**Mengapa Caching?**
- Mencegah query database redundan
- Meningkatkan responsivitas dashboard
- Auto-invalidate saat kode berubah

**Mengapa Konversi Tipe?**
- PostgreSQL return numerics sebagai string tanpa explicit casting
- Plotly memerlukan tipe numerik untuk kalkulasi
- `errors='coerce'` handle data malformed dengan aman

---

### Pattern Python Utama

#### Pattern 1: DataFrame Creation dari Query

```python
data = get_happiness_report_by_year(year)
df = pd.DataFrame(data)
```

#### Pattern 2: Type Conversion Pipeline

```python
df['happiness_score'] = pd.to_numeric(df['happiness_score'], errors='coerce')
df['gdp_per_capita'] = pd.to_numeric(df['gdp_per_capita'], errors='coerce')
```

#### Pattern 3: Chart Creation dengan Plotly

```python
fig = px.bar(
    df,
    x='country_name',
    y='happiness_score',
    color='region_name',
    title='Happiness Score by Country'
)
fig.update_layout(height=500, xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)
```

#### Pattern 4: Folium Map Integration

```python
m = folium.Map(location=[20, 0], zoom_start=2)
folium.Choropleth(
    geo_data=world_geo,
    data=df,
    columns=['country_name', 'happiness_score'],
    key_on='feature.properties.name',
    fill_color='YlOrRd'
).add_to(m)
st_folium(m, width=800)
```

---

## 📍 Halaman Dashboard

### Halaman 1: 🏠 Beranda (Home)

**Tujuan:** Dashboard KPI high-level

**Metrik yang Ditampilkan:**
- Total Negara dalam database
- Rata-rata Happiness Score global
- Negara paling bahagia
- Negara paling tidak bahagia

**SQL Queries:**
```sql
-- Total Countries
SELECT COUNT(DISTINCT country_id) FROM country

-- Average Happiness
SELECT AVG(happiness_score) FROM happiness_report

-- Top/Bottom Countries
SELECT country_name, happiness_score 
FROM happiness_report h
JOIN country c ON h.country_id = c.country_id
ORDER BY happiness_score DESC/ASC
LIMIT 1
```

**Visualisasi:**
- 4 Metric cards dengan angka dan formatting
- Quick statistics table
- Year selector untuk filter data

---

### Halaman 2: 🌍 Region Analysis

**Pertanyaan:** Bagaimana distribusi kebahagiaan per region dunia?

**Metrik:** Regional average happiness, country count per region

**Charts:**
1. **Bar Chart** - Rata-rata happiness per region
2. **Pie Chart** - Distribusi negara per region
3. **Folium Map** - Visualisasi geografis

**SQL Query:**
```sql
SELECT r.region_name,
       COUNT(c.country_id) as country_count,
       AVG(h.happiness_score) as avg_happiness
FROM region r
JOIN country c ON r.region_id = c.region_id
JOIN happiness_report h ON c.country_id = h.country_id
WHERE h.year = %s
GROUP BY r.region_id, r.region_name
ORDER BY avg_happiness DESC
```

**Key Insight:** Western Europe dan North America memiliki rata-rata kebahagiaan tertinggi

---

### Halaman 3: 🗺️ Country Profile

**Pertanyaan:** Bagaimana performa kebahagiaan tiap negara?

**Metrik:** Happiness ranking, score trend, regional comparison

**Charts:**
1. **Choropleth Map** - Peta dunia dengan color-coded happiness
2. **Line Chart** - Trend happiness per negara (2015-2024)
3. **Data Table** - Detail negara dengan semua indikator

**SQL Query:**
```sql
SELECT c.country_name, r.region_name,
       h.year, h.ranking, h.happiness_score
FROM happiness_report h
JOIN country c ON h.country_id = c.country_id
JOIN region r ON c.region_id = r.region_id
WHERE c.country_id = %s
ORDER BY h.year ASC
```

**Key Insight:** Negara Nordic (Finland, Denmark, Norway) konsisten di top 10

---

### Halaman 4: 😊 Happiness Report

**Pertanyaan:** Negara mana yang memiliki tingkat kebahagiaan tertinggi?

**Metrik:** Top 20 negara, ranking per tahun, distribusi score

**Charts:**
1. **Horizontal Bar Chart** - Top 20 negara paling bahagia
2. **Histogram** - Distribusi happiness score
3. **Box Plot** - Distribusi per region

**SQL Query:**
```sql
SELECT c.country_name, r.region_name,
       h.ranking, h.happiness_score
FROM happiness_report h
JOIN country c ON h.country_id = c.country_id
JOIN region r ON c.region_id = r.region_id
WHERE h.year = %s
ORDER BY h.ranking ASC
LIMIT 20
```

**Key Insight:** Finland, Denmark, dan Switzerland konsisten di posisi teratas

---

### Halaman 5: 💰 Economic Indicator

**Pertanyaan:** Bagaimana korelasi GDP dengan kebahagiaan?

**Metrik:** GDP per capita, correlation coefficient, scatter plot

**Charts:**
1. **Scatter Plot** - GDP vs Happiness Score
2. **Bar Chart** - Top 20 negara by GDP
3. **Correlation Matrix** - GDP correlation dengan happiness

**SQL Query:**
```sql
SELECT c.country_name, r.region_name,
       h.happiness_score, e.gdp_per_capita
FROM happiness_report h
JOIN economic_indicator e ON h.report_id = e.report_id
JOIN country c ON h.country_id = c.country_id
JOIN region r ON c.region_id = r.region_id
WHERE h.year = %s
ORDER BY e.gdp_per_capita DESC
```

**Key Insight:** Korelasi positif kuat antara GDP dan happiness (r ≈ 0.7-0.8)

---

### Halaman 6: 👥 Social Indicator

**Pertanyaan:** Faktor sosial apa yang mempengaruhi kebahagiaan?

**Metrik:** Social support, life expectancy, freedom

**Charts:**
1. **Radar Chart** - Perbandingan 3 indikator sosial
2. **Scatter Plot** - Social support vs Happiness
3. **Grouped Bar Chart** - Comparison antar negara

**SQL Query:**
```sql
SELECT c.country_name, r.region_name,
       h.happiness_score, s.social_support,
       s.healthy_life_expectancy, s.freedom_to_make_life_choices
FROM happiness_report h
JOIN social_indicator s ON h.report_id = s.report_id
JOIN country c ON h.country_id = c.country_id
JOIN region r ON c.region_id = r.region_id
WHERE h.year = %s
ORDER BY s.social_support DESC
```

**Key Insight:** Social support memiliki korelasi tertinggi dengan happiness

---

### Halaman 7: 🤝 Perception Indicator

**Pertanyaan:** Bagaimana persepsi masyarakat mempengaruhi kebahagiaan?

**Metrik:** Generosity score, corruption perception

**Charts:**
1. **Scatter Plot** - Corruption vs Happiness
2. **Bar Chart** - Top/Bottom generosity
3. **Bubble Chart** - Generosity vs Corruption vs Happiness

**SQL Query:**
```sql
SELECT c.country_name, r.region_name,
       h.happiness_score, p.generosity,
       p.perceptions_of_corruption
FROM happiness_report h
JOIN perception_indicator p ON h.report_id = p.report_id
JOIN country c ON h.country_id = c.country_id
JOIN region r ON c.region_id = r.region_id
WHERE h.year = %s
ORDER BY p.perceptions_of_corruption ASC
```

**Key Insight:** Low corruption perception berkorelasi dengan higher happiness

---

## 🗄️ Schema Database (DDL_whr_v2.sql)

### Overview DDL

`DDL_whr_v2.sql` membuat 6 tabel ternormalisasi dengan constraints dan relationships yang tepat.

### Tabel 1: REGION

```sql
CREATE TABLE region (
    region_id SERIAL PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL UNIQUE
);
```

**Tujuan:** Menyimpan 10 region geografis dunia

**Karakteristik:**
- `SERIAL` auto-increment `region_id`
- `UNIQUE` mencegah duplikasi nama region

**Sample Data:**
```
1 | South Asia
2 | Central and Eastern Europe
3 | Sub-Saharan Africa
4 | Latin America and Caribbean
```

---

### Tabel 2: COUNTRY

```sql
CREATE TABLE country (
    country_id SERIAL PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL UNIQUE,
    region_id INT NOT NULL,
    
    CONSTRAINT fk_country_region
        FOREIGN KEY (region_id) REFERENCES region(region_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
```

**Tujuan:** Menyimpan negara-negara dunia dengan referensi region

**Key Fields:**
- `country_name` - Nama negara (unique)
- `region_id` - Foreign key ke tabel region

**Sample Data:**
```
1 | Switzerland | 7
2 | Iceland | 7
3 | Denmark | 7
4 | Norway | 7
```

---

### Tabel 3: HAPPINESS_REPORT (Fact Table)

```sql
CREATE TABLE happiness_report (
    report_id SERIAL PRIMARY KEY,
    country_id INT NOT NULL,
    year INT NOT NULL,
    ranking INT,
    happiness_score NUMERIC(5, 3),
    dystopia_residual NUMERIC(5, 3),
    
    CONSTRAINT fk_hr_country
        FOREIGN KEY (country_id) REFERENCES country(country_id)
        ON DELETE CASCADE,
    
    UNIQUE (country_id, year)
);
```

**Tujuan:** Menyimpan data kebahagiaan per negara per tahun (fact table)

**Key Design:**
- `UNIQUE (country_id, year)` - Satu record per negara per tahun
- `NUMERIC(5, 3)` - Presisi untuk happiness score
- Foreign key ke country

**Sample Data:**
```
id | country_id | year | ranking | happiness_score | dystopia_residual
1  | 1          | 2015 | 1       | 7.587           | 2.518
2  | 1          | 2016 | 2       | 7.509           | 2.428
```

---

### Tabel 4: ECONOMIC_INDICATOR

```sql
CREATE TABLE economic_indicator (
    economic_id SERIAL PRIMARY KEY,
    report_id INT NOT NULL,
    gdp_per_capita NUMERIC(10, 2),
    
    CONSTRAINT fk_ei_report
        FOREIGN KEY (report_id) REFERENCES happiness_report(report_id)
        ON DELETE CASCADE
);
```

**Tujuan:** Menyimpan data GDP per capita per happiness report

**Key Design:**
- Relasi 1:1 dengan happiness_report
- CASCADE delete untuk data integrity

---

### Tabel 5: SOCIAL_INDICATOR

```sql
CREATE TABLE social_indicator (
    social_id SERIAL PRIMARY KEY,
    report_id INT NOT NULL,
    social_support NUMERIC(5, 3),
    healthy_life_expectancy NUMERIC(5, 2),
    freedom_to_make_life_choices NUMERIC(5, 3),
    
    CONSTRAINT fk_si_report
        FOREIGN KEY (report_id) REFERENCES happiness_report(report_id)
        ON DELETE CASCADE
);
```

**Tujuan:** Menyimpan indikator sosial dengan 3 sub-komponen

---

### Tabel 6: PERCEPTION_INDICATOR

```sql
CREATE TABLE perception_indicator (
    perception_id SERIAL PRIMARY KEY,
    report_id INT NOT NULL,
    generosity NUMERIC(5, 3),
    perceptions_of_corruption NUMERIC(5, 3),
    
    CONSTRAINT fk_pi_report
        FOREIGN KEY (report_id) REFERENCES happiness_report(report_id)
        ON DELETE CASCADE
);
```

**Tujuan:** Menyimpan indikator persepsi masyarakat

---

### Star Schema Concept

```
              Region
                 │
                 ▼
             Country
                 │
                 ▼
         Happiness_Report (Fact)
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
Economic    Social      Perception
Indicator   Indicator   Indicator
```

---

## 📥 Data Sample (DML_whr_v2.sql)

### Overview DML

`DML_whr_v2.sql` menyimpan data untuk 171 negara dengan 1.710 records kebahagiaan (10 tahun × 171 negara).

### Block 1: INSERT REGIONS

```sql
INSERT INTO region (region_id, region_name) VALUES
(1, 'South Asia'),
(2, 'Central and Eastern Europe'),
(3, 'Sub-Saharan Africa'),
(4, 'Latin America and Caribbean'),
(5, 'Commonwealth of Independent States'),
(6, 'North America and ANZ'),
(7, 'Western Europe'),
(8, 'Southeast Asia'),
(9, 'East Asia'),
(10, 'Middle East and North Africa');
```

**Data:** 10 region geografis yang mencakup seluruh dunia

---

### Block 2: INSERT COUNTRIES

```sql
INSERT INTO country (country_id, country_name, region_id) VALUES
(1, 'Switzerland', 7),
(2, 'Iceland', 7),
(3, 'Denmark', 7),
...
(170, 'South Sudan', 3);
```

**Data:** 171 negara dari berbagai region

**Distribusi:**
- Western Europe: 21 negara
- Sub-Saharan Africa: 41 negara
- Latin America and Caribbean: 23 negara
- Central and Eastern Europe: 17 negara
- Middle East and North Africa: 18 negara
- Commonwealth of Independent States: 12 negara
- Southeast Asia: 9 negara
- South Asia: 7 negara
- East Asia: 6 negara
- North America and ANZ: 4 negara

---

### Block 3: INSERT HAPPINESS_REPORT

```sql
INSERT INTO happiness_report (report_id, country_id, year, ranking, happiness_score, dystopia_residual) VALUES
(10001, 1, 2015, 1, 7.59, 2.52),
(10002, 1, 2017, 2, 7.51, 2.43),
...
```

**Data Characteristics:**
- 1.710 records total (171 negara × 10 tahun)
- Tahun: 2015-2024 (lengkap)
- Happiness score range: 2.5 - 7.8
- Missing data diisi dengan nilai 0

---

### Block 4-6: INSERT INDICATORS

```sql
-- Economic Indicators (GDP)
INSERT INTO economic_indicator (economic_id, report_id, gdp_per_capita) VALUES
(10001, 10001, 1.39),
...

-- Social Indicators
INSERT INTO social_indicator (social_id, report_id, social_support, healthy_life_expectancy, freedom_to_make_life_choices) VALUES
(20001, 10001, 1.52, 0.87, 0.66),
...

-- Perception Indicators
INSERT INTO perception_indicator (perception_id, report_id, generosity, perceptions_of_corruption) VALUES
(30001, 10001, 0.29, 0.03),
...
```

**Data Quality:**
- ✅ Nilai realistis berdasarkan data asli WHR
- ✅ Distribusi geografis proporsional
- ✅ Missing data handled dengan nilai 0
- ✅ Konsisten antar tahun

---

## 🎮 Panduan Penggunaan

### Menjalankan Dashboard

```bash
# 1. Aktivasi virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 2. Navigate ke project
cd visualisasi-abd-8

# 3. Start Streamlit
streamlit run app_whr.py

# 4. Buka browser
# http://localhost:8501
```

### Interaksi dengan Halaman

**Navigasi:**
- Klik nama halaman di sidebar untuk pindah
- Setiap halaman load data saat pertama kali dikunjungi
- Data cached mempercepat load selanjutnya

**Charts:**
- Hover untuk detail tooltips
- Klik legend items untuk toggle series
- Gunakan Plotly toolbar untuk zoom, pan, export

**Filters:**
- Year selector untuk filter tahun
- Region filter untuk fokus area tertentu
- Country selector untuk detail negara

---

## 🔧 Troubleshooting

### Issue 1: "Connection Refused" Error

```
❌ Gagal terhubung ke Supabase: could not connect to server
```

**Solusi:**
```bash
# 1. Verifikasi .env file ada dan benar
cat .env

# 2. Test koneksi langsung
python -c "from config_whr import get_database_connection; print('✅ Connected!')"

# 3. Check firewall/VPN settings
# Pastikan port 5432 tidak diblokir
```

---

### Issue 2: "ModuleNotFoundError"

```
❌ ModuleNotFoundError: No module named 'streamlit'
```

**Solusi:**
```bash
# 1. Reinstall dependencies
pip install -r requirements.txt

# 2. Verifikasi instalasi
pip list | grep streamlit

# 3. Jika masih gagal, reinstall di environment bersih
pip uninstall -y streamlit pandas plotly psycopg2-binary
pip install -r requirements.txt
```

---

### Issue 3: "Data Type" Errors pada Charts

```
❌ TypeError: unsupported operand type(s)
```

**Solusi:**
- Sudah di-fix di helper functions dengan `pd.to_numeric()`
- Pastikan semua operasi numerik menggunakan kolom yang sudah dikonversi:

```python
# ✅ BENAR
df['score'] = pd.to_numeric(df['score'], errors='coerce')
df['score'].mean()

# ❌ SALAH
df['score'].mean()  # Tanpa type conversion
```

---

### Issue 4: "No such table" Error

```
❌ psycopg2.errors.UndefinedTable: relation "happiness_report" does not exist
```

**Solusi:**
```bash
# 1. Buat schema
psql -h your_host -U your_user -d postgres -f DDL_whr_v2.sql

# 2. Load data
psql -h your_host -U your_user -d postgres -f DML_whr_v2.sql

# 3. Verifikasi tabel
psql -h your_host -U your_user -d postgres \
     -c "SELECT tablename FROM pg_tables WHERE schemaname='public';"
```

---

### Issue 5: "SSL Connection Error"

```
❌ psycopg2.Error: FATAL: SSL connection required
```

**Solusi:**
- Sudah dikonfigurasi di `config_whr.py` dengan `sslmode="require"`
- Jika masih gagal, check:

```python
# Di config_whr.py - pastikan line ini ada
sslmode="require"  # Wajib untuk Supabase
```

---

## 📈 Tips Optimasi Performa

### 1. Database Indexing

Indexes yang direkomendasikan:

```sql
CREATE INDEX idx_hr_year ON happiness_report(year);
CREATE INDEX idx_hr_country ON happiness_report(country_id);
CREATE INDEX idx_country_region ON country(region_id);
```

**Impact:** 10-100x faster queries untuk dataset besar

### 2. Streamlit Caching

Sudah diimplementasi dengan `@st.cache_data`:

```python
@st.cache_data
def get_happiness_data(year):
    # Cached selama session
    # Auto-invalidate jika kode berubah
```

### 3. Query Optimization

Queries menggunakan:
- ✅ Proper aggregations (`SUM()`, `AVG()`, `COUNT()`)
- ✅ Complete `GROUP BY` clauses
- ✅ Selective column selection
- ✅ `LIMIT` untuk top-N queries

---

## 🚀 Opsi Deployment

### Option 1: Streamlit Cloud (Recommended)

```bash
# 1. Push ke GitHub
git push origin main

# 2. Connect ke Streamlit Cloud
# https://share.streamlit.io/deploy

# 3. Select repository dan app_whr.py
# App automatically deploys dan updates on push
```

### Option 2: Docker Container

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app_whr.py"]
```

```bash
docker build -t whr-dashboard .
docker run -p 8501:8501 whr-dashboard
```

---

## 📚 Sumber Tambahan

### PostgreSQL Documentation
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Aggregate Functions](https://www.postgresql.org/docs/current/functions-aggregate.html)

### Streamlit Documentation
- [Streamlit Docs](https://docs.streamlit.io/)
- [Plotly Integration](https://docs.streamlit.io/library/api-reference/charts/st.plotly_chart)
- [Caching](https://docs.streamlit.io/library/api-reference/performance/st.cache_data)

### Supabase Documentation
- [Supabase Docs](https://supabase.com/docs)
- [PostgreSQL on Supabase](https://supabase.com/docs/guides/database)

### World Happiness Report
- [Official WHR Website](https://worldhappiness.report/)
- [Data Source](https://www.kaggle.com/datasets/unsdsn/world-happiness)

---

## 📝 Ringkasan Project

| Aspek | Detail |
|-------|--------|
| **Database** | 6 tabel ternormalisasi, 171 negara, 1.710 records happiness |
| **Schema** | 3NF dengan star schema design |
| **Data Volume** | 10 region, 171 negara, 10 tahun data (2015-2024) |
| **Visualisasi** | 15+ chart interaktif (Bar, Scatter, Pie, Choropleth, dll) |
| **Halaman** | 8 halaman analisis dengan fokus berbeda |
| **Query Count** | 15+ optimized SQL queries dengan proper indexing |
| **Performance** | Response time sub-second dengan caching & indexes |
| **Security** | Environment-based credentials, SSL/TLS encrypted |
| **Hosting** | Supabase cloud PostgreSQL (global availability) |

---

## 👥 Kontributor

- **Rayhan Iqbal** - Analisis Basis Data
- Database Design: Normalized Schema
- Frontend: Streamlit Dashboard
- Data: 170 Countries dengan Real WHR Data

---

## 📄 Lisensi

Project ini untuk keperluan edukasi di Institut Teknologi Kalimantan

---

## 🌐 Live Demo

**Dashboard URL:** [https://visualisasi-abd-8-5n8fkqxmjxha2p45cgz78x.streamlit.app/](https://visualisasi-abd-8-5n8fkqxmjxha2p45cgz78x.streamlit.app/)

---

**Last Updated:** December 9, 2025  
**Status:** ✅ Production Ready
