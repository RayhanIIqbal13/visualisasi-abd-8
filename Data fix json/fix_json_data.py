"""
Script untuk memperbaiki format decimal di JSON files
Mengubah koma (,) menjadi titik (.) untuk kompatibilitas SQL
Menghapus entry dengan region_id = 0
"""

import json
import os
from pathlib import Path

def fix_decimal_format(value):
    """Ubah format decimal dari koma ke titik"""
    if isinstance(value, str):
        # Ganti koma dengan titik untuk angka desimal
        return value.replace(',', '.')
    return value

def fix_json_file(filepath):
    """Baca, perbaiki, dan simpan JSON file"""
    print(f"\n🔧 Processing: {os.path.basename(filepath)}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"   📊 Total entries sebelum: {len(data)}")
        
        # Perbaiki format decimal dan filter region_id = 0
        fixed_data = []
        removed_count = 0
        
        for entry in data:
            # Skip jika region_id = 0
            if entry.get('region_id') == 0:
                removed_count += 1
                continue
            
            # Perbaiki format decimal semua field numerik
            fixed_entry = {
                'ranking': entry.get('ranking'),
                'country_name': entry.get('country_name'),
                'region_name': entry.get('region_name'),
                'happiness_score': fix_decimal_format(entry.get('happiness_score', '0')),
                'gdp_per_capita': fix_decimal_format(entry.get('gdp_per_capita', '0')),
                'social_support': fix_decimal_format(entry.get('social_support', '0')),
                'healthy_life_expectancy': entry.get('healthy_life_expectancy', 0),
                'freedom_to_make_life_choices': fix_decimal_format(entry.get('freedom_to_make_life_choices', '0')),
                'generosity': fix_decimal_format(entry.get('generosity', '0')),
                'perceptions_of_corruption': fix_decimal_format(entry.get('perceptions_of_corruption', '0')),
                'dystopia_residual': fix_decimal_format(entry.get('dystopia_residual', '0')),
                'region_id': entry.get('region_id'),
                'country_id': entry.get('country_id'),
                'report_id': entry.get('report_id'),
                'economic_id': entry.get('economic_id'),
                'social_id': entry.get('social_id'),
                'perception_id': entry.get('perception_id')
            }
            fixed_data.append(fixed_entry)
        
        # Simpan file yang sudah diperbaiki
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(fixed_data, f, indent=1, ensure_ascii=False)
        
        print(f"   ✅ Total entries setelah: {len(fixed_data)}")
        if removed_count > 0:
            print(f"   ⚠️  Dihapus (region_id=0): {removed_count}")
        else:
            print(f"   ✅ Tidak ada entry yang dihapus")
        
        return len(fixed_data), removed_count
        
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON Error: {e}")
        return 0, 0
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 0, 0

def main():
    """Process semua JSON files"""
    json_dir = Path('Data/Json')
    
    if not json_dir.exists():
        print(f"❌ Directory tidak ditemukan: {json_dir}")
        return
    
    # Cari semua JSON files
    json_files = sorted(json_dir.glob('world_happiness_*.json'))
    
    if not json_files:
        print("❌ Tidak ada JSON files ditemukan")
        return
    
    print("=" * 60)
    print("🔧 MEMPERBAIKI FORMAT DECIMAL DAN MENGHAPUS DATA INVALID")
    print("=" * 60)
    
    total_entries = 0
    total_removed = 0
    
    for filepath in json_files:
        entries, removed = fix_json_file(str(filepath))
        total_entries += entries
        total_removed += removed
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Total entries (valid): {total_entries}")
    print(f"⚠️  Total entries (dihapus): {total_removed}")
    print(f"📁 Files diproses: {len(json_files)}")
    print("\n✨ Semua JSON files sudah diperbaiki!")
    print("=" * 60)

if __name__ == "__main__":
    main()
