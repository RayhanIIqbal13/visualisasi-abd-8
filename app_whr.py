# -*- coding: utf-8 -*-
# ================================================
# FILE: app_whr.py
# FUNGSI: Main Application - World Happiness Report Dashboard
# ================================================
#
# DESKRIPSI LENGKAP:
#   Aplikasi Streamlit yang menampilkan dashboard interaktif untuk analisis
#   World Happiness Report dengan data dari 175+ negara tahun 2015-2024.
#   
#   Frontend: Streamlit (Python web framework)
#   Backend: PostgreSQL database (config_whr.py)
#   Visualisasi: Plotly Express + Plotly Graph Objects
#   Maps: Folium + Streamlit-folium
#
# ================================================
# ARSITEKTUR APLIKASI
# ================================================
#
# 1. DATA FLOW:
#    User Browser (Streamlit UI)
#        ↓
#    app_whr.py (Frontend - halaman_*)
#        ↓
#    config_whr.py (Backend - database queries)
#        ↓
#    PostgreSQL Database (data storage)
#
# 2. STRUKTUR HALAMAN (8 Pages):
#    - Beranda: Statistik ringkas + intro
#    - Region: Map, bar/pie chart regional
#    - Country: Map, chart, filter by region
#    - Happiness Report: Ranking + histogram + box plot (filter tahun+region)
#    - Economic Indicator: GDP analysis (filter tahun+region)
#    - Social Indicator: 3 sub-pages - bar charts, table, grouped bar + heatmap
#    - Perception Indicator: Generosity + corruption (filter tahun+region)
#
# 3. PATTERN FILTER:
#    - Year Filter: "Semua Tahun" + [2024, 2023, ..., 2015]
#    - Region Filter: "Semua Region" + [13 regions]
#    - Logika:
#      if selected_year is None → gunakan get_*_all() → return banyak kolom
#      else → gunakan get_*_by_year(year) → return sedikit kolom
#      Penting: DataFrame columns HARUS sesuai dengan columns parameter!
#
# 4. SESSION STATE (Persist data antar refresh):
#    - current_page: Halaman aktif (diubah oleh sidebar button)
#    - country_filter_region: Region pilihan di halaman Country
#
# 5. UTILITIES:
#    - convert_df_to_csv(): Convert DataFrame ke CSV bytes (untuk download)
#    - @st.cache_data: Cache hasil function untuk performa
#
# 6. ERROR HANDLING:
#    - Setiap function punya try-except
#    - Jika database error → tampilkan st.error()
#    - Jika data kosong → tampilkan st.info() atau st.warning()
#
# ================================================
# CARA MENJALANKAN:
# ================================================
#
# 1. Setup PostgreSQL:
#    - Pastikan PostgreSQL sudah running
#    - Database "world_happines_v2" sudah dibuat
#    - DDL: DDL_whr_v2.sql sudah di-execute
#
# 2. Install Dependencies:
#    pip install streamlit pandas plotly numpy psycopg2 folium streamlit-folium
#
# 3. Run Dashboard:
#    cd "d:\Kampus ITK\ABD\Tugas Besar - ABD 8 v2"
#    streamlit run app_whr.py
#
#    Akan buka di: http://localhost:8501
#
# ================================================

# ================================================
# IMPORT LIBRARIES
# ================================================
import streamlit as st             # Framework untuk dashboard
import pandas as pd                # Data manipulation
import plotly.express as px        # Visualisasi chart (bar, scatter, pie, etc)
import plotly.graph_objects as go  # Advanced chart controls
import numpy as np                 # Numerical computing
from datetime import datetime      # Date/time utilities
from config_whr import *           # Import semua functions dan variables dari config_whr.py

# Try import folium untuk peta interaktif
try:
    import folium                  # Library untuk membuat peta interaktif
    from streamlit_folium import st_folium  # Wrapper untuk render folium di Streamlit
    FOLIUM_AVAILABLE = True        # Flag: folium berhasil di-import
except ImportError:
    FOLIUM_AVAILABLE = False       # Flag: folium tidak tersedia (user belum install)

# ================================================
# KONFIGURASI HALAMAN STREAMLIT
# ================================================
# Konfigurasi tampilan dashboard sebelum render
st.set_page_config(
    page_title="Dashboard WHR",          # Judul browser tab
    page_icon="🌍",                      # Icon browser tab
    layout="wide",                       # Layout lebar (vs 'centered')
    initial_sidebar_state="expanded"     # Sidebar default expanded
)

# Custom CSS untuk styling dashboard
st.markdown("""
<style>
    .main { padding: 0px; }  /* Hapus padding default Streamlit */
    .metric-container { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ================================================
# INISIALISASI SESSION STATE
# ================================================
# session_state = storage untuk persist data antar-refresh Streamlit
# Streamlit re-run halaman setiap kali ada interaksi (click, input, dll)
# session_state memungkinkan kita menyimpan data sehingga tidak hilang

def init_session_state():
    """
    FUNGSI: Initialize semua session state variables
    
    PENJELASAN SESSION STATE:
      - st.session_state adalah dict global untuk menyimpan data per user session
      - Data di session_state persist sampai browser ditutup
      - Berguna untuk menyimpan: halaman aktif, filter pilihan, dsb
    
    VARIABLES YANG DISIMPAN:
      1. current_page: Halaman mana yang sedang ditampilkan
         - Default: "Beranda"
         - Digunakan di sidebar navigation button
      
      2. country_filter_region: Region yang dipilih di halaman Country
         - Default: None (artinya tampilkan semua negara)
         - Digunakan untuk filter dropdown
    """
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Beranda"  # Halaman default saat pertama kali buka dashboard
    if 'country_filter_region' not in st.session_state:
        st.session_state.country_filter_region = None  # Tidak ada filter region default

# Jalankan initialization function
init_session_state()

# ================================================
# DATA MAPPING: REGION DAN COUNTRY KE KOORDINAT GPS
# ================================================
# Digunakan untuk membuat peta interaktif dengan folium
# Format: latitude (garis lintang), longitude (garis bujur)

# REGION_COORDINATES: Koordinat pusat setiap region di dunia
# Digunakan sebagai fallback jika country tidak punya koordinat spesifik
REGION_COORDINATES = {
    'Western Europe': (55, 10),                                    # Eropa Barat
    'Central and Eastern Europe': (52, 25),                        # Eropa Tengah dan Timur
    'Commonwealth of Independent States': (60, 105),              # CIS (Russia, Kazakhstan, dll)
    'Middle East and North Africa': (25, 40),                      # Timur Tengah dan Afrika Utara
    'Sub-Saharan Africa': (-5, 20),                                # Afrika Sub-Sahara
    'South Asia': (20, 77),                                        # Asia Selatan
    'Southeast Asia': (15, 105),                                   # Asia Tenggara
    'East Asia': (35, 100),                                        # Asia Timur
    'Latin America and Caribbean': (-5, -60),                      # Amerika Latin dan Karibia
    'North America and ANZ': (45, -100),                            # Amerika Utara + Australia/NZ
}

# COUNTRY_COORDINATES: Koordinat GPS presisi untuk 175+ negara dunia
# Digunakan untuk plotting marker peta dengan akurasi tinggi
# Format: 'country_name': (latitude, longitude)
COUNTRY_COORDINATES = {
    'Denmark': (56.26, 9.50), 'Iceland': (64.96, -19.02), 'Switzerland': (46.82, 8.23),
    'Netherlands': (52.13, 5.29), 'Finland': (61.92, 25.75), 'Sweden': (60.13, 18.64),
    'Norway': (60.47, 8.47), 'Austria': (47.52, 14.55), 'Germany': (51.17, 10.45),
    'Luxembourg': (49.82, 6.13), 'Belgium': (50.50, 4.48), 'United Kingdom': (55.38, -3.44),
    'France': (46.23, 2.21), 'Spain': (40.46, -3.75), 'Italy': (41.87, 12.57),
    'Greece': (39.07, 21.82), 'Portugal': (39.40, -8.22), 'Czechia': (49.82, 15.47),
    'Poland': (51.92, 19.15), 'Romania': (45.94, 24.97), 'Slovakia': (48.67, 19.70),
    'Hungary': (47.16, 19.50), 'Croatia': (45.10, 15.20), 'Serbia': (44.02, 21.01),
    'Bulgaria': (42.73, 25.49), 'Slovenia': (46.15, 14.99), 'Lithuania': (55.17, 23.88),
    'Latvia': (56.88, 24.60), 'Estonia': (58.60, 25.01), 'Ukraine': (48.38, 31.17),
    'Russia': (61.52, 105.32), 'Israel': (31.05, 34.85), 'Saudi Arabia': (23.89, 45.08),
    'United Arab Emirates': (23.42, 53.85), 'Iran': (32.43, 53.69), 'Turkey': (38.96, 35.24),
    'Egypt': (26.82, 30.80), 'Morocco': (31.79, -7.09), 'Algeria': (28.03, 1.66),
    'South Africa': (-30.56, 22.94), 'Nigeria': (9.08, 8.68), 'Kenya': (-0.02, 37.91),
    'Ethiopia': (9.15, 40.49), 'Ghana': (7.37, -1.00), 'India': (20.59, 78.96),
    'Pakistan': (30.38, 69.35), 'Bangladesh': (23.68, 90.36), 'Nepal': (28.39, 84.12),
    'Sri Lanka': (7.87, 80.77), 'Thailand': (15.87, 100.99), 'Vietnam': (14.06, 108.28),
    'Philippines': (12.88, 121.77), 'Indonesia': (-0.79, 113.92), 'Malaysia': (4.21, 101.69),
    'Singapore': (1.35, 103.82), 'South Korea': (35.91, 127.77), 'Japan': (36.20, 138.25),
    'China': (35.86, 104.20), 'Taiwan': (23.70, 120.96), 'Hong Kong': (22.40, 114.11),
    'Mongolia': (46.86, 103.85), 'Brazil': (-14.24, -51.93), 'Mexico': (23.63, -102.55),
    'Colombia': (4.57, -74.30), 'Argentina': (-38.42, -63.62), 'Chile': (-35.68, -71.54),
    'Peru': (-9.19, -75.02), 'Venezuela': (6.42, -66.59), 'Guatemala': (15.78, -90.23),
    'Ecuador': (-1.83, -78.18), 'Nicaragua': (12.87, -85.21), 'Honduras': (15.20, -86.24),
    'El Salvador': (13.79, -88.90), 'Panama': (8.54, -80.77), 'Costa Rica': (9.75, -83.75),
    'Canada': (56.13, -106.35), 'United States': (37.09, -95.71), 'Jamaica': (18.11, -77.30),
    'Trinidad and Tobago': (10.69, -61.22), 'Dominican Republic': (18.73, -70.16),
    'Haiti': (18.97, -72.29), 'Puerto Rico': (18.22, -66.59), 'Australia': (-25.27, 133.78),
    'New Zealand': (-40.90, 174.89), 'Cambodia': (12.57, 104.99), 'Myanmar': (21.91, 95.96),
    'Laos': (19.86, 102.50), 'Paraguay': (-23.44, -58.44), 'Uruguay': (-32.52, -55.77),
    'Bolivia': (-16.29, -63.59), 'Suriname': (3.92, -56.03), 'Guyana': (4.86, -58.93),
    'Lebanon': (33.85, 35.86), 'Palestinian Territories': (31.95, 35.19), 'Jordan': (30.59, 36.24),
    'Iraq': (33.31, 44.36), 'Syria': (34.80, 38.99), 'Yemen': (15.55, 48.52),
    'Bahrain': (26.07, 50.56), 'Kuwait': (29.31, 47.48), 'Qatar': (25.35, 51.18),
    'Oman': (21.51, 55.92), 'Tunisia': (33.89, 9.54), 'Libya': (26.34, 17.23),
    'Sudan': (12.86, 30.22), 'Somalia': (5.15, 46.20), 'Zimbabwe': (-19.02, 29.15),
    'Botswana': (-22.33, 24.68), 'Namibia': (-22.96, 18.68), 'Zambia': (-13.13, 27.85),
    'Malawi': (-13.25, 34.30), 'Tanzania': (-6.37, 34.89), 'Uganda': (1.37, 32.29),
    'Rwanda': (-1.94, 30.06), 'Burundi': (-3.37, 29.92), 'Congo (Brazzaville)': (-4.04, 21.76),
    'Congo (Kinshasa)': (-4.04, 21.76), 'Angola': (-11.20, 17.87), 'Cameroon': (3.85, 11.50),
    'Ivory Coast': (7.54, -5.55), 'Senegal': (14.50, -14.45), 'Mali': (17.57, -4.00),
    'Mauritania': (21.01, -10.94), 'Guinea': (9.95, -9.70), 'Liberia': (6.43, -9.43),
    'Sierra Leone': (8.46, -11.78), 'Chad': (15.45, 18.73), 'Niger': (17.61, 8.67),
    'Benin': (9.31, 2.31), 'Togo': (6.13, 1.23), 'Gabon': (-1.00, 11.61),
    'Equatorial Guinea': (1.87, 10.39), 'Mauritius': (-20.35, 57.55), 'Seychelles': (-4.68, 55.49),
    'Madagascar': (-18.73, 46.87), 'Belize': (17.19, -88.76), 'Barbados': (13.19, -59.53),
}

# ================================================
# COUNTRY NAME MAPPING: Database -> GeoJSON
# ================================================
# Mapping untuk mencocokkan nama negara di database dengan nama di GeoJSON file
# Database country names -> GeoJSON feature names
COUNTRY_NAME_MAPPING = {
    # North America
    'United States': 'United States of America',
    'Trinidad & Tobago': 'Trinidad and Tobago',
    
    # Europe
    'Czechia': 'Czech Republic',
    'North Macedonia': 'Macedonia',
    'Serbia': 'Republic of Serbia',
    'Turkiye': 'Turkey',
    'North Cyprus': 'Northern Cyprus',
    
    # Western Asia / Middle East
    'Palestinian Territories': 'West Bank',
    'State of Palestine': 'West Bank',
    
    # Africa
    'Argelia': 'Algeria',
    'Democratic Republic of the Congo': 'Democratic Republic of the Congo',
    'Republic of the Congo': 'Republic of the Congo',
    'Somaliland region': 'Somaliland',
    
    # Asia
    'Taiwan Province of China': 'Taiwan',
    
    # Special cases - these countries are not in GeoJSON
    # (will remain as gray "Unknown" on the map):
    # 'Bahrain': <not in GeoJSON>
    # 'Comoros': <not in GeoJSON>
    # 'Congo': <ambiguous - not mapped>
    # 'Hong Kong': <not in GeoJSON>
    # 'Hong Kong S.A.R. of China': <not in GeoJSON>
    # 'Maldives': <not in GeoJSON>
    # 'Malta': <not in GeoJSON>
    # 'Mauritius': <not in GeoJSON>
    # 'Singapore': <not in GeoJSON>
    'Eswatini': 'Swaziland',
    'Tanzania': 'United Republic of Tanzania',
}

# ================================================
# UTILITY FUNCTIONS
# ================================================

@st.cache_data  # Decorator: cache hasil function agar tidak dijalankan setiap refresh
def convert_df_to_csv(_df):
    """
    FUNGSI: Mengkonversi pandas DataFrame menjadi CSV bytes untuk di-download
    
    PARAMETER:
      _df (pandas.DataFrame): DataFrame yang ingin dikonversi ke CSV
        Catatan: underscore (_df) adalah konvensi untuk parameter yang di-cache
    
    RETURN: bytes (CSV dalam format bytes)
      Encoded dengan UTF-8 untuk mendukung karakter spesial (emoji, huruf non-ASCII)
    
    PENGGUNAAN:
      csv = convert_df_to_csv(df)
      st.download_button(
          label="Download CSV",
          data=csv,
          file_name='data.csv',
          mime='text/csv'
      )
    
    CACHE:
      - @st.cache_data decorator menyimpan hasil di memory
      - Jika function dipanggil dengan parameter yang sama, gunakan cache bukan re-compute
      - Hemat resource dan mempercepat app
    """
    return _df.to_csv(index=False).encode('utf-8')

# ================================================
# HALAMAN: BERANDA
# ================================================
# Halaman pertama yang tampil saat user buka dashboard
# Menampilkan: Judul, deskripsi, dan statistik ringkas database

def halaman_beranda():
    """
    FUNGSI: Halaman Beranda (Home Page)
    
    KOMPONEN:
      1. Judul dan deskripsi singkat dashboard
      2. Statistik ringkas 4 metrik dari database:
         - Total Region
         - Total Country
         - Total Happiness Records
         - Tahun data tersedia
      3. Info tips untuk navigasi
    
    ALUR KODE:
      1. st.title() → Tampilkan judul besar
      2. st.markdown() → Tampilkan deskripsi halaman-halaman
      3. st.columns(4) → Buat 4 kolom untuk metrics
      4. Untuk setiap kolom, panggil function get_*_count() dari config_whr.py
      5. st.metric() → Tampilkan angka metrics
      6. st.info() → Tampilkan info box
    
    DATA SOURCES:
      - get_region_count() dari config_whr.py → total region
      - get_country_count() dari config_whr.py → total negara
      - get_happiness_count() dari config_whr.py → total records happiness
      - get_available_years() dari config_whr.py → list tahun tersedia
    """
    st.title("🌍 World Happiness Report Dashboard")
    st.markdown("---")
    
    st.markdown("""
    ### Selamat Datang di Dashboard Analisis Kebahagiaan Dunia!
    
    Dashboard ini menyajikan visualisasi dan analisis data **World Happiness Report** yang mencakup:
    
    - **🌐 Region**: Data wilayah geografis dunia
    - **🗺️ Country**: Data negara-negara di setiap wilayah
    - **😊 Happiness Report**: Skor kebahagiaan dan ranking negara per tahun
    - **💰 Economic Indicator**: Indikator ekonomi (GDP per Capita) dan hubungannya dengan kebahagiaan
    - **👥 Social Indicator**: Indikator sosial (dukungan sosial, harapan hidup, kebebasan)
    - **🤝 Perception Indicator**: Tingkat kemurahan hati dan persepsi korupsi
    
    **Fitur Utama:**
    - 📊 Visualisasi interaktif dengan Plotly
    - 📋 Tabel data dengan filter dan ekspor CSV
    - 📈 Analisis trend dan statistik
    - 🔍 Filter data berdasarkan region, tahun, dan parameter lainnya
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Statistik Ringkas Database")
    
    # Ambil statistik global
    stats = get_global_happiness_statistics()
    total_countries = get_country_count()
    countries_with_data = get_countries_with_happiness_count()
    
    # Buat 4 kolom untuk menampilkan 4 metrik utama
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Total negara di database
        st.metric(
            label="🌐 Total Countries",
            value=total_countries,
            help=f"Total negara dalam database: {total_countries}\nDengan data happiness: {countries_with_data}"
        )
    
    with col2:
        # Rata-rata happiness score
        st.metric(
            label="📊 Rata-rata Happiness Score",
            value=f"{stats['avg_happiness']:.3f}",
            help="Rata-rata dari semua negara semua tahun (2015-2024)"
        )
    
    with col3:
        # Skor tertinggi
        st.metric(
            label="⬆️ Skor Tertinggi",
            value=f"{stats['max_happiness']:.3f}",
            help="Skor happiness tertinggi di seluruh data"
        )
    
    with col4:
        # Skor terendah
        st.metric(
            label="⬇️ Skor Terendah",
            value=f"{stats['min_happiness']:.3f}",
            help="Skor happiness terendah di seluruh data"
        )
    
    st.markdown("---")
    st.info("💡 Gunakan menu di sidebar untuk navigasi ke halaman yang berbeda")

# ================================================
# HALAMAN: REGION
# ================================================
# Menampilkan data regional dengan 4 tabs:
# 1. Peta interaktif dengan folium
# 2. Visualisasi bar chart dan pie chart
# 3. Tabel data region lengkap
# 4. Statistik ringkas

def halaman_region():
    """
    FUNGSI: Halaman Region - Analisis wilayah geografis dunia
    
    STRUKTUR HALAMAN:
      1. Title + Metadata (total region, negara, rata-rata)
      2. 4 Tabs: Map, Visualization, Table, Statistics
    
    TAB 1 - PETA:
      - Folium map dengan center [20, 0] (pusat dunia) dan zoom 2
      - Circle marker untuk setiap region
      - Warna marker: red (banyak) → orange → green → blue (sedikit)
      - Ukuran marker proporsional dengan jumlah negara
      - Popup: Nama region + jumlah negara
    
    TAB 2 - VISUALISASI:
      - Bar chart: Jumlah negara per region (sorted desc)
      - Pie chart: Distribusi persentase negara per region
      - Plotly Express untuk interaktivitas
    
    TAB 3 - TABEL:
      - Tabel region dengan sort by country_count desc
      - Download button untuk export CSV
    
    TAB 4 - STATISTIK:
      - Min/Max/Mean/Median/StdDev jumlah negara
      - Top 5 region dengan negara terbanyak
    
    DATABASE QUERIES:
      - get_region_with_countries_count() → 13 regions dengan count negara
    """
    st.title("🌐 Data Region")
    st.markdown("---")
    
    # Ambil data region
    region_list = get_regions()
    
    # Filter di sidebar
    with st.sidebar.expander("🔍 Filter Data Region", expanded=True):
        region_options = ["Semua Region"] + [r[1] for r in region_list]
        selected_region_display = st.selectbox(
            "Pilih Region",
            options=region_options,
            key="region_region_filter"
        )
        selected_region = None if selected_region_display == "Semua Region" else selected_region_display
    
    # Ambil data region beserta jumlah negara di setiap region
    region_data = get_region_with_countries_count()
    
    # Error handling: jika tidak ada data
    if not region_data:
        st.error("❌ Data region tidak ditemukan")
        return
    
    # Konversi list of tuples ke pandas DataFrame untuk manipulasi data
    df_region = pd.DataFrame(region_data, columns=[
        "region_id", "region_name", "country_count"
    ])
    
    # Terapkan filter region jika dipilih
    if selected_region:
        df_region_display = df_region[df_region['region_name'] == selected_region].copy()
    else:
        df_region_display = df_region.copy()
    
    # ============ METRIK RINGKAS ============
    # 3 kolom untuk menampilkan 3 statistik utama region
    col1, col2, col3 = st.columns(3)
    with col1:
        # Total jumlah region yang ditampilkan
        display_text = f"{len(df_region_display)}" if selected_region else f"{len(df_region)}"
        st.metric("🌐 Total Region", display_text)
    with col2:
        # Total semua negara di region(s) yang ditampilkan
        st.metric("🗺️ Total Country", int(df_region_display['country_count'].sum()))
    with col3:
        # Rata-rata negara per region yang ditampilkan
        st.metric("📊 Rata-rata Country per Region", f"{df_region_display['country_count'].mean():.1f}")
    
    st.markdown("---")
    
    # ============ TABS ============
    # 4 tabs untuk different views data region
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Peta", "📊 Jumlah & Distribusi", "📋 Tabel Data", "📈 Statistik"])
    
    with tab1:
        st.markdown("### 🗺️ Peta Distribusi Region Dunia")
        
        if FOLIUM_AVAILABLE:
            # Buat peta dengan folium
            m = folium.Map(location=[20, 0], zoom_start=2)  # Center di equator, zoom 2
            
            # Cari max country_count untuk normalisasi warna (skala 0-100%)
            max_count = df_region_display['country_count'].max()
            
            # Loop setiap region dan tambahkan marker ke peta
            for idx, row in df_region_display.iterrows():
                region_name = row['region_name']
                country_count = int(row['country_count'])
                
                # Ambil koordinat region dari dictionary
                if region_name in REGION_COORDINATES:
                    lat, lng = REGION_COORDINATES[region_name]
                    
                    # Tentukan warna marker berdasarkan prosentase country_count
                    # Scale: 0-25% = blue, 25-50% = green, 50-75% = orange, 75-100% = red
                    if country_count >= max_count * 0.75:
                        color = '#d62728'  # Red - banyak negara
                    elif country_count >= max_count * 0.5:
                        color = '#ff7f0e'  # Orange - cukup banyak
                    elif country_count >= max_count * 0.25:
                        color = '#2ca02c'  # Green - sedang
                    else:
                        color = '#1f77b4'  # Blue - sedikit
                    
                    # Tambahkan circle marker ke peta
                    folium.CircleMarker(
                        location=[lat, lng],
                        radius=max(8, country_count / 2),  # Ukuran: min 8px, scaled by country_count
                        popup=f"<b>{region_name}</b><br>Negara: {country_count}",  # Popup saat diklik
                        tooltip=f"{region_name}: {country_count} negara",  # Tooltip saat hover
                        color=color,              # Border color
                        fill=True,
                        fillColor=color,          # Fill color
                        fillOpacity=0.7,          # 70% opacity
                        weight=2                  # Border thickness
                    ).add_to(m)
            
            # Render peta di Streamlit
            st_folium(m, width=1300, height=500)
            
            # Tambahkan legend untuk menjelaskan warna dan ukuran
            st.markdown("""
            #### 🎨 Penjelasan Warna dan Ukuran Marker:
            
            **Warna marker berdasarkan jumlah negara:**
            - 🔴 **Merah**: ≥75% dari maksimum (Banyak negara)
            - 🟠 **Orange**: 50-75% dari maksimum (Cukup banyak negara)
            - 🟢 **Hijau**: 25-50% dari maksimum (Jumlah sedang)
            - 🔵 **Biru**: <25% dari maksimum (Sedikit negara)
            
            **Ukuran marker**: Semakin besar = semakin banyak negara di region tersebut
            
            **Cara membaca peta**: Klik marker untuk melihat detail jumlah negara, atau arahkan mouse untuk tooltip.
            """)
        else:
            st.info("📌 Peta interaktif memerlukan library folium. Gunakan: pip install folium streamlit-folium")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart: Jumlah country per region
            fig_bar = px.bar(
                df_region_display,
                x='region_name',
                y='country_count',
                title='📊 Jumlah Negara per Region',
                labels={'region_name': 'Region', 'country_count': 'Jumlah Negara'},
                color='country_count',
                color_continuous_scale='Viridis'
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, width='stretch')
            st.markdown("""
            **📖 Penjelasan Bar Chart:**
            - Menampilkan jumlah negara di setiap region
            - Warna lebih gelap = lebih banyak negara
            - Urutkan dari region dengan negara terbanyak hingga paling sedikit
            - Berguna untuk melihat distribusi negara geografis global
            """)
        
        with col2:
            # Pie chart: Distribusi negara
            fig_pie = px.pie(
                df_region_display,
                values='country_count',
                names='region_name',
                title='📈 Distribusi Negara per Region'
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, width='stretch')
            st.markdown("""
            **📖 Penjelasan Pie Chart:**
            - Menunjukkan persentase negara di setiap region
            - Ukuran potongan = jumlah relatif negara
            - Membantu melihat komposisi global secara keseluruhan
            - Warna berbeda untuk setiap region agar mudah dibedakan
            """)
    
    with tab3:
        st.markdown("### 📋 Tabel Data Region")
        st.dataframe(
            df_region_display.sort_values('country_count', ascending=False),
            width='stretch',
            hide_index=True
        )
        
        # Download CSV
        csv = convert_df_to_csv(df_region_display)
        st.download_button(
            label="⬇️ Download Data Region sebagai CSV",
            data=csv,
            file_name='data_region.csv',
            mime='text/csv'
        )
    
    with tab4:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📊 Statistik Jumlah Negara")
            stats = {
                "Minimum": int(df_region_display['country_count'].min()),
                "Maksimum": int(df_region_display['country_count'].max()),
                "Rata-rata": round(df_region_display['country_count'].mean(), 2),
                "Median": int(df_region_display['country_count'].median()),
                "Std Dev": round(df_region_display['country_count'].std(), 2)
            }
            for key, value in stats.items():
                st.write(f"**{key}**: {value}")
        
        with col2:
            st.markdown("#### 🌐 Region dengan Negara Terbanyak")
            top_region = df_region_display.nlargest(5, 'country_count')[['region_name', 'country_count']]
            for idx, row in top_region.iterrows():
                st.write(f"🏅 **{row['region_name']}**: {int(row['country_count'])} negara")

# ================================================
# HALAMAN: COUNTRY
# ================================================

def halaman_country():
    st.title("🗺️ Data Country")
    st.markdown("---")
    
    # Ambil data region untuk filter
    region_list = get_regions()
    region_dict = {r[1]: r[0] for r in region_list}
    
    # Filter di sidebar dengan key yang unik
    with st.sidebar.expander("🔍 Filter Data Country", expanded=True):
        selected_region = st.selectbox(
            "Pilih Region",
            options=[None] + [r[1] for r in region_list],
            format_func=lambda x: "Semua Region" if x is None else x,
            key="country_page_region_filter"
        )
    
    # Ambil data country
    if selected_region:
        country_data = get_countries_by_region(region_dict[selected_region])
    else:
        country_data = get_countries()
    
    if not country_data:
        st.error("❌ Data country tidak ditemukan")
        return
    
    df_country = pd.DataFrame(country_data, columns=[
        "country_id", "country_name", "region_name"
    ])
    
    # ============ METRIK ============
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🗺️ Total Country", len(df_country))
    with col2:
        if selected_region:
            st.metric("Region Terpilih", selected_region)
    
    st.markdown("---")
    
    # ============ TABS ============
    tab1, tab2, tab3 = st.tabs(["🗺️ Peta", "📊 Distribusi", "📋 Tabel Data"])
    
    with tab1:
        st.markdown("### 🗺️ Peta Choropleth Negara (Berdasarkan Region)")
        
        if FOLIUM_AVAILABLE:
            try:
                # ============ IMPORT REQUIRED LIBRARIES ============
                import requests
                
                # ============ URL GEOJSON DATA ============
                # URL untuk GeoJSON file berisi geometri semua negara dunia
                # Source: Natural Earth Data (public domain geographic data)
                geojson_url = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json'
                
                # ============ DICTIONARY WARNA REGION → HEX COLOR ============
                # Setiap region punya warna unik
                # IMPORTANT: Names MUST match exactly with regions in database!
                color_map = {
                    'Western Europe': '#FF6B6B',                        # Red
                    'Central and Eastern Europe': '#4ECDC4',            # Cyan
                    'Commonwealth of Independent States': '#45B7D1',    # Blue (Russia, CIS countries)
                    'Middle East and North Africa': '#F7DC6F',          # Yellow
                    'Sub-Saharan Africa': '#BB8FCE',                    # Purple
                    'South Asia': '#85C1E2',                            # Light Blue
                    'Southeast Asia': '#F8B88B',                        # Peach
                    'East Asia': '#95E1D3',                             # Turquoise
                    'Latin America and Caribbean': '#C7CEEA',           # Lavender
                    'North America and ANZ': '#B5EAD7',                 # Mint Light (USA, Canada, Australia, NZ)
                }
                
                # ============ BUAT MAPPING COUNTRY → REGION ============
                # Dictionary mapping: nama negara → region
                # Digunakan untuk lookup region saat processing GeoJSON features
                country_to_region = dict(zip(df_country['country_name'], df_country['region_name']))
                
                # ============ DOWNLOAD GEOJSON DATA ============
                response = requests.get(geojson_url)
                geojson_data = response.json()
                
                # ============ INISIALISASI BASE MAP ============
                m = folium.Map(
                    location=[20, 0],
                    zoom_start=2,
                    tiles='CartoDB positron'  # Gunakan tile map yang clean
                )
                
                # ============ FUNCTION UNTUK STYLE CHOROPLETH ============
                def style_function(feature, country_to_region_dict=country_to_region, color_dict=color_map, name_mapping=COUNTRY_NAME_MAPPING):
                    """
                    FUNCTION: Menentukan style (warna) setiap negara berdasarkan region-nya
                    
                    PARAMETER:
                      feature: GeoJSON feature object yang berisi properti negara dan geometri
                      country_to_region_dict: Dictionary mapping country → region
                      color_dict: Dictionary mapping region → warna hex
                      name_mapping: Dictionary mapping GeoJSON names to database names
                    
                    RETURN: Dictionary dengan style properties
                    """
                    # Ambil nama negara dari GeoJSON feature properties
                    geojson_country_name = feature['properties'].get('name', '')
                    
                    # Cek apakah nama GeoJSON perlu di-map ke nama database
                    # (karena beberapa negara punya nama berbeda di database vs GeoJSON)
                    # REVERSE mapping: GeoJSON name -> Database name
                    database_country_name = geojson_country_name
                    for db_name, geojson_name in name_mapping.items():
                        if geojson_name == geojson_country_name:
                            database_country_name = db_name
                            break
                    
                    # Cari region untuk negara ini menggunakan database name
                    region = country_to_region_dict.get(database_country_name, 'Unknown')
                    
                    # Ambil warna dari color_map berdasarkan region
                    color = color_dict.get(region, '#CCCCCC')
                    
                    # Return style dictionary
                    return {
                        'fillColor': color,          # Warna isi negara
                        'color': '#333333',          # Warna border negara (dark gray)
                        'weight': 1,                 # Ketebalan border
                        'fillOpacity': 0.8           # Opacity 80% (20% transparent)
                    }
                
                # ============ TAMBAHKAN GEOJSON LAYER KE MAP ============
                # folium.GeoJson: Layer untuk menampilkan GeoJSON data di map
                geojson_layer = folium.GeoJson(
                    geojson_data,
                    style_function=style_function,  # Style normal
                    popup=folium.GeoJsonPopup(fields=['name']),  # Popup saat klik
                    tooltip=folium.GeoJsonTooltip(fields=['name'], labels=True)  # Tooltip saat hover
                )
                geojson_layer.add_to(m)
                
                # ============ TAMBAHKAN LEGEND KE MAP ============
                # Legend menjelaskan mapping warna ← region
                legend_html = '''
                <div style="position: fixed; 
                            bottom: 50px; right: 50px; width: 250px; height: auto; 
                            background-color: white; border:2px solid grey; z-index:9999; 
                            font-size:12px; padding: 10px; border-radius: 5px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3)">
                    <b style="font-size: 14px;">🎨 Warna Region</b><br>
                    <hr style="margin: 5px 0;">
                '''
                
                # Loop setiap region dan tambahkan ke legend
                for region, color in color_map.items():
                    legend_html += f'<span style="display: inline-block; width: 15px; height: 15px; background-color: {color}; border: 1px solid #333; margin-right: 5px;"></span> {region}<br>'
                
                legend_html += '''
                <hr style="margin: 5px 0;">
                <span style="display: inline-block; width: 15px; height: 15px; background-color: #CCCCCC; border: 1px solid #333; margin-right: 5px;"></span> Unknown
                </div>
                '''
                
                # Tambahkan HTML legend ke map
                m.get_root().html.add_child(folium.Element(legend_html))
                
                # ============ RENDER PETA ============
                st_folium(m, width=1300, height=600)
                
                # ============ STATISTIK NEGARA ============
                # Hitung berapa banyak negara yang ditampilkan
                st.markdown("---")
                
                # Create columns untuk menampilkan statistik
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                
                # Total countries di GeoJSON
                total_geojson = len(geojson_data['features'])
                
                # Total countries di database
                total_database = len(df_country)
                
                # Countries yang berhasil di-map
                successfully_mapped = 0
                for country in df_country['country_name']:
                    # Check if country atau nama mapping-nya ada di GeoJSON
                    if country in [f['properties']['name'] for f in geojson_data['features']]:
                        successfully_mapped += 1
                    else:
                        # Check di mapping dictionary
                        if country in COUNTRY_NAME_MAPPING:
                            geojson_name = COUNTRY_NAME_MAPPING[country]
                            if geojson_name in [f['properties']['name'] for f in geojson_data['features']]:
                                successfully_mapped += 1
                
                # Countries tidak ada di peta
                missing_from_map = total_database - successfully_mapped
                
                with stat_col1:
                    st.metric(
                        label="📊 Total Negara (DB)",
                        value=total_database,
                        delta=None
                    )
                
                with stat_col2:
                    st.metric(
                        label="🗺️ Total Negara (GeoJSON)",
                        value=total_geojson,
                        delta=None
                    )
                
                with stat_col3:
                    st.metric(
                        label="✅ Negara Terepresentasi",
                        value=successfully_mapped,
                        delta=f"{(successfully_mapped/total_database*100):.1f}%"
                    )
                
                with stat_col4:
                    st.metric(
                        label="⚠️ Tidak di Peta",
                        value=missing_from_map,
                        delta=f"{(missing_from_map/total_database*100):.1f}%"
                    )
                
                # ============ DETAIL NEGARA YANG TIDAK DITAMPILKAN ============
                if missing_from_map > 0:
                    with st.expander(f"📋 Lihat {missing_from_map} negara yang tidak ditampilkan di peta"):
                        missing_countries = []
                        geojson_names = [f['properties']['name'] for f in geojson_data['features']]
                        
                        # Dictionary untuk alasan mengapa negara tidak ditampilkan
                        unmapped_reasons = {
                            'Bahrain': '🏝️ Terlalu kecil - Pulau kecil di Teluk Persia',
                            'Comoros': '🏝️ Terlalu kecil - Kepulauan kecil di Samudera Hindia',
                            'Maldives': '🏝️ Terlalu kecil - Kepulauan atol di Samudera Hindia',
                            'Malta': '🏝️ Terlalu kecil - Pulau kecil di Laut Tengah',
                            'Mauritius': '🏝️ Terlalu kecil - Pulau kecil di Samudera Hindia',
                            'Singapore': '🏙️ Kota negara - Terlalu kecil untuk terlihat di peta global',
                        }
                        
                        for country in sorted(df_country['country_name']):
                            # Check apakah negara ada di GeoJSON
                            if country not in geojson_names:
                                # Check mapping
                                if country in COUNTRY_NAME_MAPPING:
                                    geojson_name = COUNTRY_NAME_MAPPING[country]
                                    if geojson_name not in geojson_names:
                                        missing_countries.append(country)
                                else:
                                    missing_countries.append(country)
                        
                        if missing_countries:
                            for country in missing_countries:
                                reason = unmapped_reasons.get(country, '❓ Tidak tersedia di GeoJSON')
                                st.info(f"**{country}**: {reason}")
                            
                            st.markdown("""
                            ---
                            **Catatan**: Negara-negara di atas tidak ditampilkan di peta karena:
                            1. **Terlalu kecil** - Ukuran geografis terlalu kecil untuk terlihat di peta dunia
                            2. **Wilayah khusus** - Status politis khusus tidak direpresentasikan sebagai negara terpisah di GeoJSON
                            3. **Data GeoJSON terbatas** - GeoJSON yang digunakan tidak mencakup semua area geografis
                            
                            Meskipun tidak ditampilkan di peta, data kebahagiaan negara-negara ini tetap tersedia di tabel dan visualisasi lainnya.
                            """)
                
                # Tambahkan penjelasan
                st.markdown("""
                #### 📖 Penjelasan Peta Choropleth:
                
                **Fitur Interaktif:**
                - 🎨 **Warna**: Setiap negara diberi warna sesuai region-nya (lihat legend)
                - 🎯 **Hover**: Arahkan mouse ke negara untuk melihat nama negara (tooltip)
                - 🖱️ **Klik**: Klik negara untuk melihat popup dengan informasi
                - 🌟 **Highlight**: Negara akan berubah warna saat di-hover
                
                **Interpretasi:**
                - Warna yang sama = region yang sama
                - Wilayah geografis yang berdekatan dengan warna sama = region yang sama
                - Negara dengan warna abu-abu (#CCCCCC) = data tidak ditemukan di database
                
                **Tips:**
                - Zoom in/out dengan scroll atau tombol +/- di peta
                - Drag peta untuk pan (menggeser tampilan)
                - Gunakan filter region di sidebar untuk melihat negara tertentu saja
                """)
                
            except Exception as e:
                st.error(f"❌ Error membuat peta choropleth: {str(e)}")
                st.info("💡 Pastikan library requests sudah terinstall: pip install requests")
        else:
            st.info("📌 Peta choropleth memerlukan library folium dan requests. Gunakan: pip install folium streamlit-folium requests")
    
    with tab2:
        if selected_region:
            # Jika filter region aktif, tampilkan daftar negara
            fig_bar = px.bar(
                df_country,
                y='country_name',
                title=f'📊 Negara di Region: {selected_region}',
                labels={'country_name': 'Country'},
                color_discrete_sequence=['#636EFA']
            )
            fig_bar.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_bar, width='stretch')
            st.markdown("""
            **📖 Penjelasan Bar Chart:**
            - Menampilkan daftar semua negara di region yang dipilih
            - Setiap bar mewakili satu negara
            - Gunakan scroll untuk melihat semua negara jika jumlahnya banyak
            """)
        else:
            # Jika semua region, tampilkan distribusi per region
            country_per_region = df_country.groupby('region_name').size().reset_index(name='country_count')
            fig_bar = px.bar(
                country_per_region.sort_values('country_count', ascending=True),
                x='country_count',
                y='region_name',
                title='📊 Distribusi Country per Region',
                labels={'country_count': 'Jumlah Country', 'region_name': 'Region'},
                color='country_count',
                color_continuous_scale='Blues'
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, width='stretch')
            st.markdown("""
            **📖 Penjelasan Bar Chart:**
            - Menampilkan jumlah negara di setiap region secara horizontal
            - Warna lebih gelap (biru) = lebih banyak negara
            - Memudahkan perbandingan distribusi negara antar region
            """)
    
    with tab3:
        st.markdown("### 📋 Tabel Data Country")
        st.dataframe(
            df_country.sort_values(['region_name', 'country_name']),
            width='stretch',
            hide_index=True
        )
        
        # Download CSV
        csv = convert_df_to_csv(df_country)
        st.download_button(
            label="⬇️ Download Data Country sebagai CSV",
            data=csv,
            file_name='data_country.csv',
            mime='text/csv'
        )

# ================================================
# HALAMAN: HAPPINESS REPORT
# ================================================

def halaman_happiness_report():
    st.title("😊 Happiness Report")
    st.markdown("---")
    
    # Ambil data tahun yang tersedia
    years = sorted(get_available_years(), reverse=True)
    region_list = get_regions()
    
    if not years:
        st.error("❌ Data Happiness Report tidak ditemukan")
        return
    
    # Filter di sidebar
    with st.sidebar.expander("🔍 Filter Happiness Report", expanded=True):
        year_options = ["Semua Tahun"] + [str(y) for y in years]
        selected_year_display = st.selectbox(
            "Pilih Tahun",
            options=year_options,
            key="happiness_year_filter"
        )
        selected_year = None if selected_year_display == "Semua Tahun" else int(selected_year_display)
        
        region_options = ["Semua Region"] + [r[1] for r in region_list]
        selected_region_display = st.selectbox(
            "Pilih Region",
            options=region_options,
            key="happiness_region_filter"
        )
        selected_region = None if selected_region_display == "Semua Region" else selected_region_display
    
    # Ambil data
    if selected_year is None:
        # AGGREGATED: Average ranking and score across all years (2015-2024) per negara
        happiness_data = get_happiness_report_all_aggregated()
        # get_happiness_report_all_aggregated returns: country_name, region_name, avg_ranking, avg_happiness_score
        df_happiness = pd.DataFrame(happiness_data, columns=[
            "country_name", "region_name", "ranking", "happiness_score"
        ])
    else:
        happiness_data = get_happiness_report_by_year(selected_year)
        # get_happiness_report_by_year returns: country_name, region_name, ranking, happiness_score, dystopia_residual
        df_happiness = pd.DataFrame(happiness_data, columns=[
            "country_name", "region_name", "ranking", "happiness_score", "dystopia_residual"
        ])
    
    # Konversi kolom numeric
    df_happiness['ranking'] = pd.to_numeric(df_happiness['ranking'], errors='coerce')
    df_happiness['happiness_score'] = pd.to_numeric(df_happiness['happiness_score'], errors='coerce')
    
    # Konversi dystopia_residual hanya jika kolom ada (untuk specific year, bukan aggregated)
    if 'dystopia_residual' in df_happiness.columns:
        df_happiness['dystopia_residual'] = pd.to_numeric(df_happiness['dystopia_residual'], errors='coerce')
    
    # Filter berdasarkan region jika dipilih
    if selected_region:
        df_happiness = df_happiness[df_happiness['region_name'] == selected_region]
    
    # ============ METRIK ============
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("😊 Total Countries", len(df_happiness))
    with col2:
        st.metric("📊 Rata-rata Happiness Score", f"{df_happiness['happiness_score'].mean():.3f}")
    with col3:
        st.metric("🏆 Skor Tertinggi", f"{df_happiness['happiness_score'].max():.3f}")
    with col4:
        st.metric("📉 Skor Terendah", f"{df_happiness['happiness_score'].min():.3f}")
    
    st.markdown("---")
    
    # ============ TABS ============
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Top 10", "📈 Distribusi", "📋 Tabel Data", "🔍 Detail"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 Tertinggi
            top_10 = df_happiness.nlargest(10, 'happiness_score')
            fig_top = px.bar(
                top_10.sort_values('happiness_score'),
                x='happiness_score',
                y='country_name',
                title='🏆 Top 10 Negara Paling Bahagia',
                labels={'happiness_score': 'Happiness Score', 'country_name': 'Country'},
                color='happiness_score',
                color_continuous_scale='Greens'
            )
            fig_top.update_layout(height=400)
            st.plotly_chart(fig_top, width='stretch')
            st.markdown("""
            **📖 Penjelasan Bar Chart - Top 10 Bahagia:**
            - Menampilkan 10 negara dengan skor kebahagiaan tertinggi
            - Warna lebih gelap (hijau) = skor kebahagiaan lebih tinggi
            - Skor berkisar 0-10, negara di atas biasanya: kaya, stabil, & harmonis sosial
            - Indikator kesejahteraan & kualitas hidup masyarakat
            """)
        
        with col2:
            # Top 10 Terendah
            bottom_10 = df_happiness.nsmallest(10, 'happiness_score')
            fig_bottom = px.bar(
                bottom_10.sort_values('happiness_score', ascending=False),
                x='happiness_score',
                y='country_name',
                title='📉 Top 10 Negara Paling Tidak Bahagia',
                labels={'happiness_score': 'Happiness Score', 'country_name': 'Country'},
                color='happiness_score',
                color_continuous_scale='Reds'
            )
            fig_bottom.update_layout(height=400)
            st.plotly_chart(fig_bottom, width='stretch')
            st.markdown("""
            **📖 Penjelasan Bar Chart - Top 10 Tidak Bahagia:**
            - Menampilkan 10 negara dengan skor kebahagiaan terendah
            - Warna lebih gelap (merah) = skor kebahagiaan lebih rendah
            - Negara di posisi ini biasanya: konflik, kemiskinan, ketidakstabilan
            - Perlu perhatian khusus untuk pembangunan & kesejahteraan masyarakat
            """)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogram distribusi happiness score
            fig_hist = px.histogram(
                df_happiness,
                x='happiness_score',
                nbins=15,
                title='📊 Distribusi Happiness Score',
                labels={'happiness_score': 'Happiness Score'},
                color_discrete_sequence=['#636EFA']
            )
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, width='stretch')
            st.markdown("""
            **📖 Penjelasan Histogram:**
            - Menunjukkan sebaran happiness score di seluruh negara
            - X-axis: Range happiness score, Y-axis: Jumlah negara
            - Bukit/puncak menunjukkan happiness score yang paling umum
            - Membantu melihat distribusi kebahagiaan secara keseluruhan
            """)
        
        with col2:
            # Box plot per region
            fig_box = px.box(
                df_happiness,
                x='region_name',
                y='happiness_score',
                title='📊 Happiness Score per Region',
                labels={'happiness_score': 'Happiness Score', 'region_name': 'Region'},
                color='region_name'
            )
            fig_box.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_box, width='stretch')
            st.markdown("""
            **📖 Penjelasan Box Plot:**
            - Garis tengah = median (nilai tengah)
            - Kotak = 50% data di tengah (IQR)
            - Garis atas/bawah = nilai minimum/maksimum
            - Titik outlier = negara dengan happiness score ekstrem
            - Membandingkan kebahagiaan antar region
            """)
    
    with tab3:
        st.markdown("### 📋 Tabel Lengkap Happiness Report")
        st.dataframe(
            df_happiness.sort_values('ranking'),
            width='stretch',
            hide_index=True
        )
        
        # Download CSV
        csv = convert_df_to_csv(df_happiness)
        year_suffix = "all_years" if selected_year is None else str(selected_year)
        st.download_button(
            label="⬇️ Download Data sebagai CSV",
            data=csv,
            file_name=f'happiness_report_{year_suffix}.csv',
            mime='text/csv'
        )
    
    with tab4:
        st.markdown("#### 📊 Statistik Happiness Score")
        
        col1, col2 = st.columns(2)
        with col1:
            stats = {
                "Rata-rata": f"{df_happiness['happiness_score'].mean():.3f}",
                "Median": f"{df_happiness['happiness_score'].median():.3f}",
                "Std Dev": f"{df_happiness['happiness_score'].std():.3f}",
                "Minimum": f"{df_happiness['happiness_score'].min():.3f}",
                "Maksimum": f"{df_happiness['happiness_score'].max():.3f}"
            }
            for key, value in stats.items():
                st.write(f"**{key}**: {value}")
        
        with col2:
            st.markdown("#### 🌍 Statistik per Region")
            region_stats = df_happiness.groupby('region_name')['happiness_score'].agg(['mean', 'count']).round(3)
            st.dataframe(region_stats, width='stretch')

# ================================================
# HALAMAN: ECONOMIC INDICATOR
# ================================================

def halaman_economic_indicator():
    st.title("💰 Economic Indicator")
    st.markdown("---")
    
    # Ambil data tahun
    years = sorted(get_available_years(), reverse=True)
    region_list = get_regions()
    
    if not years:
        st.error("❌ Data Economic Indicator tidak ditemukan")
        return
    
    # Filter di sidebar
    with st.sidebar.expander("🔍 Filter Economic Indicator", expanded=True):
        year_options = ["Semua Tahun"] + [str(y) for y in years]
        selected_year_display = st.selectbox(
            "Pilih Tahun",
            options=year_options,
            key="econ_year"
        )
        selected_year = None if selected_year_display == "Semua Tahun" else int(selected_year_display)
        
        region_options = ["Semua Region"] + [r[1] for r in region_list]
        selected_region_display = st.selectbox(
            "Pilih Region",
            options=region_options,
            key="econ_region"
        )
        selected_region = None if selected_region_display == "Semua Region" else selected_region_display
    
    # Ambil data
    if selected_year is None:
        # AGGREGATED: Total GDP across all years (2015-2024) per negara
        econ_data = get_economic_indicators_all_aggregated()
        # get_economic_indicators_all_aggregated returns: country_name, region_name, total_gdp, avg_happiness_score
        df_econ = pd.DataFrame(econ_data, columns=[
            "country_name", "region_name", "gdp_per_capita", "happiness_score"
        ])
    else:
        econ_data = get_economic_indicators_by_year(selected_year)
        # get_economic_indicators_by_year returns: country_name, region_name, happiness_score, gdp_per_capita
        df_econ = pd.DataFrame(econ_data, columns=[
            "country_name", "region_name", "happiness_score", "gdp_per_capita"
        ])
    
    # Konversi kolom numeric
    df_econ['happiness_score'] = pd.to_numeric(df_econ['happiness_score'], errors='coerce')
    df_econ['gdp_per_capita'] = pd.to_numeric(df_econ['gdp_per_capita'], errors='coerce')
    
    # Filter data dengan GDP yang valid (> 0 dan tidak NULL)
    df_econ = df_econ[(df_econ['gdp_per_capita'].notna()) & (df_econ['gdp_per_capita'] > 0)]
    
    # Filter berdasarkan region jika dipilih
    if selected_region:
        df_econ = df_econ[df_econ['region_name'] == selected_region]
    
    if df_econ.empty:
        st.warning("⚠️ Data Economic Indicator untuk tahun ini tidak tersedia")
        return
    
    # ============ METRIK ============
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Countries", len(df_econ))
    with col2:
        st.metric("💵 GDP Rata-rata", f"${df_econ['gdp_per_capita'].mean():.3f}")
    with col3:
        st.metric("💹 GDP Tertinggi", f"${df_econ['gdp_per_capita'].max():.3f}")
    with col4:
        st.metric("📉 GDP Terendah", f"${df_econ['gdp_per_capita'].min():.3f}")
    
    st.markdown("---")
    
    # ============ TABS ============
    tab1, tab2, tab3 = st.tabs(["💰 Top GDP & Distribusi", "📋 Tabel Data", "🔍 Korelasi"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart top 15 GDP
            top_gdp = df_econ.nlargest(15, 'gdp_per_capita')
            fig_bar = px.bar(
                top_gdp.sort_values('gdp_per_capita'),
                x='gdp_per_capita',
                y='country_name',
                title='💰 Top 15 Negara dengan GDP Tertinggi',
                labels={'gdp_per_capita': 'GDP per Capita', 'country_name': 'Country'},
                color='gdp_per_capita',
                color_continuous_scale='Blues'
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, width='stretch')
            st.markdown("""
            **📖 Penjelasan Bar Chart - Top 15 GDP per Capita:**
            - Menampilkan 15 negara dengan GDP per Capita (pendapatan per orang) tertinggi
            - **Warna**: Gradasi biru - semakin gelap = GDP lebih tinggi
            - **Interpretasi**: 
              - Qatar, Luxembourg, Singapura = negara terkaya di dunia
              - GDP tinggi ≠ selalu kebahagiaan tertinggi (lihat scatter plot)
              - Negara maju dominan di ranking atas
            - **Cara baca**: Semakin panjang bar = GDP semakin besar
            """)
        
        with col2:
            # Histogram distribusi GDP
            fig_hist = px.histogram(
                df_econ,
                x='gdp_per_capita',
                nbins=15,
                title='📊 Distribusi GDP per Capita',
                labels={'gdp_per_capita': 'GDP per Capita'},
                color_discrete_sequence=['#636EFA']
            )
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, width='stretch')
            
            # Tentukan teks penjelasan berdasarkan filter tahun
            if selected_year is None:
                penjelasan_hist = """
                **📖 Penjelasan Histogram - Distribusi GDP per Capita (TOTAL 10 TAHUN):**
                - 📊 **Data**: Setiap negara = 1 titik (Total GDP dari 2015-2024 dijumlahkan)
                - **Y-axis (Frequency)**: Berapa banyak NEGARA pada range GDP tertentu
                - **X-axis (GDP per Capita)**: Total pendapatan per orang selama 10 tahun (dalam USD)
                - **Contoh**: Jika Qatar punya GDP rata-rata $50/tahun × 10 tahun = $500 total (1 negara di range 500-600)
                - **Pola**: Kebanyakan negara punya GDP TOTAL rendah-sedang (negara berkembang)
                - **Right-skewed**: Sedikit negara dengan GDP SANGAT tinggi (Qatar, Luxembourg, Singapura)
                - **Insight**: Ketimpangan ekonomi global - mayoritas negara miskin/berkembang
                """
            else:
                penjelasan_hist = f"""
                **📖 Penjelasan Histogram - Distribusi GDP per Capita (TAHUN {selected_year}):**
                - 📊 **Data**: Setiap negara = 1 titik (GDP pada tahun {selected_year} saja)
                - **Y-axis (Frequency)**: Berapa banyak NEGARA pada range GDP tertentu di tahun {selected_year}
                - **X-axis (GDP per Capita)**: Pendapatan per orang tahun {selected_year} (dalam USD)
                - **Pola**: Kebanyakan negara punya GDP rendah-sedang
                - **Right-skewed**: Sedikit negara dengan GDP SANGAT tinggi
                - **Insight**: Ketimpangan ekonomi global yang persisten
                """
            
            st.markdown(penjelasan_hist)
        
        # Scatter: Relasi GDP vs Happiness Score
        fig_scatter = px.scatter(
            df_econ,
            x='gdp_per_capita',
            y='happiness_score',
            color='region_name',
            hover_name='country_name',
            title='💰 Hubungan GDP per Capita vs Happiness Score',
            labels={'gdp_per_capita': 'GDP per Capita', 'happiness_score': 'Happiness Score', 'region_name': 'Region'}
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, width='stretch')
        st.markdown("""
        **📖 Penjelasan Scatter Plot - GDP vs Happiness Score:**
        - **Setiap titik = 1 negara** (X = GDP per Capita, Y = Happiness Score, Warna = Region)
        - **Trend garis**: Pola umum bahwa GDP lebih tinggi → Kebahagiaan lebih tinggi
        - **Interpretasi**:
          - ✅ GDP tinggi CENDERUNG lebih bahagia (karena penuhi kebutuhan dasar)
          - ⚠️ Tapi BUKAN satu-satunya faktor (lihat outlier yang menyimpang)
          - ⚠️ Negara kaya seperti Qatar punya GDP tertinggi tapi kebahagiaan tidak tertinggi
        - **Outlier (menyimpang dari garis)**:
          - Di atas garis = bahagia lebih dari ekspektasi GDP
          - Di bawah garis = bahagia kurang dari ekspektasi GDP
        - **Kesimpulan**: Uang penting untuk bahagia, tapi ada faktor lain (sosial, freedom, kesehatan)
        """)
    
    with tab2:
        st.markdown("### 📋 Tabel Data Economic Indicator")
        st.dataframe(
            df_econ.sort_values('gdp_per_capita', ascending=False),
            width='stretch',
            hide_index=True
        )
        
        csv = convert_df_to_csv(df_econ)
        year_suffix = "all_years" if selected_year is None else str(selected_year)
        st.download_button(
            label="⬇️ Download Data sebagai CSV",
            data=csv,
            file_name=f'economic_indicator_{year_suffix}.csv',
            mime='text/csv'
        )
    
    with tab3:
        st.markdown("#### 📊 Analisis Korelasi")
        
        correlation = df_econ['gdp_per_capita'].corr(df_econ['happiness_score'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📈 Korelasi GDP-Happiness", f"{correlation:.3f}")
            st.write("""
            **Interpretasi:**
            - Nilai positif menunjukkan hubungan positif
            - Semakin dekat ke 1.0, semakin kuat hubungannya
            - Semakin dekat ke 0, semakin lemah hubungannya
            """)
        
        with col2:
            st.markdown("#### 📊 Statistik GDP per Capita")
            stats = {
                "Rata-rata": f"${df_econ['gdp_per_capita'].mean():.3f}",
                "Median": f"${df_econ['gdp_per_capita'].median():.3f}",
                "Std Dev": f"${df_econ['gdp_per_capita'].std():.3f}",
                "Minimum": f"${df_econ['gdp_per_capita'].min():.3f}",
                "Maksimum": f"${df_econ['gdp_per_capita'].max():.3f}"
            }
            for key, value in stats.items():
                st.write(f"**{key}**: {value}")

# ================================================
# HALAMAN: SOCIAL INDICATOR
# ================================================

def halaman_social_indicator():
    st.title("👥 Social Indicator")
    st.markdown("---")
    
    # Ambil data tahun
    years = sorted(get_available_years(), reverse=True)
    region_list = get_regions()
    
    if not years:
        st.error("❌ Data Social Indicator tidak ditemukan")
        return
    
    # Filter di sidebar
    with st.sidebar.expander("🔍 Filter Social Indicator", expanded=True):
        year_options = ["Semua Tahun"] + [str(y) for y in years]
        selected_year_display = st.selectbox(
            "Pilih Tahun",
            options=year_options,
            key="social_year"
        )
        selected_year = None if selected_year_display == "Semua Tahun" else int(selected_year_display)
        
        region_options = ["Semua Region"] + [r[1] for r in region_list]
        selected_region_display = st.selectbox(
            "Pilih Region",
            options=region_options,
            key="social_region"
        )
        selected_region = None if selected_region_display == "Semua Region" else selected_region_display
    
    # Ambil data
    if selected_year is None:
        # AGGREGATED: Average social indicators across all years (2015-2024) per negara
        social_data = get_social_indicators_all_aggregated()
        # get_social_indicators_all_aggregated returns: country_name, region_name, avg_social_support, avg_life_expectancy, avg_freedom, avg_happiness_score
        df_social = pd.DataFrame(social_data, columns=[
            "country_name", "region_name", "social_support",
            "healthy_life_expectancy", "freedom_to_make_life_choices", "happiness_score"
        ])
    else:
        social_data = get_social_indicators_by_year(selected_year)
        # get_social_indicators_by_year returns: country_name, region_name, happiness_score, social_support, healthy_life_expectancy, freedom_to_make_life_choices
        df_social = pd.DataFrame(social_data, columns=[
            "country_name", "region_name", "happiness_score",
            "social_support", "healthy_life_expectancy", "freedom_to_make_life_choices"
        ])
    
    # Konversi kolom numeric
    df_social['happiness_score'] = pd.to_numeric(df_social['happiness_score'], errors='coerce')
    df_social['social_support'] = pd.to_numeric(df_social['social_support'], errors='coerce')
    df_social['healthy_life_expectancy'] = pd.to_numeric(df_social['healthy_life_expectancy'], errors='coerce')
    df_social['freedom_to_make_life_choices'] = pd.to_numeric(df_social['freedom_to_make_life_choices'], errors='coerce')
    
    # Filter data dengan minimal 2 indikator valid
    df_social = df_social.dropna(subset=['social_support', 'healthy_life_expectancy', 'freedom_to_make_life_choices'], how='all')
    
    # Filter berdasarkan region jika dipilih
    if selected_region:
        df_social = df_social[df_social['region_name'] == selected_region]
    
    if df_social.empty:
        st.warning("⚠️ Data Social Indicator untuk tahun ini tidak tersedia")
        return
    
    # ============ METRIK ============
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Countries", len(df_social))
    with col2:
        st.metric("🤝 Social Support Rata-rata", f"{df_social['social_support'].mean():.3f}")
    with col3:
        st.metric("❤️ Life Expectancy Rata-rata", f"{df_social['healthy_life_expectancy'].mean():.3f}")
    with col4:
        st.metric("🕊️ Freedom Rata-rata", f"{df_social['freedom_to_make_life_choices'].mean():.3f}")
    
    st.markdown("---")
    
    # ============ TABS ============
    tab1, tab2, tab3 = st.tabs(["🤝 Social Support, Life Expectancy, Freedom", "📋 Tabel Data", "📈 Perbandingan"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 Social Support
            top_support = df_social.nlargest(10, 'social_support')[['country_name', 'social_support']].sort_values('social_support')
            fig_support = px.bar(
                top_support,
                x='social_support',
                y='country_name',
                title='🤝 Top 10 Negara dengan Social Support Tertinggi',
                labels={'social_support': 'Social Support', 'country_name': 'Country'},
                color='social_support',
                color_continuous_scale='Greens'
            )
            fig_support.update_layout(height=400)
            st.plotly_chart(fig_support, width='stretch')
            st.markdown("""
            **📖 Penjelasan Bar Chart - Social Support:**
            - Mengukur kualitas hubungan & dukungan sosial di setiap negara
            - Skor 0-1, nilai lebih tinggi = masyarakat lebih saling mendukung
            - Negara dengan dukungan sosial kuat cenderung lebih bahagia
            """)
        
        with col2:
            # Top 10 Life Expectancy
            top_life = df_social.nlargest(10, 'healthy_life_expectancy')[['country_name', 'healthy_life_expectancy']].sort_values('healthy_life_expectancy')
            fig_life = px.bar(
                top_life,
                x='healthy_life_expectancy',
                y='country_name',
                title='❤️ Top 10 Negara dengan Life Expectancy Tertinggi',
                labels={'healthy_life_expectancy': 'Healthy Life Expectancy', 'country_name': 'Country'},
                color='healthy_life_expectancy',
                color_continuous_scale='Blues'
            )
            fig_life.update_layout(height=400)
            st.plotly_chart(fig_life, width='stretch')
            st.markdown("""
            **📖 Penjelasan Bar Chart - Life Expectancy:**
            - Menunjukkan rata-rata harapan hidup sehat di setiap negara
            - Semakin tinggi = kesehatan publik lebih baik
            - Berkaitan dengan akses kesehatan, nutrisi, dan gaya hidup
            """)
        
        # Top 10 Freedom
        top_freedom = df_social.nlargest(10, 'freedom_to_make_life_choices')[['country_name', 'freedom_to_make_life_choices']].sort_values('freedom_to_make_life_choices')
        fig_freedom = px.bar(
            top_freedom,
            x='freedom_to_make_life_choices',
            y='country_name',
            title='🕊️ Top 10 Negara dengan Freedom Tertinggi',
            labels={'freedom_to_make_life_choices': 'Freedom', 'country_name': 'Country'},
            color='freedom_to_make_life_choices',
            color_continuous_scale='Purples'
        )
        fig_freedom.update_layout(height=400)
        st.plotly_chart(fig_freedom, width='stretch')
        st.markdown("""
        **📖 Penjelasan Bar Chart - Freedom:**
        - Mengukur kebebasan individu dalam membuat pilihan hidup
        - Skor 0-1, nilai tinggi = masyarakat lebih bebas
        - Mencakup kebebasan berekspresi, beragama, dll
        """)
    
    with tab2:
        st.markdown("### 📋 Tabel Data Social Indicator")
        st.dataframe(
            df_social.sort_values('happiness_score', ascending=False),
            width='stretch',
            hide_index=True
        )
        
        csv = convert_df_to_csv(df_social)
        year_suffix = "all_years" if selected_year is None else str(selected_year)
        st.download_button(
            label="⬇️ Download Data sebagai CSV",
            data=csv,
            file_name=f'social_indicator_{year_suffix}.csv',
            mime='text/csv'
        )
    
    with tab3:
        st.markdown("#### 📊 Perbandingan Indikator Sosial - Top 10 Negara")
        
        # Ambil top 10 negara berdasarkan happiness score
        top_10_countries = df_social.nlargest(10, 'happiness_score')[['country_name', 'social_support', 'healthy_life_expectancy', 'freedom_to_make_life_choices']].dropna(how='any')
        
        if not top_10_countries.empty:
            # Normalisasi data ke range 0-1 untuk perbandingan visual yang adil
            df_norm = top_10_countries.copy()
            df_norm['social_support'] = df_norm['social_support'].fillna(0)
            df_norm['healthy_life_expectancy'] = df_norm['healthy_life_expectancy'].fillna(0)
            df_norm['freedom_to_make_life_choices'] = df_norm['freedom_to_make_life_choices'].fillna(0)
            
            # Normalize life expectancy ke skala 0-1 (anggap max 100 tahun)
            if df_norm['healthy_life_expectancy'].max() > 0:
                df_norm['healthy_life_expectancy'] = df_norm['healthy_life_expectancy'] / 100
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Grouped Bar Chart - Perbandingan 3 indikator
                df_chart = df_norm.set_index('country_name').reset_index()
                
                fig_grouped = go.Figure()
                
                fig_grouped.add_trace(go.Bar(
                    name='Social Support',
                    y=df_chart['country_name'],
                    x=df_chart['social_support'],
                    orientation='h',
                    marker=dict(color='#2ca02c')
                ))
                
                fig_grouped.add_trace(go.Bar(
                    name='Life Expectancy (normalized)',
                    y=df_chart['country_name'],
                    x=df_chart['healthy_life_expectancy'],
                    orientation='h',
                    marker=dict(color='#1f77b4')
                ))
                
                fig_grouped.add_trace(go.Bar(
                    name='Freedom',
                    y=df_chart['country_name'],
                    x=df_chart['freedom_to_make_life_choices'],
                    orientation='h',
                    marker=dict(color='#9467bd')
                ))
                
                fig_grouped.update_layout(
                    barmode='group',
                    title='📊 Perbandingan 3 Indikator Sosial (Top 10 Negara)',
                    xaxis_title='Skor (0-1)',
                    yaxis_title='Negara',
                    height=500,
                    legend=dict(x=0.5, y=-0.15, orientation='h')
                )
                
                st.plotly_chart(fig_grouped, width='stretch')
                st.markdown("""
                **📖 Penjelasan Grouped Bar Chart:**
                - Membandingkan 3 indikator sosial secara berdampingan
                - 🟢 Hijau = Social Support (dukungan sosial)
                - 🔵 Biru = Life Expectancy (harapan hidup, sudah dinormalisasi)
                - 🟪 Ungu = Freedom (kebebasan)
                - Semakin panjang bar = skor lebih tinggi di indikator tersebut
                - Mudah melihat keseimbangan indikator tiap negara
                """)
            
            with col2:
                # Heatmap - Matrix view untuk melihat pola
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=[df_norm['social_support'].values, 
                       df_norm['healthy_life_expectancy'].values,
                       df_norm['freedom_to_make_life_choices'].values],
                    x=df_norm['country_name'].values,
                    y=['Social Support', 'Life Expectancy', 'Freedom'],
                    colorscale='YlGnBu',
                    text=[[f'{val:.2f}' for val in df_norm['social_support'].values],
                          [f'{val:.2f}' for val in df_norm['healthy_life_expectancy'].values],
                          [f'{val:.2f}' for val in df_norm['freedom_to_make_life_choices'].values]],
                    texttemplate='%{text}',
                    textfont={"size": 10},
                    colorbar=dict(title='Skor')
                ))
                
                fig_heatmap.update_layout(
                    title='🔥 Heatmap Indikator Sosial (Top 10 Negara)',
                    xaxis_title='Negara',
                    yaxis_title='Indikator',
                    height=500
                )
                
                st.plotly_chart(fig_heatmap, width='stretch')
                st.markdown("""
                **📖 Penjelasan Heatmap:**
                - Warna semakin gelap/biru = skor semakin tinggi
                - Warna lebih terang/kuning = skor semakin rendah
                - Angka di setiap sel = skor pasti
                - Mudah melihat pola & kekuatan/kelemahan per negara
                - Misalnya: Nordic countries kuat di semua indikator (biru semua)
                """)
        else:
            st.info("Data tidak cukup untuk menampilkan perbandingan indikator")

# ================================================
# HALAMAN: PERCEPTION INDICATOR
# ================================================

def halaman_perception_indicator():
    st.title("🤝 Perception Indicator")
    st.markdown("---")
    
    # Ambil data tahun
    years = sorted(get_available_years(), reverse=True)
    region_list = get_regions()
    
    if not years:
        st.error("❌ Data Perception Indicator tidak ditemukan")
        return
    
    # Filter di sidebar
    with st.sidebar.expander("🔍 Filter Perception Indicator", expanded=True):
        year_options = ["Semua Tahun"] + [str(y) for y in years]
        selected_year_display = st.selectbox(
            "Pilih Tahun",
            options=year_options,
            key="perception_year"
        )
        selected_year = None if selected_year_display == "Semua Tahun" else int(selected_year_display)
        
        region_options = ["Semua Region"] + [r[1] for r in region_list]
        selected_region_display = st.selectbox(
            "Pilih Region",
            options=region_options,
            key="perception_region"
        )
        selected_region = None if selected_region_display == "Semua Region" else selected_region_display
    
    # Ambil data
    if selected_year is None:
        # AGGREGATED: Average perception indicators across all years (2015-2024) per negara
        perception_data = get_perception_indicators_all_aggregated()
        # get_perception_indicators_all_aggregated returns: country_name, region_name, avg_generosity, avg_perceptions_of_corruption, avg_happiness_score
        df_perception = pd.DataFrame(perception_data, columns=[
            "country_name", "region_name",
            "generosity", "perceptions_of_corruption", "happiness_score"
        ])
    else:
        perception_data = get_perception_indicators_by_year(selected_year)
        # get_perception_indicators_by_year returns: country_name, region_name, happiness_score, generosity, perceptions_of_corruption
        df_perception = pd.DataFrame(perception_data, columns=[
            "country_name", "region_name", "happiness_score",
            "generosity", "perceptions_of_corruption"
        ])
    
    # Konversi kolom numeric
    df_perception['happiness_score'] = pd.to_numeric(df_perception['happiness_score'], errors='coerce')
    df_perception['generosity'] = pd.to_numeric(df_perception['generosity'], errors='coerce')
    df_perception['perceptions_of_corruption'] = pd.to_numeric(df_perception['perceptions_of_corruption'], errors='coerce')
    
    # Filter data dengan minimal 1 indikator valid
    df_perception = df_perception.dropna(subset=['generosity', 'perceptions_of_corruption'], how='all')
    
    # Filter berdasarkan region jika dipilih
    if selected_region:
        df_perception = df_perception[df_perception['region_name'] == selected_region]
    
    if df_perception.empty:
        st.warning("⚠️ Data Perception Indicator untuk tahun ini tidak tersedia")
        return
    
    # ============ METRIK ============
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Countries", len(df_perception))
    with col2:
        st.metric("💝 Generosity Rata-rata", f"{df_perception['generosity'].mean():.3f}")
    with col3:
        st.metric("😟 Corruption Perception Rata-rata", f"{df_perception['perceptions_of_corruption'].mean():.3f}")
    with col4:
        st.metric("😊 Happiness Score Rata-rata", f"{df_perception['happiness_score'].mean():.3f}")
    
    st.markdown("---")
    
    # ============ TABS ============
    tab1, tab2, tab3 = st.tabs(["💝 Generosity & Corruption", "📋 Tabel Data", "🔍 Korelasi"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 Generosity
            df_gen_clean = df_perception.dropna(subset=['generosity'])
            if not df_gen_clean.empty:
                top_gen = df_gen_clean.nlargest(10, 'generosity')[['country_name', 'generosity']].sort_values('generosity')
                fig_gen = px.bar(
                    top_gen,
                    x='generosity',
                    y='country_name',
                    title='💝 Top 10 Negara dengan Generosity Tertinggi',
                    labels={'generosity': 'Generosity', 'country_name': 'Country'},
                    color='generosity',
                    color_continuous_scale='Greens'
                )
                fig_gen.update_layout(height=400)
                st.plotly_chart(fig_gen, width='stretch')
                st.markdown("""
                **📖 Penjelasan Bar Chart - Generosity:**
                - Mengukur tingkat kemurahan hati masyarakat
                - Diukur dari kontribusi charity/donasi sosial
                - Skor 0-1, nilai tinggi = masyarakat lebih murah hati
                - Indikasi karakter moral & empati sosial
                """)
        
        with col2:
            # Top 10 Corruption Perception
            df_corr_clean = df_perception.dropna(subset=['perceptions_of_corruption'])
            if not df_corr_clean.empty:
                top_corr = df_corr_clean.nlargest(10, 'perceptions_of_corruption')[['country_name', 'perceptions_of_corruption']].sort_values('perceptions_of_corruption')
                fig_corr = px.bar(
                    top_corr,
                    x='perceptions_of_corruption',
                    y='country_name',
                    title='⚠️ Top 10 Negara dengan Corruption Perception Tertinggi',
                    labels={'perceptions_of_corruption': 'Corruption Perception', 'country_name': 'Country'},
                    color='perceptions_of_corruption',
                    color_continuous_scale='Reds'
                )
                fig_corr.update_layout(height=400)
                st.plotly_chart(fig_corr, width='stretch')
                st.markdown("""
                **📖 Penjelasan Bar Chart - Corruption Perception:**
                - Mengukur persepsi rakyat tentang korupsi pemerintah
                - Skor 0-1, nilai TINGGI = persepsi korupsi TINGGI (BURUK)
                - Tingginya korupsi = kepercayaan publik berkurang
                - Berkaitan dengan kesejahteraan & kebahagiaan sosial
                """)
        
        # Scatter: Generosity vs Corruption Perception
        df_scatter = df_perception.dropna(subset=['generosity', 'perceptions_of_corruption'])
        if not df_scatter.empty:
            fig_scatter = px.scatter(
                df_scatter,
                x='generosity',
                y='perceptions_of_corruption',
                color='happiness_score',
                hover_name='country_name',
                title='📊 Hubungan Generosity vs Corruption Perception',
                labels={'generosity': 'Generosity', 'perceptions_of_corruption': 'Corruption Perception', 'happiness_score': 'Happiness Score'},
                color_continuous_scale='Viridis'
            )
            fig_scatter.update_layout(height=400)
            st.plotly_chart(fig_scatter, width='stretch')
            st.markdown("""
            **📖 Penjelasan Scatter Plot:**
            - X-axis: Generosity (semakin kanan = lebih murah hati)
            - Y-axis: Corruption Perception (semakin atas = persepsi korupsi lebih tinggi)
            - Warna: Happiness Score (kuning = bahagia, ungu = sedih)
            - Pola: Negara dengan generosity tinggi & korupsi rendah biasanya lebih bahagia
            """)
    
    with tab2:
        st.markdown("### 📋 Tabel Data Perception Indicator")
        st.dataframe(
            df_perception.sort_values('happiness_score', ascending=False),
            width='stretch',
            hide_index=True
        )
        
        csv = convert_df_to_csv(df_perception)
        year_suffix = "all_years" if selected_year is None else str(selected_year)
        st.download_button(
            label="⬇️ Download Data sebagai CSV",
            data=csv,
            file_name=f'perception_indicator_{year_suffix}.csv',
            mime='text/csv'
        )
    
    with tab3:
        st.markdown("#### 📊 Analisis Korelasi")
        
        df_corr_analysis = df_perception.dropna(subset=['generosity', 'perceptions_of_corruption', 'happiness_score'])
        
        if not df_corr_analysis.empty:
            corr_gen_happiness = df_corr_analysis['generosity'].corr(df_corr_analysis['happiness_score'])
            corr_corrupt_happiness = df_corr_analysis['perceptions_of_corruption'].corr(df_corr_analysis['happiness_score'])
            corr_gen_corrupt = df_corr_analysis['generosity'].corr(df_corr_analysis['perceptions_of_corruption'])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💝 Generosity-Happiness", f"{corr_gen_happiness:.3f}")
            with col2:
                st.metric("😟 Corruption-Happiness", f"{corr_corrupt_happiness:.3f}")
            with col3:
                st.metric("💝-😟 Generosity-Corruption", f"{corr_gen_corrupt:.3f}")
            
            st.write("""
            **Interpretasi Korelasi:**
            - Positif: Saat X naik, Y cenderung naik
            - Negatif: Saat X naik, Y cenderung turun
            - Mendekati 0: Tidak ada hubungan yang jelas
            """)
        else:
            st.info("Data tidak cukup untuk analisis korelasi")

# ================================================
# SIDEBAR NAVIGASI - MAIN MENU
# ================================================
# DESKRIPSI SIDEBAR:
#   Sidebar adalah panel navigasi di sebelah kiri dashboard
#   Fungsi: Memungkinkan user untuk berpindah antar halaman dengan mudah
#   Method: Button-based navigation yang update session_state
#
# ALUR NAVIGATION:
#   1. User klik tombol halaman di sidebar (contoh: "🏠 Beranda")
#   2. Callback function: st.session_state.active_page = "🏠 Beranda"
#   3. Streamlit re-run seluruh script
#   4. Conditional logic di bawah check active_page dan jalankan function halaman yang sesuai
#   5. Halaman berubah ke yang dipilih
#
# SESSION STATE:
#   st.session_state = storage global per user session (persist antar re-run)
#   active_page = variable yang menyimpan halaman mana yang sedang ditampilkan

# ============ RENDER SIDEBAR HEADER ============
# Tampilkan judul di sidebar
st.sidebar.title("📊 Dashboard Menu")  # Header sidebar dengan emoji
st.sidebar.markdown("---")              # Separator line

# ============ INISIALISASI SESSION STATE ============
# Cek apakah 'active_page' sudah ada di session_state
# Jika belum (pertama kali app dibuka), set default ke "🏠 Beranda"
# Jika sudah ada, retain nilainya (persist across re-runs)
if 'active_page' not in st.session_state:
    st.session_state.active_page = "🏠 Beranda"  # Default halaman = Beranda

# ============ TAMPILKAN INSTRUKSI DI SIDEBAR ============
# Teks instruksi untuk user
st.sidebar.markdown("**Pilih Halaman:**")

# ============ DAFTAR HALAMAN YANG TERSEDIA ============
# List berisi nama-nama halaman dengan emoji dan keterangan
# Format: "emoji label" (untuk tampilan yang user-friendly)
# Comments sebelah: Penjelasan singkat fungsi halaman
pages = [
    "🏠 Beranda",                    # Halaman home: Welcome message + database statistics
    "🌐 Region",                     # Halaman region: Map interaktif + bar chart + pie chart
    "🗺️ Country",                    # Halaman country: Map per country + chart + filter by region
    "😊 Happiness Report",           # Halaman happiness: Ranking + histogram + box plot (filter tahun+region)
    "💰 Economic Indicator",         # Halaman economic: GDP analysis + correlation scatter plot
    "👥 Social Indicator",           # Halaman social: 3 indicators - support, life exp, freedom (filter tahun+region)
    "🤝 Perception Indicator"        # Halaman perception: Generosity + corruption (filter tahun+region)
]

# ============ BUAT NAVIGATION BUTTONS ============
# Loop setiap halaman dan buat button di sidebar
# Setiap button memiliki key unik = page name (untuk mencegah duplicate key error)
for page in pages:
    # ============ BUTTON CREATION ============
    # st.sidebar.button(): Buat button di sidebar
    # Parameters:
    #   - page: Text yang ditampilkan di button (contoh: "🏠 Beranda")
    #   - width='stretch': Perlebar button untuk full width sidebar
    #   - key=page: Unique identifier untuk button (prevent duplicate key error)
    # Return: Boolean (True jika button di-click, False jika tidak)
    
    if st.sidebar.button(page, width='stretch', key=page):
        # ============ UPDATE SESSION STATE SAAT BUTTON DI-CLICK ============
        # Ketika user klik button, update active_page ke page yang dipilih
        # Session_state akan persist across re-runs (Streamlit akan re-run script)
        st.session_state.active_page = page

# ============ SEPARATOR DAN INFO BOX ============
st.sidebar.markdown("---")                                          # Separator line
st.sidebar.info("💡 Navigasi halaman menggunakan tombol di atas")   # Info message

# ================================================
# RENDER HALAMAN AKTIF - CONDITIONAL ROUTING LOGIC
# ================================================
# DESKRIPSI:
#   Section ini adalah "router" yang menentukan halaman mana yang di-render
#   Berdasarkan nilai st.session_state.active_page, jalankan function halaman yang sesuai
#   Alur:
#     1. Cek nilai active_page di session_state
#     2. Match dengan salah satu kondisional (if/elif)
#     3. Panggil function halaman yang sesuai (contoh: halaman_beranda())
#     4. Function halaman akan render content dan visualisasi
#
# STRUKTUR FUNCTION HALAMAN:
#   Setiap function halaman bertanggung jawab untuk:
#     - Query data dari database via config_whr.py functions
#     - Filter/process data menggunakan pandas
#     - Create visualizations menggunakan Plotly/Folium
#     - Display UI components menggunakan Streamlit
#
# PERFORMANCE NOTES:
#   - @st.cache_data decorator: Cache data untuk mencegah re-query database
#   - Streamlit hanya run conditional yang True, skip yang False
#   - Memory efficient: Hanya load halaman yang sedang ditampilkan

# ============ CONDITIONAL ROUTING - PILIH HALAMAN MANA YANG DI-RENDER ============
# Setiap kondisional check apakah active_page cocok dengan halaman itu
# Jika cocok, panggil function halaman yang sesuai

if st.session_state.active_page == "🏠 Beranda":
    # ============ HALAMAN BERANDA ============
    # Function: halaman_beranda()
    # Content: Welcome message, database statistics, JSON data preview
    # Filters: None (home page tidak punya filter)
    halaman_beranda()

elif st.session_state.active_page == "🌐 Region":
    # ============ HALAMAN REGION ============
    # Function: halaman_region()
    # Content: Interactive map dengan marker per region, bar chart, pie chart, table, statistics
    # Filters: None (display semua region)
    halaman_region()

elif st.session_state.active_page == "🗺️ Country":
    # ============ HALAMAN COUNTRY ============
    # Function: halaman_country()
    # Content: Interactive map dengan marker per country, bar chart (filter region), table
    # Filters: Region filter di sidebar (optional)
    halaman_country()

elif st.session_state.active_page == "😊 Happiness Report":
    # ============ HALAMAN HAPPINESS REPORT ============
    # Function: halaman_happiness_report()
    # Content: Top 10 ranking (top/bottom), histogram, box plot per region, table, statistics
    # Filters: Year filter + Region filter di sidebar
    halaman_happiness_report()

elif st.session_state.active_page == "💰 Economic Indicator":
    # ============ HALAMAN ECONOMIC INDICATOR ============
    # Function: halaman_economic_indicator()
    # Content: Top 15 GDP bar chart, histogram distribusi, scatter GDP vs Happiness, table, korelasi
    # Filters: Year filter + Region filter di sidebar
    halaman_economic_indicator()

elif st.session_state.active_page == "👥 Social Indicator":
    # ============ HALAMAN SOCIAL INDICATOR ============
    # Function: halaman_social_indicator()
    # Content: Top 10 Social Support, Life Expectancy, Freedom (3 bar charts), table, comparison chart
    # Filters: Year filter + Region filter di sidebar
    halaman_social_indicator()

elif st.session_state.active_page == "🤝 Perception Indicator":
    # ============ HALAMAN PERCEPTION INDICATOR ============
    # Function: halaman_perception_indicator()
    # Content: Top 10 Generosity + Top 10 Corruption Perception (2 bar charts), scatter korelasi, table, korelasi analysis
    # Filters: Year filter + Region filter di sidebar
    halaman_perception_indicator()
