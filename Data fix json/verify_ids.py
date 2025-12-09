import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
json_file = PROJECT_ROOT / "Data" / "Json_Bersih" / "world_happiness_2024.json"

with open(json_file) as f:
    data = json.load(f)
    entry = data[0]
    print("Sample entry with IDs:")
    print(json.dumps(entry, indent=2))
    
    print("\n\nFirst 5 entries - ID verification:")
    for i in range(min(5, len(data))):
        e = data[i]
        print(f"{e['country_name']:20} (rank {e['ranking']:3}): region_id={e['region_id']}, country_id={e['country_id']:3}, report_id={e['report_id']:6}, economic_id={e['economic_id']:7}, social_id={e['social_id']:7}, perception_id={e['perception_id']:7}")
