"""
Script untuk generate DML (Data Manipulation Language) dari JSON files
Format sesuai dengan DML_whr_v2.sql yang sudah ada

================================================================================
ALUR DATA PIPELINE - World Happiness Report Database
================================================================================

Data Mentah (CSV/JSON)
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ [1] add_ids.py                                                              │
│     → Menambahkan ID fields ke setiap entry:                                │
│       • region_id   : ID region berdasarkan mapping                         │
│       • country_id  : ID unik untuk setiap negara                           │
│       • report_id   : ID untuk happiness report                             │
│       • economic_id : ID untuk economic indicator                           │
│       • social_id   : ID untuk social indicator                             │
│       • perception_id: ID untuk perception indicator                        │
└─────────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ [2] verify_ids.py                                                           │
│     → Verifikasi ID yang sudah ditambahkan:                                 │
│       • Cek kelengkapan semua ID fields                                     │
│       • Cek keunikan ID                                                     │
│       • Cek konsistensi antar file                                          │
│       ✓ Output: Laporan verifikasi ID                                       │
└─────────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ [3] fix_json_data.py                                                        │
│     → Memperbaiki format data:                                              │
│       • Fix decimal separator (koma → titik)                                │
│       • Hapus entries dengan region_id = 0 (invalid)                        │
│       • Normalisasi nilai numerik                                           │
└─────────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ [4] clean_and_reorder.py                                                    │
│     → Membersihkan dan merapikan data:                                      │
│       • Reorder 17 fields sesuai urutan standar                             │
│       • Recalculate dystopia_residual menggunakan MD5 hash                  │
│       • Standardisasi format output JSON                                    │
└─────────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ [5] verify_cleanup.py                                                       │
│     → Verifikasi hasil akhir:                                               │
│       • Cek struktur data final                                             │
│       • Cek kelengkapan fields                                              │
│       • Cek validitas nilai                                                 │
│       ✓ Output: Laporan verifikasi final                                    │
└─────────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Data Bersih (Data/Json_Bersih/)                                             │
│     → File JSON yang sudah bersih dan siap digunakan                        │
│       • world_happiness_2015.json                                           │
│       • world_happiness_2017.json                                           │
│       • world_happiness_2018.json                                           │
│       • ... (sampai 2024)                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ [6] generate_dml_from_json.py (SCRIPT INI)                                  │
│     → Generate SQL DML dari data bersih:                                    │
│       • INSERT INTO region                                                  │
│       • INSERT INTO country                                                 │
│       • INSERT INTO happiness_report                                        │
│       • INSERT INTO economic_indicator                                      │
│       • INSERT INTO social_indicator                                        │
│       • INSERT INTO perception_indicator                                    │
│       ✓ Output: DML_whr_v2_generated.sql                                    │
└─────────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Database (Supabase PostgreSQL / Local)                                      │
│     → Execute SQL untuk import data ke database                             │
└─────────────────────────────────────────────────────────────────────────────┘

================================================================================
"""

import json
import os
from pathlib import Path
from collections import OrderedDict

# Path ke folder JSON bersih
JSON_DIR = Path("Data/Json_Bersih")
OUTPUT_FILE = "DML_whr_v2_generated.sql"

# Region mapping
REGIONS = {
    1: "South Asia",
    2: "Central and Eastern Europe", 
    3: "Sub-Saharan Africa",
    4: "Latin America and Caribbean",
    5: "Commonwealth of Independent States",
    6: "North America and ANZ",
    7: "Western Europe",
    8: "Southeast Asia",
    9: "East Asia",
    10: "Middle East and North Africa"
}

def load_all_json_files():
    """Load semua file JSON dan gabungkan"""
    all_data = {}
    
    json_files = sorted(JSON_DIR.glob("world_happiness_*.json"))
    
    for filepath in json_files:
        # Extract year from filename
        year = int(filepath.stem.split("_")[-1])
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_data[year] = data
                print(f"✓ Loaded {filepath.name}: {len(data)} entries")
        except Exception as e:
            print(f"✗ Error loading {filepath.name}: {e}")
    
    return all_data

def extract_countries(all_data):
    """Extract unique countries dengan region_id"""
    countries = {}
    
    for year, entries in all_data.items():
        for entry in entries:
            country_name = entry.get('country_name')
            country_id = entry.get('country_id')
            region_id = entry.get('region_id')
            
            if country_name and country_id:
                if country_id not in countries:
                    countries[country_id] = {
                        'country_name': country_name,
                        'region_id': region_id
                    }
    
    return countries

def safe_float(value, default=0.0):
    """Convert value to float safely"""
    if value is None or str(value).lower() == 'none':
        return default
    try:
        return float(str(value).replace(',', '.'))
    except:
        return default

def safe_int(value, default=0):
    """Convert value to int safely"""
    if value is None or str(value).lower() == 'none':
        return default
    try:
        return int(float(str(value).replace(',', '.')))
    except:
        return default

def escape_string(s):
    """Escape single quotes in SQL strings"""
    if s is None:
        return ''
    return str(s).replace("'", "''")

def generate_dml(all_data):
    """Generate complete DML SQL file"""
    
    # Extract countries
    countries = extract_countries(all_data)
    
    # Collect all records
    happiness_records = []
    economic_records = []
    social_records = []
    perception_records = []
    
    # Generate record ID counter
    record_counter = 10001
    
    # Sort countries by ID
    sorted_country_ids = sorted(countries.keys())
    
    # For each country, generate 10 years of data
    for country_id in sorted_country_ids:
        country_info = countries[country_id]
        country_name = country_info['country_name']
        
        for year in sorted(all_data.keys()):
            entries = all_data[year]
            
            # Find entry for this country in this year
            entry = None
            for e in entries:
                if e.get('country_id') == country_id:
                    entry = e
                    break
            
            if entry:
                report_id = record_counter
                
                # Happiness Report
                happiness_records.append({
                    'report_id': report_id,
                    'country_id': country_id,
                    'year': year,
                    'ranking': safe_int(entry.get('ranking', 0)),
                    'happiness_score': round(safe_float(entry.get('happiness_score', 0)), 2),
                    'dystopia_residual': round(safe_float(entry.get('dystopia_residual', 0.1)), 3)
                })
                
                # Economic Indicator
                economic_records.append({
                    'economic_id': report_id,
                    'report_id': report_id,
                    'gdp_per_capita': round(safe_float(entry.get('gdp_per_capita', 0)), 2)
                })
                
                # Social Indicator
                social_records.append({
                    'social_id': report_id + 10000,
                    'report_id': report_id,
                    'social_support': round(safe_float(entry.get('social_support', 0)), 2),
                    'healthy_life_expectancy': round(safe_float(entry.get('healthy_life_expectancy', 0)), 1),
                    'freedom_to_make_life_choices': round(safe_float(entry.get('freedom_to_make_life_choices', 0)), 2)
                })
                
                # Perception Indicator
                perception_records.append({
                    'perception_id': report_id + 20000,
                    'report_id': report_id,
                    'generosity': round(safe_float(entry.get('generosity', 0)), 2),
                    'perceptions_of_corruption': round(safe_float(entry.get('perceptions_of_corruption', 0)), 2)
                })
                
                record_counter += 1
    
    # Generate SQL output
    sql_lines = []
    
    # Header
    sql_lines.append("-- DML (Data Manipulation Language) - World Happiness Report Database")
    sql_lines.append(f"-- Generated from JSON files in {JSON_DIR}")
    sql_lines.append(f"-- Total Countries: {len(countries)}")
    sql_lines.append(f"-- Total Records: {len(happiness_records)}")
    sql_lines.append("-- ============================================================")
    sql_lines.append("")
    
    # Region INSERT
    sql_lines.append("-- ============================================================")
    sql_lines.append("-- INSERT REGION DATA")
    sql_lines.append("-- ============================================================")
    sql_lines.append("INSERT INTO region (region_id, region_name) VALUES")
    region_values = []
    for region_id, region_name in sorted(REGIONS.items()):
        region_values.append(f"({region_id}, '{escape_string(region_name)}')")
    sql_lines.append(",\n".join(region_values) + ";")
    sql_lines.append("")
    
    # Country INSERT
    sql_lines.append("-- ============================================================")
    sql_lines.append(f"-- INSERT COUNTRY DATA ({len(countries)} countries)")
    sql_lines.append("-- ============================================================")
    sql_lines.append("INSERT INTO country (country_id, country_name, region_id) VALUES")
    country_values = []
    for country_id in sorted_country_ids:
        info = countries[country_id]
        country_values.append(f"({country_id}, '{escape_string(info['country_name'])}', {info['region_id']})")
    sql_lines.append(",\n".join(country_values) + ";")
    sql_lines.append("")
    
    # Happiness Report INSERT
    sql_lines.append("-- ============================================================")
    sql_lines.append(f"-- INSERT HAPPINESS REPORT DATA ({len(happiness_records)} records)")
    sql_lines.append("-- ============================================================")
    sql_lines.append("INSERT INTO happiness_report (report_id, country_id, year, ranking, happiness_score, dystopia_residual) VALUES")
    hr_values = []
    for rec in happiness_records:
        hr_values.append(f"({rec['report_id']}, {rec['country_id']}, {rec['year']}, {rec['ranking']}, {rec['happiness_score']}, {rec['dystopia_residual']})")
    sql_lines.append(",\n".join(hr_values) + ";")
    sql_lines.append("")
    
    # Economic Indicator INSERT
    sql_lines.append("-- ============================================================")
    sql_lines.append(f"-- INSERT ECONOMIC INDICATOR DATA ({len(economic_records)} records)")
    sql_lines.append("-- ============================================================")
    sql_lines.append("INSERT INTO economic_indicator (economic_id, report_id, gdp_per_capita) VALUES")
    eco_values = []
    for rec in economic_records:
        eco_values.append(f"({rec['economic_id']}, {rec['report_id']}, {rec['gdp_per_capita']})")
    sql_lines.append(",\n".join(eco_values) + ";")
    sql_lines.append("")
    
    # Social Indicator INSERT
    sql_lines.append("-- ============================================================")
    sql_lines.append(f"-- INSERT SOCIAL INDICATOR DATA ({len(social_records)} records)")
    sql_lines.append("-- ============================================================")
    sql_lines.append("INSERT INTO social_indicator (social_id, report_id, social_support, healthy_life_expectancy, freedom_to_make_life_choices) VALUES")
    soc_values = []
    for rec in social_records:
        soc_values.append(f"({rec['social_id']}, {rec['report_id']}, {rec['social_support']}, {rec['healthy_life_expectancy']}, {rec['freedom_to_make_life_choices']})")
    sql_lines.append(",\n".join(soc_values) + ";")
    sql_lines.append("")
    
    # Perception Indicator INSERT
    sql_lines.append("-- ============================================================")
    sql_lines.append(f"-- INSERT PERCEPTION INDICATOR DATA ({len(perception_records)} records)")
    sql_lines.append("-- ============================================================")
    sql_lines.append("INSERT INTO perception_indicator (perception_id, report_id, generosity, perceptions_of_corruption) VALUES")
    per_values = []
    for rec in perception_records:
        per_values.append(f"({rec['perception_id']}, {rec['report_id']}, {rec['generosity']}, {rec['perceptions_of_corruption']})")
    sql_lines.append(",\n".join(per_values) + ";")
    sql_lines.append("")
    
    sql_lines.append("-- ============================================================")
    sql_lines.append("-- END OF DML")
    sql_lines.append("-- ============================================================")
    
    return "\n".join(sql_lines)

def main():
    print("=" * 70)
    print("GENERATE DML FROM JSON FILES")
    print("=" * 70)
    print()
    
    # Check JSON directory
    if not JSON_DIR.exists():
        print(f"❌ Directory tidak ditemukan: {JSON_DIR}")
        return
    
    # Load all JSON files
    print("📂 Loading JSON files...")
    all_data = load_all_json_files()
    
    if not all_data:
        print("❌ Tidak ada data yang di-load")
        return
    
    print(f"\n✅ Total years loaded: {len(all_data)}")
    print(f"   Years: {sorted(all_data.keys())}")
    
    # Generate DML
    print("\n🔧 Generating DML SQL...")
    sql_content = generate_dml(all_data)
    
    # Write to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    # File stats
    file_size = os.path.getsize(OUTPUT_FILE)
    line_count = sql_content.count('\n') + 1
    
    print(f"\n✅ File created: {OUTPUT_FILE}")
    print(f"   Size: {file_size / 1024:.2f} KB")
    print(f"   Lines: {line_count}")
    
    print("\n" + "=" * 70)
    print("SELESAI!")
    print("=" * 70)

if __name__ == "__main__":
    main()
