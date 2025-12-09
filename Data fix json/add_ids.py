import json
import os
from pathlib import Path

# Path relative to script location
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
json_folder = PROJECT_ROOT / "Data" / "Json_Bersih"

# Region mapping
REGION_MAP = {
    "South Asia": 1,
    "Central and Eastern Europe": 2,
    "Sub-Saharan Africa": 3,
    "Latin America and Caribbean": 4,
    "Commonwealth of Independent States": 5,
    "North America and ANZ": 6,
    "Western Europe": 7,
    "Southeast Asia": 8,
    "East Asia": 9,
    "Middle East and North Africa": 10,
}

# Country to ID mapping (consistent across all years)
COUNTRY_ID_MAP = {}

def get_country_id(country_name):
    """Get atau buat country_id yang konsisten"""
    if country_name not in COUNTRY_ID_MAP:
        # Assign new country ID based on alphabetical + existing count
        new_id = len(COUNTRY_ID_MAP) + 1
        COUNTRY_ID_MAP[country_name] = new_id
    return COUNTRY_ID_MAP[country_name]

def add_ids_to_entry(entry):
    """Add ID fields ke entry"""
    region_name = entry.get("region_name", "")
    country_name = entry.get("country_name", "")
    ranking = entry.get("ranking", 1)
    
    # Get IDs
    region_id = REGION_MAP.get(region_name, 0)
    country_id = get_country_id(country_name)
    
    # Calculate other IDs using formulas
    report_id = (country_id * 1000) + ranking
    economic_id = (report_id * 10) + 1
    social_id = (report_id * 10) + 2
    perception_id = (report_id * 10) + 3
    
    # Add IDs to entry
    entry["region_id"] = region_id
    entry["country_id"] = country_id
    entry["report_id"] = report_id
    entry["economic_id"] = economic_id
    entry["social_id"] = social_id
    entry["perception_id"] = perception_id
    
    return entry

def process_files():
    """Process semua file JSON dan tambah IDs"""
    files_to_update = [
        "world_happiness_2015.json",
        "world_happiness_2016.json",
        "world_happiness_2017.json",
        "world_happiness_2018.json",
        "world_happiness_2019.json",
        "world_happiness_2020.json",
        "world_happiness_2021.json",
        "world_happiness_2022.json",
        "world_happiness_2023.json",
        "world_happiness_2024.json",
    ]
    
    print("=" * 70)
    print("Menambahkan ID Fields ke JSON Files")
    print("=" * 70)
    print()
    
    total_entries = 0
    
    for filename in files_to_update:
        filepath = os.path.join(json_folder, filename)
        
        if not os.path.exists(filepath):
            print(f"File tidak ditemukan: {filepath}")
            continue
        
        try:
            # Baca file
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Tambah IDs ke setiap entry
            for entry in data:
                add_ids_to_entry(entry)
            
            # Simpan file dengan format rapi
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=1, ensure_ascii=False)
            
            print(f"✓ {filename:30} - {len(data):3} entries dengan IDs ditambahkan")
            total_entries += len(data)
            
        except Exception as e:
            print(f"✗ {filename:30} - Error: {str(e)}")
    
    print()
    print("=" * 70)
    print(f"Total entries processed: {total_entries}")
    print(f"Total unique countries: {len(COUNTRY_ID_MAP)}")
    print("=" * 70)
    
    # Print sample country IDs
    print("\nSample Country IDs:")
    sample_countries = sorted(list(COUNTRY_ID_MAP.items()))[:10]
    for country, cid in sample_countries:
        print(f"  {country:30} -> ID: {cid:3}")
    print("  ...")

if __name__ == "__main__":
    process_files()
