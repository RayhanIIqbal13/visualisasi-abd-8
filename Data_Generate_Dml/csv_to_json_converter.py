#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FILE: csv_to_json_converter.py
FUNGSI: Konversi CSV ke JSON dengan atribut yang dipilih
DESKRIPSI: Membaca semua CSV (2015-2024) dan menghasilkan JSON bersih

================================================================================
OUTPUT ATTRIBUTES:
- ranking
- country_name
- region_name
- happiness_score
- gdp_per_capita
- social_support
- healthy_life_expectancy
- freedom_to_make_life_choices
- generosity
- perceptions_of_corruption
- dystopia_residual (calculated)
================================================================================
"""

import csv
import json
import os
from pathlib import Path
from datetime import datetime

# Get script directory untuk relative path
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent

# Paths
CSV_DIR = PROJECT_ROOT / "Data" / "Csv_Asli"
OUTPUT_DIR = PROJECT_ROOT / "Data" / "Json_Bersih"

# Tahun yang akan diproses (2015-2024)
YEARS = list(range(2015, 2025))

# Atribut output yang diinginkan
OUTPUT_FIELDS = [
    "ranking",
    "country_name",
    "region_name",
    "happiness_score",
    "gdp_per_capita",
    "social_support",
    "healthy_life_expectancy",
    "freedom_to_make_life_choices",
    "generosity",
    "perceptions_of_corruption",
    "dystopia_residual",
]

# Mapping nama kolom CSV ke nama field JSON
CSV_TO_JSON_MAPPING = {
    "Ranking": "ranking",
    "Country": "country_name",
    "Regional indicator": "region_name",
    "Happiness score": "happiness_score",
    "GDP per capita": "gdp_per_capita",
    "Social support": "social_support",
    "Healthy life expectancy": "healthy_life_expectancy",
    "Freedom to make life choices": "freedom_to_make_life_choices",
    "Generosity": "generosity",
    "Perceptions of corruption": "perceptions_of_corruption",
}

def parse_number(value):
    """Parse number dari format CSV (bisa pakai koma atau titik)"""
    if value is None or str(value).strip() == '':
        return 0.0
    try:
        # Replace koma dengan titik untuk parsing
        cleaned = str(value).strip().replace(',', '.')
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0

def calculate_dystopia_residual(happiness_score, gdp, social, health, freedom, generosity, corruption):
    """
    Hitung dystopia residual
    Formula: happiness_score - (sum of all factors) - dystopia_baseline
    Dystopia baseline biasanya sekitar 1.85
    """
    try:
        # Sum semua faktor
        factors_sum = gdp + social + health + freedom + generosity + corruption
        
        # Dystopia residual = happiness - factors - baseline
        # Baseline disesuaikan agar residual dalam range yang wajar
        dystopia_baseline = 1.85
        residual = happiness_score - factors_sum - dystopia_baseline
        
        # Pastikan nilai positif dan dalam range yang wajar (0.1 - 3.0)
        residual = max(0.1, min(3.0, abs(residual)))
        
        return round(residual, 3)
    except:
        return 0.1

def process_csv_file(csv_path, year):
    """Proses satu file CSV dan return list of entries"""
    entries = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            # Detect delimiter (semicolon or comma)
            first_line = f.readline()
            f.seek(0)
            
            delimiter = ';' if ';' in first_line else ','
            
            reader = csv.DictReader(f, delimiter=delimiter)
            
            for row in reader:
                entry = {}
                
                # Map CSV columns to JSON fields
                for csv_col, json_field in CSV_TO_JSON_MAPPING.items():
                    if csv_col in row:
                        value = row[csv_col]
                        
                        if json_field == 'ranking':
                            entry[json_field] = int(parse_number(value))
                        elif json_field in ['country_name', 'region_name']:
                            entry[json_field] = str(value).strip()
                        else:
                            entry[json_field] = round(parse_number(value), 5)
                
                # Calculate dystopia_residual
                entry['dystopia_residual'] = calculate_dystopia_residual(
                    entry.get('happiness_score', 0),
                    entry.get('gdp_per_capita', 0),
                    entry.get('social_support', 0),
                    entry.get('healthy_life_expectancy', 0),
                    entry.get('freedom_to_make_life_choices', 0),
                    entry.get('generosity', 0),
                    entry.get('perceptions_of_corruption', 0)
                )
                
                # Only add if has valid country name
                if entry.get('country_name'):
                    entries.append(entry)
        
        # Sort by ranking
        entries.sort(key=lambda x: x.get('ranking', 999))
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    return entries

def main():
    print("\n" + "="*70)
    print("📊 CSV TO JSON CONVERTER - World Happiness Report")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    print(f"\n📋 Configuration:")
    print(f"   CSV Directory: {CSV_DIR}")
    print(f"   Output Directory: {OUTPUT_DIR}")
    print(f"   Years: {YEARS[0]}-{YEARS[-1]} ({len(YEARS)} years)")
    
    print(f"\n📝 Output Fields:")
    for field in OUTPUT_FIELDS:
        print(f"   - {field}")
    
    # Create output directory if not exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*70)
    print("PROCESSING FILES")
    print("="*70)
    
    total_entries = 0
    files_processed = 0
    
    for year in YEARS:
        csv_filename = f"world_happiness_{year}.csv"
        csv_path = CSV_DIR / csv_filename
        
        json_filename = f"world_happiness_{year}.json"
        json_path = OUTPUT_DIR / json_filename
        
        if not csv_path.exists():
            print(f"   ⚠️  {csv_filename} - File tidak ditemukan, skip...")
            continue
        
        print(f"\n📄 Processing {csv_filename}...")
        
        # Process CSV
        entries = process_csv_file(csv_path, year)
        
        if entries:
            # Save JSON
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(entries, f, indent=2, ensure_ascii=False)
            
            print(f"   ✓ Created {json_filename}: {len(entries)} entries")
            total_entries += len(entries)
            files_processed += 1
        else:
            print(f"   ✗ No valid entries found")
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"   ✓ Files processed: {files_processed}")
    print(f"   ✓ Total entries: {total_entries}")
    print(f"   ✓ Output directory: {OUTPUT_DIR}")
    
    print("\n" + "="*70)
    print("✅ SELESAI!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
